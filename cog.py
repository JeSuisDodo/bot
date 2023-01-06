# .env imports
import os
from dotenv import load_dotenv

# discord imports
import discord
from discord.ext.commands import Bot, Cog, Context, CooldownMapping, BucketType
from discord.commands import slash_command

# personal imports
from threading import Timer
from db import (
    add_reaction_role,
    get_bag,
    get_member,
    get_members,
    get_reaction_roles,
    give_potato,
    remove_potato,
    update_profile,
)
from format import format, format_seconds
from update_count import update_count
from roles import roles

load_dotenv()

guild_ids = [int(os.getenv("GUILD"))]
permissions = [
    discord.CommandPermission(478600472245043211, 2),
    discord.CommandPermission(270200933839929345, 2),
]
bot_category = 957024099228590191
voice_dodo = 958070176190980156


class Event(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._cd = CooldownMapping.from_cooldown(1, 30, BucketType.member)
        Timer(150, self.voice_activity).start()
        self.dodo_streaming = False
        Timer(10, self.check_streaming).start()

    def check_streaming(self):
        Timer(300, self.check_streaming).start()
        streaming_now = False
        url = ""
        # get datas
        guild = self.bot.get_guild(guild_ids[0])
        dodo = guild.get_member(270200933839929345)
        activities = dodo.activities
        # check if dodo is streaming
        for activity in activities:
            if (
                activity.type == discord.ActivityType.streaming
                and activity.platform == "Twitch"
            ):
                streaming_now = True
                url = activity.url
        # send an embed message
        if not self.dodo_streaming and streaming_now:
            notif_channel = guild.get_channel(957216153007190016)
            self.bot.loop.create_task(
                notif_channel.send(content=f"Dodo est en stream !\n{url}")
            )
        elif self.dodo_streaming and not streaming_now:
            notif_channel = guild.get_channel(957216153007190016)
            self.bot.loop.create_task(notif_channel.send(content="Fin du stream !"))
        # update the dodo streaming status
        self.dodo_streaming = streaming_now

    def get_ratelimit(self, message: discord.Message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    def voice_activity(self):
        Timer(150, self.voice_activity).start()
        voice_channels = self.bot.get_guild(guild_ids[0]).voice_channels
        for channel in voice_channels:
            if len(channel.members) > 1:
                for member in channel.members:
                    voice = member.voice
                    if not (
                        voice.deaf
                        or voice.mute
                        or voice.self_deaf
                        or voice.self_mute
                        or voice.afk
                    ):
                        update_profile(member, bag=2, voicetime=150)

    @Cog.listener()
    async def on_ready(self):
        print("Ready!")
        print("Logged in as ---->", self.bot.user)
        print("ID:", self.bot.user.id)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # welcome message
        channel = member.guild.get_channel(957006273424011324)
        embed = discord.Embed()
        embed.add_field(
            name=f"Bienvenue {member.name} ! 🎉",
            value=f"Installe toi bien tranquillement dans **la Pataterie** et profite de l'ambiance ! Tu peux même récolter des patates en étant actif !",
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_image(url="https://i.imgur.com/ANi6L1o.jpg")
        await channel.send(embed=embed)
        # give potatoes and roles
        update_profile(member)
        client = discord.utils.get(member.guild.roles, name="🥔Client🥔")
        await member.add_roles(client)
        # update count
        await update_count(self.bot.get_guild(guild_ids[0]))

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await update_count(self.bot.get_guild(guild_ids[0]))

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and message.channel.category_id != bot_category:
            ratelimit = self.get_ratelimit(message)
            if ratelimit is None:
                length = len(message.content)
                multiplier = length // 20 + 1
                update_profile(message.author, bag=1 * multiplier, messages=1)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message_id = payload.message_id
        emoji = str(payload.emoji)
        reaction_roles = get_reaction_roles()
        for r_role in reaction_roles.find():
            if r_role["message_id"] == message_id and r_role["emoji"] == emoji:
                member = self.bot.get_guild(guild_ids[0]).get_member(payload.user_id)
                if member:
                    role = discord.utils.get(member.guild.roles, id=r_role["role_id"])
                    await member.add_roles(role)
                    return

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        message_id = payload.message_id
        emoji = str(payload.emoji)
        reaction_roles = get_reaction_roles()
        for r_role in reaction_roles.find():
            if r_role["message_id"] == message_id and r_role["emoji"] == emoji:
                member = self.bot.get_guild(guild_ids[0]).get_member(payload.user_id)
                if member:
                    role = discord.utils.get(member.guild.roles, id=r_role["role_id"])
                    await member.remove_roles(role)
                    return


class Slash(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.emote = {"potato": "<:patate:957016663721652244>"}

    def get_message(self, url: str) -> discord.Message:
        links = url.split("/")
        if len(links) > 3:
            channel = self.bot.get_channel(int(links[-2]))
            message = channel.get_partial_message(int(links[-1])) if channel else None
            return message
        else:
            return None

    @slash_command(
        name="aide",
        description="Informations à propos des commandes",
        guild_ids=guild_ids,
    )
    async def _help(self, ctx: Context):
        """Send an embed with help about commands"""
        embed = discord.Embed()
        if ctx.channel.category_id == bot_category:
            embed.add_field(
                name="ℹ️ Aide",
                value="Le bot fonctionne uniquement avec des /commandes pour le moment.\nIl vous permet d'accumuler des patates en participant à la vie active du serveur (écrire des messages, parler en vocal).\nVos patates vous permettent ensuite d'acheter divers rôles personnalisés, elles seront consommées et non réutilisables.",
                inline=False,
            )
            embed.add_field(
                name="📝Liste des commandes",
                value="\n".join(
                    f"**/{command.name}** - {command.description}"
                    for command in self.get_commands()
                ),
                inline=False,
            )
            await ctx.respond(embed=embed)
        else:
            embed.add_field(
                name="🚫 Erreur",
                value="Tu ne peux pas utiliser cette commande ici, va dans le salon <#957023761696170044>",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(
        name="profil",
        description="Regarde ton profil",
        guild_ids=guild_ids,
    )
    async def _profil(
        self, ctx: Context, member: discord.Option(discord.Member, "La personne") = None
    ):
        """Send an embed with the profile of a member"""
        embed = discord.Embed()
        if ctx.channel.category_id == bot_category:
            if member is None:
                member = ctx.author
            profile = get_member(member)
            embed.add_field(
                name=f"🥔 Profil de {member.name}",
                value=f"Patates: **{profile['bag']}** ({profile['bag']+profile['spend']})\nMessages: **{profile['messages']}**\nTemps de parole: **{format_seconds(profile['voicetime'])}**",
            )
            embed.set_thumbnail(url=member.avatar.url)
            await ctx.respond(embed=embed)
        else:
            embed.add_field(
                name="🚫 Erreur",
                value="Tu ne peux pas utiliser cette commande ici, va dans le salon <#957023761696170044>",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="magasin", description="Magasin de rôles", guild_ids=guild_ids)
    async def _magasin(self, ctx: Context):
        """Send an embed with the roles that are possible to buy"""
        embed = discord.Embed()
        if ctx.channel.category_id == bot_category:

            class BuyButton(discord.ui.Button):
                def __init__(
                    self, role: discord.Role, price: int, needed: discord.Role
                ):
                    if needed is None or not ctx.author.get_role(needed) is None:
                        super().__init__(label=role.name)
                    else:
                        super().__init__(label=role.name, disabled=True)
                    self.role = role
                    self.price = price

                async def callback(self, interaction: discord.Interaction):
                    embed = discord.Embed()
                    member = interaction.user
                    if member != ctx.author:
                        embed.add_field(
                            name="🚫 Erreur",
                            value="Ce n'est pas ton magasin",
                        )
                        await interaction.response.send_message(
                            embed=embed, ephemeral=True
                        )
                    else:
                        bag = get_bag(member)
                        if bag < self.price:
                            embed.add_field(
                                name="🚫 Erreur",
                                value=f"Tu n'as pas assez de patates pour acheter ce rôle. Il te faut {self.price} <:patate:957016663721652244>",
                            )
                            await interaction.message.edit(embed=embed, view=None)
                        elif not member.get_role(self.role.id) is None:
                            embed.add_field(
                                name="🚫 Erreur",
                                value=f"Tu as déjà ce rôle",
                            )
                            await interaction.message.edit(embed=embed, view=None)
                        else:
                            remove_potato(member, self.price)
                            await member.add_roles(self.role)
                            embed.add_field(
                                name="🎉 Félicitations !",
                                value=f"Tu as acheté le rôle {self.role.mention} pour {self.price} <:patate:957016663721652244>",
                            )
                            await interaction.message.edit(
                                embed=embed, view=None, delete_after=None
                            )

            embed.add_field(
                name="🏪 Magasin",
                value="\n".join(
                    f"{ctx.guild.get_role(roles[role]['id']).mention} - {roles[role]['prix']} {self.emote['potato']}"
                    for role in roles.keys()
                ),
            )

            buttons = [
                BuyButton(
                    ctx.guild.get_role(roles[role]["id"]),
                    roles[role]["prix"],
                    roles[role]["needed"],
                )
                for role in roles.keys()
            ]
            view = discord.ui.View(*buttons)
            await ctx.respond(embed=embed, view=view, delete_after=60 * 5)
        else:
            embed.add_field(
                name="🚫 Erreur",
                value="Tu ne peux pas utiliser cette commande ici, va dans le salon <#957023761696170044>",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="ptop", description="Top des patates", guild_ids=guild_ids)
    async def _ptop(
        self,
        ctx: Context,
        critere: discord.Option(
            str,
            "Le critère sur lequel se base le classement",
            choices=["potatoes", "messages", "voicetime"],
        ),
    ):
        """Send an embed with the current potatoes leaderboard"""
        embed = discord.Embed()
        if ctx.channel.category_id == bot_category:
            update_profile(ctx.author)
            members = get_members()
            members = sorted(
                [member for member in members.find()],
                key=lambda m: m["bag"] + m["spend"]
                if critere == "potatoes"
                else m[critere],
                reverse=True,
            )
            author_rank = members.index(get_member(ctx.author)) + 1

            embed.add_field(
                name="🏆 Top des patates"
                if critere == "potatoes"
                else "🏆 Top des messages"
                if critere == "messages"
                else "🏆 Top des temps de parole",
                value="\n".join(
                    f"**{i+1}.{members[i]['name']}** - {format(members[i]['bag']+members[i]['spend'])} {self.emote['potato']}"
                    if critere == "potatoes"
                    else f"**{i+1}.{members[i]['name']}** - {members[i]['messages']} 💬"
                    if critere == "messages"
                    else f"**{i+1}.{members[i]['name']}** - {format_seconds(members[i]['voicetime'])} 🎤"
                    for i in range(15 if len(members) >= 15 else len(members))
                ),
            ).set_footer(text=f"Tu es rang {author_rank}")
            await ctx.respond(embed=embed)
        else:
            embed.add_field(
                name="🚫 Erreur",
                value="Tu ne peux pas utiliser cette commande ici, va dans le salon <#957023761696170044>",
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(
        name="clean",
        description="Clean le salon (admin)",
        guild_ids=guild_ids,
        permissions=permissions,
    )
    async def _clean(
        self,
        ctx: Context,
        number: discord.Option(
            int, "Nombre de messages à supprimer", min_value=1, max_value=100
        ),
    ):
        """Purge a certain number of messages in the channel"""
        embed = discord.Embed()
        await ctx.channel.purge(limit=number)
        embed.add_field(
            name="🗑 Cleaned",
            value=f"{number} message{'s' if number>1 else ''} {'ont' if number>1 else 'a'} été supprimé{'s' if number>1 else ''}",
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(
        name="give",
        description="Donne des patates à un membre (admin)",
        guild_ids=guild_ids,
        permissions=permissions,
    )
    async def _give(
        self,
        ctx: Context,
        member: discord.Member,
        number: discord.Option(int, "Nombre de patates à donner", min_value=1),
    ):
        """Give a certain amount of potatoes to someone"""
        embed = discord.Embed()
        give_potato(member, number)
        embed.add_field(
            name="🎉 Patates",
            value=f"{member.mention} a reçu {number} {self.emote['potato']}",
        )
        await ctx.respond(embed=embed)

    @slash_command(
        name="reactionroles",
        description="Ajoute un reaction role à un message (admin)",
        guild_ids=guild_ids,
        permissions=permissions,
    )
    async def _reactionroles(
        self,
        ctx: Context,
        message_url: discord.Option(str, "Url du message"),
        emoji: discord.Option(str, "Emoji à ajouter"),
        role: discord.Option(discord.Role, "Rôle à attribuer"),
    ):
        """Add a reaction role to a message"""
        message = self.get_message(message_url)
        embed = discord.Embed()
        if message is None:
            embed.add_field(
                name="🚫 Erreur",
                value="Ce message n'existe pas",
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            try:
                await message.add_reaction(emoji)
                add_reaction_role(message, emoji, role)
                embed.add_field(
                    name="👍 Rôle ajouté",
                    value=f"{emoji} ajouté pour le rôle {role.mention}",
                )
                await ctx.respond(embed=embed)
            except discord.HTTPException:
                embed.add_field(
                    name="🚫 Erreur",
                    value="Cet emoji n'existe pas",
                )
                await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: Bot):
    bot.add_cog(Event(bot))
    bot.add_cog(Slash(bot))

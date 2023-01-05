import os
import discord 
from discord.ext import commands
from asyncio import sleep
import os
from dotenv import load_dotenv

bot = discord.Bot()

load_dotenv()

guild_ids = [os.getenv("834429780916830280")]

intents = discord.Intents.default()
intents.members = True

async def update_members(guild):
    channel = guild.get_channel(1060460635495878656)
    await channel.edit(name=f"{guild.member_count}")

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(854675820270714920)
    embed = discord.Embed()
    embed.add_field(
        name=f"Bienvenue {member.name} ! 🎉",
        value=f"Installe toi bien tranquillement et profite de l'ambiance !",
    )
    embed.set_thumbnail(url=member.avatar.url)
    await channel.send(embed=embed)
    await member.add_role(discord.utils.get(member.guild.roles, name="Cool Guys"))
    await update_members(bot.get_guild(834429780916830280))

@bot.event
async def on_member_remove(member):
    await update_members(bot.get_guild(834429780916830280))




 
@bot.slash_command()
async def membercount(ctx):
    count = ctx.guild.member_count
    await ctx.respond(f"Le serveur compte {count} {'membre' if count <= 1 else 'membres'}")
	




bot.run("MTA1OTUxNDY2NzgyOTAzNTAxOA.Gu86KI.7p20hi4sFqYT7eopHj_GcLv_3tzgwNa2tG-ajc")
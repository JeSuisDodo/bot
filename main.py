import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_message(message):
    if message.content.startswith('!membres'):
        guild = message.guild
        member_count = guild.member_count
        await message.channel.send(f'Le serveur a {member_count} membres.')
@bot.event
async def on_message(message):
    if message.content.startswith('!update_channel_name'):
        voice_channel = message.author.voice.channel
        guild = message.guild
        member_count = guild.member_count
        new_channel_name = f'Salon vocal ({member_count} membres)'
        await voice_channel.edit(name=new_channel_name)

@bot.event
async def on_member_join(member):
    guild = member.guild
    role = guild.get_role(1061651884353540187)
    await member.add_roles(role)


bot.run('MTA1OTUxNDY2NzgyOTAzNTAxOA.Gu86KI.7p20hi4sFqYT7eopHj_GcLv_3tzgwNa2tG-ajc')
import os
import discord 
from discord.ext import commands
from asyncio import sleep
import os
from dotenv import load_dotenv


load_dotenv()



intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', help_command=None, intents=intents)


@client.slash_command()
async def membercount(ctx):
    count = ctx.guild.member_count
    await ctx.respond(f"Le serveur compte {count} {'membre' if count <= 1 else 'membres'}")
	



client.run("MTA1OTUxNDY2NzgyOTAzNTAxOA.Gu86KI.7p20hi4sFqYT7eopHj_GcLv_3tzgwNa2tG-ajc")
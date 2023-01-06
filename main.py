import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = discord.Bot(command_prefix="p", self_bot=True, intents=intents)

bot.load_extension("cog")
bot.run(TOKEN)
import discord 

bot = discord.Bot()

@bot.event
async def conect():
    print(f"Connecter sous le nom de {bot.user}")

@bot.slash_command()
async def test(ctx):
    await ctx.respond("Yep !")

bot.run("MTA1OTUxNDY2NzgyOTAzNTAxOA.Gu86KI.7p20hi4sFqYT7eopHj_GcLv_3tzgwNa2tG-ajc")
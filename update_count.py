from discord import Guild


async def update_count(guild: Guild) -> None:
    """Update the guild member count's channel name"""
    counter = guild.get_channel(957018927563694160)
    await counter.edit(name=f"Membres : {guild.member_count} 🥔")

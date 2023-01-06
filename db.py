import os
from dotenv import load_dotenv
import pymongo
import discord

load_dotenv()


def get_db():
    """Get the whole database for this bot"""
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv("DBSTRING")

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = pymongo.MongoClient(CONNECTION_STRING)
    return client["discord"]


# members part
def get_members():
    """Get all the members from the database"""
    db = get_db()
    return db["members"]


def get_member(member: discord.Member) -> dict:
    """Get a specific member"""
    collection = get_members()
    doc = collection.find_one({"id": member.id})
    if doc == None:
        doc = {
            "id": member.id,
            "name": member.name,
            "bag": 0,
            "spend": 0,
            "messages": 0,
            "voicetime": 0,
        }
        collection.insert_one(doc)
    return doc


def get_bag(member: discord.Member) -> int:
    """Get the bag for a specific member"""
    return get_member(member)["bag"]


def get_spend(member: discord.Member) -> int:
    """Get the amount a specific member spent"""
    return get_member(member)["spend"]


def update_profile(
    member: discord.Member, bag=0, spend=0, messages=0, voicetime=0
) -> None:
    """Update the profile of a member"""
    collection = get_members()
    collection.update_one(
        {"id": member.id},
        {
            "$setOnInsert": {"name": member.name},
            "$inc": {
                "bag": bag,
                "spend": spend,
                "messages": messages,
                "voicetime": voicetime,
            },
        },
        upsert=True,
    )


def give_potato(member: discord.Member, amount: int) -> None:
    """Give a certain amount of potatoes to a member"""
    update_profile(member, bag=amount)


def remove_potato(member: discord.Member, amount: int) -> None:
    """Remove a certain amount of potatoes for a member"""
    update_profile(member, bag=-amount, spend=amount)


def increase_messages(member: discord.Member, amount: int) -> None:
    """Increase the messages of a member"""
    update_profile(member, messages=amount)


def increase_voicetime(member: discord.Member, amount: int) -> None:
    """Increase the voicetime of a member"""
    update_profile(member, voicetime=amount)


# reaction roles part
def get_reaction_roles():
    """Get all the reaction roles from the database"""
    db = get_db()
    return db["reaction_roles"]


def add_reaction_role(message: discord.Message, emoji: str, role: discord.Role) -> None:
    """Add a reaction role to the database"""
    collection = get_reaction_roles()
    collection.insert_one(
        {"message_id": message.id, "emoji": emoji, "role_id": role.id}
    )

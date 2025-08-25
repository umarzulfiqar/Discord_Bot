import discord
from typing import Any
from db.mongo import get_collection
import os
from dotenv import load_dotenv
from pymongo.errors import BulkWriteError

load_dotenv()

messages_collection = get_collection("messages")

async def on_ready(bot : discord.Client):
    print(f"We are ready, {bot.user.name}")

    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    all_data = []

    async for message in channel.history(limit=None):
        if message.author.bot:
            continue

        data : dict[str,Any] = {
            "_id": message.id,
            "author" : str(message.author),
            "content" : message.content,
            "channel" : str(message.channel),
            "timestamp" : message.created_at.isoformat(),
        }
        if message.attachments:
            data["attachments"] = [attachment.url for attachment in message.attachments]


        if message.reactions:
            data["reactions"] = {}
            for reaction in message.reactions:
                user_ids = []
                async for user in reaction.users(limit=None):
                    user_ids.append(str(user.id))
                data["reactions"][str(reaction.emoji)] = user_ids
        all_data.append(data)
    for data in all_data:
        try:
            messages_collection.update_one(
                {"_id": data["_id"]},
                {"$set": data},
                upsert=True
            )
        except Exception as e:
            print(f"Error saving message {data['_id']}: {e}")
    print("History messages and reactions saved!")

async def on_member_join(member : discord.Member):
    await member.send(f"Welcome to the server {member.name}")

async def on_message(bot,message:discord.Message):
    if message.author == bot.user:    #Check for user is bot
        return
    bad_words = ["fuck", "fuck you", "shit"]
    if any(word in message.content.lower() for word in bad_words):         #Check for bad words.
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")
        return

    #save message into mongodb
    data: dict[str, Any] = {
        "_id": message.id,
        "author" : str(message.author),
        "content" : message.content,
        "channel" : str(message.channel),
        "timestamp":message.created_at.isoformat(),
    }

    if message.attachments:
        data["attachments"] = [attachment.url for attachment in message.attachments]
    messages_collection.insert_one(data)
    print("Message saved:", data)

    await bot.process_commands(message)


async def on_reaction_add(reaction, user):
    if user.bot:
        return

    messages_collection.update_one(
        {"_id": reaction.message.id},
        {"$addToSet": {f"reactions.{str(reaction.emoji)}": str(user.id)}},
        upsert=True
    )
    print(f"emoji {reaction.emoji} added by {user.id}")


async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    messages_collection.update_one(
        {"_id": reaction.message.id},
        {"$pull": {f"reactions.{str(reaction.emoji)}": str(user.id)}}
    )
    print(f"emoji {reaction.emoji} removed by {user.id}")


async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == payload.member.bot:
        return
    messages_collection.update_one(
        {"_id": payload.message_id},
        {"$addToSet": {f"reactions.{str(payload.emoji)}": str(payload.user_id)}},
        upsert=True
    )
    print(f"emoji{payload.emoji} added by {payload.user_id}")


async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    messages_collection.update_one(
        {"_id": payload.message_id},
        {"$pull": {f"reactions.{str(payload.emoji)}": str(payload.user_id)}}
    )
    print(f"emoji {payload.emoji} removed by {payload.user_id}")

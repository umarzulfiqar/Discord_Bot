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

    async for message in channel.history(limit=200):
        data : dict[str,Any] = {
            "_id": message.id,
            "author" : str(message.author),
            "content" : message.content,
            "channel" : str(message.channel),
            "timestamp" : message.created_at.isoformat(),
        }
        if message.attachments:
            data["attachments"] = [attachment.url for attachment in message.attachments]
        all_data.append(data)

    try:
        messages_collection.insert_many(all_data, ordered=False)
    except BulkWriteError:
        pass
    print("History messages saved!")

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
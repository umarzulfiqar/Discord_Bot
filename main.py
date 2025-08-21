import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from Bot import events,commands as bot_commands

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)  # passing # so bot gets message


@bot.event
async def on_ready():
    await events.on_ready(bot)

@bot.event
async def on_member_join(member):
    await events.on_member_join(member)


@bot.event
async def on_message(message):
    await events.on_message(bot,message)

bot_commands.setup_commands(bot)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
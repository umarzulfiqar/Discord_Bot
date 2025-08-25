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
intents.reactions = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents,max_messages=5000)


@bot.event
async def on_ready():
    await events.on_ready(bot)

@bot.event
async def on_member_join(member):
    await events.on_member_join(member)


@bot.event
async def on_message(message):
    await events.on_message(bot,message)


@bot.event
async def on_reaction_add(reaction,user):
    await events.on_reaction_add(reaction,user)

@bot.event
async def on_reaction_remove(reaction,user):
    await events.on_reaction_remove(reaction,user)

@bot.event
async def on_raw_reaction_add(payload):
    await events.on_raw_reaction_add(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    await events.on_raw_reaction_remove(payload)

bot_commands.setup_commands(bot)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
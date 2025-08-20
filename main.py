import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)  # passing # so bot gets message


@bot.event
async def on_ready():
    print(f"We are ready, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:  # check who is messaging
        return

    bad_words = ["fuck", "fuck you", "shit"]

    if any(word in message.content.lower() for word in bad_words):  # here we add custom line of code
        await message.delete()
        await message.channel.send(f"{message.author.mention} - dont use that word!")

    await bot.process_commands(message)  # we continue processing


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)
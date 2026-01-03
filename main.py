import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()

#Set command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot coming online message
@bot.event
async def on_ready():
    print("JerryBot2.0 Powering On")

#React to messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    #Set all characters of message to lower case
    msg = message.content.lower()
    if msg == "!hello":
        await message.channel.send('Hello World!')

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
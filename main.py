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
    print('Powering On')
    print(bot.user.name)

#Ignore messages from the bot
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
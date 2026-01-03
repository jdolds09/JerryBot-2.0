import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Give JerryBot 2.0 all the permissions
intents = discord.Intents.all()

# Set command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot coming online message
@bot.event
async def on_ready():
    print("JerryBot2.0 Powering On")

# Loading command files
async def load():
    for filename in os.listdir("./Commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"Commands.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
grok_client = OpenAI(api_key=os.getenv("GROK_TOKEN"), base_url="https://api.x.ai/v1")

# Give JerryBot 2.0 all the permissions
intents = discord.Intents.all()

# Set command prefix
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

# Get rid of default help command. I am going to make my own help command
bot.remove_command("help")

# Create a list to keep track of all commands
commands = ["meme", "vagina", "cock", "cocks", "dick", "dicks", "wiener", "wieners", "tits", "boob", "boobies",
            "titties", "butt", "butts", "titty", "disconnect", "stop", "commands", "command"]

# Chat history
chat_history = []

# Bot coming online message
@bot.event
async def on_ready():
    print("JerryBot2.0 Powering On")

# Load Fun Commands
async def fun_load():
    for filename in os.listdir("Commands/Fun"):
        if filename.endswith(".py"):
            commands.append(filename[:-3])
            await bot.load_extension(f"Commands.Fun.{filename[:-3]}")

# Load Music Commands
async def music_load():
    for filename in os.listdir("Commands/Music"):
        if filename.endswith(".py"):
            commands.append(filename[:-3])
            await bot.load_extension(f"Commands.Music.{filename[:-3]}")

# Load NSFW Commands
async def nsfw_load():
    for filename in os.listdir("Commands/NSFW"):
        if filename.endswith(".py"):
            commands.append(filename[:-3])
            await bot.load_extension(f"Commands.NSFW.{filename[:-3]}")

# Load Help Command
async def help_load():
    commands.append('help')
    await bot.load_extension("Commands.help")

@bot.event
async def on_message(message):
    # If message author is JerryBot 2.0, do nothing
    if message.author == bot.user:
        return

    # Get the first token of the user's message
    full_message = message.content
    first_token = full_message.split()[0]
    if first_token.startswith("!"):
        # Remove the ! if message starts with !
        first_token = first_token[1:]

        # If message starts with ! and is not in the list of commands, execute chatbot
        if first_token.lower() not in (command.lower() for command in commands):

            ''' This block is for conversation memory. I don't know how to implement it yet :D
            
            chat_history = [text.content async for text in message.channel.history(limit=11)]
            while len(chat_history) > 10:
                #del chat_history[-1]
            '''

            try:
                response = grok_client.chat.completions.create(model="grok-4-1-fast-reasoning", messages=[
                    {"role": "system", "content": "You are a bot named JerryBot that provides short, witty, a tiny bit crass responses."},
                    {"role": "user", "content": f"{full_message[1:]}"}]
                )

            except Exception as e:
                print(e)

            answer = response.choices[0].message.content
            await message.channel.send(answer)

    # Execute command if user entered pre-defined command
    await bot.process_commands(message)

async def main():
    async with bot:
        await fun_load()
        await music_load()
        await nsfw_load()
        await help_load()
        await bot.start(token)

asyncio.run(main())
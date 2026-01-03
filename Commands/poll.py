import discord
from discord.ext import commands
from discord import app_commands

class poll(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

@app_commands.command(name="poll", description="Creates a Yes/No poll or a multi choice poll depending on number of arguments")
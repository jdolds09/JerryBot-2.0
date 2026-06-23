import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, set_key

class Token(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Token function
    @commands.command()
    async def token(self, ctx, *args):
        # Check if user sent a message with arguments
        if len(args) == 0:
            return await ctx.send("Need to enter a token dumbass.")
        
        # Set token
        else:
            dotenv_path = ".env"
            load_dotenv(dotenv_path)
            set_key(dotenv_path, "TOKEN_V2", args[0])
            return await ctx.send("Token set successfully.")

async def setup(bot):
    await bot.add_cog(Token(bot))
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, set_key

class Session(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Session function
    @commands.command()
    async def session(self, ctx, *args):
        # Check if user sent a message with arguments
        if len(args) == 0:
            return await ctx.send("Need to enter a cookie session dumbass.")
        
        # Set cookie session
        else:
            dotenv_path = ".env"
            load_dotenv(dotenv_path)
            set_key(dotenv_path, "REDDIT_SESSION", args[0])
            return await ctx.send("Cookie session set successfully.")

async def setup(bot):
    await bot.add_cog(Session(bot))
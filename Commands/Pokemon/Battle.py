import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Battle function
    @commands.command()
    async def battle(self, ctx):
        # Generate a random number from 1-3
        random_number = random.randint(1,3)
        if random_number == 1:
            await ctx.send('Rock! Fuck we tied. Go againe!')
        elif random_number == 2:
            await ctx.send('Paper! HAHAHA I WIN!')
        else:
            await ctx.send('Scissors! Shit...')

    async def command_help(self, ctx):
        await ctx.send("**!rock**: Play Rock Paper Scissors by choosing Rock.")

async def setup(bot):
    await bot.add_cog(Battle(bot))
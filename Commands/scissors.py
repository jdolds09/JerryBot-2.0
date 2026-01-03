import discord
from discord.ext import commands
import random

class Scissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Paper function
    @commands.command()
    async def scissors(self, ctx):
        # Generate a random number from 1-3
        random_number = random.randint(1,3)
        if random_number == 1:
            await ctx.send('Rock! HAHAHA I WIN!')
        elif random_number == 2:
            await ctx.send('Paper! Shit...')
        else:
            await ctx.send('Scissors! Fuck we tied. Go againe!')

async def setup(bot):
    await bot.add_cog(Scissors(bot))
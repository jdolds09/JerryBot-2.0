import discord
from discord.ext import commands
import random

class Paper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Paper function
    @commands.command()
    async def paper(self, ctx):
        # Generate a random number from 1-3
        random_number = random.randint(1,3)
        if random_number == 1:
            await ctx.send('Rock! Shit...')
        elif random_number == 2:
            await ctx.send('Paper! Fuck we tied. Go againe!')
        else:
            await ctx.send('Scissors! HAHAHA I WIN!')

async def setup(bot):
    await bot.add_cog(Paper(bot))
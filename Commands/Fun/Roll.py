import discord
from discord.ext import commands
import random

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Roll function
    @commands.command()
    async def roll(self, ctx, *, message = None):
        # User did not provide a number
        if message is None:
            random_number = random.randint(1, 100)
            await ctx.send(f"You rolled a {random_number}")

        # User provided a number to roll to
        else:
            if message.isdigit():
                random_number = random.randint(1, int(message))
                await ctx.send(f"You rolled a {random_number}")

            else:
                await ctx.send("You didn't enter a positive integer dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!roll OPTIONAL: [number]**: Roll between 1 and given number. If no number given, roll a random number between 1-100.")

async def setup(bot):
    await bot.add_cog(Roll(bot))
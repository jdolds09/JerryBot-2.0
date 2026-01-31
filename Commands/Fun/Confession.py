import discord
from discord.ext import commands
import random

class Confession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command function
    @commands.command()
    async def confession(self, ctx):
        random_number = random.randint(1, 100)
        # 10% Chance JerryBot does not forgive the sin
        if random_number < 11:
            await ctx.send("That is an act that I cannot forgive my son, may you burn in eternal hellfire for your actions.")
            file_path = "Images/devil.gif"
            picture = discord.File(file_path)
            return await ctx.send(file=picture)
        # JerryBot forgives
        else:
            return await ctx.send("You are forgiven my son. Be cleansed of all guilt your actions have brought upon you.")

    async def command_help(self, ctx):
        await ctx.send("**!Confession [message]**: Be cleansed of your sin or burn in eternal hellfire for your action.")

async def setup(bot):
    await bot.add_cog(Confession(bot))
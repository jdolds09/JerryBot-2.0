import discord
from discord.ext import commands


class Classes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Classes function
    @commands.command()
    async def classes(self, ctx):
        await ctx.send("The playable classes are:")
        await ctx.send("1. Warrior")
        await ctx.send("2. Hunter")
        await ctx.send("3. Mage")
        await ctx.send("4. Rogue")
        await ctx.send("5. Gambler")
        return await ctx.send("![Enter class name] to see more details about a class.")

async def setup(bot):
    await bot.add_cog(Classes(bot))
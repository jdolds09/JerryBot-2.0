import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, *, message):
        await message.channel.send(message)

async def setup(bot):
    await bot.add_cog(Poll(bot))
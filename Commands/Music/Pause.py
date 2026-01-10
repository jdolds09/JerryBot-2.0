import discord
from discord.ext import commands

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        elif ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    async def command_help(self, ctx):
        await ctx.send("**!pause**: Pauses whatever is currently playing.")

async def setup(bot):
    await bot.add_cog(Pause(bot))
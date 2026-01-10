import discord
from discord.ext import commands

class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            await ctx.send("Video must be paused to resume.")
        elif ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    async def command_help(self, ctx):
        await ctx.send("**!resume**: Resumes whatever is currently playing.")

async def setup(bot):
    await bot.add_cog(Resume(bot))
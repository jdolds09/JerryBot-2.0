import discord
from discord.ext import commands

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            play_cog = self.bot.get_cog('Play')
            await play_cog.playTrack(self, ctx)
        else:
            await ctx.send("There is nothing currently playing dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!skip**: Skips whatever is currently playing.")

async def setup(bot):
    await bot.add_cog(Skip(bot))
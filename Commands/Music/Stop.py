import discord
from discord.ext import commands

class Stop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Stop function
    @commands.command(aliases=["disconnect", "stop"])
    async def stop(self, ctx):
        # JerryBot 2.0 must be in a voice channel to disconnect
        if ctx.voice_client is not None:
            # Clear the queue and disconnect from the voice channel
            guild_id = ctx.guild.id
            play_cog = self.bot.get_cog('Play')
            play_cog.queue[guild_id].clear()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("JerryBot 2.0 is not in a voice channel dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!stop**: JerryBot 2.0 stops playing, clears the music queue and disconnects from the voice channel.")

async def setup(bot):
    await bot.add_cog(Stop(bot))
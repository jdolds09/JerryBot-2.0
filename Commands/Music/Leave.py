import discord
from discord.ext import commands

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            guild_id = ctx.guild.id
            play_cog = self.bot.get_cog('Play')
            play_cog.queue[guild_id].clear()
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("JerryBot 2.0 is not in a voice channel dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!leave**: JerryBot 2.0 disconnects from the voice channel.")

async def setup(bot):
    await bot.add_cog(Leave(bot))
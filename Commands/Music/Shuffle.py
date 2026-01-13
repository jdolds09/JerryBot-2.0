import discord
from discord.ext import commands
import random

class Shuffle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Shuffle function
    @commands.command()
    async def shuffle(self, ctx):
        # If JerryBot is connected to voice
        if ctx.voice_client is not None:
            # Get queue and if it exists, shuffle it
            guild_id = ctx.guild.id
            play_cog = self.bot.get_cog('Play')
            if play_cog.queue[guild_id]:
                random.shuffle(play_cog.queue[guild_id])
                await ctx.send("Queue shuffled!")
            # Queue doesn't exist
            else:
                await ctx.send('Nothing to shuffle dumbass.')
        # JerryBot isn't connected to voice channel
        else:
            await ctx.send("JerryBot 2.0 is not in a voice channel dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!shuffle**: JerryBot 2.0 shuffles the queue.")

async def setup(bot):
    await bot.add_cog(Shuffle(bot))
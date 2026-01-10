import os
import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Help function
    @commands.command()
    async def help(self, ctx):
        fun_cog_commands = []
        music_cog_commands = []
        nsfw_cog_commands = []

        # Get all the Fun cogs
        for filename in os.listdir("Commands/Fun"):
            if filename.endswith(".py"):
                fun_cog_commands.append(self.bot.get_cog(f'{filename[:-3]}'))

        # Get all the Music cogs
        for filename in os.listdir("Commands/Music"):
            if filename.endswith(".py"):
                music_cog_commands.append(self.bot.get_cog(f'{filename[:-3]}'))

        # Get all the NSFW cogs
        for filename in os.listdir("Commands/NSFW"):
            if filename.endswith(".py"):
                nsfw_cog_commands.append(self.bot.get_cog(f'{filename[:-3]}'))

        # Print all the help messages of the Fun commands
        await ctx.send("**__FUN COMMANDS__**")
        for c in fun_cog_commands:
              await c.command_help(ctx)

        # Print all the help messages of the Music commands
        await ctx.send("**__MUSIC COMMANDS__**")
        for c in music_cog_commands:
              await c.command_help(ctx)

        # Print all the help messages of the NSFW commands
        await ctx.send("**__NSFW COMMANDS__**")
        for c in nsfw_cog_commands:
            await c.command_help(ctx)

async def setup(bot):
    await bot.add_cog(Help(bot))
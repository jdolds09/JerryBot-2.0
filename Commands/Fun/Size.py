import discord
from discord.ext import commands
import random

class Size(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Size function
    @commands.command()
    async def size(self, ctx):
        # Create a length that is random from 0-10
        length = random.randint(0, 10)
        shaft = ""
        # If Alex executed size command
        if ctx.author.name == "thatsaltysnipezguy":
            # Give Alex a 5% chance of actually returning a random size
            alex_random = random.randint(1, 100)
            if alex_random < 6:
                # If he hit the 5% chance but also rolled a 0 on size, give him a size of 1
                if length == 0:
                    await ctx.send(f"{ctx.author.name}'s penis size:")
                    return await ctx.send("8=D")
                # Return Alex's random size
                else:
                    for _ in range(length):
                        shaft += "="
                    await ctx.send(f"{ctx.author.name}'s penis size:")
                    if length == 10:
                        await ctx.send(f"8{shaft}D")
                        return ctx.send("**MAXIMUM SIZE**")
                    else:
                        return await ctx.send(f"8{shaft}D")
            # Alex didn't hit the 5% chance, return his size as 0
            else:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                return await ctx.send("8D")
        # Execute everyone else's size
        else:
            for _ in range(length):
                shaft += "="
            # Maximum size was rolled
            if length == 10:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                await ctx.send(f"8{shaft}D")
                return await ctx.send("**MAXIMUM SIZE**")
            # Return size
            else:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                return await ctx.send(f"8{shaft}D")

    async def command_help(self, ctx):
        await ctx.send("**!size**: See how big you are...")

async def setup(bot):
    await bot.add_cog(Size(bot))
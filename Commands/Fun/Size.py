import discord
from discord.ext import commands
import random

class Size(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Roll function
    @commands.command()
    async def size(self, ctx):
        random_number = random.randint(0, 10)
        shaft = ""
        if ctx.author.name == "thatsaltysnipezguy":
            alex_random = random.randint(1, 100)
            if alex_random < 6:
                if random_number == 0:
                    await ctx.send(f"{ctx.author.name}'s penis size:")
                    return await ctx.send("8=D")
                else:
                    for _ in range(random_number):
                        shaft += "="
                    await ctx.send(f"{ctx.author.name}'s penis size:")
                    if random_number == 10:
                        await ctx.send(f"8{shaft}D")
                        return ctx.send("**MAXIMUM SIZE**")
                    else:
                        return await ctx.send(f"8{shaft}D")
            else:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                return await ctx.send("8D")
        else:
            for _ in range(random_number):
                shaft += "="
            if random_number == 10:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                await ctx.send(f"8{shaft}D")
                return await ctx.send("**MAXIMUM SIZE**")
            else:
                await ctx.send(f"{ctx.author.name}'s penis size:")
                return await ctx.send(f"8{shaft}D")

    async def command_help(self, ctx):
        await ctx.send("**!size**: See how big you are...")

async def setup(bot):
    await bot.add_cog(Size(bot))
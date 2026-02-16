import discord
from discord.ext import commands

class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Exp function
    @commands.command()
    async def rpg(self, ctx, *args):
        
        await ctx.send("**RPG COMMANDS:**")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!battle** - Start a battle against a random enemy.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!cast** - Casts a basic attack. !attack or !spell also works.")
        await ctx.send("**!cast [spell]** - Cast a spell/ability during battle. ![enter your class here] to see a list of your class's spells.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!character** - View your character's info.")
        await ctx.send("**!character create [class]** - Create a new character with the specified class.")
        await ctx.send("**!character delete** - Delete your character.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!classes** - View the available classes to choose from when creating a character.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!exp** - View your current level and experience points. !level, !lvl, !xp, !experience also works.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!gold** - View your character's gold.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!potion** - Uses a potion to restore 100 HP. !use also works.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!shop** - View the items in the shop.")
        await ctx.send("**!shop buy [item]** - Buy an item from the shop.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!spells** - View your spells and their current cooldowns. !abilities, !cooldown, !cooldowns, !spellbook, !cd, !cds also works.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!gambler** - View details about the gambler class.")
        await ctx.send("**!gambler loot** - View the gambler loot table.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!hunter** - View details about the hunter class.")
        await ctx.send("**!hunter loot** - View the hunter loot table.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!mage** - View details about the mage class.")
        await ctx.send("**!mage loot** - View the mage loot table.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!rogue** - View details about the rogue class.")
        await ctx.send("**!rogue loot** - View the rogue loot table.")
        await ctx.send("-------------------------------------------------")
        await ctx.send("**!warrior** - View details about the warrior class.")
        await ctx.send("**!warrior loot** - View the warrior loot table.")
        await ctx.send("-------------------------------------------------")

async def setup(bot):
    await bot.add_cog(Rpg(bot))
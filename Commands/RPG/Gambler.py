import discord
from discord.ext import commands


class Gambler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gambler function
    @commands.command()
    async def gambler(self, ctx, *args):
        # Gambler
        if "loot" in args:
            return await self.gambler_loot_table(ctx)

        await ctx.send("**__GAMBLER__**")
        await ctx.send("**__Starting HP__**: 150")
        await ctx.send("**__Dodge Chance__**: 15%")
        await ctx.send("**__Block Chance__**: 15%")
        await ctx.send("**__Crit Chance__**: 10%")
        await ctx.send("**------------------------------------------------------**")
        await ctx.send("**__SPELLS/ABILITIES:__**")
        await ctx.send("**__Basic Attack__**: 90% Deal 10 Damage, 10% Deal 5 Damage to Yourself")
        await ctx.send("**__Deal (Lvl 1)__**: Roll a d20, Perform a 10 Damage Attack That Many Times (Cooldown: 3 Turns)")
        await ctx.send("**__Jack (Lvl 2)__**: 80% Deal 20 Damage, 20% Deal 10 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Queen (Lvl 3)__**: 70% Deal 50 Damage, 30% Deal 20 Damage to Yourself (No Cooldown)")
        await ctx.send("**__King (Lvl 4)__**: 60% Deal 80 Damage, 40% Deal 30 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Ace (Lvl 5)__**: 50% Deal 100 Damage, 50% Deal 40 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Joker (Lvl 6)__**: 40% Deal 120 Damage, 60% Deal 50 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Straight (Lvl 7)__**: 30% Deal 150 Damage, 70% Deal 60 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Flush (Lvl 8)__**: 20% Deal 200 Damage, 80% Deal 70 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Blackjack (Lvl 9)__**: 10% Deal 300 Damage, 90% Deal 80 Damage to Yourself (No Cooldown)")
        await ctx.send("**__Roulette (Lvl 10)__**: 50% Chance to Kill the Enemy, 50% Chance you Die (No Cooldown)")

    async def gambler_loot_table(self, ctx):
        await ctx.send("**__GAMBLER__**")
        await ctx.send("**Boots**")
        await ctx.send("Shitty Boots")
        await ctx.send("🟩 Good Boots of Luck (+20 Max HP)")
        await ctx.send("🟦 Rare Boots of Luck (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Boots of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Boots of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Legs**")
        await ctx.send("Shitty Pants")
        await ctx.send("🟩 Good Pants of Luck (+20 Max HP)")
        await ctx.send("🟦 Rare Pants of Luck (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Pants of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Pants of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Chest**")
        await ctx.send("Shitty Jacket")
        await ctx.send("🟩 Good Jacket of Luck (+20 Max HP)")
        await ctx.send("🟦 Rare Jacket of Luck (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Jacket of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Jacket of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Gloves**")
        await ctx.send("Shitty Gloves")
        await ctx.send("🟩 Good Gloves of Luck (+20 Max HP)")
        await ctx.send("🟦 Rare Gloves of Luck (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Gloves of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Gloves of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Helmet**")
        await ctx.send("Shitty Fedora")
        await ctx.send("🟩 Good Fedora of Luck (+20 Max HP)")
        await ctx.send("🟦 Rare Fedora of Luck (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Fedora of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Fedora of Luck (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Main Hand Weapon**")
        await ctx.send("Shitty Trinket")
        await ctx.send("🟩 Good Trinket of Luck (+5% Chance of Success)")
        await ctx.send("🟦 Rare Trinket of Luck (+10% Chance of Success)")
        await ctx.send("🟪 Epic Trinket of Luck (+15% Chance of Success)")
        await ctx.send("🟨 Legendary Trinket of Luck (+20% Chance of Success)")
        await ctx.send("**Off Hand**")
        await ctx.send("Shitty Charm")
        await ctx.send("🟩 Good Charm of Luck (+1% Chance of Success)")
        await ctx.send("🟦 Rare Charm of Luck (+2% Chance of Success)")
        await ctx.send("🟪 Epic Charm of Luck (+3% Chance of Success)")
        await ctx.send("🟨 Legendary Charm of Luck (+5% Chance of Success)")
async def setup(bot):
    await bot.add_cog(Gambler(bot))
import discord
from discord.ext import commands


class Hunter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hunter function
    @commands.command()
    async def hunter(self, ctx, *args):
        # Hunter
        if "loot" in args:
            return await self.hunter_loot_table(ctx)
        
        await ctx.send("**__HUNTER__**")
        await ctx.send("**__Starting HP__**: 150")
        await ctx.send("**__Dodge Chance__**: 15%")
        await ctx.send("**__Block Chance__**: 15%")
        await ctx.send("**__Crit Chance__**: 15%")
        await ctx.send("**------------------------------------------------------**")
        await ctx.send("**__SPELLS/ABILITIES:__**")
        await ctx.send("**__Basic Attack__**: 10 Damage")
        await ctx.send("**__Trishot (Lvl 1)__**: Preform 3 Basic Attacks (Cooldown: 3 Turns)")
        await ctx.send("**__Precision (Lvl 2)__**: 100% Crit Chance on Next 3 Attacks (Cooldown: 6 Turns)")
        await ctx.send("**__Blind (Lvl 3)__**: 20 Damage, Reduce Enemy Accuracy 50% One Turn (Cooldown: 3 Turns)")
        await ctx.send("**__Snipe (Lvl 4)__**: 40 Damage, 100% Accuracy (Cooldown: 3 Turns)")
        await ctx.send("**__Rapidfire (Lvl 5)__**: Preform 5 Basic Attacks (Cooldown: 5 Turns)")
        await ctx.send("**__Bear (Lvl 6)__**: Bear Companion Does 30 Damage and Stuns the Enemy (Cooldown: 5 Turns)")
        await ctx.send("**__Headshot (Lvl 7)__**: 50 Damage, 5% Chance of Instant Kill (Cooldown: 5 Turns)")
        await ctx.send("**__Volley (Lvl 8)__**: 50 Damage, 50% Chance to Hit Again (Continuous) (Cooldown: 5 Turns)")
        await ctx.send("**__Powershot (Lvl 9)__**: 150 Damage, 30% Chance to get Interrupted (Cooldown: 10 Turns)")
        await ctx.send("**__Unload (Lvl 10)__**: Attack 10 Times, All Hits are Critical (Cooldown: 10 Turns)")

    async def hunter_loot_table(self, ctx):
        await ctx.send("**__HUNTER__**")
        await ctx.send("**Boots**")
        await ctx.send("Shitty Boots")
        await ctx.send("🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)")
        await ctx.send("🟦 Rare Boots of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Boots of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Boots of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Legs**")
        await ctx.send("Shitty Pants")
        await ctx.send("🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)")
        await ctx.send("🟦 Rare Pants of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Pants of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Pants of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Chest**")
        await ctx.send("Shitty Chainmail")
        await ctx.send("🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)")
        await ctx.send("🟦 Rare Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Gloves**")
        await ctx.send("Shitty Gloves")
        await ctx.send("🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)")
        await ctx.send("🟦 Rare Gloves of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Gloves of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Gloves of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Helmet**")
        await ctx.send("Shitty Hood")
        await ctx.send("🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)")
        await ctx.send("🟦 Rare Hood of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Hood of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Hood of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Main Hand Weapon**")
        await ctx.send("Shitty Bow")
        await ctx.send("🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)")
        await ctx.send("🟦 Rare Bow of Shooting Motherfuckers with Arrows (+10 Damage)")
        await ctx.send("🟪 Epic Bow of Shooting Motherfuckers with Arrows (+15 Damage,)")
        await ctx.send("🟨 Legendary Bow of Shooting Motherfuckers with Arrows (+20 Damage)")
        await ctx.send("**Off Hand**")
        await ctx.send("Shitty Quiver")
        await ctx.send("🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)")
        await ctx.send("🟦 Rare Quiver of Shooting Motherfuckers with Arrows (+2 Damage)")
        await ctx.send("🟪 Epic Quiver of Shooting Motherfuckers with Arrows (+3 Damage)")
        await ctx.send("🟨 Legendary Quiver of Shooting Motherfuckers with Arrows (+5 Damage)")

async def setup(bot):
    await bot.add_cog(Hunter(bot))
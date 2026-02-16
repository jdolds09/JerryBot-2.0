import discord
from discord.ext import commands


class Warrior(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Warrior function
    @commands.command()
    async def warrior(self, ctx, *args):

        if "loot" in args:
            return await self.warrior_loot_table(ctx)
        
        # Warrior
        await ctx.send("**__WARRIOR__**")
        await ctx.send("**__Starting HP__**: 200")
        await ctx.send("**__Dodge Chance__**: 10%")
        await ctx.send("**__Block Chance__**: 20%")
        await ctx.send("**__Crit Chance__**: 10%")
        await ctx.send("**------------------------------------------------------**")
        await ctx.send("**__SPELLS/ABILITIES:__**")
        await ctx.send("**__Basic Attack__**: 10 Damage")
        await ctx.send("**__Crush (Lvl 1)__**: 20 Damage 50% Chance to Stun (Cooldown: 3 Turns)")
        await ctx.send("**__Flurry (Lvl 2)__**: Preform 3 Basic Attacks (Cooldown: 3 Turns)")
        await ctx.send("**__ShieldBash (Lvl 3)__**: 30 Damage 50% Additional Chance to Block this Turn (Cooldown: 3 Turns)")
        await ctx.send("**__Bloodthirst (Lvl 4)__**: 30 Damage, Heal 30 HP (Cooldown: 3 Turns)")
        await ctx.send("**__Execute (Lvl 5)__**: 20 Damage, if Enemy HP is Below 30% Deal 60 Damage Instead (Cooldown: 1 Turns)")
        await ctx.send("**__Headbutt (Lvl 6)__**: 50 Damage, 30 Damage to Self (Cooldown: 3 Turns)")
        await ctx.send("**__Haymaker (Lvl 7)__**: 100 Damage, 30% Chance to Hit (Cooldown: 3 Turns)")
        await ctx.send("**__Whirlwind (Lvl 8)__**: 50 Damage, 50% Chance to Hit Again (Continuous) (Cooldown: 5 Turns)")
        await ctx.send("**__Retailiate (Lvl 9)__**: Take 3 Turns Worth of Damage, Deal 2x of Damage Taken (Cooldown: 10 Turns)")
        await ctx.send("**__Takedown (Lvl 10)__**: 150 Damage, 100 Damage to Self (Cooldown: 10 Turns)")

    async def warrior_loot_table(self, ctx):
        await ctx.send("**__WARRIOR__**")
        await ctx.send("**Boots**")
        await ctx.send("Shitty Boots")
        await ctx.send("🟩 Good Boots of Asskicking (+20 Max HP)")
        await ctx.send("🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Boots of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Boots of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Legs**")
        await ctx.send("Shitty Greaves")
        await ctx.send("🟩 Good Greaves of Asskicking (+20 Max HP)")
        await ctx.send("🟦 Rare Greaves of Asskicking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Greaves of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Greaves of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Chest**")
        await ctx.send("Shitty Chestplate")
        await ctx.send("🟩 Good Chestplate of Asskicking (+20 Max HP)")
        await ctx.send("🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Gloves**")
        await ctx.send("Shitty Gauntlets")
        await ctx.send("🟩 Good Gauntlets of Asskicking (+20 Max HP)")
        await ctx.send("🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Helmet**")
        await ctx.send("Shitty Helmet")
        await ctx.send("🟩 Good Helmet of Asskicking (+20 Max HP)")
        await ctx.send("🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Helmet of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Helmet of Asskicking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Main Hand Weapon**")
        await ctx.send("Shitty Sword")
        await ctx.send("🟩 Good Sword of Asskicking (+5 Damage)")
        await ctx.send("🟦 Rare Sword of Asskicking (+10 Damage)")
        await ctx.send("🟪 Epic Sword of Asskicking (+15 Damage,)")
        await ctx.send("🟨 Legendary Sword of Asskicking (+20 Damage)")
        await ctx.send("**Off Hand**")
        await ctx.send("Shitty Shield")
        await ctx.send("🟩 Good Shield of Asskicking (+1% Block Chance)")
        await ctx.send("🟦 Rare Shield of Asskicking (+3% Block Chance)")
        await ctx.send("🟪 Epic Shield of Asskicking (+5% Block Chance)")
        await ctx.send("🟨 Legendary Shield of Asskicking (+10% Block Chance)")

async def setup(bot):
    await bot.add_cog(Warrior(bot))
import discord
from discord.ext import commands


class Rogue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Rogue function
    @commands.command()
    async def rogue(self, ctx, *args):
        # Rogue
        if "loot" in args:
            return await self.rogue_loot_table(ctx)

        await ctx.send("**__ROGUE__**")
        await ctx.send("**__Starting HP__**: 150")
        await ctx.send("**__Dodge Chance__**: 20%")
        await ctx.send("**__Block Chance__**: 10%")
        await ctx.send("**__Crit Chance__**: 10%")
        await ctx.send("**------------------------------------------------------**")
        await ctx.send("**__SPELLS/ABILITIES:__**")
        await ctx.send("__Rogue Attacks Trigger Twice For Dual Wielding__")
        await ctx.send("**__Basic Attack__**: 10 Damage")
        await ctx.send("**__Gouge (Lvl 1)__**: 10 Damage, 50% Chance to Evade (Cooldown: 3 Turns)")
        await ctx.send("**__Stab (Lvl 2)__**: 20 Damage (Cooldown: 3 Turns)")
        await ctx.send("**__Sap (Lvl 3)__**: 10 Damage, 50% Chance to Stun (Cooldown: 3 Turns)")
        await ctx.send("**__Bleed (Lvl 4)__**: 20 Damage, Heal 20 HP (Cooldown: 5 Turns)")
        await ctx.send("**__Betrayal (Lvl 5)__**: 30 Damage, 30% Critical Strike (Cooldown: 5 Turns)")
        await ctx.send("**__Relentless (Lvl 6)__**: Your Next Ability Triggers Twice (once per fight)")
        await ctx.send("**__Counter (Lvl 7)__**: 20 Damage, for the rest of the fight, if you dodge an attack, you counterattack for 20 damage and interrupt the enemy's turn (Cooldown: Once per fight)")
        await ctx.send("**__Assassinate (Lvl 8)__**: 10 Damage. If Enemy Below 30% Max HP, 30% chance of Instant Kill (Cooldown: 1 Turns)")
        await ctx.send("**__Bladestorm (Lvl 9)__**: 25 Damage, 50% Chance to Retrigger Bladestorm (Continuous) (Cooldown: 10 Turns)")
        await ctx.send("**__Backstab (Lvl 10)__**: 50 Damage, 50% Critical Chance (Cooldown: 10 Turns)")

    async def rogue_loot_table(self, ctx):
        await ctx.send("**__ROGUE__**")
        await ctx.send("**Boots**")
        await ctx.send("Shitty Boots")
        await ctx.send("🟩 Good Boots of Shanking (+20 Max HP)")
        await ctx.send("🟦 Rare Boots of Shanking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Boots of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Boots of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Legs**")
        await ctx.send("Shitty Pants")
        await ctx.send("🟩 Good Pants of Shanking (+20 Max HP)")
        await ctx.send("🟦 Rare Pants of Shanking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Pants of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Pants of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Chest**")
        await ctx.send("Shitty Vest")
        await ctx.send("🟩 Good Vest of Shanking (+20 Max HP)")
        await ctx.send("🟦 Rare Vest of Shanking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Vest of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Vest of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Gloves**")
        await ctx.send("Shitty Gloves")
        await ctx.send("🟩 Good Gloves of Shanking (+20 Max HP)")
        await ctx.send("🟦 Rare Gloves of Shanking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Gloves of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Gloves of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Helmet**")
        await ctx.send("Shitty Hood")
        await ctx.send("🟩 Good Hood of Shanking (+20 Max HP)")
        await ctx.send("🟦 Rare Hood of Shanking (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Hood of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Hood of Shanking (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Main Hand Weapon**")
        await ctx.send("Shitty Dagger")
        await ctx.send("🟩 Good Dagger of Shanking (+1 Damage)")
        await ctx.send("🟦 Rare Dagger of Shanking (+3 Damage)")
        await ctx.send("🟪 Epic Dagger of Shanking (+5 Damage)")
        await ctx.send("🟨 Legendary Dagger of Shanking (+10 Damage)")
        await ctx.send("**Off Hand**")
        await ctx.send("Shitty Dagger")
        await ctx.send("🟩 Good Dagger of Shanking (+1 Damage)")
        await ctx.send("🟦 Rare Dagger of Shanking (+3 Damage)")
        await ctx.send("🟪 Epic Dagger of Shanking (+5 Damage)")
        await ctx.send("🟨 Legendary Dagger of Shanking (+10 Damage)")
        
async def setup(bot):
    await bot.add_cog(Rogue(bot))
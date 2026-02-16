import discord
from discord.ext import commands


class Mage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Mage function
    @commands.command()
    async def mage(self, ctx, *args):
        # Mage
        if "loot" in args:
            return await self.mage_loot_table(ctx)

        await ctx.send("**__MAGE__**")
        await ctx.send("**__Starting HP__**: 100")
        await ctx.send("**__Dodge Chance__**: 10%")
        await ctx.send("**__Block Chance__**: 10%")
        await ctx.send("**__Crit Chance__**: 20%")
        await ctx.send("**------------------------------------------------------**")
        await ctx.send("**__SPELLS/ABILITIES:__**")
        await ctx.send("**__Basic Attack__**: 10 Damage")
        await ctx.send("**__Fireball (Lvl 1)__**: Deal 20 Damage, 30% to Deal 20 More (Cooldown: 3 Turns)")
        await ctx.send("**__Frostbolt (Lvl 2)__**: Deal 20 Damage, 30% to freeze (Cooldown: 3 Turns)")
        await ctx.send("**__Iceblock (Lvl 3)__**: Become Invulnerable for 3 Turns and Heal 50 HP (Cooldown: 6 Turns)")
        await ctx.send("**__Lifesteal (Lvl 4)__**: Deal 30 Damage and Heal 30 HP (Cooldown: 3 Turns)")
        await ctx.send("**__Wildfire (Lvl 5)__**: Cast 5 Fireballs (Cooldown: 5 Turns)")
        await ctx.send("**__Blizzard (Lvl 6)__**: Cast 5 Frostbolts (Cooldown: 5 Turns)")
        await ctx.send("**__Evocation (Lvl 7)__**: Set all Cooldowns to 0 (Cooldown: Once per Fight)")
        await ctx.send("**__Lightning (Lvl 8)__**: 50 Damage, 50% to Cast Again (Continuous) (Cooldown: 5 Turns)")
        await ctx.send("**__Pyroblast (Lvl 9)__**: 150 Damage, 30% Chance of Being Interrupted (Cooldown: 10 Turns)")
        await ctx.send("**__Storm (Lvl 10)__**: Cast Fireball, Frostbolt, and Lightning (Cooldown: 10 Turns)")

    async def mage_loot_table(self, ctx):
        await ctx.send("**__MAGE__**")
        await ctx.send("**Boots**")
        await ctx.send("Shitty Boots")
        await ctx.send("🟩 Good Boots of Casting Spells and Shit (+20 Max HP)")
        await ctx.send("🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Legs**")
        await ctx.send("Shitty Pants")
        await ctx.send("🟩 Good Pants of Casting Spells and Shit (+20 Max HP)")
        await ctx.send("🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Chest**")
        await ctx.send("Shitty Robes")
        await ctx.send("🟩 Good Robes of Casting Spells and Shit (+20 Max HP)")
        await ctx.send("🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Gloves**")
        await ctx.send("Shitty Gloves")
        await ctx.send("🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)")
        await ctx.send("🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Helmet**")
        await ctx.send("Shitty Hood")
        await ctx.send("🟩 Good Hood of Casting Spells and Shit (+20 Max HP)")
        await ctx.send("🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block)")
        await ctx.send("🟪 Epic Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance)")
        await ctx.send("🟨 Legendary Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
        await ctx.send("**Main Hand Weapon**")
        await ctx.send("Shitty Staff")
        await ctx.send("🟩 Good Staff of Casting Spells and Shit (+5 Damage)")
        await ctx.send("🟦 Rare Staff of Casting Spells and Shit (+10 Damage)")
        await ctx.send("🟪 Epic Staff of Casting Spells and Shit (+15 Damage,)")
        await ctx.send("🟨 Legendary Staff of Casting Spells and Shit (+20 Damage)")
        await ctx.send("**Off Hand**")
        await ctx.send("Shitty Spellbook")
        await ctx.send("🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)")
        await ctx.send("🟦 Rare Spellbook of Casting Spells and Shit (+2 Damage)")
        await ctx.send("🟪 Epic Spellbook of Casting Spells and Shit (+3 Damage)")
        await ctx.send("🟨 Legendary Spellbook of Casting Spells and Shit (+5 Damage)")
        
async def setup(bot):
    await bot.add_cog(Mage(bot))
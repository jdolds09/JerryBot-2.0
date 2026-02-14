import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os


class Spells(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Spells function
    @commands.command(aliases=['abilities', 'cooldown', 'cooldowns', 'spellbook'])
    async def spells(self, ctx):
        # Connect to DB
        load_dotenv()
        try:
            db = mysql.connector.connect(host=os.getenv("DB_HOST"),
                                        user=os.getenv("DB_USER"),
                                        password=os.getenv("DB_PASSWORD"),
                                        database=os.getenv("DB_USER"),
                                        port = 3306,
                                        autocommit=True)
            
            cursor = db.cursor(dictionary=True) 
        except Exception as e:
            print(e)
            return await ctx.send("Error connecting to database.")

        except Exception as e:
            print(e)
            return await ctx.send("Error connecting to the database.")

        # Fetch user's character
        try:
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            # User doesn't have a character
            if not result:
                return await ctx.send("You don't have a character dumbass.")
            
        except Exception as e:
            print(e)
            return await ctx.send("Error grabbing character details")
        
        # Display warrior's current cooldowns
        if result['class'] == 'warrior':
            await ctx.send("**__ABILITIES:__**")
            await ctx.send(f"**Crush** Current Cooldown: {result['cooldown_1']}")
            if result['level'] > 1:
                await ctx.send(f"**Flurry** Current Cooldown: {result['cooldown_2']}")
            if result['level'] > 2:
                await ctx.send(f"**ShieldBash** Current Cooldown: {result['cooldown_3']}")
            if result['level'] > 3:
                await ctx.send(f"**Bloodthirst** Current Cooldown: {result['cooldown_4']}")
            if result['level'] > 4:
                await ctx.send(f"**Execute** Current Cooldown: {result['cooldown_5']}")
            if result['level'] > 5:
                await ctx.send(f"**Headbutt** Current Cooldown: {result['cooldown_6']}")
            if result['level'] > 6:
                await ctx.send(f"**Haymaker** Current Cooldown: {result['cooldown_7']}")
            if result['level'] > 7:
                await ctx.send(f"**Whirlwind** Current Cooldown: {result['cooldown_8']}")
            if result['level'] > 8:
                await ctx.send(f"**Retailiate** Current Cooldown: {result['cooldown_9']}")
            if result['level'] > 9:
                await ctx.send(f"**Takedown** Current Cooldown: {result['cooldown_10']}")

        # Display mage's current cooldowns
        elif result['class'] == 'mage':
            await ctx.send("**__SPELLS:__**")
            await ctx.send(f"**Fireball** Current Cooldown: {result['cooldown_1']}")
            if result['level'] > 1:
                await ctx.send(f"**Frostbolt** Current Cooldown: {result['cooldown_2']}")
            if result['level'] > 2:
                await ctx.send(f"**Iceblock** Current Cooldown: {result['cooldown_3']}")
            if result['level'] > 3:
                await ctx.send(f"**Lifesteal** Current Cooldown: {result['cooldown_4']}")
            if result['level'] > 4:
                await ctx.send(f"**Wildfire** Current Cooldown: {result['cooldown_5']}")
            if result['level'] > 5:
                await ctx.send(f"**Blizzard** Current Cooldown: {result['cooldown_6']}")
            if result['level'] > 6:
                await ctx.send(f"**Evocation** Current Cooldown: {result['cooldown_7']}")
            if result['level'] > 7:
                await ctx.send(f"**Lightning** Current Cooldown: {result['cooldown_8']}")
            if result['level'] > 8:
                await ctx.send(f"**Pyroblast** Current Cooldown: {result['cooldown_9']}")
            if result['level'] > 9:
                await ctx.send(f"**Storm** Current Cooldown: {result['cooldown_10']}")

        # Display rogue's current cooldowns
        elif result['class'] == 'rogue':
            await ctx.send("**__ABILITIES:__**")
            await ctx.send(f"**Gouge** Current Cooldown: {result['cooldown_1']}")
            if result['level'] > 1:
                await ctx.send(f"**Stab** Current Cooldown: {result['cooldown_2']}")
            if result['level'] > 2:
                await ctx.send(f"**Sap** Current Cooldown: {result['cooldown_3']}")
            if result['level'] > 3:
                await ctx.send(f"**Bleed** Current Cooldown: {result['cooldown_4']}")
            if result['level'] > 4:
                await ctx.send(f"**Betrayal** Current Cooldown: {result['cooldown_5']}")
            if result['level'] > 5:
                await ctx.send(f"**Relentless** Current Cooldown: {result['cooldown_6']}")
            if result['level'] > 6:
                await ctx.send(f"**Counter** Current Cooldown: {result['cooldown_7']}")
            if result['level'] > 7:
                await ctx.send(f"**Assassinate** Current Cooldown: {result['cooldown_8']}")
            if result['level'] > 8:
                await ctx.send(f"**Bladestorm** Current Cooldown: {result['cooldown_9']}")
            if result['level'] > 9:
                await ctx.send(f"**Backstab** Current Cooldown: {result['cooldown_10']}")

        # Display hunter's current cooldowns
        elif result['class'] == 'hunter':
            await ctx.send("**__ABILITIES:__**")
            await ctx.send(f"**Trishot** Current Cooldown: {result['cooldown_1']}")
            if result['level'] > 1:
                await ctx.send(f"**Precision** Current Cooldown: {result['cooldown_2']}")
            if result['level'] > 2:
                await ctx.send(f"**Blind** Current Cooldown: {result['cooldown_3']}")
            if result['level'] > 3:
                await ctx.send(f"**Snipe** Current Cooldown: {result['cooldown_4']}")
            if result['level'] > 4:
                await ctx.send(f"**Rapidfire** Current Cooldown: {result['cooldown_5']}")
            if result['level'] > 5:
                await ctx.send(f"**Bear** Current Cooldown: {result['cooldown_6']}")
            if result['level'] > 6:
                await ctx.send(f"**Headshot** Current Cooldown: {result['cooldown_7']}")
            if result['level'] > 7:
                await ctx.send(f"**Volley** Current Cooldown: {result['cooldown_8']}")
            if result['level'] > 8:
                await ctx.send(f"**Powershot** Current Cooldown: {result['cooldown_9']}")
            if result['level'] > 9:
                await ctx.send(f"**Unload** Current Cooldown: {result['cooldown_10']}")
            
        # Display gambler's current cooldowns
        else:
            await ctx.send("**__SPELLS:__**")
            await ctx.send(f"**Deal (Lvl 1)** Cooldown: {result['cooldown_1']}")
            if result['level'] > 1:
                await ctx.send(f"**Jack (Lvl 2)** Cooldown: {result['cooldown_2']}")
            if result['level'] > 2:
                await ctx.send(f"**Queen (Lvl 3)** Cooldown: {result['cooldown_3']}")
            if result['level'] > 3:
                await ctx.send(f"**King (Lvl 4)** Cooldown: {result['cooldown_4']}")
            if result['level'] > 4:
                await ctx.send(f"**Ace (Lvl 5)** Cooldown: {result['cooldown_5']}")
            if result['level'] > 5:
                await ctx.send(f"**Joker (Lvl 6)** Cooldown: {result['cooldown_6']}")
            if result['level'] > 6:
                await ctx.send(f"**Straight (Lvl 7)** Cooldown: {result['cooldown_7']}")
            if result['level'] > 7:
                await ctx.send(f"**Flush (Lvl 8)** Cooldown: {result['cooldown_8']}")
            if result['level'] > 8:
                await ctx.send(f"**Blackjack (Lvl 9)** Cooldown: {result['cooldown_9']}")
            if result['level'] > 9:
                await ctx.send(f"**Roulette (Lvl 10)** Cooldown: {result['cooldown_10']}")

async def setup(bot):
    await bot.add_cog(Spells(bot))
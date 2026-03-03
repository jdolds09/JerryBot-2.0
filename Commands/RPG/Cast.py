import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random
import asyncio

class Cast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enemy = {}
        self.active_battle = False
        self.participants = []
        self.participant_names = []
        self.beserk_damage = 10
        self.user_died = False
        self.classes = ["warrior", "hunter", "mage", "rogue", "gambler"]
        self.slots = ["boots", "legs", "chest", "gloves", "helmet", "main_hand", "off_hand"]
        self.loot = [[["🟩 Good Boots of Asskicking (+ 20 Max HP)", "🟩 Good Greaves of Asskicking (+ 20 Max HP)", 
                                  "🟩 Good Chestplate of Asskicking (+ 20 Max HP)", "🟩 Good Gauntlets of Asskicking (+ 20 Max HP)",
                                  "🟩 Good Helmet of Asskicking (+ 20 Max HP)", "🟩 Good Sword of Asskicking (+5 Damage)", 
                                  "🟩 Good Shield of Asskicking (+1% Block Chance)"], ["🟩 Good Boots of Casting Spells and Shit (+ 20 Max HP)", "🟩 Good Pants of Casting Spells and Shit (+ 20 Max HP)", 
                                  "🟩 Good Robes of Casting Spells and Shit (+ 20 Max HP)", "🟩 Good Gloves of Casting Spells and Shit (+ 20 Max HP)",
                                  "🟩 Good Hood of Casting Spells and Shit (+ 20 Max HP)", "🟩 Good Staff of Casting Spells and Shit (+5 Damage)", 
                                  "🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)"], ["🟩 Good Boots of Shooting Motherfuckers with Arrows (+ 20 Max HP)", "🟩 Good Pants of Shooting Motherfuckers with Arrows (+ 20 Max HP)", 
                                  "🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+ 20 Max HP)", "🟩 Good Gloves of Shooting Motherfuckers with Arrows (+ 20 Max HP)",
                                  "🟩 Good Hood of Shooting Motherfuckers with Arrows (+ 20 Max HP)", "🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)", 
                                  "🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)"], ["🟩 Good Boots of Shanking (+ 20 Max HP)", "🟩 Good Pants of Shanking(+ 20 Max HP)", 
                                  "🟩 Good Vest of Shanking (+ 20 Max HP)", "🟩 Good Gloves of Shanking (+ 20 Max HP)",
                                  "🟩 Good Hood of Shanking (+ 20 Max HP)", "🟩 Good Dagger of Shanking (+1 Damage)", 
                                  "🟩 Good Dagger of Shanking (+1 Damage)"], ["🟩 Good Boots of Luck (+ 20 Max HP)", "🟩 Good Pants of Luck(+ 20 Max HP)", 
                                  "🟩 Good Jacket of Luck (+ 20 Max HP)", "🟩 Good Gloves of Luck (+ 20 Max HP)",
                                  "🟩 Good Fedora of Luck (+ 20 Max HP)", "🟩 Good Trinket of Luck (+5% Chance of Success)", 
                                  "🟩 Good Charm of Luck (+1% Chance of Success)"]], 
                                  [["🟦 Rare Boots of Asskicking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Greaves of Asskicking (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Chestplate of Asskicking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Gauntlets of Asskicking (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Helmet of Asskicking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Sword of Asskicking (+10 Damagee)", 
                                  "🟦 Rare Shield of Asskicking (+3% Block Chance)"], ["🟦 Rare Boots of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Pants of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Robes of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Gloves of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Hood of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Staff of Casting Spells and Shit (+10 Damagee)", 
                                  "🟦 Rare Spellbook of Casting Spells and Shit (+2 Damage)"], ["🟦 Rare Boots of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Pants of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Chainmail of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Gloves of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Hood of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Bow of Shooting Motherfuckers with Arrows (+10 Damage)", 
                                  "🟦 Rare Quiver of Shooting Motherfuckers with Arrows (+2 Damage)"], ["🟦 Rare Boots of Shanking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Pants of Shanking (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Vest of Shanking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Gloves of Shanking (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Hood of Shanking (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Dagger of Shanking (+3 Damage)", 
                                  "🟦 Rare Dagger of Shanking (+3 Damage)"], ["🟦 Rare Boots of Luck (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Pants of Luck (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Jacket of Luck (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Gloves of Luck (+ 20 Max HP, +1% Dodge & Block)",
                                  "🟦 Rare Fedora of Luck (+ 20 Max HP, +1% Dodge & Block)", 
                                  "🟦 Rare Trinket of Luck (+10% Chance of Success)", 
                                  "🟦 Rare Charm of Luck (+2% Chance of Success)"]], 
                                  [["🟪 Epic Boots of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Greaves of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Chestplate of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Gauntlets of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Helmet of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Sword of Asskicking (+15 Damage)", 
                                  "🟪 Epic Shield of Asskicking (+5% Block Chance)"], ["🟪 Epic Boots of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Pants of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Robes of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Gloves of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Hood of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Staff of Casting Spells and Shit (+15 Damage)", 
                                  "🟪 Epic Spellbook of Casting Spells and Shit (+3 Damage)"], ["🟪 Epic Boots of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Pants of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Chainmail of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Gloves of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Hood of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Bow of Shooting Motherfuckers with Arrows (+15 Damage)", 
                                  "🟪 Epic Quiver of Shooting Motherfuckers with Arrows (+3 Damage)"], ["🟪 Epic Boots of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Pants of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Vest of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Gloves of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Hood of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Dagger of Shanking (+5 Damage)", 
                                  "🟪 Epic Dagger of Shanking (+5 Damage)"], ["🟪 Epic Boots of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Pants of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Jacket of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Gloves of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)",
                                  "🟪 Epic Fedora of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance)", 
                                  "🟪 Epic Trinket of Luck (+15% Chance of Success)", 
                                  "🟪 Epic Charm of Luck (+3% Chance of Success)"]], 
                                  [["🟨 Legendary Boots of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Greaves of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Chestplate of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Gauntlets of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Helmet of Asskicking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Sword of Asskicking (+20 Damage)", 
                                       "🟨 Legendary Shield of Asskicking (+10% Block Chance)"], ["🟨 Legendary Boots of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Pants of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Robes of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Gloves of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Hood of Casting Spells and Shit (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Staff of Casting Spells and Shit (+20 Damage)", 
                                       "🟨 Legendary Spellbook of Casting Spells and Shit (+5 Damage)"], ["🟨 Legendary Boots of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Pants of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Chainmail of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Gloves of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Hood of Shooting Motherfuckers with Arrows (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Bow of Shooting Motherfuckers with Arrows (+20 Damage)", 
                                       "🟨 Legendary Quiver of Shooting Motherfuckers with Arrows (+5 Damage)"], ["🟨 Legendary Boots of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Pants of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Vest of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Gloves of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Hood of Shanking (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Dagger of Shanking (+10 Damage)", 
                                       "🟨 Legendary Dagger of Shanking (+10 Damage)"], ["🟨 Legendary Boots of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Pants of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Jacket of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Gloves of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)",
                                       "🟨 Legendary Fedora of Luck (+ 20 Max HP, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)", 
                                       "🟨 Legendary Dagger of Luck (+20% Chance of Success)", 
                                       "🟨 Legendary Dagger of Luck (+5% Chance of Success)"]]]
        self.highest_loot_roll = None
        self.loot_winner = None

    # Cast function
    @commands.command(aliases=['attack', 'spell'])
    async def cast(self, ctx, *args):
        # Reset user died
        self.user_died = False

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
        
        # Guild id
        guild_id = ctx.guild.id

        # Get the enemy details
        battle_cog = self.bot.get_cog("Combat")
        if not battle_cog.encounter or not battle_cog.encounter[guild_id]['active_battle']:
            return await ctx.send("There is no active battle dumbass.")
        
        if not self.active_battle:
            self.enemy = battle_cog.enemy
            self.active_battle = True
        
        # User wants to basic attack
        if len(args) == 0 or 'basic' in args[0].lower():
            await self.user_basic_attack(ctx, result, cursor, battle_cog)

        # User wants to use crush
        elif 'crush' in args[0].lower():
            await self.user_crush_attack(ctx, result, cursor, battle_cog)

        # User wants to use flurry
        elif 'flurry' in args[0].lower():
            await self.user_flurry_attack(ctx, result, cursor, battle_cog)

        # User wants to use shieldbash
        elif 'shieldbash' in args[0].lower():
            await self.user_shieldbash_attack(ctx, result, cursor, battle_cog)

        # User wants to use bloodthirst
        elif 'bloodthirst' in args[0].lower():
            await self.user_bloodthirst_attack(ctx, result, cursor, battle_cog)

        # User wants to use execute
        elif 'execute' in args[0].lower():
            await self.user_execute_attack(ctx, result, cursor, battle_cog)
        
        # User wants to use headbutt
        elif 'headbutt' in args[0].lower():
            await self.user_headbutt_attack(ctx, result, cursor, battle_cog)

        # User wants to use haymaker
        elif 'haymaker' in args[0].lower():
            await self.user_haymaker_attack(ctx, result, cursor, battle_cog)

        # User wants to use whirlwind
        elif 'whirlwind' in args[0].lower():
            await self.user_whirlwind_attack(ctx, result, cursor, battle_cog)

        # User wants to use retaliate
        elif 'retaliate' in args[0].lower():
            await self.user_retaliate_attack(ctx, result, cursor, battle_cog)

        # User wants to use takedown
        elif 'takedown' in args[0].lower():
            await self.user_takedown_attack(ctx, result, cursor, battle_cog)

        # User wants to use trishot
        elif 'trishot' in args[0].lower():
            await self.user_trishot_attack(ctx, result, cursor, battle_cog)
        
        # User wants to use precision
        elif 'precision' in args[0].lower():
            await self.user_precision_attack(ctx, result, cursor, battle_cog)

        # User wants to use blind
        elif 'blind' in args[0].lower():
            await self.user_blind_attack(ctx, result, cursor, battle_cog)

        # User wants to use snipe
        elif 'snipe' in args[0].lower():
            await self.user_snipe_attack(ctx, result, cursor, battle_cog)

        # User wants to use rapidfire
        elif 'rapidfire' in args[0].lower():
            await self.user_rapidfire_attack(ctx, result, cursor, battle_cog)

        # User wants to use bear
        elif 'bear' in args[0].lower():
            await self.user_bear_attack(ctx, result, cursor, battle_cog)

        # User wants to use headshot
        elif 'headshot' in args[0].lower():
            await self.user_headshot_attack(ctx, result, cursor, battle_cog)

        # User wants to use volley
        elif 'volley' in args[0].lower():
            await self.user_volley_attack(ctx, result, cursor, battle_cog)

        # User wants to use powershot
        elif 'powershot' in args[0].lower():
            await self.user_powershot_attack(ctx, result, cursor, battle_cog)

        # User wants to use unload
        elif 'unload' in args[0].lower():
            await self.user_unload_attack(ctx, result, cursor, battle_cog)

        # User wants to use deal
        elif 'deal' in args[0].lower():
            await self.user_deal_attack(ctx, result, cursor, battle_cog)

        # User wants to use jack
        elif 'jack' in args[0].lower():
            await self.user_jack_attack(ctx, result, cursor, battle_cog)

        # User wants to use queen
        elif 'queen' in args[0].lower():
            await self.user_queen_attack(ctx, result, cursor, battle_cog)

        # User wants to use king
        elif 'king' in args[0].lower():
            await self.user_king_attack(ctx, result, cursor, battle_cog)

        # User wants to use ace
        elif 'ace' in args[0].lower():
            await self.user_ace_attack(ctx, result, cursor, battle_cog)

        # User wants to use straight
        elif 'straight' in args[0].lower():
            await self.user_straight_attack(ctx, result, cursor, battle_cog)

        # User wants to use flush
        elif 'flush' in args[0].lower():
            await self.user_flush_attack(ctx, result, cursor, battle_cog)

        # User wants to use blackjack
        elif 'blackjack' in args[0].lower():
            await self.user_blackjack_attack(ctx, result, cursor, battle_cog)

        # User wants to use roulette
        elif 'roulette' in args[0].lower():
            await self.user_roulette_attack(ctx, result, cursor, battle_cog)

        # User wants to use fireball
        elif 'fireball' in args[0].lower():
            await self.user_fireball_attack(ctx, result, cursor, battle_cog)

        # User wants to use frostbolt
        elif 'frostbolt' in args[0].lower():
            await self.user_frostbolt_attack(ctx, result, cursor, battle_cog)

        # User wants to use iceblock
        elif 'iceblock' in args[0].lower():
            await self.user_iceblock_attack(ctx, result, cursor, battle_cog)

        # User wants to use lifesteal
        elif 'lifesteal' in args[0].lower():
            await self.user_lifesteal_attack(ctx, result, cursor, battle_cog)

        # User wants to use wildfire
        elif 'wildfire' in args[0].lower():
            await self.user_wildfire_attack(ctx, result, cursor, battle_cog)

        # User wants to use blizzard
        elif 'blizzard' in args[0].lower():
            await self.user_blizzard_attack(ctx, result, cursor, battle_cog)

        # User wants to use evocation
        elif 'evocation' in args[0].lower():
            await self.user_evocation_attack(ctx, result, cursor, battle_cog)

        # User wants to use lightning
        elif 'lightning' in args[0].lower():
            await self.user_lightning_attack(ctx, result, cursor, battle_cog)

        # User wants to use pyroblast
        elif 'pyroblast' in args[0].lower():
            await self.user_pyroblast_attack(ctx, result, cursor, battle_cog)

        # User wants to use storm
        elif 'storm' in args[0].lower():
            await self.user_storm_attack(ctx, result, cursor, battle_cog) 

        # User wants to use gouge
        elif 'gouge' in args[0].lower():
            await self.user_gouge_attack(ctx, result, cursor, battle_cog)

        # User wants to use stab
        elif 'stab' in args[0].lower():
            await self.user_stab_attack(ctx, result, cursor, battle_cog)

        # User wants to use sap
        elif 'sap' in args[0].lower():
            await self.user_sap_attack(ctx, result, cursor, battle_cog)

        # User wants to use bleed
        elif 'bleed' in args[0].lower():
            await self.user_bleed_attack(ctx, result, cursor, battle_cog)

        # User wants to use betrayal
        elif 'betrayal' in args[0].lower():
            await self.user_betrayal_attack(ctx, result, cursor, battle_cog)

        # User wants to use relentless
        elif 'relentless' in args[0].lower():
            await self.user_relentless_attack(ctx, result, cursor, battle_cog)

        # User wants to use counter
        elif 'counter' in args[0].lower():
            await self.user_counter_attack(ctx, result, cursor, battle_cog)

        # User wants to use assassinate
        elif 'assassinate' in args[0].lower():
            await self.user_assassinate_attack(ctx, result, cursor, battle_cog)

        # User wants to use bladestorm
        elif 'bladestorm' in args[0].lower():
            await self.user_bladestorm_attack(ctx, result, cursor, battle_cog)

        # User wants to use backstab
        elif 'backstab' in args[0].lower():
            await self.user_backstab_attack(ctx, result, cursor, battle_cog)

        # User wants to run
        elif 'run' in args[0].lower():
            await self.user_run(ctx, result, cursor, battle_cog)    

        else:
            return await ctx.send("Invalid attack dumbass.")
        
    # --------------------------- BASIC ATTACK --------------------------------------

    async def user_basic_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Dodge and Block booleans
        dodge = False
        block = False

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'basic', 0)

        if result['class'] == "gambler":
            # Check to see if Gambler failed
            gambler_random = random.randint(1, 100)
            await ctx.send(f"{ctx.author.name}'s basic attack was a...")

            # Gambler failed and hurt themself
            if gambler_random < 11 - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send("**Failure!**")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name} hurt themself for 5 damage!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                # Gambler died
                if result['current_hp'] - 5 <= 0:
                    file_path = f"Images/respects.gif"
                    picture = discord.File(file_path)
                    await ctx.send(file=picture)
                    for participant in self.participants:
                        if participant['username'] == ctx.author.name:
                            result = participant
                            break
                    self.participants.remove(result)
                    self.participant_names.remove(result['username'])
                    # Delete character
                    try:
                        cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        await ctx.send(f"**{ctx.author.name}** has died!")
                        return await ctx.send("----------------------------------------------")
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error deleting character.")
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 5}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 5 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        result = cursor.fetchone()
                        return await ctx.send("----------------------------------------------")
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
                    
            # Gambler's basic attack succeeds
            else:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send("**Success!**")

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            dodge = True
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack missed!")
            if result['relentless_active'] == 0 and result['class'] != "rogue":
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            block = True
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack was blocked!")
            if result['relentless_active'] == 0 and result['class'] != "rogue":
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
        
        if not dodge and not block:
            # Calculate damage
            damage = 10 + result['main_hand_damage'] + result['off_hand_damage']
            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                damage *= 2
                if result['precision_active'] > 0:
                    cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
            
            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

        if result['class'] == "rogue":
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                dodge = True
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name}'s attack missed!")
                if result['relentless_active'] == 0:
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                block = True
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name}'s attack was blocked!")
                if result['relentless_active'] == 0:
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']
                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                    damage *= 2
                    if result['precision_active'] > 0:
                        cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        result = cursor.fetchone()
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
                
                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # If relentless active, attack again
        if result['relentless_active'] > 0:
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)            
            await ctx.send(f"{ctx.author.name} is relentless and attacks again!")
            await ctx.send("----------------------------------------------")
            await self.user_basic_attack(ctx, result, cursor, battle_cog)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # --------------------------- WARRIOR ABILITIES --------------------------------------

    # Warrior crush attack
    async def user_crush_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Crush attack!")
        # Check to see if crush is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Crush attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 20 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Check to see if user stunned the enemy
        stun_check = random.randint(1, 100)
        if stun_check <= 50:
            stun = True
            await ctx.send(f"{result['username']} stunned the {self.enemy[ctx.guild.id]['name']}!")
            await ctx.send("----------------------------------------------")
        else:
            await ctx.send("----------------------------------------------")
            stun = False

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, stun)

    # Warrior flurry attack
    async def user_flurry_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Flurry attack!")
        if result['level'] < 2:
            return await ctx.send("You need to be at least level 2 to use the Flurry attack!")

        # Check to see if flurry is on cooldown
        if result['cooldown_2'] > 0:
            return await ctx.send(f"{result['username']}'s Flurry attack is on cooldown for {result['cooldown_2']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_2', 3)

        for _ in range(3):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage
                
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior shieldbash attack
    async def user_shieldbash_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Shieldbash attack!")
        if result['level'] < 3:
            return await ctx.send("You need to be at least level 3 to use the Shieldbash attack!")

        # Check to see if shieldbash is on cooldown
        if result['cooldown_3'] > 0:
            return await ctx.send(f"{result['username']}'s Shieldbash attack is on cooldown for {result['cooldown_3']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 3)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 30 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has a 50% greater chance to block the next attack!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Activate shieldbash
        cursor.execute(f"UPDATE Characters SET shieldbash_active = 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior bloodthirst attack
    async def user_bloodthirst_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Bloodthirst attack!")
        if result['level'] < 4:
            return await ctx.send("You need to be at least level 4 to use the Bloodthirst attack!")

        # Check to see if bloodthirst is on cooldown
        if result['cooldown_4'] > 0:
            return await ctx.send(f"{result['username']}'s Bloodthirst attack is on cooldown for {result['cooldown_4']} more turns!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_4', 3)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 30 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Heal for damage done
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} healed for **{damage}** HP!")
        # Update user HP
        if result['current_hp'] + damage >= result['max_hp']:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
        else:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior execute attack
    async def user_execute_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Execute attack!")
        if result['level'] < 5:
            return await ctx.send("You need to be at least level 5 to use the Execute attack!")

        # Check to see if execute is on cooldown
        if result['cooldown_5'] > 0:
            return await ctx.send(f"{result['username']}'s Execute attack is on cooldown for {result['cooldown_5']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_5', 1)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        if self.enemy[ctx.guild.id]['current_hp'] / self.enemy[ctx.guild.id]['max_hp'] <= 0.3:
            damage = 60 + result['main_hand_damage']
        else:
            damage = 20 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior headbutt attack
    async def user_headbutt_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Headbutt attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Headbutt attack!")

        # Check to see if headbutt is on cooldown
        if result['cooldown_6'] > 0:
            return await ctx.send(f"{result['username']}'s Headbutt attack is on cooldown for {result['cooldown_6']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 2)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 50 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has also done 30 damage to themself!")

        # Deal headbutt damage to user
        if result['current_hp'] - 30 <= 0:
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                return await ctx.send(f"**{ctx.author.name}** has died!")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        else:
            # Display current HP
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 30 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior haymaker attack
    async def user_haymaker_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Haymaker attack!")
        if result['level'] < 7:
            return await ctx.send("You need to be at least level 7 to use the Haymaker attack!")
        
        # Check to see if haymaker is on cooldown
        if result['cooldown_7'] > 0:
            return await ctx.send(f"{result['username']}'s Haymaker attack is on cooldown for {result['cooldown_7']} more turns!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_7', 3)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
        
        # Check to see if warrior missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} missed the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 100 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

         # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior whirlwind attack
    async def user_whirlwind_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Whirlwind attack!")
        if result['level'] < 8:
            return await ctx.send("You need to be at least level 8 to use the Whirlwind attack!")

        # Check to see if whirlwind is on cooldown
        if result['cooldown_8'] > 0:
            return await ctx.send(f"{result['username']}'s Whirlwind attack is on cooldown for {result['cooldown_8']} more turns!")

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        whirlwind = True

        while whirlwind:
            # Calculate damage
            damage = 50 + result['main_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} is still whirling and attacks again!")
            else:
                whirlwind = False

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior retaliate attack
    async def user_retaliate_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Retaliate attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Retaliate attack!")

        # Check to see if retaliate is on cooldown
        if result['cooldown_9'] > 0:
            return await ctx.send(f"{result['username']}'s Retaliate attack is on cooldown for {result['cooldown_9']} more turns!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_9', 10)

        # Get warrior's current health
        current_health = result['current_hp']
        
        # Enemy attacks 3 times
        await self.choose_enemy_attack(ctx, battle_cog, result, cursor)
        await self.choose_enemy_attack(ctx, battle_cog, result, cursor)
        await self.choose_enemy_attack(ctx, battle_cog, result, cursor)

        if self.user_died == False:
            # Calculate damage
            result = cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            damage = (current_health - result['current_hp']) * 2

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} retaliated and dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!") 

             # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")      

            await ctx.send("----------------------------------------------")

            # Check to see if enemy died
            await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Warrior takedown attack
    async def user_takedown_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "warrior":
            return await ctx.send("Only warriors can use the Takedown attack!")
        if result['level'] < 10:
            return await ctx.send("You need to be at least level 10 to use the Takedown attack!")

        # Check to see if takedown is on cooldown
        if result['cooldown_10'] > 0:
            return await ctx.send(f"{result['username']}'s Takedown attack is on cooldown for {result['cooldown_10']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 150 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has also done 100 damage to themself!")

        # Deal takedown damage to user
        if result['current_hp'] - 100 <= 0:
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                return await ctx.send(f"**{ctx.author.name}** has died!")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        else:
            # Display current HP
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 100}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 100 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # --------------------------- HUNTER ABILITIES --------------------------------------

    # Hunter trishot attack
    async def user_trishot_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Trishot attack!")
        
        # Check to see if trishot is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Trishot attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        for _ in range(3):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                    damage *= 2
                    if result['precision_active'] > 0:
                        cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        result = cursor.fetchone()
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter precision attack
    async def user_precision_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Precision attack!")
        if result['level'] < 2:
            return await ctx.send("You need to be at least level 2 to use the Precision attack!")

        # Check to see if precision attack is on cooldown
        if result['cooldown_2'] > 0:
            return await ctx.send(f"{result['username']}'s Precision attack is on cooldown for {result['cooldown_2']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_2', 3)

        # Set precision to 3
        cursor.execute(f"UPDATE Characters SET precision_active = 3 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} is precise and their next 3 attacks will be critical hits!")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter blind attack
    async def user_blind_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Blind attack!")
        if result['level'] < 3:
            return await ctx.send("You need to be at least level 3 to use the Blind attack!")
        
        # Check to see if blind is on cooldown
        if result['cooldown_3'] > 0:
            return await ctx.send(f"{result['username']}'s Blind attack is on cooldown for {result['cooldown_3']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 3)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Output blind message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} has been blinded and has an additional 50% chance to miss their next attack!")
        cursor.execute(f"UPDATE Characters SET gouge_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter snipe attack
    async def user_snipe_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Precision attack!")
        if result['level'] < 4:
            return await ctx.send("You need to be at least level 4 to use the Precision attack!")
        
        # Check to see if snipe is on cooldown
        if result['cooldown_4'] > 0:
            return await ctx.send(f"{result['username']}'s Snipe attack is on cooldown for {result['cooldown_4']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_4', 3)

        # Calculate damage
        damage = 40 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter rapidfire attack
    async def user_rapidfire_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Rapidfire attack!")
        if result['level'] < 5:
            return await ctx.send("You need to be at least level 5 to use the Rapidfire attack!")
        
        # Check to see if rapidfire is on cooldown
        if result['cooldown_5'] > 0:
            return await ctx.send(f"{result['username']}'s Rapidfire attack is on cooldown for {result['cooldown_5']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_5', 5)

        for _ in range(5):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                    damage *= 2
                    if result['precision_active'] > 0:
                        cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        result = cursor.fetchone()
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter bear attack
    async def user_bear_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Bear attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Bear attack!")
        
        # Check to see if bear attack is on cooldown
        if result['cooldown_6'] > 0:
            return await ctx.send(f"{result['username']}'s Bear attack is on cooldown for {result['cooldown_6']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 5)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 30

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s bear companion dealt **{damage}** damage and stunned the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, True)

    # Hunter headshot attack
    async def user_headshot_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Headshot attack!")
        if result['level'] < 7:
            return await ctx.send("You need to be at least level 7 to use the Headshot attack!")
        
        # Check to see if headshot is on cooldown
        if result['cooldown_7'] > 0:
            return await ctx.send(f"{result['username']}'s Headshot attack is on cooldown for {result['cooldown_7']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_7', 5)

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Check to see if hunter insta killed the enemy
        instakill_check = random.randint(1, 100)
        if instakill_check <= 5:
            self.enemy[ctx.guild.id]['current_hp'] = 0
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} instantly killed the {self.enemy[ctx.guild.id]['name']} with a headshot!")

        else:
            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter volley attack
    async def user_volley_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Volley attack!")
        if result['level'] < 8:
            return await ctx.send("You need to be at least level 8 to use the Volley attack!")
        
        # Check to see if volley is on cooldown
        if result['cooldown_8'] > 0:
            return await ctx.send(f"{result['username']}'s Volley attack is on cooldown for {result['cooldown_8']} more turns!")

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        volley = True

        while volley:
            # Calculate damage
            damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                damage *= 2
                if result['precision_active'] > 0:
                    cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} volley strikes again!")
            else:
                volley = False

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter powershot attack
    async def user_powershot_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Powershot attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Powershot attack!")
        
        # Check to see if powershot is on cooldown
        if result['cooldown_9'] > 0:
            return await ctx.send(f"{result['username']}'s Powershot attack is on cooldown for {result['cooldown_9']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_9', 10)
        
        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 150 + result['main_hand_damage'] + result['off_hand_damage']

        # Check to see if hunter missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s Powershot was interrupted!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                result = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")
        
        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Hunter unload attack
    async def user_unload_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Unload attack!")
        if result['level'] < 10:
            return await ctx.send("You need to be at least level 10 to use the Unload attack!")
        
        # Check to see if unload is on cooldown
        if result['cooldown_10'] > 0:
            return await ctx.send(f"{result['username']}'s Unload attack is on cooldown for {result['cooldown_10']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)

        for _ in range(10):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = (10 + result['main_hand_damage'] + result['off_hand_damage']) * 2

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # --------------------------- GAMBLER ABILITIES --------------------------------------

    # Gambler deal attack
    async def user_deal_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Deal attack!")
        
        # Check to see if deal is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Deal attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        # Check to see how many times deal attacks
        deal_check = random.randint(1, 10)
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt {deal_check} attacks!")

        for _ in range(deal_check):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage
                
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler jack attack
    async def user_jack_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Jack attack!")
        if result['level'] < 2:
            return await ctx.send("You need to be at least level 2 to use the Jack attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_2', 0)

        # Check to see if jack attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Jack attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 20 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 10 damage!")
            # Gambler died
            if result['current_hp'] - 10 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 10}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 10 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 20

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler queen attack
    async def user_queen_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Queen attack!")
        if result['level'] < 3:
            return await ctx.send("You need to be at least level 3 to use the Queen attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 0)

        # Check to see if queen attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Queen attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 30 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 20 damage!")
            # Gambler died
            if result['current_hp'] - 20 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 50

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler king attack
    async def user_king_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the King attack!")
        if result['level'] < 4:
            return await ctx.send("You need to be at least level 4 to use the King attack!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_4', 0)

        # Check to see if king attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s King attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 40 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 30 damage!")
            # Gambler died
            if result['current_hp'] - 30 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 30 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 80

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler Ace attack
    async def user_ace_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Ace attack!")
        if result['level'] < 5:
            return await ctx.send("You need to be at least level 5 to use the Ace attack!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_5', 0)

        # Check to see if ace attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Ace attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 50 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 40 damage!")
            # Gambler died
            if result['current_hp'] - 40 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 40}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 40 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 100

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler joker attack
    async def user_joker_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Joker attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Joker attack!")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 0)

        # Check to see if joker attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Joker attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 60 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 50 damage!")
            # Gambler died
            if result['current_hp'] - 50 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 50}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 50 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 120

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler straight attack
    async def user_straight_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Straight attack!")
        if result['level'] < 7:
            return await ctx.send("You need to be at least level 7 to use the Straight attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_7', 0)

        # Check to see if straight attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Straight attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 70 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 60 damage!")
            # Gambler died
            if result['current_hp'] - 60 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 60}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 60 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 150

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler flush attack
    async def user_flush_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Flush attack!")
        if result['level'] < 8:
            return await ctx.send("You need to be at least level 8 to use the Flush attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 0)

        # Check to see if flush attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Flush attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 80 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 70 damage!")
            # Gambler died
            if result['current_hp'] - 70 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 70}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 70 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 200

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler blackjack attack
    async def user_blackjack_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Blackjack attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Blackjack attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_9', 0)

        # Check to see if blackjack attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s Blackjack attack was a...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 90 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Failure!**")
            await ctx.send(f"{ctx.author.name} hurt themself for 80 damage!")
            # Gambler died
            if result['current_hp'] - 80 <= 0:
                file_path = f"Images/respects.gif"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                for participant in self.participants:
                    if participant['username'] == ctx.author.name:
                        result = participant
                        break
                self.participants.remove(result)
                self.participant_names.remove(result['username'])
                # Delete character
                try:
                    cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    return await ctx.send("----------------------------------------------")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error deleting character.")
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 80}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 80 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    result = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send("**Success!**")
            # Calculate damage
            damage = 300

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Gambler roulette attack
    async def user_roulette_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Roulette attack!")
        if result['level'] < 10:
            return await ctx.send("You need to be at least level 10 to use the Roulette attack!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 0)

        # Check to see if roulette attack hits
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has bet it all on black!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send("The wheel is spinning...")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send("The ball lands on...")
        gambler = random.randint(1, 100)

        # Gambler's attack fails
        if gambler <= 50:
            async with ctx.typing():
                await asyncio.sleep(5)
            await ctx.send("**RED!**")
            await ctx.send(f"{ctx.author.name} has died!")
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                await ctx.send(f"**{ctx.author.name}** has died!")
                return await ctx.send("----------------------------------------------")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(5)
            await ctx.send("**BLACK!**")

            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The gambler has killed the {self.enemy[ctx.guild.id]['name']}!")
            
            self.enemy[ctx.guild.id]['current_hp'] = 0

        await ctx.send("----------------------------------------------")

        # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # --------------------------- MAGE ABILITIES --------------------------------------

    # Mage fireball attack
    async def user_fireball_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Fireball attack!")
        
        # Check to see if fireball is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Fireball attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)
        
        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Check to see if fireball burned
        burn_check = random.randint(1, 100)
        if burn_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was burned for 20 additional damage!")
            damage += 20

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage frostbolt attack
    async def user_frostbolt_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Frostbolt attack!")
        if result['level'] < 2:
            return await ctx.send("You need to be at least level 2 to use the Frostbolt attack!")
        
        # Check to see if frostbolt is on cooldown
        if result['cooldown_2'] > 0:
            return await ctx.send(f"{result['username']}'s Frostbolt attack is on cooldown for {result['cooldown_2']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_2', 3)
        
        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Check to see if frostbolt froze the enemy
        freeze = False
        freeze_check = random.randint(1, 100)
        if freeze_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was frozen!")
            freeze = True

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, freeze)

    # Mage iceblock attack
    async def user_iceblock_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Iceblock attack!")
        if result['level'] < 3:
            return await ctx.send("You need to be at least level 3 to use the Iceblock attack!")
        
        # Check to see if iceblock is on cooldown
        if result['cooldown_3'] > 0:
            return await ctx.send(f"{result['username']}'s Iceblock attack is on cooldown for {result['cooldown_3']} more turns!")
        
        # Output message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} used Iceblock! They have regained 50 HP and reduced all other cooldowns by 3 turns!")

        # Heal user
        if result['current_hp'] + 50 > result['max_hp']:
            try:
                await ctx.send(f"{result['username']}'s HP: **{result['max_hp']}/{result['max_hp']}**")
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")
        else:
            try:
                await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] + 50}/{result['max_hp']}**")
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 50 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")

         # Update cooldowns
        if result['cooldown_1'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_1 = cooldown_1 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_2'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_2 = cooldown_2 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_3'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_3 = cooldown_3 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_4'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_4 = cooldown_4 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_5'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_5 = cooldown_5 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_6'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_6 = cooldown_6 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_7'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_7 = cooldown_7 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_8'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_8 = cooldown_8 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_9'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_9 = cooldown_9 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_10'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_10 = cooldown_10 - 2 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 3)

        await ctx.send("----------------------------------------------")

    # Mage lifesteal attack
    async def user_lifesteal_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Lifesteal attack!")
        if result['level'] < 4:
            return await ctx.send("You need to be at least level 4 to use the Lifesteal attack!")
        # Check to see if lifesteal is on cooldown
        if result['cooldown_4'] > 0:
            return await ctx.send(f"{result['username']}'s Lifesteal attack is on cooldown for {result['cooldown_4']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_4', 3)
        
        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 30 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']} and healed for **{damage}** HP!")

        # Heal user
        if result['current_hp'] + damage > result['max_hp']:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")
        else:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                result = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage wildfire attack
    async def user_wildfire_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Wildfire attack!")
        if result['level'] < 5:
            return await ctx.send("You need to be at least level 5 to use the Wildfire attack!")
        
        # Check to see if wildfire is on cooldown
        if result['cooldown_5'] > 0:
            return await ctx.send(f"{result['username']}'s Wildfire attack is on cooldown for {result['cooldown_5']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_5', 5)
        
        for _ in range(5):
            dodge = False
            block = False

            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Check to see if fireball burned
                burn_check = random.randint(1, 100)
                if burn_check <= 30:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was burned for 20 additional damage!")
                    damage += 20

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage blizzard attack
    async def user_blizzard_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Blizzard attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Blizzard attack!")
        
        # Check to see if blizzard is on cooldown
        if result['cooldown_6'] > 0:
            return await ctx.send(f"{result['username']}'s Blizzard attack is on cooldown for {result['cooldown_6']} more turns!")
        
        freeze = False
        
        for _ in range(5):
            dodge = False
            block = False

            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Check to see if frostbolt froze the enemy
                freeze_check = random.randint(1, 100)
                if freeze_check <= 30:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was frozen!")
                    freeze = True
                    
                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 5)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, freeze)

    # Mage evocation attack
    async def user_evocation_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Evocation attack!")
        if result['level'] < 7:
            return await ctx.send("You need to be at least level 7 to use the Evocation attack!")
        
        # Check to see if evocation is on cooldown
        if result['cooldown_7'] > 0:
            return await ctx.send(f"{result['username']}'s Evocation attack is on cooldown for {result['cooldown_7']} more turns!")
        
        # Output message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} used Evocation! All their cooldowns have been reset!")

        # Update cooldowns
        if result['cooldown_1'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_1 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_2'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_2 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_3'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_3 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_4'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_4 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_5'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_5 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_6'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_6 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_7'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_7 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_8'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_8 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_9'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_9 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_10'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_10 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"UPDATE Characters SET cooldown_7 = 100 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage lightning attack
    async def user_lightning_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Lightning attack!")
        if result['level'] < 8:
            return await ctx.send("You need to be at least level 8 to use the Lightning attack!")
        
        # Check to see if lightning attack is on cooldown
        if result['cooldown_8'] > 0:
            return await ctx.send(f"{result['username']}'s Lightning attack is on cooldown for {result['cooldown_8']} more turns!")

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        lightning = True

        while lightning:
            # Calculate damage
            damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} lightning strikes again!")
            else:
                lightning = False

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage pyroblast attack
    async def user_pyroblast_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Pyroblast attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Pyroblast attack!")
        
        # Check to see if pyroblast is on cooldown
        if result['cooldown_9'] > 0:
            return await ctx.send(f"{result['username']}'s Pyroblast attack is on cooldown for {result['cooldown_9']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_9', 10)
        
        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Calculate damage
        damage = 150 + result['main_hand_damage'] + result['off_hand_damage']

        # Check to see if mage missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s Pyroblast was interrupted!")
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")
        
        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Mage storm attack
    async def user_storm_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Storm attack!")
        if result['level'] < 10:
            return await ctx.send("You need to be at least level 10 to use the Storm attack!")
        
        # Check to see if storm is on cooldown
        if result['cooldown_10'] > 0:
            return await ctx.send(f"{result['username']}'s Storm attack is on cooldown for {result['cooldown_10']} more turns!")
        
        fireball_dodge = False
        fireball_block = False
        frostbolt_dodge = False
        frostbolt_block = False

        freeze = False
        lightning = True

        # ----------------- FIREBALL SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the fireball!")
            fireball_dodge = True

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the fireball!")
            fireball_block = True

        if not fireball_dodge and not fireball_block:
            # Calculate damage
            damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Check to see if fireball burned
            burn_check = random.randint(1, 100)
            if burn_check <= 30:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was burned for 20 additional damage!")
                damage += 20

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

        # ----------------- FROSTBOLT SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the frostbolt!")
            frostbolt_dodge = True

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the frostbolt!")
            frostbolt_block = True

        if not frostbolt_dodge and not frostbolt_block:
            # Calculate damage
            damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Check to see if frostbolt froze the enemy
            freeze_check = random.randint(1, 100)
            if freeze_check <= 30:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} was frozen!")
                freeze = True

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

        # ------------------ LIGHTNING SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the lightning!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the lightning!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)
            await ctx.send("----------------------------------------------")
            return await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

        while lightning:
            # Calculate damage
            damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance']:
                damage *= 2
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

            # Update enemy HP
            self.enemy[ctx.guild.id]['current_hp'] -= damage

            # Check to see if lightning retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} lightning strikes again!")
            else:
                lightning = False

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, freeze)

    # --------------------------- ROGUE ABILITIES --------------------------------------

    # Rogue gouge attack
    async def user_gouge_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Gouge attack!")

        # Check to see if gouge is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Gouge attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Output blind message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} has been blinded and has an additional 50% chance to miss their next attack!")
        cursor.execute(f"UPDATE Characters SET gouge_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_gouge_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue stab attack
    async def user_stab_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Stab attack!")
        if result['level'] < 2:
            return await ctx.send("You need to be at least level 2 to use the Stab attack!")

        # Check to see if stab is on cooldown
        if result['cooldown_2'] > 0:
            return await ctx.send(f"{result['username']}'s Stab attack is on cooldown for {result['cooldown_2']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_2', 3)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_stab_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue sap attack
    async def user_sap_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Sap attack!")
        if result['level'] < 3:
            return await ctx.send("You need to be at least level 3 to use the Sap attack!")

        # Check to see if sap is on cooldown
        if result['cooldown_3'] > 0:
            return await ctx.send(f"{result['username']}'s Sap attack is on cooldown for {result['cooldown_3']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 3)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Check to see if enemy stunned
        sap = False
        stun_check = random.randint(1, 100)
        if stun_check <= 50:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} has been sapped and will miss their next turn!")
            sap = True
            
        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_sap_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, sap)

    # Rogue bleed attack
    async def user_bleed_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Bleed attack!")
        if result['level'] < 4:
            return await ctx.send("You need to be at least level 4 to use the Bleed attack!") 

        # Check to see if bleed is on cooldown
        if result['cooldown_4'] > 0:
            return await ctx.send(f"{result['username']}'s Bleed attack is on cooldown for {result['cooldown_4']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_4', 5)

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage
                # Add to total damage
                total_damage += damage

        # Heal HP
        if result['current_hp'] + total_damage > result['max_hp']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s HP: {result['max_hp']}/{result['max_hp']}")
            cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s HP: {result['current_hp'] + total_damage}/{result['max_hp']}")
            cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {total_damage} WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_bleed_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue betrayal attack
    async def user_betrayal_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Betrayal attack!")
        if result['level'] < 5:
            return await ctx.send("You need to be at least level 5 to use the Betrayal attack!")

        # Check to see if betrayal is on cooldown
        if result['cooldown_5'] > 0:
            return await ctx.send(f"{result['username']}'s Betrayal attack is on cooldown for {result['cooldown_5']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_5', 5)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 30 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] + 30 > 0:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_betrayal_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue relentless attack
    async def user_relentless_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Relentless attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Relentless attack!")

        # Check to see if relentless is on cooldown
        if result['cooldown_6'] > 0:
            return await ctx.send(f"{result['username']}'s Relentless attack is on cooldown for {result['cooldown_6']} more turns!")

        # Activate relentless
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} is relentless and will preform the next attack twice!")
        cursor.execute(f"UPDATE Characters SET relentless_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 100)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue counter attack
    async def user_counter_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Counter attack!")
        if result['level'] < 7:
            return await ctx.send("You need to be at least level 7 to use the Counter attack!")

        # Check to see if counter is on cooldown
        if result['cooldown_7'] > 0:
            return await ctx.send(f"{result['username']}'s Counter attack is on cooldown for {result['cooldown_7']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_7', 100)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Ouput counter message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dodges will do 20 damage and interrupt the enemy's attack for the rest of the fight!")
        cursor.execute(f"UPDATE Characters SET counter_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        result = cursor.fetchone()

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_counter_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue assassinate attack
    async def user_assassinate_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        instakill = False
        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Assassinate attack!")
        if result['level'] < 8:
            return await ctx.send("You need to be at least level 8 to use the Assassinate attack!")

        # Check to see if assassinate is on cooldown
        if result['cooldown_8'] > 0:
            return await ctx.send(f"{result['username']}'s Assassinate attack is on cooldown for {result['cooldown_8']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 1)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Check for instant kill
                if self.enemy[ctx.guild.id]['current_hp'] / self.enemy[ctx.guild.id]['max_hp'] <= 0.3:
                    instakill_check = random.randint(1, 100)
                    if instakill_check >= 30:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{result['username']} has assassinated the {self.enemy[ctx.guild.id]['name']} for an instant kill!")
                        self.enemy[ctx.guild.id]['current_hp'] = 0
                        instakill = True
                
                    if not instakill:
                        # Calculate damage
                        damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                        # Check if user critical hit
                        crit_check = random.randint(1, 100)
                        if crit_check <= result['crit_chance']:
                            damage *= 2
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**Critical Hit!**")

                        # Output damage message
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                        # Update enemy HP
                        self.enemy[ctx.guild.id]['current_hp'] -= damage
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

                else:
                    # Calculate damage
                    damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                    # Check if user critical hit
                    crit_check = random.randint(1, 100)
                    if crit_check <= result['crit_chance']:
                        damage *= 2
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"**Critical Hit!**")

                    # Output damage message
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                    # Update enemy HP
                    self.enemy[ctx.guild.id]['current_hp'] -= damage
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_assassinate_attack(ctx, result, cursor, battle_cog)

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue bladestorm attack
    async def user_bladestorm_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Bladestorm attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Bladestorm attack!")

        # Check to see if bladestorm is on cooldown
        if result['cooldown_9'] > 0:
            return await ctx.send(f"{result['username']}'s Bladestorm attack is on cooldown for {result['cooldown_9']} more turns!")

        bladestorm = True

        while bladestorm:

            for _ in range(2):
                dodge = False
                block = False
                # Check to see if enemy dodged
                dodge_check = random.randint(1, 100)
                if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                    dodge = True
                    
                # Check to see if enemy blocked
                block_check = random.randint(1, 100)
                if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                    block = True

                if not dodge and not block:
                    # Calculate damage
                    damage = 25 + result['main_hand_damage'] + result['off_hand_damage']

                    # Check if user critical hit
                    crit_check = random.randint(1, 100)
                    if crit_check <= result['crit_chance']:
                        damage *= 2
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"**Critical Hit!**")

                    # Output damage message
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                    # Update enemy HP
                    self.enemy[ctx.guild.id]['current_hp'] -= damage

                    # Check to see if bladestorm retriggers
                    retrigger_check = random.randint(1, 100)
                    if retrigger_check <= 50:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{result['username']}'s bladestorm strikes again!")
                    else:
                        bladestorm = False

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_9', 10)

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_bladestorm_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # Rogue backstab attack
    async def user_backstab_attack(self, ctx, result, cursor, battle_cog):
        # Add user to particpants list
        if result['username'] not in self.participant_names:
            self.participant_names.append(result['username'])
            self.participants.append(result)

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Backstab attack!")
        if result['level'] < 10:
            return await ctx.send("You need to be at least level 10 to use the Backstab attack!")

        # Check to see if backstab is on cooldown
        if result['cooldown_10'] > 0:
            return await ctx.send(f"{result['username']}'s Backstab attack is on cooldown for {result['cooldown_10']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dodged the attack!")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] + 50:
                    damage *= 2
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")

                # Update enemy HP
                self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Relentless
        if result['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            result = cursor.fetchone()
            await self.user_backstab_attack(ctx, result, cursor, battle_cog)

        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.enemy[ctx.guild.id]['name']}'s HP: **{self.enemy[ctx.guild.id]['current_hp']}/{self.enemy[ctx.guild.id]['max_hp']}**")

        await ctx.send("----------------------------------------------")

       # Check to see if enemy died
        await self.enemy_health_check(ctx, result, battle_cog, cursor, False)

    # User run command
    async def user_run(self, ctx, result, cursor, battle_cog):
        # Check to see if user is in participants list, if not add them
        if result['username'] not in self.participant_names:
            return await ctx.send("You are not in the battle.")
        
        else:
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"UPDATE Characters SET cooldown_1 = 0, cooldown_2 = 0, cooldown_3 = 0, cooldown_4 = 0, cooldown_5 = 0, cooldown_6 = 0, cooldown_7 = 0, cooldown_8 = 0, cooldown_9 = 0, cooldown_10 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"UPDATE Characters SET precision_active = 0, relentless_active = 0, gouge_active = 0, counter_active = 0, shieldbash_active = 0  WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                await ctx.send(f"**{result['username']} has fled from the battle!**")
            except Exception as e:
                print(e)

            # If no participants left, end battle
            if len(self.participants) == 0:
                battle_cog.encounter[ctx.guild.id]['active_battle'] = False
                battle_cog.enemy[ctx.guild.id] = {}
                battle_cog.enemy[ctx.guild.id]['name'] = None
                battle_cog.enemy[ctx.guild.id]['max_hp'] = None
                battle_cog.enemy[ctx.guild.id]['current_hp'] = None
                battle_cog.enemy[ctx.guild.id]['dodge_chance'] = None
                battle_cog.enemy[ctx.guild.id]['block_chance'] = None
                battle_cog.enemy[ctx.guild.id]['crit_chance'] = None
                battle_cog.enemy[ctx.guild.id]['damage'] = None
                battle_cog.enemy[ctx.guild.id]['attacks'] = []
                battle_cog.enemy[ctx.guild.id]['gold'] = None
                battle_cog.enemy[ctx.guild.id]['exp'] = None
                battle_cog.enemy[ctx.guild.id]['good_drop_chance'] = None
                battle_cog.enemy[ctx.guild.id]['rare_drop_chance'] = None
                battle_cog.enemy[ctx.guild.id]['epic_drop_chance'] = None
                battle_cog.enemy[ctx.guild.id]['legendary_drop_chance'] = None

                # Clear participants list and enemy details
                self.participants = []
                self.participant_names = []
                self.enemy = {}
                self.active_battle = False
                self.beserk_damage = 10
                return await ctx.send("**All participants have fled. The battle has ended.**")
            return

    # --------------------------- UPDATE COOLDOWNS --------------------------------------

    async def update_cooldowns(self, ctx, result, cursor, cooldown, cooldown_duration):
        # Update cooldowns
        if result['cooldown_1'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_1 = cooldown_1 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_2'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_2 = cooldown_2 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_3'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_3 = cooldown_3 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_4'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_4 = cooldown_4 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_5'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_5 = cooldown_5 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_6'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_6 = cooldown_6 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_7'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_7 = cooldown_7 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_8'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_8 = cooldown_8 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_9'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_9 = cooldown_9 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if result['cooldown_10'] > 0:
            cursor.execute(f"UPDATE Characters SET cooldown_10 = cooldown_10 - 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")

        if cooldown != 'basic':
            cursor.execute(f"UPDATE Characters SET {cooldown} = {cooldown_duration} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")

    # --------------------------- ENEMY HEALTH CHECK --------------------------------------

    async def enemy_health_check(self, ctx, result, battle_cog, cursor, stun):
    # Check if enemy died
        if self.enemy[ctx.guild.id]['current_hp'] <= 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**The {self.enemy[ctx.guild.id]['name']} has been defeated!**")

            # Distribute EXP, gold and loot to participants
            for participant in self.participants:
                # Update EXP
                try:
                    if participant['level'] < 10:
                        # Level up check
                        if participant['exp'] + self.enemy[ctx.guild.id]['exp'] >= participant['next_level_exp']:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("**DING!**")
                            await ctx.send(f"**{participant['username']}** has leveled up to {participant['level'] + 1}!")

                            # Update level and next level EXP
                            if participant['level'] == 1:
                                cursor.execute(f"UPDATE Characters SET level = 2, next_level_exp = 150 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 2:
                                cursor.execute(f"UPDATE Characters SET level = 3, next_level_exp = 300 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 3:
                                cursor.execute(f"UPDATE Characters SET level = 4, next_level_exp = 500 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 4:
                                cursor.execute(f"UPDATE Characters SET level = 5, next_level_exp = 750 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 5:
                                cursor.execute(f"UPDATE Characters SET level = 6, next_level_exp = 1050 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 6:
                                cursor.execute(f"UPDATE Characters SET level = 7, next_level_exp = 1400 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 7:
                                cursor.execute(f"UPDATE Characters SET level = 8, next_level_exp = 1800 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 8:
                                cursor.execute(f"UPDATE Characters SET level = 9, next_level_exp = 2250 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                            elif participant['level'] == 9:
                                cursor.execute(f"UPDATE Characters SET level = 10 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")

                        cursor.execute(f"UPDATE Characters SET exp = exp + {self.enemy[ctx.guild.id]['exp']} WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character EXP.")
                
                # Update Gold
                try:
                    cursor.execute(f"UPDATE Characters SET gold = gold + {self.enemy[ctx.guild.id]['gold']} WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character Gold.")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**{participant['username']}** received {self.enemy[ctx.guild.id]['exp']} EXP and {self.enemy[ctx.guild.id]['gold']} Gold!")
            
            # Loot
            good_loot_check = random.randint(1, 100)
            rare_loot_check = random.randint(1, 100)
            epic_loot_check = random.randint(1, 100)
            legendary_loot_check = random.randint(1, 100)

            # Good loot dropped
            if good_loot_check <= self.enemy[ctx.guild.id]['good_drop_chance']:
                # Determine what piece of loot dropped
                loot_class = random.choice(self.classes)
                loot_slot = random.choice(self.slots)

                # Distribute loot
                async with ctx.typing():
                    await asyncio.sleep(2)
                await self.distribute_loot(ctx, loot_class, loot_slot, "good", cursor)

            # Rare loot dropped
            if rare_loot_check <= self.enemy[ctx.guild.id]['rare_drop_chance']:
                # Determine what piece of loot dropped
                loot_class = random.choice(self.classes)
                loot_slot = random.choice(self.slots)

                # Distribute loot
                async with ctx.typing():
                    await asyncio.sleep(2)
                await self.distribute_loot(ctx, loot_class, loot_slot, "rare", cursor)

            # Epic loot dropped
            if epic_loot_check <= self.enemy[ctx.guild.id]['epic_drop_chance']:
                # Determine what piece of loot dropped
                loot_class = random.choice(self.classes)
                loot_slot = random.choice(self.slots)

                # Distribute loot
                async with ctx.typing():
                    await asyncio.sleep(2)
                await self.distribute_loot(ctx, loot_class, loot_slot, "epic", cursor)

            # Legendary loot dropped
            if legendary_loot_check <= self.enemy[ctx.guild.id]['legendary_drop_chance']:
                # Determine what piece of loot dropped
                loot_class = random.choice(self.classes)
                loot_slot = random.choice(self.slots)

                # Distribute loot
                async with ctx.typing():
                    await asyncio.sleep(2)
                await self.distribute_loot(ctx, loot_class, loot_slot, "legendary", cursor)

            # Set particpants health back to max and set their cooldowns to 0
            for participant in self.participants:
                try:
                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"UPDATE Characters SET cooldown_1 = 0, cooldown_2 = 0, cooldown_3 = 0, cooldown_4 = 0, cooldown_5 = 0, cooldown_6 = 0, cooldown_7 = 0, cooldown_8 = 0, cooldown_9 = 0, cooldown_10 = 0 WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"UPDATE Characters SET precision_active = 0, relentless_active = 0, gouge_active = 0, counter_active = 0, shieldbash_active = 0  WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                
            # Reset battle details
            battle_cog.encounter[ctx.guild.id]['active_battle'] = False
            battle_cog.enemy[ctx.guild.id] = {}
            battle_cog.enemy[ctx.guild.id]['name'] = None
            battle_cog.enemy[ctx.guild.id]['max_hp'] = None
            battle_cog.enemy[ctx.guild.id]['current_hp'] = None
            battle_cog.enemy[ctx.guild.id]['dodge_chance'] = None
            battle_cog.enemy[ctx.guild.id]['block_chance'] = None
            battle_cog.enemy[ctx.guild.id]['crit_chance'] = None
            battle_cog.enemy[ctx.guild.id]['damage'] = None
            battle_cog.enemy[ctx.guild.id]['attacks'] = []
            battle_cog.enemy[ctx.guild.id]['gold'] = None
            battle_cog.enemy[ctx.guild.id]['exp'] = None
            battle_cog.enemy[ctx.guild.id]['good_drop_chance'] = None
            battle_cog.enemy[ctx.guild.id]['rare_drop_chance'] = None
            battle_cog.enemy[ctx.guild.id]['epic_drop_chance'] = None
            battle_cog.enemy[ctx.guild.id]['legendary_drop_chance'] = None

            # Clear participants list and enemy details
            self.participants = []
            self.participant_names = []
            self.enemy = {}
            self.active_battle = False
            self.beserk_damage = 10    

        else:
            if not stun:
                await self.choose_enemy_attack(ctx, battle_cog, result, cursor)

    # --------------------------- ENEMY ABILITIES --------------------------------------  

    async def enemy_basic_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses basic attack!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                await ctx.send("----------------------------------------------")
                # Check to see if enemy died
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = self.enemy[ctx.guild.id]['damage']

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
    
    async def enemy_fireball_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Fireball!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 20

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # Check to see if user suffered burn damage
        burn_check = random.randint(1, 100)
        if burn_check <= 20:
            async with ctx.typing():
                    await asyncio.sleep(2)
            await ctx.send(f"{result['username']} was burned! {result['username']} takes an additional 20 damage!")
            damage += 20

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
        await ctx.send("----------------------------------------------")
            
    async def enemy_frostbolt_attack(self, ctx, battle_cog, result, cursor):
        frozen = False

        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Frostbolt!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 20

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            await ctx.send("----------------------------------------------")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Check to see if user suffered freeze
            freeze_check = random.randint(1, 100)
            if freeze_check <= 20:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} was frozen!")
                frozen = True

            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
            # If user is frozen, skip their next turn
            await ctx.send("----------------------------------------------")
            if frozen:
                await self.choose_enemy_attack(ctx, battle_cog, result, cursor)
        
    async def enemy_trishot_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Trishot!")

        # Total damage
        total_damage = 0

        for _ in range(3):
            dodge = False
            block = False

            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = self.enemy[ctx.guild.id]['damage']

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Add damage to total damage
                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - total_damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
                    
    async def enemy_snipe_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Snipe!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 40

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
            
    async def enemy_sap_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Sap!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 10

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            await ctx.send("----------------------------------------------")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Check to see if user was stunned
            stun = False
            stun_check = random.randint(1, 100)
            if stun_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} was stunned!")
                stun = True

            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")

            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
            await ctx.send("----------------------------------------------")
            
            # If user is stunned, skip their next turn
            if stun:
                await self.choose_enemy_attack(ctx, battle_cog, result, cursor)

    async def enemy_stab_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Stab!")

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                if self.enemy[ctx.guild.id]['name'] == "cutthroat":
                    damage = 20
                else:
                    damage = 40

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Add damage to total damage
                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - total_damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
                    
    async def enemy_crush_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Crush!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 20

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            await ctx.send("----------------------------------------------")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Check to see if user was stunned
            stun = False
            stun_check = random.randint(1, 100)
            if stun_check <= 20:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} was stunned!")
                stun = True

            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            await ctx.send("----------------------------------------------")

            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
            # If user is stunned, skip their next turn
            if stun:
                await self.choose_enemy_attack(ctx, battle_cog, result, cursor)

    async def enemy_flurry_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Flurry!")

        # Total damage
        total_damage = 0

        # Set flurry attacks
        if self.enemy[ctx.guild.id]['name'] == "gladiator":
            flurry_attacks = 5
        else:
            flurry_attacks = 3

        for _ in range(flurry_attacks):
            dodge = False
            block = False

            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = self.enemy[ctx.guild.id]['damage']

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Add damage to total damage
                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - total_damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
        
        await ctx.send("----------------------------------------------")
            
    async def enemy_haymaker_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Haymaker!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")
        
        # Check to see if enemy missed
        miss_check = random.randint(1, 100)
        if miss_check <= 50:
            async with ctx.typing():
                await asyncio.sleep(2)
            return await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} missed the attack!")

        # Calculate damage
        damage = 50

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
            
    async def enemy_lifesteal_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Lifesteal!")

        # Damage list
        damage_list = [10, 20, 30, 40, 50]

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = random.choice(damage_list)

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # Heal enemy for damage deal
        self.enemy[ctx.guild.id]['current_hp'] += damage
        if self.enemy[ctx.guild.id]['current_hp'] > self.enemy[ctx.guild.id]['max_hp']:
            self.enemy[ctx.guild.id]['current_hp'] = self.enemy[ctx.guild.id]['max_hp']

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
            
    async def enemy_wildfire_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Wildfire!")

        # Total damage
        total_damage = 0

        for _ in range(5):
            dodge = False
            block = False
            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 20

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

                # Check to see if user suffered burn damage
                burn_check = random.randint(1, 100)
                if burn_check <= 20:
                    async with ctx.typing():
                            await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} was burned! {result['username']} takes an additional 20 damage!")
                    damage += 20

                # Add damage to total damage
                total_damage += damage

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - total_damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
                    
    async def enemy_lightning_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Lightning!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 50

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
                return await ctx.send(f"**{result['username']}** has died!")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            # Check to see if lightning should retrigger
            lightning_check = random.randint(1, 100)
            if lightning_check <= 30:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The lightning strikes again!")
                await self.enemy_lightning_attack(ctx, battle_cog, result, cursor)

            else:
                await ctx.send("----------------------------------------------")

    async def enemy_rapidfire_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Rapidfire!")

        # Total damage
        total_damage = 0

        for _ in range(5):
            dodge = False
            block = False

            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = self.enemy[ctx.guild.id]['damage']

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Add damage to total damage
                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - total_damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
                    
    async def enemy_volley_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Volley!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = 50

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            # Check to see if volley should retrigger
            volley_check = random.randint(1, 100)
            if volley_check <= 30:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The volley strikes again!")
                await self.enemy_volley_attack(ctx, battle_cog, result, cursor)
            else:
                await ctx.send("----------------------------------------------")

    async def enemy_bladestorm_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses Bladestorm!")

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False

            # Check to see if user dodged
            dodge_check = random.randint(1, 100)
            if result['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if dodge_check <= result['dodge_chance']:
                if result['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged and countered the attack!")
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                    self.enemy[ctx.guild.id]['current_hp'] -= 20
                    # Check to see if enemy died
                    await ctx.send("----------------------------------------------")
                    return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
                else:                     
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dodged the attack!")
                    dodge = True

            # Check to see if user blocked
            block_check = random.randint(1, 100)
            if result['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            if block_check <= result['block_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 25

                # Check if enemy critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                # Add damage to total damage
                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - total_damage <= 0:
            self.user_died = True
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
            
            # User didn't die, update their current HP
            else:
                # Display current HP
                await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE Characters SET current_hp = current_hp - {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")
                # Check to see if bladestorm should retrigger
                bladestorm_check = random.randint(1, 100)
                if bladestorm_check <= 30:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"The bladestorm strikes again!")
                    await self.enemy_bladestorm_attack(ctx, battle_cog, result, cursor)
                else:
                    await ctx.send("----------------------------------------------")

    async def enemy_beserk_attack(self, ctx, battle_cog, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses basic attack!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if result['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if dodge_check <= result['dodge_chance']:
            if result['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged and countered the attack!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt 20 damage to the {self.enemy[ctx.guild.id]['name']}!")
                self.enemy[ctx.guild.id]['current_hp'] -= 20
                # Check to see if enemy died
                await ctx.send("----------------------------------------------")
                return await self.enemy_health_check(ctx, result, battle_cog, cursor, True)
            else:                     
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dodged the attack!")
                return await ctx.send("----------------------------------------------")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if result['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        if block_check <= result['block_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} blocked the attack!")
            return await ctx.send("----------------------------------------------")

        # Calculate damage
        damage = self.beserk_damage

        # Check if enemy critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= self.enemy[ctx.guild.id]['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt **{damage}** damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            self.user_died
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            for participant in self.participants:
                if participant['username'] == ctx.author.name:
                    result = participant
                    break
            self.participants.remove(result)
            self.participant_names.remove(result['username'])
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] - damage}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp - {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        await ctx.send("----------------------------------------------")
            
        # Update beskerk damage for next attack
        self.beserk_damage *= 2

    # --------------------------- CHOOSE ENEMY ATTACK --------------------------------------

    async def choose_enemy_attack(self, ctx, battle_cog, result, cursor):
        enemy_attack = random.choice(self.enemy[ctx.guild.id]['attacks'])
        if enemy_attack == "basic":
            await self.enemy_basic_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "fireball":
            await self.enemy_fireball_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "frostbolt":
            await self.enemy_frostbolt_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "trishot":
            await self.enemy_trishot_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "snipe":
            await self.enemy_snipe_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "sap":
            await self.enemy_sap_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "stab":
            await self.enemy_stab_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "crush":
            await self.enemy_crush_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "flurry":
            await self.enemy_flurry_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "haymaker":
            await self.enemy_haymaker_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "lifesteal":
            await self.enemy_lifesteal_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "wildfire":
            await self.enemy_wildfire_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "lightning":
            await self.enemy_lightning_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "rapidfire":
            await self.enemy_rapidfire_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "volley":
            await self.enemy_volley_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "bladestorm":
            await self.enemy_bladestorm_attack(ctx, battle_cog, result, cursor)
        elif enemy_attack == "beserk":
            await self.enemy_beserk_attack(ctx, battle_cog, result, cursor)

    # --------------------------- DISTRIBUTE LOOT --------------------------------------

    async def distribute_loot(self, ctx, loot_class, loot_slot, rarity, cursor):
        # Set roll for loot boolean
        roll_for_loot = False

        # Set numerical values for loot rarity
        if rarity == "good":
            rarity_num = 0
        elif rarity == "rare":
            rarity_num = 1
        elif rarity == "epic":
            rarity_num = 2
        elif rarity == "legendary":
            rarity_num = 3

        # Set slot rarity values
        if rarity == "good":
            slot_rarity = 2
        elif rarity == "rare":
            slot_rarity = 3
        elif rarity == "epic":
            slot_rarity = 4
        elif rarity == "legendary":
            slot_rarity = 5

        # Set numerical values for loot class
        if loot_class == "warrior":
            loot_class_num = 0
        elif loot_class == "mage":
            loot_class_num = 1
        elif loot_class == "hunter":
            loot_class_num = 2
        elif loot_class == "rogue":
            loot_class_num = 3
        elif loot_class == "gambler":
            loot_class_num = 4

        # Set numerical values for loot slot
        if loot_slot == "boots":
            loot_slot_num = 0
        elif loot_slot == "legs":
            loot_slot_num = 1
        elif loot_slot == "chest":
            loot_slot_num = 2
        elif loot_slot == "gloves":
            loot_slot_num = 3
        elif loot_slot == "helmet":
            loot_slot_num = 4
        elif loot_slot == "main_hand":
            loot_slot_num = 5
        elif loot_slot == "off_hand":
            loot_slot_num = 6

        # See what particpants match the loot class
        matching_participants = []
        for participant in self.participants:
            if participant['class'] == loot_class:
                matching_participants.append(participant)

        # Output what piece of loot dropped
        async with ctx.typing():
            await asyncio.sleep(2)
        loot_drop = self.loot[rarity_num][loot_class_num][loot_slot_num]
        await ctx.send(f"**{loot_drop}** dropped!")

        # If there are any participants that match the loot class
        if len(matching_participants) > 0:
            # See which participant(s) need the loot
            needers = []
            for participant in matching_participants:
                if loot_slot == "boots":
                    if participant['boots'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "legs":
                    if participant['legs'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "chest":
                    if participant['chest'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "gloves":
                    if participant['gloves'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "helmet":
                    if participant['helmet'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "main_hand":
                    if participant['main_hand'] < slot_rarity:
                        needers.append(participant)
                elif loot_slot == "off_hand":
                    if participant['off_hand'] < slot_rarity:
                        needers.append(participant)

            # If multiple needers, roll for need
            if len(needers) > 1:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send("Multiple participants need this item, rolling for need...")
                for needer in needers:
                    roll = random.randint(1, 100)
                    await ctx.send(f"{needer['username']} rolled a {roll}!")
                    if not self.highest_loot_roll or roll > self.highest_loot_roll:
                        self.highest_loot_roll = roll
                        self.loot_winner = needer
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**{self.loot_winner['username']}** has won the **{loot_drop}**!")

            # Only one particpant needs the loot, they win by default
            elif len(needers) == 1:
                self.loot_winner = needers[0]
                await ctx.send(f"**{self.loot_winner['username']}** has won the **{loot_drop}**!")

            else:
                roll_for_loot = True
        
        # No matching participants for the loot
        else:
            roll_for_loot = True

        # Update loot winner's equipment in DB
        if not roll_for_loot:
            # Update loot winner's boots
            if loot_slot == "boots":
                cursor.execute(f"UPDATE Characters SET boots = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                if slot_rarity == 5:
                    if self.loot_winner['boots'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 4:
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 4:
                    if self.loot_winner['boots'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 3:
                    if self.loot_winner['boots'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['boots'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                elif slot_rarity == 2:
                    if self.loot_winner['boots'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
            
            # Update loot winner's legs
            elif loot_slot == "legs":
                cursor.execute(f"UPDATE Characters SET legs = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                if slot_rarity == 5:
                    if self.loot_winner['legs'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 4:
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 4:
                    if self.loot_winner['legs'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 3:
                    if self.loot_winner['legs'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['legs'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                elif slot_rarity == 2:
                    if self.loot_winner['legs'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Update loot winner's chest
            elif loot_slot == "chest":
                cursor.execute(f"UPDATE Characters SET chest = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                if slot_rarity == 5:
                    if self.loot_winner['chest'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 4:
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 4:
                    if self.loot_winner['chest'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 3:
                    if self.loot_winner['chest'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['chest'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                elif slot_rarity == 2:
                    if self.loot_winner['chest'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Update loot winner's gloves
            elif loot_slot == "gloves":
                cursor.execute(f"UPDATE Characters SET gloves = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                if slot_rarity == 5:
                    if self.loot_winner['gloves'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 4:
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 4:
                    if self.loot_winner['gloves'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 3:
                    if self.loot_winner['gloves'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['gloves'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                elif slot_rarity == 2:
                    if self.loot_winner['gloves'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Update loot winner's helmet
            elif loot_slot == "helmet":
                cursor.execute(f"UPDATE Characters SET helmet = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                if slot_rarity == 5:
                    if self.loot_winner['helmet'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 4:
                        cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 4:
                    if self.loot_winner['helmet'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 3:
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif slot_rarity == 3:
                    if self.loot_winner['helmet'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif self.loot_winner['helmet'] == 2:
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                elif slot_rarity == 2:
                    if self.loot_winner['helmet'] == 1:
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Update loot winner's main hand
            elif loot_slot == "main_hand":

                # Update Rogue main hand or off hand whichever is lower
                if self.loot_winner['class'] == 'rogue':
                    if self.loot_winner['off_hand'] < self.loot_winner['main_hand']:
                        if slot_rarity == 5:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 4:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 3:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 2:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    else:
                        if slot_rarity == 5:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 4:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 3:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 2:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                
                # Update Gambler main hand
                elif self.loot_winner['class'] == 'gambler':
                    cursor.execute(f"UPDATE Characters SET main_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    if slot_rarity == 5:
                        if self.loot_winner['main_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 15 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 4:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 4:
                        if self.loot_winner['main_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 15 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 3:
                        if self.loot_winner['main_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['main_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 2:
                        if self.loot_winner['main_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                # Update all other classes main hand
                else:
                    cursor.execute(f"UPDATE Characters SET main_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    if slot_rarity == 5:
                        cursor.execute(f"UPDATE Characters SET main_hand_damage = 20 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif slot_rarity == 4:
                        cursor.execute(f"UPDATE Characters SET main_hand_damage = 15 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif slot_rarity == 3:
                        cursor.execute(f"UPDATE Characters SET main_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    elif slot_rarity == 2:
                        cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Update loot winner's off hand
            elif loot_slot == "off_hand":

                # Update Rogue off hand or main hand whichever is lower
                if self.loot_winner['class'] == 'rogue':
                    if self.loot_winner['main_hand'] < self.loot_winner['off_hand']:
                            if slot_rarity == 5:
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                            elif slot_rarity == 4:
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                            elif slot_rarity == 3:
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                            elif slot_rarity == 2:
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                            cursor.execute(f"UPDATE Characters SET main_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                            
                    else:
                        if slot_rarity == 5:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 4:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 3:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif slot_rarity == 2:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                # Update Gambler off hand
                elif self.loot_winner['class'] == 'gambler':
                    cursor.execute(f"UPDATE Characters SET off_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    if slot_rarity == 5:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 4:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 4:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 3:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 2:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                # Update Warrior off hand
                elif self.loot_winner['class'] == 'warrior':
                    cursor.execute(f"UPDATE Characters SET off_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    if slot_rarity == 5:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 10 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 4:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 4:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 3:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 2:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                # Update Hunter and Mage off hands
                else:
                    cursor.execute(f"UPDATE Characters SET off_hand = {slot_rarity} WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                    if slot_rarity == 5:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 4:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 4:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 3 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 3:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 3:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 2 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
                        elif self.loot_winner['off_hand'] == 2:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                    elif slot_rarity == 2:
                        if self.loot_winner['off_hand'] == 1:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

        # Roll for loot
        else:

            # Only one participant and they don't need the loot
            if len(self.participants) == 1:
                self.loot_winner = self.participants[0]
                if rarity == 'good':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 50 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'rare':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 100 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'epic':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 200 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 200 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'legendary':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 500 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 500 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

            # Multiple participants but no one needs the loot, roll for greed
            else:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send("No particpants need the loot. Rolling for greed...")

                for participant in self.participants:
                    loot_roll = random.randint(1, 100)
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                    if self.highest_loot_roll is None or loot_roll > self.highest_loot_roll:
                        self.highest_loot_roll = loot_roll
                        self.loot_winner = participant

                # Announce loot winner and update their gold
                if rarity == 'good':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 50 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'rare':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 100 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'epic':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 200 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 200 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")

                elif rarity == 'legendary':
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.loot_winner['username']} has won 500 gold in exchange for {loot_drop}!")
                    cursor.execute(f"UPDATE Characters SET gold = gold + 500 WHERE username = '{self.loot_winner['username']}' and guild_id = '{ctx.guild.id}'")
            

        # Reset loot winner and highest loot roll
        self.loot_winner = None
        self.highest_loot_roll = None

async def setup(bot):
    await bot.add_cog(Cast(bot))
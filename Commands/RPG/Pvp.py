import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random
import asyncio


class Pvp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.turn_player = None
        self.turn_player_num = None
        self.other_player = None
        self.active_duel = False
        self.duelists = []

    # Mage function
    @commands.command()
    async def pvp(self, ctx, *args):
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
        
        if len(args) == 0:
            # The first duelist enters the arena
            if len(self.duelists) == 0:
                self.duelists.append(result)
                await ctx.send(f"{result['username']} has entered the arena!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                return await ctx.send("You need one more duelist to enter the arena to begin the duel.")
        
            # The second duelist enters the arena
            elif len(self.duelists) == 1:
                self.duelists.append(result)
                await ctx.send(f"{result['username']} has entered the arena!")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send("The duel has begun!")
                self.active_duel = True
                turn_choice = random.randint(0, 1)
                self.turn_player = self.duelists[turn_choice]
                self.turn_player_num = turn_choice
                if turn_choice == 0:
                    self.other_player = self.duelists[1]
                else:
                    self.other_player = self.duelists[0]
                await ctx.send(f"Your move {self.turn_player['username']}!")

            # There are already 2 duelists in the arena
            else:
                return await ctx.send("There are already 2 duelists in the arena. Please wait for the current duel to finish.")
            
        elif len(args) == 1:
            if 'cast' in args[0].lower() or 'attack' in args[0].lower() or 'spell' in args[0].lower():
                if not self.active_duel:
                    return await ctx.send("There is no active duel.")
                else:
                    cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                    return await self.user_basic_attack(ctx, result, cursor)
            else:
                return await ctx.send("Invalid command. To cast a spell/ability in pvp, use the command `!pvp cast [spell name]`")
            
        else:
            if not self.active_duel:
                return await ctx.send("There is no active duel.")
            
            else:
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()

            for arg in args:
                # User wants to basic attack
                if 'basic' in arg.lower():
                    return await self.user_basic_attack(ctx, result, cursor)

                # User wants to use crush
                elif 'crush' in arg.lower():
                    return await self.user_crush_attack(ctx, result, cursor)

                # User wants to use flurry
                elif 'flurry' in arg.lower():
                    return await self.user_flurry_attack(ctx, result, cursor)

                # User wants to use shieldbash
                elif 'shieldbash' in arg.lower():
                    return await self.user_shieldbash_attack(ctx, result, cursor)

                # User wants to use bloodthirst
                elif 'bloodthirst' in arg.lower():
                    return await self.user_bloodthirst_attack(ctx, result, cursor)

                # User wants to use execute
                elif 'execute' in arg.lower():
                    return await self.user_execute_attack(ctx, result, cursor)
                
                # User wants to use headbutt
                elif 'headbutt' in arg.lower():
                    return await self.user_headbutt_attack(ctx, result, cursor)

                # User wants to use haymaker
                elif 'haymaker' in arg.lower():
                    return await self.user_haymaker_attack(ctx, result, cursor)

                # User wants to use whirlwind
                elif 'whirlwind' in arg.lower():
                    return await self.user_whirlwind_attack(ctx, result, cursor)

                # User wants to use retaliate
                elif 'retaliate' in arg.lower():
                    return await self.user_retaliate_attack(ctx, result, cursor)

                # User wants to use takedown
                elif 'takedown' in arg.lower():
                    return await self.user_takedown_attack(ctx, result, cursor)

                # User wants to use trishot
                elif 'trishot' in arg.lower():
                    return await self.user_trishot_attack(ctx, result, cursor)
                
                # User wants to use precision
                elif 'precision' in arg.lower():
                    return await self.user_precision_attack(ctx, result, cursor)

                # User wants to use blind
                elif 'blind' in arg.lower():
                    return await self.user_blind_attack(ctx, result, cursor)

                # User wants to use snipe
                elif 'snipe' in arg.lower():
                    return await self.user_snipe_attack(ctx, result, cursor)

                # User wants to use rapidfire
                elif 'rapidfire' in arg.lower():
                    return await self.user_rapidfire_attack(ctx, result, cursor)

                # User wants to use bear
                elif 'bear' in arg.lower():
                    return await self.user_bear_attack(ctx, result, cursor)

                # User wants to use headshot
                elif 'headshot' in arg.lower():
                    return await self.user_headshot_attack(ctx, result, cursor)

                # User wants to use volley
                elif 'volley' in arg.lower():
                    return await self.user_volley_attack(ctx, result, cursor)

                # User wants to use powershot
                elif 'powershot' in arg.lower():
                    return await self.user_powershot_attack(ctx, result, cursor)

                # User wants to use unload
                elif 'unload' in arg.lower():
                    return await self.user_unload_attack(ctx, result, cursor)

                # User wants to use deal
                elif 'deal' in arg.lower():
                    return await self.user_deal_attack(ctx, result, cursor)

                # User wants to use jack
                elif 'jack' in arg.lower():
                    return await self.user_jack_attack(ctx, result, cursor)

                # User wants to use queen
                elif 'queen' in arg.lower():
                    return await self.user_queen_attack(ctx, result, cursor)

                # User wants to use king
                elif 'king' in arg.lower():
                    return await self.user_king_attack(ctx, result, cursor)

                # User wants to use ace
                elif 'ace' in arg.lower():
                    return await self.user_ace_attack(ctx, result, cursor)

                # User wants to use straight
                elif 'straight' in arg.lower():
                    return await self.user_straight_attack(ctx, result, cursor)

                # User wants to use flush
                elif 'flush' in arg.lower():
                    return await self.user_flush_attack(ctx, result, cursor)

                # User wants to use blackjack
                elif 'blackjack' in arg.lower():
                    return await self.user_blackjack_attack(ctx, result, cursor)

                # User wants to use roulette
                elif 'roulette' in arg.lower():
                    return await self.user_roulette_attack(ctx, result, cursor)

                # User wants to use fireball
                elif 'fireball' in arg.lower():
                    return await self.user_fireball_attack(ctx, result, cursor)

                # User wants to use frostbolt
                elif 'frostbolt' in arg.lower():
                    return await self.user_frostbolt_attack(ctx, result, cursor)

                # User wants to use iceblock
                elif 'iceblock' in arg.lower():
                    return await self.user_iceblock_attack(ctx, result, cursor)

                # User wants to use lifesteal
                elif 'lifesteal' in arg.lower():
                    return await self.user_lifesteal_attack(ctx, result, cursor)

                # User wants to use wildfire
                elif 'wildfire' in arg.lower():
                    return await self.user_wildfire_attack(ctx, result, cursor)

                # User wants to use blizzard
                elif 'blizzard' in arg.lower():
                    return await self.user_blizzard_attack(ctx, result, cursor)

                # User wants to use evocation
                elif 'evocation' in arg.lower():
                    return await self.user_evocation_attack(ctx, result, cursor)

                # User wants to use lightning
                elif 'lightning' in arg.lower():
                    return await self.user_lightning_attack(ctx, result, cursor)

                # User wants to use pyroblast
                elif 'pyroblast' in arg.lower():
                    return await self.user_pyroblast_attack(ctx, result, cursor)

                # User wants to use gouge
                elif 'gouge' in arg.lower():
                    return await self.user_gouge_attack(ctx, result, cursor)

                # User wants to use stab
                elif 'stab' in arg.lower():
                    return await self.user_stab_attack(ctx, result, cursor)

                # User wants to use sap
                elif 'sap' in arg.lower():
                    return await self.user_sap_attack(ctx, result, cursor)

                # User wants to use bleed
                elif 'bleed' in arg.lower():
                    return await self.user_bleed_attack(ctx, result, cursor)

                # User wants to use betrayal
                elif 'betrayal' in arg.lower():
                    return await self.user_betrayal_attack(ctx, result, cursor)

                # User wants to use relentless
                elif 'relentless' in arg.lower():
                    return await self.user_relentless_attack(ctx, result, cursor)

                # User wants to use counter
                elif 'counter' in arg.lower():
                    return await self.user_counter_attack(ctx, result, cursor)

                # User wants to use assassinate
                elif 'assassinate' in arg.lower():
                    return await self.user_assassinate_attack(ctx, result, cursor)

                # User wants to use bladestorm
                elif 'bladestorm' in arg.lower():
                    return await self.user_bladestorm_attack(ctx, result, cursor)
                
                # User wants to use backstab
                elif 'backstab' in arg.lower():
                    return await self.user_backstab_attack(ctx, result, cursor)

            return await ctx.send("Invalid command. To cast a spell/ability in pvp, use the command `!pvp cast [spell name]`")

    # ---------------------------- BASIC ATTACK --------------------------------------

    async def user_basic_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'basic', 0)

        # Dodge and Block booleans
        dodge = False
        block = False

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

                # Gambler has lost the duel
                if result['current_hp'] - 5 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 5}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    await self.reset_duel(ctx, result, cursor)
                    
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 5}/{result['max_hp']}**")
                    await ctx.send("---------------------------------------------")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 5 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                        temp_player = self.turn_player
                        self.turn_player = self.other_player
                        self.other_player = temp_player
                        return
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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            dodge = True
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack missed!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
                    
            await ctx.send("---------------------------------------------")
            if self.turn_player['relentless_active'] == 0 and result['class'] != "rogue":
                temp_player = self.turn_player
                self.turn_player = self.other_player
                self.other_player = temp_player
                return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            block = True
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack was blocked!")
            await ctx.send("---------------------------------------------")
            if self.turn_player['relentless_active'] == 0 and result['class'] != "rogue":
                temp_player = self.turn_player
                self.turn_player = self.other_player
                self.other_player = temp_player
                return
        
        if not dodge and not block:
            # Calculate damage
            damage = 10 + result['main_hand_damage'] + result['off_hand_damage']
            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance'] or self.turn_player['precision_active'] > 0:
                damage *= 2
                if self.turn_player['precision_active'] > 0:
                    cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name} dealt **{damage}** damage to {self.other_player['username']}!")
            
            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                    if result['class'] != "rogue":
                        temp_player = self.turn_player
                        self.turn_player = self.other_player
                        self.other_player = temp_player
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

        if result['class'] == "rogue":
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name}'s attack missed!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                await ctx.send("---------------------------------------------")
                if self.turn_player['relentless_active'] == 0:
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
                    return
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.name}'s attack was blocked!")
                await ctx.send("---------------------------------------------")
                if self.turn_player['relentless_active'] == 0:
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
                    return
                
            # Calculate damage
            damage = 10 + result['main_hand_damage'] + result['off_hand_damage']
            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance'] or self.turn_player['precision_active'] > 0:
                damage *= 2
                if self.turn_player['precision_active'] > 0:
                    cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name} dealt **{damage}** damage to {self.other_player['username']}!")
        
            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

        # If relentless active, attack again
        if self.turn_player['relentless_active'] > 0:
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)            
            await ctx.send(f"{ctx.author.name} is relentless and attacks again!")
            await ctx.send("---------------------------------------------")
            await self.user_basic_attack(ctx, result, cursor)

        await ctx.send("---------------------------------------------")

    # ----------------------------- WARRIOR ABILITIES --------------------------------------

    # Warrior crush attack
    async def user_crush_attack(self, ctx, result, cursor):  
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        # Check to see if user stunned the enemy
        stun_check = random.randint(1, 100)
        if stun_check <= 50:
            await ctx.send(f"{result['username']} stunned {self.other_player['username']}!")
            await ctx.send("---------------------------------------------")
        else:
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

    # Warrior flurry attack
    async def user_flurry_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(3):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance']:
                    damage *= 2
                    await ctx.send(f"**Critical Hit!**")

                total_damage += damage

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")
            
        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
                temp_player = self.turn_player
                self.turn_player = self.other_player
                self.other_player = temp_player
                await ctx.send("---------------------------------------------")
                return 
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")            

    # Warrior shieldbash attack
    async def user_shieldbash_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has a 50% greater chance to block the next attack!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        # Activate shieldbash
        cursor.execute(f"UPDATE Characters SET shieldbash_active = 1 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return


    # Warrior bloodthirst attack
    async def user_bloodthirst_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

         # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        # Heal for damage done
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} healed for **{damage}** HP!")
        # Update user HP
        if result['current_hp'] + damage >= result['max_hp']:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
        else:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Warrior execute attack
    async def user_execute_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        if self.other_player['current_hp'] / self.other_player['max_hp'] <= 0.3:
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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

         # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Warrior headbutt attack
    async def user_headbutt_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has also done 30 damage to themself!")

        # Deal headbutt damage to user
        if result['current_hp'] - 30 <= 0:
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
            await ctx.send(f"**{self.other_player['username']} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        else:
            # Display current HP
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 30 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Warrior haymaker attack
    async def user_haymaker_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if warrior missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30 - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} missed the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 100 + result['main_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2
            await ctx.send(f"**Critical Hit!**")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Warrior whirlwind attack
    async def user_whirlwind_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
                    
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        total_damage = 0
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} is still whirling and attacks again!")
            else:
                whirlwind = False

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Warrior retaliate attack
    async def user_retaliate_attack(self, ctx, result, cursor):
        return await ctx.send("Not usable in PVP i'm too lazy to program it fuck you.")

    # Warrior takedown attack
    async def user_takedown_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")
        
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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} has also done 100 damage to themself!")

        # Deal takedown damage to user
        if result['current_hp'] - 100 <= 0:
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 100}/{result['max_hp']}**")
            await ctx.send(f"**{self.other_player['username']} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        else:
            # Display current HP
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 100}/{result['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 100 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
            
        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # -------------------------------- HUNTER ABILITIES --------------------------------

    # Hunter trishot attack
    async def user_trishot_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Check to see if user can use this attack
        if result['class'] != "hunter":
            return await ctx.send("Only hunters can use the Trishot attack!")
        
        # Check to see if trishot is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Trishot attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        # Total damage
        total_damage = 0

        for _ in range(3):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = 10 + result['main_hand_damage'] + result['off_hand_damage']

                # Check if user critical hit
                crit_check = random.randint(1, 100)
                if crit_check <= result['crit_chance'] or self.turn_player['precision_active'] > 0:
                    damage *= 2
                    if self.turn_player['precision_active'] > 0:
                        cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM Characters WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter precision attack
    async def user_precision_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        self.turn_player = cursor.fetchone()
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} is precise and their next 3 attacks will be critical hits!")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter blind attack
    async def user_blind_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 20 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        # Output blind message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.other_player['username']} has been blinded and has an additional 50% chance to miss their next attack!")
        cursor.execute(f"UPDATE Characters SET gouge_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter snipe attack
    async def user_snipe_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter rapidfire attack
    async def user_rapidfire_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(5):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"**Critical Hit!**")

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter bear attack
    async def user_bear_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 30

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance']:
            damage *= 2

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']}'s bear companion dealt **{damage}** damage and stunned {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        await ctx.send("---------------------------------------------")
        return

    # Hunter headshot attack
    async def user_headshot_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Check to see if hunter insta killed the enemy
        instakill_check = random.randint(1, 100)
        if instakill_check <= 5:
            await ctx.send(f"{result['username']} has landed a headshot and instantly killed {self.other_player['username']}!")
            return await self.reset_duel(ctx, result, cursor)

        else:
            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Hunter volley attack
    async def user_volley_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        volley = True
        total_damage = 0

        while volley:
            # Calculate damage
            damage = 50 + result['main_hand_damage'] + result['off_hand_damage']

            # Check if user critical hit
            crit_check = random.randint(1, 100)
            if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                damage *= 2
                if result['precision_active'] > 0:
                    cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"**Critical Hit!**")

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} volley strikes again!")
            else:
                volley = False

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter powershot attack
    async def user_powershot_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 150 + result['main_hand_damage'] + result['off_hand_damage']

        # Check if user critical hit
        crit_check = random.randint(1, 100)
        if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
            damage *= 2
            if result['precision_active'] > 0:
                cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**Critical Hit!**")

        # Check to see if hunter missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s Powershot was interrupted!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return
        
        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Hunter unload attack
    async def user_unload_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(10):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Calculate damage
                damage = (10 + result['main_hand_damage'] + result['off_hand_damage']) * 2

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

       # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # --------------------------- GAMBLER ABILITIES ------------------------------

    # Gambler deal attack
    async def user_deal_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Check to see if user can use this attack
        if result['class'] != "gambler":
            return await ctx.send("Only gamblers can use the Deal attack!")
        
        # Check to see if deal is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Deal attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        # Total damage
        total_damage = 0

        # Check to see how many times deal attacks
        deal_check = random.randint(1, 20)
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt {deal_check} attacks!")

        for _ in range(deal_check):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE Characters SET gouge_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE Characters SET shieldbash_active = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage
                
        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Gambler jack attack
    async def user_jack_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            # Gambler has lost the duel
            if result['current_hp'] - 10 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 10}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 10}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 10 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler queen attack
    async def user_queen_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            
            # Gambler has lost the duel
            if result['current_hp'] - 20 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler king attack
    async def user_king_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            
            # Gambler has lost the duel
            if result['current_hp'] - 30 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 30}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 30 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler Ace attack
    async def user_ace_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            
            # Gambler has lost the duel
            if result['current_hp'] - 40 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 40}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 40}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 40 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler joker attack
    async def user_joker_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")
        
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
            
            # Gambler has lost the duel
            if result['current_hp'] - 50 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 50}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 50}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 50 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler straight attack
    async def user_straight_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            
            # Gambler has lost the duel
            if result['current_hp'] - 60 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 60}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 60}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 60 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler flush attack
    async def user_flush_attack(self, ctx, result, cursor):
        # Check if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
           
            # Gambler has lost the duel
            if result['current_hp'] - 70 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 70}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 70}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 70 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler blackjack attack
    async def user_blackjack_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            
            # Gambler has lost the duel
            if result['current_hp'] - 80 <= 0:
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 80}/{result['max_hp']}**")
                await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
                
            else:
                # Display current HP
                await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 80}/{result['max_hp']}**")
                await ctx.send("---------------------------------------------")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 80 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    self.turn_player = cursor.fetchone()
                    temp_player = self.turn_player
                    self.turn_player = self.other_player
                    self.other_player = temp_player
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Check duelists hp
            if self.other_player['current_hp'] - damage <= 0:
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                await ctx.send(f"**{ctx.author.name} has won the duel!**")
                return await self.reset_duel(ctx, result, cursor)
            
            else:
                # Display current HP
                await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
                # Update HP in DB
                try:
                    cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character HP.")

            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Gambler roulette attack
    async def user_roulette_attack(self, ctx, result, cursor):
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
            await ctx.send(f"**{self.other_player['username']} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
                
        # Gambler's attack succeeds
        else:
            async with ctx.typing():
                await asyncio.sleep(5)
            await ctx.send("**BLACK!**")

            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**{self.turn_player['username']} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)

    # ------------------------------- MAGE ABILTIES --------------------------------------

    # Mage fireball attack
    async def user_fireball_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()          
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
            await ctx.send(f"{self.other_player['username']} was burned for 20 additional damage!")
            damage += 20

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage frostbolt attack
    async def user_frostbolt_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
            await ctx.send(f"{self.other_player['username']} was frozen!")
            freeze = True

        # Output damage message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        if not freeze:
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Mage iceblock attack
    async def user_iceblock_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")
        else:
            try:
                await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] + 50}/{result['max_hp']}**")
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 50 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
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

        cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_3', 3)

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage lifesteal attack
    async def user_lifesteal_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']} and healed for **{damage}** HP!")

        # Heal user
        if result['current_hp'] + damage > result['max_hp']:
            try:
                await ctx.send(f"{result['username']}'s HP: **{result['max_hp']}/{result['max_hp']}**")
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")
        else:
            try:
                await ctx.send(f"{result['username']}'s HP: **{result['current_hp'] + damage}/{result['max_hp']}**")
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {damage} WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
                self.turn_player = cursor.fetchone()
            except Exception as e:
                print(e)
                await ctx.send(f"An error occurred while updating HP")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage wildfire attack
    async def user_wildfire_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0
        
        for _ in range(5):
            dodge = False
            block = False

            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                    await ctx.send(f"{self.other_player['username']} was burned for 20 additional damage!")
                    damage += 20

                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage blizzard attack
    async def user_blizzard_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Check to see if user can use this attack
        if result['class'] != "mage":
            return await ctx.send("Only mages can use the Blizzard attack!")
        if result['level'] < 6:
            return await ctx.send("You need to be at least level 6 to use the Blizzard attack!")
        
        # Check to see if blizzard is on cooldown
        if result['cooldown_6'] > 0:
            return await ctx.send(f"{result['username']}'s Blizzard attack is on cooldown for {result['cooldown_6']} more turns!")
        
        freeze = False
        total_damage = 0
        
        for _ in range(5):
            dodge = False
            block = False

            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True

            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                    await ctx.send(f"{self.other_player['username']} was frozen!")
                    freeze = True
                    
                # Output damage message
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage evocation attack
    async def user_evocation_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        cursor.execute(f"SELECT * FROM Characters WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage lightning attack
    async def user_lightning_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        lightning = True
        total_damage = 0

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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

            # Check to see if whirlwind retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} lightning strikes again!")
            else:
                lightning = False

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_8', 5)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage pyroblast attack
    async def user_pyroblast_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")
        
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
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the attack!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the attack!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

        # Calculate damage
        damage = 150 + result['main_hand_damage'] + result['off_hand_damage']

        # Check to see if mage missed
        hit_check = random.randint(1, 100)
        if hit_check <= 30:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s Pyroblast was interrupted!")
            await ctx.send("---------------------------------------------")
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            return

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
        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

        # Check duelists hp
        if self.other_player['current_hp'] - damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Mage storm attack
    async def user_storm_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        lightning_dodge = False
        lightning_block = False

        total_damage = 0

        freeze = False
        lightning = True

        # ----------------- FIREBALL SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if self.other_player['gouge_active'] > 0:
            dodge_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the fireball!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            fireball_dodge = True

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if self.other_player['shieldbash_active'] > 0:
            block_check -= 50
            cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
            self.other_player = cursor.fetchone()
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the fireball!")
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
                await ctx.send(f"{self.other_player['username']} was burned for 20 additional damage!")
                damage += 20

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

        # ----------------- FROSTBOLT SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the frostbolt!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            frostbolt_dodge = True

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the frostbolt!")
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
                await ctx.send(f"{self.other_player['username']} was frozen!")
                freeze = True

            # Output damage message
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

        # ------------------ LIGHTNING SECTION -----------------

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} dodged the lightning!")
            if self.other_player['counter_active'] > 0:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                # Check if counterattack wins the duel for the enemy
                if result['current_hp'] - 20 <= 0:
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                    return await self.reset_duel(ctx, result, cursor)
                
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                        self.turn_player = cursor.fetchone()
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)
            await ctx.send("---------------------------------------------")
            lightning_dodge = True

        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.other_player['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} blocked the lightning!")
            # Update cooldowns
            await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)
            await ctx.send("---------------------------------------------")
            lightning_block = True

        while lightning and not lightning_dodge and not lightning_block:
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
            await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

            # Add to total damage
            total_damage += damage

            # Check to see if lightning retriggers
            retrigger_check = random.randint(1, 100)
            if retrigger_check <= 50:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{result['username']} lightning strikes again!")
            else:
                lightning = False

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_10', 10)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # ---------------------------------- ROGUE ATTACKS --------------------------------------

    # Rogue gouge attack
    async def user_gouge_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Gouge attack!")

        # Check to see if gouge is on cooldown
        if result['cooldown_1'] > 0:
            return await ctx.send(f"{result['username']}'s Gouge attack is on cooldown for {result['cooldown_1']} more turns!")
        
        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_1', 3)

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Output blind message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{self.other_player['username']} has been blinded and has an additional 50% chance to miss their next attack!")
        cursor.execute(f"UPDATE Characters SET gouge_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_gouge_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue stab attack
    async def user_stab_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_stab_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue sap attack
    async def user_sap_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Check to see if enemy stunned
        sap = False
        stun_check = random.randint(1, 100)
        if stun_check <= 50:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{self.other_player['username']} has been sapped and will miss their next turn!")
            sap = True
            
        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_sap_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        if not sap:                                                
            temp_player = self.turn_player
            self.turn_player = self.other_player
            self.other_player = temp_player
            await ctx.send("---------------------------------------------")
            return

    # Rogue bleed attack
    async def user_bleed_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Heal HP
        if result['current_hp'] + total_damage > result['max_hp']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s HP: {result['max_hp']}/{result['max_hp']}")
            cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        else:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s HP: {result['current_hp'] + total_damage}/{result['max_hp']}")
            cursor.execute(f"UPDATE Characters SET current_hp = current_hp + {total_damage} WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_bleed_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue betrayal attack
    async def user_betrayal_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_betrayal_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue relentless attack
    async def user_relentless_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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
        self.turn_player = cursor.fetchone()

        # Update cooldowns
        await self.update_cooldowns(ctx, result, cursor, 'cooldown_6', 100)

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue counter attack
    async def user_counter_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                    
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Ouput counter message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"{result['username']} dodges will do 20 damage and interrupt the enemy's attack for the rest of the fight!")
        cursor.execute(f"UPDATE Characters SET counter_active = 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
        self.turn_player = cursor.fetchone()

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            self.turn_player = cursor.fetchone()
            await self.user_counter_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue assassinate attack
    async def user_assassinate_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")
        
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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
                block = True

            if not dodge and not block:
                # Check for instant kill
                if self.other_player['current_hp'] / self.other_player['max_hp'] <= 0.3:
                    instakill_check = random.randint(1, 100)
                    if instakill_check >= 30:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{result['username']} has assassinated {self.other_player['username']} for an instant kill!")
                        return await self.reset_duel(ctx, result, cursor)
                
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
                        await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                        # Add to total damage
                        total_damage += damage
        
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
                    await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                    # Add to total damage
                    total_damage += damage

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            await self.user_assassinate_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue bladestorm attack
    async def user_bladestorm_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

        # Check to see if user can use this attack
        if result['class'] != "rogue":
            return await ctx.send("Only rogues can use the Bladestorm attack!")
        if result['level'] < 9:
            return await ctx.send("You need to be at least level 9 to use the Bladestorm attack!")

        # Check to see if bladestorm is on cooldown
        if result['cooldown_9'] > 0:
            return await ctx.send(f"{result['username']}'s Bladestorm attack is on cooldown for {result['cooldown_9']} more turns!")

        bladestorm = True
        total_damage = 0

        while bladestorm:

            for _ in range(2):
                dodge = False
                block = False
                # Check to see if enemy dodged
                dodge_check = random.randint(1, 100)
                if self.other_player['gouge_active'] > 0:
                    dodge_check -= 50
                    cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} dodged the attack!")
                    if self.other_player['counter_active'] > 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                        # Check if counterattack wins the duel for the enemy
                        if result['current_hp'] - 20 <= 0:
                            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                            await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                            return await self.reset_duel(ctx, result, cursor)
                
                        else:
                            # Display current HP
                            await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                            # Update HP in DB
                            try:
                                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                                self.turn_player = cursor.fetchone()
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character HP.")
                    dodge = True
                    
                # Check to see if enemy blocked
                block_check = random.randint(1, 100)
                if self.other_player['shieldbash_active'] > 0:
                    block_check -= 50
                    cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                    cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                    self.other_player = cursor.fetchone()
                if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} blocked the attack!")
                    block = True

                if not dodge and not block:
                    # Calculate damage
                    damage = 25 + result['main_hand_damage'] + result['off_hand_damage']

                    # Check if user critical hit
                    crit_check = random.randint(1, 100)
                    if crit_check <= result['crit_chance'] or result['precision_active'] > 0:
                        damage *= 2
                        if result['precision_active'] > 0:
                            cursor.execute(f"UPDATE Characters SET precision_active = precision_active - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"**Critical Hit!**")

                    # Output damage message
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                    # Add to total damage
                    total_damage += damage

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
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            await self.user_bladestorm_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

    # Rogue backstab attack
    async def user_backstab_attack(self, ctx, result, cursor):
        # Check to see if it is the user's turn
        if self.turn_player['username'] != ctx.author.name:
            return await ctx.send("It is not your turn.")

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

        # Total damage
        total_damage = 0

        for _ in range(2):
            dodge = False
            block = False
            # Check to see if enemy dodged
            dodge_check = random.randint(1, 100)
            if self.other_player['gouge_active'] > 0:
                dodge_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `gouge_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if dodge_check <= self.other_player['dodge_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} dodged the attack!")
                if self.other_player['counter_active'] > 0:
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{self.other_player['username']} counterattacks for 20 damage!")
                    # Check if counterattack wins the duel for the enemy
                    if result['current_hp'] - 20 <= 0:
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        await ctx.send(f"**{self.other_player['username']} has won the duel!**")
                        return await self.reset_duel(ctx, result, cursor)
                
                    else:
                        # Display current HP
                        await ctx.send(f"{ctx.author.name}'s HP: **{result['current_hp'] - 20}/{result['max_hp']}**")
                        # Update HP in DB
                        try:
                            cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 20 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                            self.turn_player = cursor.fetchone()
                        except Exception as e:
                            print(e)
                            return await ctx.send("Error updating character HP.")
                dodge = True
                
            # Check to see if enemy blocked
            block_check = random.randint(1, 100)
            if self.other_player['shieldbash_active'] > 0:
                block_check -= 50
                cursor.execute(f"UPDATE `Characters` SET `shieldbash_active` = 0 WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")  
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            if block_check <= self.other_player['block_chance'] - result['hit_chance']:
                async with ctx.typing():
                    await asyncio.sleep(2)
                await ctx.send(f"{self.other_player['username']} blocked the attack!")
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
                await ctx.send(f"{result['username']} dealt **{damage}** damage to {self.other_player['username']}!")

                # Add to total damage
                total_damage += damage

        # Relentless
        if self.turn_player['relentless_active'] > 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{result['username']}'s is relentless and attacks again!")
            cursor.execute(f"UPDATE Characters SET relentless_active = 0 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            await self.user_backstab_attack(ctx, result, cursor)

        # Check duelists hp
        if self.other_player['current_hp'] - total_damage <= 0:
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            await ctx.send(f"**{ctx.author.name} has won the duel!**")
            return await self.reset_duel(ctx, result, cursor)
        
        else:
            # Display current HP
            await ctx.send(f"{self.other_player['username']}'s HP: **{self.other_player['current_hp'] - total_damage}/{self.other_player['max_hp']}**")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {total_damage} WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{self.other_player['username']}' AND `guild_id` = '{ctx.guild.id}'")
                self.other_player = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")

        temp_player = self.turn_player
        self.turn_player = self.other_player
        self.other_player = temp_player
        await ctx.send("---------------------------------------------")
        return

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
    
    async def reset_duel(self, ctx, result, cursor):
        # Update HP in DB
        try:
            cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"UPDATE Characters SET cooldown_1 = 0, cooldown_2 = 0, cooldown_3 = 0, cooldown_4 = 0, cooldown_5 = 0, cooldown_6 = 0, cooldown_7 = 0, cooldown_8 = 0, cooldown_9 = 0, cooldown_10 = 0 WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"UPDATE Characters SET precision_active = 0, relentless_active = 0, gouge_active = 0, counter_active = 0, shieldbash_active = 0  WHERE username = '{result['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"UPDATE Characters SET cooldown_1 = 0, cooldown_2 = 0, cooldown_3 = 0, cooldown_4 = 0, cooldown_5 = 0, cooldown_6 = 0, cooldown_7 = 0, cooldown_8 = 0, cooldown_9 = 0, cooldown_10 = 0 WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
            cursor.execute(f"UPDATE Characters SET precision_active = 0, relentless_active = 0, gouge_active = 0, counter_active = 0, shieldbash_active = 0  WHERE username = '{self.other_player['username']}' AND guild_id = '{ctx.guild.id}'")
        except Exception as e:
            print(e)
            return await ctx.send("Error updating character HP.")
        
        self.turn_player = None
        self.turn_player_num = None
        self.other_player = None
        self.active_duel = False
        self.duelists = []

async def setup(bot):
    await bot.add_cog(Pvp(bot))
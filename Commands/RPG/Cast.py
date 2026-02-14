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
        self.participants = []
        self.classes = ["warrior", "hunter", "mage", "rogue", "gambler"]
        self.slots = ["boots", "legs", "chest", "gloves", "helmet", "main_hand", "off_hand"]
        self.good_loot_drop = None
        self.rare_loot_drop = None
        self.epic_loot_drop = None
        self.legendary_loot_drop = None
        self.highest_loot_roll = None
        self.loot_winner = None

    # Cast function
    @commands.command(aliases=['attack', 'spell'])
    async def cast(self, ctx, *args):
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
        battle_cog = self.bot.get_cog("Battle")
        if not battle_cog.encounter:
            return await ctx.send("There is no active battle dumbass.")
        
        self.enemy = battle_cog.enemy
        
        # User wants to basic attack
        if len(args) == 0:
            await self.user_basic_attack(ctx, result, cursor, False, battle_cog)

    async def user_basic_attack(self, ctx, result, cursor, deal, battle_cog):
        # Add user to particpants list
        if result not in self.participants:
            self.participants.append(result)

        if result['class'] == "gambler" and not deal:
            # Check to see if Gambler failed
            gambler_random = random.randint(1, 100)
            await ctx.send(f"{ctx.author.name}'s basic attack was a...")
            async with ctx.typing():
                await asyncio.sleep(2)

            # Gambler failed and hurt themself
            if gambler_random < 11 - result['hit_chance']:
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
                    await ctx.send(f"**{ctx.author.name}** has died!")
                    self.participants.remove(result)
                    # Delete character
                    try:
                        cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error deleting character.")
                else:
                    # Display current HP
                    await ctx.send(f"{ctx.author.name}'s HP: {result['current_hp'] - 5}/{result['max_hp']}")
                    await ctx.send("------------------------------------------------------")
                    # Update HP in DB
                    try:
                        cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - 5 WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                    except Exception as e:
                        print(e)
                        return await ctx.send("Error updating character HP.")
                    
            # Gambler's basic attack succeeds
            else:
                await ctx.send("**Success!**")

        # Check to see if enemy dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= self.enemy[ctx.guild.id]['dodge_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack missed!")
            await ctx.send("------------------------------------------------------")
            if result['relentless_active'] == 0:
                await self.choose_enemy_attack(ctx, result, cursor)
            
        # Check to see if enemy blocked
        block_check = random.randint(1, 100)
        if block_check <= self.enemy[ctx.guild.id]['block_chance'] - result['hit_chance']:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.name}'s attack was blocked!")
            await ctx.send("------------------------------------------------------")
            if result['relentless_active'] == 0:
                await self.choose_enemy_attack(ctx, result, cursor)
        
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
        await ctx.send(f"{ctx.author.name} dealt **{damage}** damage to the {self.enemy[ctx.guild.id]['name']}!")
        
        # Update enemy HP
        self.enemy[ctx.guild.id]['current_hp'] -= damage

        # Check if enemy died
        if self.enemy[ctx.guild.id]['current_hp'] <= 0:
            async with ctx.typing():
                await asyncio.sleep(2)
            await ctx.send(f"**The {self.enemy[ctx.guild.id]['name']} has been defeated!**")
            battle_cog.encounter = False

            # Distribute EXP, gold and loot to participants
            for participant in self.participants:
                # Update EXP
                try:
                    if participant['level'] < 10:
                        # Output EXP message
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        await ctx.send(f"{participant['username']} gained {self.enemy[ctx.guild.id]['exp']} EXP!")
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
                    async with ctx.typing():
                        await asyncio.sleep(2)
                    await ctx.send(f"{participant['username']} received {self.enemy[ctx.guild.id]['gold']} Gold!")  
                    cursor.execute(f"UPDATE Characters SET gold = gold + {self.enemy[ctx.guild.id]['gold']} WHERE username = '{participant['username']}' AND guild_id = '{ctx.guild.id}'")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error updating character Gold.")
                await ctx.send(f"**{participant['username']}** received {self.enemy[ctx.guild.id]['exp']} EXP and {self.enemy[ctx.guild.id]['gold']} Gold!")
            
            # Loot
            good_loot_check = random.randint(1, 100)

            # Good loot dropped
            if good_loot_check <= self.enemy[ctx.guild.id]['good_drop_chance']:
                # Determine what piece of loot dropped
                loot_class = random.choice(self.classes)
                loot_slot = random.choice(self.slots)

                # Output what dropped
                async with ctx.typing():
                    await asyncio.sleep(2)
                await self.distribute_loot(ctx, loot_class, loot_slot, "good", cursor)

            # Clear participants list
            self.participants = []

    async def enemy_basic_attack(self, ctx, result, cursor):
        # Output enemy attack message
        async with ctx.typing():
            await asyncio.sleep(2)
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} uses basic attack!")

        # Check to see if user dodged
        dodge_check = random.randint(1, 100)
        if dodge_check <= result['dodge_chance']:
            async with ctx.typing():
                    await asyncio.sleep(2)
            return await ctx.send(f"{result['username']} dodged the attack!")

        # Check to see if user blocked
        block_check = random.randint(1, 100)
        if block_check <= result['block_chance']:
            async with ctx.typing():
                    await asyncio.sleep(2)
            return await ctx.send(f"{result['username']} blocked the attack!")

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
        await ctx.send(f"The {self.enemy[ctx.guild.id]['name']} dealt {damage} damage to {result['username']}!")

        # User dies
        if result['current_hp'] - damage <= 0:
            file_path = f"Images/respects.gif"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send(f"**{result['username']}** has died!")
            self.participants.remove(result)
            # Delete character
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")
        
        # User didn't die, update their current HP
        else:
            # Display current HP
            await ctx.send(f"{result['username']}'s HP: {result['current_hp'] - damage}/{result['max_hp']}")
            # Update HP in DB
            try:
                cursor.execute(f"UPDATE `Characters` SET `current_hp` = `current_hp` - {damage} WHERE `username` = '{result['username']}' AND `guild_id` = '{ctx.guild.id}'")
            except Exception as e:
                print(e)
                return await ctx.send("Error updating character HP.")
    
    async def choose_enemy_attack(self, ctx, result, cursor):
        enemy_attack = random.choice(self.enemy[ctx.guild.id]['attacks'])
        if enemy_attack == "basic":
            await self.enemy_basic_attack(ctx, result, cursor)
        elif enemy_attack == "fireball":
            await self.enemy_fireball_attack(ctx, result, cursor)
        elif enemy_attack == "frostbolt":
            await self.enemy_frostbolt_attack(ctx, result, cursor)
        elif enemy_attack == "trishot":
            await self.enemy_trishot_attack(ctx, result, cursor)
        elif enemy_attack == "snipe":
            await self.enemy_snipe_attack(ctx, result, cursor)
        elif enemy_attack == "sap":
            await self.enemy_sap_attack(ctx, result, cursor)
        elif enemy_attack == "stab":
            await self.enemy_stab_attack(ctx, result, cursor)
        elif enemy_attack == "crush":
            await self.enemy_crush_attack(ctx, result, cursor)
        elif enemy_attack == "flurry":
            await self.enemy_flurry_attack(ctx, result, cursor)
        elif enemy_attack == "haymaker":
            await self.enemy_haymaker_attack(ctx, result, cursor)
        elif enemy_attack == "lifesteal":
            await self.enemy_lifesteal_attack(ctx, result, cursor)
        elif enemy_attack == "wildfire":
            await self.enemy_wildfire_attack(ctx, result, cursor)
        elif enemy_attack == "lightning":
            await self.enemy_lightning_attack(ctx, result, cursor)
        elif enemy_attack == "rapidfire":
            await self.enemy_rapidfire_attack(ctx, result, cursor)
        elif enemy_attack == "volley":
            await self.enemy_volley_attack(ctx, result, cursor)
        elif enemy_attack == "bladestorm":
            await self.enemy_bladestorm_attack(ctx, result, cursor)
        elif enemy_attack == "beserk":
            await self.enemy_beserk_attack(ctx, result, cursor)

    async def distribute_loot(self, ctx, loot_class, loot_slot, rarity, cursor):
        # Get list of participants by class
        warriors = []
        hunters = []
        mages = []
        rogues = []
        gamblers = []

        for participant in self.participants:
            if participant['class'] == 'warrior':
                warriors.append(participant)
            elif participant['class'] == 'hunter':
                hunters.append(participant)
            elif participant['class'] == 'mage':
                mages.append(participant)
            elif participant['class'] == 'rogue':
                rogues.append(participant)
            elif participant['class'] == 'gambler':
                gamblers.append(participant)

        # Distribute good loot drop
        if rarity == "good":
            # Good warrior gear dropped
            if loot_class == 'warrior':
                # Good warrior boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Asskicking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Asskicking (+20 Max HP)")

                    # No warriors participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight       
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good warrior greaves dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Greaves of Asskicking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Greaves of Asskicking (+20 Max HP)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Greaves of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Greaves of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Greaves of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one warrior needs the loot, they get it   
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Greaves of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Greaves of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good warrior chestplate dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Chestplate of Asskicking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Chestplate of Asskicking (+20 Max HP)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Chestplate of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Chestplate of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Chestplate of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Chestplate of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gauntlets of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good warrior gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gauntlets of Asskicking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gauntlets of Asskicking (+20 Max HP)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gauntlets of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gauntlets of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gauntlets of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Gauntlets of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gauntlets of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good warrior helmet dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Helmet of Asskicking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Helmet of Asskicking (+20 Max HP)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Helmet of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Helmet of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Helmet of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Helmet of Asskicking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Helmet of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good warrior main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Sword of Asskicking (+5 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Sword of Asskicking (+5 Damage)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Sword of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Sword of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Sword of Asskicking (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Sword of Asskicking (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Sword of Asskicking (+20 HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good warrior off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Shield of Asskicking (+1% Block Chance) has dropped!")
                    self.good_loot_drop = ("🟩 Good Shield of Asskicking (+1% Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Good mage gear dropped       
            elif loot_class == 'mage':
                # Good mage boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Casting Spells and Shit (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Casting Spells and Shit (+20 Max HP)")

                    # No warriors participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight       
                    else:
                        # See which mage the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good mage pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Casting Spells and Shit (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Casting Spells and Shit (+20 Max HP)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one mage needs the loot, they get it   
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good mage robes dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Robes of Casting Spells and Shit (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Robes of Casting Spells and Shit (+20 Max HP)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mage need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good mage gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Casting Spells and Shit (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good mage hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Hood of Casting Spells and Shit (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Hood of Casting Spells and Shit (+20 Max HP)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good mage main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Staff of Casting Spells and Shit (+5 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Staff of Casting Spells and Shit (+5 Damage)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good mage off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Spellbook of Casting Spells and Shit (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Good rogue gear dropped             
            elif loot_class == 'rogue':
                # Good rogue boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Shanking (+20 Max HP)")

                    # No rogues participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight       
                    else:
                        # See which rogue the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good rogue pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one rogue needs the loot, they get it   
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue vest dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Vest of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Vest of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogue need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Hood of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Hood of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Hood of Shanking (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Hood of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Dagger of Shanking (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Dagger of Shanking (+1 Damage)")

                    # No rogue participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good rogue off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Dagger of Shanking (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Dagger of Shanking (+1 Damage)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
            # Good hunter gear dropped             
            elif loot_class == 'hunter':
                # Good hunter boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight       
                    else:
                        # See which hunter the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good hunter pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one hunter needs the loot, they get it   
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter chainmail dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunter need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)")

                    # No hunter participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good hunter off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Good gambler gear dropped             
            elif loot_class == 'gambler':
                # Good gambler boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Luck (+20 Max HP)")

                    # No gamblers participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight       
                    else:
                        # See which gambler the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good gambler pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one gambler needs the loot, they get it   
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler jacket dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good jacket of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good jacket of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gambler need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler fedora dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Fedora of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Fedora of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Fedora of Luck (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Fedora of Luck (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Trinket of Luck (+5% Chance of Success) has dropped!")
                    self.good_loot_drop = ("🟩 Good Trinket of Luck (+5% Chance of Success)")

                    # No gambler participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good gambler off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Charm of Luck (+1% Chance of Success) has dropped!")
                    self.good_loot_drop = ("🟩 Good Charm of Luck (+1% Chance of Success)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

        # Distribute rare loot drop
        elif rarity == "rare":
            # Rare warrior gear dropped
            if loot_class == 'warrior':
                # Rare warrior boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance) has dropped!")
                    self.rare_loot_drop = ("🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)")

                    # No warriors participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight       
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                           
                            if result['boots'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['boots'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if warriors_that_need_loot[0]['boots'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Rare warrior greaves dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟦 Rare Greaves of Asskicking (+20 Max HP, +1% Dodge & Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Greaves of Asskicking (+20 Max HP, +1% Dodge & Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Greaves of Asskicking! (+20 Max HP, +1% Dodge & Block Chance)")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Greaves of Asskicking! (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Greaves of Asskicking! (+20 Max HP, +1% Dodge & Block Chance)!")
                           # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['legs'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one warrior needs the loot, they get it   
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Greaves of Asskicking! (+20 Max HP, +1% Dodge & Block Chance)!")
                           # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if warriors_that_need_loot[0]['legs'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Greaves of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare warrior chestplate dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance) has dropped!")
                    self.rare_loot_drop = ("🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                             # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['chest'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if warriors_that_need_loot[0]['chest'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare warrior gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['gloves'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                           # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if warriors_that_need_loot[0]['gloves'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare warrior helmet dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Helmet of Asskicking (+20 HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Helmet of Asskicking (+20 HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['helmet'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if warriors_that_need_loot[0]['helmet'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Helmet of Asskicking (+20 HP, +1% Dodge & Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare warrior main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟦 Rare Sword of Asskicking (+10 Damage) has dropped!")
                    self.rare_loot_drop = ("🟦 Rare Sword of Asskicking (+10 Damage)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Sword of Asskicking (+10 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Sword of Asskicking (+10 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Sword of Asskicking (+10 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 10 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Sword of Asskicking (+10 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 10 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Sword of Asskicking (+10 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Rare warrior off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟦 Rare Shield of Asskicking (+3% Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Shield of Asskicking (+3% Block Chance)")

                    # No warriors participated in the fight
                    if len(warriors) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No warriors participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one warrior participated in the fight        
                    else:
                        # See which warriors the loot would be an upgrade for
                        warriors_that_need_loot = []
                        for warrior in warriors:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{warrior['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] < 3:
                                warriors_that_need_loot.append(warrior)
                        
                        # If multiple warriors need the loot, roll for it
                        if len(warriors_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple warriors need the loot. Rolling for Need.")
                            for warrior in warriors_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{warrior['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = warrior

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['off_hand'] == 2:
                                    cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one warrior needs the loot, they get it
                        elif len(warriors_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{warriors_that_need_loot[0]['username']}** has won the 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['off_hand'] == 2:
                                    cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 2 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{warriors_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No warriors need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No warriors need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Rare mage gear dropped       
            elif loot_class == 'mage':
                # Rare mage boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)")

                    # No warriors participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight       
                    else:
                        # See which mage the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] < 3:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['boots'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['boots'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Rare mage pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] < 3:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                                await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)! (+20 Max HP, +1% Dodge and Block Chance)!")
                                # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET legs = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['legs'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one mage needs the loot, they get it   
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)! (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET pants = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['pants'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare mage robes dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance) has dropped!")
                    self.rare_loot_drop = ("🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] < 3:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['chest'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['chest'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mage need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare mage gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] < 3:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                if self.loot_winner['gloves'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['gloves'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Rare mage hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance) has dropped!")
                    self.good_loot_drop = ("🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 100 gold in exchange for 🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 100 gold in exchange for 🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 100 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] < 3:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)! (+20 Max HP, +1% Dodge and Block Chance)")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['helmet '] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge and Block Chance)!")
                            # Update equipment
                            try:
                                cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                if mages_that_need_loot[0]['helmet'] == 2:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                else:
                                    cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1, block_chance = block_chance + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                    cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good mage main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Staff of Casting Spells and Shit (+5 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Staff of Casting Spells and Shit (+5 Damage)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good mage off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Spellbook of Casting Spells and Shit (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)")

                    # No mages participated in the fight
                    if len(mages) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No mages participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one mage participated in the fight        
                    else:
                        # See which mages the loot would be an upgrade for
                        mages_that_need_loot = []
                        for mage in mages:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                mages_that_need_loot.append(mage)
                        
                        # If multiple mages need the loot, roll for it
                        if len(mages_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple mages need the loot. Rolling for Need.")
                            for mage in mages_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{mage['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = mage

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one mage needs the loot, they get it
                        elif len(mages_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{mages_that_need_loot[0]['username']}** has won the 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{mages_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No mages need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No mages need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Good rogue gear dropped             
            elif loot_class == 'rogue':
                # Good rogue boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Shanking (+20 Max HP)")

                    # No rogues participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight       
                    else:
                        # See which rogue the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good rogue pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one rogue needs the loot, they get it   
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue vest dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Vest of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Vest of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogue need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Vest of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Hood of Shanking (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Hood of Shanking (+20 Max HP)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Hood of Shanking (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Hood of Shanking (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good rogue main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Dagger of Shanking (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Dagger of Shanking (+1 Damage)")

                    # No rogue participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{mage['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 1 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good rogue off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Dagger of Shanking (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Dagger of Shanking (+1 Damage)")

                    # No rogues participated in the fight
                    if len(rogues) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No rogues participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one rogue participated in the fight        
                    else:
                        # See which rogues the loot would be an upgrade for
                        rogues_that_need_loot = []
                        for rogue in rogues:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{rogue['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                rogues_that_need_loot.append(rogue)
                        
                        # If multiple rogues need the loot, roll for it
                        if len(rogues_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple rogues need the loot. Rolling for Need.")
                            for rogue in rogues_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{rogue['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = rogue

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one rogue needs the loot, they get it
                        elif len(rogues_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{rogues_that_need_loot[0]['username']}** has won the 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{rogues_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No rogues need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No rogues need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
            # Good hunter gear dropped             
            elif loot_class == 'hunter':
                # Good hunter boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight       
                    else:
                        # See which hunter the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good hunter pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one hunter needs the loot, they get it   
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter chainmail dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunter need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter hood dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good hunter main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)")

                    # No hunter participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET main_hand_damage = 5 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good hunter off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage) has dropped!")
                    self.good_loot_drop = ("🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)")

                    # No hunters participated in the fight
                    if len(hunters) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No hunters participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one hunter participated in the fight        
                    else:
                        # See which hunters the loot would be an upgrade for
                        hunters_that_need_loot = []
                        for hunter in hunters:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{hunter['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                hunters_that_need_loot.append(hunter)
                        
                        # If multiple hunters need the loot, roll for it
                        if len(hunters_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple hunters need the loot. Rolling for Need.")
                            for hunter in hunters_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{hunter['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = hunter

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one hunter needs the loot, they get it
                        elif len(hunters_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{hunters_that_need_loot[0]['username']}** has won the 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{hunters_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No hunters need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No hunters need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

            # Good gambler gear dropped             
            elif loot_class == 'gambler':
                # Good gambler boots dropped
                if loot_slot == 'boots':
                    await ctx.send("🟩 Good Boots of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Boots of Luck (+20 Max HP)")

                    # No gamblers participated in the fight, roll to see who gets the gold in exchange for the loot
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                        # Only one participant, they get the gold 
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Dagger of Shanking (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight       
                    else:
                        # See which gambler the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['boots'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Boots of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                # Good gambler pants dropped
                elif loot_slot == 'legs':
                    await ctx.send("🟩 Good Pants of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Pants of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['legs'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # Only one gambler needs the loot, they get it   
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Pants of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler jacket dropped
                elif loot_slot == 'chest':
                    await ctx.send("🟩 Good jacket of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good jacket of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['chest'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gambler need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Jacket of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler gloves dropped
                elif loot_slot == 'gloves':
                    await ctx.send("🟩 Good Gloves of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Gloves of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['gloves'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Gloves of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler fedora dropped      
                elif loot_slot == 'helmet':
                    await ctx.send("🟩 Good Fedora of Luck (+20 Max HP) has dropped!")
                    self.good_loot_drop = ("🟩 Good Fedora of Luck (+20 Max HP)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['helmet'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Fedora of Luck (+20 Max HP)! (+20 Max HP)")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Fedora of Luck (+20 Max HP)! (+20 Max HP)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Fedora of Luck (+20 Max HP)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

                # Good gambler main hand dropped      
                elif loot_slot == 'main_hand':
                    await ctx.send("🟩 Good Trinket of Luck (+5% Chance of Success) has dropped!")
                    self.good_loot_drop = ("🟩 Good Trinket of Luck (+5% Chance of Success)")

                    # No gambler participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['main_hand'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                            
                # Good gambler off hand dropped      
                elif loot_slot == 'off_hand':
                    await ctx.send("🟩 Good Charm of Luck (+1% Chance of Success) has dropped!")
                    self.good_loot_drop = ("🟩 Good Charm of Luck (+1% Chance of Success)")

                    # No gamblers participated in the fight
                    if len(gamblers) == 0:
                        async with ctx.typing():
                            await asyncio.sleep(2)
                        # Multiple participants need to roll for greed
                        if len(self.participants) > 1:
                            await ctx.send("No gamblers participated in the battle. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")
                        
                        # Only one participant, they get the gold
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.participants[0]['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.participants[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.") 

                    # At least one gambler participated in the fight        
                    else:
                        # See which gamblers the loot would be an upgrade for
                        gamblers_that_need_loot = []
                        for gambler in gamblers:
                            try:
                                cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{gambler['username']}' AND `guild_id` = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error fetching character data.")
                            result = cursor.fetchone()
                            if result['off_hand'] == 1:
                                gamblers_that_need_loot.append(gambler)
                        
                        # If multiple gamblers need the loot, roll for it
                        if len(gamblers_that_need_loot) > 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("Multiple gamblers need the loot. Rolling for Need.")
                            for gambler in gamblers_that_need_loot:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{gambler['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = gambler

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won the 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                        
                        # Only one gambler needs the loot, they get it
                        elif len(gamblers_that_need_loot) == 1:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{gamblers_that_need_loot[0]['username']}** has won the 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update equipment
                            try: 
                                cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                                cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{gamblers_that_need_loot[0]['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character equipment.")
                            
                        # No gamblers need the loot, roll for greed
                        else:
                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send("No gamblers need the loot. Rolling for greed.")
                            for participant in self.participants:
                                loot_roll = random.randint(1, 100)
                                async with ctx.typing():
                                    await asyncio.sleep(2)
                                await ctx.send(f"{participant['username']} rolled a {loot_roll}!")
                                if not self.highest_loot_roll or loot_roll > self.highest_loot_roll:
                                    self.highest_loot_roll = loot_roll
                                    self.loot_winner = participant

                            async with ctx.typing():
                                await asyncio.sleep(2)
                            await ctx.send(f"**{self.loot_winner['username']}** has won 50 gold in exchange for 🟩 Good Charm of Luck (+1% Chance of Success)!")
                            # Update gold
                            try: 
                                cursor.execute(f"UPDATE Characters SET gold = gold + 50 WHERE username = '{self.loot_winner['username']}' AND guild_id = '{ctx.guild.id}'")
                            except Exception as e:
                                print(e)
                                return await ctx.send("Error updating character Gold.")

async def setup(bot):
    await bot.add_cog(Cast(bot))
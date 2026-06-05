import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encounter = {}
        self.active_pokemon = {}
        self.user_pokemon_list = {}
        self.enemy_active_pokemon = {}
        self.enemy_pokemon = {}
        self.enemy_pokemon_list = {}
        self.common_pokemon = ['bulbasaur', 'charmander', 'squirtle', 'caterpie', 'weedle', 'pidgey', 'rattata', 'spearow', 'ekans', 
                             'pikachu', 'sandshrew', 'nidoran_female', 'nidoran_male', 'clefairy', 'vulpix', 'jigglypuff', 'zubat', 
                             'oddish', 'paras', 'venonat', 'diglett', 'meowth', 'psyduck', 'mankey', 'growlithe', 'poliwag', 'abra', 
                             'machop', 'bellsprout', 'tentacool', 'geodude', 'ponyta', 'slowpoke', 'magnemite', 'farfetchd', 'doduo', 
                             'seel', 'grimer', 'shellder', 'gastly', 'onix', 'drowzee', 'krabby', 'voltorb', 'exeggcute', 'cubone', 
                             'hitmonlee', 'hitmonchan', 'lickitung', 'koffing', 'rhyhorn', 'chansey', 'tangela', 'horsea', 
                             'goldeen', 'staryu', 'magikarp', 'eevee', 'porygon', 'omanyte', 'kabuto']
        self.rare_pokemon = ['lapras', 'snorlax', 'aerodactyl', 'dratini', 'magmar', 'kangaskhan', 
                             'scyther', 'tauros', 'electabuzz', 'pinsir' 'jynx', 'mr. mime']
        self.legendary_pokemon = ['articuno', 'zapdos', 'moltres', 'mewtwo', 'mew']
        self.pokemon_name = None

    # Battle function
    @commands.command()
    async def battle(self, ctx, *args):
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

        # Fetch user's trainer
        try:
            cursor.execute(f"SELECT * FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            trainer = cursor.fetchone()
            # User doesn't have a trainer
            if not trainer:
                return await ctx.send("You don't have a trainer dumbass.")
            
        except Exception as e:
            print(e)
            return await ctx.send("Error grabbing trainer details")
        
        # Create active battle tracker
        if ctx.guild.id not in self.encounter:
            self.encounter[ctx.guild.id] = {}
        else:
            if self.encounter[ctx.guild.id]['active_battle']:
                return await ctx.send("A battle is already in progress dumbass.")
            
        self.encounter[ctx.guild.id]['active_battle'] = True

        # Create enemy active pokemon
        if ctx.guild.id not in self.enemy_active_pokemon:
            self.enemy_active_pokemon[ctx.guild.id] = {}

        if ctx.guild.id not in self.enemy_pokemon:
            self.enemy_pokemon[ctx.guild.id] = {}

        # Create enemy pokemon list
        if ctx.guild.id not in self.enemy_pokemon_list:
            self.enemy_pokemon_list[ctx.guild.id] = []
            
        # Set user's active pokemon
        if ctx.guild.id not in self.active_pokemon:
            self.active_pokemon[ctx.guild.id] = None

        cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_1']}'")
        self.active_pokemon[ctx.guild.id] = cursor.fetchone()

        # Set user's pokemon list
        if ctx.guild.id not in self.user_pokemon_list:
            self.user_pokemon_list[ctx.guild.id] = []

        if trainer['pokemon_2'] and trainer['pokemon_2'] != "None":
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_2']}'")
            self.user_pokemon_list[ctx.guild.id].append(cursor.fetchone())

        if trainer['pokemon_3'] and trainer['pokemon_3'] != "None":
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_3']}'")
            self.user_pokemon_list[ctx.guild.id].append(cursor.fetchone())

        if trainer['pokemon_4'] and trainer['pokemon_4'] != "None":
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_4']}'")
            self.user_pokemon_list[ctx.guild.id].append(cursor.fetchone())

        if trainer['pokemon_5'] and trainer['pokemon_5'] != "None":
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_5']}'")
            self.user_pokemon_list[ctx.guild.id].append(cursor.fetchone())

        if trainer['pokemon_6'] and trainer['pokemon_6'] != "None":
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{trainer['pokemon_6']}'")
            self.user_pokemon_list[ctx.guild.id].append(cursor.fetchone())

        # Trainer battle
        if "trainer" in args[0].lower():
            await self.pokemon_battle(ctx, cursor, trainer, "trainer")

        # Gym battle
        elif "gym" in args[0].lower():
            await self.pokemon_battle(ctx, cursor, trainer, "gym")

        # Elite 4
        elif "elite" in args[0].lower():
            await self.pokemon_battle(ctx, cursor, trainer, "elite")

        # Wild pokemon battle
        else:
            await self.pokemon_battle(ctx, cursor, trainer, "wild")

    async def pokemon_battle(self, ctx, cursor, trainer, battle_type):
        # Wild pokemon battle
        if battle_type == "wild":
            # Generate random pokemon
            encounter_chance = random.randint(1, 100)
            if encounter_chance == 100:
                i = 0
                caught = True
                while caught:
                    self.pokemon_name = random.choice(self.legendary_pokemon)
                    # Check to see if the Legendary pokemon has been caught
                    cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}' AND name = '{self.pokemon_name}'")
                    if cursor.fetchone():
                        self.legendary_pokemon.remove(self.pokemon_name)
                        i += 1
                        if i == len(self.legendary_pokemon):
                            await ctx.send("**A rare pokemon appeared!**")
                            self.pokemon_name = random.choice(self.rare_pokemon)
                            caught = False
                    else:
                        await ctx.send("**A LEGENDARY POKEMON APPEARED!**")
                        caught = False
            elif encounter_chance >= 90 and encounter_chance < 100:
                await ctx.send("**A rare pokemon appeared!**")
                self.pokemon_name = random.choice(self.rare_pokemon)
            else:
                self.pokemon_name = random.choice(self.common_pokemon)

            # Set pokemon moves
            await self.set_pokemon_moves(ctx, True)

            # Set wild pokemon level and stats
            await self.set_pokemon_details(ctx, cursor, battle_type)
        
        # Trainer pokemon battle
        if battle_type == "trainer":
            # Choose trainer's active pokemon
            random_pokemon = random.randint(1, 100)
            if random_pokemon > 90:
                self.enemy_active_pokemon[ctx.guild.id]['name'] = random.choice(self.rare_pokemon)
            else:
                self.enemy_active_pokemon[ctx.guild.id]['name'] = random.choice(self.common_pokemon)

            # Set trainer's active pokemon details
            self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
            await self.set_pokemon_moves(ctx, True)
            await self.set_pokemon_details(ctx, cursor, battle_type)

            # Set how many pokemon trainer has
            trainer_pokemon_count = random.randint(0, 5)
            pokemon_counter = 0

            while pokemon_counter < trainer_pokemon_count:
                # Choose a pokemon for the trainer
                random_pokemon = random.randint(1, 100)
                if random_pokemon > 90:
                    self.enemy_pokemon[ctx.guild.id]['name'] = random.choice(self.rare_pokemon)
                    self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                    await self.set_pokemon_moves(ctx, False)
                    await self.set_pokemon_details(ctx, cursor, battle_type)
                    self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                else:
                    self.enemy_pokemon[ctx.guild.id]['name'] = random.choice(self.common_pokemon)
                    self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                    await self.set_pokemon_moves(ctx, False)
                    await self.set_pokemon_details(ctx, cursor, battle_type)
                    self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())
                
                pokemon_counter += 1
        
        # Gym battle
        if battle_type == "gym":
            # Get # of badges the trainer has
            cursor.execute(f"SELECT badges FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            badges = cursor.fetchone()['badges']

            # Trainer challenges Brock
            if badges == 0:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Brock!**")
                # Add geodude as Brock's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'geodude'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 12
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 12), (pokemon_stats['hp'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 12), (pokemon_stats['attack'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 12), (pokemon_stats['special_attack'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 12), (pokemon_stats['defense'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 12), (pokemon_stats['special_defense'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 12), (pokemon_stats['speed'] + (12 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'defense curl'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = None
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = None

                # Add onix as Brock's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'onix'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 14
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 14), (pokemon_stats['hp'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 14), (pokemon_stats['attack'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 14), (pokemon_stats['special_attack'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 14), (pokemon_stats['defense'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 14), (pokemon_stats['special_defense'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 14), (pokemon_stats['speed'] + (14 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'screech'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'bide'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = None
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

            # Trainer challenges Misty
            elif badges == 1:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Misty!**")
                # Add staryu as Misty's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'staryu'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 18
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 18), (pokemon_stats['hp'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 18), (pokemon_stats['attack'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 18), (pokemon_stats['special_attack'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 18), (pokemon_stats['defense'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 18), (pokemon_stats['special_defense'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 18), (pokemon_stats['speed'] + (18 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'water gun'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'harden'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = None

                # Add starmie as Misty's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'starmie'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 21
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 21), (pokemon_stats['hp'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 21), (pokemon_stats['attack'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 21), (pokemon_stats['special_attack'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 21), (pokemon_stats['defense'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 21), (pokemon_stats['special_defense'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 21), (pokemon_stats['speed'] + (21 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'bubble beam'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'harden'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'water gun'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

            # Trainer challenges Lt. Surge
            elif badges == 2:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Lt. Surge!**")
                # Add voltorb as Lt. Surge's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'voltorb'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 21
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 21), (pokemon_stats['hp'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 21), (pokemon_stats['attack'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 21), (pokemon_stats['special_attack'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 21), (pokemon_stats['defense'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 21), (pokemon_stats['special_defense'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 21), (pokemon_stats['speed'] + (21 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'screech'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'sonic boom'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = None
                
                # Add pikachu as Lt. Surge's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'pikachu'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 18
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 18), (pokemon_stats['hp'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 18), (pokemon_stats['attack'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 18), (pokemon_stats['special_attack'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 18), (pokemon_stats['defense'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 18), (pokemon_stats['special_defense'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 18), (pokemon_stats['speed'] + (18 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'thunder shock'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'quick attack'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'thunder wave'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'growl'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add raichu as Lt. Surge's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'raichu'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 24
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 24), (pokemon_stats['hp'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 24), (pokemon_stats['attack'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 24), (pokemon_stats['special_attack'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 24), (pokemon_stats['defense'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 24), (pokemon_stats['special_defense'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 24), (pokemon_stats['speed'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'thunder shock'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'growl'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'thunderbolt'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = None
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

            # Trainer challenges Erika
            elif badges == 3:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Erika!**")
                # Add victreebel as Erika's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'victreebel'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 29
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 29), (pokemon_stats['hp'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 29), (pokemon_stats['attack'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 29), (pokemon_stats['special_attack'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 29), (pokemon_stats['defense'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 29), (pokemon_stats['special_defense'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 29), (pokemon_stats['speed'] + (29 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'razor leaf'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'poison powder'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'sleep powder'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = 'wrap'

                # Add Tangela as Erika's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'tangela'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 24
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 24), (pokemon_stats['hp'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 24), (pokemon_stats['attack'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 24), (pokemon_stats['special_attack'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 24), (pokemon_stats['defense'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 24), (pokemon_stats['special_defense'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 24), (pokemon_stats['speed'] + (24 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'constrict'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'bind'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = None
                self.enemy_pokemon[ctx.guild.id]['move_4'] = None
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add Vileplume as Erika's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'vileplume'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 29
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 29), (pokemon_stats['hp'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 29), (pokemon_stats['attack'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 29), (pokemon_stats['special_attack'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 29), (pokemon_stats['defense'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 29), (pokemon_stats['special_defense'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 29), (pokemon_stats['speed'] + (29 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'petal dance'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'poison powder'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'mega drain'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'sleep powder'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

            # Trainer challenges Koga
            elif badges == 4:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Koga!**")
                # Add koffing as Koga's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'koffing'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 37
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 37), (pokemon_stats['hp'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 37), (pokemon_stats['attack'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 37), (pokemon_stats['special_attack'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 37), (pokemon_stats['defense'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 37), (pokemon_stats['special_defense'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 37), (pokemon_stats['speed'] + (37 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'smog'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'sludge'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = 'smokescreen'

                # Add koffing as Koga's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'koffing'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 37
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 37), (pokemon_stats['hp'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 37), (pokemon_stats['attack'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 37), (pokemon_stats['special_attack'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 37), (pokemon_stats['defense'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 37), (pokemon_stats['special_defense'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 37), (pokemon_stats['speed'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'tackle'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'smog'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'sludge'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'smokescreen'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add muk as Koga's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'muk'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 39
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 39), (pokemon_stats['hp'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 39), (pokemon_stats['attack'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 39), (pokemon_stats['special_attack'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 39), (pokemon_stats['defense'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 39), (pokemon_stats['special_defense'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 39), (pokemon_stats['speed'] + (39 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'sludge'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'poison gas'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'minimize'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = None

                # Add weezing as Koga's fourth pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'weezing'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 43
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 43), (pokemon_stats['hp'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 43), (pokemon_stats['attack'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 43), (pokemon_stats['special_attack'] + (43* 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 43), (pokemon_stats['defense'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 43), (pokemon_stats['special_defense'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 43), (pokemon_stats['speed'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'smog'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'sludge'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'toxic'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'selfdestruct'
            
            # Trainer challenges Sabrina
            elif badges == 5:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Sabrina!**")
                # Add abra as Sabrina's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'kadabra'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 38
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 38), (pokemon_stats['hp'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 38), (pokemon_stats['attack'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 38), (pokemon_stats['special_attack'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 38), (pokemon_stats['defense'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 38), (pokemon_stats['special_defense'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 38), (pokemon_stats['speed'] + (38 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'psybeam'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'recover'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'psychic'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = None

                # Add Mr. Mime as Sabrina's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'mr. mime'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 38
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 38), (pokemon_stats['hp'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 38), (pokemon_stats['attack'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 38), (pokemon_stats['special_attack'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 38), (pokemon_stats['defense'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 38), (pokemon_stats['special_defense'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 38), (pokemon_stats['speed'] + (38 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'confusion'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'light screen'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'double slap'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'barrier'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add Venomoth as Sabrina's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'venomoth'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 37
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 37), (pokemon_stats['hp'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 37), (pokemon_stats['attack'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 37), (pokemon_stats['special_attack'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 37), (pokemon_stats['defense'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 37), (pokemon_stats['special_defense'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 37), (pokemon_stats['speed'] + (37 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'psybeam'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'stun spore'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'leech life'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'poison powder'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add Alakazam as Sabrina's fourth pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'alakazam'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 43
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 43), (pokemon_stats['hp'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 43), (pokemon_stats['attack'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 43), (pokemon_stats['special_attack'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 43), (pokemon_stats['defense'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 43), (pokemon_stats['special_defense'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 43), (pokemon_stats['speed'] + (43 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'psybeam'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'recover'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'psywave'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'reflect'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

            # Trainer challenges Blaine
            elif badges == 6:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Blaine!**")
                # Add growlithe as Blaine's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'growlithe'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 42
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 42), (pokemon_stats['hp'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 42), (pokemon_stats['attack'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 42), (pokemon_stats['special_attack'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 42), (pokemon_stats['defense'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 42), (pokemon_stats['special_defense'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 42), (pokemon_stats['speed'] + (42 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'ember'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'leer'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'take down'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = 'agility'

                # Add ponyta as Blaine's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'ponyta'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 40
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 40), (pokemon_stats['hp'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 40), (pokemon_stats['attack'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 40), (pokemon_stats['special_attack'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 40), (pokemon_stats['defense'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 40), (pokemon_stats['special_defense'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 40), (pokemon_stats['speed'] + (40 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'tail whip'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'stomp'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'growl'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'fire spin'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add rapidash as Blaine's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'rapidash'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 42
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 42), (pokemon_stats['hp'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 42), (pokemon_stats['attack'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 42), (pokemon_stats['special_attack'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 42), (pokemon_stats['defense'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 42), (pokemon_stats['special_defense'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 42), (pokemon_stats['speed'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'stomp'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'fire spin'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'tail whip'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'growl'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add Arcanine as Blaine's fourth pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'arcanine'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 47
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 47), (pokemon_stats['hp'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 47), (pokemon_stats['attack'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 47), (pokemon_stats['special_attack'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 47), (pokemon_stats['defense'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 47), (pokemon_stats['special_defense'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 47), (pokemon_stats['speed'] + (47 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'fire blast'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'ember'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'take down'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'roar'

            # Trainer challenges Giovanni
            elif badges == 7:
                await ctx.send(f"**{ctx.author.name} has challenged gym leader Giovanni!**")
                # Add rhydon as Giovanni's active pokemon
                self.enemy_active_pokemon[ctx.guild.id]['name'] = 'rhyhorn'
                self.pokemon_name = self.enemy_active_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_active_pokemon[ctx.guild.id]['level'] = 45
                self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 45), (pokemon_stats['hp'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
                self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 45), (pokemon_stats['attack'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 45), (pokemon_stats['special_attack'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 45), (pokemon_stats['defense'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 45), (pokemon_stats['special_defense'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 45), (pokemon_stats['speed'] + (45 * 3)))
                self.enemy_active_pokemon[ctx.guild.id]['move_1'] = 'stomp'
                self.enemy_active_pokemon[ctx.guild.id]['move_2'] = 'tail whip'
                self.enemy_active_pokemon[ctx.guild.id]['move_3'] = 'fury attack'
                self.enemy_active_pokemon[ctx.guild.id]['move_4'] = 'horn drill'

                # Add Dugtrio as Giovanni's second pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'dugtrio'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 42
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 42), (pokemon_stats['hp'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 42), (pokemon_stats['attack'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 42), (pokemon_stats['special_attack'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 42), (pokemon_stats['defense'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 42), (pokemon_stats['special_defense'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 42), (pokemon_stats['speed'] + (42 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'growl'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'dig'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'sand attack'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'slash'
                self.enemy_pokemon_list[ctx.guild.id].append(self.enemy_pokemon[ctx.guild.id].copy())

                # Add Nidoqueen as Giovanni's third pokemon
                self.enemy_pokemon[ctx.guild.id]['name'] = 'nidoqueen'
                self.pokemon_name = self.enemy_pokemon[ctx.guild.id]['name']
                cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
                pokemon_stats = cursor.fetchone()
                self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
                self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
                self.enemy_pokemon[ctx.guild.id]['level'] = 44
                self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + 44), (pokemon_stats['hp'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
                self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + 44), (pokemon_stats['attack'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + 44), (pokemon_stats['special_attack'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + 44), (pokemon_stats['defense'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + 44), (pokemon_stats['special_defense'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + 44), (pokemon_stats['speed'] + (44 * 3)))
                self.enemy_pokemon[ctx.guild.id]['move_1'] = 'poison sting'
                self.enemy_pokemon[ctx.guild.id]['move_2'] = 'scratch'
                self.enemy_pokemon[ctx.guild.id]['move_3'] = 'body slam'
                self.enemy_pokemon[ctx.guild.id]['move_4'] = 'tail whip'

    async def set_pokemon_moves(self, ctx, active):
        # TODO: Add all other pokemon that are not listed here
        # Set pokemon evolutions based on user's active pokemon level
        if self.pokemon_name == "bulbasaur":
            move_1 = 'tackle'
            move_2 = 'growl'
            move_3 = 'vine whip'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "ivysaur"
                move_4 = 'razor leaf'
            if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                self.pokemon_name = "venusaur"
                move_3 = 'solar beam'
                move_4 = 'razor leaf'
        elif self.pokemon_name == "charmander":
            move_1 = 'scratch'
            move_2 = 'growl'
            move_3 = 'ember'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "charmeleon"
                move_4 = 'slash'
            if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                self.pokemon_name = "charizard"
                move_1 = 'slash'
                move_2 = 'leer'
                move_3 = 'flamethrower'
                move_4 = 'fire spin'
        elif self.pokemon_name == "squirtle":
            move_1 = 'tackle'
            move_2 = 'tail whip'
            move_3 = 'bubble'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "wartortle"
                move_4 = 'water gun'
            if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                self.pokemon_name = "blastoise"
                move_1 = 'bite'
                move_2 = 'skull bash'
                move_3 = 'water gun'
                move_4 = 'hydro pump'
        elif self.pokemon_name == "caterpie":
            move_1 = 'tackle'
            move_2 = 'string shot'
            move_3 = None
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 7:
                self.pokemon_name = "metapod"
                move_3 = 'harden'
            if self.active_pokemon[ctx.guild.id]['level'] >= 10:
                self.pokemon_name = "butterfree"
                move_2 = 'confusion'
                move_3 = 'supersonic'
                move_4 = 'sleep powder'
        elif self.pokemon_name == "weedle":
            move_1 = 'poison sting'
            move_2 = 'string shot'
            move_3 = None
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 7:
                self.pokemon_name = "kakuna"
                move_3 = 'harden'
            if self.active_pokemon[ctx.guild.id]['level'] >= 10:
                self.pokemon_name = "beedrill"
                move_1 = 'fury attack'
                move_2 = 'twineedle'
                move_3 = 'focus energy'
                move_4 = 'poison sting'
        elif self.pokemon_name == "pidgey":
            move_1 = 'gust'
            move_2 = 'sand attack'
            move_3 = 'quick attack'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 18:
                self.pokemon_name = "pidgeotto"
                move_4 = 'wing attack'
            if self.active_pokemon[ctx.guild.id]['level'] >= 36:
                self.pokemon_name = "pidgeot"
                move_4 = 'wing attack'
        elif self.pokemon_name == "rattata":
            move_1 = 'tackle'
            move_2 = 'tail whip'
            move_3 = 'quick attack'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                self.pokemon_name = "raticate"
                move_4 = 'hyper fang'
        elif self.pokemon_name == "spearow":
            move_1 = 'growl'
            move_2 = 'peck'
            move_3 = 'leer'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                self.pokemon_name = "fearow"
                move_4 = 'fury attack'
        elif self.pokemon_name == "ekans":
            move_1 = 'leer'
            move_2 = 'wrap'
            move_3 = 'poison sting'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                self.pokemon_name = "arbok"
                move_4 = 'bite'
        elif self.pokemon_name == "sandshrew":
            move_1 = 'scratch'
            move_2 = 'sand attack'
            move_3 = 'slash'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                self.pokemon_name = "sandslash"
                move_4 = 'swift'
        elif self.pokemon_name == "nidoran_female":
            move_1 = 'scratch'
            move_2 = 'growl'
            move_3 = 'poison sting'
            move_4 = 'double kick'
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "nidorina"
                move_2 = 'bite'
        elif self.pokemon_name == "nidoran_male":
            move_1 = 'peck'
            move_2 = 'leer'
            move_3 = 'horn attack'
            move_4 = 'poison sting'
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "nidorino"
                move_2 = 'fury attack'
        elif self.pokemon_name == "zubat":
            move_1 = 'leech life'
            move_2 = 'supersonic'
            move_3 = 'bite'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                self.pokemon_name = "golbat"
                move_4 = 'wing attack'
        elif self.pokemon_name == "oddish":
            move_1 = 'absorb'
            move_2 = 'poison powder'
            move_3 = 'stun spore'
            move_4 = 'sleep powder'
            if self.active_pokemon[ctx.guild.id]['level'] >= 21:
                self.pokemon_name = "gloom"
                move_1 = 'acid'
        elif self.pokemon_name == "paras":
            move_1 = 'scratch'
            move_2 = 'stun spore'
            move_3 = 'leech life'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 24:
                self.pokemon_name = "parasect"
                move_4 = 'spore'
        elif self.pokemon_name == "venonat":
            move_1 = 'tackle'
            move_2 = 'disable'
            move_3 = 'confusion'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 31:
                self.pokemon_name = "venomoth"
                move_4 = 'psybeam'
        elif self.pokemon_name == "diglett":
            move_1 = 'scratch'
            move_2 = 'growl'
            move_3 = 'sand attack'
            move_4 = 'magnitude'
            if self.active_pokemon[ctx.guild.id]['level'] >= 26:
                self.pokemon_name = "dugtrio"
                move_2 = 'slash'
        elif self.pokemon_name == "meowth":
            move_1 = 'scratch'
            move_2 = 'growl'
            move_3 = 'bite'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                self.pokemon_name = "persian"
                move_4 = 'slash'
        elif self.pokemon_name == "psyduck":
            move_1 = 'scratch'
            move_2 = 'tail whip'
            move_3 = 'disable'
            move_4 = 'water gun'
            if self.active_pokemon[ctx.guild.id]['level'] >= 33:
                self.pokemon_name = "golduck"
                move_3 = 'confusion'
        elif self.pokemon_name == "mankey":
            move_1 = 'scratch'
            move_2 = 'leer'
            move_3 = 'karate chop'
            move_4 = 'fury swipes'
            if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                self.pokemon_name = "primeape"
                move_4 = 'thrash'
        elif self.pokemon_name == "poliwag":
            move_1 = 'bubble'
            move_2 = 'hypnosis'
            move_3 = 'water gun'
            move_4 = 'double slap'
            if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                self.pokemon_name = "poliwhirl"
                move_4 = 'body slam'
        elif self.pokemon_name == "abra":
            move_1 = 'teleport'
            move_2 = 'confusion'
            move_3 = 'kinesis'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                self.pokemon_name = "kadabra"
                move_4 = 'psybeam'
        elif self.pokemon_name == "machop":
            move_1 = 'karate chop'
            move_2 = 'low kick'
            move_3 = 'leer'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                self.pokemon_name = "machoke"
                move_4 = 'submission'
        elif self.pokemon_name == "bellsprout":
            move_1 = 'vine whip'
            move_2 = 'growth'
            move_3 = 'wrap'
            move_4 = 'poison powder'
            if self.active_pokemon[ctx.guild.id]['level'] >= 21:
                self.pokemon_name = "weepinbell"
                move_4 = 'razor leaf'
        elif self.pokemon_name == "tentacool":
            move_1 = 'poison sting'
            move_2 = 'supersonic'
            move_3 = 'constrict'
            move_4 = 'water gun'
            if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                self.pokemon_name = "tentacruel"
                move_4 = 'bubble beam'
        elif self.pokemon_name == "geodude":
            move_1 = 'tackle'
            move_2 = 'defense curl'
            move_3 = 'rock throw'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                self.pokemon_name = "graveler"
                move_4 = 'self-destruct'
        elif self.pokemon_name == "ponyta":
            move_1 = 'tackle'
            move_2 = 'growl'
            move_3 = 'ember'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                self.pokemon_name = "rapidash"
                move_4 = 'fire spin'
        elif self.pokemon_name == "slowpoke":
            move_1 = 'tackle'
            move_2 = 'growl'
            move_3 = 'water gun'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 37:
                self.pokemon_name = "slowbro"
                move_4 = 'confusion'
        elif self.pokemon_name == "magnemite":
            move_1 = 'tackle'
            move_2 = 'sonic boom'
            move_3 = 'thunder shock'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                self.pokemon_name = "magneton"
                move_4 = 'thunderbolt'
        elif self.pokemon_name == 'doduo':
            move_1 = 'peck'
            move_2 = 'growl'
            move_3 = 'fury attack'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 31:
                self.pokemon_name = "dodrio"
                move_4 = 'drill peck'
        elif self.pokemon_name == 'seel':
            move_1 = 'headbutt'
            move_2 = 'growl'
            move_3 = 'water gun'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 34:
                self.pokemon_name = "dewgong"
                move_4 = 'aurora beam'
        elif self.pokemon_name == 'grimer':
            move_1 = 'pound'
            move_2 = 'poison gas'
            move_3 = 'disable'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 38:
                self.pokemon_name = "muk"
                move_4 = 'sludge'
        elif self.pokemon_name == 'gastly':
            move_1 = 'lick'
            move_2 = 'confuse ray'
            move_3 = 'night shade'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                self.pokemon_name = "haunter"
                move_4 = 'hypnosis'
        elif self.pokemon_name == 'drowzee':
            move_1 = 'pound'
            move_2 = 'hypnosis'
            move_3 = 'disable'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 26:
                self.pokemon_name = "hypno"
                move_4 = 'confusion'
        elif self.pokemon_name == 'krabby':
            move_1 = 'bubble'
            move_2 = 'leer'
            move_3 = 'vicegrip'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                self.pokemon_name = "kingler"
                move_4 = 'stomp'
        elif self.pokemon_name == 'voltorb':
            move_1 = 'tackle'
            move_2 = 'screech'
            move_3 = 'sonic boom'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                self.pokemon_name = "electrode"
                move_4 = 'thunder shock'
        elif self.pokemon_name == 'exeggcute':
            move_1 = 'barrage'
            move_2 = 'hypnosis'
            move_3 = 'stun spore'
            move_4 = 'confusion'
            if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                self.pokemon_name = "exeggutor"
                move_4 = 'solar beam'
        elif self.pokemon_name == 'cubone':
            move_1 = 'growl'
            move_2 = 'bone club'
            move_3 = 'headbutt'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                self.pokemon_name = "marowak"
                move_4 = 'bonemerang'
        elif self.pokemon_name == 'koffing':
            move_1 = 'tackle'
            move_2 = 'smog'
            move_3 = 'smokescreen'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 35:
                self.pokemon_name = "weezing"
                move_4 = 'sludge'
        elif self.pokemon_name == 'rhyhorn':
            move_1 = 'horn attack'
            move_2 = 'tail whip'
            move_3 = 'stomp'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 42:
                self.pokemon_name = "rhydon"
                move_4 = 'fury attack'
        elif self.pokemon_name == 'horsea':
            move_1 = 'bubble'
            move_2 = 'smokescreen'
            move_3 = 'leer'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                self.pokemon_name = "seadra"
                move_4 = 'water gun'
        elif self.pokemon_name == 'goldeen':
            move_1 = 'peck'
            move_2 = 'tail whip'
            move_3 = 'supersonic'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 33:
                self.pokemon_name = "seaking"
                move_4 = 'waterfall'
        elif self.pokemon_name == 'magikarp':
            move_1 = 'splash'
            move_2 = 'tackle'
            move_3 = None
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                self.pokemon_name = "gyarados"
                move_1 = 'bite'
                move_2 = 'dragon rage'
                move_3 = 'leer'
                move_4 = 'hydro pump'
        elif self.pokemon_name == 'omanyte':
            move_1 = 'water gun'
            move_2 = 'withdraw'
            move_3 = 'horn attack'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                self.pokemon_name = "omastar"
                move_4 = 'bite'
        elif self.pokemon_name == 'kabuto':
            move_1 = 'scratch'
            move_2 = 'harden'
            move_3 = 'absorb'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                self.pokemon_name = "kabutops"
                move_4 = 'slash'
        elif self.pokemon_name == 'dratini':
            move_1 = 'wrap'
            move_2 = 'leer'
            move_3 = 'thunder wave'
            move_4 = None
            if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                self.pokemon_name = "dragonair"
                move_4 = 'dragon rage'
            if self.active_pokemon[ctx.guild.id]['level'] >= 55:
                self.pokemon_name = "dragonite"
                move_1 = 'wing attack'
                move_2 = 'slam'
                move_3 = 'dragon rage'
                move_4 = 'hyper beam'

        if active:
            self.enemy_active_pokemon[ctx.guild.id]['move_1'] = move_1
            self.enemy_active_pokemon[ctx.guild.id]['move_2'] = move_2
            self.enemy_active_pokemon[ctx.guild.id]['move_3'] = move_3
            self.enemy_active_pokemon[ctx.guild.id]['move_4'] = move_4
        else:
            self.enemy_pokemon[ctx.guild.id]['move_1'] = move_1
            self.enemy_pokemon[ctx.guild.id]['move_2'] = move_2
            self.enemy_pokemon[ctx.guild.id]['move_3'] = move_3
            self.enemy_pokemon[ctx.guild.id]['move_4'] = move_4


    async def set_pokemon_details(self, ctx, cursor, battle_type):
        # Set wild pokemon level
        if self.active_pokemon[ctx.guild.id]['level']  < 8:
            level = random.randint(3, 6)
        else:
            level = random.randint(self.active_pokemon[ctx.guild.id]['level'] - 5, self.active_pokemon[ctx.guild.id]['level'])
        # Set wild pokemon stats
        cursor.execute(f"SELECT * FROM Stats WHERE name = '{self.pokemon_name}'")
        pokemon_stats = cursor.fetchone()

        if battle_type == 'wild':
            self.enemy_active_pokemon[ctx.guild.id]['name'] = self.pokemon_name
            self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
            self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
            self.enemy_active_pokemon[ctx.guild.id]['level'] = level
            self.enemy_active_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + level), (pokemon_stats['hp'] + (level * 3)))
            self.enemy_active_pokemon[ctx.guild.id]['current_hp'] = self.enemy_active_pokemon[ctx.guild.id]['max_hp']
            self.enemy_active_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + level), (pokemon_stats['attack'] + (level * 3)))
            self.enemy_active_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + level), (pokemon_stats['special_attack'] + (level * 3)))
            self.enemy_active_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + level), (pokemon_stats['defense'] + (level * 3)))
            self.enemy_active_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + level), (pokemon_stats['special_defense'] + (level * 3)))
            self.enemy_active_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + level), (pokemon_stats['speed'] + (level * 3)))
        else:
            self.enemy_pokemon[ctx.guild.id]['name'] = self.pokemon_name
            self.enemy_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
            self.enemy_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
            self.enemy_pokemon[ctx.guild.id]['level'] = level
            self.enemy_pokemon[ctx.guild.id]['max_hp'] = random.randint((pokemon_stats['hp'] + level), (pokemon_stats['hp'] + (level * 3)))
            self.enemy_pokemon[ctx.guild.id]['current_hp'] = self.enemy_pokemon[ctx.guild.id]['max_hp']
            self.enemy_pokemon[ctx.guild.id]['attack'] = random.randint((pokemon_stats['attack'] + level), (pokemon_stats['attack'] + (level * 3)))
            self.enemy_pokemon[ctx.guild.id]['special_attack'] = random.randint((pokemon_stats['special_attack'] + level), (pokemon_stats['special_attack'] + (level * 3)))
            self.enemy_pokemon[ctx.guild.id]['defense'] = random.randint((pokemon_stats['defense'] + level), (pokemon_stats['defense'] + (level * 3)))
            self.enemy_pokemon[ctx.guild.id]['special_defense'] = random.randint((pokemon_stats['special_defense'] + level), (pokemon_stats['special_defense'] + (level * 3)))
            self.enemy_pokemon[ctx.guild.id]['speed'] = random.randint((pokemon_stats['speed'] + level), (pokemon_stats['speed'] + (level * 3)))

async def setup(bot):
    await bot.add_cog(Battle(bot))
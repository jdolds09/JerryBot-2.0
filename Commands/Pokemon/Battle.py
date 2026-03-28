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
                             'hitmonlee', 'hitmonchan', 'lickitung', 'koffing', 'rhyhorn', 'chansey', 'tangela', 'kangaskhan', 'horsea', 
                             'goldeen', 'staryu', 'mr. mime', 'scyther', 'jynx', 'electabuzz', 'magmar', 'pinsir', 'tauros', 'magikarp', 
                             'eevee', 'porygon', 'omanyte', 'kabuto']
        self.rare_pokemon = ['lapras', 'snorlax', 'aerodactyl', 'dratini']
        self.legendary_pokemon = ['articuno', 'zapdos', 'moltres', 'mewtwo', 'mew']

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
                await ctx.send("**A LEGENDARY POKEMON APPEARED!**")
                wild_pokemon = random.choice(self.legendary_pokemon)
            elif encounter_chance >= 95 and encounter_chance < 100:
                await ctx.send("**A rare pokemon appeared!**")
                wild_pokemon = random.choice(self.rare_pokemon)
            else:
                wild_pokemon = random.choice(self.common_pokemon)

            # Set pokemon evolutions based on user's active pokemon level
            if wild_pokemon == "bulbasaur":
                move_1 = 'tackle'
                move_2 = 'growl'
                move_3 = 'vine whip'
                move_4 = None
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "ivysaur"
                    move_4 = 'razor leaf'
                if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                    wild_pokemon = "venusaur"
                    move_3 = 'solar beam'
                    move_4 = 'razor leaf'
            elif wild_pokemon == "charmander":
                move_1 = 'scratch'
                move_2 = 'growl'
                move_3 = 'ember'
                move_4 = None
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "charmeleon"
                    move_4 = 'slash'
                if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                    wild_pokemon = "charizard"
                    move_1 = 'slash'
                    move_2 = 'leer'
                    move_3 = 'flamethrower'
                    move_4 = 'fire spin'
            elif wild_pokemon == "squirtle":
                move_1 = 'tackle'
                move_2 = 'tail whip'
                move_3 = 'bubble'
                move_4 = None
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "wartortle"
                    move_4 = 'water gun'
                if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                    wild_pokemon = "blastoise"
                    move_1 = 'bite'
                    move_2 = 'skull bash'
                    move_3 = 'water gun'
                    move_4 = 'hydro pump'
            elif wild_pokemon == "caterpie":
                move_1 = 'tackle'
                move_2 = 'string shot'
                move_3 = None
                move_4 = None
                if self.active_pokemon[ctx.guild.id]['level'] >= 7:
                    wild_pokemon = "metapod"
                    move_3 = 'harden'
                if self.active_pokemon[ctx.guild.id]['level'] >= 10:
                    wild_pokemon = "butterfree"
                    move_2 = 'confusion'
                    move_3 = 'supersonic'
                    move_4 = 'sleep powder'
            elif wild_pokemon == "weedle":
                if self.active_pokemon[ctx.guild.id]['level'] >= 7:
                    wild_pokemon = "kakuna"
                if self.active_pokemon[ctx.guild.id]['level'] >= 10:
                    wild_pokemon = "beedrill"
            elif wild_pokemon == "pidgey":
                if self.active_pokemon[ctx.guild.id]['level'] >= 18:
                    wild_pokemon = "pidgeotto"
                if self.active_pokemon[ctx.guild.id]['level'] >= 36:
                    wild_pokemon = "pidgeot"
            elif wild_pokemon == "rattata":
                if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                    wild_pokemon = "raticate"
            elif wild_pokemon == "spearow":
                if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                    wild_pokemon = "fearow"
            elif wild_pokemon == "ekans":
                if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                    wild_pokemon = "arbok"
            elif wild_pokemon == "sandshrew":
                if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                    wild_pokemon = "sandslash"
            elif wild_pokemon == "nidoran_female":
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "nidorina"
            elif wild_pokemon == "nidoran_male":
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "nidorino"
            elif wild_pokemon == "zubat":
                if self.active_pokemon[ctx.guild.id]['level'] >= 22:
                    wild_pokemon = "golbat"
            elif wild_pokemon == "oddish":
                if self.active_pokemon[ctx.guild.id]['level'] >= 21:
                    wild_pokemon = "gloom"
            elif wild_pokemon == "paras":
                if self.active_pokemon[ctx.guild.id]['level'] >= 24:
                    wild_pokemon = "parasect"
            elif wild_pokemon == "venonat":
                if self.active_pokemon[ctx.guild.id]['level'] >= 31:
                    wild_pokemon = "venomoth"
            elif wild_pokemon == "diglett":
                if self.active_pokemon[ctx.guild.id]['level'] >= 26:
                    wild_pokemon = "dugtrio"
            elif wild_pokemon == "meowth":
                if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                    wild_pokemon = "persian"
            elif wild_pokemon == "psyduck":
                if self.active_pokemon[ctx.guild.id]['level'] >= 33:
                    wild_pokemon = "golduck"
            elif wild_pokemon == "mankey":
                if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                    wild_pokemon = "primeape"
            elif wild_pokemon == "poliwag":
                if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                    wild_pokemon = "poliwhirl"
            elif wild_pokemon == "abra":
                if self.active_pokemon[ctx.guild.id]['level'] >= 16:
                    wild_pokemon = "kadabra"
            elif wild_pokemon == "machop":
                if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                    wild_pokemon = "machoke"
            elif wild_pokemon == "bellsprout":
                if self.active_pokemon[ctx.guild.id]['level'] >= 21:
                    wild_pokemon = "weepinbell"
            elif wild_pokemon == "tentacool":
                if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                    wild_pokemon = "tentacruel"
            elif wild_pokemon == "geodude":
                if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                    wild_pokemon = "graveler"
            elif wild_pokemon == "ponyta":
                if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                    wild_pokemon = "rapidash"
            elif wild_pokemon == "slowpoke":
                if self.active_pokemon[ctx.guild.id]['level'] >= 37:
                    wild_pokemon = "slowbro"
            elif wild_pokemon == "magnemite":
                if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                    wild_pokemon = "magneton"
            elif wild_pokemon == 'doduo':
                if self.active_pokemon[ctx.guild.id]['level'] >= 31:
                    wild_pokemon = "dodrio"
            elif wild_pokemon == 'seel':
                if self.active_pokemon[ctx.guild.id]['level'] >= 34:
                    wild_pokemon = "dewgong"
            elif wild_pokemon == 'grimer':
                if self.active_pokemon[ctx.guild.id]['level'] >= 38:
                    wild_pokemon = "muk"
            elif wild_pokemon == 'gastly':
                if self.active_pokemon[ctx.guild.id]['level'] >= 25:
                    wild_pokemon = "haunter"
            elif wild_pokemon == 'drowzee':
                if self.active_pokemon[ctx.guild.id]['level'] >= 26:
                    wild_pokemon = "hypno"
            elif wild_pokemon == 'krabby':
                if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                    wild_pokemon = "kingler"
            elif wild_pokemon == 'voltorb':
                if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                    wild_pokemon = "electrode"
            elif wild_pokemon == 'exeggcute':
                if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                    wild_pokemon = "exeggutor"
            elif wild_pokemon == 'cubone':
                if self.active_pokemon[ctx.guild.id]['level'] >= 28:
                    wild_pokemon = "marowak"
            elif wild_pokemon == 'koffing':
                if self.active_pokemon[ctx.guild.id]['level'] >= 35:
                    wild_pokemon = "weezing"
            elif wild_pokemon == 'rhyhorn':
                if self.active_pokemon[ctx.guild.id]['level'] >= 42:
                    wild_pokemon = "rhydon"
            elif wild_pokemon == 'horsea':
                if self.active_pokemon[ctx.guild.id]['level'] >= 32:
                    wild_pokemon = "seadra"
            elif wild_pokemon == 'goldeen':
                if self.active_pokemon[ctx.guild.id]['level'] >= 33:
                    wild_pokemon = "seaking"
            elif wild_pokemon == 'magikarp':
                if self.active_pokemon[ctx.guild.id]['level'] >= 20:
                    wild_pokemon = "gyarados"
            elif wild_pokemon == 'omanyte':
                if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                    wild_pokemon = "omastar"
            elif wild_pokemon == 'kabuto':
                if self.active_pokemon[ctx.guild.id]['level'] >= 40:
                    wild_pokemon = "kabutops"
            elif wild_pokemon == 'dratini':
                if self.active_pokemon[ctx.guild.id]['level'] >= 30:
                    wild_pokemon = "dragonair"
                if self.active_pokemon[ctx.guild.id]['level'] >= 55:
                    wild_pokemon = "dragonite"

            # Set wild pokemon level
            if self.active_pokemon[ctx.guild.id]['level']  < 8:
                level = random.randint(3, 6)
            else:
                level = random.randint(self.active_pokemon[ctx.guild.id]['level'] - 5, self.active_pokemon[ctx.guild.id]['level'])
            # Set wild pokemon stats
            cursor.execute(f"SELECT * FROM Stats WHERE name = '{wild_pokemon}'")
            pokemon_stats = cursor.fetchone()
            self.enemy_active_pokemon[ctx.guild.id]['name'] = wild_pokemon
            self.enemy_active_pokemon[ctx.guild.id]['type_1'] = pokemon_stats['type_1']
            self.enemy_active_pokemon[ctx.guild.id]['type_2'] = pokemon_stats['type_2']
            self.enemy_active_pokemon[ctx.guild.id]['level'] = level
            

        
async def setup(bot):
    await bot.add_cog(Battle(bot))
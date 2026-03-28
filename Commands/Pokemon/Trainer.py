import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random
import asyncio

class Trainer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starting_pokemon = ['bulbasaur', 'charmander', 'squirtle', 'caterpie', 'weedle', 'pidgey', 'rattata', 'spearow', 'ekans', 
                                 'pikachu', 'sandshrew', 'nidoran♀', 'nidoran♂', 'clefairy', 'vulpix', 'jigglypuff', 'zubat', 'oddish', 
                                 'paras', 'venonat', 'diglett', 'meowth', 'psyduck', 'mankey', 'growlithe', 'poliwag', 'abra', 'machop', 
                                 'bellsprout', 'tentacool', 'geodude','ponyta', 'slowpoke', 'magnemite', 'farfetchd', 'doduo', 'seel', 
                                 'grimer', 'shellder', 'gastly', 'onix', 'drowzee', 'krabby', 'voltorb', 'exeggcute', 'cubone', 'hitmonlee', 
                                 'hitmonchan', 'lickitung', 'koffing', 'rhyhorn', 'chansey', 'tangela', 'horsea', 'goldeen', 
                                 'staryu', 'magikarp', 'eevee', 'porygon', 'omanyte', 'kabuto']

    # Trainer function
    @commands.command()
    async def trainer(self, ctx, *args):
        # Connect to database
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
        
        # Display trainer's pokemon
        if "pokemon" in args[0].lower():
            await self.trainer_pokemon(ctx, cursor)
        
        # Create a trainer
        elif "create" in args[0].lower():
            await self.create_trainer(ctx, cursor)

        # Delete a trainer
        elif "delete" in args[0].lower():
            await self.delete_trainer(ctx, cursor)

        # Display trainer info
        else:
            await self.trainer_info(ctx, cursor)

    # Display trainer info function  
    async def trainer_info(self, ctx, cursor):
        # Get trainer info from database
        try:
            cursor.execute(f"SELECT * FROM Trainers WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
            trainer = cursor.fetchone()
            if not trainer:
                return await ctx.send("You don't have a trainer dumbass. Use `!trainer create` to create one.")
        except Exception as e:
            print(e)
            return await ctx.send("Error retrieving trainer info from database.")
        
        # Display trainer info
        await ctx.send(f"**TRAINER {ctx.author.name}**")
        await ctx.send(f"${trainer['money']}")
        await ctx.send(f"**Badges:** {trainer['badges']}")
        await ctx.send("----------------------------------------------")
        await ctx.send("**ITEMS**")
        await ctx.send(f"**Pokeballs:** {trainer['pokeballs']}")
        await ctx.send(f"**Great Balls:** {trainer['greatballs']}")
        await ctx.send(f"**Ultra Balls:** {trainer['ultraballs']}")
        await ctx.send(f"**Potions:** {trainer['potions']}")
        await ctx.send(f"**Full Restores:** {trainer['full_restores']}")
        await ctx.send("----------------------------------------------")
        await ctx.send("**POKEMON**")

        # Trainer's first pokemon
        try:
            cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_1']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
            pokemon = cursor.fetchone()
        except Exception as e:
            print(e)
            return await ctx.send("Error retrieving pokemon info from database.")
        await ctx.send(f"**{trainer['pokemon_1']}** - Level {pokemon['level']}")

        # Trainer's second pokemon
        if trainer['pokemon_2']:
            try:
                cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_2']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                pokemon = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error retrieving pokemon info from database.")
            await ctx.send(f"**{trainer['pokemon_2']}** - Level {pokemon['level']}")

        # Trainer's third pokemon
        if trainer['pokemon_3']:
            try:
                cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_3']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                pokemon = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error retrieving pokemon info from database.")
            await ctx.send(f"**{trainer['pokemon_3']}** - Level {pokemon['level']}")

        # Trainer's fourth pokemon
        if trainer['pokemon_4']:
            try:
                cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_4']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                pokemon = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error retrieving pokemon info from database.")
            await ctx.send(f"**{trainer['pokemon_4']}** - Level {pokemon['level']}")

        # Trainer's fifth pokemon
        if trainer['pokemon_5']:
            try:
                cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_5']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                pokemon = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error retrieving pokemon info from database.")
            await ctx.send(f"**{trainer['pokemon_5']}** - Level {pokemon['level']}")

        # Trainer's sixth pokemon
        if trainer['pokemon_6']:
            try:
                cursor.execute(f"SELECT * FROM Pokemon WHERE name = '{trainer['pokemon_6']}' AND username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                pokemon = cursor.fetchone()
            except Exception as e:
                print(e)
                return await ctx.send("Error retrieving pokemon info from database.")
            await ctx.send(f"**{trainer['pokemon_6']}** - Level {pokemon['level']}")

    # Display trainer's pokemon function
    async def trainer_pokemon(self, ctx, cursor):
        # Get trainer's pokemon from database
        try:
            cursor.execute(f"SELECT * FROM Pokemon WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
            pokemans = cursor.fetchall()
            if not pokemans:
                return await ctx.send("You don't have any pokemon dumbass.")

        except Exception as e:
            print(e)
            return await ctx.send("Error retrieving trainer info from database.")

        # Pokemon counter
        i = 0

        # Display Pokemon
        await ctx.send(f"**{ctx.author.name}'s Pokemon**")
        await ctx.send("----------------------------------------------")
        for pokemon in pokemans:
            await ctx.send(f"**{pokemon['name']}** - Level {pokemon['level']}")
            i += 1

        await ctx.send(f"**Pokemon caught:** {i}/150")

    # Create a pokemon trainer function
    async def create_trainer(self, ctx, cursor):
        # See if user already has a trainer
        cursor.execute(f"SELECT * FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        trainer = cursor.fetchone()
        if trainer:
            return await ctx.send("You already have a trainer dumbass.")
        
        # Select a starting pokemon for user
        starter = random.choice(self.starting_pokemon)

        # Output trainer and starter
        await ctx.send(f"**{ctx.author.name}** has become a Pokémon Trainer!")
        await ctx.send(f"Your starting pokemon is...")
        async with ctx.typing():
            await asyncio.sleep(5)
        await ctx.send(f"**{starter.capitalize()}**!")

        if starter == "nidoran♀":
            starter = "nidoran_female"
        elif starter == "nidoran♂":
            starter = "nidoran_male"

        file_path = f"Images/{starter}.jpg"
        picture = discord.File(file_path)
        await ctx.send(file=picture)

        # Set starting moves
        if starter == 'bulbasaur':
            move_1 = 'growl'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'charmander':
            move_1 = 'growl'
            move_2 = 'scratch'
            move_3 = None
        elif starter == 'squirtle':
            move_1 = 'tackle'
            move_2 = 'tail whip'
            move_3 = None
        elif starter == 'caterpie':
            move_1 = 'tackle'
            move_2 = 'string shot'
            move_3 = None
        elif starter == 'weedle':
            move_1 = 'poison sting'
            move_2 = 'string shot'
            move_3 = None
        elif starter == 'pidgey':
            move_1 = 'gust'
            move_2 = 'sand-attack'
            move_3 = None
        elif starter == 'rattata':
            move_1 = 'tackle'
            move_2 = 'tail whip'
            move_3 = None
        elif starter == 'spearow':
            move_1 = 'peck'
            move_2 = 'growl'
            move_3 = None
        elif starter == 'ekans':
            move_1 = 'leer'
            move_2 = 'wrap'
            move_3 = None
        elif starter == 'pikachu':
            move_1 = 'thundershock'
            move_2 = 'growl'
            move_3 = None
        elif starter == 'sandshrew':
            move_1 = 'scratch'
            move_2 = None
            move_3 = None
        elif starter == 'nidoran_female':
            move_1 = 'growl'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'nidoran_male':
            move_1 = 'leer'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'clefairy':
            move_1 = 'growl'
            move_2 = 'pound'
            move_3 = None
        elif starter == 'vulpix':
            move_1 = 'ember'
            move_2 = 'tail whip'
            move_3 = None
        elif starter == 'jigglypuff':
            move_1 = 'sing'
            move_2 = None
            move_3 = None
        elif starter == 'zubat':
            move_1 = 'leech life'
            move_2 = None
            move_3 = None
        elif starter == 'oddish':
            move_1 = 'absorb'
            move_2 = None
            move_3 = None
        elif starter == 'paras':
            move_1 = 'scratch'
            move_2 = None
            move_3 = None
        elif starter == 'venonat':
            move_1 = 'tackle'
            move_2 = None
            move_3 = None
        elif starter == 'diglett':
            move_1 = 'scratch'
            move_2 = None
            move_3 = None
        elif starter == 'meowth':
            move_1 = 'growl'
            move_2 = 'scratch'
            move_3 = None
        elif starter == 'psyduck':
            move_1 = 'scratch'
            move_2 = None
            move_3 = None
        elif starter == 'mankey':
            move_1 = 'leer'
            move_2 = 'scratch'
            move_3 = None
        elif starter == 'growlithe':
            move_1 = 'bite'
            move_2 = 'roar'
            move_3 = None
        elif starter == 'poliwag':
            move_1 = 'bubble'
            move_2 = None
            move_3 = None
        elif starter == 'abra':
            move_1 = 'teleport'
            move_2 = None
            move_3 = None
        elif starter == 'machop':
            move_1 = 'karate chop'
            move_2 = None
            move_3 = None
        elif starter == 'bellsprout':
            move_1 = 'growth'
            move_2 = 'vine whip'
            move_3 = None
        elif starter == 'tentacool':
            move_1 = 'acid'
            move_2 = None
            move_3 = None
        elif starter == 'geodude':
            move_1 = 'tackle'
            move_2 = None
            move_3 = None
        elif starter == 'ponyta':
            move_1 = 'ember'
            move_2 = None
            move_3 = None
        elif starter == 'slowpoke':
            move_1 = 'confusion'
            move_2 = None
            move_3 = None
        elif starter == 'magnemite':
            move_1 = 'tackle'
            move_2 = None
            move_3 = None
        elif starter == 'farfetchd':
            move_1 = 'peck'
            move_2 = 'sand-attack'
            move_3 = None
        elif starter == 'doduo':
            move_1 = 'peck'
            move_2 = None
            move_3 = None
        elif starter == 'seel':
            move_1 = 'headbutt'
            move_2 = None
            move_3 = None
        elif starter == 'grimer':
            move_1 = 'pound'
            move_2 = None
            move_3 = None
        elif starter == 'shellder':
            move_1 = 'tackle'
            move_2 = 'withdraw'
            move_3 = None
        elif starter == 'gastly':
            move_1 = 'confuse ray'
            move_2 = 'lick'
            move_3 = 'night shade'
        elif starter == 'onix':
            move_1 = 'screech'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'drowzee':
            move_1 = 'hypnosis'
            move_2 = 'pound'
            move_3 = None
        elif starter == 'krabby':
            move_1 = 'bubble'
            move_2 = 'leer'
            move_3 = None
        elif starter == 'voltorb':
            move_1 = 'screech'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'exeggcute':
            move_1 = 'barrage'
            move_2 = 'hypnosis'
            move_3 = None
        elif starter == 'cubone':
            move_1 = 'growl'
            move_2 = 'tackle'
            move_3 = 'tail whip'
        elif starter == 'hitmonlee':
            move_1 = 'double kick'
            move_2 = 'meditate'
            move_3 = None
        elif starter == 'hitmonchan':
            move_1 = 'agility'
            move_2 = 'comet punch'
            move_3 = None
        elif starter == 'lickitung':
            move_1 = 'supersonic'
            move_2 = 'wrap'
            move_3 = None
        elif starter == 'koffing':
            move_1 = 'smog'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'rhyhorn':
            move_1 = 'horn attack'
            move_2 = None
            move_3 = None
        elif starter == 'chansey':
            move_1 = 'doubleslap'
            move_2 = 'pound'
            move_3 = None
        elif starter == 'tangela':
            move_1 = 'bind'
            move_2 = 'constrict'
            move_3 = None
        elif starter == 'horsea':
            move_1 = 'bubble'
            move_2 = None
            move_3 = None
        elif starter == 'goldeen':
            move_1 = 'peck'
            move_2 = 'tail whip'
            move_3 = None
        elif starter == 'staryu':
            move_1 = 'tackle'
            move_2 = None
            move_3 = None
        elif starter == 'magikarp':
            move_1 = 'splash'
            move_2 = None
            move_3 = None
        elif starter == 'eevee':
            move_1 = 'sand-attack'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'porygon':
            move_1 = 'sharpen'
            move_2 = 'tackle'
            move_3 = None
        elif starter == 'omanyte':
            move_1 = 'water gun'
            move_2 = 'withdraw'
            move_3 = None
        elif starter == 'kabuto':
            move_1 = 'harden'
            move_2 = 'scratch'
            move_3 = None

        # Data to update trainer table
        data = (f"{ctx.author.name}", f"{ctx.guild.id}", 0, 0, 10, 0, 0, 5, 0, 0, 0, f"{starter}", None, None, None, None, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        query = "INSERT INTO Trainers (username, guild_id, money, badges, pokeballs, greatballs, ultraballs, potions, super_potions, hyper_potions, full_restores, pokemon_1, pokemon_2, pokemon_3, pokemon_4, pokemon_5, pokemon_6, fire_stones, water_stones, thunder_stones, leaf_stones, moon_stones, tm01, tm02, tm03, tm04, tm05, tm06, tm07, tm08, tm09, tm10, tm11, tm12, tm13, tm14, tm15, tm16, tm17, tm18, tm19, tm20, tm21, tm22, tm23, tm24, tm25, tm26, tm27, tm28, tm29, tm30, tm31, tm32, tm33, tm34, tm35, tm36, tm37, tm38, tm39, tm40, tm41, tm42, tm43, tm44, tm45, tm46, tm47, tm48, tm49, tm50) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Set starter stats
        cursor.execute(f"SELECT * FROM Stats WHERE name = '{starter}'")
        stats = cursor.fetchone()
        
        hp = random.randint((stats['hp'] + 5), (stats['hp'] + 15))
        attack = random.randint((stats['attack'] + 5), (stats['attack'] + 15))
        defense = random.randint((stats['defense'] + 5), (stats['defense'] + 15))
        special_attack = random.randint((stats['special_attack'] + 5), (stats['special_attack'] + 15))
        special_defense = random.randint((stats['special_defense'] + 5), (stats['special_defense'] + 15))
        speed = random.randint((stats['speed'] + 5), (stats['speed'] + 15))
        type_1 = stats['type_1']
        type_2 = stats['type_2']
        
        # Data to update pokemon table
        pokemon_data = (f"{ctx.author.name}", f"{ctx.guild.id}", f"{starter}", f"{type_1}", f"{type_2}", 5, 125, 91, f"{move_1}", f"{move_2}", f"{move_3}", None, hp, hp, attack, defense, special_attack, special_defense, speed, 0, 0, 0, 0, 0, 0)
        pokemon_query = "INSERT INTO Pokemon (username, guild_id, name, type_1, type_2, level, exp, next_level_exp, move_1, move_2, move_3, move_4, current_hp, max_hp, attack, defense, special_attack, special_defense, speed, asleep, poisoned, paralyzed, burned, confused, frozen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Update database tables
        try:
            cursor.execute(query, data)
        except Exception as e:
            print(e)
            return await ctx.send("Error creating trainer in database.")
        
        try:
            cursor.execute(pokemon_query, pokemon_data)
        except Exception as e:
            print('shit')
            print(e)
            return await ctx.send("Error creating pokemon in database.")

    # Delete a pokemon trainer function   
    async def delete_trainer(self, ctx, cursor):
        # See if user has a trainer
        cursor.execute(f"SELECT * FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        trainer = cursor.fetchone()
        if not trainer:
            return await ctx.send("You don't have a trainer dumbass.")
        
        # Delete trainer's pokemon
        try:
            cursor.execute(f"DELETE FROM Pokemon WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        except Exception as e:
            print(e)
            return await ctx.send("Error deleting trainer's pokemon from database.")
        
        # Delete trainer
        try:
            cursor.execute(f"DELETE FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        except Exception as e:
            print(e)
            return await ctx.send("Error deleting trainer from database.")
        await ctx.send("Trainer deleted successfully.")
        
async def setup(bot):
    await bot.add_cog(Trainer(bot))
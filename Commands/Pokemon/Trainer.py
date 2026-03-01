import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random

class Trainer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starting_pokemon = ['bulbasaur', 'charmander', 'squirtle', 'caterpie', 'weedle', 'pidgey', 'rattata', 'spearow', 'ekans', 
                                 'pikachu', 'sandshrew', 'nidoran♀', 'nidoran♂', 'clefairy', 'vulpix', 'jigglypuff', 'zubat', 'oddish', 
                                 'paras', 'venonat', 'diglett', 'meowth', 'psyduck', 'mankey', 'growlithe', 'poliwag', 'abra', 'machop', 
                                 'bellsprout', 'tentacool', 'geodude','ponyta', 'slowpoke', 'magnemite', 'farfetchd', 'doduo', 'seel', 
                                 'grimer', 'shellder', 'gastly', 'onix', 'drowzee', 'krabby', 'voltorb', 'exeggcute', 'cubone', 'hitmonlee', 
                                 'hitmonchan', 'lickitung', 'koffing', 'rhyhorn', 'chansey', 'tangela', 'kangaskhan', 'horsea', 'goldeen', 
                                 'staryu', 'mr. mime', 'scyther', 'jynx', 'electabuzz', 'magmar', 'pinsir', 'tauros', 'magikarp', 'eevee', 
                                 'porygon', 'omanyte', 'kabuto', 'aerodactyl', 'dratini']

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
        
        # Display trainer info
        if len(args) == 0 or "info" in args[0].lower():
            await self.trainer_info(self, ctx, cursor)

        # Display trainer's pokemon
        if "pokemon" in args[0].lower():
            await self.trainer_pokemon(self, ctx, cursor)
        
        # Create a trainer
        elif "create" in args[0].lower():
            await self.create_trainer(self, ctx, args, cursor)

        # Delete a trainer
        elif "delete" in args[0].lower():
            await self.delete_trainer(self, ctx, cursor)

        # Invalid argument after !trainer command
        else:
            return await ctx.send("Invalid argument after !trainer command.")
        
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

        await ctx.send(f"**Pokemon caught:** {i}")

    async def create_trainer(self, ctx, cursor):
        # See if user already has a trainer
        cursor.execute(f"SELECT * FROM Trainers WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
        trainer = cursor.fetchone()
        if trainer:
            return await ctx.send("You already have a trainer dumbass.")
        
        # Select a starting pokemon for user
        starter = random.choice(self.starting_pokemon)
        
async def setup(bot):
    await bot.add_cog(Trainer(bot))
import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tier_1_enemies = ["skeleton", "goblin"]
        self.tier_2_enemies = ["dark mage", "outlaw", "cutthroat", "brute"]
        self.tier_3_enemies = ["troll", "ogre", "vampire"]
        self.tier_4_enemies = ["dark sorceror", "gladiator", "renegade", "deadeye"]
        self.tier_5_enemies = ["beserker"]
        self.encounter = {}
        self.enemy = {}

    # Battle function
    @commands.command(aliases=['fight'])
    async def battle(self, ctx):
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

        # Create active battle tracker
        if guild_id not in self.encounter:
            self.encounter[guild_id] = {}
        else:
            if self.encounter[guild_id]['active_battle']:
                return await ctx.send("A battle is already in progress dumbass.")
            
        # Create enemy dictionary
        if guild_id not in self.enemy:
            self.enemy[guild_id] = {}
            self.enemy[guild_id]['name'] = None
            self.enemy[guild_id]['max_hp'] = None
            self.enemy[guild_id]['current_hp'] = None
            self.enemy[guild_id]['dodge_chance'] = None
            self.enemy[guild_id]['block_chance'] = None
            self.enemy[guild_id]['crit_chance'] = None
            self.enemy[guild_id]['damage'] = None
            self.enemy[guild_id]['attacks'] = []
            self.enemy[guild_id]['gold'] = None
            self.enemy[guild_id]['exp'] = None
            self.enemy[guild_id]['good_drop_chance'] = None
            self.enemy[guild_id]['rare_drop_chance'] = None
            self.enemy[guild_id]['epic_drop_chance'] = None
            self.enemy[guild_id]['legendary_drop_chance'] = None

        # Set active battle to true
        self.encounter[guild_id]['active_battle'] = True
        
        # Generate a random number that will determine which enemy to encounter
        random_number = random.randint(1, 100)

        # If user is above level 6, select an enemy
        if result['level'] > 6:
            if random_number < 41:
                await self.tier_4_enemy_selection(ctx, guild_id)

            elif random_number > 40 and random_number < 61:
                await self.tier_3_enemy_selection(ctx, guild_id)

            elif random_number > 60 and random_number < 81:
                await self.tier_5_enemy_selection(ctx, guild_id)

            elif random_number > 80 and random_number < 96:
                await self.tier_2_enemy_selection(ctx, guild_id)

            else:
                await self.tier_1_enemy_selection(ctx, guild_id)
        
        # If user is between level 4 and 6, select an enemy
        elif result['level'] > 3 and result['level'] < 7:
            if random_number < 51:
                await self.tier_3_enemy_selection(ctx, guild_id)

            elif random_number > 50 and random_number < 71:
                await self.tier_2_enemy_selection(ctx, guild_id)

            elif random_number > 70 and random_number < 91:
                await self.tier_4_enemy_selection(ctx, guild_id)

            else:
                await self.tier_1_enemy_selection(ctx, guild_id)

        # If user is level 3 select an enemy
        elif result['level'] == 3:
            if random_number < 61:
                await self.tier_2_enemy_selection(ctx, guild_id)

            elif random_number > 60 and random_number < 81:
                await self.tier_3_enemy_selection(ctx, guild_id)

            else:
                await self.tier_1_enemy_selection(ctx, guild_id)

        # If user is level 1 or 2 select an enemy
        else:
            if random_number < 81:
                await self.tier_1_enemy_selection(ctx, guild_id)

            else:
                await self.tier_2_enemy_selection(ctx, guild_id)

    # Tier 1 enemy selection
    async def tier_1_enemy_selection(self, ctx, guild_id):
        self.enemy[guild_id]['name'] = random.choice(self.tier_1_enemies)

        # Skeleton encounter
        if self.enemy[guild_id]['name'] == "skeleton":
            self.enemy[guild_id]['max_hp'] = 100
            self.enemy[guild_id]['current_hp'] = 100
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic"]
            self.enemy[guild_id]['gold'] = 10
            self.enemy[guild_id]['exp'] = 10
            self.enemy[guild_id]['good_drop_chance'] = 10
            self.enemy[guild_id]['rare_drop_chance'] = 1
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/skeleton.webp"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Skeleton**!")

        # Goblin encounter
        elif self.enemy[guild_id]['name'] == "goblin":
            self.enemy[guild_id]['max_hp'] = 150
            self.enemy[guild_id]['current_hp'] = 150
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic"]
            self.enemy[guild_id]['gold'] = 10
            self.enemy[guild_id]['exp'] = 10
            self.enemy[guild_id]['good_drop_chance'] = 10
            self.enemy[guild_id]['rare_drop_chance'] = 0
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/goblin.webp"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Goblin**!")

    # Tier 2 enemy selection
    async def tier_2_enemy_selection(self, ctx, guild_id):
        self.enemy[guild_id]['name'] = random.choice(self.tier_2_enemies)

        # Dark Mage encounter
        if self.enemy[guild_id]['name'] == "dark mage":
            self.enemy[guild_id]['max_hp'] = 100
            self.enemy[guild_id]['current_hp'] = 100
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 15
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic", "fireball", "frostbolt"]
            self.enemy[guild_id]['gold'] = 20
            self.enemy[guild_id]['exp'] = 20
            self.enemy[guild_id]['good_drop_chance'] = 20
            self.enemy[guild_id]['rare_drop_chance'] = 10
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/mage.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Dark Mage**!")

        # Outlaw encounter
        elif self.enemy[guild_id]['name'] == "outlaw":
            self.enemy[guild_id]['max_hp'] = 100
            self.enemy[guild_id]['current_hp'] = 100
            self.enemy[guild_id]['dodge_chance'] = 15
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 15
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic", "trishot", "snipe"]
            self.enemy[guild_id]['gold'] = 20
            self.enemy[guild_id]['exp'] = 20
            self.enemy[guild_id]['good_drop_chance'] = 20
            self.enemy[guild_id]['rare_drop_chance'] = 10
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/outlaw.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Outlaw**!")

        # Cutthroat encounter
        elif self.enemy[guild_id]['name'] == "cutthroat":
            self.enemy[guild_id]['max_hp'] = 100
            self.enemy[guild_id]['current_hp'] = 100
            self.enemy[guild_id]['dodge_chance'] = 20
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic", "sap", "stab"]
            self.enemy[guild_id]['gold'] = 20
            self.enemy[guild_id]['exp'] = 20
            self.enemy[guild_id]['good_drop_chance'] = 20
            self.enemy[guild_id]['rare_drop_chance'] = 10
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/cutthroat.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Cutthroat**!")

        # Brute encounter
        elif self.enemy[guild_id]['name'] == "brute":
            self.enemy[guild_id]['max_hp'] = 200
            self.enemy[guild_id]['current_hp'] = 200
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 20
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["basic", "crush", "flurry"]
            self.enemy[guild_id]['gold'] = 20
            self.enemy[guild_id]['exp'] = 20
            self.enemy[guild_id]['good_drop_chance'] = 20
            self.enemy[guild_id]['rare_drop_chance'] = 10
            self.enemy[guild_id]['epic_drop_chance'] = 0
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/brute.png"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Brute**!")

    # Tier 3 enemy selection
    async def tier_3_enemy_selection(self, ctx, guild_id):
        self.enemy[guild_id]['name'] = random.choice(self.tier_3_enemies)

        # Troll encounter
        if self.enemy[guild_id]['name'] == "troll":
            self.enemy[guild_id]['max_hp'] = 400
            self.enemy[guild_id]['current_hp'] = 400
            self.enemy[guild_id]['dodge_chance'] = 5
            self.enemy[guild_id]['block_chance'] = 20
            self.enemy[guild_id]['crit_chance'] = 20
            self.enemy[guild_id]['damage'] = 20
            self.enemy[guild_id]['attacks'] = ["basic", "crush", "flurry"]
            self.enemy[guild_id]['gold'] = 30
            self.enemy[guild_id]['exp'] = 50
            self.enemy[guild_id]['good_drop_chance'] = 30
            self.enemy[guild_id]['rare_drop_chance'] = 20
            self.enemy[guild_id]['epic_drop_chance'] = 10
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/troll.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Troll**!")

        # Ogre encounter
        elif self.enemy[guild_id]['name'] == "ogre":
            self.enemy[guild_id]['max_hp'] = 400
            self.enemy[guild_id]['current_hp'] = 400
            self.enemy[guild_id]['dodge_chance'] = 5
            self.enemy[guild_id]['block_chance'] = 20
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 30
            self.enemy[guild_id]['attacks'] = ["basic", "crush", "haymaker"]
            self.enemy[guild_id]['gold'] = 30
            self.enemy[guild_id]['exp'] = 50
            self.enemy[guild_id]['good_drop_chance'] = 30
            self.enemy[guild_id]['rare_drop_chance'] = 20
            self.enemy[guild_id]['epic_drop_chance'] = 10
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/ogre.jpeg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Ogre**!")

        # Vampire encounter
        elif self.enemy[guild_id]['name'] == "vampire":
            self.enemy[guild_id]['max_hp'] = 300
            self.enemy[guild_id]['current_hp'] = 300
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 30
            self.enemy[guild_id]['attacks'] = ["lifesteal"]
            self.enemy[guild_id]['gold'] = 30
            self.enemy[guild_id]['exp'] = 50
            self.enemy[guild_id]['good_drop_chance'] = 30
            self.enemy[guild_id]['rare_drop_chance'] = 20
            self.enemy[guild_id]['epic_drop_chance'] = 10
            self.enemy[guild_id]['legendary_drop_chance'] = 0

            file_path = f"Images/vampire.webp"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Vampire**!")

    # Tier 4 enemy selection
    async def tier_4_enemy_selection(self, ctx, guild_id):
        # Select random tier 4 enemy
        self.enemy[guild_id]['name'] = random.choice(self.tier_4_enemies)

        # Dark Sorceror encounter
        if self.enemy[guild_id]['name'] == "dark sorceror":
            self.enemy[guild_id]['max_hp'] = 500
            self.enemy[guild_id]['current_hp'] = 500
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 20
            self.enemy[guild_id]['damage'] = 30
            self.enemy[guild_id]['attacks'] = ["basic", "wildfire", "lightning"]
            self.enemy[guild_id]['gold'] = 50
            self.enemy[guild_id]['exp'] = 100
            self.enemy[guild_id]['good_drop_chance'] = 40
            self.enemy[guild_id]['rare_drop_chance'] = 30
            self.enemy[guild_id]['epic_drop_chance'] = 20
            self.enemy[guild_id]['legendary_drop_chance'] = 5

            # Send image
            file_path = f"Images/sorceror.webp"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Dark Sorceror**!")

        # Gladiator encounter
        elif self.enemy[guild_id]['name'] == "gladiator":
            self.enemy[guild_id]['max_hp'] = 800
            self.enemy[guild_id]['current_hp'] = 800
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 20
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 30
            self.enemy[guild_id]['attacks'] = ["basic", "haymaker", "flurry"]
            self.enemy[guild_id]['gold'] = 50
            self.enemy[guild_id]['exp'] = 100
            self.enemy[guild_id]['good_drop_chance'] = 40
            self.enemy[guild_id]['rare_drop_chance'] = 30
            self.enemy[guild_id]['epic_drop_chance'] = 20
            self.enemy[guild_id]['legendary_drop_chance'] = 5

            file_path = f"Images/gladiator.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Gladiator**!")
        
        # Renegade encounter
        elif self.enemy[guild_id]['name'] == "renegade":
            self.enemy[guild_id]['max_hp'] = 600
            self.enemy[guild_id]['current_hp'] = 600
            self.enemy[guild_id]['dodge_chance'] = 20
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 20
            self.enemy[guild_id]['damage'] = 20
            self.enemy[guild_id]['attacks'] = ["basic", "bladestorm", "stab"]
            self.enemy[guild_id]['gold'] = 50
            self.enemy[guild_id]['exp'] = 100
            self.enemy[guild_id]['good_drop_chance'] = 40
            self.enemy[guild_id]['rare_drop_chance'] = 30
            self.enemy[guild_id]['epic_drop_chance'] = 20
            self.enemy[guild_id]['legendary_drop_chance'] = 5

            file_path = f"Images/renegade.png"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Renegade**!")

        # Deadeye encounter
        elif self.enemy[guild_id]['name'] == "deadeye":
            self.enemy[guild_id]['max_hp'] = 600
            self.enemy[guild_id]['current_hp'] = 600
            self.enemy[guild_id]['dodge_chance'] = 15
            self.enemy[guild_id]['block_chance'] = 15
            self.enemy[guild_id]['crit_chance'] = 20
            self.enemy[guild_id]['damage'] = 30
            self.enemy[guild_id]['attacks'] = ["basic", "rapidfire", "volley"]
            self.enemy[guild_id]['gold'] = 50
            self.enemy[guild_id]['exp'] = 100
            self.enemy[guild_id]['good_drop_chance'] = 40
            self.enemy[guild_id]['rare_drop_chance'] = 30
            self.enemy[guild_id]['epic_drop_chance'] = 20
            self.enemy[guild_id]['legendary_drop_chance'] = 5

            file_path = f"Images/deadeye.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Deadeye**!")
    
    # Tier 5 enemy selection
    async def tier_5_enemy_selection(self, ctx, guild_id):
        self.enemy[guild_id]['name'] = random.choice(self.tier_5_enemies)

        # Beserker encounter
        if self.enemy[guild_id]['name'] == "beserker":
            self.enemy[guild_id]['max_hp'] = 1000
            self.enemy[guild_id]['current_hp'] = 1000
            self.enemy[guild_id]['dodge_chance'] = 10
            self.enemy[guild_id]['block_chance'] = 10
            self.enemy[guild_id]['crit_chance'] = 10
            self.enemy[guild_id]['damage'] = 10
            self.enemy[guild_id]['attacks'] = ["beserk"]
            self.enemy[guild_id]['gold'] = 20
            self.enemy[guild_id]['exp'] = 30
            self.enemy[guild_id]['good_drop_chance'] = 0
            self.enemy[guild_id]['rare_drop_chance'] = 30
            self.enemy[guild_id]['epic_drop_chance'] = 30
            self.enemy[guild_id]['legendary_drop_chance'] = 5

            file_path = f"Images/beserker.jpg"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("You've encountered a **Beserker**!")

async def setup(bot):
    await bot.add_cog(Battle(bot))
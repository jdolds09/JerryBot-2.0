import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.classes = ['warrior', 'hunter', 'mage', 'rogue', 'gambler']

    # Character function
    @commands.command()
    async def character(self, ctx, *args):
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
        
        # Display character info
        if len(args) == 0 or "info" in args[0].lower():
            await Character.character_info(self, ctx, cursor)
        
        # Create a character
        elif "create" in args[0].lower():
            await Character.create_character(self, ctx, args, cursor)

        # Delete a character
        elif "delete" in args[0].lower():
            await Character.delete_character(self, ctx, cursor)

        # Invalid argument after !character command
        else:
            return await ctx.send("Invalid argument after !character command.")

    # Output character info function
    async def character_info(self, ctx, cursor):
        # Retrieve character info from database
        try:
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")

            result = cursor.fetchone()
            if not result:
                return await ctx.send("You don't have a character dumbass.")
            
        except Exception as e:
            print(e)
            return await ctx.send("Error grabbing character details")
        
        # Output character info
        await ctx.send(f"**__{ctx.author.name}'s {result['class'].capitalize()}:__**")
        await ctx.send(f"**__Level:__** {result['level']}")
        await ctx.send(f"**__HP:__** {result['current_hp']}/{result['max_hp']}")
        await ctx.send(f"**__EXP:__** {result['exp']}/{result['next_level_exp']}")
        await ctx.send(f"**__Gold:__** {result['gold']}")
        await ctx.send("--------------------------------------")
        await ctx.send("**GEAR**")
        # Output Warrior Gear
        if result['class'] == 'warrior':
            # Output boots
            if result['boots'] == 1:
                await ctx.send("**__Boots__**: Shitty Boots")
            elif result['boots'] == 2:
                await ctx.send("**__Boots__**: 🟩 Good Boots of Asskicking (+10 Health)")
            elif result['boots'] == 3:
                await ctx.send("**__Boots__**: 🟦 Rare Boots of Asskicking (+10 Health, +1% Dodge & Block)")
            elif result['boots'] == 4:
                await ctx.send("**__Boots__**: 🟪 Epic Boots of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['boots'] == 5:
                await ctx.send("**__Boots__**: 🟨 Legendary Boots of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            #Ouput legs
            if result['legs'] == 1:
                await ctx.send("**__Legs__**: Shitty Greaves")
            elif result['legs'] == 2:
                await ctx.send("**__Legs__**: 🟩 Good Greaves of Asskicking (+10 Health)")
            elif result['legs'] == 3:
                await ctx.send("**__Legs__**: 🟦 Rare Greaves of Asskicking (+10 Health, +1% Dodge & Block)")
            elif result['legs'] == 4:
                await ctx.send("**__Legs__**: 🟪 Epic Greaves of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['legs'] == 5:
                await ctx.send("**__Legs__**: 🟨 Legendary Greaves of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output chest
            if result['chest'] == 1:
                await ctx.send("**__Chest__**: Shitty Chestplate")
            elif result['chest'] == 2:
                await ctx.send("**__Chest__**: 🟩 Good Chestplate of Asskicking (+10 Health)")
            elif result['chest'] == 3:
                await ctx.send("**__Chest__**: 🟦 Rare Chestplate of Asskicking (+10 Health, +1% Dodge & Block)")
            elif result['chest'] == 4:
                await ctx.send("**__Chest__**: 🟪 Epic Chestplate of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['chest'] == 5:
                await ctx.send("**__Chest__**: 🟨 Legendary Chestplate of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output gloves
            if result['gloves'] == 1:
                await ctx.send("**__Gloves__**: Shitty Gauntlets")
            elif result['gloves'] == 2:
                await ctx.send("**__Gloves__**: 🟩 Good Gauntlets of Asskicking (+10 Health)")
            elif result['gloves'] == 3:
                await ctx.send("**__Gloves__**: 🟦 Rare Gauntlets of Asskicking (+10 Health, +1% Dodge & Block)")
            elif result['gloves'] == 4:
                await ctx.send("**__Gloves__**: 🟪 Epic Gauntlets of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['gloves'] == 5:
                await ctx.send("**__Gloves__**: 🟨 Legendary Gauntlets of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output helmet
            if result['helmet'] == 1:
                await ctx.send("**__Helmet__**: Shitty Helmet")
            elif result['helmet'] == 2:
                await ctx.send("**__Helmet__**: 🟩 Good Helmet of Asskicking (+10 Health)")
            elif result['helmet'] == 3:
                await ctx.send("**__Helmet__**: 🟦 Rare Helmet of Asskicking (+10 Health, +1% Dodge & Block)")
            elif result['helmet'] == 4:
                await ctx.send("**__Helmet__**: 🟪 Epic Helmet of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['helmet'] == 5:
                await ctx.send("**__Helmet__**: 🟨 Legendary Helmet of Asskicking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output main hand
            if result['main_hand'] == 1:
                await ctx.send("**__Main Hand__**: Shitty Sword")
            elif result['main_hand'] == 2:
                await ctx.send("**__Main Hand__**: 🟩 Good Sword of Asskicking (+5 Damage)")
            elif result['main_hand'] == 3:
                await ctx.send("**__Main Hand__**: 🟦 Rare Sword of Asskicking (+10 Damage)")
            elif result['main_hand'] == 4:
                await ctx.send("**__Main Hand__**: 🟪 Epic Sword of Asskicking (+15 Damage)")
            elif result['main_hand'] == 5:
                await ctx.send("**__Main Hand__**: 🟨 Legendary Sword of Asskicking (+20 Damage)")

            # Output off hand
            if result['off_hand'] == 1:
                await ctx.send("**__Off Hand__**: Shitty Shield")
            elif result['off_hand'] == 2:
                await ctx.send("**__Off Hand__**: 🟩 Good Shield of Asskicking (+1% Block)")
            elif result['off_hand'] == 3:
                await ctx.send("**__Off Hand__**: 🟦 Rare Shield of Asskicking (+3% Block)")
            elif result['off_hand'] == 4:
                await ctx.send("**__Off Hand__**: 🟪 Epic Shield of Asskicking (+5% Block)")
            elif result['off_hand'] == 5:
                await ctx.send("**__Off Hand__**: 🟨 Legendary Shield of Asskicking (+10% Block)")

        # Output hunter Gear
        elif result['class'] == 'hunter':
            # Output boots
            if result['boots'] == 1:
                await ctx.send("**__Boots__**: Shitty Boots")
            elif result['boots'] == 2:
                    await ctx.send("**__Boots__**: 🟩 Good Boots of Shooting Motherfuckers with Arrows (+10 Health)")
            elif result['boots'] == 3:
                    await ctx.send("**__Boots__**: 🟦 Rare Boots of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block)")
            elif result['boots'] == 4:
                    await ctx.send("**__Boots__**: 🟪 Epic Boots of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['boots'] == 5:
                    await ctx.send("**__Boots__**: 🟨 Legendary Boots of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
            #Ouput legs
            if result['legs'] == 1:
                await ctx.send("**__Legs__**: Shitty Pants")
            elif result['legs'] == 2:
                await ctx.send("**__Legs__**: 🟩 Good Pants of Shooting Motherfuckers with Arrows (+10 Health)")
            elif result['legs'] == 3:
                await ctx.send("**__Legs__**: 🟦 Rare Pants of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block)")
            elif result['legs'] == 4:
                await ctx.send("**__Legs__**: 🟪 Epic Pants of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['legs'] == 5:
                await ctx.send("**__Legs__**: 🟨 Legendary Pants of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output chest
            if result['chest'] == 1:
                await ctx.send("**__Chest__**: Shitty Chainmail")
            elif result['chest'] == 2:
                await ctx.send("**__Chest__**: 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+10 Health)")
            elif result['chest'] == 3:
                await ctx.send("**__Chest__**: 🟦 Rare Chainmail of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block)")
            elif result['chest'] == 4:
                await ctx.send("**__Chest__**: 🟪 Epic Chainmail of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['chest'] == 5:
                await ctx.send("**__Chest__**: 🟨 Legendary Chainmail of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output gloves
            if result['gloves'] == 1:
                await ctx.send("**__Gloves__**: Shitty Gloves")
            elif result['gloves'] == 2:
                await ctx.send("**__Gloves__**: 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+10 Health)")
            elif result['gloves'] == 3:
                await ctx.send("**__Gloves__**: 🟦 Rare Gloves of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block)")
            elif result['gloves'] == 4:
                await ctx.send("**__Gloves__**: 🟪 Epic Gloves of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['gloves'] == 5:
                await ctx.send("**__Gloves__**: 🟨 Legendary Gloves of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output helmet
            if result['helmet'] == 1:
                await ctx.send("**__Helmet__**: Shitty Hood")
            elif result['helmet'] == 2:
                await ctx.send("**__Helmet__**: 🟩 Good Hood of Shooting Motherfuckers with Arrows (+10 Health)")
            elif result['helmet'] == 3:
                await ctx.send("**__Helmet__**: 🟦 Rare Hood of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block)")
            elif result['helmet'] == 4:
                await ctx.send("**__Helmet__**: 🟪 Epic Hood of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['helmet'] == 5:
                await ctx.send("**__Helmet__**: 🟨 Legendary Hood of Shooting Motherfuckers with Arrows (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output main hand
            if result['main_hand'] == 1:
                await ctx.send("**__Main Hand__**: Shitty Bow")
            elif result['main_hand'] == 2:
                await ctx.send("**__Main Hand__**: 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)")
            elif result['main_hand'] == 3:
                await ctx.send("**__Main Hand__**: 🟦 Rare Bow of Shooting Motherfuckers with Arrows (+10 Damage)")
            elif result['main_hand'] == 4:
                await ctx.send("**__Main Hand__**: 🟪 Epic Bow of Shooting Motherfuckers with Arrows (+15 Damage)")
            elif result['main_hand'] == 5:
                await ctx.send("**__Main Hand__**: 🟨 Legendary Bow of Shooting Motherfuckers with Arrows (+20 Damage)")

            # Output off hand
            if result['off_hand'] == 1:
                await ctx.send("**__Off Hand__**: Shitty Quiver")
            elif result['off_hand'] == 2:
                await ctx.send("**__Off Hand__**: 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)")
            elif result['off_hand'] == 3:
                await ctx.send("**__Off Hand__**: 🟦 Rare Quiver of Shooting Motherfuckers with Arrows (+2 Damage)")
            elif result['off_hand'] == 4:
                await ctx.send("**__Off Hand__**: 🟪 Epic Quiver of Shooting Motherfuckers with Arrows (+3 Damage)")
            elif result['off_hand'] == 5:
                await ctx.send("**__Off Hand__**: 🟨 Legendary Quiver of Shooting Motherfuckers with Arrows (+5 Damage)")
        
        # Output Mage Gear
        elif result['class'] == 'mage':
            # Output boots
            if result['boots'] == 1:
                await ctx.send("**__Boots__**: Shitty Boots")
            elif result['boots'] == 2:
                await ctx.send("**__Boots__**: 🟩 Good Boots of Casting Spells and Shit (+10 Health)")
            elif result['boots'] == 3:
                await ctx.send("**__Boots__**: 🟦 Rare Boots of Casting Spells and Shit (+10 Health, +1% Dodge & Block)")
            elif result['boots'] == 4:
                await ctx.send("**__Boots__**: 🟪 Epic Boots of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['boots'] == 5:
                await ctx.send("**__Boots__**: 🟨 Legendary Boots of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")
            #Ouput legs
            if result['legs'] == 1:
                await ctx.send("**__Legs__**: Shitty Pants")
            elif result['legs'] == 2:
                await ctx.send("**__Legs__**: 🟩 Good Pants of Casting Spells and Shit (+10 Health)")
            elif result['legs'] == 3:
                await ctx.send("**__Legs__**: 🟦 Rare Pants of Casting Spells and Shit (+10 Health, +1% Dodge & Block)")
            elif result['legs'] == 4:
                await ctx.send("**__Legs__**: 🟪 Epic Pants of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['legs'] == 5:
                await ctx.send("**__Legs__**: 🟨 Legendary Pants of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output chest
            if result['chest'] == 1:
                await ctx.send("**__Chest__**: Shitty Robes")
            elif result['chest'] == 2:
                await ctx.send("**__Chest__**: 🟩 Good Robes of Casting Spells and Shit (+10 Health)")
            elif result['chest'] == 3:
                await ctx.send("**__Chest__**: 🟦 Rare Robes of Casting Spells and Shit (+10 Health, +1% Dodge & Block)")
            elif result['chest'] == 4:
                await ctx.send("**__Chest__**: 🟪 Epic Robes of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['chest'] == 5:
                await ctx.send("**__Chest__**: 🟨 Legendary Robes of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output gloves
            if result['gloves'] == 1:
                await ctx.send("**__Gloves__**: Shitty Gloves")
            elif result['gloves'] == 2:
                await ctx.send("**__Gloves__**: 🟩 Good Gloves of Casting Spells and Shit (+10 Health)")
            elif result['gloves'] == 3:
                await ctx.send("**__Gloves__**: 🟦 Rare Gloves of Casting Spells and Shit (+10 Health, +1% Dodge & Block)")
            elif result['gloves'] == 4:
                await ctx.send("**__Gloves__**: 🟪 Epic Gloves of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['gloves'] == 5:
                await ctx.send("**__Gloves__**: 🟨 Legendary Gloves of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output helmet
            if result['helmet'] == 1:
                await ctx.send("**__Helmet__**: Shitty Hood")
            elif result['helmet'] == 2:
                await ctx.send("**__Helmet__**: 🟩 Good Hood of Casting Spells and Shit (+10 Health)")
            elif result['helmet'] == 3:
                await ctx.send("**__Helmet__**: 🟦 Rare Hood of Casting Spells and Shit (+10 Health, +1% Dodge & Block)")
            elif result['helmet'] == 4:
                await ctx.send("**__Helmet__**: 🟪 Epic Hood of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['helmet'] == 5:
                await ctx.send("**__Helmet__**: 🟨 Legendary Hood of Casting Spells and Shit (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output main hand
            if result['main_hand'] == 1:
                await ctx.send("**__Main Hand__**: Shitty Staff")
            elif result['main_hand'] == 2:
                await ctx.send("**__Main Hand__**: 🟩 Good Staff of Casting Spells and Shit (+5 Damage)")
            elif result['main_hand'] == 3:
                await ctx.send("**__Main Hand__**: 🟦 Rare Staff of Casting Spells and Shit (+10 Damage)")
            elif result['main_hand'] == 4:
                await ctx.send("**__Main Hand__**: 🟪 Epic Staff of Casting Spells and Shit (+15 Damage)")
            elif result['main_hand'] == 5:
                await ctx.send("**__Main Hand__**: 🟨 Legendary Staff of Casting Spells and Shit (+20 Damage)")

            # Output off hand
            if result['off_hand'] == 1:
                await ctx.send("**__Off Hand__**: Shitty Spellbook")
            elif result['off_hand'] == 2:
                await ctx.send("**__Off Hand__**: 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)")
            elif result['off_hand'] == 3:
                await ctx.send("**__Off Hand__**: 🟦 Rare Spellbook of Casting Spells and Shit (+2 Damage)")
            elif result['off_hand'] == 4:
                await ctx.send("**__Off Hand__**: 🟪 Epic Spellbook of Casting Spells and Shit (+3 Damage)")
            elif result['off_hand'] == 5:
                await ctx.send("**__Off Hand__**: 🟨 Legendary Spellbook of Casting Spells and Shit (+5 Damage)")

        # Output Rogue Gear
        elif result['class'] == 'rogue':
            # Output boots
            if result['boots'] == 1:
                await ctx.send("**__Boots__**: Shitty Boots")
            elif result['boots'] == 2:
                await ctx.send("**__Boots__**: 🟩 Good Boots of Shanking (+10 Health)")
            elif result['boots'] == 3:
                await ctx.send("**__Boots__**: 🟦 Rare Boots of Shanking (+10 Health, +1% Dodge & Block)")
            elif result['boots'] == 4:
                await ctx.send("**__Boots__**: 🟪 Epic Boots of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['boots'] == 5:
                await ctx.send("**__Boots__**: 🟨 Legendary Boots of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            #Ouput legs
            if result['legs'] == 1:
                await ctx.send("**__Legs__**: Shitty Pants")
            elif result['legs'] == 2:
                await ctx.send("**__Legs__**: 🟩 Good Pants of Shanking (+10 Health)")
            elif result['legs'] == 3:
                await ctx.send("**__Legs__**: 🟦 Rare Pants of Shanking (+10 Health, +1% Dodge & Block)")
            elif result['legs'] == 4:
                await ctx.send("**__Legs__**: 🟪 Epic Pants of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['legs'] == 5:
                await ctx.send("**__Legs__**: 🟨 Legendary Pants of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output chest
            if result['chest'] == 1:
                await ctx.send("**__Chest__**: Shitty Vest")
            elif result['chest'] == 2:
                await ctx.send("**__Chest__**: 🟩 Good Vest of Shanking (+10 Health)")
            elif result['chest'] == 3:
                await ctx.send("**__Chest__**: 🟦 Rare Vest of Shanking (+10 Health, +1% Dodge & Block)")
            elif result['chest'] == 4:
                await ctx.send("**__Chest__**: 🟪 Epic Vest of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['chest'] == 5:
                await ctx.send("**__Chest__**: 🟨 Legendary Vest of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output gloves
            if result['gloves'] == 1:
                await ctx.send("**__Gloves__**: Shitty Gloves")
            elif result['gloves'] == 2:
                await ctx.send("**__Gloves__**: 🟩 Good Gloves of Shanking (+10 Health)")
            elif result['gloves'] == 3:
                await ctx.send("**__Gloves__**: 🟦 Rare Gloves of Shanking (+10 Health, +1% Dodge & Block)")
            elif result['gloves'] == 4:
                await ctx.send("**__Gloves__**: 🟪 Epic Gloves of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['gloves'] == 5:
                await ctx.send("**__Gloves__**: 🟨 Legendary Gloves of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output helmet
            if result['helmet'] == 1:
                await ctx.send("**__Helmet__**: Shitty Hood")
            elif result['helmet'] == 2:
                await ctx.send("**__Helmet__**: 🟩 Good Hood of Shanking (+10 Health)")
            elif result['helmet'] == 3:
                await ctx.send("**__Helmet__**: 🟦 Rare Hood of Shanking (+10 Health, +1% Dodge & Block)")
            elif result['helmet'] == 4:
                await ctx.send("**__Helmet__**: 🟪 Epic Hood of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['helmet'] == 5:
                await ctx.send("**__Helmet__**: 🟨 Legendary Hood of Shanking (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% hit chance)")

            # Output main hand
            if result['main_hand'] == 1:
                await ctx.send("**__Main Hand__**: Shitty Dagger")
            elif result['main_hand'] == 2:
                await ctx.send("**__Main Hand__**: 🟩 Good Dagger of Shanking (+1 Damage)")
            elif result['main_hand'] == 3:
                await ctx.send("**__Main Hand__**: 🟦 Rare Dagger of Shanking (+3 Damage)")
            elif result['main_hand'] == 4:
                await ctx.send("**__Main Hand__**: 🟪 Epic Dagger of Shanking (+5 Damage)")
            elif result['main_hand'] == 5:
                await ctx.send("**__Main Hand__**: 🟨 Legendary Dagger of Shanking (+10 Damage)")
            # Output off hand
            if result['off_hand'] == 1:
                await ctx.send("**__Off Hand__**: Shitty Dagger")
            elif result['off_hand'] == 2:
                await ctx.send("**__Off Hand__**: 🟩 Good Dagger of Shanking (+1 Damage)")
            elif result['off_hand'] == 3:
                await ctx.send("**__Off Hand__**: 🟦 Rare Dagger of Shanking (+3 Damage)")
            elif result['off_hand'] == 4:
                await ctx.send("**__Off Hand__**: 🟪 Epic Dagger of Shanking (+5 Damage)")
            elif result['off_hand'] == 5:
                await ctx.send("**__Off Hand__**: 🟨 Legendary Dagger of Shanking (+10 Damage)")

        # Output Gambler Gear
        elif result['class'] == 'gambler':
            # Output boots
            if result['boots'] == 1:
                await ctx.send("**__Boots__**: Shitty Boots")
            elif result['boots'] == 2:
                await ctx.send("**__Boots__**: 🟩 Good Boots of Luck (+10 Health)")
            elif result['boots'] == 3:
                await ctx.send("**__Boots__**: 🟦 Rare Boots of Luck (+10 Health, +1% Dodge & Block)")
            elif result['boots'] == 4:
                await ctx.send("**__Boots__**: 🟪 Epic Boots of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['boots'] == 5:
                await ctx.send("**__Boots__**: 🟨 Legendary Boots of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% Chance of Success)")

            #Ouput legs
            if result['legs'] == 1:
                await ctx.send("**__Legs__**: Shitty Pants")
            elif result['legs'] == 2:
                await ctx.send("**__Legs__**: 🟩 Good Pants of Luck (+10 Health)")
            elif result['legs'] == 3:
                await ctx.send("**__Legs__**: 🟦 Rare Pants of Luck (+10 Health, +1% Dodge & Block)")
            elif result['legs'] == 4:
                await ctx.send("**__Legs__**: 🟪 Epic Pants of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['legs'] == 5:
                await ctx.send("**__Legs__**: 🟨 Legendary Pants of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% Chance of Success)")

            # Output chest
            if result['chest'] == 1:
                await ctx.send("**__Chest__**: Shitty Jacket")
            elif result['chest'] == 2:
                await ctx.send("**__Chest__**: 🟩 Good Jacket of Luck (+10 Health)")
            elif result['chest'] == 3:
                await ctx.send("**__Chest__**: 🟦 Rare Jacket of Luck (+10 Health, +1% Dodge & Block)")
            elif result['chest'] == 4:
                await ctx.send("**__Chest__**: 🟪 Epic Jacket of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['chest'] == 5:
                await ctx.send("**__Chest__**: 🟨 Legendary Jacket of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% Chance of Success)")

            # Output gloves
            if result['gloves'] == 1:
                await ctx.send("**__Gloves__**: Shitty Gloves")
            elif result['gloves'] == 2:
                await ctx.send("**__Gloves__**: 🟩 Good Gloves of Luck (+10 Health)")
            elif result['gloves'] == 3:
                await ctx.send("**__Gloves__**: 🟦 Rare Gloves of Luck (+10 Health, +1% Dodge & Block)")
            elif result['gloves'] == 4:
                await ctx.send("**__Gloves__**: 🟪 Epic Gloves of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['gloves'] == 5:
                await ctx.send("**__Gloves__**: 🟨 Legendary Gloves of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% Chance of Success)")

            # Output helmet
            if result['helmet'] == 1:
                await ctx.send("**__Helmet__**: Shitty Fedora")
            elif result['helmet'] == 2:
                await ctx.send("**__Helmet__**: 🟩 Good Fedora of Luck (+10 Health)")
            elif result['helmet'] == 3:
                await ctx.send("**__Helmet__**: 🟦 Rare Fedora of Luck (+10 Health, +1% Dodge & Block)")
            elif result['helmet'] == 4:
                await ctx.send("**__Helmet__**: 🟪 Epic Fedora of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance)")
            elif result['helmet'] == 5:
                await ctx.send("**__Helmet__**: 🟨 Legendary Fedora of Luck (+10 Health, +1% Dodge & Block, +1% Crit Chance, +1% Chance of Success)")

            # Output main hand
            if result['main_hand'] == 1:
                await ctx.send("**__Main Hand__**: Shitty Trinket")
            elif result['main_hand'] == 2:
                await ctx.send("**__Main Hand__**: 🟩 Good Trinket of Luck (+5% Chance of Success)")
            elif result['main_hand'] == 3:
                await ctx.send("**__Main Hand__**: 🟦 Rare Trinket of Luck (+10% Chance of Success)")
            elif result['main_hand'] == 4:
                await ctx.send("**__Main Hand__**: 🟪 Epic Trinket of Luck (+15% Chance of Success)")
            elif result['main_hand'] == 5:
                await ctx.send("**__Main Hand__**: 🟨 Legendary Trinket of Luck (+20% Chance of Success)")

            # Output off hand
            if result['off_hand'] == 1:
                await ctx.send("**__Off Hand__**: Shitty Charm")
            elif result['off_hand'] == 2:
                await ctx.send("**__Off Hand__**: 🟩 Good Charm of Luck (+1% Chance of Success)")
            elif result['off_hand'] == 3:
                await ctx.send("**__Off Hand__**: 🟦 Rare Charm of Luck (+2% Chance of Success)")
            elif result['off_hand'] == 4:
                await ctx.send("**__Off Hand__**: 🟪 Epic Charm of Luck (+3% Chance of Success)")
            elif result['off_hand'] == 5:
                await ctx.send("**__Off Hand__**: 🟨 Legendary Charm of Luck (+5% Chance of Success)")

    # Create character function
    async def create_character(self, ctx, args, cursor):
        # Check if user already has a character
        try:
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")

            result = cursor.fetchone()
            if result:
                return await ctx.send("You already have a character dumbass")
        except Exception as e:
            print(e)
            return await ctx.send("Error checking for existing character.")

        # User inputted an invalid class
        if args[1].lower() not in self.classes:
            await ctx.send(f"Invalid class. Below are the classes to choose from:")
            for i in range(len(self.classes)):
                await ctx.send(f"**{self.classes[i].capitalize()}**")
            return
        
        # Create character based on class chosen
        else:
            if args[1].lower() == 'warrior':
                try:
                    cursor.execute(f"INSERT INTO `Characters` (`username`, `guild_id`, `class`, `level`, `exp`, `next_level_exp`, `max_hp`, `current_hp`, `dodge_chance`, `block_chance`, `crit_chance`, `hit_chance`, `main_hand_damage`, `off_hand_damage`, `gold`, `boots`, `legs`, `chest`, `gloves`, `helmet`, `main_hand`, `off_hand`, `potions`, `cooldown_1`, `cooldown_2`, `cooldown_3`, `cooldown_4`, `cooldown_5`, `cooldown_6`, `cooldown_7`, `cooldown_8`, `cooldown_9`, `cooldown_10`, `precision_active`, `relentless_active`, `gouge_active`, `counter_active`, `shieldbash_active`) VALUES ('{ctx.author.name}', '{ctx.guild.id}', 'warrior', 1, 0, 50, 200, 200, 10, 20, 10, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error creating character.")
                
            elif args[1].lower() == 'hunter':
                try:
                    cursor.execute(f"INSERT INTO `Characters` (`username`, `guild_id`, `class`, `level`, `exp`, `next_level_exp`, `max_hp`, `current_hp`, `dodge_chance`, `block_chance`, `crit_chance`, `hit_chance`, `main_hand_damage`, `off_hand_damage`, `gold`, `boots`, `legs`, `chest`, `gloves`, `helmet`, `main_hand`, `off_hand`, `potions`, `cooldown_1`, `cooldown_2`, `cooldown_3`, `cooldown_4`, `cooldown_5`, `cooldown_6`, `cooldown_7`, `cooldown_8`, `cooldown_9`, `cooldown_10`, `precision_active`, `relentless_active`, `gouge_active`, `counter_active`, `shieldbash_active`) VALUES ('{ctx.author.name}', '{ctx.guild.id}', 'hunter', 1, 0, 50, 150, 150, 15, 15, 15, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error creating character.")
                
            elif args[1].lower() == 'mage':
                try:
                    cursor.execute(f"INSERT INTO `Characters` (`username`, `guild_id`, `class`, `level`, `exp`, `next_level_exp`, `max_hp`, `current_hp`, `dodge_chance`, `block_chance`, `crit_chance`, `hit_chance`, `main_hand_damage`, `off_hand_damage`, `gold`, `boots`, `legs`, `chest`, `gloves`, `helmet`, `main_hand`, `off_hand`, `potions`, `cooldown_1`, `cooldown_2`, `cooldown_3`, `cooldown_4`, `cooldown_5`, `cooldown_6`, `cooldown_7`, `cooldown_8`, `cooldown_9`, `cooldown_10`, `precision_active`, `relentless_active`, `gouge_active`, `counter_active`, `shieldbash_active`) VALUES ('{ctx.author.name}', '{ctx.guild.id}', 'mage', 1, 0, 50, 100, 100, 10, 10, 20, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error creating character.")
                
            elif args[1].lower() == 'rogue':
                try:
                    cursor.execute(f"INSERT INTO `Characters` (`username`, `guild_id`, `class`, `level`, `exp`, `next_level_exp`, `max_hp`, `current_hp`, `dodge_chance`, `block_chance`, `crit_chance`, `hit_chance`, `main_hand_damage`, `off_hand_damage`, `gold`, `boots`, `legs`, `chest`, `gloves`, `helmet`, `main_hand`, `off_hand`, `potions`, `cooldown_1`, `cooldown_2`, `cooldown_3`, `cooldown_4`, `cooldown_5`, `cooldown_6`, `cooldown_7`, `cooldown_8`, `cooldown_9`, `cooldown_10`, `precision_active`, `relentless_active`, `gouge_active`, `counter_active`, `shieldbash_active`) VALUES ('{ctx.author.name}', '{ctx.guild.id}', 'rogue', 1, 0, 50, 150, 150, 20, 10, 10, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error creating character.")
                
            elif args[1].lower() == 'gambler':
                try:
                    cursor.execute(f"INSERT INTO `Characters` (`username`, `guild_id`, `class`, `level`, `exp`, `next_level_exp`, `max_hp`, `current_hp`, `dodge_chance`, `block_chance`, `crit_chance`, `hit_chance`, `main_hand_damage`, `off_hand_damage`, `gold`, `boots`, `legs`, `chest`, `gloves`, `helmet`, `main_hand`, `off_hand`, `potions`, `cooldown_1`, `cooldown_2`, `cooldown_3`, `cooldown_4`, `cooldown_5`, `cooldown_6`, `cooldown_7`, `cooldown_8`, `cooldown_9`, `cooldown_10`, `precision_active`, `relentless_active`, `gouge_active`, `counter_active`, `shieldbash_active`) VALUES ('{ctx.author.name}', '{ctx.guild.id}', 'gambler', 1, 0, 50, 150, 150, 15, 15, 10, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                except Exception as e:
                    print(e)
                    return await ctx.send("Error creating character.")
                
            await Character.character_info(self, ctx, cursor)
        
    async def delete_character(self, ctx, cursor):
        # Check if user already has a character
        try:
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")

            result = cursor.fetchone()
            if not result:
                return await ctx.send("You don't have a character to delete dumbass.")
        except Exception as e:
            print(e)
            return await ctx.send("Error checking for existing character.")

        # Delete character
        if result:
            try:
                cursor.execute(f"DELETE FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
                await ctx.send("Character deleted successfully.")
            except Exception as e:
                print(e)
                return await ctx.send("Error deleting character.")

async def setup(bot):
    await bot.add_cog(Character(bot))
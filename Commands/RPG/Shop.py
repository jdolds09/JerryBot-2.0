import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gold = 0
        self.boots = False
        self.legs = False
        self.chest = False
        self.gloves = False
        self.helmet = False
        self.weapon = False
        self.offhand = False
        self.is_rogue = False
        self.is_mage = False
        self.is_warrior = False
        self.is_hunter = False
        self.is_gambler = False
        self.current_boots = 0
        self.current_legs = 0
        self.current_chest = 0
        self.current_gloves = 0
        self.current_helmet = 0
        self.current_weapon = 0
        self.current_offhand = 0

    # Shop function
    @commands.command()
    async def shop(self, ctx, *args):
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
        
        # Get and set player info
        self.boots = False
        self.legs = False
        self.chest = False
        self.gloves = False
        self.helmet = False
        self.weapon = False
        self.offhand = False
        self.is_rogue = False
        self.is_mage = False
        self.is_warrior = False
        self.is_hunter = False
        self.is_gambler = False
        self.current_boots = result['boots']
        self.current_legs = result['legs']
        self.current_chest = result['chest']
        self.current_gloves = result['gloves']
        self.current_helmet = result['helmet']
        self.current_weapon = result['main_hand']
        self.current_offhand = result['off_hand']
        if result['class'] == 'rogue':
            self.is_rogue = True
        elif result['class'] == 'mage':
            self.is_mage = True
        elif result['class'] == 'warrior':
            self.is_warrior = True
        elif result['class'] == 'hunter':
            self.is_hunter = True
        elif result['class'] == 'gambler':
            self.is_gambler = True
        
        # Set player's gold
        self.gold = result['gold']
        
        # Display shop 
        if len(args) == 0:
            await Shop.display_shop(self, ctx)
        
        # Create a character
        elif "buy" in args[0].lower():
            await Shop.purchase_item(self, ctx, args, cursor)

        # Invalid argument after !shop command
        else:
            return await ctx.send("Invalid argument after !shop command.")

    # Display the shop
    async def display_shop(self, ctx):
        
        # Output shop info
        try:
            shop_picture = "shopkeep.jpeg"
            file_path = f"Images/{shop_picture}"
            picture = discord.File(file_path)
            await ctx.send(file=picture)
            await ctx.send("**Welcome to the shop!**")
            await ctx.send("=========================================")
            await ctx.send("**Health Potion** (Restores 100 HP) - 100 Gold - To purchase, type `!shop buy potion`")
            await ctx.send("------------------------------------------")
            await ctx.send("**🟩 Good Boots** (+20 Max HP) - 200 Gold - To purchase, type `!shop buy good boots`")
            await ctx.send("**🟩 Good Legs** (+20 Max HP) - 200 Gold - To purchase, type `!shop buy good legs`")
            await ctx.send("**🟩 Good Chest** (+20 Max HP) - 200 Gold - To purchase, type `!shop buy good chest`")
            await ctx.send("**🟩 Good Gloves** (+20 Max HP) - 200 Gold - To purchase, type `!shop buy good gloves`")
            await ctx.send("**🟩 Good Helmet** (+20 Max HP) - 200 Gold - To purchase, type `!shop buy good helmet`")
            await ctx.send("**🟩 Good Weapon** - 200 Gold - To purchase, type `!shop buy good weapon`")
            await ctx.send("**🟩 Good Off Hand** - 200 Gold - To purchase, type `!shop buy good offhand`")
            await ctx.send("------------------------------------------")
            await ctx.send("**🟦 Rare Boots** (+20 Max HP, 1% Dodge & Block Chance) - 400 Gold - To purchase, type `!shop buy rare boots`")
            await ctx.send("**🟦 Rare Legs** (+20 Max HP, 1% Dodge & Block Chance) - 400 Gold - To purchase, type `!shop buy rare legs`")
            await ctx.send("**🟦 Rare Chest** (+20 Max HP, 1% Dodge & Block Chance) - 400 Gold - To purchase, type `!shop buy rare chest`")
            await ctx.send("**🟦 Rare Gloves** (+20 Max HP, 1% Dodge & Block Chance) - 400 Gold - To purchase, type `!shop buy rare gloves`")
            await ctx.send("**🟦 Rare Helmet** (+20 Max HP, 1% Dodge & Block Chance) - 400 Gold - To purchase, type `!shop buy rare helmet`")
            await ctx.send("**🟦 Rare Weapon** - 400 Gold - To purchase, type `!shop buy rare weapon`")
            await ctx.send("**🟦 Rare Off Hand** - 400 Gold - To purchase, type `!shop buy rare offhand`")
            await ctx.send("------------------------------------------")
            await ctx.send("**🟪 Epic Boots** (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance) - 600 Gold - To purchase, type `!shop buy epic boots`")
            await ctx.send("**🟪 Epic Legs** (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance) - 600 Gold - To purchase, type `!shop buy epic legs`")
            await ctx.send("**🟪 Epic Chest** (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance) - 600 Gold - To purchase, type `!shop buy epic chest`")
            await ctx.send("**🟪 Epic Gloves** (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance) - 600 Gold - To purchase, type `!shop buy epic gloves`")
            await ctx.send("**🟪 Epic Helmet** (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance) - 600 Gold - To purchase, type `!shop buy epic helmet`")
            await ctx.send("**🟪 Epic Weapon** - 600 Gold - To purchase, type `!shop buy epic weapon`")
            await ctx.send("**🟪 Epic Off Hand** - 600 Gold - To purchase, type `!shop buy epic offhand`")
            await ctx.send("------------------------------------------")

        except Exception as e:
            print(e)
            return await ctx.send("Error displaying shop.")


    # Create character function
    async def purchase_item(self, ctx, args, cursor):
        # User wants to buy a health potion
        if "potion" in args[1].lower():
            # Check if user has enough gold
            if self.gold < 100:
                return await ctx.send("You don't have enough gold to buy a Health Potion dumbass.")
            else:
                cursor.execute(f"UPDATE Characters SET gold = gold - 100 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                cursor.execute(f"UPDATE Characters SET potions = potions + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                await ctx.send("You bought a Health Potion!")

        # User wants to buy a good piece of gear
        elif "good" in args[1].lower():
            # Check if user has enough gold
            if self.gold < 200:
                return await ctx.send("You don't have enough gold to buy a Good piece of gear dumbass.")
            else:
                # Player wants to buy good boots
                if "boots" in args[2].lower():
                    if self.current_boots > 2:
                        return await ctx.send("You already have better boots equipped dumbass.")
                    elif self.current_boots == 2:
                        return await ctx.send("You already have these boots equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True

                # Player wants to buy good legs
                elif "legs" in args[2].lower() or "pants" in args[2].lower():
                    if self.current_legs > 2:
                        return await ctx.send("You already have better legs equipped dumbass.")
                    elif self.current_legs == 2:
                        return await ctx.send("You already have these legs equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True

                # Player wants to buy good chest
                elif "chest" in args[2 ].lower():
                    if self.current_chest > 2:
                        return await ctx.send("You already have a better chest equipped dumbass.")
                    elif self.current_chest == 2:
                        return await ctx.send("You already have this chest equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True

                # Player wants to buy good gloves
                elif "gloves" in args[2].lower():
                    if self.current_gloves > 2:
                        return await ctx.send("You already have better gloves equipped dumbass.")
                    elif self.current_gloves == 2:
                        return await ctx.send("You already have these gloves equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True

                # Player wants to buy good helmet
                elif "helm" in args[2].lower():
                    if self.current_helmet > 2:
                        return await ctx.send("You already have a better helmet equipped dumbass.")
                    elif self.current_helmet == 2:
                        return await ctx.send("You already have this helmet equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True

                # Player wants to buy a good weapon
                elif "weapon" in args[2].lower():
                    if self.current_weapon > 2:
                        return await ctx.send("You already have a better weapon equipped dumbass.")
                    elif self.current_weapon == 2:
                        return await ctx.send("You already have this weapon equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True

                # Player wants to buy a good offhand
                elif "offhand" in args[2].lower():
                    if self.current_offhand > 2:
                        return await ctx.send("You already have better offhand equipped dumbass.")
                    elif self.current_offhand == 2:
                        return await ctx.send("You already have this offhand equipped dumbass.")
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 200 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue or self.is_hunter or self.is_mage:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True
                    
                else:
                    return await ctx.send("Invalid item to buy dumbass.")

                # User with warrior character bought gear message
                if self.is_warrior:
                    if self.boots:
                        return await ctx.send("You bought the 🟩 Good Boots of Asskicking (+20 Max HP)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟩 Good Greaves of Asskicking (+20 Max HP)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟩 Good Chestplate of Asskicking (+20 Max HP)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟩 Good Gauntlets of Asskicking (+20 Max HP)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟩 Good Helmet of Asskicking (+20 Max HP)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟩 Good Sword of Asskicking (+5 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟩 Good Shield of Asskicking (+1% Block Chance)!")
                    
                # User with mage character bought gear message    
                elif self.is_mage:
                    if self.boots:
                        return await ctx.send("You bought the 🟩 Good Boots of Casting Spells and Shit (+20 Max HP)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟩 Good Pants of Casting Spells and Shit (+20 Max HP)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟩 Good Robes of Casting Spells and Shit (+20 Max HP)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟩 Good Gloves of Casting Spells and Shit (+20 Max HP)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟩 Good Hood of Casting Spells and Shit (+20 Max HP)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟩 Good Staff of Casting Spells and Shit (+5 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟩 Good Spellbook of Casting Spells and Shit (+1 Damage)!")

                # User with rogue character bought gear message          
                elif self.is_rogue:
                    if self.boots:
                        return await ctx.send("You bought the 🟩 Good Boots of Shanking (+20 Max HP)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟩 Good Pants of Shanking (+20 Max HP)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟩 Good Vest of Shanking (+20 Max HP)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟩 Good Gloves of Shanking (+20 Max HP)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟩 Good Hood of Shanking (+20 Max HP)!")
                    elif self.weapon or self.offhand:
                        return await ctx.send("You bought the 🟩 Good Dagger of Shanking (+1 Damage)!")
                    
                # User with hunter character bought gear message
                elif self.is_hunter:
                    if self.boots:
                        return await ctx.send("You bought the 🟩 Good Boots of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟩 Good Pants of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟩 Good Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟩 Good Gloves of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟩 Good Hood of Shooting Motherfuckers with Arrows (+20 Max HP)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟩 Good Bow of Shooting Motherfuckers with Arrows (+5 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟩 Good Quiver of Shooting Motherfuckers with Arrows (+1 Damage)!")
                
                # User with gambler character bought gear message
                elif self.is_gambler:
                    if self.boots:
                        return await ctx.send("You bought the 🟩 Good Boots of Luck (+20 Max HP)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟩 Good Pants of Luck (+20 Max HP)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟩 Good Jacket of Luck (+20 Max HP)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟩 Good Gloves of Luck (+20 Max HP)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟩 Good Fedora of Luck (+20 Max HP)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟩 Good Trinket of Luck (+5% Chance of Success)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟩 Good Charm of Luck (+1% Chance of Success)!")


        # User wants to buy a rare piece of gear
        elif "rare" in args[1].lower():
            # Check if user has enough gold
            if self.gold < 400:
                return await ctx.send("You don't have enough gold to buy a Rare piece of gear dumbass.")
            else:
                # Player wants to buy rare boots
                if "boots" in args[2].lower():
                    if self.current_boots > 3:
                        return await ctx.send("You already have better boots equipped dumbass.")
                    elif self.current_boots == 3:
                        return await ctx.send("You already have these boots equipped dumbass.")
                    elif self.current_boots == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True

                # Player wants to buy rare legs
                elif "legs" in args[2].lower() or "pants" in args[2].lower():
                    if self.current_legs > 3:
                        return await ctx.send("You already have better legs equipped dumbass.")
                    elif self.current_legs == 3:
                        return await ctx.send("You already have these legs equipped dumbass.")
                    elif self.current_legs == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True

                # Player wants to buy rare chest
                elif "chest" in args[2].lower():
                    if self.current_chest > 3:
                        return await ctx.send("You already have a better chest equipped dumbass.")
                    elif self.current_chest == 3:
                        return await ctx.send("You already have this chest equipped dumbass.")
                    elif self.current_chest == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True

                # Player wants to buy rare gloves
                elif "gloves" in args[2].lower():
                    if self.current_gloves > 3:
                        return await ctx.send("You already have better gloves equipped dumbass.")
                    elif self.current_gloves == 3:
                        return await ctx.send("You already have these gloves equipped dumbass.")
                    elif self.current_gloves == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True

                # Player wants to buy rare helmet
                elif "helm" in args[2].lower():
                    if self.current_helmet > 3:
                        return await ctx.send("You already have better helmet equipped dumbass.")
                    elif self.current_helmet == 3:
                        return await ctx.send("You already have this helmet equipped dumbass.")
                    elif self.current_helmet == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True

                # Player wants to buy a rare weapon
                elif "weapon" in args[2].lower():
                    if self.current_weapon > 3:
                        return await ctx.send("You already have a better weapon equipped dumbass.")
                    elif self.current_weapon == 3:
                        return await ctx.send("You already have this weapon equipped dumbass.")
                    elif self.current_weapon == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 10 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True

                # Player wants to buy a rare offhand
                elif "offhand" in args[2].lower():
                    if self.current_offhand > 3:
                        return await ctx.send("You already have a better offhand equipped dumbass.")
                    elif self.current_offhand == 3:
                        return await ctx.send("You already have this offhand equipped dumbass.")
                    elif self.current_offhand == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_mage or self.is_hunter:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 400 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_mage or self.is_hunter:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True

                else:
                    return await ctx.send("Invalid item to buy dumbass.")    

                # User with warrior character bought gear message
                if self.is_warrior:
                    if self.boots:
                        return await ctx.send("You bought the 🟦 Rare Boots of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟦 Rare Greaves of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟦 Rare Chestplate of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟦 Rare Gauntlets of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟦 Rare Helmet of Asskicking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟦 Rare Sword of Asskicking (+10 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟦 Rare Shield of Asskicking (+3% Block Chance)!")
                    
                # User with mage character bought gear message    
                elif self.is_mage:
                    if self.boots:
                        return await ctx.send("You bought the 🟦 Rare Boots of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟦 Rare Pants of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟦 Rare Robes of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟦 Rare Gloves of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟦 Rare Hood of Casting Spells and Shit (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟦 Rare Staff of Casting Spells and Shit (+10 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟦 Rare Spellbook of Casting Spells and Shit (+2 Damage)!")

                # User with rogue character bought gear message          
                elif self.is_rogue:
                    if self.boots:
                        return await ctx.send("You bought the 🟦 Rare Boots of Shanking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟦 Rare Pants of Shanking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟦 Rare Vest of Shanking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟦 Rare Gloves of Shanking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟦 Rare Hood of Shanking (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.weapon or self.offhand:
                        return await ctx.send("You bought the 🟦 Rare Dagger of Shanking (+3 Damage)!")
                    
                # User with hunter character bought gear message
                elif self.is_hunter:
                    if self.boots:
                        return await ctx.send("You bought the 🟦 Rare Boots of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟦 Rare Pants of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟦 Rare Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟦 Rare Gloves of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟦 Rare Hood of Shooting Motherfuckers with Arrows (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟦 Rare Bow of Shooting Motherfuckers with Arrows (+10 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟦 Rare Quiver of Shooting Motherfuckers with Arrows (+2 Damage)!")
                
                # User with gambler character bought gear message
                elif self.is_gambler:
                    if self.boots:
                        return await ctx.send("You bought the 🟦 Rare Boots of Luck (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟦 Rare Pants of Luck (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟦 Rare Jacket of Luck (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟦 Rare Gloves of Luck (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟦 Rare Fedora of Luck (+20 Max HP, +1% Dodge & Block Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟦 Rare Trinket of Luck (+10% Chance of Success)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟦 Rare Charm of Luck (+2% Chance of Success)!")
                    
        # User wants to buy a epic piece of gear
        elif "epic" in args[1].lower():
            # Check if user has enough gold
            if self.gold < 600:
                return await ctx.send("You don't have enough gold to buy an Epic piece of gear dumbass.")
            else:
                # Player wants to buy epic boots
                if "boots" in args[2].lower():
                    if self.current_boots > 4:
                        return await ctx.send("You already have better boots equipped dumbass.")
                    elif self.current_boots == 4:
                        return await ctx.send("You already have these boots equipped dumbass.")
                    elif self.current_boots == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True
                    elif self.current_boots == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET boots = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.boots = True

                # Player wants to buy epic legs
                elif "legs" in args[2].lower() or "pants" in args[2].lower():
                    if self.current_legs > 4:
                        return await ctx.send("You already have better legs equipped dumbass.")
                    elif self.current_legs == 4:
                        return await ctx.send("You already have these legs equipped dumbass.")
                    elif self.current_legs == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True
                    elif self.current_legs == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET legs = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.legs = True

                # Player wants to buy epic chest
                elif "chest" in args[2].lower():
                    if self.current_chest > 4:
                        return await ctx.send("You already have a better chest equipped dumbass.")
                    elif self.current_chest == 4:
                        return await ctx.send("You already have this chest equipped dumbass.")
                    elif self.current_chest == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True
                    elif self.current_chest == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET chest = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.chest = True

                # Player wants to buy epic gloves
                elif "gloves" in args[2].lower():
                    if self.current_gloves > 4:
                        return await ctx.send("You already have better gloves equipped dumbass.")
                    elif self.current_gloves == 4:
                        return await ctx.send("You already have these gloves equipped dumbass.")
                    elif self.current_gloves == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True
                    elif self.current_gloves == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET gloves = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.gloves = True
                        
                # Player wants to buy epic helmet
                elif "helm" in args[2].lower():
                    if self.current_helmet > 4:
                        return await ctx.send("You already have better helmet equipped dumbass.")
                    elif self.current_helmet == 4:
                        return await ctx.send("You already have this helmet equipped dumbass.")
                    elif self.current_helmet == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True
                    elif self.current_helmet == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET helmet = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET max_hp = max_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET dodge_chance = dodge_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET crit_chance = crit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.helmet = True

                # Player wants to buy an epic weapon
                elif "weapon" in args[2].lower():
                    if self.current_weapon > 4:
                        return await ctx.send("You already have a better weapon equipped dumbass.")
                    elif self.current_weapon == 4:
                        return await ctx.send("You already have this weapon equipped dumbass.")
                    elif self.current_weapon == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True
                    elif self.current_weapon == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 10 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 20 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET main_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_gambler:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 15 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET main_hand_damage = main_hand_damage + 15 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.weapon = True

                # Player wants to buy an epic offhand
                elif "offhand" in args[2].lower():
                    if self.current_offhand > 4:
                        return await ctx.send("You already have a better offhand equipped dumbass.")
                    elif self.current_offhand == 4:
                        return await ctx.send("You already have this offhand equipped dumbass.")
                    elif self.current_offhand == 3:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_mage or self.is_hunter:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 1 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True
                    elif self.current_offhand == 2:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_mage or self.is_hunter:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 2 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True
                    else:
                        cursor.execute(f"UPDATE Characters SET gold = gold - 600 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        cursor.execute(f"UPDATE Characters SET off_hand = 4 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        if self.is_rogue:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_mage or self.is_hunter:
                            cursor.execute(f"UPDATE Characters SET off_hand_damage = off_hand_damage + 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        elif self.is_warrior:
                            cursor.execute(f"UPDATE Characters SET block_chance = block_chance + 5 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        else:
                            cursor.execute(f"UPDATE Characters SET hit_chance = hit_chance + 3 WHERE username = '{ctx.author.name}' and guild_id = '{ctx.guild.id}'")
                        self.offhand = True

                else:
                    return await ctx.send("Invalid item to buy dumbass.")

                # User with warrior character bought gear message
                if self.is_warrior:
                    if self.boots:
                        return await ctx.send("You bought the 🟪 Epic Boots of Asskicking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟪 Epic Greaves of Asskicking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟪 Epic Chestplate of Asskicking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟪 Epic Gauntlets of Asskicking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟪 Epic Helmet of Asskicking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟪 Epic Sword of Asskicking (+15 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟪 Epic Shield of Asskicking (+5% Block Chance)!")

                # User with mage character bought gear message    
                elif self.is_mage:
                    if self.boots:
                        return await ctx.send("You bought the 🟪 Epic Boots of Casting Spells and Shit (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟪 Epic Pants of Casting Spells and Shit (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟪 Epic Robes of Casting Spells and Shit (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟪 Epic Gloves of Casting Spells and Shit (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟪 Epic Hood of Casting Spells and Shit (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟪 Epic Staff of Casting Spells and Shit (+15 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟪 Epic Spellbook of Casting Spells and Shit (+3 Damage)!")

                # User with rogue character bought gear message          
                elif self.is_rogue:
                    if self.boots:
                        return await ctx.send("You bought the 🟪 Epic Boots of Shanking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟪 Epic Pants of Shanking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟪 Epic Vest of Shanking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟪 Epic Gloves of Shanking (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.weapon or self.offhand:
                        return await ctx.send("You bought the 🟪 Epic Dagger of Shanking (+5 Damage)!")
                    
                # User with hunter character bought gear message
                elif self.is_hunter:
                    if self.boots:
                        return await ctx.send("You bought the 🟪 Epic Boots of Shooting Motherfuckers with Arrows (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟪 Epic Pants of Shooting Motherfuckers with Arrows (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟪 Epic Chainmail of Shooting Motherfuckers with Arrows (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟪 Epic Gloves of Shooting Motherfuckers with Arrows (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟪 Epic Hood of Shooting Motherfuckers with Arrows (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟪 Epic Bow of Shooting Motherfuckers with Arrows (+15 Damage)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟪 Epic Quiver of Shooting Motherfuckers with Arrows (+3 Damage)!")

                # User with gambler character bought gear message
                elif self.is_gambler:
                    if self.boots:
                        return await ctx.send("You bought the 🟪 Epic Boots of Luck (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.legs:
                        return await ctx.send("You bought the 🟪 Epic Pants of Luck (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.chest:
                        return await ctx.send("You bought the 🟪 Epic Jacket of Luck (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.gloves:
                        return await ctx.send("You bought the 🟪 Epic Gloves of Luck (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.helmet:
                        return await ctx.send("You bought the 🟪 Epic Fedora of Luck (+20 Max HP, 1% Dodge & Block Chance, 1% Crit Chance)!")
                    elif self.weapon:
                        return await ctx.send("You bought the 🟪 Epic Trinket of Luck (+15% Chance of Success)!")
                    elif self.offhand:
                        return await ctx.send("You bought the 🟪 Epic Charm of Luck (+3% Chance of Success)!")
                    
        # User didn't format the input correctly
        else:
            return await ctx.send("Need to specify a valid rarity to buy dumbass.")

async def setup(bot):
    await bot.add_cog(Shop(bot))
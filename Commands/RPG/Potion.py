import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

class Potion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Potion function
    @commands.command(aliases=['use'])
    async def potion(self, ctx, *args):
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
        
        # Fetch user's level and exp
        try:
            cursor.execute(f"SELECT * FROM `Characters` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")

            result = cursor.fetchone()
            # User doesn't have a character
            if not result:
                return await ctx.send("You don't have a character dumbass.")
            
        except Exception as e:
            print(e)
            return await ctx.send("Error grabbing character details")
        
        # User doesn't have a potion
        if result['potions'] <= 0:
            return await ctx.send("You don't have any potions left.")
        
        battle_cog = self.bot.get_cog("Battle")
        if not battle_cog.encounter or not battle_cog.encounter[ctx.guild.id]['active_battle']:
            return await ctx.send("There is no active battle dumbass.")
        
        if result['current_hp'] + 100 > result['max_hp']:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = max_hp WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"UPDATE Characters SET potions = potions - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                await ctx.send(f"{ctx.author.name} used a potion!")
                return await ctx.send(f"{result['username']}'s HP: {result['max_hp']}/{result['max_hp']}")
            except Exception as e:
                print(e)
                return await ctx.send("Error using potion.")
        else:
            try:
                cursor.execute(f"UPDATE Characters SET current_hp = current_hp + 100 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                cursor.execute(f"UPDATE Characters SET potions = potions - 1 WHERE username = '{ctx.author.name}' AND guild_id = '{ctx.guild.id}'")
                await ctx.send(f"{ctx.author.name} used a potion!")
                return await ctx.send(f"{result['username']}'s HP: {result['current_hp'] + 100}/{result['max_hp']}")
            except Exception as e:
                print(e)
                return await ctx.send("Error using potion.") 
  
async def setup(bot):
    await bot.add_cog(Potion(bot))
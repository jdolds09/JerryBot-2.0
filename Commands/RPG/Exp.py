import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Exp function
    @commands.command(aliases=['experience', 'xp', 'level', 'lvl'])
    async def exp(self, ctx, *args):
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
        
        await ctx.send(f"**__{ctx.author.name}'s Level:__** {result['level']}")
        return await ctx.send(f"**__EXP:__** {result['exp']}/{result['next_level_exp']}")
  
async def setup(bot):
    await bot.add_cog(Exp(bot))
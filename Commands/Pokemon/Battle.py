import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Battle function
    @commands.command()
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

        # Fetch user's trainer
        try:
            cursor.execute(f"SELECT * FROM `Trainers` WHERE `username` = '{ctx.author.name}' AND `guild_id` = '{ctx.guild.id}'")
            result = cursor.fetchone()
            # User doesn't have a trainer
            if not result:
                return await ctx.send("You don't have a trainer dumbass.")
            
        except Exception as e:
            print(e)
            return await ctx.send("Error grabbing trainer details")

async def setup(bot):
    await bot.add_cog(Battle(bot))
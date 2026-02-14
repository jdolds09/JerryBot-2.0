import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os


class Gear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gear function
    @commands.command()
    async def gear(self, ctx):
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

        character_cog = self.bot.get_cog("Character")
        await character_cog.character_info(ctx, cursor)

async def setup(bot):
    await bot.add_cog(Gear(bot))
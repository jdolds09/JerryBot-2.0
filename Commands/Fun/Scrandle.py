import discord
from discord.ext import commands
import requests
import random
import os
from dotenv import load_dotenv

class Scrandle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Scrandle function
    @commands.command(aliases=[])
    async def scrandle(self, ctx):

        # Reaction emojis
        num_reactions = ["1️⃣", "2️⃣"]

        # Subreddits we are going to scrape
        subreddits = ["FoodPorn", "food", "burgers", "Pizza", "eatsandwiches", "tonightsdinner", "southernfood",
                      "DessertPorn", "BBQ", "appetizers", "mexicanfood", "FoodPics", "Sandwiches", "desserts", "cheeseburgers",
                      "tacos", "sushi", "steak", "pasta", "Bbqporn", "Breakfast"]

        search_modes = ["new", "top", "hot", "best"]
        # If the "top" search mode is randomly selected, we need to also specify the time range
        top_search_modes = ["hour", "day", "week", "month", "year", "all"]
        # This will hold all the image urls we are able to scrape from the JSON file
        image_urls = None

        i = 1

        # Post 2 images
        for _ in range(2):
            await ctx.send(f"**{i}**")
            i += 1

            while image_urls is None or len(image_urls) == 0:
                # choose a random subreddit and search mode
                subreddit = random.choice(subreddits)
                search_mode = random.choice(search_modes)

                # If the "top" search mode was randomly selected, randomly select the time range and set the search_url
                if search_mode == "top":
                    top_search_mode = random.choice(top_search_modes)
                    search_url = f"https://reddit.com/r/{subreddit}/top.json?t={top_search_mode}"

                # All other search modes other than "top"
                else:
                    search_url = f"https://reddit.com/r/{subreddit}/{search_mode}.json"


                # Get JSON data
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WIN64; x64) AppleWebKit/537.36'}
                try:
                    response = requests.get(search_url, headers=headers, timeout=60)
                except Exception as e:
                    print(e)
                data = response.json().get("data", {})
                children = data.get("children", [])

                # Scrape image URLs
                for child in children:
                    post = child["data"]
                    image_urls.append(post.get("url"))

                # Randomly select an image url from the list
                image = random.choice(image_urls)
                image_string = f"{image}"

                # If image is in preview or gallery format, remove from list and select another url
                if image_urls and ("preview" in image_string or "gallery" in image_string):
                    image_urls.remove(image)
                    image = random.choice(image_urls)
                    image_string = f"{image}"

                if image_urls and ("jpeg" not in image_string and "jpg" not in image_string and "png" not in image_string and "gif" not in image_string):
                    image_urls.remove(image)
                    image = random.choice(image_urls)
                    image_string = f"{image}"

            # Post the image
            if image_string:
                await ctx.send(image_string)
            else:
                await ctx.send("Unable to fetch image.")

        # Create a poll for people to choose between the two images
        embed = discord.Embed(title=f"**CHOOSE 1 OR 2**", color=0x0000FF)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction(num_reactions[0])
        await poll_message.add_reaction(num_reactions[1])

    async def command_help(self, ctx):
        await ctx.send("**!scrandle**: Posts an ass pic/gif.")

async def setup(bot):
    await bot.add_cog(Scrandle(bot))
import discord
from discord.ext import commands
import requests
import random

class Boobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Boobs function
    @commands.command(aliases=['tits', 'boob', 'boobies', 'titties', 'titty'])
    async def boobs(self, ctx):
        # Return if not in a NSFW channel
        if not ctx.channel.is_nsfw():
            return await ctx.send("You must be in a NSFW channel dumbass.")

        # Subreddits we are going to scrape
        subreddits = [
            "Boobies", "tits", "boobs", "PerfectTits", "adorableporn", "amazingtits", "topless", "fortyfivefiftyfive", "BustyPetite",
            "Titties", "NSFWfashion", "Playboy", "bodyperfection", "Nudes", "Nude_Selfie", "BestTits",
            "boobbounce", "TittyDrop", "CasualJiggles", "stripgirls", "BiggerThanYouThought"
        ]

        search_modes = ["new", "top", "hot", "best"]
        # If the "top" search mode is randomly selected, we need to also specify the time range
        top_search_modes = ["hour", "day", "week", "month", "year", "all"]
        # This will hold all the image urls we are able to scrape from the JSON file
        image_urls = []

        while len(image_urls) == 0:
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
            while "preview" in image_string or "gallery" in image_string:
                if len(image_urls) > 0:
                    image_urls.remove(image)
                    image = random.choice(image_urls)
                    image_string = f"{image}"

            while "jpeg" not in image_string and "jpg" not in image_string and "png" not in image_string and "gif" not in image_string:
                if len(image_urls) > 0:
                    image_urls.remove(image)
                    image = random.choice(image_urls)
                    image_string = f"{image}"
                else:
                    break

        # Post the image
        if image_string:
            await ctx.send(image_string)
        else:
            await ctx.send("Unable to fetch image.")

    async def command_help(self, ctx):
        await ctx.send("**!boobs**: Posts a boobs pic/gif.")

async def setup(bot):
    await bot.add_cog(Boobs(bot))
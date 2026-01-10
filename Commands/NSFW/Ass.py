import discord
from discord.ext import commands
import requests
import random

class Ass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Rock function
    @commands.command(aliases=['butt', 'butts'])
    async def ass(self, ctx):
        # Return if not in a NSFW channel
        if not ctx.channel.is_nsfw():
            await ctx.send("You must be in a NSFW channel dumbass.")

        # Subreddits we are going to scrape
        subreddits = [
            "ass", "butt", "cosplaybutts",
            "girlsinyogapants", "smalltitsbigass", "booty",
            "WhiteCheeks", "HungryButts", "beautifulbutt",
            "pawg", "asstastic","CuteLittleButts", "bootypetite",
            "PantyPeel","tightsqueeze", "twerking", "twerk"
        ]

        search_modes = ["new", "top", "hot", "best"]
        image_urls = []

        #choose a random subreddit and search mode
        subreddit = random.choice(subreddits)
        search_mode = random.choice(search_modes)
        search_url = f"https://reddit.com/r/{subreddit}/{search_mode}.json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WIN64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=60)
        data = response.json().get("data", {})
        children = data.get("children", [])

        for child in children:
            post = child["data"]
            image_urls.append(post.get("url_overriden_by_dest", post.get("url")))

        image = random.choice(image_urls)
        image_string = f"{image}"
        while "preview" in image_string or "gallery" in image_string:
            image_urls.remove(image)
            image = random.choice(image_urls)
            image_string = f"{image}"

        if image_string:
            await ctx.send(image_string)
        else:
            await ctx.send("Unable to fetch image.")

    async def command_help(self, ctx):
        await ctx.send("**!ass**: Posts an ass pic/gif.")

async def setup(bot):
    await bot.add_cog(Ass(bot))
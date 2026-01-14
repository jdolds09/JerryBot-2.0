import discord
from discord.ext import commands
import requests
import random

class Porn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Porn function
    @commands.command()
    async def porn(self, ctx):
        # Return if not in a NSFW channel
        if not ctx.channel.is_nsfw():
            return await ctx.send("You must be in a NSFW channel dumbass.")

        # Subreddits we are going to scrape
        subreddits = [
            "gonewild", "nsfw", "NSFW_GIF", "RealGirls", "cumsluts", "nsfw_gifs", "GirlsFinishingTheJob", "porninfifteenseconds",
        "60fpsporn", "FunWithFriends", "Blowjobs", "edging", "porn", "Facials", "collegesluts", "LegalTeens", "Amateur",
        "TooCuteForPorn", "gifsgonewild", "18_19", "porn_gifs", "CollegeAmateurs", "RuinedOrgasms","amateurcumsluts", "AmateurPorn"]

        search_modes = ["new", "top", "hot", "best"]
        # If the "top" search mode is randomly selected, we need to also specify the time range
        top_search_modes = ["hour", "day", "week", "month", "year", "all"]
        # This will hold all the image urls we are able to scrape from the JSON file
        image_urls = []
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
        proxies = {'http': 'http://ekfdieif:vvc1rdkpv2bg@142.111.48.253:7030'}
        try:
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=60)
        except Exception as e:
            print(e)
        data = response.json().get("data", {})
        children = data.get("children", [])

        # Scrape image URLs
        for child in children:
            post = child["data"]
            image_urls.append(post.get("url_overriden_by_dest", post.get("url")))

        # Randomly select an image url from the list
        image = random.choice(image_urls)
        image_string = f"{image}"
        # If image is in preview or gallery format, remove from list and select another url
        while "preview" in image_string or "gallery" in image_string:
            image_urls.remove(image)
            image = random.choice(image_urls)
            image_string = f"{image}"
        # Post the image
        if image_string:
            await ctx.send(image_string)
        else:
            await ctx.send("Unable to fetch image.")

    async def command_help(self, ctx):
        await ctx.send("**!porn**: Posts a porn pic/gif.")

async def setup(bot):
    await bot.add_cog(Porn(bot))
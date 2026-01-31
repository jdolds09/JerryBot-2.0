import discord
from discord.ext import commands, tasks
import requests
import random

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running_tasks = {}

    # Schedule function
    @commands.command()
    async def schedule(self, ctx, *, message=None):
        # Return if not in a NSFW channel
        if not ctx.channel.is_nsfw():
            return await ctx.send("You must be in a NSFW channel dumbass.")

        if message is not None:
            if 'stop' in message.lower():
                return await Schedule.stop_task(self, ctx)

        if ctx.guild.id in self.running_tasks and not self.running_tasks[ctx.guild.id].done():
            await ctx.send("Schedule command is already running dumbass.")
            return await ctx.send("Please use **!schedule stop** and then **!schedule** to restart the task.")

        self.running_tasks[ctx.guild.id] = Schedule.post_images.start(self, ctx)

    @tasks.loop(hours=2)
    async def post_images(self, ctx):
        # Subreddits we are going to scrape
        subreddits = ["ass", "butt", "cosplaybutts","girlsinyogapants", "smalltitsbigass", "booty", "WhiteCheeks", "HungryButts", "beautifulbutt",
            "pawg", "asstastic","CuteLittleButts", "bootypetite", "PantyPeel","tightsqueeze", "twerking", "twerk", "Boobies", "tits", "boobs",
            "PerfectTits", "adorableporn", "amazingtits", "topless", "fortyfivefiftyfive", "BustyPetite", "Titties", "NSFWfashion", "Playboy",
            "bodyperfection", "Nudes", "Nude_Selfie", "BestTits", "boobbounce", "TittyDrop", "CasualJiggles", "stripgirls", "BiggerThanYouThought",
            "cosplaygirls", "cosplay", "cosplaybabes", "CosplayLewd", "nsfwcosplay", "geekygirls", "cosplaybutts", "suicidegirls", "cameltoe", "Innie",
            "vagina", "Innies", "GodPussy", "shavedpussies", "simps", "rearpussy", "gonewild", "FunWithFriends", "TooCuteForPorn", "RealGirls"]

        for _ in range(20):
            try:
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
                response = requests.get(search_url, headers=headers, timeout=60)
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
                    image_urls.remove(image)
                    if not image_urls:
                        data = response.json().get("data", {})
                        children = data.get("children", [])
                        for child in children:
                            post = child["data"]
                            image_urls.append(post.get("url"))

                    image = random.choice(image_urls)
                    image_string = f"{image}"
                # Post the image
                if image_string:
                    await ctx.send(image_string)
                else:
                    await ctx.send("Unable to fetch image.")
            except Exception as e:
                print(e)

    async def stop_task(self, ctx):
        if ctx.guild.id in self.running_tasks:
            self.running_tasks[ctx.guild.id].cancel()
            del self.running_tasks[ctx.guild.id]
            return await ctx.send("Task stopped.")
        else:
            return await ctx.send("Task is not running dumbass.")

    async def command_help(self, ctx):
        await ctx.send("**!schedule OPTIONAL: [stop]**: Fetches images from reddit every 2 hours. **!schedule stop** will stop the task.")

async def setup(bot):
    await bot.add_cog(Schedule(bot))
import discord
from discord.ext import commands
import yt_dlp

YDL_PLAYLIST_OPTIONS = {'format': 'bestaudio', 'noplaylist' : False, 'no_warnings': True, 'skip_download': True, 'ignoreerrors': True, 'extract_flat': 'in_playlist', 'force_generic_extractor': True}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist' : True, 'ignoreerrors': True, 'no_warnings': True}
FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",'options' : '-vn -c:a pcm_s16le'}

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.titles = {}
        self.webpage_urls = {}

    @commands.command()
    async def play(self, ctx, *args):
        # Check to see if user is in a voice channel
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel to use this command dumbass.")
        # User didn't enter anything after !play command
        if len(args) == 0:
            return await ctx.send("You need to enter something to play dumbass.")

        args = " ".join(args)

        # Need these two lists to keep track and display song titles and the YouTube URLs
        # Also need to add ctx.guild.id to keep each discord server song queue info separate
        self.titles[ctx.guild.id] = []
        self.webpage_urls[ctx.guild.id] = []

        # User entered a YouTube Playlist link
        if args.startswith("https://www.youtube.com/playlist"):
            args = await Play.searchPlaylist(self, ctx, args, self.titles[ctx.guild.id], self.webpage_urls[ctx.guild.id])
            if args is None:
                return await ctx.send("Invalid playlist link.")

        # User entered a YouTube video link
        elif args.startswith("https://www.youtube.com/watch"):
            # Find the YouTube video and get the metadata
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{args}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                        self.titles[ctx.guild.id].append(info["title"])
                        self.webpage_urls[ctx.guild.id].append(info["webpage_url"])
                        args = info['url']
                    else:
                        return await ctx.send("The YouTube link is invalid!")
            except Exception as e:
                print(e)

        # User entered a query
        else:
            args = await Play.searchQuery(self, ctx, args, self.titles[ctx.guild.id], self.webpage_urls[ctx.guild.id])
            if args is None:
                return await ctx.send("Unable to find a match to your query.")

        # Send search results to be added to the music queue
        await Play.addTrack(self, ctx, args, self.titles[ctx.guild.id], self.webpage_urls[ctx.guild.id])

    # User entered a query, this function will extract YouTube video title, url, and webpage url
    # based on user query (yes the url and webpage url is different. FFMPEG requires a different
    # URL than the webpage url to work)
    async def searchQuery(self, ctx, args, titles, urls):
        # Get a YouTube metadata from user's query
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            url = None
            info_dictionary = ydl.extract_info(f"ytsearch:{args}", download=False)
            if 'entries' in info_dictionary:
                info = info_dictionary['entries'][0]
                titles.append(info["title"])
                urls.append(info["webpage_url"])
                url = info['url']
        return url

    async def searchPlaylist(self, ctx, args, titles, urls):
        playlist_tracks = {ctx.guild.id: []}
        # Get YouTube links from a playlist link.
        with yt_dlp.YoutubeDL(YDL_PLAYLIST_OPTIONS) as ydl:
            try:
                # extract_info returns a dictionary with metadata
                info_dictionary = ydl.extract_info(args, download=False)
                # Extract the titles and webpage urls from each individual video in the playlist.
                # For playlists, url returns webpage url, not the url FFMPEG uses.
                if 'entries' in info_dictionary:
                    for entry in info_dictionary['entries']:
                        if entry:
                            playlist_tracks[ctx.guild.id].append(entry['url'])
                            titles.append(entry['title'])
                            urls.append(entry['url'])
                    return playlist_tracks[ctx.guild.id]
                else:
                    return None
            except Exception as e:
                print(e)
                return None

    async def addTrack(self, ctx, tracks, titles, webpage_urls):
        # Get guild id
        guild_id = ctx.guild.id
        # Create the server queue if it has not been created yet
        if guild_id not in self.queue:
            self.queue[guild_id] = []

        # If there is only one track
        if not isinstance(tracks, list):
            tracks = [tracks]

        # Bot is not connected to channel, connect the bot to channel and start filling the queue

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

            # Clear the queue
            try:
                self.queue[guild_id].clear()
            except Exception as e:
                print(e)

            # Fill the queue with requested song(s)
            for track in tracks:
                try:
                    self.queue[guild_id].append((track, titles.pop(0), webpage_urls.pop(0)))
                except Exception as e:
                    print(e)

            # Play the first song in the queue
            await Play.playTrack(self, ctx, self.queue[guild_id])

        # Bot is already connected to channel, add requested song(s) to queue
        else:
            if len(tracks) == 1 and ctx.voice_client.is_playing():
                await ctx.send(f"{titles[0]} added to the queue!")
            elif len(tracks) > 1 and ctx.voice_client.is_playing():
                await ctx.send("Songs have been added to the queue!")
            try:
                for track in tracks:
                    self.queue[guild_id].append((track, titles.pop(0), webpage_urls.pop(0)))
            except Exception as e:
                print(e)
            # If bot is currently not playing, play the first song added to queue
            if not ctx.voice_client.is_playing():
                await Play.playTrack(self, ctx, self.queue[guild_id])

    async def playTrack(self, ctx, tracks):
            if tracks:
                url, title, webpage_url = tracks.pop(0)

                # If we are getting playlist info, we must get URL that FFMPEG wants, not webpage url
                # Also display song from playlist that is playing
                if url.startswith("https://www.youtube.com"):
                    try:
                        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(f"ytsearch:{url}", download=False)
                            if 'entries' in info:
                                info = info['entries'][0]
                                await ctx.send(f"**__Now Playing:__** {info["title"]}")
                                await ctx.send(f"{url}")
                                url = info['url']
                    except Exception as e:
                        print(e)

                # Display non-playlist song that is currently playing
                else:
                    await ctx.send(f"**__Now Playing:__** {title}")
                    await ctx.send(f"{webpage_url}")

                # Play!
                try:
                    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                    ctx.voice_client.play(source, after=lambda _:self.bot.loop.create_task(self.playTrack(ctx, tracks)))
                except Exception as e:
                    print(e)

    async def command_help(self, ctx):
        await ctx.send("**!play [youtube video or playlist link] OR [just type something it will search youtube for it!]**: "
                       "Plays audio from a youtube video or youtube videos from a youtube playlist.")

async def setup(bot):
    await bot.add_cog(Play(bot))

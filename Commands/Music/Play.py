import discord
from discord.ext import commands
import yt_dlp

YDL_PLAYLIST_OPTIONS = {'format': 'bestaudio', 'noplaylist' : False, 'no_warnings': True, 'skip_download': True, 'ignoreerrors': True, 'extract_flat': 'in_playlist', 'force_generic_extractor': True}
YDL_OPTIONS = {'format' : 'bestaudio', 'noplaylist' : True, 'ignoreerrors': True, 'no_warnings': True}
FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",'options' : '-vn -c:a libopus -b:a 96k'}
VIDEO_OPTIONS = {'format' : 'bestaudio', 'ignoreerrors': True, 'no_warnings': True, 'skip_download': True}

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    @commands.command()
    async def play(self, ctx, *args):
        # Check to see if user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("You must be in a voice channel to use this command.")
            return
        args = " ".join(args)

        # User entered a YouTube Playlist link
        if args.startswith("https://www.youtube.com/playlist"):
            args = await Play.searchPlaylist(self, ctx, args)
            if args is None: return

        # User entered a YouTube video link
        elif args.startswith("https://www.youtube.com/watch"):
            # Find the YouTube video and get the metadata
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{args}", download=False)
                    args = None
                    if 'entries' in info:
                        info = info['entries'][0]
                        args = info['url']
            except Exception as e:
                print(e)
            if args is None:
                return await ctx.send("The YouTube link is invalid!")

        # Query
        else:
            args = await Play.searchQuery(self, ctx, args)
            if args is None:
                return await ctx.send("Unable to find a match to your query.")

        # Send search results to be added to the music queue
        await Play.addTrack(self, ctx, args)

    async def searchQuery(self, ctx, args):
        # Get a YouTube link from a query
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info_dictionary = ydl.extract_info(f"ytsearch:{args}", download=False)
            if 'entries' in info_dictionary:
                info = info_dictionary['entries'][0]
            url = info['url']
        return url

    async def searchPlaylist(self, ctx, args):
        playlist_tracks = []
        # Get YouTube links from a playlist link.
        with yt_dlp.YoutubeDL(YDL_PLAYLIST_OPTIONS) as ydl:
            try:
                # extract_info returns a dictionary with metadata
                info_dictionary = ydl.extract_info(args, download=False)
                # Extract the URLs from the list of playlist metadata
                if 'entries' in info_dictionary:
                    for entry in info_dictionary['entries']:
                        if entry:
                            playlist_tracks.append(entry['url'])
                    return playlist_tracks
                else:
                    return None
            except Exception as e:
                print(e)
                return None

    async def addTrack(self, ctx, tracks):
        # Get guild id
        guild_id = ctx.guild.id
        if guild_id not in self.queue:
            self.queue[guild_id] = []

        if ctx.author.voice is None: return
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
                    self.queue[guild_id].append(track)
                except Exception as e:
                    print(e)

            # Play the first song in the queue
            await Play.playTrack(self, ctx, self.queue[guild_id])

        # Bot is already connected to channel, add requested song(s) to queue
        else:
            try:
                for track in tracks:
                    self.queue[guild_id].append(track)
            except Exception as e:
                print(e)
            if not ctx.voice_client.is_playing():
                await Play.playTrack(self, ctx, self.queue[guild_id])

    async def playTrack(self, ctx, tracks):
            if tracks:
                url = tracks.pop(0)
                try:
                    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{url}", download=False)
                        if 'entries' in info:
                            info = info['entries'][0]
                            url = info['url']
                except Exception as e:
                    print(e)
                try:
                    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS, executable="bin\\ffmpeg\\ffmpeg.exe")
                except Exception as e:
                    print(e)
                ctx.voice_client.play(source, after=lambda _:self.bot.loop.create_task(self.playTrack(ctx, tracks)))

    async def command_help(self, ctx):
        await ctx.send("**!play [youtube video or playlist link] OR [just type something it will search youtube for it!]**: Plays audio from a youtube video or youtube videos from a youtube playlist.")

async def setup(bot):
    await bot.add_cog(Play(bot))

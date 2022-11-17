from time import time
from discord.ext import commands
import discord
import asyncio
import youtube_dl
from datetime import datetime
from pytz import timezone
import logging
import urllib.request
from ..video import Video
from ..playlist import Videoplaylist
from discord_slash import cog_ext, SlashContext


YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "yesplaylis": True,
    "extract_flat": "in_playlist"
}

# TODO: abstract FFMPEG options into their own file?
FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
"""
Command line options to pass to `ffmpeg` before the `-i`.

See https://stackoverflow.com/questions/43218292/youtubedl-read-error-with-discord-py/44490434#44490434 for more information.
Also, https://ffmpeg.org/ffmpeg-protocols.html for command line option reference.
"""


async def audio_playing(ctx):
    """Checks that audio is currently playing before continuing."""
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise commands.CommandError("Not currently playing any audio.")


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise commands.CommandError(
            "You need to be in the channel to do that.")


async def is_audio_requester(ctx):
    """Checks that the command sender is the song requester."""
    music = ctx.bot.get_cog("Music")
    state = music.get_state(ctx.guild)
    permissions = ctx.channel.permissions_for(ctx.author)
    if permissions.administrator or state.is_requester(ctx.author):
        return True
    else:
        raise commands.CommandError(
            "You need to be the song requester to do that.")
# change time zone
def timetz(*args):
    return datetime.now(tz).timetuple()

tz = timezone('Asia/Bangkok') 

logging.Formatter.converter = timetz
#time zone list https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

class Music(commands.Cog):
    """Bot commands to help play music."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[
            -1]]  # retrieve module name, find config entry
        self.states = {}

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

            

    @cog_ext.cog_slash(
        name="donate",
        description="Donate server charge."
    )
    async def _donate(self, ctx):
        emBed = discord.Embed(title="**Donate**",url="https://tmn.app.link/R1hfCx6fmub", description="ช่องทางการสนับสนุน", color=0xF3F4F9)
        emBed.add_field(name='1.True money', value='By this QR-CODE')
        emBed.set_image(url="https://cdn.discordapp.com/attachments/927083092479467550/1033698275615838218/MyQR_2022-10-23_17.52.20.jpg")
        emBed.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/1033702427892920331.gif")
        emBed.add_field(name='2.True money(Link)', value='Click the blue-title on top')
        await ctx.send(content=None, embed=emBed)

    @cog_ext.cog_slash(
        name="avatar",
        description="get user avater."
    )
    async def _avatar(self, ctx, member: discord.Member):
        await ctx.send(f'{str(member.avatar_url)}')

    @cog_ext.cog_slash(
        name="play-playlist",
        description="play playlist by url only."
    )
    async def _playplaylist(self, ctx, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)  # get the guild's state
        channel = discord.VoiceChannel = None
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        fullstring = url
        substring = "https://www.youtube.com/playlist"
        try:
            if substring in fullstring:
                pass
            else:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='This is not a playlist url.')
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return
        except:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='This is not a playlist url.')
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return
        status_code = urllib.request.urlopen(url).getcode()
        website_is_up = status_code == 200
        if website_is_up:
            pass
        else:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='This is not url.')
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5, delete_after=10)
            await asyncio.sleep(10)
            await ctx.message.delete()
            return

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='กรุณาเชื่อมต่อช่องเสียงก่อน')
                await message.edit(content = None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return

        if client and client.channel:
            if voice_run.channel != ctx.author.voice.channel:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
            if state.repeat == True:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't add any song when loop is **on**")
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return  
            try:
                with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video = None
                    num_song = 0
                    d = len(info['entries'])
                    if d > 25:
                        emBed5 = discord.Embed(color=0xff0000)
                        emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='ไม่สามารถเล่นได้ เนื่องจากมีวิดีโอในเพลลิสต์มากกว่า 25 ')
                        emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                        await message.edit(content=None, embed=emBed5, delete_after=10)
                        await asyncio.sleep(10)
                        await ctx.message.delete()
                        return
                    if "_type" in info and info["_type"] == "playlist":
                        await message.edit(content="**processing...**")
                        for entry in info["entries"]:
                            video = Videoplaylist(url, ctx.author, num_song=num_song)
                            state.playlist.append(video)
                            num_song+=1
            except youtube_dl.DownloadError as e:
                logging.warn(f"Error downloading song: {e}")
                await message.edit(content="There was an error downloading your song, **sorry.**", embed=None)
                return
            await message.edit(content=None, embed=video.get_embed())
        else:
            if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await message.edit(content="There was an error downloading your song, **sorry.**", embed=None)
                    return
                with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    d = len(info['entries'])
                    if d > 25:
                        emBed5 = discord.Embed(color=0xff0000)
                        emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='ไม่สามารถเล่นได้ เนื่องจากมีวิดีโอในเพลลิสต์มากกว่า 25 ')
                        emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                        await message.edit(content=None, embed=emBed5, delete_after=10)
                        await asyncio.sleep(10)
                        await ctx.message.delete()
                        return
                client = await channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                self._play_song(client, state, video)
                try:
                    with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        video = None
                        num_song = 1
                    if "_type" in info and info["_type"] == "playlist":
                        await message.edit(content="**processing...**")
                        for entry in info["entries"]:
                            video = Videoplaylist(url, ctx.author, num_song=num_song)
                            state.playlist.append(video)
                            num_song+=1
                except:
                    pass
                await message.edit(content=None, embed=video.get_embed())
                logging.info(f"Now playing '{video.title_playlist}'")
                
            else:
                raise commands.CommandError(
                    "You need to be in a voice channel to do that.")

    @cog_ext.cog_slash(
        name="loop",
        description="loop only one song."
    )
    async def _loop(self, ctx):
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        channel = discord.VoiceChannel = None
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='กรุณาเชื่อมต่อช่องเสียงก่อน')
                await message.edit(content = None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        client = ctx.guild.voice_client
        if client and client.channel:
            if voice_run.channel != ctx.author.voice.channel:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
        if client and client.channel and client.source:
            state = self.get_state(ctx.guild)
            mode = state.repeat
            if mode == False:
                state.repeat = True
                await message.edit(content="loop is **On**", embed=None)
                logging.info("Loop On ")
            elif mode == True:
                state.repeat = False
                await message.edit(content="loop is **Off**", embed=None)
                logging.info("Loop Off ")
            return
        else:
            raise commands.CommandError("Not currently playing any audio.")
        

    @cog_ext.cog_slash(
        name="play",
        description="play song by url/name"
    )
    async def _play(self, ctx, search):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        url = search
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)  # get the guild's state
        channel = discord.VoiceChannel = None
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='กรุณาเชื่อมต่อช่องเสียงก่อน')
                await message.edit(content = None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return

        if client and client.channel:
            if voice_run.channel != ctx.author.voice.channel:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
            if state.repeat == True:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't add any song when loop is **on**")
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                logging.warn(f"Error downloading song: {e}")
                await message.edit(content="There was an error downloading your song, **sorry.**", embed=None)
                return
            state.playlist.append(video)
            await message.edit(content=None, embed=video.get_embed())
        else:
            if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await message.edit(content="There was an error downloading your song, **sorry.**", embed=None)
                    return
                client = await channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                self._play_song(client, state, video)
                await message.edit(content=None, embed=video.get_embed())
                logging.info(f"Now playing '{video.title}'")
            else:
                raise commands.CommandError(
                    "You need to be in a voice channel to do that.")
    @cog_ext.cog_slash(
        name="queue",
        description="show songs queue."
    )
    async def _queue(self, ctx):
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        client = ctx.guild.voice_client
        if client and client.channel and client.source:
            state = self.get_state(ctx.guild)
            if state.repeat == True:
                message = await message.edit(content="**now loop this**", embed=state.now_playing.get_embed())
                return 
            queue = state.playlist
            # await ctx.send(embed=self._queue_text(state.playlist))
            if len(queue) > 0:
                fmt = "\n".join(f"ฺ {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"for (index, song) in enumerate(queue))
                # add individual songs
                embed2 = discord.Embed(title=f'รายการเพลงที่ยังไม่ได้เล่น - ทั้งหมด {len(queue)}', description=fmt, color=0xC1E1C1)
                await message.edit(embed=embed2)
            else:
                await message.edit(content="The play queue is empty.")
        else:
            await message.edit(content="**Not currently playing any audio.**")

    @cog_ext.cog_slash(
        name="resume_or_pause",
        description="pause or resume song."
    )
    async def _pause(self, ctx):
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        state = self.get_state(ctx.guild)
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_run == None:
            emBed4 = discord.Embed(color=0xff0000)
            emBed4.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้เชื่อมต่อกับช่องเสียงอยู่')
            emBed4.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed4, delete_after=5)
            return

        if voice_run.channel != ctx.author.voice.channel:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed5, delete_after=10)
            return
        voice = ctx.author.voice
        bot_voice = ctx.guild.voice_client
        if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
            """Pauses any currently playing audio."""
            client = ctx.guild.voice_client
            self.ctx = ctx
            self._pause_audio_slash(client)
            await message.edit(content=".✅")
        else:
            raise commands.CommandError(
                "You need to be in the channel to do that.")
    def _pause_audio_slash(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()


    @cog_ext.cog_slash(
        name="clear_queue",
        description="clear all queues"
    )
    async def _clearqueue(self, ctx):
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        client = ctx.guild.voice_client
        if client and client.channel and client.source:
            """Clears the play queue without leaving the channel."""
            state = self.get_state(ctx.guild)
            state.playlist = []
            await message.edit(content="clear all queues complete ✅")
        else:
            await message.edit(content="**Not currently playing any audio.**")

    @cog_ext.cog_slash(
        name="volume",
        description="change volume"
    )
    async def _volume(self, ctx, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        state = self.get_state(ctx.guild)
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_run == None:
            emBed4 = discord.Embed(color=0xff0000)
            emBed4.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้เชื่อมต่อกับช่องเสียงอยู่')
            emBed4.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed4, delete_after=5)
            return

        if voice_run.channel != ctx.author.voice.channel:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed5, delete_after=10)
            return
        voice = ctx.author.voice
        bot_voice = ctx.guild.voice_client
        if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
            # make sure volume is nonnegative
            if volume < 0:
                volume = 0
                

            max_vol = self.config["max_volume"]
            if max_vol > -1:  # check if max volume is set
                # clamp volume to [0, max_vol]
                if volume > max_vol:
                    volume = max_vol

            client = ctx.guild.voice_client

            state.volume = float(volume) / 100.0
            await ctx.send("volume `change`")
            client.source.volume = state.volume  # update the AudioSource's volume to match
            
        else:
            raise commands.CommandError(
                "You need to be in the channel to do that.")
    @cog_ext.cog_slash(
        name="nowplaying",
        description="currently playing song"
    )
    async def _nowplaying(self, ctx):
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        state = self.get_state(ctx.guild)
        if state.repeat == True:
            client = ctx.guild.voice_client
            if client and client.channel and client.source:
                """Displays information about the current song."""
                await message.edit(content="**now loop this**", embed=state.now_playing.get_embed())
            else:
                await message.edit(content="**Not currently playing any audio.**")
            return 
        client = ctx.guild.voice_client
        if client and client.channel and client.source:
            """Displays information about the current song."""
            state = self.get_state(ctx.guild)
            await message.edit(content="**now playing**", embed=state.now_playing.get_embed())
        else:
            await message.edit(content="**Not currently playing any audio.**")


    @cog_ext.cog_slash(
        name="skip",
        description="skip song"
    )
    async def _skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_run == None:
            emBed4 = discord.Embed(color=0xff0000)
            emBed4.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้เชื่อมต่อกับช่องเสียงอยู่')
            emBed4.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed4, delete_after=5)
            return
        try:
            if voice_run.channel != ctx.author.voice.channel:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\nขณะนี้บอทกำลังอยู่ในช่อง{0}'.format(voice_run.channel))
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(embed=emBed5, delete_after=10)
                return
            elif not voice_run.is_playing():
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='เพลงไม่ได้เล่นอยู่จึง ข้ามไม่ได้')
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(embed=emBed5, delete_after=10)
                return
            elif state.repeat == True:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't skip song when loop is **on**")
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await message.edit(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
        except:
            await message.edit(content="You need to be in the channel to do that.")
            return
                
        
        emBed6 = discord.Embed(color=0xF3F4F9)
        emBed6.add_field(name='ข้ามเพลงแล้ว', value=(f'**`{ctx.author.name}`**: Skipped the song!'))
        await message.edit(embed=emBed6)
        voice_run.stop()

    @commands.command()
    async def bug (self, ctx):
        emBED = discord.Embed(color=0xF3F4F9)
        emBED.description = "bug report \n: mail :\n- supanathub@gmail.com"
        await ctx.send(embed=emBED)

    @cog_ext.cog_slash(
        name="bug",
        description="report bug to developer."
    )
    async def _bug (self, ctx):
        emBED = discord.Embed(color=0xF3F4F9)
        emBED.description = "bug report \n: mail :\n- supanathub@gmail.com"
        await ctx.send(embed=emBED)

    @cog_ext.cog_slash(
        name="leave",
        description="leave channel and clear queue"
    )
    async def _leave(self, ctx):
        """Leaves the voice channel, if currently in one."""
        message = await ctx.send("**wait for it....**")
        if message.channel.type == discord.ChannelType.private:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't use this command in DM.")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(content=None, embed=emBed5)
            return
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client == None or not voice_client.is_connected():
            emBed6 = discord.Embed(color=0xff0000)
            emBed6.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้อยู่ในช่องเพลงใดๆ')
            emBed6.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed6, delete_after=5)
            return
        if voice_client.channel != ctx.author.voice.channel:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_client.channel))
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await message.edit(embed=emBed5, delete_after=10)
            return
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        emBed3 = discord.Embed(color=0xF3F4F9)
        emBed3.add_field(name='006 music ได้ออกจากช่องแล้ว', value='disconnected')
        await message.edit(embed=emBed3)
        await client.disconnect()
        logging.info("Loop Off ")
        state.playlist = []
        state.repeat = False
        state.now_playing = None


    @cog_ext.cog_slash(
        name="ping",
        description="ping of bot"
    )
    async def _ping(self, ctx):
        emBed = discord.Embed(color=0xF3F4F9)
        emBed.add_field(name='__**Pong! 🏓**__', value=f"👉 ping: {round(self.bot.latency * 1000)} ms 👈")
        await ctx.send(embed=emBed)

    @commands.command()
    @commands.guild_only()
    async def ping(self, ctx):
        emBed = discord.Embed(color=0xF3F4F9)
        emBed.add_field(name='__**Pong! 🏓**__', value=f"👉 ping: {round(self.bot.latency * 1000)} ms 👈")
        await ctx.send(embed=emBed)

    @cog_ext.cog_slash(
        name="help",
        description="show help command"
    )
    async def _help(self, ctx):
        emBed = discord.Embed(title="**006 music help**", description="All actailable bot command", color=0xF3F4F9)
        emBed.add_field(name="-help", value="เพื่อดูว่า ณ ตอนนี้มีคำสั่งอะไรบ้าง", inline=False)
        emBed.add_field(name="-play + url หรือ ชื่อเพลง [ ย่อๆว่า : _p ]", value="เพื่อเล่นเพลง", inline=False)
        emBed.add_field(name="-skip [ ย่อๆว่า : -s ]", value="เพื่อข้ามเพลง", inline=False)
        emBed.add_field(name="-pause", value="เพื่อหยุดเล่นเพลงชั่วคราว/หรือเล่นเพลงต่อ", inline=False)
        emBed.add_field(name="-np", value="ดูเพลงที่กำลังเล่นอยู่", inline=False)
        emBed.add_field(name="-v + ค่าความดัง 0 ถึง 250", value="เพื่อเพิ่ม/ลดเสียง", inline=False)
        emBed.add_field(name="-leave [ ย่อๆว่า : -l ]", value="เพื่อให้บอทออกจากช่อง", inline=False)
        emBed.add_field(name="-bug", value="ช่องทาง report bug มาที่ผู้สร้าง", inline=False)
        emBed.add_field(name="-queue", value="เพื่อดูคิวเพลง", inline=False)
        emBed.add_field(name="-cq", value="เพื่อล้างเพลงทั้งหมดในคิว", inline=False)
        #emBed.add_field(name="**ปล.**", value="หรือจะใช้ SlashCommand ก็ได้นะคะ", inline=False)
        emBed.add_field(name="**หมายเหตุ**", value="การใช้อีโมจิจะกดได้เฉพาะ`Requester`เพลงนั้นเท่านั้น", inline=False)
        emBed.set_thumbnail(url="https://cdn.discordapp.com/avatars/880982026314985523/c0c18a163468077e6ac3a9be89f67dcb.png")
        emBed.set_footer(text="Bot by SUPANAT hub", icon_url="https://yt3.ggpht.com/ytc/AKedOLTg33C3Bel5GklXFx7bG0C9UybfE05VfTzEh2rB=s900-c-k-c0x00ffffff-no-rj")
        await ctx.send(embed=emBed)

    @commands.command(aliases=["h", "H"])
    async def help(self, ctx):
        emBed = discord.Embed(title="**006 music help**", description="All actailable bot command", color=0xF3F4F9)
        emBed.add_field(name="-help", value="เพื่อดูว่า ณ ตอนนี้มีคำสั่งอะไรบ้าง", inline=False)
        emBed.add_field(name="-play + url หรือ ชื่อเพลง [ ย่อๆว่า : _p ]", value="เพื่อเล่นเพลง", inline=False)
        emBed.add_field(name="-skip [ ย่อๆว่า : -s ]", value="เพื่อข้ามเพลง", inline=False)
        emBed.add_field(name="-pause", value="เพื่อหยุดเล่นเพลงชั่วคราว/หรือเล่นเพลงต่อ", inline=False)
        emBed.add_field(name="-np", value="ดูเพลงที่กำลังเล่นอยู่", inline=False)
        emBed.add_field(name="-v + ค่าความดัง 0 ถึง 250", value="เพื่อเพิ่ม/ลดเสียง", inline=False)
        emBed.add_field(name="-leave [ ย่อๆว่า : -l ]", value="เพื่อให้บอทออกจากช่อง", inline=False)
        emBed.add_field(name="-bug", value="ช่องทาง report bug มาที่ผู้สร้าง", inline=False)
        emBed.add_field(name="-queue", value="เพื่อดูคิวเพลง", inline=False)
        emBed.add_field(name="-cq", value="เพื่อล้างเพลงทั้งหมดในคิว", inline=False)
        #emBed.add_field(name="**ปล.**", value="หรือจะใช้ SlashCommand ก็ได้นะคะ", inline=False)
        emBed.add_field(name="**หมายเหตุ**", value="การใช้อีโมจิจะกดได้เฉพาะ`Requester`เพลงนั้นเท่านั้น", inline=False)
        emBed.set_thumbnail(url="https://cdn.discordapp.com/avatars/880982026314985523/c0c18a163468077e6ac3a9be89f67dcb.png")
        emBed.set_footer(text="Bot by SUPANAT hub", icon_url="https://yt3.ggpht.com/ytc/AKedOLTg33C3Bel5GklXFx7bG0C9UybfE05VfTzEh2rB=s900-c-k-c0x00ffffff-no-rj")
        await ctx.send(embed=emBed)

    @commands.command(aliases=["stop", "l", "L"])
    @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        """Leaves the voice channel, if currently in one."""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client == None or not voice_client.is_connected():
            emBed6 = discord.Embed(color=0xff0000)
            emBed6.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้อยู่ในช่องเพลงใดๆ')
            emBed6.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(embed=emBed6, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        if voice_client.channel != ctx.author.voice.channel:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_client.channel))
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(embed=emBed5, delete_after=10)
            await asyncio.sleep(10)
            await ctx.message.delete()
            return 
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        emBed3 = discord.Embed(color=0xff0000)
        emBed3.add_field(name='006 music ได้ออกจากช่องแล้ว', value='disconnected')
        await ctx.send(embed=emBed3)
        await client.disconnect()
        logging.info("Loop Off ")
        state.playlist = []
        state.repeat = False
        state.now_playing = None

    @commands.command(aliases=["resume"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    # @commands.check(is_audio_requester)
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        client = ctx.guild.voice_client

        self._pause_audio(client)
        await ctx.send("✅ฺ")

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
            
        else:
            client.pause()

    
    @commands.command(aliases=["vol", "v", "V"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    # @commands.check(is_audio_requester)
    async def volume(self, ctx, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        state = self.get_state(ctx.guild)

        # make sure volume is nonnegative
        if volume < 0:
            volume = 0

        max_vol = self.config["max_volume"]
        if max_vol > -1:  # check if max volume is set
            # clamp volume to [0, max_vol]
            if volume > max_vol:
                volume = max_vol

        client = ctx.guild.voice_client

        state.volume = float(volume) / 100.0
        await ctx.send("✅ฺ")
        client.source.volume = state.volume  # update the AudioSource's volume to match

    @commands.command(aliases=["s"])
    @commands.guild_only()
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_run == None:
            emBed4 = discord.Embed(color=0xff0000)
            emBed4.add_field(name='เกิดข้อผิดพลาด T_T', value='บอทไม่ได้เชื่อมต่อกับช่องเสียงอยู่')
            emBed4.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(embed=emBed4, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            return

        if voice_run.channel != ctx.author.voice.channel:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(embed=emBed5, delete_after=10)
            await asyncio.sleep(10)
            await ctx.message.delete()
            return
        elif not voice_run.is_playing():
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='เพลงไม่ได้เล่นอยู่จึง ข้ามไม่ได้')
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(embed=emBed5, delete_after=10)
            await asyncio.sleep(10)
            await ctx.message.delete()
            return
        elif state.repeat == True:
            emBed5 = discord.Embed(color=0xff0000)
            emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't skip song when loop is **on**")
            emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
            await ctx.send(content=None, embed=emBed5, delete_after=10)
            await asyncio.sleep(10)
            await ctx.message.delete()
            return 
        emBed6 = discord.Embed(color=0xF3F4F9)
        emBed6.add_field(name='ข้ามเพลงแล้ว', value=(f'**`{ctx.author.name}`**: Skipped the song!'))
        await ctx.send(embed=emBed6)
        voice_run.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)

        def after_playing(err):
            if state.repeat == True:
                self._play_song(client, state, song)
                return
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                if len(state.playlist) <= 0:
                    asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                    self.bot.loop)
                else:
                    pass

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        state = self.get_state(ctx.guild)
        if state.repeat == True:
            message = await ctx.send("**now loop this**", embed=state.now_playing.get_embed())
            return
        else:
            message = await ctx.send("**now playing**", embed=state.now_playing.get_embed())

    @commands.command(aliases=["q", "playlist"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        if state.repeat == True:
            message = await ctx.send("**now loop this**", embed=state.now_playing.get_embed())
            return 
        queue = state.playlist
        # await ctx.send(embed=self._queue_text(state.playlist))
        if len(queue) > 0:
            fmt = "\n".join(f"ฺ {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"for (index, song) in enumerate(queue))
              # add individual songs
            embed2 = discord.Embed(title=f'รายการเพลงที่ยังไม่ได้เล่น - ทั้งหมด {len(queue)}', description=fmt, color=0xC1E1C1)
            await ctx.send(embed=embed2)
        else:
            await ctx.send("The play queue is empty.")

    # def _queue_text(self, queue):
    #     """Returns a block of text describing a given song queue."""
        
        

    @commands.command(aliases=["cq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    # @commands.has_permissions(administrator=True)
    async def clearqueue(self, ctx):
        """Clears the play queue without leaving the channel."""
        state = self.get_state(ctx.guild)
        state.playlist = []
        await ctx.send("clear all queues complete ✅")


    @commands.command(aliases=["jq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    # @commands.has_permissions(administrator=True)
    async def jumpqueue(self, ctx, song: int, new_index: int):
        """Moves song at an index to `new_index` in queue."""
        state = self.get_state(ctx.guild)  # get state for this guild
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song - 1)  # take song at index...
            state.playlist.insert(new_index - 1, song)  # and insert it.

            await ctx.send(self._queue_text(state.playlist))
        else:
            raise commands.CommandError("You must use a valid index.")

    @commands.command(aliases=["p"], brief="Plays audio from <url>.")
    @commands.guild_only()
    async def play(self, ctx, *, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)  # get the guild's state
        channel = discord.VoiceChannel = None
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='กรุณาเชื่อมต่อช่องเสียงก่อน')
                await ctx.send(content = None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return
        voice_run = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # if voice_run.channel != ctx.author.voice.channel:
        #     emBed5 = discord.Embed(color=0xff0000)
        #     emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
        #     emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
        #     await ctx.send(embed=emBed5, delete_after=10)
        #     await asyncio.sleep(10)
        #     await ctx.message.delete()
        #     return  


        if client and client.channel:
            if voice_run.channel != ctx.author.voice.channel:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value='คุณไม่ได้อยู่ช่องเดียวกับบอทจึงไม่สามารถใช้คำสั่งนี้ได้\n- ขณะนี้บอทกำลังอยู่ในช่อง **{0}**'.format(voice_run.channel))
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await ctx.send(embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
            if state.repeat == True:
                emBed5 = discord.Embed(color=0xff0000)
                emBed5.add_field(name='เกิดข้อผิดพลาด T_T', value="Can't add any song when loop is **on**")
                emBed5.set_author(name="006 music", icon_url="https://cdn.discordapp.com/emojis/948836763919613974.gif")
                await ctx.send(content=None, embed=emBed5, delete_after=10)
                await asyncio.sleep(10)
                await ctx.message.delete()
                return 
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                logging.warn(f"Error downloading song: {e}")
                await ctx.send(
                    "There was an error downloading your song, **sorry.**")
                return
            state.playlist.append(video)
            message = await ctx.send(embed=video.get_embed())
        else:
            if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await ctx.send(
                        "There was an error downloading your song, **sorry.**")
                    return
                client = await channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                self._play_song(client, state, video)
                message = await ctx.send("", embed=video.get_embed())
                logging.info(f"Now playing '{video.title}'")
            else:
                raise commands.CommandError(
                    "You need to be in a voice channel to do that.")

class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None
        self.repeat = False

    def is_requester(self, user):
        return self.now_playing.requested_by == user

    
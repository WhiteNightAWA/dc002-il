import asyncio
import math

import discord.types.channel
from discord.ext import commands
from cogs.core import Core
from cogs.functions.audio import audio_playing, is_audio_requester, in_voice_channel
from cogs.util.GuildState import GuildState

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'


class Music(Core):

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.group(pass_context=True)
    async def music(self, ctx):
        pass

    @music.commands(pass_context=True, name="join")
    async def join(self, ctx):
        VS = ctx.author.voice
        if VS is not None:
            try:
                channel = VS.channel
                channel.connect()
                await ctx.reply(f":white_check_mark: The bot connected to the channel <#{channel.id}>")
            except Exception as e:
                await ctx.reply(f":x: Error while connecting to the channel!\n{e}")
        else:
            await ctx.reply(":x: You are not in a Voice Channel!")

    @music.commands(pass_context=True, name="leave", aliases=["stop", "sp"])
    @commands.guild_only()
    async def leave(self, ctx):
        VC = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if VC and VC.channel:
            await VC.disconnect()
            state.playlist = []
            state.now_playing = None
        else:
            raise commands.CommandError(":x: The bot not in a voice channel.")

    @music.command(pass_context=True, aliases=["resume", "p"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        client = ctx.guild.voice_client
        self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @music.command(pass_context=True, name="skip")
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        if ctx.channel.permissions_for(ctx.author).administrator or state.is_requester(ctx.author):
            # immediately skip if requester or admin
            client.stop()
        else:
            await ctx.reply(":x: Sorry, you can't skip.")

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                 self.bot.loop)

        client.play(source, after=after_playing)

    @music.command(pass_context=True, aliases=["np"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        state = self.get_state(ctx.guild)
        message = await ctx.send("", embed=state.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @music.command(pass_context=True, aliases=["q", "playlist"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        """Returns a block of text describing a given song queue."""
        if len(queue) > 0:
            message = [f"{len(queue)} songs in queue:"]
            message += [
                f"  {index + 1}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

async def setup(bot):
    await bot.add_cog(Music(bot))

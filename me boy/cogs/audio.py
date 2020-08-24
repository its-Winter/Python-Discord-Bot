"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.
Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re
import math
import aiohttp
import discord
import lavalink
from discord.ext import commands
from cogs.utils import utils
from typing import Optional, Union

time_rx = re.compile('[0-9]+')
url_rx = re.compile(r'https?:\/\/(?:www\.)?.+')

class Audio(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

            if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
                  bot.lavalink = lavalink.Client(bot.user.id)
                  bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'na', 'localhost')  # Host, Port, Password, Region, Name
                  bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

            bot.lavalink._event_hooks.clear()
            bot.lavalink.add_event_hook(self.track_hook)

      def cog_unload(self):
            self.bot.lavalink._event_hooks.clear()

      async def cog_before_invoke(self, ctx):
            guild_check = ctx.guild is not None
            #  This is essentially the same as `@commands.guild_only()`
            #  except it saves us repeating ourselves (and also a few lines).

            if guild_check:
                  await self.ensure_voice(ctx)
                  #  Ensure that the bot and command author share a mutual voicechannel.

            return guild_check

      async def cog_command_error(self, ctx, error):
            if isinstance(error, commands.CommandInvokeError):
                  await ctx.send(error.original)
                  # The above handles errors thrown in this cog and shows them to the user.
                  # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
                  # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
                  # if you want to do things differently.

      async def track_hook(self, event):
            if isinstance(event, lavalink.events.QueueEndEvent):
                  guild_id = int(event.player.guild_id)
                  await self.connect_to(guild_id, None)
            elif isinstance(event, lavalink.events.TrackStartEvent):
                  ch = event.player.fetch('channel')

                  if ch:
                        await ch.send(f'**Track started:** {event.track.title}')
            elif isinstance(event, lavalink.events.TrackExceptionEvent):
                  event.player.repeat = False
                  ch = event.player.fetch('channel')

                  if ch:
                        await ch.send(f'oop\n```\n{event.exception}```')

      async def connect_to(self, guild_id: int, channel_id: str):
            """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
            ws = self.bot._connection._get_websocket(guild_id)
            await ws.voice_state(str(guild_id), channel_id)
            # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
            # the bot instance is an AutoShardedBot.

      @commands.command(name="nodes")
      @commands.is_owner()
      async def _nodes(self, ctx):
            if self.bot.lavalink.node_manager.nodes:
                  await ctx.send(utils.box(self.bot.lavalink.node_manager.nodes, lang="py"))
            else:
                  await ctx.send("There are no nodes.")

      @commands.command(name="ensurenode")
      @commands.is_owner()
      async def _ensure_node(self, ctx):
            if not self.bot.lavalink.node_manager.nodes or self.bot.lavalink.node_manager.nodes[0].name != 'localhost':
                  self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'na', 'localhost')  # Host, Port, Password, Region, Name
                  await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

      @commands.command(name="lldc")
      @commands.is_owner()
      async def _disconnect_lavalink(self, ctx):
            if self.bot.lavalink.node_manager.nodes:
                  for node in self.bot.lavalink.node_manager.nodes:
                        self.bot.lavalink.node_manager.remove_node(node)
                        await ctx.message.add_reaction("✅")

      @commands.command(name="play", aliases=['p'])
      async def _play(self, ctx, *, query: str):
            """ Searches and plays a song from a given query. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            raw_query = query
            query = query.strip('<>')

            if not url_rx.match(query):
                  query = f'ytsearch:{query}'

            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                  return await ctx.send(f'`{raw_query}` yielded no results.')

            embed = discord.Embed(color=discord.Color.blurple())

            if results['loadType'] == 'PLAYLIST_LOADED':
                  tracks = results['tracks']

                  for track in tracks:
                        player.add(requester=ctx.author.id, track=track)

                  embed.title = 'Playlist Enqueued!'
                  embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
            else:
                  track = results['tracks'][0]
                  embed.title = 'Track Enqueued'
                  embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                  player.add(requester=ctx.author.id, track=track)

            await ctx.send(embed=embed)

            if not player.is_playing:
                  player.store('channel', ctx.channel)
                  await player.play()

      @commands.command(name="seek")
      async def _seek(self, ctx, *, seconds: int):
            """ Seeks to a given position in a track. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            track_time = player.position + (seconds * 1000)
            await player.seek(track_time)

            await ctx.send(f'Moved track to **{lavalink.utils.format_time(track_time)}**')

      @commands.command(name="skip", aliases=['forceskip'])
      async def _skip(self, ctx):
            """ Skips the current track. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_playing:
                  return await ctx.send('Not playing.')

            await player.skip()
            await ctx.send('⏭ Skipped.')

      @commands.command(name="stop")
      async def _stop(self, ctx):
            """ Stops the player and clears its queue. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('Not playing.')

            player.queue.clear()
            await player.stop()
            await ctx.send('⏹ Stopped.')

      @commands.command(name="now", aliases=['np', 'n', 'playing'])
      async def _now(self, ctx):
            """ Shows some stats about the currently playing song. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.current:
                  return await ctx.send('Nothing playing.')

            position = lavalink.utils.format_time(player.position)
            if player.current.stream:
                  duration = '🔴 LIVE'
            else:
                  duration = lavalink.utils.format_time(player.current.duration)
            song = f'**[{player.current.title}]({player.current.uri})**\n({position}/{duration})'

            embed = discord.Embed(color=discord.Color.blurple(),
                                  title='Now Playing', description=song)
            # if player.current and player.current.thumbnail:
            #       embed.set_thumbnail(url=player.current.thumbnail)

            embed.set_footer(text=f"Requested by {player.current.requester}")

            await ctx.send(embed=embed)

      @commands.command(name="queue", aliases=['q'])
      async def _queue(self, ctx, page: int = 1):
            """ Shows the player's queue. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.queue:
                  return await ctx.send('Nothing queued.')

            items_per_page = 10
            pages = math.ceil(len(player.queue) / items_per_page)

            start = (page - 1) * items_per_page
            end = start + items_per_page

            queue_list = ''
            for index, track in enumerate(player.queue[start:end], start=start):
                  queue_list += f"`{index + 1}.` [**{track.title}**]({track.uri}) `{lavalink.utils.format_time(track.duration)}`\n"

            embed = discord.Embed(colour=discord.Color.blurple(),
                                  description=f"**{len(player.queue)} tracks**\n\n{queue_list}")
            embed.set_footer(text=f"Viewing page {page}/{pages}")
            await ctx.send(embed=embed)

      @commands.command(name="pause", aliases=['resume'])
      async def _pause(self, ctx):
            """ Pauses/Resumes the current track. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_playing:
                  return await ctx.send('Not playing.')

            if player.paused:
                  await player.set_pause(False)
                  await ctx.send('⏯ Resumed')
            else:
                  await player.set_pause(True)
                  await ctx.send('⏯ Paused')

      @commands.command(name="volume", aliases=['vol', 'v'])
      async def _volume(self, ctx, volume: int = None):
            """ Changes the player's volume (0-1000). """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not volume:
                  return await ctx.send(f'🔈 | {player.volume}%')

            await player.set_volume(volume)  # Lavalink will automatically cap values between, or equal to 0-1000.
            await ctx.send(f'🔈 Set to {player.volume}%')

      @commands.command(name="shuffle")
      async def _shuffle(self, ctx):
            """ Shuffles the player's queue. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_playing:
                  return await ctx.send('Nothing playing.')

            player.shuffle = not player.shuffle
            await ctx.send('🔀 Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

      @commands.command(name="repeat", aliases=['loop'])
      async def _repeat(self, ctx):
            """ Repeats the current song until the command is invoked again. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_playing:
                  return await ctx.send('Nothing playing.')

            player.repeat = not player.repeat
            await ctx.send('🔁 Repeat ' + ('enabled' if player.repeat else 'disabled'))

      @commands.command(name="remove")
      async def _remove(self, ctx, index: int):
            """ Removes an item from the player's queue with the given index. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.queue:
                  return await ctx.send('Nothing queued.')

            if index > len(player.queue) or index < 1:
                  return await ctx.send(f'Index has to be **between** 1 and {len(player.queue)}')

            removed = player.queue.pop(index - 1)  # Account for 0-index.

            await ctx.send(f'Removed **{removed.title}** from the queue.')

      @commands.command(name="search")
      async def _search(self, ctx, *, query):
            """ Lists the first 10 search results from a given query. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
                  query = 'ytsearch:' + query

            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                  return await ctx.send('Nothing found.')

            tracks = results['tracks'][:10]  # First 10 results

            o = ''
            for index, track in enumerate(tracks, start=1):
                  track_title = track['info']['title']
                  track_uri = track['info']['uri']
                  o += f'`{index}.` [{track_title}]({track_uri})\n'

            embed = discord.Embed(color=discord.Color.blue(), description=o)
            await ctx.send(embed=embed)

      @commands.command(name="disconnect", aliases=['dc'])
      async def _disconnect(self, ctx):
            """ Disconnects the player from the voice channel and clears its queue. """
            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

            if not player.is_connected:
                  return await ctx.send('Not connected.')

            if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
                  return await ctx.send('You\'re not in my voicechannel!')

            player.queue.clear()
            await player.stop()
            await self.connect_to(ctx.guild.id, None)
            await ctx.send('*⃣ Disconnected.')

      async def ensure_voice(self, ctx):
            """ This check ensures that the bot and command author are in the same voicechannel. """
            player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            # Create returns a player if one exists, otherwise creates.

            should_connect = ctx.command.name in ('play')  # Add commands that require joining voice to work.

            if not ctx.author.voice or not ctx.author.voice.channel:
                  raise commands.CommandInvokeError('Join a voice channel first.')

            if not player.is_connected:
                  if not should_connect:
                        raise commands.CommandInvokeError('Not connected.')

                  permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                  if not permissions.connect or not permissions.speak:  # Check user limit too?
                        raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

                  player.store('channel', ctx.channel.id)
                  await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                  if int(player.channel_id) != ctx.author.voice.channel.id:
                        raise commands.CommandInvokeError('You need to be in my voice channel.')

def setup(bot):
    bot.add_cog(Audio(bot))
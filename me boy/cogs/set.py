import discord
import aiohttp
import asyncio
import sqlite3
from discord.ext import commands
from typing import (
      Optional,
      Union,
      Sequence
)

class Set(commands.Cog):

      def __init__(self, bot):
            self.bot = bot

      @commands.group(name="set")
      @commands.is_owner()
      async def _set(self, ctx: commands.Context):
            """Set stuff."""
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_set.command(name="avatar", aliases=["av"])
      async def _avatar(self, ctx: commands.Context, url: str = None):
            """Set bot user's avatar."""
            if len(ctx.message.attachments) > 0:
                  data = await ctx.message.attachments[0].read()
            elif url is not None:
                  if url.startswith("<") and url.endswith(">"):
                        url = url[1:-1]

                  async with aiohttp.ClientSession() as session:
                        async with session.get(url) as r:
                              data = await r.read()
            else:
                  return await ctx.send("Nothing changed.")
            try:
                  async with ctx.typing():
                        await ctx.bot.user.edit(avatar=data)
            except discord.HTTPException:
                  await ctx.send(
                        "Failed. Remember that you can edit the avatar "
                        "up to two times a hour. The URL or attachment "
                        "must be a valid image in either JPG or PNG format."
                  )
            except discord.InvalidArgument:
                  await ctx.send("JPG / PNG format only.")
            else:
                  await ctx.send("Avatar set.")

      @_set.command(name="nickname", aliases=["nick"])
      @commands.guild_only()
      async def _nickname(self, ctx: commands.Context, *, nick: str = None):
            """Set bot user's nickname in current guild."""
            if not nick:
                  nick = None
                  msg = f"Nickname Cleared."
            else:
                  msg = f"Nickname set to `{nick}`."
            try:
                  await ctx.guild.me.edit(nick=nick)
                  return await ctx.send(msg)
            except discord.Forbidden:
                  return await ctx.send("I lack the permission to change my nickname.")

      @_set.command(name="status")
      async def _status(self, ctx: commands.Context, status: str = None):
            """Set bot user's status."""
            statuses = {
                  "online": [discord.Status.online, "Online"],
                  "idle": [discord.Status.idle, "Idle"],
                  "dnd": [discord.Status.dnd, "Dnd"],
                  "invisible": [discord.Status.invisible, "Invisible"],
                  "offline": [discord.Status.invisible, "Invisible"]
            }
            if status.lower() in statuses:
                  chosenstatus = statuses.get(status.lower())
            elif status is None:
                  return await ctx.send("Nothing set.")
            else:
                  return await ctx.send(f"Invalid status: `{status}`")
            status = chosenstatus[0]
            game = ctx.bot.guilds[0].me.activity if len(ctx.bot.guilds) > 0 else None
            try:
                  await ctx.bot.change_presence(status=status, activity=game)
            except Exception as e:
                  await ctx.send(f"Failed to set status. {e}")
            await ctx.send(f"Set status to `{chosenstatus[1]}`")

      @_set.command(name="playing", aliases=["game"])
      async def _playing(self, ctx: commands.Context, *, game: str = None):
            """Set bot user's playing status."""
            if game:
                  if len(game) > 128:
                        return await ctx.send("Exceeded maximum length of 128 characters.")
                  game = discord.Game(name=game)
            else:
                  game = None
            status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
            await ctx.bot.change_presence(status=status, activity=game)
            if game:
                  return await ctx.send(f"Status set to `Playing {game.name}`")
            else:
                  return await ctx.send("Game cleared.")

      @_set.command(name="listening")
      async def _listening(self, ctx: commands.Context, *, listening: str = None):
            """set bot user's listening status."""
            status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
            if listening:
                  activity = discord.Activity(name=listening, type=discord.ActivityType.listening)
            else:
                  activity = None
            await ctx.bot.change_presence(status=status, activity=activity)
            if listening:
                  return await ctx.send(f"Status set to ``Listening to {listening}``")
            else:
                  return await ctx.send("Listening cleared.")

      @_set.command(name="streaming", aliases=["stream"])
      async def _streaming(self, ctx: commands.Context, streamer: str = None, *, stream_title: str = None):
            """Set bot user's streaming status."""
            status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else None
            if stream_title:
                  stream_title = stream_title.strip()
                  if "twitch.tv/" not in streamer:
                        streamer = "https://twitch.tv/" + streamer
                  activity = discord.Streaming(url=streamer, name=stream_title)
                  await ctx.bot.change_presence(status=status, activity=activity)
            elif streamer is not None:
                  return await ctx.send(f"Failed to provide a stream title.")
            else:
                  await ctx.bot.change_presence(activity=None, status=status)

            if stream_title:
                  return await ctx.send(f"Status set to ``Streaming {stream_title}``")
            else:
                  return await ctx.send("Status cleared.")

      @_set.command(name="watching")
      async def _watching(self, ctx: commands.Context, *, watching: str = None):
            """Set bot user's watching status."""
            status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
            if watching:
                  activity = discord.Activity(name=watching, type=discord.ActivityType.watching)
            else:
                  activity = None
            await ctx.bot.change_presence(status=status, activity=activity)
            if watching:
                  return await ctx.send(f"Status set to ``Watching {watching}``")
            else:
                  return await ctx.send("Watching cleared.")

      @_set.command(name="customstatus", hidden=True)
      async def _customstatus(self, ctx, *, text: str = None):
            if text is None or text == "":
                  return await ctx.send("Nothing changed.")
            else:
                  status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
                  activity = discord.Activity(name=status, type=discord.ActivityType.custom)
            try:
                  await ctx.bot.change_presence(activity=activity)
                  await ctx.send(f"Custom Activity set to {text}")
            except Exception as e:
                  await ctx.send(f"Error: {e}")

      @commands.command(name="copystatus", aliases=["cpstatus"], hidden=True)
      async def _copy_status(self, ctx, person_to_copy: Optional[Union[discord.User, str]] = None):
            if not person_to_copy:
                  return await ctx.send("Nobody to copy.")
            if isinstance(person_to_copy, discord.User):
                  user = ctx.guild.get_member(user.id)
            pass
            

      @_set.command(name="sql")
      @commands.is_owner()
      async def _sql(self, ctx, tablename: str = None):
            connection = sqlite3.connect('members.db')
            cursor = sqlite3.Cursor(connection)
            cursor.execute(f"""CREATE TABLE {tablename} (id INTEGER PRIMARY KEY, name TEXT)""")

            await ctx.send(f"Ran the follwing SQL: `CREATE TABLE {tablename} (id INTEGER PRIMARY KEY, name TEXT)`")
            try:
                  connection.commit()
                  connection.close()
                  return await ctx.send("Committed and closed connection successfully.")
            except Exception as e:
                  return await ctx.send(f"The following occurred: {e}")
            


def setup(bot):
      bot.add_cog(Set(bot))
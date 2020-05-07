import sys
import arrow
import time
import asyncio
import aiohttp
import discord
import contextlib
import platform
import logging
from discord import utils
from discord.ext import commands
from discord.ext.commands import errors, core
from cogs.utils import utils

corelog = logging.getLogger('Core')
corelog.setLevel(logging.INFO)

class Core(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="welcome")
      @commands.guild_only()
      async def _welcome(self, ctx, *, users: discord.User = None):
            """a basic welcome command"""
            if not users:
                  await ctx.send(f"Welcome {ctx.author.mention} to {ctx.guild.name}!")
            else:
                  if len(tuple(users)) > 1:
                        users = ", ".join(users.mention)
                  else:
                        users = users.mention
                  await ctx.send(f"Welcome {users} to {ctx.guild.name}!")

      @commands.command(name="idavatar", aliases=["idav"])
      @commands.is_owner()
      async def _idavatar(self, ctx, userid: int = None):
            e = discord.Embed(color=discord.Color.blurple())
            if not userid:
                  user = ctx.author
            else:
                  try:
                        user = await ctx.bot.fetch_user(int(userid))
                        if user is None:
                              raise Exception("User is None.")
                  except Exception as e:
                        await ctx.send(f"Failed to catch user: {e}")
            e.set_image(url=user.avatar_url)
            e.set_author(name=f"{user.name}'s avatar", icon_url=user.avatar_url, url=user.avatar_url)
            e.set_footer(text=f"{ctx.author.name} wanted to see.", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="germ")
      @commands.guild_only()
      async def _germ(self, ctx):
            germ = ctx.bot.get_user(216085324906889226)
            germstime = arrow.now("US/Pacific").strftime("%X")
            e = discord.Embed(title=germ.name, description=f"this is germ: {germ.mention}", color=discord.Color.gold())
            e.set_author(name=germ.name, icon_url=germ.avatar_url)
            e.set_footer(text=f"{ctx.author.name} has asked about Germ at {germstime} PST", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="uptime")
      async def _uptime(self, ctx):
            async with ctx.typing():
                  uptimestr = utils.botuptime(self)
                  e = discord.Embed(description=f"{ctx.bot.user.mention} has been online for ```{uptimestr}.```", color=discord.Color.green())
                  e.set_author(name="Uptime", icon_url=ctx.bot.user.avatar_url)
                  e.set_footer(text=f"summoned by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="nsfwcheck")
      @commands.guild_only()
      async def _checknsfw(self, ctx):
            if ctx.channel.nsfw:
                  await ctx.send("Channel is set to NSFW.")
            else:
                  await ctx.send("Channel is not set to NSFW.")

      @commands.command(name="ping")
      async def _ping(self, ctx):
            """Ping pong."""
            latency = self.bot.latency * 1000
            e = discord.Embed(title="Pong.", color=discord.Color.red())
            e.add_field(name="Discord API", value=f"```{str(round(latency))} ms```")
            e.add_field(name="Typing", value="```calculating ms```")

            before = time.monotonic()
            message = await ctx.send(embed=e)
            typlatency = (time.monotonic() - before) * 1000

            e = discord.Embed(title="Pong.", color=discord.Color.green())
            e.add_field(name="Discord API", value=f"```py\n{str(round(latency))} ms```")
            e.add_field(name="Typing", value=f"```py\n{str(round(typlatency))} ms```")

            await message.edit(embed=e)
      
      @commands.command(name="reload")
      @commands.is_owner()
      async def _reload(self, ctx, *cogs):
            if not cogs:
                  await ctx.send("Please call with cogs to reload.")
                  return
            for cog in cogs:
                  try:
                        ctx.bot.reload_extension(f"cogs.{cog.lower()}")
                        await ctx.send(f"Reloaded: {cog}")
                        print(f"Reloaded: {cog}")
                  except Exception as e:
                        await ctx.send(f"Failed to reload: {cog}\n{e}")


      @commands.command(name="load")
      @commands.is_owner()
      async def _load(self, ctx, *cogs):
            if len(cogs) <= 0:
                  await ctx.send("Please call with cogs to reload.")
                  return
            async with ctx.typing():
                  for cog in cogs:
                        try:
                              ctx.bot.load_extension(f"cogs.{cog.lower()}")
                              await ctx.send(f"Loaded: {cog}")
                              print(f"Loaded: {cog}")
                        except Exception as e:
                              await ctx.send(f"Failed to load: {cog}\n{e}")

      @commands.command(name="guildinfo", aliases=["ginfo", "sinfo", "serverinfo"])
      @commands.guild_only()
      async def _guildinfo(self, ctx):
            waiting = await ctx.send("`Loading server data...`")
            guild = ctx.guild
            guild_invites = await guild.invites()
            invitecodes = []
            uses = []
            channel = []
            inviter = []
            for invite in guild_invites:
                  invitecodes.append(invite.code)
                  uses.append(str(invite.uses))
                  channel.append(invite.channel.mention)
                  inviter.append(invite.inviter.mention)

            invitecodes = "\n".join(invitecodes)
            uses = "\n".join(uses)
            channel = "\n".join(channel)
            inviter = "\n".join(inviter)

            e = discord.Embed(color=ctx.guild.me.top_role.color)
            e.set_author(name=f"{guild.name}'s invites")
            e.set_thumbnail(url=guild.icon_url)
            e.add_field(name="Invites", value=invitecodes)
            e.add_field(name="Uses", value=uses)
            e.add_field(name="Channel", value=channel)
            e.add_field(name="Inviter", value=inviter)
            await waiting.edit(content=None, embed=e)

      @commands.group(name="set")
      @commands.is_owner()
      async def _set(self, ctx):
            if ctx.invoked_subcommand is None:
                  await ctx.send("No subcommand was given.")

      @_set.command(name="token")
      async def _token(self, ctx, token: str = None):
            await ctx.send("Works!")

      @_set.command(name="avatar", aliases=["av"])
      async def _avatar(self, ctx, url: str = None):
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
      async def _nickname(self, ctx, *, nick: str = None):
            if not nick:
                  nick = None
                  msg = f"Nickname Cleared."
            else:
                  msg = f"Nickname set to `{nick}.`"
            try:
                  await ctx.guild.me.edit(nick=nick)
                  return await ctx.send(msg)
            except discord.Forbidden:
                  return await ctx.send("I lack the permission to change my nickname.")

      @_set.command(name="status")
      async def _status(self, ctx, status: str = None):
            """Set's bot's status"""
            statuses = {
                  "online": [discord.Status.online, "Online"],
                  "idle": [discord.Status.idle, "Idle"],
                  "dnd": [discord.Status.dnd, "Dnd"],
                  "invisible": [discord.Status.invisible, "Invisible"],
                  "offline": [discord.Status.invisible, "Invisible"]
            }
            if status in statuses:
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
      async def _playing(self, ctx, *, game: str = None):
            if game:
                  if len(game) > 128:
                        return await ctx.send("Exceeded maximum length of 128 characters.")

                  game = discord.Game(name=game)
            else:
                  game = None
            status = ctx.bot.guilds[0].me.status if len(ctx.bot.guilds) > 0 else discord.Status.online
            await ctx.bot.change_presence(status=status, activity=game)
            if game:
                  return await ctx.send(f"Status set to ``Playing {game.name}``")
            else:
                  return await ctx.send("Game cleared.")

      @_set.command(name="listening")
      async def _listening(self, ctx, *, listening: str = None):
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
      async def _streaming(self, ctx, streamer: str = None, *, stream_title: str = None):
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
      async def _watching(self, ctx, *, watching: str = None):
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



def setup(bot):
      bot.add_cog(Core(bot))
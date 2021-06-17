import discord
from discord.ext import commands
import contextlib
import os
import sys
import json
import platform
import logging
import asyncio
import DiscordUtils
from enum import IntEnum
from typing import (
      Optional,
      List
)
from collections import defaultdict
from datetime import datetime
from cogs.utils import (
      humanize_list,
      get_local_time
)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s :: %(message)s')
# filehandler = logging.FileHandler(filename='Discord.log', mode='a', encoding='utf-8')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s :: %(message)s')

with open('settings.json', 'r') as j:
      settings = json.load(j)

desc = "I'm {bot name here}! Originally a project to learn python from scratch, and soon to be fully public!"


class Context(commands.Context):
      def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            pass

      def start_deleting_messages(self, messages: List[discord.Message]):
            pass


class Bot(commands.bot.AutoShardedBot):

      def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.load_after_ready = ["audio", "wolfpack", "specific"]
            with open("prefixes.json", "r") as j:
                  prefixes = json.load(j)
                  self.guild_prefixes = defaultdict(dict)
                  self.guild_prefixes = prefixes
            self.regex_words = {}

      def load_cogs(self, cogs: Optional[list] = None):
            """loads cogs"""
            loaded = []
            errors = []
            ignore = ["utils", "auditlogs", "help", "wolfpack"]
            if not cogs:
                  cogs = [cog[:-3] for cog in os.listdir("cogs") if cog.endswith("py")]
                  for filename in cogs:
                        if filename is None or filename in ignore or filename in self.load_after_ready:
                              continue
                        cog = filename.capitalize()
                        try:
                              bot.load_extension(f"cogs.{filename}")
                              loaded.append(cog)
                        except Exception as e:
                              errors.append(f"{type(e).__name__}: {e}")
            else:
                  for filename in cogs:
                        if filename in ignore:
                              continue
                        cog = filename.capitalize()
                        try:
                              bot.load_extension(f"cogs.{filename}")
                              loaded.append(cog)
                        except Exception as e:
                              errors.append(f"{type(e).__name__}: {e}")

            loaded = humanize_list(loaded)
            print(f"Loaded: {loaded}")
            if len(errors) > 0:
                  print(f"Errors: {errors}")


async def get_prefix(bot, message):
      if not message.guild:
            return "."
      guild_id = str(message.guild.id)
      prefixes = bot.guild_prefixes.get(guild_id, None)
      if prefixes is None:
            return "."
      elif "." not in prefixes:
            prefixes.append(".")
      return prefixes

intents = discord.Intents(guilds=True, members=True, voice_states=True, presences=True, messages=True, reactions=True, typing=True)
bot = Bot(intents=intents, command_prefix=get_prefix, description=desc, case_insensitive=True, owner_id=settings["ownerid"])

@bot.event
async def on_ready():
      if not hasattr(bot, "start_time"):
            bot.start_time = datetime.utcnow()
      if not hasattr(bot, "invite_tracker"):
            bot.invite_tracker = DiscordUtils.InviteTracker(bot)
      await bot.invite_tracker.cache_invites()
      print("Cached guild invites")
      bot_appinfo = await bot.application_info()
      bot.invite_url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(permissions=8))
      bot._last_exception = None
      print("Loading cogs that need to be loaded after ready...")
      bot.load_cogs(bot.load_after_ready)
      print(
            f"""
Discord.py:       {discord.__version__}
Python:           {platform.python_version()}
Connected as:     {bot.user}
Default Prefix:   .
Owner:            {bot_appinfo.owner}
      """
      )


@bot.event
async def on_connect():
      print(f"{bot.user} has been connected to Discord.")


@bot.event
async def on_disconnect():
      with open("prefixes.json", "w") as j:
            json.dump(bot.guild_prefixes, j, indent=6)
      print(f"{bot.user} has been disconnected from Discord.")


@bot.event
async def on_resumed():
      print(f"{bot.user} has been reconnected to Discord.")


@bot.event
async def on_command(ctx):
      if ctx.command.name == "eval":
            asyncio.sleep(0.5)
      msg = f"[{get_local_time().strftime('%x %X')}] {ctx.author} called {ctx.message.content}"
      if ctx.guild is None:
            msg += " in DMs"
      else:
            msg += f" in {ctx.guild.name}"
      print(msg)


@bot.event
async def on_message(message: discord.Message):
      if message.guild is None:
            print(f"{message.author} used dm'd {message.content}")
            return
      regex = []
      for word in bot.regex_words.keys():
            regex.append(str(word))
      for word in regex:
            pass
      if bot.user.mention in message.content:
            guild_prefixes = await get_prefix(bot, message)
            if isinstance(guild_prefixes, list):
                  while "." in guild_prefixes:
                        guild_prefixes.remove(".")
            
            if not guild_prefixes:
                  msg = "Default Prefix of `.`"
            else:
                  msg = f"Guild Prefixes are: {humanize_list([f'`{x}`' for x in guild_prefixes])}"
            await message.channel.send(msg)
      await bot.process_commands(message)

# @bot.event
# async def on_command_error(ctx: commands.Context, error):
#       e = discord.Embed(title=f"**Error in command {ctx.command}.**", description=f"```py\n{str(errors=error)}```", timestamp=get_time())
#       await ctx.send(embed=e)


# @bot.event
# async def on_error(error, *args, **kwargs):
#       bot._last_exception = error


class ExitCodes(IntEnum):
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART = 26


class Owner(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="cogs", usage=".cogs")
      @commands.is_owner()
      async def _cogs(self, ctx: commands.Context):
            all_cogs = [cog[:-3].capitalize() for cog in os.listdir("cogs") if cog.endswith("py")]
            loaded = sorted([extension[5:].capitalize() for extension in bot.extensions.keys()])
            unloaded = [cog for cog in all_cogs if cog not in loaded]
            loaded, unloaded = humanize_list(loaded), humanize_list(unloaded)

            msg = f"Loaded: {loaded}\nUnloaded: {unloaded}"
            await ctx.send(msg)


      @commands.command(name="shutdown", usage=".shutdown")
      @commands.is_owner()
      async def _shutdown(self, ctx, silently = False):
            """Shuts down the bot."""
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Shutting down...")
            with open("prefixes.json", "w") as j:
                  json.dump(bot.guild_prefixes, j, indent=6)
            await self.bot.logout()
            sys.exit(ExitCodes.SHUTDOWN)

      @commands.command(name="restart", usage=".restart", aliases=["rs"])
      @commands.is_owner()
      async def _restart(self, ctx, silently = False):
            """Attempts a bot restart."""
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Attempting Restart...")
            with open("prefixes.json", "w") as j:
                  json.dump(bot.guild_prefixes, j, indent=6)
            await self.bot.logout()
            sys.exit(ExitCodes.RESTART)

      @commands.command(name="reload", usage=".reload [cogs]", aliases=["rl"])
      @commands.is_owner()
      async def _reload(self, ctx, *cogs: str):
            """Reload cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to reload.")
            reloaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        self.bot.reload_extension(f"cogs.{cog.lower()}")
                        reloaded_cogs.append(cog.capitalize())
                  except Exception as e:
                        errors.append(e)
            if reloaded_cogs is not None and len(reloaded_cogs) > 0:
                  reloaded_cogs = humanize_list(reloaded_cogs)
                  await ctx.send(f"Reloaded: {reloaded_cogs}")
            if errors is not None and len(errors) > 0:
                  await ctx.send(f"Errors: {errors}")

      @commands.command(name="load", usage=".load [cogs]")
      @commands.is_owner()
      async def _load(self, ctx, *cogs: str):
            """Loads cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to load.")
            loaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        self.bot.load_extension(f"cogs.{cog.lower()}")
                        loaded_cogs.append(cog.capitalize())
                  except Exception as e:
                        errors.append(e)
            loaded_cogs = humanize_list(loaded_cogs)
            if loaded_cogs is not None and len(loaded_cogs) > 0:
                  await ctx.send(f"Loaded: {loaded_cogs}")
            if errors is not None and len(errors) > 0:
                  await ctx.send("Errors: {}".format(errors))

      @commands.command(name="unload", usage=".unload [cogs]")
      @commands.is_owner()
      async def _unload(self, ctx, *cogs: str):
            """Unload cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to unload.")
            unloaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        self.bot.unload_extension(f"cogs.{cog.lower()}")
                        unloaded_cogs.append(cog.capitalize())
                  except Exception as e:
                        errors.append(e)
            unloaded_cogs = humanize_list(unloaded_cogs)
            if unloaded_cogs is not None and len(unloaded_cogs) > 0:
                  await ctx.send(f"Unloaded: {unloaded_cogs}")
            if errors is not None and len(errors) > 0:
                  await ctx.send(f"Errors: {errors}")


try:
      bot.add_cog(Owner(bot))
      print("Loaded Owner commands.")
except Exception as e:
      print(f"Could not load Owner commands.\nError: {e}")

bot.load_cogs()

try:
      bot.run(settings["token"])
except KeyboardInterrupt:
      print("How dare you..")

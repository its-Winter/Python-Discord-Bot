import discord
from discord import message
from discord.ext import commands
from discord.ext.commands import context, errors
from discord.ext.commands import core
import contextlib
import os, sys
import json
import platform
import asyncio
import arrow
import logging
from enum import IntEnum

from cogs.utils import (
      humanize_list,
      bold
)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s :: %(message)s')
# filehandler = logging.FileHandler(filename='Discord.log', mode='a', encoding='utf-8')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s :: %(message)s')


with open('settings.json', 'r') as j:
      settings = json.load(j)

if settings["prefix"] is None:
      choice = ""
      print("There is no prefix set, what would you like to make it? One character allowed.")
      while len(choice) != 1:
            choice = input("> ")
            if len(choice) != 1:
                  print(f"'{choice}' is not a valid prefix, try again.")
                  continue

      settings["prefix"] = str(choice)

      with open('settings.json', 'w') as j:
            json.dump(settings, j, indent=6)

if settings["token"] is None:
      choice = ""
      print("There is no token set in settings. Please give a token to use.")
      while len(choice) < 50:
            choice = input("> ")
            if len(choice) < 50:
                  print(f"Invalid token: '{choice}'")
                  continue

      settings["token"] = str(choice)

      with open('settings.json', 'w') as j:
            json.dump(settings, j, indent=6)

desc = "I'm {bot name here}! Originally a project to learn python from scratch, and soon to be fully public!"
bot = commands.AutoShardedBot(command_prefix=settings["prefix"], description=desc, case_insensitive=True, owner_id=settings["ownerid"])

@bot.event
async def on_ready():
      bot.start_time = arrow.utcnow()
      # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Winter develop me."))
      bot_appinfo = await bot.application_info()
      bot.invite_url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(permissions=8))
      bot._last_exception = None
      print(
            f"""\n
Discord.py:       {discord.__version__}
Python:           {platform.python_version()}
Connected as:     {bot.user}
Prefix:           {bot.command_prefix}
Owner:            {bot_appinfo.owner}
      """
      )

@bot.event
async def on_connect():
      print(f"{bot.user} has been connected to Discord.")

@bot.event
async def on_disconnect():
      print(f"{bot.user} has been disconnected from Discord.")

@bot.event
async def on_message(message):
      await bot.process_commands(message)

@bot.event
async def on_command(ctx):
      msg = f"[{arrow.now('US/Eastern').strftime('%x %X')}] {ctx.message.author} called {ctx.message.content}"
      if ctx.message.guild is None:
            msg += " in DMs"
      else:
            msg += f" in {ctx.guild.name}"
      print(msg)

def loadallcogs():
      # loads cogs
      loaded = []
      errors = []
      ignore = ["Utils", "Auditlogs"]
      for cog in os.listdir("cogs"):
            if cog.endswith("py"):
                  filename = cog[:-3]
                  cog = filename.capitalize()
                  if cog is None or cog in ignore:
                        continue
                  try:
                        bot.load_extension(f"cogs.{filename}")
                        loaded.append(cog)
                  except Exception as e:
                        errors.append(e)
      
      loaded = humanize_list(loaded)
      print(f"Loaded: {loaded}")
      if len(errors) > 0:
            print(f"Errors: {errors}")

class ExitCodes(IntEnum):
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART = 26

class Owner(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="shutdown")
      @commands.is_owner()
      async def _shutdown(self, ctx, silently = False):
            """Shuts down the bot."""
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Shutting down...")
            await ctx.bot.logout()
            sys.exit(ExitCodes.SHUTDOWN)

      @commands.command(name="restart", aliases=["rs"])
      @commands.is_owner()
      async def _restart(self, ctx, silently = False):
            """Attempts a bot restart."""
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Attempting Restart...")
            await bot.logout()
            sys.exit(ExitCodes.RESTART)

      @commands.command(name="reload", aliases=["rl"])
      @commands.is_owner()
      async def _reload(self, ctx, *cogs: str):
            """Reload cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to reload.")
            reloaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        ctx.bot.reload_extension(f"cogs.{cog.lower()}")
                        reloaded_cogs.append(cog.capitalize())
                  except Exception as e:
                        errors.append(e)
            if reloaded_cogs is not None and len(reloaded_cogs) > 0:
                  reloaded_cogs = humanize_list(reloaded_cogs)
                  await ctx.send(f"Reloaded: {reloaded_cogs}")
            if errors is not None and len(errors) > 0:
                  await ctx.send(f"Errors: {errors}")

      @commands.command(name="load")
      @commands.is_owner()
      async def _load(self, ctx, *cogs: str):
            """Loads cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to load.")
            loaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        ctx.bot.load_extension(f"cogs.{cog.lower()}")
                        loaded_cogs.append(cog.capitalize())
                  except Exception as e:
                        errors.append(e)
            loaded_cogs = humanize_list(loaded_cogs)
            if loaded_cogs is not None and len(loaded_cogs) > 0:
                  await ctx.send(f"Loaded: {loaded_cogs}")
            if errors is not None and len(errors) > 0:
                  await ctx.send("Errors: {}".format(errors))

      @commands.command(name="unload")
      @commands.is_owner()
      async def _unload(self, ctx, *cogs: str):
            """Unload cogs."""
            if not cogs:
                  return await ctx.send("Please call with cogs to unload.")
            unloaded_cogs = []
            errors = []
            for cog in cogs:
                  try:
                        ctx.bot.unload_extension(f"cogs.{cog.lower()}")
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
loadallcogs()
try:
      bot.run(settings["token"])
except KeyboardInterrupt:
      print("How dare you..")

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

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s :: %(message)s')
filehandler = logging.FileHandler(filename='Discord.log', mode='a', encoding='utf-8')
handler = logging.StreamHandler(stream=sys.stdout)

corelog = logging.getLogger('Core')
coglog = logging.getLogger('Cogs')

corelog.addHandler(filehandler)
coglog.addHandler(filehandler)


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

bot = commands.AutoShardedBot(command_prefix=settings["prefix"], description="Bot", case_insensitive=True, owner_id=settings["ownerid"])

@bot.event
async def on_ready():
      bot.start_time = arrow.utcnow()
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Winter develop me."))
      bot_appinfo = await bot.application_info()
      corelog.info(
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
      corelog.info(f"{bot.user} has been connected to Discord.")

@bot.event
async def on_disconnect():
      corelog.info(f"{bot.user} has been disconnected from Discord.")

@bot.event
async def on_message(message):
      await bot.process_commands(message)

@bot.event
async def on_command(ctx):
      msg = f"[{arrow.now('US/Eastern').strftime('%x %X')}] {ctx.message.author} called {ctx.message.content}"
      if ctx.message.guild is None:
            msg += " in DMs"
      corelog.info(msg)

def loadallcogs():
      # loads cogs
      for cog in os.listdir("cogs"):
            if cog.endswith("py"):
                  filename = cog[:-3]
                  if filename is None:
                        continue
                  try:
                        bot.load_extension(f"cogs.{filename}")
                        coglog.info(f"[Cogs] Cog Loaded: {filename}")
                  except Exception as e:
                        coglog.info(f"[Cogs] Error loading cog: {filename}; Error: {e}")

class Exitcodes():
      SHUTDOWN = 0
      CRITICAL = 1
      RESTART = 26

class Owner(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="shutdown")
      @commands.is_owner()
      async def _shutdown(self, ctx, silently = False):
            """Kills the bot"""
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Shutting down...")
            await ctx.bot.logout()
            exit(Exitcodes.SHUTDOWN)

      @commands.command(name="restart")
      @commands.is_owner()
      async def _restart(self, ctx, silently = False):
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Attempting Restart...")
            await bot.logout()
            exit(Exitcodes.RESTART)

      # @commands.command(name="invite")
      # @commands.is_owner()
      # async def _invite(self, ctx):
      #       await ctx.send(bot.invitelink)

try:
      bot.add_cog(Owner(bot))
      coglog.info("[Main] Loaded Owner commands.")
except Exception as e:
      coglog.info(f"[Main] Could not load Owner commands. Error: {e}")

loadallcogs()
try:
      bot.run(settings["token"])
except KeyboardInterrupt:
      corelog.info("How dare you..")

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

logging.basicConfig(level=logging.INFO)


with open('settings.json', 'r') as j:
      settings = json.load(j)

bot = commands.AutoShardedBot(command_prefix=settings["prefix"], description="Bot", case_insensitive=True, owner_id=settings["ownerid"])

@bot.event
async def on_ready():
      bot.start_time = arrow.utcnow()
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Winter develop me on stream."))
      bot_appinfo = await bot.application_info()
      logging.info(
            f" \n"
            f"Discord.py:       {discord.__version__}\n"
            f"Python:           {platform.python_version()}\n"
            f"Connected as:     {bot.user}\n"
            f"Prefix:           {bot.command_prefix}\n"
            f"Owner:            {bot_appinfo.owner}\n"
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
      msg = f"{arrow.now('US/Eastern').strftime('%x %X')} | {ctx.message.author} called {ctx.message.content}"
      if ctx.message.guild is None:
            msg += " in DMs"
      print(msg)

@bot.event
async def on_error(event, *args, **kwargs):
      await event.send("event", event, "args", args, "kwargs", kwargs)

def loadallcogs():
      # loads cogs
      for cog in os.listdir("cogs"):
            if cog.endswith("py"):
                  filename = cog[:-3]
                  if filename is None:
                        continue
                  try:
                        bot.load_extension(f"cogs.{filename}")
                        print(f"[Cogs] Cog Loaded: {filename}")
                  except Exception as e:
                        print(f"[Cogs] Error loading cog: {filename}; Error: {e}")

class Exitcodes():
      SHUTDOWN = 0
      CRITICAL = 1
      RESTART = 26

class Owner(commands.Cog, name="Owner"):
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
            sys.exit(Exitcodes.SHUTDOWN)

      @commands.command(name="restart")
      @commands.is_owner()
      async def _restart(self, ctx, silently = False):
            with contextlib.suppress(discord.HTTPException):
                  if not silently:
                        await ctx.send("Attempting Restart...")
            await bot.logout()
            exit(int(Exitcodes.RESTART))

      # @commands.command(name="invite")
      # @commands.is_owner()
      # async def _invite(self, ctx):
      #       await ctx.send(bot.invitelink)

try:
      bot.add_cog(Owner(bot))
      print("[Main] Loaded Owner commands.")
except Exception as e:
      print(f"[Main] Could not load Owner commands. Error: {e}")

loadallcogs()
try:
      bot.run(settings["token"])
except KeyboardInterrupt:
      print("How dare you..")

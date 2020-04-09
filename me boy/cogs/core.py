import sys
import arrow
import time
import asyncio
import discord
import contextlib
import platform
from discord import utils
from discord.ext import commands
from discord.ext.commands import errors, core
from basefuncs import BaseFuncs

class Core(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="hello")
      async def _hello(self, ctx):
            """a basic hello command"""
            if ctx.guild is None:
                  await ctx.send(f"Hello, {ctx.author.mention}! suck my peen and get out of my dms.")
            else:
                  await ctx.send(f"Hello, {ctx.author.mention}! suck my peen.")
            print('also suck the console''s pp.')

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
                  uptimestr = BaseFuncs.botuptime(self)
                  e = discord.Embed(title="Uptime", description=f"{ctx.bot.user.mention} has been online for ```{uptimestr}.```", color=discord.Color.green())
                  e.set_footer(text=f"summoned by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name='nsfwcheck')
      @commands.guild_only()
      async def _checknsfw(self, ctx):
            if ctx.channel.nsfw:
                  await ctx.send("Channel is set to NSFW.")
            else:
                  await ctx.send("Channel is not set to NSFW.")

      @commands.command(name="game")
      @commands.is_owner()
      async def _game(self, ctx, *, game):
            """Set's bot's playing status"""
            text = discord.Game(name=game)
            status = discord.Status.online
            await ctx.bot.change_presence(activity=text, status=status)
            await ctx.send(f"Set game to '{text}''")

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
                        await ctx.send(f"[Cogs] Reloaded {cog}")
                        print(f"[Cogs] Reloaded {cog}")
                  except Exception as e:
                        await ctx.send(f"[Cogs] Failed to reload {cog}\nError: {e}")


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
                              await ctx.send(f"[Cogs] Loaded {cog}")
                              print(f"[Cogs] Loaded {cog}")
                        except (errors.ExtensionError, errors.ExtensionFailed, errors.ExtensionNotLoaded, errors.NoEntryPointError) as e:
                              await ctx.send(f"[Cogs] Failed to load {cog}\nError: {e}")

      @commands.command(name="guildinfo", alias=["ginfo", "sinfo"])
      @commands.guild_only()
      async def _guildinfo(self, ctx):
            guild = ctx.guild
            uptimestr = BaseFuncs.botuptime()
            e = discord.Embed(color=discord.Color.blurple())
            e.set_author(name=guild.name, icon_url=guild.avatar_url)
            e.add_field(name=guild.name, value="penis")
            await ctx.send(embed=e)


def setup(bot):
      bot.add_cog(Core(bot))
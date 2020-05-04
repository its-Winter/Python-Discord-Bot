import asyncio
import platform
import time
import arrow
import discord
from discord.ext import commands
from discord.ext.commands import core

class Dev(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="dm")
      @commands.guild_only()
      async def _dm(self, ctx, user: discord.User = None, *, message: str = None):
            if user is None:
                  await ctx.send("Provided no user to search for.")
                  return
            else:
                  try:
                        user = ctx.guild.get_member_named(user)
                  except Exception as e:
                        await ctx.send(f"Failed to fetch user: {e}")
            
            if user is None:
                  await ctx.send(f"Failed to find that user: {user}")
                  return

            if user.bot is True:
                  await ctx.send("I cannot send messages to other bots pandejo.")
                  return

            if not user.dm_channel:
                  await user.create_dm()
            try:
                  message = " ".join(message)
                  e = discord.Embed(description=message, color=discord.Colour.blurple())
                  e.set_author(name=f"Message from {ctx.author}!", icon_url=ctx.author.avatar_url)
                  e.set_footer(text=f"Sent at {arrow.now(tz='US/Eastern').strftime('%X')} EST", icon_url=ctx.bot.user.avatar_url)
                  await user.send(embed=e)
                  await ctx.send(f"Sent your message to {user}.")
            except Exception as e:
                  await ctx.send(f"Failed to send message to {user}. {e}")


      @commands.command(name="guilds", aliases=["servers"])
      @commands.is_owner()
      async def _guilds(self, ctx):
            all_guilds = ctx.bot.guilds
            e = discord.Embed(color=discord.Color.blurple())
            e.set_author(name=ctx.bot.user, icon_url=ctx.bot.user.avatar_url)
            before = time.monotonic()
            async with ctx.typing():
                  for guild in all_guilds:
                        value = f"```ini\n[Members]: {guild.member_count}\n[Shard]: {guild.shard_id}\n[Id]: {guild.id}```"
                        e.add_field(name=guild.name, value=value)
                  spent = round((time.monotonic() - before) * 1000)
                  e.set_footer(text=f"{ctx.author} | {spent} ms", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="dmid")
      @commands.is_owner()
      async def _dmid(self, ctx, id, *message):
            if not isinstance(id, str):
                  await ctx.send("You have not entered a valid ID")
                  return
            try:
                  user = await ctx.bot.fetch_user(id)
            except Exception as e:
                  await ctx.send(f"Error happened while trying to fetch user.\n{e}")
                  return

            if user.bot is True:
                  await ctx.send("I cannot send messages to bots")
                  return
            if not user.dm_channel:
                  await user.create_dm()
            
            message = " ".join(message)
            e = discord.Embed(description=message, color=discord.Color.blurple())
            e.set_author(name=f"Message from {ctx.author}!", icon_url=ctx.author.avatar_url)
            e.set_footer(text=f"Sent at {arrow.now(tz='US/Eastern').strftime('%X')} EST", icon_url=ctx.bot.user.avatar_url)
            try:
                  await user.send(embed=e)
            except Exception as e:
                  await ctx.send(f"Error while sending embed. {e}")
            await ctx.send(f"Message has been sent to {user}")

def setup(bot):
      bot.add_cog(Dev(bot))
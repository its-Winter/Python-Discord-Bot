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
      async def _dm(self, ctx, user, *message):
            user = ctx.guild.get_member_named(user)
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


      @commands.command(name="guilds")
      @commands.is_owner()
      async def guilds(self, ctx):
            all_guilds = ctx.bot.guilds
            e = discord.Embed(color=discord.Color.blurple())
            e.set_author(name=ctx.bot.user, icon_url=ctx.bot.user.avatar_url)
            before = time.monotonic()
            async with ctx.typing():
                  for guild in all_guilds:
                        value = f"```py\nmembers: {guild.member_count}\nShard: {guild.shard_id}\nId: {guild.id}```"
                        e.add_field(name=guild.name, value=value)
                  spent = round((time.monotonic() - before) * 1000)
                  e.set_footer(text=f"{ctx.author} | {spent} ms", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)


def setup(bot):
      bot.add_cog(Dev(bot))
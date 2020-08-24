import discord
import json
import asyncio
from discord.ext import commands
from typing import (
      Union,
      List,
)

class Admin(commands.Cog):

      def __init__(self, bot):
            self.bot = bot

      def cog_unload(self):
            pass

      @commands.group(name="purge")
      @commands.bot_has_guild_permissions(manage_messages=True)
      @commands.has_permissions(manage_messages=True)
      async def _purge(self, ctx):
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_purge.command(name="bot")
      async def _bot_messages(self, ctx, limit: int = 20, oldest_first = True):
            def is_bot(m):
                  return m.author.id == ctx.bot.user.id
            messages = await ctx.channel.purge(check=is_bot, limit=limit, oldest_first=oldest_first)
            msg = f"Deleted a message from myself." if len(messages) == 1 else f"Deleted {len(messages)} messages from myself."
            await ctx.send(msg)

      @_purge.command(name="before")
      async def _before(self, ctx, message, limit: int = 20, oldest_first = True):
            messages = await ctx.channel.purge(limit=limit, before=message, oldest_first=oldest_first)
            msg = f"Deleted a message." if len(messages) == 1 else f"Deleted {len(messages)} messages."
            await ctx.send(msg)

      @_purge.command(name="after")
      async def _after(self, ctx, message, limit: int = 20, oldest_first = True):
            messages = await ctx.channel.purge(limit=limit, after=message, oldest_first=oldest_first)
            msg = f"Deleted a message." if len(messages) == 1 else f"Deleted {len(messages)} messages."
            await ctx.send(msg)

def setup(bot):
      bot.add_cog(Admin(bot))
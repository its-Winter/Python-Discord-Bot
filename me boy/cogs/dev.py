import asyncio
import platform
import time
import arrow
import discord
from discord.ext import commands
from discord.ext.commands import core
from cogs.utils import bordered, box, is_allowed

class Dev(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="border")
      @commands.is_owner()
      async def _border_ig(self, ctx, *columns, ascii_border: bool = False):
            result = bordered(*columns, ascii_border=ascii_border)
            await ctx.send(box(result))

      @commands.command(name="test")
      @is_allowed(261401343208456192)
      async def only_germ(self, ctx):
            await ctx.send(f"fuck you too {ctx.author.mention}")

def setup(bot):
      bot.add_cog(Dev(bot))
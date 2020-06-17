import asyncio
import platform
import time
import arrow
import textwrap
import discord
import inspect
import subprocess, threading
from discord.ext import commands
from discord.ext.commands import core
from cogs.utils import bordered, box, is_allowed, hastepaste
from asyncio.subprocess import PIPE, STDOUT
from subprocess import Popen
from time import time

class Dev(commands.Cog):
      def __init__(self, bot):
            self.bot = bot
            self.env = {}

      def sanitize(self, s):
            return s.replace('`', '′')

      @commands.command(name="border")
      @commands.guild_only()
      async def _border_ig(self, ctx, *columns, ascii_border: bool = True):
            result = bordered(*columns, ascii_border=ascii_border)
            await ctx.send(box(result))

      @commands.command(name="test")
      @is_allowed(261401343208456192)
      async def only_germ(self, ctx):
            await ctx.send(f"fuck you too {ctx.author.mention}")

      @commands.command(name="source")
      @commands.is_owner()
      async def _source(self, ctx, *, command: str):
            """ Shows the source code of a command. """
            cmd = self.bot.get_command(command)

            if not cmd:
                  return await ctx.send('No command with that name exists.')

            source = inspect.getsource(cmd.callback)

            if len(source) > 1990:
                  paste = await hastepaste(source)
                  await ctx.send(f'Source too big, uploaded to HastePaste: <{paste}>')
            else:
                  await ctx.send(f'```py\n{source}\n```')

      @commands.command(name="eval")
      @commands.is_owner()
      async def _eval(self, ctx, *, code: str):
            """ Evaluate Python code """
            if code == 'exit()':
                  self.env.clear()
                  return await ctx.send('Environment cleared')

            player = self.bot.lavalink.player_manager.players.get(ctx.guild.id) if ctx.guild else None

            self.env.update({
                  'self': self,
                  'bot': self.bot,
                  'ctx': ctx,
                  'message': ctx.message,
                  'channel': ctx.message.channel,
                  'guild': ctx.message.guild,
                  'author': ctx.message.author,
                  'player': player
            })

            if code.startswith('```py'):
                  code = code[5:]

            code = code.strip('`').strip()

            _code = """
async def func():
      try:
{}
      finally:
            self.env.update(locals())
""".format(textwrap.indent(code, " " * 12))

            _eval_start = time() * 1000

            try:
                  exec(_code, self.env)
                  output = await self.env['func']()

                  if output is None:
                        output = ''
                  elif not isinstance(output, str):
                        output = f'\n{repr(output) if output else str(output)}\n'
                  else:
                        output = f'\n{output}\n'
            except Exception as e:
                  output = f'\n{type(e).__name__}: {e}\n'

            _eval_end = time() * 1000

            code = code.split('\n')
            s = ''
            for i, line in enumerate(code):
                  s += '>>> ' if i == 0 else '... '
                  s += line + '\n'

            _eval_time = _eval_end - _eval_start
            message = f'{s}{output}# {_eval_time:.3f}ms'

            try:
                  await ctx.send(f'```py\n{self.sanitize(message)}```')
            except discord.HTTPException:
                  paste = await hastepaste(message)
                  await ctx.send(f'Eval result: <{paste}>')


      @commands.command(aliases=["shell"])
      @commands.is_owner()
      async def bash(self, ctx, *, arg):
            """Bash shell"""
            proc = await asyncio.create_subprocess_shell(arg, stdin=None, stderr=STDOUT, stdout=PIPE)
            out = await proc.stdout.read()
            msg = out.decode('utf-8')
            await ctx.send(f"```ini\n\n[Bash Input]: {arg}\n```")
            await ctx.send_interactive(msg, box_lang="py")

def setup(bot):
      bot.add_cog(Dev(bot))
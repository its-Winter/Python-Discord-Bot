import asyncio
import aiohttp
import platform
import time
import arrow
import textwrap
import discord
import inspect
import subprocess, threading
import re, ast
import io
import traceback
from discord.ext import commands
from discord.ext.commands import core
from cogs.utils import bordered, box, is_allowed, hastepaste, pagify
from contextlib import redirect_stdout
from asyncio.subprocess import PIPE, STDOUT
from subprocess import Popen
from time import time

START_CODE_BLOCK_RE = re.compile(r"^((```py)(?=\s)|(```))")

class Dev(commands.Cog):
      def __init__(self, bot):
            super().__init__()
            self.bot = bot
            self._last_result = None

      @staticmethod
      def sanitize(s):
            return s.replace('`', '′')

      @staticmethod
      def sanitize_output(ctx: commands.Context, input_: str) -> str:
            """Hides the bot's token from a string."""
            token = ctx.bot.http.token
            return re.sub(re.escape(token), "[EXPUNGED]", input_, re.I)

      @staticmethod
      def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith("```") and content.endswith("```"):
                  return START_CODE_BLOCK_RE.sub("", content)[:-3]

            # remove `foo`
            return content.strip("` \n")

      @staticmethod
      def async_compile(source, filename, mode):
            return compile(source, filename, mode, flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT, optimize=0)

      @staticmethod
      def get_syntax_error(e):
            """Format a syntax error to send to the user.
            Returns a string representation of the error formatted as a codeblock.
            """
            if e.text is None:
                  return box("{0.__class__.__name__}: {0}".format(e), lang="py")
            return box(
                  "{0.text}\n{1:>{0.offset}}\n{2}: {0}".format(e, "^", type(e).__name__), lang="py"
            )

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
                  await ctx.send(box(source, lang="py"))

      @commands.command(name="eval")
      @commands.is_owner()
      async def _eval(self, ctx, *, body: str):
            """Execute asynchronous code.
            This command wraps code into the body of an async function and then
            calls and awaits it. The bot will respond with anything printed to
            stdout, as well as the return value of the function.
            The code can be within a codeblock, inline code or neither, as long
            as they are not mixed and they are formatted correctly.
            Environment Variables:
                ctx      - command invokation context
                bot      - bot object
                channel  - the current channel object
                author   - command author's member object
                message  - the command's message object
                discord  - discord.py library
                commands - redbot.core.commands
                _        - The result of the last dev command.
            """
            env = {
                  "bot": ctx.bot,
                  "ctx": ctx,
                  "channel": ctx.channel,
                  "author": ctx.author,
                  "guild": ctx.guild,
                  "message": ctx.message,
                  "asyncio": asyncio,
                  "aiohttp": aiohttp,
                  "discord": discord,
                  "commands": commands,
                  "_": self._last_result,
                  "__name__": "__main__",
            }

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = "async def func():\n%s" % textwrap.indent(body, " " * 6)

            try:
                  compiled = self.async_compile(to_compile, "<string>", "exec")
                  exec(compiled, env)
            except SyntaxError as e:
                  return await ctx.send(self.get_syntax_error(e))

            func = env["func"]
            result = None
            try:
                  with redirect_stdout(stdout):
                        result = await func()
            except:
                  printed = "{}{}".format(stdout.getvalue(), traceback.format_exc())
            else:
                  printed = stdout.getvalue()
                  await ctx.tick()

            if result is not None:
                  self._last_result = result
                  msg = "{}{}".format(printed, result)
            else:
                  msg = printed
            msg = self.sanitize_output(ctx, msg)

            for page in pagify(msg):    
                  await ctx.send(box(page, lang="py"))

      @commands.command(aliases=["shell"])
      @commands.is_owner()
      async def cmd(self, ctx, *, arg):
            """Bash shell"""
            proc = await asyncio.create_subprocess_shell(arg, stdin=None, stderr=STDOUT, stdout=PIPE)
            out = await proc.stdout.read()
            msg = out.decode('utf-8')
            await ctx.send(f"```ini\n\n[Command Prompt Input]: {arg}\n```")
            await ctx.send(box(msg, lang="cmd"))

def setup(bot):
      bot.add_cog(Dev(bot))
from discord.ext import commands
from collections.abc import Iterable
from typing import List, Sequence, Tuple, Optional, Union, SupportsInt
from babel.numbers import format_decimal
from random import randint
from urllib.parse import quote
from datetime import timezone, timedelta, datetime
import discord
import itertools
import aiohttp

_headers = {
      'User-Agent': 'Discord Bot (https://github.com/its-Winter/Python-Discord-Bot)',
      'Content-Type': 'application/x-www-form-urlencoded'
}

class utils:

      @staticmethod
      def randomize_colour(embed: discord.Embed) -> discord.Embed:
            embed.colour = discord.Color(value=randint(0x000000, 0xFFFFFF))
            return embed

      @staticmethod
      def get_user(guild: discord.Guild, user: Union[str, int, discord.Member, discord.User]):
            if isinstance(user, discord.User):
                  user = guild.get_member(user.id)
            elif isinstance(user, int):
                  user = guild.get_member(user)
            elif isinstance(user, str):
                  user = guild.get_member_named(user)
            
            return user

      @staticmethod
      def utc_to_local(utc_dt: datetime) -> datetime:
            return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

      @staticmethod
      def wolfpack():
            def predicate(ctx):
                  return ctx.guild.id == 336025135620423680
            return commands.check(predicate)

      @staticmethod
      def is_allowed(*ids: int):
            def predicate(ctx):
                  return ctx.author.id in ids
            return commands.check(predicate)

      @staticmethod
      def guilds_only(*ids: int):
            def predicate(ctx):
                  return ctx.guild.id in ids
            return commands.check(predicate)

      @staticmethod
      def nsfw_only():
            async def predicate(ctx):
                  if ctx.guild is None:
                        await ctx.send("really? dms? nah bro.")
                        return False
                  if ctx.channel.is_nsfw():
                        return True
                  else:
                        await ctx.send("This is not a nsfw channel.")
                        return False
            return commands.check(predicate)

      @staticmethod
      def botuptime(bot) -> str:
            uptime = datetime.utcnow() - bot.start_time
            totalseconds = uptime.total_seconds()
            seconds = int(totalseconds)
            periods = [
                  ("year", "years", 60 * 60 * 24 * 365),
                  ("month", "months", 60 * 60 * 24 * 30),
                  ("day", "days", 60 * 60 * 24),
                  ("hour", "hours", 60 * 60),
                  ("minute", "minutes", 60),
                  ("second", "seconds", 1),
            ]
            strings = []
            for period_name, plural_period_name, period_seconds in periods:
                  if seconds >= period_seconds:
                        period_value, seconds = divmod(seconds, period_seconds)
                        if period_value == 0:
                              continue
                        unit = plural_period_name if period_value > 1 else period_name
                        strings.append(f"{period_value} {unit}")
            uptimestr = Utils.humanize_list(strings)
            return uptimestr

      @staticmethod
      def italicize(text: str) -> str:
            return "*{}*".format(text)

      @staticmethod
      def bold(text: str) -> str:
            return "**{}**".format(text)

      @staticmethod
      def bold_italicize(text: str) -> str:
            return "***{}***".format(text)

      @staticmethod
      def underline(text: str) -> str:
            return "__{}__".format(text)

      @staticmethod
      def box(text: str, lang: str = "") -> str:
            ret = "```{}\n{}\n```".format(lang, text)
            return ret

      @staticmethod
      def inline(text: str) -> str:
            if "`" in text:
                  return "``{text}``".format(text)
            else:
                  return "`{text}`".format(text)

      @staticmethod
      def bordered(*columns, ascii_border: bool = False) -> str:
            borders = {
                  "TL": "-" if ascii_border else "┌",  # Top-left
                  "TR": "-" if ascii_border else "┐",  # Top-right
                  "BL": "-" if ascii_border else "└",  # Bottom-left
                  "BR": "-" if ascii_border else "┘",  # Bottom-right
                  "HZ": "-" if ascii_border else "─",  # Horizontal
                  "VT": "|" if ascii_border else "│",  # Vertical
            }

            sep = " " * 4  # Separator between boxes
            widths = tuple(max(len(row) for row in column) + 9 for column in columns)  # width of each col
            colsdone = [False] * len(columns)  # whether or not each column is done
            lines = [sep.join("{TL}" + "{HZ}" * width + "{TR}" for width in widths)]

            for line in itertools.zip_longest(*columns):
                  row = []
                  for colidx, column in enumerate(line):
                        width = widths[colidx]
                        done = colsdone[colidx]
                        if column is None:
                              if not done:
                                    # bottom border of column
                                    column = "{HZ}" * width
                                    row.append("{BL}" + column + "{BR}")
                                    colsdone[colidx] = True  # mark column as done
                              else:
                                    # leave empty
                                    row.append(" " * (width + 2))
                        else:
                              column += " " * (width - len(column))  # append padded spaces
                              row.append("{VT}" + column + "{VT}")

                  lines.append(sep.join(row))

            final_row = []
            for width, done in zip(widths, colsdone):
                  if not done:
                        final_row.append("{BL}" + "{HZ}" * width + "{BR}")
                  else:
                        final_row.append(" " * (width + 2))
            lines.append(sep.join(final_row))

            return "\n".join(lines).format(**borders)

      @staticmethod
      def humanize_list(items: Sequence[str]) -> str:
            if len(items) == 1:
                  return str(items[0])
            try:
                  return ", ".join(items[:-1]) + ", and " + items[-1]
            except IndexError:
                  return None

      def humanize_timedelta(
            self, *, timedelta: Optional[datetime] = None, seconds: Optional[SupportsInt] = None
            ) -> str:
            try:
                  obj = seconds if seconds is not None else timedelta.total_seconds()
            except AttributeError:
                  raise ValueError("You must provide either a timedelta or a number of seconds")

            seconds = int(obj)
            periods = [
                  ("year", "years", 60 * 60 * 24 * 365),
                  ("month", "months", 60 * 60 * 24 * 30),
                  ("day", "days", 60 * 60 * 24),
                  ("hour", "hours", 60 * 60),
                  ("minute", "minutes", 60),
                  ("second", "seconds", 1),
            ]
            strings = []
            for period_name, plural_period_name, period_seconds in periods:
                  if seconds >= period_seconds:
                        period_value, seconds = divmod(seconds, period_seconds)
                        if period_value == 0:
                              continue
                        unit = plural_period_name if period_value > 1 else period_name
                        strings.append(f"{period_value} {unit}")

            return self.humanize_list(strings)

      @staticmethod
      def humanize_number(val: Union[int, float]) -> str:
            return format_decimal(val, locale="en_US")

      @staticmethod
      def pagify(text: str, limit: int = 2000):
            """ Slices text into chunks to make it manageable """
            lines = text.split('\n')
            pages = []

            chunk = ''
            for line in lines:
                  if len(chunk) + len(line) > limit and len(chunk) > 0:
                        pages.append(chunk)
                        chunk = ''

                  if len(line) > limit:
                        _lchunks = len(line) / limit
                        for _lchunk in range(_lchunks):
                              s = limit * _lchunk
                              e = s + limit
                              pages.append(line[s:e])
                  else:
                        chunk += line + '\n'

            if chunk:
                  pages.append(chunk)

            return pages

      @staticmethod
      async def get_messages_for_deletion(
            *,
            channel: discord.TextChannel,
            number = None,
            check = lambda x: True,
            limit = None,
            before: Union[discord.Message, datetime] = None,
            after: Union[discord.Message, datetime] = None,
            delete_pinned: bool = False,
      ) -> List[discord.Message]:
            """
            Gets a list of messages meeting the requirements to be deleted.
            Generally, the requirements are:
            - We don't have the number of messages to be deleted already
            - The message passes a provided check (if no check is provided,
              this is automatically true)
            - The message is less than 14 days old
            - The message is not pinned
            Warning: Due to the way the API hands messages back in chunks,
            passing after and a number together is not advisable.
            If you need to accomplish this, you should filter messages on
            the entire applicable range, rather than use this utility.
            """

            # This isn't actually two weeks ago to allow some wiggle room on API limits
            two_weeks_ago = datetime.utcnow() - timedelta(days=14, minutes=-5)

            def message_filter(message):
                  return (
                      check(message)
                      and message.created_at > two_weeks_ago
                      and (delete_pinned or not message.pinned)
                  )

            if after:
                  if isinstance(after, discord.Message):
                        after = after.created_at
                  after = max(after, two_weeks_ago)

            collected = []
            async for message in channel.history(
                  limit=limit, before=before, after=after, oldest_first=False
            ):
                  if message.created_at < two_weeks_ago:
                        break
                  if message_filter(message):
                        collected.append(message)
                  if number is not None and number <= len(collected):
                        break

            return collected

      @staticmethod
      async def hastepaste(content: str):
            async with aiohttp.request('POST', 'https://hastepaste.com/api/create', data=f'raw=false&text={quote(content)}', headers=_headers) as res:
                  return await res.text() if res.status >= 200 and res.status < 400 else None
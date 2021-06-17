from discord.ext import commands
from collections.abc import Iterable
from typing import List, Sequence, Tuple, Optional, Union, SupportsInt
from random import randint
from urllib.parse import quote
from babel.numbers import format_decimal
from datetime import timezone, timedelta
import datetime
import discord
import itertools
import aiohttp

_headers = {
      'User-Agent': 'Discord Bot (https://github.com/its-Winter/Python-Discord-Bot)',
      'Content-Type': 'application/x-www-form-urlencoded'
}


def randomize_colour(embed: discord.Embed) -> discord.Embed:
      embed.colour = discord.Color(value=randint(0x000000, 0xFFFFFF))
      return embed


async def get_members(ctx: commands.Context, users: List):
      converter = commands.MemberConverter()
      members = []

      for user in users:
            if isinstance(user, discord.Member):
                  members.append(user)
                  continue
            try:
                  member = await converter.convert(ctx, user)
                  members.append(member)
            except commands.MemberNotFound:
                  continue

      return members


def get_message_embed(message):
      return message.embeds[0] if len(message.embeds) > 0 else None


def get_local_time() -> datetime.datetime:
      return datetime.datetime.utcnow()


def wolfpack():
      def predicate(ctx):
            return ctx.guild.id == 336025135620423680
      return commands.check(predicate)


def whitelisted_users(*ids: int):
      def predicate(ctx):
            return ctx.author.id in ids
      return commands.check(predicate)


def whitelisted_guilds(*ids: int):
      def predicate(ctx):
            return ctx.guild.id in ids
      return commands.check(predicate)


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


def botuptime(bot) -> str:
      uptime = datetime.datetime.utcnow() - bot.start_time
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
      uptimestr = humanize_list(strings)
      return uptimestr


def italicize(text: str) -> str:
      return "*{}*".format(text)


def bold(text: str) -> str:
      return "**{}**".format(text)


def bold_italicize(text: str) -> str:
      return "***{}***".format(text)


def underline(text: str) -> str:
      return "__{}__".format(text)


def box(text: str, lang: str = "") -> str:
      ret = "```{}\n{}\n```".format(lang, text)
      return ret


def inline(text: str) -> str:
      if "`" in text:
            return "``{text}``".format(text)
      else:
            return "`{text}`".format(text)


def get_event_colour(event_type: str) -> discord.Colour:
      colours = {
            "message_edit": discord.Colour.orange(),
            "message_delete": discord.Colour.dark_red(),
            "user_change": discord.Colour.greyple(),
            "role_change": discord.Colour.blue(),
            "role_added": discord.Colour.blue(),
            "role_removed": discord.Colour.red(),
            "role_create": discord.Colour.blue(),
            "role_delete": discord.Colour.dark_blue(),
            "voice_change": discord.Colour.magenta(),
            "user_join": discord.Colour.green(),
            "user_left": discord.Colour.dark_green(),
            "channel_change": discord.Colour.teal(),
            "channel_create": discord.Colour.teal(),
            "channel_delete": discord.Colour.dark_teal(),
            "guild_change": discord.Colour.blurple(),
            "emoji_change": discord.Colour.gold(),
            "invite_created": discord.Colour.blurple(),
            "invite_deleted": discord.Colour.blurple(),
      }
      colour = colours.get(event_type, discord.Colour.blurple())
      return colour


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


def humanize_list(items: Sequence[str]) -> str:
      if len(items) == 1:
            return str(items[0])
      try:
            return ", ".join(items[:-1]) + ", and " + items[-1]
      except IndexError:
            return None


def humanize_timedelta(
      *, timedelta: Optional[datetime.datetime] = None, seconds: Optional[SupportsInt] = None
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
      return humanize_list(strings)


def humanize_number(val: Union[int, float]) -> str:
      return format_decimal(val, locale="en_US")


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


async def get_messages_for_deletion(
      *,
      channel: discord.TextChannel,
      number = None,
      check = lambda x: True,
      limit = None,
      before: Union[discord.Message, datetime.datetime] = None,
      after: Union[discord.Message, datetime.datetime] = None,
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
      two_weeks_ago = datetime.datetime.utcnow() - timedelta(days=14, minutes=-5)
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


async def hastepaste(content: str):
      async with aiohttp.request('POST', 'https://hastepaste.com/api/create', data=f'raw=false&text={quote(content)}', headers=_headers) as res:
            return await res.text() if 200 <= res.status < 400 else None

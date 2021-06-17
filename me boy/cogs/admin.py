import discord
import asyncio
from discord.ext import commands
from typing import (
      List,
      Optional,
      Iterable
)
from cogs.utils import (
      get_messages_for_deletion,
)


class Admin(commands.Cog):

      def __init__(self, bot):
            self.bot = bot

      @staticmethod
      async def mass_purge(messages: List[discord.Message], channel: discord.TextChannel):
            """Bulk delete messages from a channel.
            If more than 100 messages are supplied, the bot will delete 100 messages at
            a time, sleeping between each action.
            Note
            ----
            Messages must not be older than 14 days, and the bot must not be a user
            account.
            Parameters
            ----------
            messages : `list` of `discord.Message`
                The messages to bulk delete.
            channel : discord.TextChannel
                The channel to delete messages from.
            Raises
            ------
            discord.Forbidden
                You do not have proper permissions to delete the messages or you’re not
                using a bot account.
            discord.HTTPException
                Deleting the messages failed.
            """
            while messages:
                  # discord.NotFound can be raised when `len(messages) == 1` and the message does not exist.
                  # As a result of this obscure behavior, this error needs to be caught just in case.
                  try:
                        await channel.delete_messages(messages[:100])
                  except discord.errors.HTTPException:
                        pass
                  messages = messages[100:]
                  await asyncio.sleep(1.5)

      @staticmethod
      async def slow_deletion(messages: Iterable[discord.Message]):
            """Delete a list of messages one at a time.
            Any exceptions raised when trying to delete the message will be silenced.
            Parameters
            ----------
            messages : `iterable` of `discord.Message`
                The messages to delete.
            """
            for message in messages:
                  try:
                        await message.delete()
                  except discord.HTTPException:
                        pass

      def cog_unload(self):
            pass

      @commands.group(name="purge")
      @commands.bot_has_guild_permissions(manage_messages=True)
      @commands.has_permissions(manage_messages=True)
      async def _purge(self, ctx):
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_purge.command(name="message", aliases=['messages'])
      async def purge_messages(self, ctx: commands.Context, limit: int = 5, delete_pinned: bool = False):
            """Delete the last X messages.
            Example:
                - `[p]cleanup messages 26`
            **Arguments:**
            - `<number>` The max number of messages to cleanup. Must be a positive integer.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel

            to_delete = await get_messages_for_deletion(channel=channel, number=limit, before=ctx.message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)

      @_purge.command(name="bot")
      async def _bot_messages(self, ctx: commands.Context, limit: int = 20, delete_pinned: bool = False):
            """Clean up command messages and messages from the bot.
            Can only cleanup custom commands and alias commands if those cogs are loaded.
            **Arguments:**
            - `<number>` The max number of messages to cleanup. Must be a positive integer.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            is_bot = lambda m: m.author.id == ctx.bot.user.id or m == ctx.message
            to_delete = await get_messages_for_deletion(channel=ctx.channel, check=is_bot, number=limit, before=ctx.message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            can_mass_purge: bool = ctx.channel.permissions_for(ctx.guild.me).manage_messages
            if can_mass_purge:
                  await self.mass_purge(to_delete, ctx.channel)
            else:
                  self.slow_deletion(to_delete)
            msg = f"Deleted a message from myself." if len(to_delete) == 1 else f"Deleted {len(to_delete)} messages from myself."
            await ctx.send(msg, delete_after=10)

      @_purge.command(name="user")
      async def purge_user(self, ctx: commands.Context, user: discord.Member, limit: int, delete_pinned: bool = False):
            """Delete the last X messages from a specified user.
            Examples:
                - `[p]cleanup user @Bob 2`
                - `[p]cleanup user Bob 6`
            **Arguments:**
            - `<user>` The user whose messages are to be cleaned up.
            - `<number>` The max number of messages to cleanup. Must be a positive integer.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel

            is_user = lambda m: m.author.id == user.id
            to_delete = await get_messages_for_deletion(channel=channel, check=is_user, number=limit, before=ctx.message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, ctx.channel)

            msg = f"Deleted {len(to_delete)} messages from {str(user)}."
            await ctx.send(msg)


      @_purge.command(name="before")
      async def _before(self, ctx: commands.Context, message: discord.Message, limit: int = 20, delete_pinned: bool = True):
            """Deletes X messages before the specified message.
            To get a message id, enable developer mode in Discord's
            settings, 'appearance' tab. Then right click a message
            and copy its id.
            **Arguments:**
            - `<message_id>` The id of the message to cleanup before. This message won't be deleted.
            - `<number>` The max number of messages to cleanup. Must be a positive integer.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel

            to_delete = await get_messages_for_deletion(channel=channel, number=limit, before=message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)

      @_purge.command(name="after")
      async def _after(self, ctx: commands.Context, message: discord.Message, limit: int = 20, delete_pinned: bool = False):
            """Delete all messages after a specified message.
            To get a message id, enable developer mode in Discord's
            settings, 'appearance' tab. Then right click a message
            and copy its id.
            **Arguments:**
            - `<message_id>` The id of the message to cleanup after. This message won't be deleted.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel
            
            to_delete = await get_messages_for_deletion(channel=channel, limit=limit, before=ctx.message, after=message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)

      @_purge.command(name="between")
      async def purge_between(self, ctx: commands.Context, one: discord.Message, two: discord.Message, delete_pinned: bool = False):
            """Delete the messages between Message One and Message Two, providing the messages IDs.
            The first message ID should be the older message and the second one the newer.
            Example:
                - `[p]cleanup between 123456789123456789 987654321987654321`
            **Arguments:**
            - `<one>` The id of the message to cleanup after. This message won't be deleted.
            - `<two>` The id of the message to cleanup before. This message won't be deleted.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel

            to_delete = await get_messages_for_deletion(channel=channel, before=one, after=two, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)


      @_purge.command(name="text")
      async def purge_text(self, ctx: commands.Context, text: str, limit: int = 5, delete_pinned: bool = False):
            """Delete the last X messages matching the specified text.
            Example:
                - `[p]cleanup text "test" 5`
            Remember to use double quotes.
            **Arguments:**
            - `<number>` The max number of messages to cleanup. Must be a positive integer.
            - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
            """
            channel = ctx.channel

            check = lambda m: text in m.content
            to_delete = await get_messages_for_deletion(channel=channel, number=limit, check=check, before=ctx.message, delete_pinned=delete_pinned)
            to_delete.append(ctx.message)
            self.mass_purge(to_delete, channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)

      
      @_purge.command(name="spam")
      async def purge_spam(self, ctx: commands.Context, limit: int = 50):
            """Deletes duplicate messages in the channel from the last X messages and keeps only one copy.
            Defaults to 50.
            **Arguments:**
            - `<number>` The number of messages to check for duplicates. Must be a positive integer.
            """
            msgs = []
            spam = []

            def is_spam(m: discord.Message):
                  if m.attachments:
                        return False
                  c = (m.author.id, m.content, [e.to_dict() for e in m.embeds])
                  if c in msgs:
                        spam.append(m)
                        return True
                  else:
                        msgs.append(c)
                        return False

            to_delete = await get_messages_for_deletion(channel=ctx.channel, check=is_spam, limit=limit, before=ctx.message)
            to_delete.append(ctx.message)
            await self.mass_purge(to_delete, ctx.channel)

            msg = f"Deleted {len(to_delete)} messages."
            await ctx.send(msg, delete_after=10)

      @commands.group(name="roles")
      @commands.bot_has_guild_permissions(manage_roles=True)
      async def _roles(self, ctx: commands.Context):
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_roles.command(name="add")
      async def _add_role(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
            if role in user.roles:
                  await ctx.send(f"{str(user)} already has {str(role)}")
                  return
            
            try:
                  await user.add_roles(role)
                  await ctx.send(f"Added {str(role)} to {str(user)}.")
            except discord.Forbidden:
                  await ctx.send("Insufficent Permissions.")
            except discord.HTTPException:
                  await ctx.send('Failed Operation')


      @commands.command(name="nickname", aliases=['nick'], usage="<user> <new nickname>")
      @commands.has_guild_permissions(manage_nicknames=True)
      async def _nickname(self, ctx: commands.Context, user: discord.Member, *, new_nick: Optional[str]):
            try:
                  await user.edit(nick=new_nick)
                  await ctx.send(f"{user.name} is now known as {user.display_name}")
            except discord.Forbidden:
                  await ctx.send("Insufficient Permissions.")


def setup(bot):
      bot.add_cog(Admin(bot))

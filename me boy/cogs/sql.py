import sqlite3
import discord
from discord.ext import commands
from typing import (
      Optional,
      Union,
      Sequence
)

class Config(commands.Cog):
      
      def __init__(self, bot):
            self.bot = bot

      def get_config(self, table: str, id: int) -> list:
            sql = f"""SELECT * FROM {table} WHERE user_id={id}"""
            with sqlite3.connect('main.db') as db:
                  cursor = db.cursor()
                  cursor.execute(sql)
                  results = cursor.fetchall()
            
            return results

      @commands.group(name="config")
      @commands.is_owner()
      async def _config(self, ctx):
            """Configuration... and stuff."""
            if ctx.invoked_subcommand is None:
                  return await ctx.send_help(ctx.command)
      
      @_config.command(name="fetchuser", aliases=["userfetch"])
      @commands.guild_only()
      async def _user_fetch(self, ctx, user: Optional[Union[discord.User, int, str]] = None):
            """testing databse stuff"""
            if user is None:
                  return await ctx.send("Nobody entered.")
            elif isinstance(user, discord.User):
                  fetched_user = user
            elif isinstance(user, str):
                  fetched_user = ctx.guild.get_member_named(str(user))
            elif isinstance(user, int):
                  fetched_user = ctx.bot.fetch_user(int(user))

            if fetched_user is None:
                  return await ctx.send(f"Failed to find {user}")
            
            check_table = """CREATE TABLE IF NOT EXISTS
                              fetched_users(user_id INTEGER, user_name TEXT)"""

            insert_statement = """INSERT INTO fetched_users VALUES (?, ?)"""
            values = (fetched_user.id, fetched_user.name)

            with sqlite3.connect('main.db') as db:
                  cursor = db.cursor()
                  cursor.execute(check_table)
                  cursor.execute(insert_statement, values)
                  db.commit()
            
            await ctx.message.add_reaction('✅')

      @_config.command(name="get")
      async def _get_config(self, ctx, id: int):
            await ctx.send(self.get_config('fetched_users', id))

def setup(bot):
      bot.add_cog(Config(bot))
import discord
import twitchio
import json
import asyncio
from discord.ext import commands
from datetime import timedelta

with open('settings.json', 'r') as j:
      settings = json.load(j)

TWITCH_API = settings["apis"]["twitch"]
TWITCH_BASE_URL = "https://twitch.tv/"

class Twitch_Cog(commands.Cog):
      
      def __init__(self, bot):
            self.bot = bot
            self.twitch_api = twitchio.client.Client(client_id=TWITCH_API[0], client_secret=TWITCH_API[1])

      def cog_unload(self):
            pass

      @commands.command(name="getstream")
      @commands.is_owner()
      async def _get_twitch_stream(self, ctx, user: str):
            twitch_stream = await self.twitch_api.get_stream(user)
            twitch_users = await self.twitch_api.get_users(user)
            twitch_user = twitch_users[0]
            if not twitch_stream and twitch_user:
                  await ctx.send(f"{twitch_user.display_name} is not live.")
                  return
            if not twitch_user:
                  await ctx.send(f"{user} is not a twitch user.")
                  return
            game = await self.twitch_api.get_games(twitch_stream['game_id'])
            game = game[0]['name']
            desc = f"""
            **[{twitch_stream['title']}]({TWITCH_BASE_URL + twitch_user.login})**
            Playing {game} for {twitch_stream['viewer_count']} viewers!"""
            embed = discord.Embed(colour=ctx.author.colour, description=desc)
            embed.set_author(name=f"{twitch_user.display_name} is now live on Twitch!", url=TWITCH_BASE_URL + twitch_user.login, icon_url=twitch_user.profile_image)
            embed.set_image(url=twitch_stream['thumbnail_url'].format(width="1920", height="1080"))
            embed.set_footer(text=f"twitch.tv/{twitch_user.login}")
            await ctx.send(embed=embed)




def setup(bot):
      bot.add_cog(Twitch_Cog(bot))
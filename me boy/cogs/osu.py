import discord
import json
import aiohttp
from discord import utils
from discord.ext import commands
from discord.ext.commands import errors, core


class Osu(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="osu")
      async def _osu(self, ctx, username: str = None):
            """Shows a osu user!"""
            if username is None or len(username) <= 0:
                  return await ctx.send("Please give an osu name to look up.")
                 
            with open('settings.json', 'r') as data:
                  apikey = json.load(data)["apis"]["osu"]

            if apikey is None or apikey == "":
                  return await ctx.send("Failed to find apikey.")
                  
            # Queries api to get osu profile
            headers = {"content-type": "application/json", "user-key": apikey}

            async with aiohttp.ClientSession() as session:
                  async with session.post(f"https://osu.ppy.sh/api/get_user?k={apikey}&u={username}", headers=headers) as response:
                        osu = await response.json()

            if osu:
                  # Build Embed
                  if ctx.guild:
                        embed = discord.Embed(color=ctx.guild.me.top_role.color)
                  else:
                        embed = discord.Embed(color=discord.Color.magenta())
                  embed.title = osu[0]["username"]
                  embed.url = "https://osu.ppy.sh/u/{}".format(osu[0]["user_id"])
                  embed.set_footer(text="Powered by the osu api!")
                  embed.add_field(name="Join date", value=osu[0]["join_date"][:10])
                  embed.add_field(name="Accuracy", value=osu[0]["accuracy"][:6])
                  embed.add_field(name="Level", value=osu[0]["level"][:5])
                  embed.add_field(name="Ranked score", value=osu[0]["ranked_score"])
                  embed.add_field(name="Rank", value=osu[0]["pp_rank"])
                  embed.add_field(name="Country rank ({})".format(osu[0]["country"]), value=osu[0]["pp_country_rank"])
                  embed.add_field(name="Playcount", value=osu[0]["playcount"])
                  embed.add_field(name="Total score", value=osu[0]["total_score"])
                  embed.add_field(name="Total seconds played", value=osu[0]["total_seconds_played"])
                  embed.set_thumbnail(url="https://a.ppy.sh/{}".format(osu[0]["user_id"]))
                  await ctx.send(embed=embed)
            else:
                  await ctx.send("No results.")

def setup(bot):
      bot.add_cog(Osu(bot))
import discord
import aiohttp
import asyncio
from discord.ext import commands
from cogs.utils import nsfw_only

valid_neko_args = [
      "anal",
      "4k",
      "ass",
      "pussy",
      "gonewild",
      "lewdkitsune",
      "hentai",
      "pgif",
]


class NSFW(commands.Cog):

      def __init__(self, bot):
            self.bot = bot
            self.session = aiohttp.ClientSession()

      async def cog_unload(self):
            await self.session.close()
            del self.session

      async def nekobot(self, imgtype: str):
            async with self.session.get("https://nekobot.xyz/api/image?type=%s" % imgtype) as res:
                  res = await res.json()
            return res.get("message")

      @nsfw_only()
      @commands.group(name="nsfw", invoke_without_command=True)
      @commands.cooldown(2, 5, commands.BucketType.user)
      async def _nsfw(self, ctx, requested: str):
            if ctx.invoked_subcommand is None:
                  if requested in valid_neko_args:
                        image = await self.nekobot(requested)
                  else:
                        await ctx.send("Invalid Argument.")
                        return
                  em = discord.Embed(color=ctx.author.colour)
                  em.set_author(name="Url to image", url=image)
                  em.set_image(url=image)
                  em.set_footer(text="Powered by Nekobot api.", icon_url=ctx.author.avatar_url)
                  await ctx.send(embed=em)
            else:
                  await ctx.send_help(ctx.command)

      @nsfw_only()
      @_nsfw.command(name="bomb")
      async def _nsfw_bomb(self, ctx, imgtype: str):
            for x in range(1, 6):
                  url = await self.nekobot(imgtype)
                  em = discord.Embed(colour=ctx.author.colour)
                  em.set_author(name=f"({x}/5) URL to image", url=url)
                  em.set_image(url=url)
                  em.set_footer(text="Powered by Nekobot api.", icon_url=ctx.author.avatar_url)

                  await ctx.send(embed=em)


def setup(bot):
      bot.add_cog(NSFW(bot))
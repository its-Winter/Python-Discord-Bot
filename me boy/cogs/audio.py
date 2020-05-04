import discord
import aiohttp
import os
from discord.ext import commands

class Audio(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="join", aliases=["connect", "summon"])
      async def _join(self, ctx):
            if ctx.author.voice.channel is None:
                  return await ctx.send("You're not connected to a voice channel yet!")
            else:
                  try:
                        vc = await ctx.author.voice.channel.connect()
                        vc.source = discord.PCMVolumeTransformer(vc.source)
                        music = os.listdir('music')
                        vc.source.volume = 0.2
                        vc.play(discord.FFmpegPCMAudio(music[0]))
                  except Exception as e:
                        await ctx.send(f"Problem joining. {e}")

                  if vc.is_connected():
                        await ctx.send(f"Connected to `{vc.channel}`")
                        vc.stop()

def setup(bot):
      bot.add_cog(Audio(bot))
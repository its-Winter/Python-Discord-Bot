import discord
from discord.ext import commands
from cogs.utils import Utils

class Guild_Specific(commands.Cog):

      def __init__(self, bot):
            self.bot = bot

      @Utils.guilds_only(742134895899574343)
      @commands.command(name="bonk")
      async def _bonk(self, ctx: commands.Context, user: discord.Member = None):
            if user is None:
                  await ctx.author.send("https://cdn.discordapp.com/attachments/742134896574595144/742986573632634900/image0.jpg")
                  await ctx.send(f"Get BONKED ||{ctx.author}||")
                  return
            else:
                  user = await Utils.get_user(ctx, user)
            
            try:
                  await user.send("https://cdn.discordapp.com/attachments/742134896574595144/742986573632634900/image0.jpg")
                  await ctx.send(f"Bonked {user.display_name}")
            except discord.Forbidden:
                  await ctx.send(f"Failed to bonk {user}")
            

def setup(bot):
      bot.add_cog(Guild_Specific(bot))
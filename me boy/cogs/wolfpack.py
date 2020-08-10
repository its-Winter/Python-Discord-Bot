import asyncio
import random
import discord
from discord.ext import commands
from cogs.utils import guilds_allowed

reactions = {
      "\N{WHITE HEAVY CHECK MARK}": 423840858777845761,
      # 580452557693124618: 580452860777594880,
      "\N{BELL}": 588589944189091840,
      "\N{BELL WITH CANCELLATION STROKE}": 588589934181482496,
}

messages = [
      "Leave your guns by the door.",
      "Leave the meat by the fireplace.",
      "Don't leave the dog outside.",
]

class WolfPack(commands.Cog):
      def __init__(self, bot):
            self.bot = bot
            self.guild = self.bot.get_guild(336025135620423680)
            self.guild_stuff = {
                  "verified": self.guild.get_role(423840858777845761),
                  "clean": self.guild.get_role(587624429777977354),
                  "dj": self.guild.get_role(580452860777594880),
                  "free": self.guild.get_channel(563733430320496641),
                  "rules": self.guild.get_channel(423849956370022401)
            }

      @guilds_allowed(336025135620423680)
      @commands.Cog.listener()
      async def on_raw_reaction_add(self, payload):
            if payload.channel_id == self.guild_stuff["rules"].id:
                  if self.guild_stuff["clean"] in payload.member.roles and str(payload.emoji) == "\N{WHITE HEAVY CHECK MARK}":
                        await payload.member.add_roles(self.guild_stuff["verified"])
                        await self.guild_stuff["rules"].send(f"Welcome {payload.member.mention}. {random.choice(messages)}", delete_after=5)
                  else:
                        try:
                              await payload.member.send(f"{payload.member.mention}, you are not verified by AltDentifier yet. please make sure you are cleared there before trying again.")
                        except discord.Forbidden:
                              await self.rules_channel.send(f"{payload.member.mention}, you are not verified by AltDentifier yet. please make sure you are cleared there before trying again.", delete_after=10)
            elif payload.channel_id == self.guild_stuff["free"].id:
                  if str(payload.emoji) in reactions.keys():
                        role = self.guild.get_role(reactions.get(str(payload.emoji)))
                        await payload.member.add_roles(role)
                  elif payload.emoji.id == 580452557693124618:
                        await payload.member.add_roles(self.dj_role)
      
      @guilds_allowed(336025135620423680)
      @commands.Cog.listener()
      async def on_raw_reaction_remove(self, payload):
            if payload.channel_id == self.guild_stuff["free"].id:
                  


def setup(bot):
      bot.add_cog(WolfPack(bot))
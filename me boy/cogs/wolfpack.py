import asyncio
import random
import discord
from datetime import datetime
from discord.ext import commands
from cogs.utils import utils

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
                  "rules": self.guild.get_channel(423849956370022401),
                  "modlog": self.guild.get_channel(471873478337757194),
            }

      @utils.guilds_only(336025135620423680)
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
                              await self.guild_stuff["rules"].send(f"{payload.member.mention}, you are not verified by AltDentifier yet. please make sure you are cleared there before trying again.", delete_after=10)
            elif payload.channel_id == self.guild_stuff["free"].id:
                  if str(payload.emoji) in reactions.keys():
                        role = self.guild.get_role(reactions.get(str(payload.emoji)))
                        await payload.member.add_roles(role)
                  elif payload.emoji.id == 580452557693124618:
                        await payload.member.add_roles(self.guild_stuff["dj"])
      
      @utils.guilds_only(336025135620423680)
      @commands.Cog.listener()
      async def on_raw_reaction_remove(self, payload):
            if payload.channel_id == self.guild_stuff["free"].id:
                  pass

      @utils.guilds_only(336025135620423680)
      @commands.Cog.listener()
      async def on_member_update(self, before, after):
            if len(before.roles) != len(after.roles):
                  e = discord.Embed()
                  e.set_author(name=f"{after.name} updated.", icon_url=after.avatar_url)
                  if (len(before.roles) - len(after.roles)) == 1:
                        role = [role for role in before.roles if role not in after.roles]
                        e.add_field(name="Role Removed", value=role[0].mention)
                        e.colour = self.get_event_colour("role_removed")
                  elif (len(after.roles) - len(before.roles)) == 1:
                        role = [role for role in after.roles if role not in before.roles]
                        e.add_field(name="Role Added", value=role[0].mention)
                        e.colour = self.get_event_colour("role_added")

                  if self.guild_stuff["modlog"].permissions_for(after.guild.me).view_audit_log:
                        action = discord.AuditLogAction.member_role_update
                        async for log in after.guild.audit_logs(limit=5, action=action):
                              if log.target.id == before.id:
                                    perp = log.user
                                    if log.reason:
                                          reason = log.reason
                                    else:
                                          reason = discord.Embed.Empty
                                    break
                              else:
                                    perp = discord.Embed.Empty
                        if perp:
                              e.add_field(name="Updated by", value=perp.mention)
                        if reason:
                              e.add_field(name="Reason", value=reason)
                  
                  e.set_footer(text=datetime.now().strftime("%H:%M:%S EST"), icon_url=perp.avatar_url if perp else None)
                  await self.guild_stuff["modlog"].send(embed=e)

      def get_event_colour(self, event_type: str) -> discord.Colour:
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
            colour = colours[event_type]
            return colour


def setup(bot):
      bot.add_cog(WolfPack(bot))
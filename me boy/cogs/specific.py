import discord
import random
import re
import json
from discord.ext import commands
from datetime import datetime
from cogs.utils import utils
from collections import defaultdict
from typing import List

bonks = [
      "https://cdn.discordapp.com/attachments/742134896574595144/742986573632634900/image0.jpg",
      "https://cdn.discordapp.com/attachments/742134896574595144/743684351140561037/image0.png",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936809196847144/image0.jpg",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936809460826162/image1.jpg",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936809846964285/image2.jpg",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936810190766197/image3.jpg",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936810413195334/image4.jpg",
      "https://cdn.discordapp.com/attachments/738258142353293403/743936810714923069/image5.jpg",
]

reactions = {
      "\N{WHITE HEAVY CHECK MARK}": 579884752253747201,
}

urlreg = re.compile(r"https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
image_url = re.compile(r"'(?:http\:|https\:)?\/\/.*\.(?:png|jpg|webm|gif)'")

class Guild_Specific(commands.Cog):

      def __init__(self, bot):
            self.bot = bot
            self.fuyu = self.bot.get_guild(399500360877867018)
            self.fuyu_channels = {
                  "welcome": self.fuyu.get_channel(579884546389049345),
                  "audit": self.fuyu.get_channel(471898099581845525),
            }
            self.fuyu_roles = {
                  "live": self.fuyu.get_role(567916817646092318),
                  "approved": self.fuyu.get_role(579884752253747201),
            }
            self.last_deleted_msgs = defaultdict(dict)

      def format_prefixes(self, prefixes: List[str]) -> str:
            if len(prefixes) == 1:
                  return f"`{prefixes[0]}`"
            try:
                  formatted = [f"`{x}`" for x in prefixes]
                  return utils.humanize_list(formatted)
            except IndexError:
                  return None

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
                  "user_left": discord.Colour.red(),
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

      @commands.Cog.listener()
      async def on_raw_message_delete(self, payload):
            guild_id = str(payload.guild_id)
            channel_id = str(payload.channel_id)
            if payload.cached_message.author.id == self.bot.user.id:
                  return
            self.last_deleted_msgs[guild_id][channel_id] = payload.cached_message

      @commands.command(name="snipe")
      async def _snipe(self, ctx):
            guild_messages = self.last_deleted_msgs.get(str(ctx.guild.id))
            deleted_msg = guild_messages.get(str(ctx.channel.id)) if guild_messages else None
            if guild_messages is None or deleted_msg is None:
                  await ctx.send("No deleted messages, yet.")
                  return

            desc = deleted_msg.description if isinstance(deleted_msg, discord.Embed) else deleted_msg.content
            
            e = discord.Embed(colour=discord.Colour.dark_red(), description=desc)
            msg = f"Sniped {deleted_msg.author.name}!" if deleted_msg.author.id != ctx.author.id else "Sniped yo self!"
            e.set_author(name=msg, icon_url=deleted_msg.author.avatar_url)
            e.set_footer(text=f"Sent at {deleted_msg.created_at.strftime('%B %d, %Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
            urls = re.findall(image_url, deleted_msg.content)
            if urls:
                  e.set_image(url=urls[0])
            await ctx.send(embed=e)
            

      @utils.guilds_only(399500360877867018)
      @commands.cooldown(1, 5, commands.BucketType.user)
      @commands.command(name="bonk")
      async def _bonk(self, ctx: commands.Context, user: discord.Member = None):
            if user is None:
                  await ctx.author.send(random.choice(bonks))
                  await ctx.send("you did it to yourself")
                  return
            else:
                  user = utils.get_user(ctx.guild, user)
                  if user is None:
                        await ctx.send(f"No user as: {user}")
            
            try:
                  await user.send(f"from {ctx.author.mention} {random.choice(bonks)}")
                  await ctx.send(f"Bonked {user.display_name}")
            except discord.Forbidden:
                  await ctx.send(f"Failed to bonk {user}")

      @utils.guilds_only(399500360877867018)
      @commands.cooldown(1, 3, commands.BucketType.user)
      @commands.command(name="quote")
      async def _quote(self, ctx, msg_id: int = None):
            if not isinstance(msg_id, int):
                  await ctx.send("no")
                  return
            quote_channel = ctx.guild.get_channel(746571034450329660)
            try:
                  message = await ctx.channel.fetch_message(msg_id)
            except discord.NotFound:
                  await ctx.send("Message not found.")
                  return
            except discord.HTTPException:
                  await ctx.send("Retrieving the message failed.")
                  return
            
            desc = message.description if isinstance(message, discord.Embed) else message.content

            e = discord.Embed(colour=message.author.color, description=desc)
            e.set_author(name=f"Quote from {message.author.name}", url=message.jump_url, icon_url=message.author.avatar_url)
            try:
                  urls = re.findall(urlreg, message.content)
            except TypeError:
                  urls = None

            attachment = message.attachments[0] if len(message.attachments) > 0 else None
            if urls or attachment:
                  e.set_image(url=attachment.url if attachment else urls[0])

            created_at = utils.utc_to_local(message.created_at)
            e.set_footer(text=f"Quoted by {ctx.author.name} ● {created_at.strftime('%B %d, %Y %H:%M:%S')} EST", icon_url=ctx.author.avatar_url)
            await quote_channel.send(embed=e, content=message.jump_url)
            await ctx.send("Quoted.")

      @commands.group(name="prefixes", aliases=["prefix"])
      async def _prefixes(self, ctx):
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_prefixes.command(name="remove", aliases=["rem", "rm"])
      @commands.has_permissions(manage_guild=True)
      async def _remove_prefix(self, ctx, prefix: str = None):
            if not prefix:
                  await ctx.send("Nothing Removed.")
                  return
            if not isinstance(prefix, str):
                  await ctx.send("Invalid Argument.")
                  return

            guild_id = str(ctx.guild.id)

            prefixes = ctx.bot.guild_prefixes
            res = prefixes.get(guild_id)
            if not res:
                  await ctx.send("Guild has no prefixes.")
                  return
            elif prefix in res:
                  ctx.bot.guild_prefixes.get(guild_id).pop(prefix)
                  await ctx.send(f"Removed Guild Prefix: {prefix}")
                  return

      @_prefixes.command(name="add")
      @commands.has_permissions(manage_guild=True)
      async def _add_prefix(self, ctx, *, prefix: str = None):
            if not prefix:
                  await ctx.send("Nothing Added.")
                  return
            if not isinstance(prefix, str):
                  await ctx.send("Invalid Argument.")
                  return

            guild_id = str(ctx.guild.id)

            prefixes = ctx.bot.guild_prefixes
            res = prefixes.get(guild_id)
            if res is None:
                  prefixes[guild_id] = [prefix]
            elif prefix in prefixes:
                  await ctx.send(f"{prefix} is already a prefix for this server.")
                  return
            else:
                  new_pre_list = res.append(prefix)
                  prefixes[guild_id] = new_pre_list
            ctx.bot.guild_prefixes = prefixes
            await ctx.send(f"Added {prefix} to guild prefixes.")

      @_prefixes.command(name="get")
      async def _get_prefixes(self, ctx):
            guild_prefixes = ctx.bot.guild_prefixes.get(str(ctx.guild.id))
            if guild_prefixes is None:
                  await ctx.send("Default Prefix.")
                  return
            else:
                  guild_prefixes.remove(".")
                  await ctx.send(f"Guild prefixes are: {self.format_prefixes(guild_prefixes)}")

      @_prefixes.command(name="update", hidden=True)
      @commands.is_owner()
      async def _update_prefixes(self, ctx):
            with open("prefixes.json", "w") as j:
                  json.dump(ctx.bot.guild_prefixes, j, indent=6)
            await ctx.send("Updated Prefixes file.")

      @_prefixes.command(name="match", hidden=True)
      @commands.is_owner()
      async def _match_prefixes(self, ctx):
            with open("prefixes.json", "r") as j:
                  file_json = json.load(j)
            ctx.bot.guild_prefixes = file_json
            await ctx.send("Updated Prefixes dict.")

      @commands.command(name="massroleadd", hidden=True)
      @commands.bot_has_permissions(manage_guild=True)
      @commands.is_owner()
      async def _mass_role_add(self, ctx, member: discord.Member, *, roles: List[discord.Role] = None):
            if not member:
                  await ctx.send("Did not specify a member.")
                  return
            if not roles:
                  await ctx.send("No roles added.")
                  return
            
            pass

      @commands.command(name="ensurestreaming")
      @utils.guilds_only(399500360877867018)
      @commands.has_permissions(manage_guild=True)
      @commands.bot_has_permissions(manage_guild=True, manage_roles=True)
      async def _ensure_streaming(self, ctx):
            uneffected_members = []
            for member in ctx.guild.members:
                  if any(a.type is discord.ActivityType.streaming for a in member.activities):
                        await member.add_roles(self.fuyu_roles["live"])
                  elif not any(a.type is discord.ActivityType.streaming for a in member.activities):
                        try:
                              await member.remove_roles(self.fuyu_roles["live"])
                        except:
                              uneffected_members.append(member.id)
                  else:
                        uneffected_members.append(member.id)
            if len(uneffected_members) == len(ctx.guild.members):
                  await ctx.send("No one is streaming.")

      @commands.Cog.listener()
      @commands.bot_has_permissions(manage_guild=True)
      async def on_member_update(self, before, after):
            if after.guild.id != self.fuyu.id:
                  return
            role = self.fuyu_roles["live"]
            if any(a.type is discord.ActivityType.streaming for a in after.activities):
                  await after.add_roles(role)
            if not any(a.type is discord.ActivityType.streaming for a in after.activities):
                  await after.remove_roles(role)


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

                  if self.fuyu_channels["audit"].permissions_for(after.guild.me).view_audit_log:
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
                                    perp = None
                        if perp:
                              e.add_field(name="Updated by", value=perp.mention)
                        if reason:
                              e.add_field(name="Reason", value=reason)
                  
                  e.set_footer(text=datetime.now().strftime("%H:%M:%S EST"), icon_url=perp.avatar_url if perp else None)
                  await self.fuyu_channels["audit"].send(embed=e)

      @commands.Cog.listener()
      async def on_member_remove(self, member):
            if member.guild.id != self.fuyu.id:
                  return
            e = discord.Embed(colour=self.get_event_colour("user_left"), description=f"**{member.mention} left the server.**")
            e.set_author(name=str(member))
            e.set_thumbnail(url=member.avatar_url)
            e.set_footer(text=f"ID: {member.id} • {datetime.now().strftime('%x')}")
            await self.fuyu_channels["audit"].send(embed=e)

      @commands.Cog.listener()
      async def on_member_join(self, member):
            if member.guild.id != self.fuyu.id:
                  return
            e = discord.Embed(colour=self.get_event_colour("user_join"), description=f"**{member.mention} joined the server.**")
            e.set_author(name=str(member))
            e.set_thumbnail(url=member.avatar_url)
            e.add_field(name="Account Created", value=utils.humanize_timedelta(member.created_at))
            e.set_footer(text=f"ID: {member.id} • {datetime.now().strftime('%x')}")
            await self.fuyu_channels["audit"].send(embed=e)


      @utils.guilds_only(399500360877867018)
      @commands.Cog.listener()
      @commands.bot_has_permissions(manage_guild=True)
      async def on_raw_reaction_add(self, payload):
            if payload.channel_id == self.fuyu_channels["welcome"].id:
                  if str(payload.emoji) in reactions.keys():
                        role = self.fuyu.get_role(reactions.get(str(payload.emoji)))
                        await payload.member.add_roles(role)
                        await self.fuyu_channels["welcome"].send(f"Welcome {payload.member.mention}.", delete_after=5)
            # elif payload.channel_id == self.guild_stuff["free"].id:
            #       if str(payload.emoji) in reactions.keys():
            #             role = self.guild.get_role(reactions.get(str(payload.emoji)))
            #             await payload.member.add_roles(role)


def setup(bot):
      bot.add_cog(Guild_Specific(bot))
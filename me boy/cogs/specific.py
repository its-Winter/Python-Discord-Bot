import discord, DiscordUtils
import random
import re
import json
from discord.ext import commands
from discord.ext.commands.converter import Greedy
from datetime import datetime
from cogs.utils import (
      humanize_list,
      humanize_timedelta,
      get_message_embed,
      get_members,
      get_messages_for_deletion,
      whitelisted_guilds,
      get_event_colour,
      get_local_time,
      randomize_colour,
)
from collections import defaultdict
from typing import (
      List,
      Optional,
      Union
)

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

audit_channels = {
      "399500360877867018": 471898099581845525,
      "652129382139297803": 652196698528940167,
      "336025135620423680": 471873478337757194,
      "227009051895005187": 674786287307456522,
      "655647530255777792": 664936087080140831,
      "505497908330889227": 507736456232697856,
      "529183098165002240": 593358461786390528,
      "233464844450398208": 643590408525447170,
}

reactions = defaultdict(dict)

with open("reactions.json", "r") as j:
      reactions = json.load(j)

urlreg = re.compile(r"https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
image_url = re.compile(r"'(?:http\:|https\:)?\/\/.*\.(?:png|jpg|webm|gif)'")


class Guild(commands.Cog):
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
            self.last_edited_msgs = defaultdict(dict)

      @commands.Cog.listener()
      async def on_invite_create(self, invite: discord.Invite):
            await self.bot.invite_tracker.update_invite_cache(invite)

      @commands.Cog.listener()
      async def on_invite_delete(self, invite: discord.Invite):
            await self.bot.invite_tracker.remove_invite_cache(invite)

      @commands.Cog.listener()
      async def on_guild_join(self, guild: discord.Guild):
            await self.bot.invite_tracker.update_guild_cache(guild)

      @commands.Cog.listener()
      async def on_guild_remove(self, guild: discord.Guild):
            await self.bot.invite_tracker.remove_guild_cache(guild)

      @staticmethod
      def format_prefixes(prefixes: List[str]) -> str:
            if len(prefixes) == 1:
                  return f"`{prefixes[0]}`"
            try:
                  formatted = [f"`{x}`" for x in prefixes]
                  return humanize_list(formatted)
            except IndexError:
                  return

      @commands.Cog.listener()
      async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
            guild_id = str(payload.guild_id)
            channel_id = str(payload.channel_id)
            author = payload.cached_message.author or None
            if author and author.id == self.bot.user.id:
                  return
            self.last_deleted_msgs[guild_id][channel_id] = payload.cached_message

      @commands.Cog.listener()
      async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
            guild_id = str(payload.data['guild_id'])
            channel_id = str(payload.channel_id)
            author = payload.cached_message.author or (await self.bot.get_guild(int(guild_id)).get_channel(int(channel_id)).fetch_message(int(payload.data['id'])))
            self.last_edited_msgs[guild_id][channel_id] = payload.cached_message or payload.data["content"]

      @commands.group(name="snipe", invoke_without_command=True)
      async def _snipe(self, ctx: commands.Context):
            guild_messages = self.last_deleted_msgs.get(str(ctx.guild.id))
            msg_in_q = guild_messages.get(str(ctx.channel.id)) if guild_messages else None
            if guild_messages is None or msg_in_q is None:
                  await ctx.send("No deleted messages, yet.")
                  return

            maybe_embed = get_message_embed(msg_in_q)
            desc = maybe_embed.description if maybe_embed is not None else msg_in_q.content

            e = discord.Embed(colour=discord.Colour.dark_red(), description=desc)
            msg = f"Sniped {msg_in_q.author.name}!" if msg_in_q.author.id != ctx.author.id else "Sniped yo self!"
            e.set_author(name=msg, icon_url=msg_in_q.author.avatar_url)
            e.set_footer(text=f"Sent at {msg_in_q.created_at.strftime('%B %d, %Y %H:%M:%S')}")
            e.timestamp = get_local_time()
            urls = re.findall(image_url, msg_in_q.content)
            if urls:
                  e.set_image(url=urls[0])
            await ctx.send(embed=e)

      @_snipe.command(name="edit")
      async def _edited_message(self, ctx: commands.Context):
            guild_message = self.last_edited_msgs.get(str(ctx.guild.id))
            msg_in_q = guild_message.get(str(ctx.channel.id)) if guild_message else None
            if guild_message is None or msg_in_q is None:
                  await ctx.send("No edited messages, yet.")
                  return

            maybe_embed = get_message_embed(msg_in_q)
            desc = maybe_embed.description if maybe_embed is not None else msg_in_q.content

            e = discord.Embed(colour=discord.Colour.dark_red(), description=desc)
            msg = f"Sniped {msg_in_q.author.name}'s edit!" if msg_in_q.author.id != ctx.author.id else "Sniped your own"
            e.set_author(name=msg, icon_url=msg_in_q.author.avatar_url)
            e.set_footer(text=f"Sent at {msg_in_q.created_at.strftime('%B %d, %Y %H:%M:%S')}")
            e.timestamp = get_local_time()
            urls = re.findall(image_url, msg_in_q.content)
            if urls:
                  e.set_image(url=urls[0])
            await ctx.send(embed=e)

      @commands.command(name="massbonk")
      @commands.is_owner()
      async def _massbonk(self, ctx: commands.Context,  *, users: Optional[str]):
            if users is None:
                  await ctx.message.delete()
                  return
            users = users.split("|")
            users = await get_members(ctx, users)
            await ctx.send(users)
            bonk = ctx.bot.get_command("bonk")
            for user in users:
                  await ctx.invoke(bonk, user)
            

      @whitelisted_guilds(399500360877867018)
      @commands.cooldown(1, 5, commands.BucketType.user)
      @commands.command(
            name="bonk",
            usage="<user>"
      )
      async def _bonk(self, ctx: commands.Context, *, user: discord.Member = None):
            """bonk?"""
            if not user:
                  await ctx.author.send(random.choice(bonks))
                  await ctx.send("you did it to yourself")
                  return
            try:
                  await user.send(f"from {ctx.author.mention} {random.choice(bonks)}")
                  await ctx.send(f"Bonked {user.display_name}")
            except discord.Forbidden:
                  await ctx.send(f"Failed to bonk {user}")

      @whitelisted_guilds(399500360877867018)
      @commands.command(name="brooklyn", aliases=['brook'])
      async def _brooklyn(self, ctx: commands.Context):
            pass

      @whitelisted_guilds(399500360877867018)
      @commands.cooldown(1, 3, commands.BucketType.user)
      @commands.command(name="quote")
      async def _quote(self, ctx: commands.Context, msg: Optional[discord.Message]):
            if not isinstance(msg, discord.Message):
                  await ctx.send("no")
                  return
            quote_channel = ctx.guild.get_channel(746571034450329660)
            
            maybe_embed = get_message_embed(msg)
            desc = maybe_embed.description if maybe_embed else msg.content

            e = discord.Embed(colour=msg.author.color, description=f"**[Quoted from #{msg.channel.name}]({msg.jump_url})**\n\n{desc}", timestamp=get_local_time())
            e.set_author(name="", icon_url=msg.author.avatar_url)
            try:
                  urls = re.findall(urlreg, msg.content)
            except TypeError:
                  urls = None

            attachment = msg.attachments[0] if len(msg.attachments) > 0 else None
            if urls or attachment:
                  e.set_image(url=attachment.url if attachment else urls[0])

            e.set_footer(text=f"Message sent on {msg.created_at.strftime('%B %d, at %Y %H:%M:%S')} EST")
            await quote_channel.send(embed=e)
            await ctx.send("Quoted.")

      @commands.group(name="prefixes", aliases=["prefix"])
      async def _prefixes(self, ctx):
            if ctx.invoked_subcommand is None:
                  await ctx.send_help(ctx.command)

      @_prefixes.command(name="remove", aliases=["rem", "rm"])
      @commands.has_permissions(manage_guild=True)
      async def _remove_prefix(self, ctx, prefix: Optional[str]):
            if not prefix:
                  await ctx.send("Nothing Removed.")
                  return
            if not isinstance(prefix, str):
                  await ctx.send("Invalid Argument.")
                  return

            guild_id = str(ctx.guild.id)

            res = ctx.bot.guild_prefixes.get(guild_id)
            try:
                  res.remove(".")
            except ValueError:
                  pass
            if not res:
                  await ctx.send("Guild has no prefixes.")
                  
                  return
            elif prefix in res:
                  ctx.bot.guild_prefixes.get(guild_id).remove(prefix)
                  await ctx.send(f"Removed Guild Prefix: {prefix}")


      @_prefixes.command(name="add")
      @commands.has_permissions(manage_guild=True)
      async def _add_prefix(self, ctx, prefix: str):
            if not prefix:
                  await ctx.send("Nothing Added.")
                  return
            if not isinstance(prefix, str):
                  await ctx.send("Invalid Argument.")
                  return

            guild_id = str(ctx.guild.id)

            prefixes: list = ctx.bot.guild_prefixes.get(guild_id)
            if not prefixes:
                  prefixes[guild_id] = [prefix]
            elif prefix in prefixes:
                  await ctx.send(f"{prefix} is already a prefix for this server.")
                  return
            else:
                  prefixes.append(prefix)
                  try:
                        prefixes.remove(".")
                  except ValueError:
                        pass
                  prefixes[guild_id] = prefixes
            ctx.bot.guild_prefixes = prefixes
            await ctx.send(f"Added {prefix} to guild prefixes.")

      @_prefixes.command(name="get")
      async def _get_prefixes(self, ctx):
            guild_prefixes: list = ctx.bot.guild_prefixes.get(str(ctx.guild.id))
            while "." in guild_prefixes:
                  guild_prefixes.remove(".")
            if not guild_prefixes:
                  await ctx.send("Default Prefix of `.`")
                  return
            else:
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

      @_prefixes.command(name="show", hidden=True)
      @commands.is_owner()
      async def _show_prefixes(self, ctx: commands.Context):
            await ctx.send(ctx.bot.guild_prefixes)

      @commands.command(name="massroleadd", hidden=True)
      @commands.bot_has_permissions(manage_guild=True)
      @commands.is_owner()
      async def _mass_role_add(self, ctx, member: discord.Member, *roles: discord.Role):
            if not member:
                  await ctx.send("Did not specify a member.")
                  return
            if not roles:
                  await ctx.send("No roles added.")
                  return

      @commands.command(name="ensurestreaming")
      @whitelisted_guilds(399500360877867018)
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
      async def on_member_update(self, before: discord.Member, after: discord.Member):
            audit_channel = audit_channels.get(str(after.guild.id), None)
            if audit_channel is None:
                  return
            audit_channel = after.guild.get_channel(audit_channel)
            
            e = discord.Embed(timestamp=get_local_time())
            e.set_footer(text=f"ID: {after.id}")

            if len(before.roles) != len(after.roles):
                  e.set_author(name=f"{after} updated.")
                  e.set_thumbnail(url=after.avatar_url)
                  if (len(before.roles) - len(after.roles)) == 1:
                        role = [role for role in before.roles if role not in after.roles]
                        e.add_field(name="Role Removed", value=role[0].mention)
                        e.colour = get_event_colour("role_removed")
                  elif (len(after.roles) - len(before.roles)) == 1:
                        role = [role for role in after.roles if role not in before.roles]
                        e.add_field(name="Role Added", value=role[0].mention)
                        e.colour = get_event_colour("role_added")

                  if audit_channel.permissions_for(after.guild.me).view_audit_log:
                        action = discord.AuditLogAction.member_role_update
                        perp, reason = "", ""
                        async for log in after.guild.audit_logs(limit=5, action=action):
                              if log.target.id == before.id:
                                    perp = log.user
                                    if log.reason:
                                          reason = log.reason
                                    break
                        if perp:
                              e.add_field(name="Updated by", value=perp.mention)
                        if reason:
                              e.add_field(name="Reason", value=reason)
                  await audit_channel.send(embed=e)
            
            if after.guild.id == 399500360877867018:
                  role = self.fuyu_roles["live"]
                  if any(a.type is discord.ActivityType.streaming for a in after.activities):
                        await after.add_roles(role)
                        # return
                  if not any(a.type is discord.ActivityType.streaming for a in after.activities):
                        await after.remove_roles(role)
                        # return

            if before.display_name != after.display_name:
                  e.set_author(name=f"{after} updated.")
                  if audit_channel.permissions_for(after.guild.me).view_audit_log:
                        action = discord.AuditLogAction.member_update
                        perp, reason = "", ""
                        async for log in after.guild.audit_logs(limit=5, action=action):
                              if log.target.id == before.id:
                                    perp = log.user
                                    if log.reason:
                                          reason = log.reason
                                    break

                  e.set_thumbnail(url=after.avatar_url)
                  e.add_field(name="Before Nickname", value=before.display_name)
                  e.add_field(name="After Nickname", value=after.display_name)
                  e.colour = get_event_colour("user_change")
                  if perp:
                        e.add_field(name="Updated by", value=perp.mention)
                  if reason:
                        e.add_field(name="Reason", value=reason)
                  await audit_channel.send(embed=e)

      @commands.Cog.listener()
      async def on_member_remove(self, member):
            audit_channel = audit_channels.get(str(member.guild.id), None)
            if audit_channel is None:
                  return
            audit_channel = member.guild.get_channel(audit_channel)
            e = discord.Embed(colour=get_event_colour("user_left"), description=f"**{member.mention} left the server.**", timestamp=get_local_time())
            e.set_author(name=str(member))
            e.set_thumbnail(url=member.avatar_url)
            e.set_footer(text=f"ID: {member.id}")
            await audit_channel.send(embed=e)
      
      @commands.Cog.listener()
      async def on_member_join(self, member):
            audit_channel = audit_channels.get(str(member.guild.id), None)
            if audit_channel is None:
                  return
            audit_channel = member.guild.get_channel(audit_channel)
            e = discord.Embed(colour=get_event_colour("user_join"), description=f"**{member.mention} joined the server.**", timestamp=get_local_time())
            e.set_author(name=str(member))
            e.set_thumbnail(url=member.avatar_url)
            e.add_field(name="Account Created", value=f"{humanize_timedelta(timedelta=get_local_time() - member.created_at)} ago.")
            inviter = await self.bot.invite_tracker.fetch_inviter(member)
            if inviter:
                  e.add_field(name="Invited by", value=str(inviter))
            e.set_footer(text=f"ID: {member.id}")
            await audit_channel.send(embed=e)

      @commands.Cog.listener()
      @commands.bot_has_permissions(manage_guild=True)
      async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
            guild_id = str(payload.guild_id)
            channel_id = str(payload.channel_id)
            message_id = str(payload.message_id)
            emoji = str(payload.emoji)
            guild_RRs = reactions.get(guild_id, None)
            if guild_RRs:
                  channel_RRs = guild_RRs.get(channel_id, None)
                  if channel_RRs:
                        message_RRS = channel_RRs.get(message_id, None)
                        if message_RRS:
                              role = message_RRS.get(emoji, None)
                              if role:
                                    role = payload.member.guild.get_role(role)
                                    await payload.member.add_roles(role)
                                    if guild_id == self.fuyu.id:
                                          await self.fuyu_channels["welcome"].send(f"Welcome {payload.member.mention}.", delete_after=5)
                              else:
                                    return
                        else:
                              return
                  else:
                        return
            else:
                  return


      @commands.command(name="unicode", hidden=True)
      async def _unicode(self, ctx, emoji):
            print(emoji)
            await ctx.send(emoji)


      @commands.command(name="insult")
      async def _insult(self, ctx, *whatever_args):
            await ctx.send("impatient fuck. wait.")

      @whitelisted_guilds(399500360877867018)
      @commands.is_owner() # TODO: make a mod_or_higher check and admin_or_higher check. also guild_owner check.
      @commands.command(name="hornyjail", aliases=['hjail', 'jail'], usage="[user(s)]", hidden=True)
      async def _timeout(self, ctx: commands.Context, *, users: Optional[str]):
            if not users:
                  await ctx.message.delete()
                  return
            
            users = await get_members(ctx, users.split(", "))

            not_in_vc = []
            timed_out = []
            alr_timed_out = []
            timeout = ctx.guild.get_channel(761826605370310717)

            for user in users:
                  if user.voice:
                        if user.voice.channel == timeout:
                              alr_timed_out.append(user.mention)
                        else:
                              await user.edit(voice_channel=timeout)
                              timed_out.append(user.mention)
                  else:
                        not_in_vc.append(user.mention)

            e = discord.Embed(title="Horny Jail", colour=discord.Colour.dark_teal(), timestamp=get_local_time())
            if len(timed_out) > 0:
                  e.add_field(name="Sent to horny jail", value=", ".join(timed_out))
            if len(alr_timed_out) > 0:
                  e.add_field(name="Already in horny jail", value=", ".join(alr_timed_out))
            if len(not_in_vc) > 0:
                  e.add_field(name="Not in a Voice Channel", value=", ".join(not_in_vc))
            if len(timed_out) == 0 and len(alr_timed_out) == 0 and len(not_in_vc) == 0:
                  e.description = "Nobody changed."
            
            await ctx.send(embed=e)


def setup(bot):
      bot.add_cog(Guild(bot))

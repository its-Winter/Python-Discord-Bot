import sys
import arrow
import time
import asyncio
import aiohttp
import discord
import contextlib
import platform
import logging
from discord import utils
from discord.ext import commands
from discord.ext.commands import errors, core
from cogs.utils import (
      botuptime,
      bold,
      box,
      bordered,
      inline,
      humanize_list
)

corelog = logging.getLogger('Core')
corelog.setLevel(logging.INFO)

class Core(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      @commands.command(name="welcome")
      @commands.guild_only()
      async def _welcome(self, ctx, *, users: discord.User = None):
            """A basic welcome command"""
            if not users:
                  await ctx.send(f"Welcome {ctx.author.mention} to {ctx.guild.name}!")
            else:
                  if len(users) > 1:
                        users = humanize_list(users)
                  else:
                        users = users[0].mention
                  await ctx.send(f"Welcome {users} to {ctx.guild.name}!")

      @commands.command(name="idavatar", aliases=["idav"])
      @commands.is_owner()
      async def _idavatar(self, ctx, userid: int = None):
            """Show any user id's avatar."""
            e = discord.Embed(color=discord.Color.blurple())
            if not userid:
                  user = ctx.author
            else:
                  try:
                        user = await ctx.bot.fetch_user(int(userid))
                        if user is None:
                              raise Exception("User is None.")
                  except Exception as e:
                        await ctx.send(f"Failed to catch user: {e}")
            e.set_image(url=user.avatar_url)
            e.set_author(name=f"{user.name}'s avatar", icon_url=user.avatar_url, url=user.avatar_url)
            e.set_footer(text=f"{ctx.author.name} wanted to see.", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="germ")
      @commands.guild_only()
      async def _germ(self, ctx):
            """it's a germ!"""
            germ = ctx.bot.get_user(216085324906889226)
            germstime = arrow.now("US/Pacific").strftime("%X")
            e = discord.Embed(title=germ.name, description=f"this is germ: {germ.mention}", color=discord.Color.gold())
            e.set_author(name=germ.name, icon_url=germ.avatar_url)
            e.set_footer(text=f"{ctx.author.name} has asked about Germ at {germstime} PST", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="uptime")
      async def _uptime(self, ctx):
            """Shows bot's uptime since last startup."""
            async with ctx.typing():
                  uptimestr = botuptime(ctx.bot)
                  e = discord.Embed(description=f"{ctx.bot.user.mention} has been online for ```{uptimestr}.```", color=discord.Color.green())
                  e.set_author(name="Uptime", icon_url=ctx.bot.user.avatar_url)
                  e.set_footer(text=f"summoned by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)

      @commands.command(name="nsfwcheck")
      @commands.guild_only()
      async def _checknsfw(self, ctx):
            """Check is a channel is set to NSFW."""
            if ctx.channel.nsfw:
                  await ctx.send("Channel is set to NSFW.")
            else:
                  await ctx.send("Channel is not set to NSFW.")

      @commands.command(name="ping")
      async def _ping(self, ctx):
            """Check bot's API latency and discord typing latency."""
            latency = self.bot.latency * 1000
            e = discord.Embed(title="Pong.", color=discord.Color.red())
            e.add_field(name="Discord API", value=f"```{str(round(latency))} ms```")
            e.add_field(name="Typing", value="```calculating ms```")

            before = time.monotonic()
            message = await ctx.send(embed=e)
            typlatency = (time.monotonic() - before) * 1000

            e = discord.Embed(title="Pong.", color=discord.Color.green())
            e.add_field(name="Discord API", value=f"```py\n{str(round(latency))} ms```")
            e.add_field(name="Typing", value=f"```py\n{str(round(typlatency))} ms```")

            await message.edit(embed=e)

      @commands.command(name="invites")
      @commands.guild_only()
      async def _invites(self, ctx):
            """Get stats on server invites."""
            waiting = await ctx.send("`Loading server invites...`")
            guild = ctx.guild
            guild_invites = await guild.invites()
            invitecodes = []
            uses = []
            channel = []
            inviter = []
            for invite in guild_invites:
                  invitecodes.append(invite.code)
                  uses.append(str(invite.uses))
                  channel.append(invite.channel.mention)
                  inviter.append(invite.inviter.mention)

            invitecodes = "\n".join(invitecodes)
            uses = "\n".join(uses)
            channel = "\n".join(channel)
            inviter = "\n".join(inviter)

            e = discord.Embed(color=ctx.guild.me.top_role.color)
            e.set_author(name=f"{guild.name}'s invites")
            e.set_thumbnail(url=guild.icon_url)
            e.add_field(name="Invites", value=invitecodes)
            e.add_field(name="Uses", value=uses)
            e.add_field(name="Channel", value=channel)
            e.add_field(name="Inviter", value=inviter)
            await waiting.edit(content=None, embed=e)

      @commands.command(name="dm")
      @commands.guild_only()
      async def _dm(self, ctx, user: str, *, message: str = None):
            """Direct message a user from the bot."""
            if user is None:
                  await ctx.send("Provided no user to search for.")
                  return
            else:
                  try:
                        user = ctx.guild.get_member_named(user)
                        if user is None:
                              user = ctx.guild.get_member(int(user))
                  except Exception as e:
                        await ctx.send(f"Failed to fetch user: {e}")
            
            if user is None:
                  await ctx.send(f"Failed to find that user: {user}")
                  return

            if user.bot is True:
                  await ctx.send("I cannot send messages to other bots pandejo.")
                  return

            if not user.dm_channel:
                  await user.create_dm()
            try:
                  e = discord.Embed(description=message, color=discord.Colour.blurple())
                  e.set_author(name=f"Message from {ctx.author}!", icon_url=ctx.author.avatar_url)
                  e.set_footer(text=f"Sent at {arrow.now(tz='US/Eastern').strftime('%X')} EST", icon_url=ctx.bot.user.avatar_url)
                  await user.send(embed=e)
                  await ctx.send(f"Sent your message to {user}.")
            except Exception as e:
                  await ctx.send(f"Failed to send message to {user}. {e}")


      @commands.command(name="guilds", aliases=["servers"])
      @commands.is_owner()
      async def _guilds(self, ctx):
            """List servers the bot is current a part of."""
            all_guilds = sorted(list(ctx.bot.guilds), key=lambda s: s.name.lower())
            msg = "Currently in these servers.\n"
            responses = []
            async with ctx.typing():
                  for i, guild in enumerate(all_guilds, 1):
                        msg += f"{i}: ``{guild.name}`` ({guild.id})\n"
                        responses.append(str(i))
                  query = await ctx.send("To leave a server, just type its number.")
                  await ctx.send(msg)

            def pred(m):
                  return True if m.author.id == ctx.message.author.id and m.content in responses else False

            try:
                  msg = await ctx.bot.wait_for("message", check=pred, timeout=15)
                  if guild.owner.id == ctx.bot.user.id:
                        return await ctx.send("I cannot leave a guild I am the owner of.")
            except asyncio.TimeoutError:
                  await query.delete()
                  return await ctx.send("message timed out.")

            guild_leave = await ctx.send(f"Are you sure you want me to leave {guild.name}? (yes/no)")
            def pred2(m):
                  return True if m.author == ctx.author and m.content == "yes" else False
            try:
                  pred = await self.bot.wait_for("message", check=pred2, timeout=15)
                  if pred.result is True:
                        await guild.leave()
                  if guild != ctx.guild:
                        await ctx.send("Done.")
                  else:
                        await ctx.send("Alright then.")
            except asyncio.TimeoutError:
                  await guild_leave.delete()
                  await query.delete()
                  await ctx.send("Response timed out.")

      @commands.command(name="dmid")
      @commands.is_owner()
      async def _dmid(self, ctx, id: int, *, message: str = None):
            """Direct message any user id with a message."""
            if not isinstance(id, str):
                  return await ctx.send("You have not entered a valid ID")

            if not message:
                  return await ctx.send("You must give a message to send.")

            try:
                  user = await ctx.bot.fetch_user(int(id))
            except Exception as e:
                  return await ctx.send(f"Error happened while trying to fetch user.\n{e}")

            if user.bot is True:
                  return await ctx.send("I cannot send messages to bots")

            if not user.dm_channel:
                  await user.create_dm()

            message = " ".join(message)
            e = discord.Embed(description=message, color=discord.Color.blurple())
            e.set_author(name=f"Message from {ctx.author}!", icon_url=ctx.author.avatar_url)
            e.set_footer(text=f"Sent at {arrow.now(tz='US/Eastern').strftime('%X')} EST", icon_url=ctx.bot.user.avatar_url)
            try:
                  await user.send(embed=e)
                  return await ctx.send(f"Message has been sent to `{user}`!")
            except discord.Forbidden:
                  return await ctx.send("Cannot send messages to this user")
            except discord.HTTPException:
                  return await ctx.send("Message failed.")
            except Exception as e:
                  await ctx.send(f"Error while sending embed. {e}")

      @commands.command(name="serverinfo", aliases=["guildinfo", "sinfo", "ginfo"])
      @commands.guild_only()
      async def _serverinfo(self, ctx, details: bool = True):
            """Get server information in a fancy embed."""
            # if not id:
            #       guild = ctx.guild
            # else:
            #       try:
            #             guild = ctx.bot.get_guild(int(id))
            #             if not guild:
            #                   guild = await ctx.bot.fetch_guild(int(id))
            #       except Exception as e:
            #             await ctx.send(f"Error: {e}")

            guild = ctx.guild
            online = len([m.status for m in guild.members if m.status != discord.Status.offline])
            if not details:
                  desc = "Created at {date}".format(date=guild.created_at.strftime("%d %b %Y %H:%M"))
                  data = discord.Embed(color=ctx.guild.me.top_role.color, description=desc)
                  data.set_author(name=guild.name)
                  data.set_thumbnail(url=guild.icon_url)
                  data.add_field(name="Region", value=bold(guild.region))
                  data.add_field(name="Users Online", value=bold(f"{online}/{guild.member_count}"))
                  data.add_field(name="Roles", value=bold(len(guild.roles)))
                  data.add_field(name="Owner", value=bold(str(guild.owner)))
                  data.set_footer(text=f"ID: {guild.id}")

            else:
                  passed = (ctx.message.created_at - guild.created_at).days
                  created_at = ("Created on {date}. That's **{num}** days ago!").format(
                        date=guild.created_at.strftime("%d %b %Y %H:%M"), num=passed,
                  )
                  total_users = guild.member_count
                  text_channels = len(guild.text_channels)
                  voice_channels = len(guild.voice_channels)

                  def _size(num: int):
                        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
                              if abs(num) < 1024.0:
                                    return "{0:.1f}{1}".format(num, unit)
                              num /= 1024.0
                        return "{0:.1f}{1}".format(num, "YB")

                  def _bitsize(num: int):
                        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
                              if abs(num) < 1000.0:
                                    return "{0:.1f}{1}".format(num, unit)
                              num /= 1000.0
                        return "{0:.1f}{1}".format(num, "YB")

                  shard_info = (
                        "\nShard ID: **{shard_id}/{shard_count}**".format(
                              shard_id=guild.shard_id + 1,
                              shard_count=ctx.bot.shard_count,
                        )
                        if ctx.bot.shard_count > 1
                        else ""
                  )
                  online_stats = {
                        "Humans: ": lambda x: not x.bot,
                        " • Bots: ": lambda x: x.bot,
                        "\N{LARGE GREEN CIRCLE}": lambda x: x.status is discord.Status.online,
                        "\N{LARGE ORANGE CIRCLE}": lambda x: x.status is discord.Status.idle,
                        "\N{LARGE RED CIRCLE}": lambda x: x.status is discord.Status.do_not_disturb,
                        "\N{MEDIUM WHITE CIRCLE}": lambda x: x.status is discord.Status.offline,
                        "\N{LARGE PURPLE CIRCLE}": lambda x: any(
                              a.type is discord.ActivityType.streaming for a in x.activities
                        ),
                        "\N{MOBILE PHONE}": lambda x: x.is_on_mobile(),
                  }
                  member_msg = ("Users online: **{onlineusr}/{total_users}**\n").format(
                        onlineusr=online, total_users=total_users
                  )
                  count = 1
                  for emoji, value in online_stats.items():
                        try:
                              num = len([m for m in guild.members if value(m)])
                        except Exception as error:
                              print(error)
                              continue
                        else:
                              member_msg += f"{emoji} {bold(num)} " + (
                                    "\n" if count % 2 == 0 else ""
                              )
                        count += 1

                  vc_regions = {
                        "vip-us-east": "__VIP__ US East " + "\U0001F1FA\U0001F1F8",
                        "vip-us-west": "__VIP__ US West " + "\U0001F1FA\U0001F1F8",
                        "vip-amsterdam": "__VIP__ Amsterdam " + "\U0001F1F3\U0001F1F1",
                        "eu-west": "EU West " + "\U0001F1EA\U0001F1FA",
                        "eu-central": "EU Central " + "\U0001F1EA\U0001F1FA",
                        "europe": "Europe " + "\U0001F1EA\U0001F1FA",
                        "london": "London " + "\U0001F1EC\U0001F1E7",
                        "frankfurt": "Frankfurt " + "\U0001F1E9\U0001F1EA",
                        "amsterdam": "Amsterdam " + "\U0001F1F3\U0001F1F1",
                        "us-west": "US West " + "\U0001F1FA\U0001F1F8",
                        "us-east": "US East " + "\U0001F1FA\U0001F1F8",
                        "us-south": "US South " + "\U0001F1FA\U0001F1F8",
                        "us-central": "US Central " + "\U0001F1FA\U0001F1F8",
                        "singapore": "Singapore " + "\U0001F1F8\U0001F1EC",
                        "sydney": "Sydney " + "\U0001F1E6\U0001F1FA",
                        "brazil": "Brazil " + "\U0001F1E7\U0001F1F7",
                        "hongkong": "Hong Kong " + "\U0001F1ED\U0001F1F0",
                        "russia": "Russia " + "\U0001F1F7\U0001F1FA",
                        "japan": "Japan " + "\U0001F1EF\U0001F1F5",
                        "southafrica": "South Africa " + "\U0001F1FF\U0001F1E6",
                        "india": "India " + "\U0001F1EE\U0001F1F3",
                        "dubai": "Dubai " + "\U0001F1E6\U0001F1EA",
                        "south-korea": "South Korea " + "\U0001f1f0\U0001f1f7",
                  }
                  verif = {
                        "none": "0 - None",
                        "low": "1 - Low",
                        "medium": "2 - Medium",
                        "high": "3 - High",
                        "extreme": "4 - Extreme",
                  }
                  features = {
                        "PARTNERED": "Partnered",
                        "VERIFIED": "Verified",
                        "DISCOVERABLE": "Server Discovery",
                        "FEATURABLE": "Featurable",
                        "PUBLIC": "Public",
                        "PUBLIC_DISABLED": "Public disabled",
                        "INVITE_SPLASH": "Splash Invite",
                        "VIP_REGIONS": "VIP Voice Servers",
                        "VANITY_URL": "Vanity URL",
                        "MORE_EMOJI": "More Emojis",
                        "COMMERCE": "Commerce",
                        "NEWS": "News Channels",
                        "ANIMATED_ICON": "Animated Icon",
                        "BANNER": "Banner Image",
                        "MEMBER_LIST_DISABLED": "Member list disabled",
                  }
                  guild_features_list = [
                        f"✅ {name}" for feature, name in features.items() if feature in guild.features
                  ]
                  joined_on = (
                        "{bot_name} joined this server on {bot_join}. That's {since_join} days ago!"
                  ).format(
                        bot_name=ctx.bot.user.name,
                        bot_join=guild.me.joined_at.strftime("%d %b %Y %H:%M:%S"),
                        since_join=(ctx.message.created_at - guild.me.joined_at).days,
                  )
                  data = discord.Embed(
                        description=(f"{guild.description}\n\n" if guild.description else "") + created_at,
                        colour=ctx.guild.me.top_role.color,
                  )
                  data.set_author(
                        name=guild.name,
                        icon_url="https://cdn.discordapp.com/emojis/457879292152381443.png"
                        if "VERIFIED" in guild.features
                        else "https://cdn.discordapp.com/emojis/508929941610430464.png"
                        if "PARTNERED" in guild.features
                        else discord.Embed.Empty,
                  )
                  if guild.icon_url:
                        data.set_thumbnail(url=guild.icon_url)
                  data.add_field(name="Members:", value=member_msg)
                  data.add_field(
                        name= "Channels:",
                        value= (
                              "\N{SPEECH BALLOON} Text: {text}\n"
                              "\N{SPEAKER WITH THREE SOUND WAVES} Voice: {voice}"
                        ).format(text=bold(text_channels), voice=bold(voice_channels)),
                  )
                  data.add_field(
                        name="Utility:",
                        value=(
                          "Owner: {owner}\nVoice region: {region}\nVerif. level: {verif}\nServer ID: {id}{shard_info}"
                        ).format(
                              owner=bold(str(guild.owner)),
                              region=bold(f"{vc_regions.get(str(guild.region)) or str(guild.region)}"),
                              verif=bold(verif[str(guild.verification_level)]),
                              id=bold(str(guild.id)),
                              shard_info=shard_info,
                        ),
                        inline=False,
                  )
                  data.add_field(
                        name="Misc:",
                        value=(
                              "AFK channel: {afk_chan}\nAFK timeout: {afk_timeout}\nCustom emojis: {emoji_count}\nRoles: {role_count}"
                        ).format(
                              afk_chan=bold(str(guild.afk_channel))
                              if guild.afk_channel
                              else bold("Not Set"),
                              afk_timeout=bold(guild.afk_timeout),
                              emoji_count=bold(len(guild.emojis)),
                              role_count=bold(len(guild.roles)),
                        ),
                        inline=False,
                  )
                  if guild_features_list:
                        data.add_field(name="Server features:", value="\n".join(guild_features_list))
                  if guild.premium_tier != 0:
                        nitro_boost = (
                              "Tier {boostlevel} with {nitroboosters} boosters\n"
                              "File size limit: {filelimit}\n"
                              "Emoji limit: {emojis_limit}\n"
                              "VCs max bitrate: {bitrate}"
                        ).format(
                              boostlevel=bold(str(guild.premium_tier)),
                              nitroboosters=bold(guild.premium_subscription_count),
                              filelimit=bold(_size(guild.filesize_limit)),
                              emojis_limit=bold(str(guild.emoji_limit)),
                              bitrate=bold(_bitsize(guild.bitrate_limit)),
                        )
                        data.add_field(name="Nitro Boost:", value=nitro_boost)
                  if guild.splash:
                        data.set_image(url=guild.splash_url_as(format="png"))
                        data.set_footer(text=joined_on)

            await ctx.send(embed=data)

def setup(bot):
      bot.add_cog(Core(bot))
from discord.ext import commands
import arrow

class utils(commands.Cog):
      def __init__(self, bot):
            self.bot = bot

      def botuptime(self) -> str:
            uptime = arrow.utcnow() - self.bot.start_time
            totalseconds = uptime.total_seconds()
            seconds = int(totalseconds)
            periods = [
                  ("year", "years", 60 * 60 * 24 * 365),
                  ("month", "months", 60 * 60 * 24 * 30),
                  ("day", "days", 60 * 60 * 24),
                  ("hour", "hours", 60 * 60),
                  ("minute", "minutes", 60),
                  ("second", "seconds", 1),
            ]
            strings = []
            for period_name, plural_period_name, period_seconds in periods:
                  if seconds >= period_seconds:
                        period_value, seconds = divmod(seconds, period_seconds)
                        if period_value == 0:
                              continue
                        unit = plural_period_name if period_value > 1 else period_name
                        strings.append(f"{period_value} {unit}")
            uptimestr = ", ".join(strings)
            return uptimestr

def setup(bot):
      bot.add_cog(utils(bot))
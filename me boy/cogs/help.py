from discord.ext import commands


class Help(commands.HelpCommand):
      def __init__(self, bot, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.bot = bot

from discord.ext import commands

class CommonCogMixin:
    """
    Provision methods common to most cogs
    """
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Print to the console when the cog is loaded.
        """
        name = self.__class__.__name__
        print(f"{name} cog ready as {self.bot.user}")
"""
Disboard decides how to rank servers based on how often users are entering the command /bump.
One of the reasons it does this is because after entering that command, it will spam the channel
with links to patreon, paypal, etc. We have confined the DISBOARD bot to the bot channel so that
this command can't be used elsewhere and we're deleting any messages that it posts and replacing
their confirmation of the bump with our own confirmation.

Keep in mind until we get some type of server identity, search tags, a good description, etc,
there isn't much value in bumping to be honest.

https://disboard.org/server/1248815078581735437
"""

import discord
from constants import channel_names
from discord.ext import commands
from mixins import CommonCogMixin

DISBOARD_BOT_ID = 302050872383242240


class Disboard(commands.Cog, CommonCogMixin):
    """
    Handle Disboard Bumping
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle_bump(self, message):
        """Handle /bump and disboard messages in the bot channel"""
        if message.channel.name != channel_names.bot_commands:
            return

        if message.content.strip().lower() == "/bump" and not message.author.bot:
            await message.channel.send(
                f"✅ Thanks {message.author.mention}! Please come back and bump again in **2 hours**."
            )

        if message.author.id == DISBOARD_BOT_ID:
            try:
                await message.delete()
            except discord.Forbidden:
                print("Missing permissions to delete Disboard messages.")


    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Fired when a message is created
        """
        await self.handle_bump(message)


async def setup(bot):
    await bot.add_cog(Disboard(bot))

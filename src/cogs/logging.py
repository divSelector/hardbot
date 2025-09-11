import discord
from discord.ext import commands
from types import SimpleNamespace
from constants import channel_names
from mixins import CommonCogMixin

colors = SimpleNamespace(
    new=discord.Color.blue(),
    edited=discord.Color.orange(),
    deleted=discord.Color.red()
)

class Logging(commands.Cog, CommonCogMixin):
    """
    Log created, edited, and deleted messages to specific log channel.
    """
    def __init__(self, bot):
        self.bot = bot

    # HELPER METHODS

    def create_base_embed(self, title: str, color: discord.Color, message: discord.Message):
        """
        All three logging functions use the same embed code with a different color and title, so we do
        most of the setup here.
        """
        embed = discord.Embed(
            title=title,
            description=f"[Jump to Message]({message.jump_url})" if hasattr(message, "jump_url") else None,
            color=color,
            timestamp=getattr(message, "created_at", discord.utils.utcnow())
        )

        embed.add_field(name="User ID", value=message.author.id, inline=False)
        embed.add_field(
            name="Username",
            value=f"{message.author} ({message.author.name}#{message.author.discriminator})",
            inline=False
        )
        embed.add_field(name="Nickname", value=message.author.display_name, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)

        return embed

    def add_attachments(self, embed, attachments):
        """
        Attachments are added to the embed when created or destroyed
        """
        if attachments:
            files_list = "\n".join([att.url for att in attachments])
            embed.add_field(name="Attachments", value=files_list, inline=False)
        return embed

    def get_log_channel(self, message: discord.Message):
        """
        If the message author is a bot the log channel will not be found.
        """
        return discord.utils.get(message.guild.text_channels, name=channel_names.admin_log)


    # LOGGING METHODS

    async def log_create(self, message):
        """
        Write a log when a message is created.
        """
        channel = self.get_log_channel(message)

        embed = self.create_base_embed("Message Created", colors.new, message)
        if message.content:
            embed.add_field(name="Content", value=message.content[:1024], inline=False)
        embed = self.add_attachments(embed, message.attachments)
        await channel.send(embed=embed)

    async def log_edit(self, before, after):
        """
        Write a log when a message is edited.
        """
        channel = self.get_log_channel(before)

        embed = self.create_base_embed("Message Edited", colors.edited, after)
        embed.add_field(name="Before", value=before.content[:1024] if before.content else "No content", inline=False)
        embed.add_field(name="After", value=after.content[:1024] if after.content else "No content", inline=False)
        await channel.send(embed=embed)

    async def log_delete(self, message):
        """
        Write a log when a message is deleted.
        """
        channel = self.get_log_channel(message)

        embed = self.create_base_embed("Message Deleted", colors.deleted, message)
        if message.content:
            embed.add_field(name="Content", value=message.content[:1024], inline=False)
        embed = self.add_attachments(embed, message.attachments)
        await channel.send(embed=embed)


    # EVENT LISTENERS

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Fired when a message is created
        """
        if message.author.bot:
            return
        await self.log_create(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Fired when a message is edited.
        If message before and after have the same content, it's probably an embed being added by Discord so skip logging it.
        """
        if before.content == after.content:
            return
        await self.log_edit(before, after)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Fired when a message is deleted
        """
        if message.author.bot:
            return
        await self.log_delete(message)


async def setup(bot):
    await bot.add_cog(Logging(bot))

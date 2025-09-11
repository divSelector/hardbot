import discord
from types import SimpleNamespace


from constants import channel_names

colors = SimpleNamespace(
    new=discord.Color.blue(),
    edited=discord.Color.orange(),
    deleted=discord.Color.red()
)

def create_base_embed(title: str, color: discord.Color, message: discord.Message):
    """Create a base embed with common fields from a message."""
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


def add_attachments(embed, attachments):
    """Add attachments field if there are any."""
    if attachments:
        files_list = "\n".join([att.url for att in attachments])
        embed.add_field(name="Attachments", value=files_list, inline=False)
    return embed


def get_log_channel(message: discord.Message):
    """Return the log channel if available, else None. Skip bots."""
    if message.author.bot:
        return None
    return discord.utils.get(message.guild.text_channels, name=channel_names.admin_log)


async def log_create(message):
    log_channel = get_log_channel(message)
    if not log_channel:
        return

    embed = create_base_embed("New Message Logged", colors.new, message)

    if message.content:
        embed.add_field(name="Content", value=message.content[:1024], inline=False)

    embed = add_attachments(embed, message.attachments)
    await log_channel.send(embed=embed)


async def log_edit(before, after):
    log_channel = get_log_channel(before)
    if not log_channel:
        return

    embed = create_base_embed("Message Edited", colors.edited, after)

    embed.add_field(name="Before", value=before.content[:1024] if before.content else "No content", inline=False)
    embed.add_field(name="After", value=after.content[:1024] if after.content else "No content", inline=False)

    await log_channel.send(embed=embed)


async def log_delete(message):
    log_channel = get_log_channel(message)
    if not log_channel:
        return

    embed = create_base_embed("Message Deleted", colors.deleted, message)

    if message.content:
        embed.add_field(name="Content", value=message.content[:1024], inline=False)

    embed = add_attachments(embed, message.attachments)
    await log_channel.send(embed=embed)
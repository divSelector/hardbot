import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

OWNER_ROLE_NAME = 'owner'
ADMIN_ROLE_NAME = 'admin'
LOG_CHANNEL_NAME = 'log'
BOT_CHANNEL_NAME = 'bot'

DISBOARD_BOT_ID = 302050872383242240  # Official Disboard bot ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def log_message(message):
    """Log all non-bot messages to #log"""
    if message.author.bot:
        return

    log_channel = discord.utils.get(message.guild.text_channels, name="log")
    if not log_channel:
        return

    embed = discord.Embed(
        title="Message Logged",
        description=f"[Jump to Message]({message.jump_url})",
        color=discord.Color.blue(),
        timestamp=message.created_at
    )

    embed.add_field(name="User ID", value=message.author.id, inline=False)
    embed.add_field(name="Username", value=f"{message.author} ({message.author.name}#{message.author.discriminator})", inline=False)
    embed.add_field(name="Nickname", value=message.author.display_name, inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=False)

    if message.content:
        embed.add_field(name="Content", value=message.content[:1024], inline=False)

    if message.attachments:
        files_list = "\n".join([att.url for att in message.attachments])
        embed.add_field(name="Attachments", value=files_list, inline=False)

    await log_channel.send(embed=embed)



async def handle_bump(message):
    """Handle /bump and disboard messages in the bot channel"""
    if message.channel.name != BOT_CHANNEL_NAME:
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
        except discord.HTTPException:
            pass


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await log_message(message)
    await handle_bump(message)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')


# DELETE
@bot.command(name='delete')
@commands.has_role(OWNER_ROLE_NAME)
async def delete_messages(ctx, number_of_messages: int):
    deleted = await ctx.channel.purge(limit=number_of_messages + 1)
    await ctx.send(f'Deleted {len(deleted)-1} messages', delete_after=5)

@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('You do not have the required role to use this command.', delete_after=5)


bot.run(DISCORD_BOT_TOKEN)

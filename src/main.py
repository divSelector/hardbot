import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
OWNER_ROLE_NAME = 'owner'
ADMIN_ROLE_NAME = 'admin'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')


# @bot.event
# async def on_message(message):
#     if message.channel.id == DISCORD_CHANNEL_ID and message.author != bot.user:
#         msg = "This server is locked up pretty tight. Just be patient and someone will let you into the main channel. " \
#               + "If you have any questions or concerns you can DM an admin -- Thanks for your interest in the site."
#         await message.channel.send(f'Hello! {msg}')
    
#     await bot.process_commands(message)


@bot.command(name='delete')
@commands.has_role(OWNER_ROLE_NAME)
async def delete_messages(ctx, number_of_messages: int):
    deleted = await ctx.channel.purge(limit=number_of_messages + 1)
    await ctx.send(f'Deleted {len(deleted)-1} messages', delete_after=5)


@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('You do not have the required role to use this command.', delete_after=5)



@bot.command(name='move')
@commands.has_role(ADMIN_ROLE_NAME)
async def move_messages(ctx, target_channel: discord.TextChannel, start_msg_id: int, end_msg_id: int):
    source_channel = ctx.channel

    try:
        start_msg = await source_channel.fetch_message(start_msg_id)
        end_msg = await source_channel.fetch_message(end_msg_id)
    except discord.NotFound:
        await ctx.send("One of the provided message IDs was not found.", delete_after=5)
        return

    # Ensure correct ordering
    if start_msg.created_at > end_msg.created_at:
        start_msg, end_msg = end_msg, start_msg

    # Fetch messages between start and end
    messages = []
    async for msg in source_channel.history(after=start_msg, before=end_msg, oldest_first=True):
        messages.append(msg)

    # Include the boundary messages
    messages.insert(0, start_msg)
    messages.append(end_msg)

    await ctx.send(f"Moving {len(messages)} messages to {target_channel.mention}...", delete_after=5)

    for msg in messages:
        content = f"**{msg.author.display_name}** ({msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}):\n{msg.content}"
        files = [await a.to_file() for a in msg.attachments]

        await target_channel.send(content, files=files)

    await ctx.send("Done!", delete_after=5)

bot.run(DISCORD_BOT_TOKEN)

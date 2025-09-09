import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
ADMIN_ROLE_NAME = 'owner'

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
@commands.has_role(ADMIN_ROLE_NAME)
async def delete_messages(ctx, number_of_messages: int):
    deleted = await ctx.channel.purge(limit=number_of_messages + 1)
    await ctx.send(f'Deleted {len(deleted)-1} messages', delete_after=5)


@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('You do not have the required role to use this command.', delete_after=5)

bot.run(DISCORD_BOT_TOKEN)

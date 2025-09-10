import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from log_channel import log_create, log_delete, log_edit
from disboard_bump import handle_bump

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

OWNER_ROLE_NAME = 'owner'
ADMIN_ROLE_NAME = 'admin'
MEMBER_ROLE_NAME = 'member'


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await log_create(message)
    await handle_bump(message)

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    await log_edit(before, after)


@bot.event
async def on_message_delete(message):
    await log_delete(message)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')



@bot.command(name='delete')
@commands.has_role(OWNER_ROLE_NAME)
async def delete_messages(ctx, number_of_messages: int):
    deleted = await ctx.channel.purge(limit=number_of_messages + 1)
    await ctx.send(f'Deleted {len(deleted)-1} messages', delete_after=5)

@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('You do not have the required role to use this command.', delete_after=5)



@bot.command(name="accept")
@commands.has_role(ADMIN_ROLE_NAME)
async def accept_member(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Usage: `!accept @User`")
        return

    role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE_NAME)
    if not role:
        await ctx.send(f"❌ '{MEMBER_ROLE_NAME}' role does not exist.")
        return

    if role in member.roles:
        await ctx.send(f"⚠️ {member.mention} already has the {MEMBER_ROLE_NAME} role.")
        return

    try:
        await member.add_roles(role, reason=f"Accepted by {ctx.author}")
        await ctx.send(f"✅ {member.mention} has been given the {MEMBER_ROLE_NAME} role.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to add this role.")

bot.run(DISCORD_BOT_TOKEN)

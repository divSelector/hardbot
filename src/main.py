import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from log_channel import log_create, log_delete, log_edit
from disboard_bump import handle_bump
from constants import role_names

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


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
@commands.has_role(role_names.owner)
async def delete_messages(ctx, number_of_messages: int):
    deleted = await ctx.channel.purge(limit=number_of_messages + 1)
    await ctx.send(f'Deleted {len(deleted)-1} messages', delete_after=5)

@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('You do not have the required role to use this command.', delete_after=5)



@bot.command(name="accept")
@commands.has_role(role_names.admin)
async def accept_member(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Usage: `!accept @User`")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_names.member)
    if not role:
        await ctx.send(f"❌ '{role_names.member}' role does not exist.")
        return

    if role in member.roles:
        await ctx.send(f"⚠️ {member.mention} already has the {role.name} role.")
        return

    try:
        await member.add_roles(role, reason=f"Accepted by {ctx.author}")
        await ctx.send(f"✅ {member.mention} has been given the {role.name} role.")
    except discord.Forbidden:
        await ctx.send("❌ No permission to add this role.")

bot.run(DISCORD_BOT_TOKEN)

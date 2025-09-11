import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot_extensions = [
    "cogs.logging",
    "cogs.administration",
    "cogs.disboard",
]

async def main():
    async with bot:
        for ext in bot_extensions:
            await bot.load_extension(ext)
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
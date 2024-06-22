import os
import discord
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.target_channel_id = DISCORD_CHANNEL_ID

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        msg = "This server is locked up pretty tight. Just be patient and someone will let you into the main channel. " \
             + "If you have any questions or concerns you can DM nobody_goeshard -- Thanks for your interest in the site."
        if message.channel.id == self.target_channel_id and message.author != self.user:
            await message.channel.send(f'Hello! {msg}')

client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
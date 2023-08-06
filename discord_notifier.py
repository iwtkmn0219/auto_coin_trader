import discord
import asyncio
from datetime import datetime, time

# discord bot token
DISCORD_TOKEN = (
    "MTEzNzU0MDI4OTg5NzE3NzEzOA.GffzZO.VTtO95OlDvAKLHlMedCXKvhsh9GNMGJMZ2Ju0g"
)
# discord channel id (일반)
CHANNEL_ID = 1137546202708185182

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)


async def send_message(msg: str):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(msg)
    else:
        print("Cannot found channel")

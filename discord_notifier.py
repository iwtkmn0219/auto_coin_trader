import discord
import asyncio
from datetime import datetime, time

# discord bot token
DISCORD_TOKEN = "MTEzNzU0MDI4OTg5NzE3NzEzOA.GffzZO.VTtO95OlDvAKLHlMedCXKvhsh9GNMGJMZ2Ju0g"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

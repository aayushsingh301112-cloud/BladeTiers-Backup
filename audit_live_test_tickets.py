import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv("/root/tierbot/.env")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.environ["GUILD_ID"])
CATEGORY_NAME = "Tier Test Tickets"

intents = discord.Intents.none()
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    try:
        guild = client.get_guild(GUILD_ID)

        if guild is None:
            print("ERROR: Bot could not find the configured server.")
            return

        print(f"Server: {guild.name}")
        print(f"Looking for category: {CATEGORY_NAME}")

        category = discord.utils.get(
            guild.categories, name=CATEGORY_NAME
        )

        if category is None:
            print("Category not found.")
            return

        tickets = [
            channel for channel in category.text_channels
            if "-test-" in channel.name.lower()
        ]

        if not tickets:
            print("No matching open test-ticket channels found.")
        else:
            print(f"Matching ticket channels: {len(tickets)}")
            for channel in tickets:
                print(f"- #{channel.name} | ID: {channel.id}")
                if channel.topic:
                    print(f"  Topic: {channel.topic}")

    finally:
        await client.close()

async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN missing from .env")
    await client.start(TOKEN)

asyncio.run(main())

import asyncio
import json
import os
from pathlib import Path

import discord
from dotenv import load_dotenv

ROOT = Path("/root/tierbot")
load_dotenv(ROOT / ".env")

print("========== QUEUES & CURRENT TESTING ==========")

queue_path = ROOT / "queue.json"
if not queue_path.exists():
    print("ERROR: queue.json not found")
else:
    data = json.loads(queue_path.read_text(encoding="utf-8"))

    def inspect(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current = f"{path}.{key}" if path else key
                low = key.lower()

                if "currently_testing" in low:
                    print(f"\nCURRENTLY TESTING — {current}")
                    print(json.dumps(value, ensure_ascii=False))

                elif "queue" in low or "waitlist" in low:
                    if isinstance(value, (list, dict)):
                        print(f"\nQUEUE/WAITLIST — {current}")
                        print(json.dumps(value, ensure_ascii=False))

                inspect(value, current)

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                inspect(value, f"{path}[{i}]")

    inspect(data)

print("\n========== LIVE DISCORD TEST TICKETS ==========")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.environ["GUILD_ID"])

intents = discord.Intents.none()
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    try:
        guild = client.get_guild(GUILD_ID)
        if guild is None:
            print("ERROR: Server not found in bot cache.")
            return

        print(f"Server: {guild.name}")
        category = discord.utils.get(
            guild.categories, name="Tier Test Tickets"
        )

        if category is None:
            print("Tier Test Tickets category not found.")
            return

        tickets = [
            ch for ch in category.text_channels
            if "-test-" in ch.name.lower()
        ]

        print(f"Matching open test-ticket channels: {len(tickets)}")
        for ch in tickets:
            print(f"- #{ch.name} | channel ID: {ch.id}")
            if ch.topic:
                print(f"  Topic: {ch.topic}")

    finally:
        await client.close()

async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN missing from .env")
    await client.start(TOKEN)

asyncio.run(main())

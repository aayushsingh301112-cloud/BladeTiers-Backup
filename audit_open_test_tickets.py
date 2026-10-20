import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv("/root/tierbot/.env")
GUILD_ID = int(os.environ["GUILD_ID"])
CATEGORY_NAME = "Tier Test Tickets"

class Audit(discord.Client):
    async def on_ready(self):
        try:
            guild = await self.fetch_guild(GUILD_ID)
            channels = await guild.fetch_channels()
            categories = [
                c for c in channels
                if isinstance(c, discord.CategoryChannel)
                and c.name == CATEGORY_NAME
            ]

            if not categories:
                print(f"Category not found: {CATEGORY_NAME}")
                return

            for category in categories:
                tickets = [
                    c for c in channels
                    if isinstance(c, discord.TextChannel)
                    and c.category_id == category.id
                    and "-test-" in c.name.lower()
                ]
                print(f"\nCategory: {category.name}")
                print(f"Open test-ticket channels found: {len(tickets)}")
                for c in tickets:
                    print(f"- #{c.name} | channel ID: {c.id}")
                    if c.topic:
                        print(f"  Topic: {c.topic}")
        except Exception as e:
            print(f"Ticket audit failed: {type(e).__name__}: {e}")
        finally:
            await self.close()

async def main():
    client = Audit(intents=discord.Intents(guilds=True))
    await client.start(os.environ["DISCORD_TOKEN"])

asyncio.run(main())

import asyncio
import os
import shutil
from pathlib import Path
from datetime import datetime

import discord
from dotenv import load_dotenv

load_dotenv("/root/tierbot/.env")

GUILD_ID = int(os.environ["GUILD_ID"])
TOKEN = os.environ["DISCORD_TOKEN"]
REG_FILE = Path("/root/tierbot/registrations.txt")

class MembershipCheck(discord.Client):
    async def on_ready(self):
        try:
            guild = await self.fetch_guild(GUILD_ID)
            current_ids = set()

            async for member in guild.fetch_members(limit=None):
                current_ids.add(member.id)

            lines = REG_FILE.read_text(encoding="utf-8").splitlines()
            kept = []
            removed = []
            malformed = []

            for line in lines:
                if not line.strip():
                    kept.append(line)
                    continue

                parts = line.strip().split("|")
                if len(parts) != 4 or not parts[0].isdigit():
                    malformed.append(line)
                    kept.append(line)
                    continue

                discord_id = int(parts[0])
                if discord_id in current_ids:
                    kept.append(line)
                else:
                    removed.append(line)

            print(f"Guild: {guild.name}")
            print(f"Current registrations: {len(lines)}")
            print(f"Live server members fetched: {len(current_ids)}")
            print(f"Registrations confirmed absent: {len(removed)}")
            print(f"Malformed records preserved: {len(malformed)}")

            if not removed:
                print("Nothing to remove.")
                await self.close()
                return

            print("\nAccounts marked for removal:")
            for line in removed:
                print(line)

            print("\\nDRY RUN ONLY — no registrations were changed.")
            print(f"Potential removals: {len(removed)}")
            print(f"Registrations that would remain: {len(kept)}")
        except Exception as e:
            print(f"Cleanup aborted; registrations were not intentionally changed: {type(e).__name__}: {e}")
        finally:
            await self.close()

intents = discord.Intents.default()
intents.members = True

async def main():
    client = MembershipCheck(intents=intents)
    await client.start(TOKEN)

asyncio.run(main())

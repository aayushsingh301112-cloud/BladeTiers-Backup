import asyncio
from collections import Counter
from pathlib import Path

import discord
from dotenv import load_dotenv
import os

load_dotenv("/root/tierbot/.env")

GUILD_ID = int(os.environ["GUILD_ID"])
REG_FILE = Path("/root/tierbot/registrations.txt")

registrations = {}
malformed = 0

for line in REG_FILE.read_text(encoding="utf-8").splitlines():
    parts = line.strip().split("|")
    if len(parts) != 4:
        if line.strip():
            malformed += 1
        continue

    discord_id, ign, region, account_type = parts
    try:
        uid = int(discord_id.strip())
    except ValueError:
        malformed += 1
        continue

    registrations[uid] = {
        "ign": ign.strip(),
        "region": region.strip(),
        "account_type": account_type.strip(),
    }

intents = discord.Intents.none()
intents.guilds = True
intents.members = True

class AuditClient(discord.Client):
    async def on_ready(self):
        try:
            guild = await self.fetch_guild(GUILD_ID)
            member_ids = set()

            async for member in guild.fetch_members(limit=None):
                member_ids.add(member.id)

            present = [
                (uid, info) for uid, info in registrations.items()
                if uid in member_ids
            ]
            left = [
                (uid, info) for uid, info in registrations.items()
                if uid not in member_ids
            ]

            print("\n========== BLADETIERS REGISTRATION AUDIT ==========")
            print(f"Guild: {guild.name}")
            print(f"Valid unique registrations: {len(registrations)}")
            print(f"Malformed lines skipped: {malformed}")
            print(f"Still in server: {len(present)}")
            print(f"Not found in server: {len(left)}")

            print("\n========== REGISTERED PLAYERS NOT FOUND ==========")
            if not left:
                print("None.")
            for uid, info in sorted(left, key=lambda x: x[1]["ign"].lower()):
                print(
                    f"IGN: {info['ign']} | Discord ID: {uid} | "
                    f"Region: {info['region']} | Account: {info['account_type']}"
                )

            print("\n========== REGISTERED PLAYERS STILL IN SERVER ==========")
            for uid, info in sorted(present, key=lambda x: x[1]["ign"].lower()):
                print(f"{info['ign']} | {uid}")

            print("\nAudit complete. No registration data was changed.")
        except discord.Forbidden:
            print(
                "AUDIT FAILED: Discord denied member-list access. "
                "Enable Server Members Intent for the bot in the Discord "
                "Developer Portal, then rerun this script."
            )
        except discord.HTTPException as e:
            print(f"AUDIT FAILED: Discord API error: {e}")
        finally:
            await self.close()

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("AUDIT FAILED: DISCORD_TOKEN is missing from .env")
        return

    client = AuditClient(intents=intents)
    try:
        await client.start(token)
    except discord.PrivilegedIntentsRequired:
        print(
            "AUDIT FAILED: Server Members Intent is not enabled in the "
            "Discord Developer Portal. Enable it and rerun."
        )
    except discord.LoginFailure:
        print("AUDIT FAILED: Discord rejected the bot login.")
    finally:
        if not client.is_closed():
            await client.close()

asyncio.run(main())

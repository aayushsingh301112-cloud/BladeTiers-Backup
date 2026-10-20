import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv("/root/tierbot/.env")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

HELPER_ROLE = "Discord Helper"
STAFF_ROLE = "Blade Staff Team"


class OneTimeRoleBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)

    async def on_ready(self):
        try:
            guild = self.get_guild(GUILD_ID)
            if guild is None:
                guild = await self.fetch_guild(GUILD_ID)

            helper = discord.utils.get(guild.roles, name=HELPER_ROLE)
            staff = discord.utils.get(guild.roles, name=STAFF_ROLE)

            if helper is None or staff is None:
                print("ERROR: Could not find both roles.")
                return

            print(f"Guild: {guild.name}")
            print(f"Finding members with {HELPER_ROLE}...")

            added = 0
            already_had = 0
            failed = 0

            async for member in guild.fetch_members(limit=None):
                if member.bot or helper not in member.roles:
                    continue

                if staff in member.roles:
                    already_had += 1
                    continue

                try:
                    await member.add_roles(
                        staff,
                        reason="One-time assignment to Blade Staff Team"
                    )
                    added += 1
                    print(f"Added role to {member} ({member.id})")
                    await asyncio.sleep(0.4)
                except discord.HTTPException as e:
                    failed += 1
                    print(f"FAILED: {member} ({member.id}): {e}")

            print("\n===== ONE-TIME ASSIGNMENT COMPLETE =====")
            print(f"Newly assigned: {added}")
            print(f"Already had role: {already_had}")
            print(f"Failed: {failed}")

        finally:
            await self.close()


async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN missing from /root/tierbot/.env")

    client = OneTimeRoleBot()
    await client.start(TOKEN)


asyncio.run(main())

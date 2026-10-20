import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv("/root/tierbot/.env")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.environ["GUILD_ID"])

GAMEMODES = [
    "Mace", "Sword", "Axe", "UHC", "SMP",
    "Nethop", "Pot", "Vanilla", "Spear", "Crystal"
]

async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing from .env")

    intents = discord.Intents.none()
    intents.guilds = True

    client = discord.Client(intents=intents)

    try:
        await client.login(TOKEN)
        guild = await client.fetch_guild(GUILD_ID)
        existing_roles = await guild.fetch_roles()
        existing_names = {role.name.casefold() for role in existing_roles}

        print(f"Server: {guild.name}")

        for gamemode in GAMEMODES:
            name = f"{gamemode} Tester"

            if name.casefold() in existing_names:
                print(f"SKIPPED — {name} already exists")
                continue

            try:
                await guild.create_role(
                    name=name,
                    reason="Create BladeTiers gamemode tester roles"
                )
                existing_names.add(name.casefold())
                print(f"CREATED — {name}")
            except discord.Forbidden:
                print(f"FAILED — {name}: missing Manage Roles permission")
                break

        print("Role creation finished.")
    finally:
        await client.close()

asyncio.run(main())

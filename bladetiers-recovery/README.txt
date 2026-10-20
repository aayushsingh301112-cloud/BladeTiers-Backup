BladeTiers recovery bundle

Saved bot.py is a recovered BladeTiers source snapshot from the user's Library.
player_api.py is a clean reconstruction matching the known BladeTiers API contract:
- GET /api/players
- GET /api/players?username=IGN
- GET /api/players/IGN
- GET /api/health

The API keeps the internal tier keys such as nethop unchanged.
No Discord token or secret is included.

IMPORTANT: restore your real tiers.json, registrations.txt, skins/, results/, and .env backups if you have them.
Do not invent or reuse an old exposed Discord token; create a new token if the old one may have been exposed.

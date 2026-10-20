import json
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = Path("/root/tierbot")
TIERS = BASE / "tiers.json"
REGS = BASE / "registrations.txt"
SKIN_WEBSITE = BASE / "skin_website"


def load_tiers():
    try:
        with open(TIERS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_players():
    players = []

    if not REGS.exists():
        return players

    with open(REGS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) < 4:
                continue

            discord_id, username, region, account_type = parts[:4]

            player = {
                "discord_id": discord_id,
                "name": username,
                "region": region,
                "account_type": account_type
            }

            # Website-rendered model
            model_file = SKIN_WEBSITE / f"{username.strip()}model.png"
            if model_file.exists():
                player["skin"] = f"/skin_website/{model_file.name}"
            else:
                player["skin"] = None

            players.append(player)

    return players


@app.get("/api/players")
def get_players():
    tiers = load_tiers()
    players = load_players()

    for player in players:
        name = player["name"].strip()

        tier_key = next(
            (k for k in tiers if k.strip().lower() == name.lower()),
            None
        )

        player["tiers"] = tiers.get(tier_key, {}) if tier_key else {}

    return jsonify(players)


@app.get("/skin_website/<path:filename>")
def skin_website(filename):
    return send_from_directory(SKIN_WEBSITE, filename)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

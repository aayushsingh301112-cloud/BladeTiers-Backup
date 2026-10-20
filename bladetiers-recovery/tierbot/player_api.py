import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

BASE_DIR = Path(os.getenv("TIERBOT_DIR", "/root/tierbot"))
REGISTRATIONS_FILE = BASE_DIR / "registrations.txt"
TIERS_FILE = BASE_DIR / "tiers.json"

app = Flask(__name__)
CORS(app)


def clean_username(username: str) -> str:
    username = str(username).strip()
    return "".join(c for c in username if c.isalnum() or c in ("_", "-"))


def load_registrations():
    registrations = {}
    if not REGISTRATIONS_FILE.exists():
        return registrations

    try:
        with REGISTRATIONS_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\r\n").split("|")
                if len(parts) >= 4:
                    discord_id, username, region, account_type = parts[:4]
                elif len(parts) >= 3:
                    discord_id, username, region = parts[:3]
                    account_type = "cracked"
                else:
                    continue

                registrations[str(discord_id)] = {
                    "discord_id": str(discord_id),
                    "name": username,
                    "region": region,
                    "account_type": account_type,
                }
    except OSError:
        return {}

    return registrations


def load_tiers():
    if not TIERS_FILE.exists():
        return {}
    try:
        with TIERS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def tiers_for(username, tier_data):
    target = str(username).strip().casefold()
    merged = {}
    for key, value in tier_data.items():
        if str(key).strip().casefold() == target and isinstance(value, dict):
            for mode, tier in value.items():
                merged[str(mode).strip().lower()] = str(tier).upper()
    return merged


def build_players():
    registrations = load_registrations()
    tier_data = load_tiers()
    players = []

    for registration in registrations.values():
        username = registration["name"]
        players.append({
            "discord_id": registration["discord_id"],
            "name": username,
            "region": registration["region"],
            "account_type": registration["account_type"],
            "tiers": tiers_for(username, tier_data),
        })

    return players


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/players")
def players():
    data = build_players()
    username = request.args.get("username", "").strip()

    if username:
        target = username.casefold()
        data = [p for p in data if p["name"].casefold() == target]

    return jsonify(data)


@app.get("/api/players/<path:username>")
def player(username):
    target = username.strip().casefold()
    for item in build_players():
        if item["name"].casefold() == target:
            return jsonify(item)
    return jsonify({"error": "Player not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

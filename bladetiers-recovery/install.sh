#!/usr/bin/env bash
set -e

mkdir -p /root/tierbot/skins /root/tierbot/results
cp tierbot/* /root/tierbot/ 2>/dev/null || true
cd /root/tierbot

python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created /root/tierbot/.env — PUT YOUR NEW TOKEN + GUILD_ID THERE."
fi

echo "Files installed. Test syntax with: venv/bin/python -m py_compile bot.py player_api.py"
echo "Run bot: venv/bin/python bot.py"
echo "Run API: venv/bin/python player_api.py"

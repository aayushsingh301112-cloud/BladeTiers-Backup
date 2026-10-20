from pathlib import Path
import subprocess
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SCRIPT = "/root/tierbot/daily_tempskin.py"
PYTHON = "/root/tierbot/venv/bin/python"
IST = ZoneInfo("Asia/Kolkata")

while True:
    now = datetime.now(IST)
    target = now.replace(hour=23, minute=0, second=0, microsecond=0)

    if now >= target:
        target += timedelta(days=1)

    sleep_seconds = (target - now).total_seconds()

    print(
        f"[daily_tempskin] Next run: "
        f"{target.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        flush=True
    )

    time.sleep(sleep_seconds)

    try:
        subprocess.run(
            [PYTHON, SCRIPT],
            check=False
        )
    except Exception as e:
        print(f"[daily_tempskin] Error: {e}", flush=True)

    time.sleep(2)

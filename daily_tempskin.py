from pathlib import Path
import time
import shutil
import datetime

BASE = Path("/root/tierbot")
REG = BASE / "registrations.txt"
SKINS = BASE / "skin_website"
TEMP = SKINS / "tempskin.png"
LOG = BASE / "daily_tempskin.log"

def log(msg):
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    if not REG.exists():
        log("❌ registrations.txt not found.")
        return

    if not TEMP.exists():
        log("❌ skin_website/tempskin.png not found.")
        return

    SKINS.mkdir(exist_ok=True)
    count = 0

    for line in REG.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split("|")

        if len(parts) < 4:
            continue

        user_id, username, region, account_type = parts[:4]

        if account_type.strip().lower() != "cracked":
            continue

        username = username.strip()

        if not username:
            continue

        model_path = SKINS / f"{username}model.png"

        if model_path.exists():
            continue

        try:
            shutil.copy2(TEMP, model_path)
            count += 1
            log(f"✅ {username} → {model_path.name}")
            time.sleep(5)
        except Exception as e:
            log(f"❌ Failed for {username}: {e}")

    log(f"✅ Finished. Assigned tempskin to {count} cracked players.")

if __name__ == "__main__":
    main()

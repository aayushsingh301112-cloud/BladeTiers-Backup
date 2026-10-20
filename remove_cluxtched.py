import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path("/root/tierbot")
IGN = "Cluxtched"
DISCORD_ID = "1535018806706044948"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TARGETS = [
    ROOT / "registrations.txt",
    ROOT / "queue.json",
    ROOT / "tiers.json",
    ROOT / "tester_stats.json",
]

def is_target_name(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    return (
        value.casefold() == IGN.casefold()
        or value.casefold() == f"EU | {IGN}".casefold()
    )

def clean_json(obj, path="$"):
    removed = []
    if isinstance(obj, dict):
        # Remove a stats/queue record belonging to this IGN.
        if any(
            key.lower() in ("username", "ign", "player", "minecraft_username")
            and is_target_name(value)
            for key, value in obj.items()
        ):
            return None, [path]

        result = {}
        for key, value in obj.items():
            if isinstance(key, str) and key.casefold() == IGN.casefold():
                removed.append(f"{path}.{key}")
                continue
            new_value, hits = clean_json(value, f"{path}.{key}")
            removed.extend(hits)
            result[key] = new_value
        return result, removed

    if isinstance(obj, list):
        result = []
        for i, value in enumerate(obj):
            if is_target_name(value):
                removed.append(f"{path}[{i}]")
                continue
            new_value, hits = clean_json(value, f"{path}[{i}]")
            removed.extend(hits)
            if new_value is not None:
                result.append(new_value)
        return result, removed

    return obj, removed

def atomic_write(path, content):
    fd, temp_name = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)

# Validate all files before changing anything.
for path in TARGETS:
    if not path.is_file():
        raise SystemExit(f"STOP: Required file missing: {path}")
for path in TARGETS[1:]:
    json.loads(path.read_text(encoding="utf-8"))

# Back up live files.
for path in TARGETS:
    backup = path.with_name(f"{path.name}.BACKUP_REMOVE_CLUXTCHED_{STAMP}")
    shutil.copy2(path, backup)
    print(f"Backup: {backup}")

# Remove exact registration by IGN or matching Discord ID.
reg_path = TARGETS[0]
lines = reg_path.read_text(encoding="utf-8").splitlines(keepends=True)
kept = []
removed_reg = []
for line in lines:
    fields = line.rstrip("\r\n").split("|")
    if len(fields) >= 2 and (
        fields[0].strip() == DISCORD_ID
        or fields[1].strip().casefold() == IGN.casefold()
    ):
        removed_reg.append(line.rstrip())
    else:
        kept.append(line)

if removed_reg:
    atomic_write(reg_path, "".join(kept))
print(f"Registration records removed: {len(removed_reg)}")
for line in removed_reg:
    print(f"  {line}")

# Remove exact IGN-related records from live JSON data.
for path in TARGETS[1:]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cleaned, locations = clean_json(data)
    if locations:
        atomic_write(
            path,
            json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n"
        )
    print(f"{path.name}: {len(locations)} matching record(s) removed")
    for location in locations:
        print(f"  {location}")

# Verify live files no longer contain the exact IGN.
print("\n===== VERIFICATION =====")
for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    remaining = [
        line for line in text.splitlines()
        if IGN.casefold() in line.casefold()
        or DISCORD_ID in line
    ]
    print(f"{path.name}: {'STILL HAS MATCHES' if remaining else 'clean'}")
    for line in remaining[:10]:
        print(f"  {line.strip()}")

print("\nCleanup finished. Historical backups were not changed.")

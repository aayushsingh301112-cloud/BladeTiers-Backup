import os
import shutil
from pathlib import Path
from datetime import datetime

REG = Path("/root/tierbot/registrations.txt")

REMOVE_IDS = {
    "1408448251476316210", "1456889139885510871",
    "1391369438103863357", "1394948604329988136",
    "1139484902077775903", "983689685505282090",
    "1506203957650001920", "1507703003140849765",
    "1464150638022627421", "1404387345481994321",
    "1013097288891121724", "1541399790229790743",
    "1415000341832929350", "1371862889178337362",
    "1482669604684697620", "1401231998160212058",
    "1489976054306177115", "1555239699629744232",
    "1526821992827846728", "1546144395663908980",
    "1455978991457406988", "1489510066850893865",
    "1292446173067481140", "1449665911886712973",
    "1005880916708696176", "1372941127560335360",
    "1227311753755492412", "1468181586372464714",
    "1514867326405836826", "1218481943885385778",
    "1332637626288705621", "1495188887084208168",
    "1542055213781876757", "1055506880987926529",
    "1435023376765812836",
}

lines = REG.read_text(encoding="utf-8").splitlines()
counts = {uid: 0 for uid in REMOVE_IDS}
parsed = []

for line in lines:
    parts = line.strip().split("|")
    if len(parts) != 4 or not parts[0].isdigit():
        raise SystemExit("ABORTED: malformed registration found; file unchanged.")
    counts[parts[0]] = counts.get(parts[0], 0) + 1
    parsed.append((line, parts[0]))

missing = [uid for uid in REMOVE_IDS if counts[uid] == 0]
duplicates = [uid for uid in REMOVE_IDS if counts[uid] != 1]

if missing or duplicates:
    print("ABORTED: expected every target ID exactly once.")
    print("Missing IDs:", missing)
    print("IDs not occurring exactly once:", duplicates)
    raise SystemExit(1)

kept = [line for line, uid in parsed if uid not in REMOVE_IDS]
removed = [line for line, uid in parsed if uid in REMOVE_IDS]

if len(removed) != 35 or len(kept) != len(lines) - 35:
    raise SystemExit("ABORTED: count verification failed; file unchanged.")

backup = REG.with_name(
    f"registrations.txt.BACKUP_BEFORE_FINAL_REMOVE_{datetime.now():%Y%m%d_%H%M%S}"
)
shutil.copy2(REG, backup)

temp = REG.with_name("registrations.txt.cleanup.tmp")
try:
    temp.write_text("".join(line + "\n" for line in kept), encoding="utf-8")
    if len(temp.read_text(encoding="utf-8").splitlines()) != len(kept):
        raise RuntimeError("Temporary file count verification failed.")
    os.replace(temp, REG)
except Exception:
    temp.unlink(missing_ok=True)
    raise

print(f"Removed registrations: {len(removed)}")
for line in removed:
    print("REMOVED:", line)
print(f"Remaining registrations: {len(kept)}")
print(f"Backup saved: {backup}")

from pathlib import Path
from datetime import datetime
import shutil
import sys

p = Path("/root/tierbot/bot.py")
source = p.read_text(encoding="utf-8")

# Refuse to patch if the expected code layout has changed.
checks = {
    "imports": "import asyncio\n",
    "base directory": 'BASE_DIR = Path("/root/tierbot")',
    "tester result function": "def record_tester_result(tester_id, tester_username, gamemode=None):",
    "hourly task": "@tasks.loop(hours=1)\nasync def hourly_tier_role_sync():",
    "startup hook": "async def on_ready():",
    "blackout command": "@app_commands.choices(mode=[",
}
for label, needle in checks.items():
    if source.count(needle) != 1:
        print(f"STOP: expected exactly one {label} marker; found {source.count(needle)}.")
        sys.exit(1)

if "MONTHLY LEADERBOARD SYSTEM" in source:
    print("STOP: monthly leaderboard code already appears to exist. No changes made.")
    sys.exit(1)

backup = p.with_name(
    "bot.py.bak_before_monthly_leaderboard_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
shutil.copy2(p, backup)

# 1. Add timezone support.
source = source.replace(
    "import asyncio\n",
    "import asyncio\nfrom datetime import datetime\nfrom zoneinfo import ZoneInfo\n",
    1,
)

# 2. Add the independent monthly data system before lifetime tracking.
monthly_code = r'''
# ============================================================
# MONTHLY LEADERBOARD SYSTEM
# ============================================================
MONTHLY_CONFIG_FILE = BASE_DIR / "monthly_leaderboard_config.json"
MONTHLY_TIMEZONE = ZoneInfo("Asia/Kolkata")


def monthly_now():
    return datetime.now(MONTHLY_TIMEZONE)


def monthly_file_for(moment=None):
    moment = moment or monthly_now()
    month_name = moment.strftime("%B").lower()
    return BASE_DIR / f"testing_data_{month_name}_{moment.year}.json"


def load_monthly_config():
    try:
        data = json.loads(MONTHLY_CONFIG_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"enabled": False}
    except (OSError, ValueError):
        return {"enabled": False}


def atomic_json_write(path, data):
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temp_path.replace(path)


def ensure_monthly_file(moment=None):
    moment = moment or monthly_now()
    path = monthly_file_for(moment)

    # Never overwrite an existing month/archive.
    if not path.exists():
        atomic_json_write(path, {
            "month": moment.strftime("%Y-%m"),
            "timezone": "Asia/Kolkata",
            "testers": {},
            "events": [],
        })

    return path


def record_monthly_tester_result(tester_id, tester_username, gamemode=None):
    """Record one successfully posted test without changing lifetime stats."""
    try:
        if not load_monthly_config().get("enabled", False):
            return

        now = monthly_now()
        path = ensure_monthly_file(now)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"Monthly leaderboard: could not read {path.name}: {exc}")
            return

        if not isinstance(data, dict):
            print(f"Monthly leaderboard: invalid structure in {path.name}; skipped.")
            return

        testers = data.setdefault("testers", {})
        tester_id = str(tester_id)
        username = str(tester_username)
        mode = str(gamemode).lower() if gamemode else "unknown"

        entry = testers.setdefault(tester_id, {
            "username": username,
            "tests": 0,
            "gamemodes": {},
        })
        entry["username"] = username
        entry["tests"] = int(entry.get("tests", 0)) + 1

        gamemodes = entry.setdefault("gamemodes", {})
        gamemodes[mode] = int(gamemodes.get(mode, 0)) + 1

        data.setdefault("events", []).append({
            "timestamp": now.isoformat(),
            "tester_id": tester_id,
            "username": username,
            "gamemode": mode,
        })

        atomic_json_write(path, data)
        print(
            f"Monthly leaderboard: {username} recorded "
            f"test #{entry['tests']} in {data.get('month', now.strftime('%Y-%m'))}."
        )

    except Exception as exc:
        # A monthly-stat failure must not interrupt the tier-result workflow.
        print(f"Monthly leaderboard recording failed safely: {exc}")


@tasks.loop(hours=1)
async def monthly_leaderboard_month_check():
    """Ensure the current calendar month's file exists; preserve all archives."""
    try:
        if load_monthly_config().get("enabled", False):
            path = ensure_monthly_file()
            print(f"Monthly leaderboard month check: {path.name}")
    except Exception as exc:
        print(f"Monthly leaderboard month check failed safely: {exc}")


@monthly_leaderboard_month_check.before_loop
async def before_monthly_leaderboard_month_check():
    await bot.wait_until_ready()


monthlyleaderboard_group = app_commands.Group(
    name="monthlyleaderboard",
    description="Manage the monthly tester leaderboard.",
)


@monthlyleaderboard_group.command(
    name="enable",
    description="Enable persistent monthly tester tracking.",
)
async def monthlyleaderboard_enable(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Only server administrators can enable the monthly leaderboard.",
            ephemeral=True,
        )
        return

    config = load_monthly_config()
    if config.get("enabled", False):
        current_file = ensure_monthly_file()
        await interaction.response.send_message(
            f"Monthly leaderboard is already enabled. Current file: `{current_file.name}`.",
            ephemeral=True,
        )
        return

    now = monthly_now()
    config = {
        "enabled": True,
        "enabled_at": now.isoformat(),
        "timezone": "Asia/Kolkata",
    }

    try:
        atomic_json_write(MONTHLY_CONFIG_FILE, config)
        current_file = ensure_monthly_file(now)
    except Exception as exc:
        await interaction.response.send_message(
            f"Could not enable monthly tracking: {exc}",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"✅ Monthly tester tracking is now enabled.\n"
        f"Current archive: `{current_file.name}`\n"
        "Only successfully posted test results from now onward are counted. "
        "Lifetime statistics and older monthly archives are kept separately.",
        ephemeral=True,
    )


bot.tree.add_command(
    monthlyleaderboard_group,
    guild=discord.Object(id=int(GUILD_ID)),
)


'''

source = source.replace(
    "def record_tester_result(tester_id, tester_username, gamemode=None):",
    monthly_code + "def record_tester_result(tester_id, tester_username, gamemode=None):",
    1,
)

# 3. Record monthly stats only after lifetime stats were saved successfully.
needle = '''        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(
'''
replacement = '''        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Separate monthly tracking; lifetime totals above remain unchanged.
        record_monthly_tester_result(
            tester_id,
            tester_username,
            gamemode,
        )

        print(
'''
if source.count(needle) != 1:
    print("STOP: couldn't uniquely locate the lifetime-stats save point.")
    shutil.copy2(backup, p)
    sys.exit(1)
source = source.replace(needle, replacement, 1)

# 4. Start the month checker alongside the existing hourly task.
needle = '''async def on_ready():
    if not hourly_tier_role_sync.is_running():
'''
replacement = '''async def on_ready():
    if not monthly_leaderboard_month_check.is_running():
        monthly_leaderboard_month_check.start()
        print("📅 Monthly leaderboard month checker started.")

    if not hourly_tier_role_sync.is_running():
'''
if source.count(needle) != 1:
    print("STOP: couldn't uniquely locate the on_ready task startup.")
    shutil.copy2(backup, p)
    sys.exit(1)
source = source.replace(needle, replacement, 1)

# Write only after all expected patch points have been verified.
p.write_text(source, encoding="utf-8")
print(f"Patch applied. Backup: {backup}")

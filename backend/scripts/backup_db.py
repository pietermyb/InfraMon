"""Database backup and restore utilities."""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite


DATABASE_PATH = Path("./inframon.db")
BACKUP_DIR = Path("./backups")


async def backup_database() -> Path:
    """Create a timestamped backup of the database."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"inframon_{timestamp}.db"

    async with aiosqlite.connect(str(DATABASE_PATH)) as source:
        async with aiosqlite.connect(str(backup_path)) as target:
            await target.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            await source.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            await source.backup(target)

    print(f"Backup created: {backup_path}")
    return backup_path


async def list_backups() -> list[Path]:
    """List all available backups."""
    if not BACKUP_DIR.exists():
        return []

    return sorted(BACKUP_DIR.glob("inframon_*.db"), reverse=True)


async def restore_database(backup_path: Path) -> bool:
    """Restore database from a backup file."""
    if not backup_path.exists():
        print(f"Backup not found: {backup_path}")
        return False

    backup = DATABASE_PATH.with_suffix(".bak")
    if DATABASE_PATH.exists():
        shutil.move(str(DATABASE_PATH), str(backup))

    shutil.copy(str(backup_path), str(DATABASE_PATH))
    print(f"Database restored from: {backup_path}")

    if backup.exists():
        backup.unlink()

    return True


async def get_backup_info(backup_path: Path) -> dict:
    """Get information about a backup file."""
    async with aiosqlite.connect(str(backup_path)) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM users")
        user_count = await cursor.fetchone()

        cursor = await conn.execute("SELECT COUNT(*) FROM containers")
        container_count = await cursor.fetchone()

        cursor = await conn.execute("SELECT COUNT(*) FROM container_groups")
        group_count = await cursor.fetchone()

    return {
        "path": backup_path,
        "size_bytes": backup_path.stat().st_size,
        "users": user_count,
        "containers": container_count,
        "groups": group_count,
        "created": datetime.fromtimestamp(backup_path.stat().st_mtime),
    }


async def cleanup_old_backups(keep_count: int = 5) -> int:
    """Remove old backups, keeping the most recent ones."""
    backups = await list_backups()

    if len(backups) <= keep_count:
        return 0

    removed = 0
    for backup in backups[:-keep_count]:
        backup.unlink()
        removed += 1

    print(f"Removed {removed} old backups")
    return removed


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python backup_db.py [backup|restore|list|cleanup]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "backup":
        asyncio.run(backup_database())
    elif command == "list":
        backups = asyncio.run(list_backups())
        for backup in backups:
            info = asyncio.run(get_backup_info(backup))
            print(f"{info['path']}: {info['size_bytes']} bytes - {info['created']}")
    elif command == "cleanup":
        asyncio.run(cleanup_old_backups())
    elif command == "restore" and len(sys.argv) > 2:
        asyncio.run(restore_database(Path(sys.argv[2])))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

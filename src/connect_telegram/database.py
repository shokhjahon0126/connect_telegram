"""Asynchronous SQLite database operations for connect_telegram using aiosqlite."""

import logging
from datetime import datetime
from typing import Any, Optional
import aiosqlite

logger = logging.getLogger("connect_telegram.database")


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self) -> None:
        """Initialize database tables and default settings."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode = WAL;")
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reply_type TEXT NOT NULL DEFAULT 'busy',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_msg_logs_user_time 
                ON message_logs(user_id, created_at);

                CREATE TABLE IF NOT EXISTS call_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    call_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_call_logs_user_time 
                ON call_logs(user_id, created_at);

                CREATE TABLE IF NOT EXISTS birthday_history (
                    user_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(user_id, year)
                );

                CREATE TABLE IF NOT EXISTS vip_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT DEFAULT '',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Default initial settings
            await db.execute("""
                INSERT OR IGNORE INTO settings (key, value)
                VALUES ('is_busy', '1'), ('auto_reply_active', '1');
            """)
            await db.commit()
            logger.info("Database initialized successfully at %s", self.db_path)

    # -------------------------------------------------------------
    # Settings Management
    # -------------------------------------------------------------
    async def get_setting(self, key: str, default: str = "") -> str:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            await db.commit()

    async def is_busy(self) -> bool:
        val = await self.get_setting("is_busy", "1")
        return val == "1"

    async def set_busy(self, busy: bool) -> None:
        await self.set_setting("is_busy", "1" if busy else "0")

    # -------------------------------------------------------------
    # Auto-Reply Cooldown
    # -------------------------------------------------------------
    async def can_send_auto_reply(self, user_id: int, cooldown_minutes: int) -> bool:
        """Check if enough time has passed since the last auto-reply for this user."""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT strftime('%s', 'now') - strftime('%s', created_at)
                FROM message_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """
            async with db.execute(query, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] is None:
                    return True
                seconds_elapsed = row[0]
                return seconds_elapsed >= (cooldown_minutes * 60)

    async def record_auto_reply(self, user_id: int, reply_type: str = "busy") -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO message_logs (user_id, reply_type) VALUES (?, ?)",
                (user_id, reply_type),
            )
            await db.commit()

    # -------------------------------------------------------------
    # Call Cooldown
    # -------------------------------------------------------------
    async def can_send_call_reply(self, user_id: int, cooldown_minutes: int) -> bool:
        """Check if enough time has passed since the last call-related response."""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT strftime('%s', 'now') - strftime('%s', created_at)
                FROM call_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """
            async with db.execute(query, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] is None:
                    return True
                seconds_elapsed = row[0]
                return seconds_elapsed >= (cooldown_minutes * 60)

    async def record_call_reply(self, user_id: int, call_type: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO call_logs (user_id, call_type) VALUES (?, ?)",
                (user_id, call_type),
            )
            await db.commit()

    # -------------------------------------------------------------
    # Birthday Greetings History
    # -------------------------------------------------------------
    async def is_birthday_already_sent(self, user_id: int, year: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM birthday_history WHERE user_id = ? AND year = ?",
                (user_id, year),
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def record_birthday_sent(self, user_id: int, year: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO birthday_history (user_id, year) VALUES (?, ?)",
                (user_id, year),
            )
            await db.commit()

    # -------------------------------------------------------------
    # VIP Management
    # -------------------------------------------------------------
    async def is_vip(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM vip_users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def add_vip(self, user_id: int, username: str = "") -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO vip_users (user_id, username) VALUES (?, ?)",
                (user_id, username),
            )
            await db.commit()
            return True

    async def remove_vip(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM vip_users WHERE user_id = ?", (user_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def list_vip(self) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT user_id, username, added_at FROM vip_users ORDER BY added_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # -------------------------------------------------------------
    # Dashboard & Statistics
    # -------------------------------------------------------------
    async def get_statistics(self) -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            # Auto-replies today
            async with db.execute(
                "SELECT COUNT(*) FROM message_logs WHERE date(created_at) = date('now')"
            ) as c:
                auto_replies_today = (await c.fetchone())[0]

            # Total auto-replies
            async with db.execute("SELECT COUNT(*) FROM message_logs") as c:
                auto_replies_total = (await c.fetchone())[0]

            # Missed calls today
            async with db.execute(
                "SELECT COUNT(*) FROM call_logs WHERE call_type = 'missed' AND date(created_at) = date('now')"
            ) as c:
                missed_calls_today = (await c.fetchone())[0]

            # Post-calls today
            async with db.execute(
                "SELECT COUNT(*) FROM call_logs WHERE call_type = 'post_call' AND date(created_at) = date('now')"
            ) as c:
                post_calls_today = (await c.fetchone())[0]

            # Birthdays sent this year
            current_year = datetime.now().year
            async with db.execute(
                "SELECT COUNT(*) FROM birthday_history WHERE year = ?", (current_year,)
            ) as c:
                birthdays_this_year = (await c.fetchone())[0]

            # VIP users count
            async with db.execute("SELECT COUNT(*) FROM vip_users") as c:
                vip_count = (await c.fetchone())[0]

            is_busy = await self.is_busy()

            return {
                "is_busy": is_busy,
                "auto_replies_today": auto_replies_today,
                "auto_replies_total": auto_replies_total,
                "missed_calls_today": missed_calls_today,
                "post_calls_today": post_calls_today,
                "birthdays_this_year": birthdays_this_year,
                "vip_count": vip_count,
            }

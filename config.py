"""Configuration loader for connect_telegram userbot."""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or workspace
load_dotenv()


def _get_bool(key: str, default: bool = True) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None or not val.strip():
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # Telegram API
    api_id_raw: str = os.getenv("API_ID", "")
    api_hash: str = os.getenv("API_HASH", "").strip()

    # Paths
    session_path: str = os.getenv("SESSION_PATH", "data/user_session")
    database_path: str = os.getenv("DATABASE_PATH", "data/userbot.db")

    # User Information
    owner_name: str = os.getenv("OWNER_NAME", "Shohjahon").strip()

    # Auto-Reply
    auto_reply_enabled: bool = _get_bool("AUTO_REPLY_ENABLED", True)
    auto_reply_cooldown_minutes: int = _get_int("AUTO_REPLY_COOLDOWN_MINUTES", 30)

    # Call Handlers
    call_handler_enabled: bool = _get_bool("CALL_HANDLER_ENABLED", True)
    missed_call_reply_enabled: bool = _get_bool("MISSED_CALL_REPLY_ENABLED", True)
    post_call_reply_enabled: bool = _get_bool("POST_CALL_REPLY_ENABLED", True)
    call_cooldown_minutes: int = _get_int("CALL_COOLDOWN_MINUTES", 15)

    # Birthday Scheduler
    birthday_enabled: bool = _get_bool("BIRTHDAY_ENABLED", True)
    birthday_check_hour: int = _get_int("BIRTHDAY_CHECK_HOUR", 0)
    birthday_check_minute: int = _get_int("BIRTHDAY_CHECK_MINUTE", 1)
    timezone: str = os.getenv("TIMEZONE", "Asia/Tashkent").strip()

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    @property
    def api_id(self) -> int:
        if not self.api_id_raw:
            return 0
        try:
            return int(self.api_id_raw)
        except ValueError:
            return 0

    def ensure_directories(self) -> None:
        """Create parent folders for database and session files if they don't exist."""
        session_dir = Path(self.session_path).parent
        db_dir = Path(self.database_path).parent
        session_dir.mkdir(parents=True, exist_ok=True)
        db_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """Validate critical settings."""
        errors: list[str] = []
        if not self.api_id:
            errors.append("API_ID belgilanmagan yoki noto'g'ri (raqam bo'lishi kerak). .env faylini tekshiring.")
        if not self.api_hash:
            errors.append("API_HASH belgilanmagan. .env faylini tekshiring.")
        return errors


config = Settings()
config.ensure_directories()

"""TelegramClient initialization and lifecycle management."""

import logging
from typing import Optional
from telethon import TelegramClient
from telethon.tl.types import User

from config import config

logger = logging.getLogger("connect_telegram.client")

_client: Optional[TelegramClient] = None
_me: Optional[User] = None


def get_telegram_client() -> TelegramClient:
    """Get or create singleton TelegramClient instance."""
    global _client
    if _client is None:
        validation_errors = config.validate()
        if validation_errors:
            for err in validation_errors:
                logger.error(err)
            raise ValueError("\n".join(validation_errors))

        _client = TelegramClient(
            config.session_path,
            config.api_id,
            config.api_hash,
            device_model="Desktop",
            system_version="Linux",
            app_version="1.0.0",
        )
    return _client


async def get_current_user(client: TelegramClient) -> User:
    """Cache and return current logged in user."""
    global _me
    if _me is None:
        _me = await client.get_me()
    return _me

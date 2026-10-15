"""Automatic reply handler for incoming private messages."""

import logging
from telethon import TelegramClient, events
from telethon.tl.types import User

from config import config
from database import Database
from templates import get_auto_reply_message

logger = logging.getLogger("connect_telegram.handlers.auto_reply")

# Official Telegram notification service user IDs
TELEGRAM_SERVICE_IDS = {777000, 42777}


def register_auto_reply_handler(client: TelegramClient, db: Database) -> None:
    """Register auto-reply event handler on client."""

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handle_incoming_message(event: events.NewMessage.Event) -> None:
        if not config.auto_reply_enabled:
            return

        # Check if userbot is in busy mode
        if not await db.is_busy():
            return

        sender_id = event.sender_id
        if not sender_id:
            return

        # Skip official Telegram notifications
        if sender_id in TELEGRAM_SERVICE_IDS:
            return

        # Don't respond to self
        me = await client.get_me()
        if sender_id == me.id:
            return

        # Get sender details
        try:
            sender = await event.get_sender()
        except Exception as e:
            logger.warning("Could not fetch sender for %s: %s", sender_id, e)
            sender = None

        # Ignore bots and deleted accounts
        if isinstance(sender, User):
            if sender.bot or sender.deleted:
                return

        # Ignore VIP users
        if await db.is_vip(sender_id):
            logger.debug("Skipping auto-reply for VIP user %s", sender_id)
            return

        # Check cooldown to prevent message flooding
        can_reply = await db.can_send_auto_reply(
            sender_id, config.auto_reply_cooldown_minutes
        )
        if not can_reply:
            logger.debug(
                "Cooldown active for user %s (last replied within %s mins)",
                sender_id,
                config.auto_reply_cooldown_minutes,
            )
            return

        # Send response
        reply_text = get_auto_reply_message(config.owner_name)
        try:
            await event.reply(reply_text)
            await db.record_auto_reply(sender_id, reply_type="busy")
            sender_name = getattr(sender, "first_name", str(sender_id))
            logger.info("Auto-reply sent to %s (ID: %s)", sender_name, sender_id)
        except Exception as e:
            logger.error("Failed to send auto-reply to %s: %s", sender_id, e)

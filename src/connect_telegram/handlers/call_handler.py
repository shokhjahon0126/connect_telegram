"""VoIP Telegram Phone Call handler (missed calls and post-call follow-ups)."""

import asyncio
import logging
from typing import Any
from telethon import TelegramClient, events
from telethon.tl.types import (
    UpdatePhoneCall,
    PhoneCallRequested,
    PhoneCallWaiting,
    PhoneCallAccepted,
    PhoneCallDiscarded,
    PhoneCallDiscardReasonBusy,
    PhoneCallDiscardReasonMissed,
    PhoneCallDiscardReasonHangup,
    PhoneCallDiscardReasonDisconnect,
)

from connect_telegram.config import config
from connect_telegram.database import Database
from connect_telegram.templates import get_missed_call_message, get_post_call_message

logger = logging.getLogger("connect_telegram.handlers.call_handler")

# In-memory registry of active calls: call_id -> dict
_active_calls: dict[int, dict[str, Any]] = {}


def register_call_handler(client: TelegramClient, db: Database) -> None:
    """Register raw UpdatePhoneCall handler for handling VoIP calls."""

    @client.on(events.Raw)
    async def handle_raw_call_updates(event: Any) -> None:
        if not config.call_handler_enabled:
            return

        if not isinstance(event, UpdatePhoneCall):
            return

        call = getattr(event, "phone_call", None)
        if not call:
            return

        me = await client.get_me()

        # -------------------------------------------------------------
        # 1. Incoming Call Request (PhoneCallRequested / PhoneCallWaiting)
        # -------------------------------------------------------------
        if isinstance(call, (PhoneCallRequested, PhoneCallWaiting)):
            admin_id = getattr(call, "admin_id", None)
            participant_id = getattr(call, "participant_id", None)

            # Check if this call is incoming (someone calling us)
            is_incoming = (participant_id == me.id) or (admin_id is not None and admin_id != me.id)
            caller_id = admin_id if is_incoming else participant_id

            if is_incoming and caller_id:
                _active_calls[call.id] = {
                    "caller_id": caller_id,
                    "is_answered": False,
                    "is_incoming": True,
                }
                logger.info("📞 Kiruvchi qo'ng'iroq aniqlandi (Call ID: %s, User: %s)", call.id, caller_id)

        # -------------------------------------------------------------
        # 2. Call Accepted / Connected (PhoneCallAccepted)
        # -------------------------------------------------------------
        elif isinstance(call, PhoneCallAccepted):
            call_info = _active_calls.get(call.id)
            if call_info:
                call_info["is_answered"] = True
                logger.info("📞 Qo'ng'iroqqa javob berildi va ulandi (Call ID: %s)", call.id)

        # -------------------------------------------------------------
        # 3. Call Ended / Discarded (PhoneCallDiscarded)
        # -------------------------------------------------------------
        elif isinstance(call, PhoneCallDiscarded):
            call_info = _active_calls.pop(call.id, None)
            reason = getattr(call, "reason", None)
            reason_name = type(reason).__name__ if reason else "Unknown"

            logger.info("📞 Qo'ng'iroq yakunlandi (Call ID: %s, Sabab: %s)", call.id, reason_name)

            if not call_info or not call_info.get("is_incoming"):
                return

            caller_id = call_info["caller_id"]
            was_answered = call_info.get("is_answered", False)

            # Check if call was missed or unanswered
            is_missed = (
                not was_answered
                or isinstance(reason, (PhoneCallDiscardReasonMissed, PhoneCallDiscardReasonBusy))
            )

            # A) MISSED CALL SCENARIO
            if is_missed and config.missed_call_reply_enabled:
                can_reply = await db.can_send_call_reply(caller_id, config.call_cooldown_minutes)
                if can_reply:
                    msg = get_missed_call_message(config.owner_name)
                    try:
                        # Short delay before sending message
                        await asyncio.sleep(2)
                        await client.send_message(caller_id, msg)
                        await db.record_call_reply(caller_id, "missed")
                        logger.info("📩 O'tkazib yuborilgan qo'ng'iroq xabari yuborildi: User %s", caller_id)
                    except Exception as e:
                        logger.error("O'tkazib yuborilgan qo'ng'iroq xabarini yuborishda xatolik: %s", e)
                else:
                    logger.debug("Qo'ng'iroq cooldown sabab xabar yuborilmadi: User %s", caller_id)

            # B) POST-CALL (SUCCESSFUL CONVERSATION) SCENARIO
            elif was_answered and config.post_call_reply_enabled:
                # Wait 3 seconds after hanging up to look natural
                await asyncio.sleep(3)
                can_reply = await db.can_send_call_reply(caller_id, config.call_cooldown_minutes)
                if can_reply:
                    msg = get_post_call_message(config.owner_name)
                    try:
                        await client.send_message(caller_id, msg)
                        await db.record_call_reply(caller_id, "post_call")
                        logger.info("✨ Suhbat yakunlanganidan keyin minnatdorchilik xabari yuborildi: User %s", caller_id)
                    except Exception as e:
                        logger.error("Suhbat yakunlash xabarini yuborishda xatolik: %s", e)

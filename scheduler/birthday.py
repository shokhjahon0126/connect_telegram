"""APScheduler-based periodic birthday greeting job."""

import asyncio
import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient, functions

from config import config
from database import Database
from templates import get_birthday_message

logger = logging.getLogger("connect_telegram.scheduler.birthday")


async def check_and_send_birthdays(client: TelegramClient, db: Database) -> int:
    """Check Telegram contacts for birthdays today and send congratulatory messages."""
    try:
        tz = pytz.timezone(config.timezone)
    except Exception:
        tz = pytz.timezone("Asia/Tashkent")

    now = datetime.now(tz)
    today_day = now.day
    today_month = now.month
    today_year = now.year

    logger.info("🎂 Tug'ilgan kunlarni tekshirish boshlandi: Sana %02d.%02d.%04d", today_day, today_month, today_year)

    try:
        result = await client(functions.contacts.GetBirthdaysRequest())
    except Exception as e:
        logger.error("Telegram API orqali tug'ilgan kunlarni olishda xatolik: %s", e)
        return 0

    if not result or not result.contacts:
        logger.info("Bugungi sana uchun tug'ilgan kunlar topilmadi.")
        return 0

    users_dict = {user.id: user for user in result.users}
    sent_count = 0

    for contact in result.contacts:
        birthday = getattr(contact, "birthday", None)
        if not birthday:
            continue

        # Match day and month
        if birthday.day == today_day and birthday.month == today_month:
            user_id = contact.contact_id

            # Avoid duplicate greetings for the same calendar year
            already_sent = await db.is_birthday_already_sent(user_id, today_year)
            if already_sent:
                logger.debug("User %s ga bu yil (%s) allaqachon tabrik yuborilgan.", user_id, today_year)
                continue

            user = users_dict.get(user_id)
            first_name = user.first_name if user and user.first_name else ""
            age = (today_year - birthday.year) if getattr(birthday, "year", None) else None

            message = get_birthday_message(first_name, config.owner_name, age)

            try:
                await client.send_message(user_id, message)
                await db.record_birthday_sent(user_id, today_year)
                sent_count += 1
                logger.info(
                    "🎉 Tug'ilgan kun tabrigi yuborildi: %s (ID: %s)",
                    first_name or "Kontakt",
                    user_id,
                )
                # Sleep to prevent FloodWait / rate limiting
                await asyncio.sleep(5)
            except Exception as e:
                logger.error("User %s ga tabrik yuborishda xatolik: %s", user_id, e)

    logger.info("Tug'ilgan kun tekshiruvi yakunlandi. Jami yuborilgan: %s ta", sent_count)
    return sent_count


def setup_birthday_scheduler(client: TelegramClient, db: Database) -> AsyncIOScheduler:
    """Initialize and start the APScheduler for birthday checks."""
    try:
        tz = pytz.timezone(config.timezone)
    except Exception:
        tz = pytz.timezone("Asia/Tashkent")

    scheduler = AsyncIOScheduler(timezone=tz)

    scheduler.add_job(
        check_and_send_birthdays,
        trigger="cron",
        hour=config.birthday_check_hour,
        minute=config.birthday_check_minute,
        args=[client, db],
        id="daily_birthday_checker",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "Tug'ilgan kun scheduleri faollashtirildi: Har kuni %02d:%02d da (%s)",
        config.birthday_check_hour,
        config.birthday_check_minute,
        config.timezone,
    )
    return scheduler

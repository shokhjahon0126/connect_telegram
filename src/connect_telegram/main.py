"""Main application entry point for connect_telegram userbot."""

import asyncio
import logging
import signal
import sys
from telethon import TelegramClient

from connect_telegram.config import config
from connect_telegram.database import Database
from connect_telegram.client import get_telegram_client
from connect_telegram.handlers import (
    register_auto_reply_handler,
    register_call_handler,
    register_command_handlers,
)
from connect_telegram.scheduler import setup_birthday_scheduler

BANNER = r"""
============================================================
   🤖 CONNECT-TELEGRAM USERBOT — TELETHON AUTOMATION
============================================================
"""


def setup_logging() -> None:
    """Configure formatted console logging."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    level = getattr(logging, config.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Silence overly verbose external loggers
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


async def async_main() -> None:
    """Async main routine."""
    setup_logging()
    logger = logging.getLogger("connect_telegram.main")
    print(BANNER)

    # 1. Check credentials
    validation_errors = config.validate()
    if validation_errors:
        logger.error("Konfiguratsiya xatosi:\n" + "\n".join(f"  • {e}" for e in validation_errors))
        print("\n" + "=" * 60)
        print("DIQQAT: Userbotni ishga tushirish uchun .env fayli kerak!")
        print("1. .env.example faylidan nusxa olib, .env faylini yarating:")
        print("   cp .env.example .env")
        print("2. .env fayliga my.telegram.org saytidan olgan API_ID va API_HASH'ingizni yozing.")
        print("=" * 60 + "\n")
        sys.exit(1)

    # 2. Initialize Database
    db = Database(config.database_path)
    await db.init()

    # 3. Initialize TelegramClient
    client: TelegramClient = get_telegram_client()

    # 4. Register Event Handlers
    register_auto_reply_handler(client, db)
    register_call_handler(client, db)
    register_command_handlers(client, db)

    # 5. Connect and Authorize
    logger.info("Telegram'ga ulanmoqda...")
    await client.start()

    me = await client.get_me()
    phone = f"+{me.phone}" if me.phone else "Raqam yashiringan"
    logger.info("Muvaffaqiyatli ulandi! Profil: %s (@%s | %s)", me.first_name, me.username or "username_yoq", phone)

    # 6. Setup Birthday Scheduler
    scheduler = None
    if config.birthday_enabled:
        scheduler = setup_birthday_scheduler(client, db)

    stats = await db.get_statistics()
    status_str = "Bandlik rejimi faol" if stats["is_busy"] else "Erkin rejim faol"
    logger.info("Tizim to'liq ishga tushdi (%s). Xabarlar kutilyapti...", status_str)

    # 7. Graceful Shutdown Handler
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("To'xtatish signali qabul qilindi. Jarayonlar to'xtatilmoqda...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    # Run until disconnected or signal received
    client_task = asyncio.create_task(client.run_until_disconnected())
    stop_task = asyncio.create_task(stop_event.wait())

    done, pending = await asyncio.wait(
        [client_task, stop_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    # Teardown
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler to'xtatildi.")

    if client.is_connected():
        await client.disconnect()
        logger.info("TelegramClient uzildi.")

    logger.info("Userbot to'liq to'xtatildi. Xayr!")


def main() -> None:
    """Sync wrapper for package entrypoint."""
    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()

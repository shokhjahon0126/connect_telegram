"""Scheduler package for connect_telegram."""

from connect_telegram.scheduler.birthday import setup_birthday_scheduler, check_and_send_birthdays

__all__ = ["setup_birthday_scheduler", "check_and_send_birthdays"]

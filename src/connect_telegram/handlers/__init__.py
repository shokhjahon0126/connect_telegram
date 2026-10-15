"""Event handlers package for connect_telegram."""

from connect_telegram.handlers.auto_reply import register_auto_reply_handler
from connect_telegram.handlers.call_handler import register_call_handler
from connect_telegram.handlers.commands import register_command_handlers

__all__ = [
    "register_auto_reply_handler",
    "register_call_handler",
    "register_command_handlers",
]

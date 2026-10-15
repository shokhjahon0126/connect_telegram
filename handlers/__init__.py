"""Event handlers package for connect_telegram."""

from handlers.auto_reply import register_auto_reply_handler
from handlers.call_handler import register_call_handler
from handlers.commands import register_command_handlers

__all__ = [
    "register_auto_reply_handler",
    "register_call_handler",
    "register_command_handlers",
]

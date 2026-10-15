"""Owner commands handler for managing the userbot."""

import logging
from typing import Optional
from telethon import TelegramClient, events, functions
from telethon.tl.types import User

from config import config
from database import Database
from templates import get_help_message

logger = logging.getLogger("connect_telegram.handlers.commands")


def register_command_handlers(client: TelegramClient, db: Database) -> None:
    """Register commands available exclusively to the account owner."""

    @client.on(events.NewMessage(outgoing=True))
    async def handle_owner_commands(event: events.NewMessage.Event) -> None:
        text = (event.raw_text or "").strip()
        if not text:
            return

        # Commands can start with '.' or '/'
        if not (text.startswith(".") or text.startswith("/")):
            return

        parts = text[1:].split()
        if not parts:
            return

        command = parts[0].lower()
        args = parts[1:]

        # -------------------------------------------------------------
        # 1. HELP
        # -------------------------------------------------------------
        if command in ("help", "yordam"):
            await event.edit(get_help_message())
            return

        # -------------------------------------------------------------
        # 2. STATUS & DASHBOARD
        # -------------------------------------------------------------
        if command in ("status", "holat"):
            stats = await db.get_statistics()
            status_emoji = "🔴 BAND" if stats["is_busy"] else "🟢 BO'SH"

            report = (
                "📊 **Connect-Telegram Tizim Holati**\n\n"
                f"• **Rejim:** {status_emoji}\n"
                f"• **Foydalanuvchi:** {config.owner_name}\n"
                f"• **Vaqt zonasi:** {config.timezone}\n"
                f"• **Cooldown:** {config.auto_reply_cooldown_minutes} daqiqa\n\n"
                "📈 **Bugungi Ko'rsatkichlar:**\n"
                f"  📨 Avto-javoblar (bugun): **{stats['auto_replies_today']}** ta\n"
                f"  📬 Jami avto-javoblar: **{stats['auto_replies_total']}** ta\n"
                f"  📞 O'tkazib yuborilgan qo'ng'iroqlar: **{stats['missed_calls_today']}** ta\n"
                f"  🤝 Suhbatdan keyingi xabarlar: **{stats['post_calls_today']}** ta\n"
                f"  🎂 Bu yil tabriklanganlar: **{stats['birthdays_this_year']}** ta\n"
                f"  ⭐ VIP foydalanuvchilar: **{stats['vip_count']}** ta\n"
            )
            await event.edit(report)
            return

        # -------------------------------------------------------------
        # 3. BUSY / FREE MODE TOGGLE
        # -------------------------------------------------------------
        if command in ("busy", "band"):
            await db.set_busy(True)
            await event.edit(
                "🔴 **Bandlik rejimi yoqildi!**\n\n"
                "Endi shaxsiy xabarlarga avtomatik tarzda band ekanligingiz haqida javob yuboriladi."
            )
            return

        if command in ("free", "bosh", "bo'sh"):
            await db.set_busy(False)
            await event.edit(
                "🟢 **Erkin rejim yoqildi!**\n\n"
                "Avto-javob xabarlari vaqtincha to'xtatildi. Faqat o'zingiz xabar yozasiz."
            )
            return

        # -------------------------------------------------------------
        # 4. VIP USERS MANAGEMENT
        # -------------------------------------------------------------
        if command == "vip":
            if not args:
                await event.edit(
                    "ℹ️ **VIP boshqaruv formati:**\n"
                    "• `.vip list` — Ro'yxatni ko'rish\n"
                    "• `.vip add <id|username>` — VIP qo'shish\n"
                    "• `.vip remove <id|username>` — VIP dan chiqarish"
                )
                return

            subcmd = args[0].lower()

            if subcmd == "list":
                vips = await db.list_vip()
                if not vips:
                    await event.edit("⭐ **VIP ro'yxati hozircha bo'sh.**")
                    return

                vip_lines = [
                    f"• ID: `{v['user_id']}` {('@' + v['username']) if v.get('username') else ''} (Qo'shilgan: {v['added_at'][:10]})"
                    for v in vips
                ]
                await event.edit("⭐ **VIP Ro'yxati (Avto-javob bormaydiganlar):**\n\n" + "\n".join(vip_lines))
                return

            if subcmd in ("add", "qo'sh"):
                if len(args) < 2:
                    await event.edit("❌ Iltimos, foydalanuvchi ID yoki @username'ni kiriting: `.vip add @username`")
                    return

                target = args[1]
                try:
                    entity = await client.get_entity(target)
                    user_id = entity.id
                    username = getattr(entity, "username", "") or ""
                    await db.add_vip(user_id, username)
                    name = getattr(entity, "first_name", str(user_id))
                    await event.edit(f"✅ **{name}** (`{user_id}`) VIP ro'yxatiga muvaffaqiyatli qo'shildi!")
                except Exception as e:
                    await event.edit(f"❌ Foydalanuvchini topib bo'lmadi: {e}")
                return

            if subcmd in ("remove", "del", "o'chir"):
                if len(args) < 2:
                    await event.edit("❌ Iltimos, foydalanuvchi ID yoki @username'ni kiriting: `.vip remove <id>`")
                    return

                target = args[1]
                try:
                    entity = await client.get_entity(target)
                    user_id = entity.id
                    removed = await db.remove_vip(user_id)
                    if removed:
                        await event.edit(f"✅ Foydalanuvchi (`{user_id}`) VIP ro'yxatidan o'chirildi.")
                    else:
                        await event.edit("❌ Bu foydalanuvchi VIP ro'yxatida topilmadi.")
                except Exception as e:
                    # Try raw numeric ID
                    try:
                        uid = int(target)
                        removed = await db.remove_vip(uid)
                        if removed:
                            await event.edit(f"✅ Foydalanuvchi (`{uid}`) VIP ro'yxatidan o'chirildi.")
                        else:
                            await event.edit("❌ Bu foydalanuvchi VIP ro'yxatida topilmadi.")
                    except ValueError:
                        await event.edit(f"❌ Xatolik yuz berdi: {e}")
                return

        # -------------------------------------------------------------
        # 5. BIRTHDAY COMMANDS
        # -------------------------------------------------------------
        if command in ("birthdays", "tugulgan_kunlar"):
            try:
                result = await client(functions.contacts.GetBirthdaysRequest())
                if not result.contacts:
                    await event.edit("🎂 Yaqin kunlarda tug'ilgan kuni bo'lgan kontaktlar topilmadi.")
                    return

                users_dict = {u.id: u for u in result.users}
                lines = []
                for contact in result.contacts:
                    user = users_dict.get(contact.contact_id)
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip() if user else f"ID: {contact.contact_id}"
                    bd = contact.birthday
                    year_str = f"/{bd.year}" if getattr(bd, "year", None) else ""
                    lines.append(f"• **{name}**: {bd.day:02d}.{bd.month:02d}{year_str}")

                await event.edit("🎂 **Bugun / Yaqin kunlarda tug'ilgan kunlar:**\n\n" + "\n".join(lines))
            except Exception as e:
                await event.edit(f"❌ Tug'ilgan kunlarni olishda xatolik: {e}")
            return

        if command in ("check_birthdays", "sinash_tugulgan_kun"):
            from scheduler.birthday import check_and_send_birthdays
            await event.edit("🔄 Tug'ilgan kunlarni tekshirish boshlanmoqda...")
            sent_count = await check_and_send_birthdays(client, db)
            await event.edit(f"🎉 Tekshirish tugadi! Bugun yuborilgan tabriklar soni: **{sent_count}** ta.")
            return

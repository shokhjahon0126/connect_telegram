"""Interactive QR Code login helper for Telegram userbot."""
import asyncio
import sys
from pathlib import Path

import qrcode
from telethon import errors
from config import config
from client import get_telegram_client


async def qr_login_main():
    print("=" * 60)
    print("   📲 TELEGRAM QR-KOD ORQALI KIRISH")
    print("=" * 60)
    print("SMS yoki Telegram kodini kutish shart emas!\n")
    print("1. Telefoningizda Telegram ilovasini oching.")
    print("2. Sozlamalar (Settings) -> Qurilmalar (Devices) bo'limiga kiring.")
    print("3. 'Desktop qurilmani ulash' (Link Desktop Device) tugmasini bosing.")
    print("4. Terminalda chiqadigan QR-kodni kamerangiz bilan skanerlang.\n")

    client = get_telegram_client()
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"✅ Akkaunt allaqachon ulangan: {me.first_name} (@{me.username})")
        await client.disconnect()
        return

    qr_login = await client.qr_login()

    # Print ASCII QR Code to terminal
    qr = qrcode.QRCode(border=1)
    qr.add_data(qr_login.url)
    qr.print_ascii(invert=True)

    print("\n⏳ Skanerlash kutilmoqda (telefoningizda skanerlang)...")

    try:
        await qr_login.wait(timeout=120)
    except errors.SessionPasswordNeededError:
        print("\n🔒 Ikki bosqichli parol (2FA) yoqilgan.")
        import getpass
        password = getpass.getpass("Iltimos, 2FA parolingizni kiriting: ")
        await client.sign_in(password=password)
    except asyncio.TimeoutError:
        print("\n❌ Vaqt tugadi (2 daqiqa). Qaytadan ishga tushiring.")
        await client.disconnect()
        return

    me = await client.get_me()
    phone = f"+{me.phone}" if me.phone else "Raqam yashiringan"
    print("\n" + "=" * 60)
    print("🎉 MUVAFFAQIYATLI ULANDI!")
    print(f"Profil: {me.first_name} (@{me.username or 'username_yoq'} | {phone})")
    print("Sessiya fayli saqlandi: data/user_session.session")
    print("=" * 60)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(qr_login_main())

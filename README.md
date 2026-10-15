# 🤖 Connect-Telegram — Shaxsiy Telegram Avtomatlashtirish Userboti

Telethon va Python 3.12 yordamida yaratilgan, shaxsiy Telegram akkauntingizni professional darajada avtomatlashtiruvchi userbot tizimi.

---

## 🌟 Asosiy Imkoniyatlar

1. **📩 Aqlli Auto-Reply (Bandlik xabari):**
   - Kimdir shaxsiy xat yozganda: *"Hozirda muhim loyihalar ustida ishlayapman..."* deb avtomatik javob qaytaradi.
   - **Cooldown tizimi:** Bitta insonga har 30 daqiqada (sozlanadi) faqat 1 marta javob beradi (spam bo'lmaydi).
   - Faqat shaxsiy chatlarga javob beradi (guruhlar, kanallar va botlar filtrlanadi).

2. **📞 VoIP Qo'ng'iroqlarni Boshqarish:**
   - **O'tkazib yuborilgan qo'ng'iroq:** Agar siz qo'ng'iroqni ko'tara olmasangiz, qo'ng'iroq qilgan shaxsga avtomatik kechirim va qisqa xabar qoldirishni so'rovchi matn yuboriladi.
   - **Suhbat yakunlanganda:** Muvaffaqiyatli suhbatdan so'ng darhol samimiy va chiroyli minnatdorchilik xabari jo'natiladi (*"Siz bilan gaplashganimizdan juda xursandman..."*).

3. **🎂 Kontaktlarning Tug'ilgan Kunini Avtomatik Tabriklash:**
   - Har kuni 00:01 da (Toshkent vaqti bilan) yangi kun boshlanishi bilanoq kontaktlaringizni tekshiradi.
   - Bugun tug'ilgan kuni bo'lgan do'stlaringizga ularning ismini qo'shib, 3 xil chiroyli va samimiy shablondan birini yuboradi.
   - Bitta insonni bir yilda ikki marta tabriklamaydi (SQLite orqali nazorat qilinadi).

4. **⭐ VIP Ro'yxat Tizimi:**
   - O'zingiz xohlagan muhim insonlarni (ota-ona, rahbar yoki yaqin do'stlar) VIP ro'yxatga qo'shishingiz mumkin — ularga hech qachon avto-javob bormaydi.

5. **⚡ Shaxsiy Boshqaruv Buyruqlari:**
   - O'zingizning istalgan chatingiz yoki *Saqlangan xabarlar* (Saved Messages) orqali userbotni boshqarish mumkin:
     - `.status` — Tizim holati va bugungi statistika
     - `.busy` — Bandlik rejimini yoqish
     - `.free` — Erkin rejimni yoqish (avto-javoblarni to'xtatish)
     - `.vip list` — VIP foydalanuvchilar ro'yxati
     - `.vip add @username` — VIP ro'yxatiga qo'shish
     - `.vip remove <id>` — VIP dan chiqarish
     - `.birthdays` — Yaqin kunlardagi tug'ilgan kunlar
     - `.check_birthdays` — Tug'ilgan kun tekshiruvini darhol sinash
     - `.help` — Buyruqlar ro'yxati

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) paket menejeri (tavsiya etiladi)

### 2. Bog'liqliklarni o'rnatish
```bash
uv sync
```

### 3. Telegram API ma'lumotlarini olish
1. [my.telegram.org](https://my.telegram.org) saytiga telefon raqamingiz orqali kiring.
2. **API development tools** bo'limiga o'ting.
3. Yangi dastur yarating (masalan, nomi: `MyUserbot`) va `api_id` hamda `api_hash` ma'lumotlarini oling.

### 4. Konfiguratsiyani sozlash (.env)
Namuna nusxasini yarating:
```bash
cp .env.example .env
```
So'ngra `.env` faylini ochib, ma'lumotlaringizni kiriting:
```env
API_ID=12345678
API_HASH=abcdef0123456789abcdef0123456789
OWNER_NAME=Shohjahon
AUTO_REPLY_ENABLED=true
AUTO_REPLY_COOLDOWN_MINUTES=30
TIMEZONE=Asia/Tashkent
```

### 5. Dasturni ishga tushirish
```bash
uv run connect-telegram
```

> [!NOTE]
> **Birinchi marta kirish:** Dastur terminalda sizdan telefon raqamingizni (masalan, `+998901234567`) va Telegram orqali kelgan tasdiqlash kodini kiritishingizni so'raydi. Agar ikki bosqichli parol (2FA) yoqilgan bo'lsa, parolingizni ham so'raydi. Shundan so'ng login ma'lumotlari `data/user_session.session` faylida xavfsiz saqlanadi va keyingi safar kod so'ramaydi.

---

## 📁 Loyiha Strukturasi

```
connect_telegram/
├── src/
│   └── connect_telegram/
│       ├── __init__.py          # Paket eksporti
│       ├── main.py              # Dastur entrypoint va lifecycle boshqaruvi
│       ├── config.py            # .env yuklovchi va tekshiruvchi modul
│       ├── client.py            # Telethon TelegramClient yaratish
│       ├── database.py          # SQLite ma'lumotlar bazasi (aiosqlite)
│       ├── templates.py         # O'zbekcha chiroyli xabar shablonlari
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── auto_reply.py    # Kiruvchi xabarlar uchun avto-javob
│       │   ├── call_handler.py  # VoIP qo'ng'iroqlarni tutuvchi handler
│       │   └── commands.py      # Shaxsiy boshqaruv komandalari
│       └── scheduler/
│           ├── __init__.py
│           └── birthday.py      # APScheduler orqali tug'ilgan kun tabriklari
├── .agents/
│   └── plan.md                  # Loyihaning to'liq texnik rejasi
├── data/                        # Baza va sessiya fayllari (gitignore'da)
├── .env.example                 # Sozlamalar namunasi
├── .gitignore                   # Xavfsizlik uchun maxfiy fayllarni cheklash
└── pyproject.toml               # Loyiha metadata va dependensiyalari
```

---

## 🔒 Xavfsizlik va Tavsiyalar
- `.env` va `data/*.session` fayllarini hech qachon birovga bermang yoki GitHub'ga yuklamang (ular `.gitignore` orqali himoyalangan).
- Telegram spam filtrlariga tushmaslik uchun barcha xabarlarga avtomatik cooldown va kechikishlar (`asyncio.sleep`) o'rnatilgan.
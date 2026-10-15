"""Predefined and dynamic Uzbek message templates for connect_telegram."""

import random
from typing import Optional


def get_auto_reply_message(owner_name: str) -> str:
    """Generate professional and polite auto-reply message when busy."""
    return (
        "🔔 **Assalomu alaykum!**\n\n"
        "Hozirda muhim dasturlash va texnik loyihalar ustida diqqat bilan ishlayapman, "
        "shu sababli xabarlarga darhol javob bera olmayapman.\n\n"
        "📌 **Holat:** Band (Fokus rejimi)\n"
        "⏰ Bo'shashim bilan sizga albatta batafsil javob yozaman!\n\n"
        "📞 *Agar kechiktirib bo'lmaydigan o'ta shoshilinch masala bo'lsa, "
        "Telegram orqali qo'ng'iroq qilib ko'ring.*\n\n"
        f"Hurmat bilan,\n**{owner_name}** 🙏"
    )


def get_missed_call_message(owner_name: str) -> str:
    """Generate polite message when an incoming call was missed / unanswered."""
    return (
        "📞 **Qo'ng'irog'ingizga javob bera olmadim**\n\n"
        "Assalomu alaykum! Qo'ng'iroq qilganingiz uchun tashakkur.\n"
        "Afsuski, hozir qo'ng'iroqqa javob berish imkoniyati bo'lmadi "
        "(muhim ish jarayoni yoki uchrashuvdaman).\n\n"
        "💬 **Iltimos:** Agar masala bo'yicha qisqacha xabar qoldirsangiz, "
        "imkon bo'lishi bilanoq sizga o'zim qayta aloqaga chiqaman!\n\n"
        f"Keltirilgan noqulaylik uchun uzr so'rayman.\nHurmat bilan, **{owner_name}** 🙏"
    )


def get_post_call_message(owner_name: str) -> str:
    """Generate warm thank you message after completing a phone conversation."""
    variants = [
        (
            "✨ **Samimiy suhbat uchun rahmat!**\n\n"
            "Siz bilan gaplashganimizdan juda mamnun bo'ldim! 😊\n\n"
            "Muloqotimiz ikkalamiz uchun ham unumli va manfaatli bo'ldi deb umid qilaman. "
            "Doimo aloqada bo'laylik! Yangi fikrlar, takliflar yoki savollar paydo bo'lsa, bemalol yozing.\n\n"
            "Kuningiz xayrli, maroqli va barakali o'tsin! ☀️\n\n"
            f"Hurmat bilan,\n**{owner_name}** 🤝"
        ),
        (
            "🤝 **Ajoyib muloqot uchun tashakkur!**\n\n"
            "Siz bilan suhbatlashish har doim yoqimli va foydali! 😊\n"
            "Kelishilgan masalalar bo'yicha yana bog'lanib turamiz.\n\n"
            "Ishlaringizga ulkan zafarlar va omad tilayman! 🚀\n\n"
            f"Ehtirom bilan,\n**{owner_name}** ✨"
        ),
    ]
    return random.choice(variants)


def get_birthday_message(name: str, owner_name: str, age: Optional[int] = None) -> str:
    """Generate inspiring and celebratory birthday greetings."""
    display_name = name.strip() if name and name.strip() else "Aziz do'stim"

    templates = [
        (
            f"🎂🎉 **Tug'ilgan kuningiz muborak bo'lsin, {display_name}!**\n\n"
            "Bugungi quvonchli va maxsus kuningiz munosabati bilan sizga samimiy "
            "tabriklarim va eng ezgu tilaklarimni yo'llayman!\n\n"
            "🌟 Sizga mustahkam sog'liq, oilaviy baxt-saodat, xotirjamlik va "
            "kelajakdagi barcha buyuk maqsadlaringiz ro'yobini tilayman!\n"
            "🚀 Har bir boshlagan ishingizda muvaffaqiyat, omad va yuksak cho'qqilar yor bo'lsin!\n\n"
            "Bugungi kuningiz ajoyib taassurotlar va yorqin xotiralarga boy bo'lsin! 🥳🎊\n\n"
            f"Chin dildan,\n**{owner_name}** 🎈"
        ),
        (
            f"🎊 **Happy Birthday, {display_name}!** 🎂✨\n\n"
            f"Sizni tavallud ayyomingiz bilan chin qalbimdan muborakbod etaman!\n\n"
            "🎯 Yangi yoshingizda:\n"
            "  • Yangi va ulkan cho'qqilarni zabt eting!\n"
            "  • Barcha orzu va rejalaringiz o'ngidan kelsin!\n"
            "  • Hayotingiz doimo quvonch, mehr va omadga to'lsin!\n\n"
            "🎁 Umringiz uzoq va mazmunli bo'lsin! Bayramingiz zavqli o'tsin! 🎉\n\n"
            f"Eng yaxshi tilaklar bilan,\n**{owner_name}** 💙"
        ),
        (
            f"🌟 **{display_name}, tavallud kuningiz qutlug' bo'lsin!** 💐\n\n"
            "Hayotdagi eng qadrli ne'matlar — sog'lik, xotirjamlik, baxt va "
            "yaxshi insonlar davrasi sizni hech qachon tark etmasin!\n\n"
            "🏆 Har bir kuningiz yangi imkoniyatlar, yutuqlar va samimiy quvonchlar olib kelsin.\n"
            "Yuzingizdan tabassum, qalbingizdan ezgulik arimasin! 🥳\n\n"
            f"Hurmat va ehtirom bilan,\n**{owner_name}** 🎈"
        ),
    ]

    return random.choice(templates)


def get_help_message() -> str:
    """Help message listing commands available to the owner."""
    return (
        "🤖 **Connect-Telegram Userbot Boshqaruv Paneli**\n\n"
        "O'zingizning shaxsiy yoki *Saqlangan xabarlar* chatingizdan quyidagi buyruqlarni yuborishingiz mumkin:\n\n"
        "📊 **Holat va Statistika:**\n"
        "• `.status` yoki `/status` — Tizim holati va bugungi statistika\n"
        "• `.help` yoki `/help` — Ushbu yordam xabarini ko'rsatish\n\n"
        "🔀 **Bandlik Rejimi:**\n"
        "• `.busy` yoki `/busy` — Band rejimini yoqish (avto-javob faol)\n"
        "• `.free` yoki `/free` — Erkin rejim (avto-javob o'chiriladi)\n\n"
        "⭐ **VIP Ro'yxat (Avto-javob bormaydigan shaxslar):**\n"
        "• `.vip add <id|@username>` — VIP ro'yxatiga qo'shish\n"
        "• `.vip remove <id|@username>` — VIP dan chiqarish\n"
        "• `.vip list` — Hozirgi VIP foydalanuvchilar\n\n"
        "🎂 **Tug'ilgan Kun:**\n"
        "• `.check_birthdays` — Tug'ilgan kun tekshiruvini darhol sinash\n"
        "• `.birthdays` — Bugun tug'ilgan kuni bo'lgan kontaktlarni ko'rish\n"
    )

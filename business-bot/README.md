# Telegram Business Bot — ELYOR.DEV demo

A real Telegram bot prototype, separate from the interactive browser-only preview. This is a portfolio learning sample, not a production-ready booking or payment service.

**Interactive browser demo:** https://elyormakhmanazarov67-star.github.io/business-bot-demo.html

## Nimalar ishlaydi?

- /start — xizmatlar menyusi (veb-sayt, Telegram-bot, Mini App, avtomatlashtirish)
- Xizmat tanlash → qisqa tavsif yuborish → yangi buyurtmani saqlash
- Buyurtmalar SQLite bazasiga yoziladi
- Administratorga buyurtma haqida xabar yuboriladi
- Administrator buyruqlari: /orders, /stats, /done N
- /cancel — jarayonni bekor qilish
- /id — o‘z Telegram chat ID raqamingizni ko‘rsatadi
- Qayta ishga tushirilganda buyurtmalar bazada qoladi

### Texnologiyalar

Python 3.10+, Python standard library, sqlite3, Telegram Bot API (long polling).

**Muhim:** brauzer demosi va haqiqiy bot bir-biriga ulanmagan. Brauzer demosidagi so‘rovlar serverga yuborilmaydi. Real bot uchun Telegram token va ishlayotgan kompyuter yoki hosting kerak.

## Windows 11 da ishga tushirish

1. Telegram ichida **@BotFather** orqali yangi bot yarating. Tokenni hech kimga yubormang va GitHub’ga joylamang.
2. Python 3.10+ o‘rnatilganini tekshiring: py --version
3. Ushbu papkani yuklab oling yoki GitHub’dan klonlang. PowerShell’da shu papkani oching.
4. Terminalda quyidagi buyruqlarni bajaring (qiymatlarni o‘zingiznikiga almashtiring):

    $env:BOT_TOKEN = "TOKEN_HERE"
    $env:ADMIN_CHAT_ID = "YOUR_NUMERIC_CHAT_ID"
    py bot.py

   Administrator ID raqamingizni bilmasangiz, botni boshlang, /id yuboring va uni oling. Admin ID ni yangilab, dasturni qayta ishga tushiring.
5. Telegram botga /start yuboring, xizmat tanlang va faqat demo ma’lumotlar bilan sinab ko‘ring.
6. Administrator sifatida /orders, /stats, /done 1 buyruqlarini tekshiring.

To‘xtatish: Ctrl+C.

**Tokenni screenshotda ko‘rsatmang.** Token tarqalib ketsa, BotFather’dan uni yangilang. Repo ichiga token, haqiqiy foydalanuvchi ma’lumotlari yoki orders.sqlite3 faylini joylamang.

## Cheklovlar

- Bot long polling ishlatadi. Kompyuter o‘chirilsa bot ham to‘xtaydi.
- To‘lov, haqiqiy bron qilish, avtomatik server va reklama ommaviy xabarlari funksiyalari yo‘q.
- Real foydalanuvchilar bilan ishga tushirishdan oldin maxfiylik, ma’lumotlarni o‘chirish, zaxiralash va hosting xavfsizligini alohida ishlab chiqish kerak.
- Bot mijozlardan parol va boshqa maxfiy ma’lumotlarni so‘ramaydi.

## Offline test

    py -m unittest discover -s tests -v

Testlar Telegram tokenisiz ishlaydi.

Portfolio: [ELYOR.DEV](https://elyormakhmanazarov67-star.github.io/) · Aloqa: [@eywn88](https://t.me/eywn88)

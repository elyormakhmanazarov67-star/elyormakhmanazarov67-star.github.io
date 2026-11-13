# Telegram Business Bot — ELYOR.DEV demo

A real Telegram bot prototype, separate from the interactive browser-only preview. This is a portfolio learning sample, not a production-ready booking or payment service.

**Interactive browser demo:** https://elyormakhmanazarov67-star.github.io/business-bot-demo.html

## Nimalar ishlaydi?

- /start — xizmatlar menyusi (veb-sayt, Telegram-bot, Mini App, avtomatlashtirish)
- /services — xizmatlar tavsifi va boshlang‘ich narxlar (kichik MVP)
- Birinchi mijozlar uchun narxlar: Veb-sayt 990 000 so‘mdan, Telegram-bot 550 000 so‘mdan, Mini App 1 590 000 so‘mdan, bitta sodda avtomatlashtirish 990 000 so‘mdan
- Narxlarga domen, hosting, pullik API va murakkab integratsiyalar kirmaydi; narxlar loyiha hajmi aniqlangach tasdiqlanadi
- /myorders — mijoz o‘zining oxirgi 5 ta buyurtmasi holatini ko‘radi
- /contact — ELYOR.DEV bilan aloqa
- Xizmat tanlash → qisqa tavsif yuborish → yangi buyurtmani saqlash
- Buyurtmalar SQLite bazasiga yoziladi
- Administratorga buyurtma haqida xabar yuboriladi
- Administrator buyruqlari: /orders, /pending, /order N, /stats, /done N
- /cancel — jarayonni bekor qilish
- /id — o‘z Telegram chat ID raqamingizni ko‘rsatadi
- Qayta ishga tushirilganda buyurtmalar bazada qoladi

### Texnologiyalar

Python 3.10+, Python standard library, sqlite3, Telegram Bot API (long polling).

**Muhim:** brauzer demosi va haqiqiy bot bir-biriga ulanmagan. Brauzer demosidagi so‘rovlar serverga yuborilmaydi. Haqiqiy bot Railway hostingida ishlaydi: https://t.me/ElyorBusinessDemoBot.

## Birinchi mijoz taklifi

550 000 so‘mdan Telegram Business Bot taklifi: menyu, oddiy buyurtma qabul qilish, administrator xabari va buyurtma holati. Demo: https://t.me/ElyorBusinessDemoBot. Bu narx faqat kichik talablar to‘plami uchun; mijozga real ishga tushirishdan oldin maxfiylik, texnik qo‘llab-quvvatlash, qo‘shimcha servislar narxi va ma’lumotlarni boshqarish kelishiladi.

## Railway hosting

Bot alohida `elyor-business-bot` loyihasining `telegram-business-bot` servisida ishlaydi. GitHub dagi `business-bot` papkasi root directory sifatida ko‘rsatilgan.

- Start command: `python bot.py`
- Environment variables: `BOT_TOKEN`, `ADMIN_CHAT_ID`, `BUSINESS_BOT_DB=/data/orders.sqlite3`
- Persistent volume: `/data` (buyurtmalar va Telegram offseti saqlanadi)
- Bitta Railway worker ishlatilsin. Shu token bilan mahalliy BAT/GUI botni bir vaqtning o‘zida yoqmang.
- Maxfiy tokenni GitHub ga yoki ommaviy loglarga joylamang.

## Windows 11 da ishga tushirish

1. Telegram ichida **@BotFather** orqali yangi bot yarating. Tokenni hech kimga yubormang va GitHub’ga joylamang.
2. Python 3.10+ o‘rnatilganini tekshiring: py --version
3. Ushbu papkani yuklab oling yoki GitHub’dan klonlang. PowerShell’da shu papkani oching.
4. Terminalda quyidagi buyruqlarni bajaring (qiymatlarni o‘zingiznikiga almashtiring):

    $env:BOT_TOKEN = "TOKEN_HERE"
    $env:ADMIN_CHAT_ID = "YOUR_NUMERIC_CHAT_ID"
    py bot.py

   Administrator chat ID raqamingizni bilmasangiz, avval ADMIN_CHAT_ID uchun vaqtincha 0 qiymatini yozing, botni ishga tushirib o‘zingiz unga /id yuboring. Raqamni olgach Ctrl+C bilan to‘xtating va ADMIN_CHAT_ID ni shu raqamga almashtirib qayta ishga tushiring.
5. Telegram botga /start yuboring, xizmat tanlang va faqat demo ma’lumotlar bilan sinab ko‘ring.
6. Administrator sifatida /orders, /stats, /done 1 buyruqlarini tekshiring.

To‘xtatish: Ctrl+C.

**Tokenni screenshotda ko‘rsatmang.** Token tarqalib ketsa, BotFather’dan uni yangilang. Repo ichiga token, haqiqiy foydalanuvchi ma’lumotlari yoki orders.sqlite3 faylini joylamang.

## Cheklovlar

- Bot long polling ishlatadi. Faqat lokal ishga tushirilganda kompyuter o‘chsa bot to‘xtaydi; Railway hostingida bunday cheklov yo‘q (tarif, resurs va hosting mavjudligiga bog‘liq).
- To‘lov, haqiqiy bron qilish, avtomatik server va reklama ommaviy xabarlari funksiyalari yo‘q.
- Real foydalanuvchilar bilan ishga tushirishdan oldin maxfiylik, ma’lumotlarni o‘chirish, zaxiralash va hosting xavfsizligini alohida ishlab chiqish kerak.
- Bot mijozlardan parol va boshqa maxfiy ma’lumotlarni so‘ramaydi.

## Offline test

    py -m unittest discover -s tests -v

Testlar Telegram tokenisiz ishlaydi.

Portfolio: [ELYOR.DEV](https://elyormakhmanazarov67-star.github.io/) · Aloqa: [@eywn88](https://t.me/eywn88)

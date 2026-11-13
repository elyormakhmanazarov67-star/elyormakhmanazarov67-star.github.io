#!/usr/bin/env python3
"""Business Bot demo: orders, SQLite, admin notifications, Telegram Bot API.

Requires Python 3.10+; no third-party dependencies.
Do not commit BOT_TOKEN, ADMIN_CHAT_ID, or a real customer database.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "orders.sqlite3"
SERVICES = {
    "🌐 Veb-sayt": "Veb-sayt",
    "🤖 Telegram-bot": "Telegram-bot",
    "📱 Mini App": "Mini App",
    "⚙️ Avtomatlashtirish": "Avtomatlashtirish",
}
SERVICE_DESCRIPTIONS = {
    "Veb-sayt": "1 sahifali moslashuvchan landing: xizmatlar, aloqa va buyurtma havolasi.",
    "Telegram-bot": "Tugmali menyu, oddiy buyurtma qabul qilish va administratorga bildirishnoma.",
    "Mini App": "Telegram ichidagi boshlang‘ich 2–3 ekranli MVP: katalog yoki forma.",
    "Avtomatlashtirish": "Bitta sodda jarayon: masalan, Telegram so‘rovini jadvalga yozish.",
}
STARTING_PRICES = {
    "Veb-sayt": 990_000,
    "Telegram-bot": 550_000,
    "Mini App": 1_590_000,
    "Avtomatlashtirish": 990_000,
}


def starting_price(service: str) -> str:
    return f"{STARTING_PRICES[service]:,}".replace(",", " ") + " so‘mdan"


PRICE_NOTE = (
    "Boshlang‘ich narx kichik MVP uchun; yakuniy narx ish hajmiga qarab tasdiqlanadi. "
    "Hosting, domen, pullik API va murakkab integratsiyalar alohida."
)
CONTACT_USERNAME = "eywn88"


def services_catalog() -> str:
    lines = ["📋 ELYOR.DEV xizmatlari:"]
    for title, service in SERVICES.items():
        lines.append(
            f"\n{title}\n{SERVICE_DESCRIPTIONS[service]}\n"
            f"Boshlang‘ich narx: {starting_price(service)}"
        )
    lines.append(
        "\n" + PRICE_NOTE + "\nBuyurtma berish uchun menyudan xizmatni tanlang."
        "\n💬 Aloqa: https://t.me/" + CONTACT_USERNAME
    )
    return "\n".join(lines)


WELCOME = (
    "Assalomu alaykum! 👋\n"
    "Bu biznes uchun buyurtma qabul qiluvchi demo-bot.\n"
    "Quyidagi xizmatlardan birini tanlang.\n\n"
    "Birinchi mijozlar uchun arzon boshlang‘ich narxlar!\n" 
    "Narxlarni ko‘rish: /services\n\n"
    "/services — xizmatlar\n"
    "/myorders — buyurtmalarim\n"
    "/contact — aloqa\n"
    "/cancel — jarayonni bekor qilish"
)


def create_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            details TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS settings (
            name TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )"""
    )
    con.commit()
    return con


def add_order(con: sqlite3.Connection, chat_id: int, service: str, details: str) -> int:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = con.execute(
        "INSERT INTO orders(chat_id,service,details,status,created_at) VALUES(?,?,?,?,?)",
        (chat_id, service, details, "new", now),
    )
    con.commit()
    return int(cur.lastrowid)


def latest_orders(con: sqlite3.Connection, limit: int = 10) -> list[sqlite3.Row]:
    return con.execute(
        "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()


def pending_orders(con: sqlite3.Connection, limit: int = 10) -> list[sqlite3.Row]:
    return con.execute(
        "SELECT * FROM orders WHERE status='new' ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()


def get_order(con: sqlite3.Connection, order_id: int) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()


def customer_orders(con: sqlite3.Connection, chat_id: int, limit: int = 5) -> list[sqlite3.Row]:
    # Never return another customer's orders, even to a normal Telegram user.
    return con.execute(
        "SELECT id, service, status, created_at FROM orders "
        "WHERE chat_id=? ORDER BY id DESC LIMIT ?",
        (chat_id, limit),
    ).fetchall()


def format_customer_orders(rows: list[sqlite3.Row]) -> str:
    if not rows:
        return "📦 Sizda hali buyurtmalar yo‘q. Xizmat tanlab, so‘rov qoldirishingiz mumkin."
    lines = ["📦 Oxirgi buyurtmalaringiz:"]
    for row in rows:
        status = "🆕 Yangi" if row["status"] == "new" else "✅ Bajarilgan"
        lines.append(f"#{row['id']} · {row['service']} — {status}")
    return "\n".join(lines)


def format_order(row: sqlite3.Row, *, full: bool = False) -> str:
    status = "🆕 Yangi" if row["status"] == "new" else "✅ Bajarilgan"
    details = row["details"] if full else row["details"][:160]
    return (
        f"#{row['id']} | {row['service']} | {status}\n"
        f"Chat ID: {row['chat_id']}\n"
        f"Yaratilgan: {row['created_at']}\n"
        f"So‘rov: {details}"
    )


def finish_order(con: sqlite3.Connection, order_id: int) -> sqlite3.Row | None:
    row = con.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return None
    if row["status"] != "done":
        con.execute("UPDATE orders SET status='done' WHERE id=?", (order_id,))
        con.commit()
    return row


def stats(con: sqlite3.Connection) -> tuple[int, int, int]:
    total = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    new = con.execute("SELECT COUNT(*) FROM orders WHERE status='new'").fetchone()[0]
    return int(total), int(new), int(total - new)


def get_offset(con: sqlite3.Connection) -> int:
    row = con.execute(
        "SELECT value FROM settings WHERE name='telegram_update_offset'"
    ).fetchone()
    return int(row[0]) if row is not None else 0


def set_offset(con: sqlite3.Connection, offset: int) -> None:
    con.execute(
        "INSERT INTO settings(name,value) VALUES('telegram_update_offset',?) "
        "ON CONFLICT(name) DO UPDATE SET value=excluded.value",
        (str(offset),),
    )
    con.commit()


class TelegramApi:
    def __init__(self, token: str):
        self._api = "https://api.telegram.org/bot" + token + "/"

    def call(self, method: str, params: dict | None = None) -> dict:
        payload = urlencode({
            key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
            for key, value in (params or {}).items()
        }).encode("utf-8")
        request = Request(
            self._api + method,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=35) as response:
                data = json.load(response)
        except (HTTPError, URLError, TimeoutError) as exc:
            # Avoid printing exception details: URL may contain the bot token.
            raise RuntimeError("Telegram API transport error: " + type(exc).__name__) from None
        if not isinstance(data, dict) or not data.get("ok"):
            raise RuntimeError("Telegram API returned a non-success status")
        return data["result"]

    def message(self, chat_id: int, text: str, *, keyboard: dict | None = None):
        params = {"chat_id": chat_id, "text": text[:4000]}
        if keyboard is not None:
            params["reply_markup"] = keyboard
        return self.call("sendMessage", params)


def menu() -> dict:
    return {
        "keyboard": [
            [{"text": "🌐 Veb-sayt"}, {"text": "🤖 Telegram-bot"}],
            [{"text": "📱 Mini App"}, {"text": "⚙️ Avtomatlashtirish"}],
            [{"text": "📋 Xizmatlar va narxlar"}],
            [{"text": "📦 Buyurtmalarim"}, {"text": "💬 Aloqa"}],
            [{"text": "🏠 Menyu"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def hide_menu() -> dict:
    return {"remove_keyboard": True}


def handle_message(
    message: dict,
    api: TelegramApi,
    con: sqlite3.Connection,
    admin_chat_id: int,
    sessions: dict[int, dict],
) -> None:
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")
    if not isinstance(chat_id, int) or not isinstance(text, str):
        return
    text = text.strip()
    if not text:
        return

    # Admin-only commands. A stranger cannot read or change orders.
    command = text.split(maxsplit=1)[0].split("@", 1)[0].lower()
    if command in {"/orders", "/pending", "/order", "/stats", "/done"}:
        if chat_id != admin_chat_id:
            api.message(chat_id, "Bu buyruq faqat administrator uchun.")
            return
        if command in {"/orders", "/pending"}:
            rows = pending_orders(con) if command == "/pending" else latest_orders(con)
            if not rows:
                msg = "Yangi buyurtmalar yo‘q." if command == "/pending" else "Hozircha buyurtmalar yo‘q."
                api.message(chat_id, msg)
                return
            heading = "🆕 Yangi buyurtmalar:" if command == "/pending" else "📋 Oxirgi buyurtmalar:"
            lines = [heading] + [format_order(row) for row in rows]
            api.message(chat_id, "\n\n".join(lines))
            return
        if command == "/stats":
            total, new, done = stats(con)
            api.message(
                chat_id,
                f"📊 Jami: {total}\n🆕 Yangi: {new}\n✅ Bajarilgan: {done}"
                "\n\n/orders — oxirgi 10 ta\n/pending — faqat yangi buyurtmalar"
            )
            return
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            example = "/order 123" if command == "/order" else "/done 123"
            api.message(chat_id, f"Foydalanish: {example}")
            return
        order_id = int(parts[1])
        if command == "/order":
            row = get_order(con, order_id)
            api.message(chat_id, format_order(row, full=True) if row else "Bu raqamli buyurtma topilmadi.")
            return
        row = finish_order(con, order_id)
        if row is None:
            api.message(chat_id, "Bu raqamli buyurtma topilmadi.")
            return
        api.message(chat_id, f"✅ #{row['id']} bajarildi deb belgilandi.")
        if row["status"] != "done":
            try:
                api.message(int(row["chat_id"]), f"✅ #{row['id']} buyurtmangiz bajarildi!")
            except RuntimeError:
                pass
        return

    if command == "/id":
        api.message(chat_id, f"Telegram chat ID: {chat_id}")
        return

    if command == "/services" or text == "📋 Xizmatlar va narxlar":
        sessions.pop(chat_id, None)
        api.message(chat_id, services_catalog(), keyboard=menu())
        return

    if command == "/myorders" or text == "📦 Buyurtmalarim":
        sessions.pop(chat_id, None)
        api.message(chat_id, format_customer_orders(customer_orders(con, chat_id)), keyboard=menu())
        return

    if command == "/contact" or text == "💬 Aloqa":
        sessions.pop(chat_id, None)
        api.message(
            chat_id,
            "💬 ELYOR.DEV bilan bog‘lanish:\n"
            f"https://t.me/{CONTACT_USERNAME}\n\n"
            "Buyurtmani bot orqali ham yuborishingiz mumkin.",
            keyboard=menu(),
        )
        return

    if text == "🏠 Menyu" or command == "/menu":
        sessions.pop(chat_id, None)
        api.message(chat_id, WELCOME, keyboard=menu())
        return

    if command == "/cancel":
        sessions.pop(chat_id, None)
        api.message(chat_id, "Bekor qilindi. Qaytadan xizmat tanlashingiz mumkin.", keyboard=menu())
        return

    if command in {"/start", "/help"}:
        sessions.pop(chat_id, None)
        greeting = WELCOME
        if chat_id == admin_chat_id:
            greeting += (
                "\n\n👨‍💼 Admin: /orders, /pending, /order 1, /stats, /done 1"
            )
        api.message(chat_id, greeting, keyboard=menu())
        return

    if text in SERVICES:
        sessions[chat_id] = {"service": SERVICES[text]}
        api.message(
            chat_id,
            f"Tanlandi: {SERVICES[text]}\n"
            f"{SERVICE_DESCRIPTIONS[SERVICES[text]]}\n"
            f"Boshlang‘ich narx: {starting_price(SERVICES[text])}\n"
            f"{PRICE_NOTE}\n\n"
            "Nima kerakligini qisqacha tushuntiring (8–700 ta belgi). "
            "Telefon yoki boshqa maxfiy ma’lumotlarni yuborish shart emas.",
            keyboard=hide_menu(),
        )
        return

    state = sessions.get(chat_id)
    if state:
        if not 8 <= len(text) <= 700:
            api.message(chat_id, "Iltimos, 8–700 belgidan iborat izoh yozing.")
            return
        number = add_order(con, chat_id, state["service"], text)
        sessions.pop(chat_id, None)
        api.message(
            chat_id,
            f"✅ So‘rov qabul qilindi! Raqami: #{number}.\n"
            "Yana buyurtma berish uchun xizmat tanlang.",
            keyboard=menu(),
        )
        admin_text = (
            f"🆕 Yangi buyurtma #{number}\n"
            f"Xizmat: {state['service']}\n"
            f"Chat ID: {chat_id}\n"
            f"So‘rov: {text}\n\n"
            f"/done {number} — bajarildi deb belgilash"
        )
        try:
            api.message(admin_chat_id, admin_text)
        except RuntimeError:
            # Order remains safely in SQLite; admin can use /orders.
            pass
        return

    api.message(chat_id, "Buyurtmani boshlash uchun /start yuboring.", keyboard=menu())


def main() -> int:
    token = os.getenv("BOT_TOKEN", "").strip()
    admin_raw = os.getenv("ADMIN_CHAT_ID", "").strip()
    if not token or not admin_raw.lstrip("-").isdigit():
        print("BOT_TOKEN va ADMIN_CHAT_ID muhit o‘zgaruvchilarini sozlang.", file=sys.stderr)
        return 2
    admin_id = int(admin_raw)
    db_path = Path(os.getenv("BUSINESS_BOT_DB", str(DEFAULT_DB_PATH)))
    con = create_connection(db_path)
    api = TelegramApi(token)
    try:
        bot = api.call("getMe")
    except RuntimeError as exc:
        print("Botga ulanib bo‘lmadi: " + str(exc), file=sys.stderr)
        return 1
    print("Ishga tushdi: @" + str(bot.get("username", "bot")) + " (Ctrl+C to stop)")
    sessions: dict[int, dict] = {}
    offset = get_offset(con)
    try:
        while True:
            try:
                updates = api.call("getUpdates", {
                    "offset": offset,
                    "timeout": 20,
                    "limit": 50,
                    "allowed_updates": ["message"],
                })
                for update in updates:
                    update_id = int(update["update_id"])
                    if update_id < offset:
                        continue
                    try:
                        if "message" in update:
                            handle_message(update["message"], api, con, admin_id, sessions)
                    except RuntimeError:
                        # Don't advance offset on transient delivery errors.
                        raise
                    offset = update_id + 1
                    set_offset(con, offset)
            except RuntimeError as exc:
                print("Ulanish uzildi: " + str(exc) + "; qayta uriniladi.", file=sys.stderr)
                time.sleep(3)
    except KeyboardInterrupt:
        print("\nBot to‘xtatildi.")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())

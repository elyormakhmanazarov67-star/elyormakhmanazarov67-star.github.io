"""Offline unit tests for the SQLite order workflow."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import (
    create_connection, add_order, latest_orders, pending_orders, get_order,
    format_order, finish_order, stats, get_offset, set_offset,
    customer_orders, format_customer_orders, services_catalog, menu, handle_message
)


class FakeTelegramApi:
    def __init__(self):
        self.messages = []

    def message(self, chat_id, text, *, keyboard=None):
        self.messages.append((chat_id, text, keyboard))



class TestOrders(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.con = create_connection(Path(self.tmp.name) / "test.sqlite3")

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_create_and_complete(self):
        first = add_order(self.con, 111, "Telegram-bot", "Simple booking demo")
        second = add_order(self.con, 222, "Mini App", "Catalog demo")
        self.assertEqual((first, second), (1, 2))
        self.assertEqual(stats(self.con), (2, 2, 0))
        self.assertEqual(latest_orders(self.con)[0]["service"], "Mini App")
        self.assertEqual(finish_order(self.con, first)["chat_id"], 111)
        self.assertEqual(stats(self.con), (2, 1, 1))
        self.assertIsNone(finish_order(self.con, 99))

    def test_pending_and_full_order_detail(self):
        one = add_order(self.con, 111, "Veb-sayt", "First sample order")
        two = add_order(self.con, 222, "Telegram-bot", "Second sample order")
        self.assertEqual([row["id"] for row in pending_orders(self.con)], [two, one])
        self.assertEqual(get_order(self.con, one)["details"], "First sample order")
        self.assertIn("First sample order", format_order(get_order(self.con, one), full=True))
        self.assertIsNone(get_order(self.con, 999))
        finish_order(self.con, one)
        self.assertEqual([row["id"] for row in pending_orders(self.con)], [two])

    def test_customer_privacy_and_menu(self):
        first = add_order(self.con, 111, "Veb-sayt", "Customer 111 project")
        add_order(self.con, 222, "Mini App", "Customer 222 project")
        rows = customer_orders(self.con, 111)
        self.assertEqual([row["id"] for row in rows], [first])
        self.assertNotIn("Customer 222", format_customer_orders(rows))
        self.assertEqual(customer_orders(self.con, 333), [])
        self.assertIn("📦", format_customer_orders([]))
        self.assertIn("📦 Buyurtmalarim", str(menu()))
        self.assertIn("Narx:", services_catalog())
        self.assertIn("https://t.me/eywn88", services_catalog())

    def test_public_commands_and_admin_isolation(self):
        add_order(self.con, 111, "Veb-sayt", "Personal order")
        add_order(self.con, 222, "Telegram-bot", "Another person's order")
        api = FakeTelegramApi()
        sessions = {}
        admin_id = 999
        def send(chat_id, text):
            handle_message(
                {"chat": {"id": chat_id}, "text": text},
                api, self.con, admin_id, sessions,
            )
            return api.messages[-1][1]
        self.assertIn("Veb-sayt", send(111, "/services"))
        self.assertIn("https://t.me/eywn88", send(111, "💬 Aloqa"))
        own = send(111, "/myorders")
        self.assertIn("#1", own)
        self.assertNotIn("#2", own)
        self.assertIn("faqat administrator", send(111, "/orders"))
        self.assertIn("Assalomu alaykum", send(111, "🏠 Menyu"))
        self.assertIn("Telegram-bot", send(111, "🤖 Telegram-bot"))
        self.assertEqual(sessions[111]["service"], "Telegram-bot")
        self.assertIn("Telegram", send(111, "/contact"))
        self.assertNotIn(111, sessions)

    def test_offset(self):
        self.assertEqual(get_offset(self.con), 0)
        set_offset(self.con, 42)
        self.assertEqual(get_offset(self.con), 42)
        set_offset(self.con, 43)
        self.assertEqual(get_offset(self.con), 43)

    def test_database_persists(self):
        db = Path(self.tmp.name) / "test.sqlite3"
        add_order(self.con, 123, "Veb-sayt", "Sample request")
        self.con.close()
        self.con = create_connection(db)
        self.assertEqual(len(latest_orders(self.con)), 1)


if __name__ == "__main__":
    unittest.main()

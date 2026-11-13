"""Offline unit tests for the SQLite order workflow."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import create_connection, add_order, latest_orders, finish_order, stats, get_offset, set_offset


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

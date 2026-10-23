import sqlite3
import unittest
from migration import migrate


class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        self.conn.execute("INSERT INTO users VALUES (1, 'demo')")
        self.conn.commit()

    def test_existing_rows_and_nullable_text_column(self):
        migrate(self.conn)
        self.assertEqual(
            self.conn.execute("SELECT id,name,timezone FROM users").fetchall(),
            [(1, "demo", None)],
        )
        column = next(row for row in self.conn.execute("PRAGMA table_info(users)") if row[1] == "timezone")
        self.assertEqual(column[2], "TEXT")
        self.assertEqual(column[3], 0)
        self.conn.execute("INSERT INTO users (id,name) VALUES (2, 'new')")
        self.assertIsNone(self.conn.execute("SELECT timezone FROM users WHERE id=2").fetchone()[0])

    def test_repeat_preserves_stored_timezone_and_rows(self):
        migrate(self.conn)
        self.conn.execute("UPDATE users SET timezone='America/Sao_Paulo' WHERE id=1")
        migrate(self.conn)
        migrate(self.conn)
        self.assertEqual(
            self.conn.execute("SELECT id,name,timezone FROM users").fetchall(),
            [(1, "demo", "America/Sao_Paulo")],
        )
        columns = [row[1] for row in self.conn.execute("PRAGMA table_info(users)")]
        self.assertEqual(columns.count("timezone"), 1)

    def test_does_not_commit_callers_transaction(self):
        self.conn.execute("INSERT INTO users VALUES (2, 'pending')")
        migrate(self.conn)
        self.conn.rollback()
        self.assertEqual(self.conn.execute("SELECT id,name FROM users").fetchall(), [(1, "demo")])
        self.assertNotIn("timezone", [row[1] for row in self.conn.execute("PRAGMA table_info(users)")])

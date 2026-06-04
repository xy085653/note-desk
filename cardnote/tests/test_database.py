import sqlite3
import pytest
from cardnote.db.database import Database, SCHEMA_SQL, migrate_if_needed


class TestDatabase:
    def test_connect_creates_tables(self, db_path):
        db = Database(db_path)
        conn = db.connect()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [r["name"] for r in tables]
        assert "cards" in table_names
        assert "settings" in table_names
        assert "todos" in table_names
        db.close()

    def test_connect_idempotent(self, db_path):
        """多次调用 connect 不会重复创建表."""
        db = Database(db_path)
        db.connect()
        db.conn.execute("INSERT INTO settings (key, value) VALUES ('k', 'v')")
        db.conn.commit()
        db.close()
        # 第二次打开
        db2 = Database(db_path)
        conn2 = db2.connect()
        row = conn2.execute("SELECT value FROM settings WHERE key='k'").fetchone()
        assert row["value"] == "v"
        db2.close()

    def test_custom_path(self, db_path):
        db = Database(db_path)
        assert db.db_path == db_path

    def test_schema_sql_contains_all_tables(self):
        assert "CREATE TABLE IF NOT EXISTS cards" in SCHEMA_SQL
        assert "CREATE TABLE IF NOT EXISTS settings" in SCHEMA_SQL
        assert "CREATE TABLE IF NOT EXISTS todos" in SCHEMA_SQL

    def test_migrate_adds_is_completed(self, db_path):
        """模拟旧数据库迁移场景."""
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE cards (
            id TEXT PRIMARY KEY, content TEXT DEFAULT '',
            color_scheme INTEGER DEFAULT 0,
            pos_x REAL, pos_y REAL,
            width REAL DEFAULT 260, height REAL DEFAULT 260,
            z_index INTEGER DEFAULT 0,
            is_visible INTEGER DEFAULT 1,
            is_deleted INTEGER DEFAULT 0,
            created_at TEXT, updated_at TEXT
        )""")
        conn.commit()
        conn.close()
        conn2 = sqlite3.connect(db_path)
        conn2.row_factory = sqlite3.Row
        migrate_if_needed(conn2)
        cols = {r["name"] for r in conn2.execute("PRAGMA table_info(cards)").fetchall()}
        assert "is_completed" in cols
        conn2.close()
        # 幂等
        conn3 = sqlite3.connect(db_path)
        conn3.row_factory = sqlite3.Row
        migrate_if_needed(conn3)
        conn3.close()

import pytest
from cardnote.db.database import Database
from cardnote.db.database import SCHEMA_SQL


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

    def test_schema_sql_contains_both_tables(self):
        assert "CREATE TABLE IF NOT EXISTS cards" in SCHEMA_SQL
        assert "CREATE TABLE IF NOT EXISTS settings" in SCHEMA_SQL

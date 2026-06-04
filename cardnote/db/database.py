import sqlite3
import os


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cards (
    id          TEXT PRIMARY KEY,
    content     TEXT NOT NULL DEFAULT '',
    color_scheme INTEGER DEFAULT 0,
    pos_x       REAL,
    pos_y       REAL,
    width       REAL DEFAULT 260,
    height      REAL DEFAULT 260,
    z_index     INTEGER DEFAULT 0,
    is_visible  INTEGER DEFAULT 1,
    is_deleted  INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Database:
    """SQLite 数据库连接与初始化."""

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            from PySide6.QtCore import QStandardPaths
            data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "cardnote.db")
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """建立连接并初始化表结构."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        return self.conn

    def close(self):
        """关闭连接."""
        if self.conn:
            self.conn.close()
            self.conn = None

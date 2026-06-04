DEFAULTS = {
    "theme": "light",
    "auto_theme": "false",
    "launch_at_startup": "false",
    "default_card_width": "260",
    "default_card_height": "260",
}


class Settings:
    """全局设置管理，读写 settings 表."""

    def __init__(self, conn):
        self.conn = conn
        self._ensure_defaults()

    def _ensure_defaults(self):
        for key, value in DEFAULTS.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        self.conn.commit()

    def get(self, key: str, default: str | None = None) -> str:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return default if default is not None else DEFAULTS.get(key, "")
        return row["value"]

    def set(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    def get_bool(self, key: str) -> bool:
        return self.get(key).lower() in ("true", "1", "yes")

    def get_int(self, key: str, default: int = 260) -> int:
        try:
            return int(self.get(key))
        except (ValueError, TypeError):
            return default

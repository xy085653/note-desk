from cardnote.utils.helpers import new_uuid, now_iso
from cardnote.ui.color_schemes import random_scheme_index


class CardRepository:
    """卡片数据的 CRUD 操作."""

    def __init__(self, conn):
        self.conn = conn

    def create(self, pos_x: float = 400, pos_y: float = 300,
               width: float = 260, height: float = 260) -> dict:
        now = now_iso()
        card = {
            "id": new_uuid(),
            "content": "",
            "color_scheme": random_scheme_index(),
            "pos_x": pos_x,
            "pos_y": pos_y,
            "width": width,
            "height": height,
            "z_index": 0,
            "is_visible": 1,
            "is_deleted": 0,
            "created_at": now,
            "updated_at": now,
        }
        self.conn.execute(
            """INSERT INTO cards (id, content, color_scheme, pos_x, pos_y,
             width, height, z_index, is_visible, is_deleted, created_at, updated_at)
             VALUES (:id, :content, :color_scheme, :pos_x, :pos_y,
             :width, :height, :z_index, :is_visible, :is_deleted, :created_at, :updated_at)""",
            card,
        )
        self.conn.commit()
        return card

    def get(self, card_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM cards WHERE id = ? AND is_deleted = 0", (card_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_active(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM cards WHERE is_deleted = 0 ORDER BY z_index DESC, updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def update_content(self, card_id: str, content: str):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, card_id),
        )
        self.conn.commit()

    def update_position(self, card_id: str, pos_x: float, pos_y: float):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET pos_x = ?, pos_y = ?, updated_at = ? WHERE id = ?",
            (pos_x, pos_y, now, card_id),
        )
        self.conn.commit()

    def update_size(self, card_id: str, width: float, height: float):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET width = ?, height = ?, updated_at = ? WHERE id = ?",
            (width, height, now, card_id),
        )
        self.conn.commit()

    def update_color_scheme(self, card_id: str, scheme_index: int):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET color_scheme = ?, updated_at = ? WHERE id = ?",
            (scheme_index, now, card_id),
        )
        self.conn.commit()

    def soft_delete(self, card_id: str):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET is_deleted = 1, updated_at = ? WHERE id = ?",
            (now, card_id),
        )
        self.conn.commit()

    def count_active(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM cards WHERE is_deleted = 0"
        ).fetchone()
        return row["cnt"]

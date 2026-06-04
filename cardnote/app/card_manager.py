from PySide6.QtCore import QObject, Signal, QTimer

from cardnote.db.repository import CardRepository
from cardnote.ui.floating_card import FloatingCard


class CardManager(QObject):
    """卡片管理器: 维护卡片生命周期、与数据库同步."""

    card_created = Signal(str)   # card_id
    card_deleted = Signal(str)   # card_id
    card_count_changed = Signal(int)

    def __init__(self, repository: CardRepository, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.cards: dict[str, FloatingCard] = {}
        self._save_timers: dict[str, QTimer] = {}
        self._debounce_ms = 3000

    def load_all(self):
        """从数据库加载所有活跃卡片并创建窗口."""
        records = self.repository.get_all_active()
        for record in records:
            self._create_card_from_data(record)

    def create_card(self, pos_x: float = 400, pos_y: float = 300,
                    width: float = 260, height: float = 260) -> FloatingCard:
        """创建新卡片."""
        data = self.repository.create(pos_x, pos_y, width, height)
        card = self._create_card_from_data(data)
        self.card_created.emit(data["id"])
        self.card_count_changed.emit(len(self.cards))
        return card

    def _create_card_from_data(self, data: dict) -> FloatingCard:
        """根据数据库记录创建卡片窗口."""
        card = FloatingCard(data["id"], data)
        card.set_save_callback(lambda: self._save_card(card.card_id))
        card.set_delete_callback(lambda: self.delete_card(card.card_id))
        card.destroyed.connect(lambda: self._on_card_closed(card.card_id))
        card.delete_requested.connect(self._on_delete_requested)
        card.card_widget.content_changed.connect(
            lambda text: self._debounce_save(card.card_id, text)
        )
        card.show()
        self.cards[data["id"]] = card
        return card

    def _save_card(self, card_id: str):
        """保存卡片当前状态到数据库."""
        card = self.cards.get(card_id)
        if card is None:
            return
        data = card.card_data
        self.repository.update_content(card_id, data.get("content", ""))
        self.repository.update_position(card_id, data["pos_x"], data["pos_y"])
        self.repository.update_size(card_id, data["width"], data["height"])
        self.repository.update_color_scheme(card_id, data.get("color_scheme", 0))

    def _on_delete_requested(self, card_id: str):
        """处理卡片删除请求: 播放动画后自动触发 delete_card."""
        card = self.cards.get(card_id)
        if card:
            card._animate_delete()
        else:
            self.delete_card(card_id)

    def _debounce_save(self, card_id: str, text: str):
        """防抖保存: 内容变化后 3s 自动保存."""
        if card_id in self._save_timers:
            self._save_timers[card_id].stop()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._save_card(card_id))
        timer.start(self._debounce_ms)
        self._save_timers[card_id] = timer
        # 同步更新内存中的数据
        if card_id in self.cards:
            self.cards[card_id].card_data["content"] = text

    def delete_card(self, card_id: str):
        """删除卡片."""
        if card_id in self.cards:
            self.cards[card_id].close()
        self.cards.pop(card_id, None)
        if card_id in self._save_timers:
            self._save_timers[card_id].stop()
            del self._save_timers[card_id]
        self.repository.soft_delete(card_id)
        self.card_deleted.emit(card_id)
        self.card_count_changed.emit(len(self.cards))

    def _on_card_closed(self, card_id: str):
        """卡片窗口关闭后的清理."""
        self.cards.pop(card_id, None)
        if card_id in self._save_timers:
            self._save_timers[card_id].stop()
            del self._save_timers[card_id]

    def hide_all(self):
        """隐藏所有卡片窗口."""
        for card in self.cards.values():
            card.hide()

    def show_all(self):
        """显示所有卡片窗口."""
        for card in self.cards.values():
            card.show()

    def toggle_visible(self):
        """切换所有卡片的可见性."""
        if any(card.isVisible() for card in self.cards.values()):
            self.hide_all()
        else:
            self.show_all()

    def save_all(self):
        """立即保存所有卡片."""
        for card_id in list(self.cards.keys()):
            self._save_card(card_id)

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from cardnote.db.database import Database
from cardnote.db.repository import CardRepository
from cardnote.app.card_manager import CardManager


def _close_card(card):
    """Safely close a FloatingCard without triggering deleteLater crash."""
    card.blockSignals(True)
    card.setAttribute(Qt.WA_DeleteOnClose, False)
    card.close()


@pytest.fixture(scope="session")
def qapp_session():
    """Session-scoped QApplication for all CardManager tests."""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def card_manager(db_path, qapp_session):
    db = Database(db_path)
    conn = db.connect()
    repo = CardRepository(conn)
    mgr = CardManager(repo)
    yield mgr
    # Safe cleanup
    for card_id in list(mgr.cards.keys()):
        _close_card(mgr.cards[card_id])
    mgr.cards.clear()
    qapp_session.processEvents()


class TestCardManager:
    def test_create_card(self, card_manager):
        card = card_manager.create_card(100, 200, 260, 260)
        assert card.card_id in card_manager.cards
        assert card_manager.repository.count_active() == 1

    def test_load_all(self, card_manager):
        card_manager.create_card()
        card_manager.create_card()
        # 模拟重启: 新建一个 manager 并 load_all
        repo = card_manager.repository
        mgr2 = CardManager(repo)
        mgr2.load_all()
        assert len(mgr2.cards) == 2
        # 清理 mgr2
        for cid in list(mgr2.cards.keys()):
            _close_card(mgr2.cards[cid])
        mgr2.cards.clear()

    def test_delete_card(self, card_manager):
        card = card_manager.create_card()
        card_id = card.card_id
        assert card_id in card_manager.cards
        card_manager.delete_card(card_id)
        assert card_id not in card_manager.cards
        assert card_manager.repository.count_active() == 0

    def test_toggle_visible(self, card_manager):
        card_manager.create_card()
        card_manager.hide_all()
        assert all(not c.isVisible() for c in card_manager.cards.values())
        card_manager.show_all()
        assert all(c.isVisible() for c in card_manager.cards.values())

    def test_save_all(self, card_manager):
        card = card_manager.create_card()
        card.card_widget.set_content("test content")
        card.card_data["content"] = "test content"
        card_manager.save_all()
        saved = card_manager.repository.get(card.card_id)
        assert saved["content"] == "test content"

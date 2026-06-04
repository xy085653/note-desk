import pytest
from cardnote.db.database import Database
from cardnote.db.repository import CardRepository


@pytest.fixture
def repo(db_path):
    db = Database(db_path)
    conn = db.connect()
    return CardRepository(conn)


class TestCardRepository:
    def test_create_card(self, repo):
        card = repo.create(pos_x=100, pos_y=200)
        assert card["id"] is not None
        assert card["content"] == ""
        assert card["pos_x"] == 100
        assert card["pos_y"] == 200
        assert card["is_deleted"] == 0

    def test_get_card(self, repo):
        created = repo.create()
        fetched = repo.get(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]

    def test_get_nonexistent(self, repo):
        assert repo.get("nonexistent-id") is None

    def test_get_all_active(self, repo):
        repo.create()
        repo.create()
        all_cards = repo.get_all_active()
        assert len(all_cards) >= 2

    def test_soft_delete(self, repo):
        card = repo.create()
        repo.soft_delete(card["id"])
        assert repo.get(card["id"]) is None
        assert repo.count_active() == 0

    def test_update_content(self, repo):
        card = repo.create()
        repo.update_content(card["id"], "hello world")
        updated = repo.get(card["id"])
        assert updated["content"] == "hello world"

    def test_update_position(self, repo):
        card = repo.create()
        repo.update_position(card["id"], 500, 600)
        updated = repo.get(card["id"])
        assert updated["pos_x"] == 500
        assert updated["pos_y"] == 600

    def test_update_size(self, repo):
        card = repo.create()
        repo.update_size(card["id"], 300, 200)
        updated = repo.get(card["id"])
        assert updated["width"] == 300
        assert updated["height"] == 200

    def test_update_color_scheme(self, repo):
        card = repo.create()
        repo.update_color_scheme(card["id"], 5)
        updated = repo.get(card["id"])
        assert updated["color_scheme"] == 5

    def test_count_active(self, repo):
        assert repo.count_active() == 0
        repo.create()
        assert repo.count_active() == 1

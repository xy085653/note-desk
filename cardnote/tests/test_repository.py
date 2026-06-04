import pytest
from cardnote.db.database import Database
from cardnote.db.repository import CardRepository, TodoRepository


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


class TestCardRepositoryExtended:
    def test_set_card_completed(self, repo):
        card = repo.create()
        assert card["is_completed"] == 0
        repo.set_card_completed(card["id"], True)
        updated = repo.get(card["id"])
        assert updated["is_completed"] == 1
        repo.set_card_completed(card["id"], False)
        updated = repo.get(card["id"])
        assert updated["is_completed"] == 0


@pytest.fixture
def todo_repo(db_path):
    from cardnote.db.database import Database
    db = Database(db_path)
    conn = db.connect()
    return TodoRepository(conn)


class TestTodoRepository:
    def test_add_and_get(self, todo_repo):
        from cardnote.db.database import Database
        from cardnote.db.repository import CardRepository
        # 需要先有卡片才能添加 todo
        db = Database(todo_repo.conn)
        cr = CardRepository(todo_repo.conn)
        card = cr.create()
        todo = todo_repo.add_todo(card["id"], "买牛奶")
        assert todo["card_id"] == card["id"]
        assert todo["text"] == "买牛奶"
        assert todo["done"] == 0
        todos = todo_repo.get_todos(card["id"])
        assert len(todos) == 1
        assert todos[0]["text"] == "买牛奶"

    def test_toggle(self, todo_repo):
        from cardnote.db.repository import CardRepository
        cr = CardRepository(todo_repo.conn)
        card = cr.create()
        todo = todo_repo.add_todo(card["id"], "测试项")
        assert todo_repo.get_todos(card["id"])[0]["done"] == 0
        todo_repo.toggle_todo(todo["id"])
        assert todo_repo.get_todos(card["id"])[0]["done"] == 1
        todo_repo.toggle_todo(todo["id"])
        assert todo_repo.get_todos(card["id"])[0]["done"] == 0

    def test_delete(self, todo_repo):
        from cardnote.db.repository import CardRepository
        cr = CardRepository(todo_repo.conn)
        card = cr.create()
        todo = todo_repo.add_todo(card["id"], "待删除")
        assert len(todo_repo.get_todos(card["id"])) == 1
        todo_repo.delete_todo(todo["id"])
        assert len(todo_repo.get_todos(card["id"])) == 0

    def test_update_todo(self, todo_repo):
        from cardnote.db.repository import CardRepository
        cr = CardRepository(todo_repo.conn)
        card = cr.create()
        todo = todo_repo.add_todo(card["id"], "旧文字")
        todo_repo.update_todo(todo["id"], "新文字")
        assert todo_repo.get_todos(card["id"])[0]["text"] == "新文字"

    def test_delete_card_todos(self, todo_repo):
        from cardnote.db.repository import CardRepository
        cr = CardRepository(todo_repo.conn)
        card = cr.create()
        todo_repo.add_todo(card["id"], "项1")
        todo_repo.add_todo(card["id"], "项2")
        assert len(todo_repo.get_todos(card["id"])) == 2
        todo_repo.delete_card_todos(card["id"])
        assert len(todo_repo.get_todos(card["id"])) == 0

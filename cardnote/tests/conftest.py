import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """提供 QApplication 实例给 pytest-qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def db_path(tmp_path):
    """返回临时数据库路径."""
    return str(tmp_path / "test_cardnote.db")

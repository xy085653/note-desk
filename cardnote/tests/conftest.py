import pytest


@pytest.fixture
def db_path(tmp_path):
    """返回临时数据库路径."""
    return str(tmp_path / "test_cardnote.db")

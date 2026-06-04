import pytest
from cardnote.db.database import Database
from cardnote.app.settings import Settings, DEFAULTS


@pytest.fixture
def settings(db_path):
    db = Database(db_path)
    conn = db.connect()
    return Settings(conn)


class TestSettings:
    def test_defaults_exist(self, settings):
        for key, default_val in DEFAULTS.items():
            assert settings.get(key) == default_val

    def test_set_and_get(self, settings):
        settings.set("theme", "dark")
        assert settings.get("theme") == "dark"

    def test_get_bool_false(self, settings):
        assert settings.get_bool("auto_theme") is False

    def test_get_bool_true(self, settings):
        settings.set("auto_theme", "true")
        assert settings.get_bool("auto_theme") is True

    def test_get_int_default(self, settings):
        assert settings.get_int("default_card_width") == 260

    def test_get_int_custom(self, settings):
        settings.set("default_card_width", "300")
        assert settings.get_int("default_card_width") == 300

    def test_unknown_key_returns_default(self, settings):
        assert settings.get("nonexistent", "fallback") == "fallback"

import os
import random
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from cardnote.db.database import Database
from cardnote.db.repository import CardRepository
from cardnote.app.settings import Settings
from cardnote.app.card_manager import CardManager
from cardnote.app.tray import CardTray


class CardNoteApp:
    """CardNote 主应用: 组装所有模块."""

    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.qapp.setApplicationName("CardNote")
        self.qapp.setOrganizationName("CardNote")
        self.qapp.setQuitOnLastWindowClosed(False)

        # 数据层
        self.database = Database()
        self.conn = self.database.connect()
        self.repository = CardRepository(self.conn)
        self.settings = Settings(self.conn)

        # 业务层
        self.card_manager = CardManager(self.repository)

        # UI
        self.tray = CardTray()
        self._connect_signals()

        # 加载已有卡片
        self.card_manager.load_all()
        self.tray.set_tooltip(len(self.card_manager.cards))

        # 设置主题
        self._is_dark = self.settings.get("theme") == "dark"
        self._apply_theme()

        # 全局快捷键
        self._setup_shortcuts()

    def _connect_signals(self):
        self.tray.new_card_requested.connect(self._on_new_card)
        self.tray.show_all_requested.connect(self.card_manager.show_all)
        self.tray.hide_all_requested.connect(self.card_manager.hide_all)
        self.tray.toggle_theme_requested.connect(self._toggle_theme)
        self.tray.tray_clicked.connect(self.card_manager.toggle_visible)
        self.tray.quit_requested.connect(self._quit)
        self.card_manager.card_count_changed.connect(self.tray.set_tooltip)

    def _setup_shortcuts(self):
        from PySide6.QtGui import QShortcut, QKeySequence
        sc_new = QShortcut(QKeySequence("Ctrl+N"), self.qapp)
        sc_new.setContext(Qt.ApplicationShortcut)
        sc_new.activated.connect(self._on_new_card)
        sc_hide = QShortcut(QKeySequence("Ctrl+Shift+H"), self.qapp)
        sc_hide.setContext(Qt.ApplicationShortcut)
        sc_hide.activated.connect(self.card_manager.hide_all)

    def _on_new_card(self):
        """创建新卡片，随机偏移位置避免重叠."""
        base_x, base_y = 400, 300
        offset_x = random.randint(-100, 100)
        offset_y = random.randint(-100, 100)
        card = self.card_manager.create_card(base_x + offset_x, base_y + offset_y)
        card.card_widget.focus_edit()

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self.settings.set("theme", "dark" if self._is_dark else "light")
        self._apply_theme()
        self.tray.set_theme_label(self._is_dark)

    def _apply_theme(self):
        theme_file = "dark.qss" if self._is_dark else "light.qss"
        qss_path = os.path.join(os.path.dirname(__file__), "..",
                                "ui", "resources", "styles", theme_file)
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.qapp.setStyleSheet(f.read())
        else:
            self.qapp.setStyleSheet("")

    def _quit(self):
        self.card_manager.save_all()
        self.database.close()
        self.qapp.quit()

    def run(self):
        sys.exit(self.qapp.exec())

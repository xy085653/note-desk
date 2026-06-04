from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


class CardTray(QObject):
    """系统托盘图标与菜单."""

    new_card_requested = Signal()
    show_all_requested = Signal()
    hide_all_requested = Signal()
    toggle_theme_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        # 使用内置图标作为 fallback
        self.tray_icon.setIcon(QIcon.fromTheme("accessory-text-editor",
                                                QIcon(":/icons/card.svg")))
        self.tray_icon.setToolTip("CardNote - 悬浮卡片记事本")

        self._build_menu()
        self.tray_icon.activated.connect(self._on_activated)
        self.tray_icon.show()

    def _build_menu(self):
        menu = QMenu()

        self.act_new = QAction("📝 新建卡片")
        self.act_new.setShortcut(QKeySequence("Ctrl+N"))
        self.act_new.triggered.connect(self.new_card_requested.emit)
        menu.addAction(self.act_new)

        menu.addSeparator()

        self.act_show = QAction("👁 全部显示")
        self.act_show.triggered.connect(self.show_all_requested.emit)
        menu.addAction(self.act_show)

        self.act_hide = QAction("🙈 全部隐藏")
        self.act_hide.setShortcut(QKeySequence("Ctrl+Shift+H"))
        self.act_hide.triggered.connect(self.hide_all_requested.emit)
        menu.addAction(self.act_hide)

        menu.addSeparator()

        self.act_theme = QAction("🌙 夜间模式")
        self.act_theme.triggered.connect(self.toggle_theme_requested.emit)
        menu.addAction(self.act_theme)

        menu.addSeparator()

        self.act_quit = QAction("❌ 退出")
        self.act_quit.triggered.connect(self.quit_requested.emit)
        menu.addAction(self.act_quit)

        self.tray_icon.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if hasattr(self, 'parent') and hasattr(self.parent(), 'card_manager'):
                self.parent().card_manager.toggle_visible()

    def set_theme_label(self, is_dark: bool):
        action = self.tray_icon.contextMenu().actions()[4]  # theme action
        action.setText("☀️ 日间模式" if is_dark else "🌙 夜间模式")

    def set_tooltip(self, count: int):
        self.tray_icon.setToolTip(f"CardNote - {count} 张卡片")

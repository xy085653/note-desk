import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import QSystemTrayIcon, QMenu

from cardnote.utils.helpers import resource_path


def _load_icon() -> QIcon:
    """加载卡片图标，从文件路径加载 SVG."""
    icon_path = resource_path(os.path.join("ui", "resources", "icons", "card.svg"))
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    # fallback: 使用系统内置图标
    return QIcon.fromTheme("accessory-text-editor")


class CardTray(QObject):
    """系统托盘图标与菜单."""

    new_card_requested = Signal()
    show_all_requested = Signal()
    hide_all_requested = Signal()
    toggle_theme_requested = Signal()
    quit_requested = Signal()
    tray_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(_load_icon())
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
            self.tray_clicked.emit()

    def set_theme_label(self, is_dark: bool):
        self.act_theme.setText("☀️ 日间模式" if is_dark else "🌙 夜间模式")

    def set_tooltip(self, count: int):
        self.tray_icon.setToolTip(f"CardNote - {count} 张卡片")

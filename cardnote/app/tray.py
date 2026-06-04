import os
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QIcon, QAction, QKeySequence, QPixmap, QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


def _create_tray_icon() -> QIcon:
    """程序化绘制托盘图标，不依赖外部文件."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 卡片主体：圆角矩形
    painter.setBrush(QColor(255, 228, 181))
    painter.setPen(QPen(QColor(232, 200, 138), 2))
    painter.drawRoundedRect(6, 10, 52, 44, 8, 8)

    # 卡片顶栏
    painter.setBrush(QColor(255, 214, 153))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(6, 10, 52, 10, 8, 8)
    painter.drawRect(6, 18, 52, 2)

    # 文字线条
    painter.setPen(QPen(QColor(204, 176, 122), 2))
    line_y = [28, 36, 44]
    line_widths = [32, 24, 18]
    for y, w in zip(line_y, line_widths):
        painter.drawLine(18, y, 18 + w, y)

    # 右上角红点
    painter.setBrush(QColor(255, 138, 128))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(48, 14, 8, 8)

    painter.end()
    return QIcon(pixmap)


class CardTray(QObject):
    """系统托盘图标与菜单."""

    new_card_requested = Signal()
    show_all_requested = Signal()
    hide_all_requested = Signal()
    toggle_theme_requested = Signal()
    toggle_startup_requested = Signal()
    quit_requested = Signal()
    tray_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(_create_tray_icon())
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

        self.act_startup = QAction("⚡ 开机自启")
        self.act_startup.triggered.connect(self.toggle_startup_requested.emit)
        menu.addAction(self.act_startup)

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

    def set_startup_label(self, enabled: bool):
        self.act_startup.setText("✅ 开机自启" if enabled else "⚡ 开机自启")

    def set_tooltip(self, count: int):
        self.tray_icon.setToolTip(f"CardNote - {count} 张卡片")

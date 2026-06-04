from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QEasingCurve, QPoint, QAbstractAnimation
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QSizeGrip, QCheckBox

from cardnote.ui.card_widget import CardWidget
from cardnote.ui.color_schemes import get_scheme, SCHEMES


class FloatingCard(QWidget):
    """独立悬浮卡片窗口 (FramelessWindowHint)."""

    CARD_RADIUS = 16
    SHADOW_MARGIN = 10
    TITLE_BAR_HEIGHT = 32

    delete_requested = Signal(str)  # card_id

    def __init__(self, card_id: str, card_data: dict, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.card_data = card_data
        self._dragging = False
        self._drag_pos = QPoint()
        self._resizing = False
        self._edit_mode = False
        self._delete_animation = None

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)

        # 根据数据设置几何位置
        scheme = get_scheme(card_data.get("color_scheme", 0))
        self.color_start = QColor(scheme.light_start)
        self.color_end = QColor(scheme.light_end)
        w = int(card_data.get("width", 260))
        h = int(card_data.get("height", 260))
        self.setGeometry(
            int(card_data.get("pos_x", 400)),
            int(card_data.get("pos_y", 300)),
            w + self.SHADOW_MARGIN * 2,
            h + self.SHADOW_MARGIN * 2,
        )

        self._build_ui()
        self._setup_menu()

        # 如果数据库标记已完成，应用样式
        if bool(self.card_data.get("is_completed", 0)):
            self._apply_completed_style()

    def _build_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(self.SHADOW_MARGIN, self.SHADOW_MARGIN,
                                       self.SHADOW_MARGIN, self.SHADOW_MARGIN)
        main_layout.setSpacing(0)

        # 内容容器
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("cardContent")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(self.TITLE_BAR_HEIGHT)
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 0, 4, 0)

        self.complete_check = QCheckBox()
        self.complete_check.setFixedWidth(20)
        completed = bool(self.card_data.get("is_completed", 0))
        self.complete_check.setChecked(completed)
        self.complete_check.toggled.connect(self._on_completed_toggled)
        title_layout.addWidget(self.complete_check)

        self.pin_label = QLabel("📌")
        self.pin_label.setFixedWidth(24)
        title_layout.addWidget(self.pin_label)
        title_layout.addStretch()

        self.menu_btn = QLabel("⋯")
        self.menu_btn.setFixedWidth(24)
        self.menu_btn.mousePressEvent = self._show_context_menu
        title_layout.addWidget(self.menu_btn)

        content_layout.addWidget(title_bar)

        # 编辑区
        self.card_widget = CardWidget(self.content_widget)
        self.card_widget.set_content(self.card_data.get("content", ""))
        content_layout.addWidget(self.card_widget, 1)

        main_layout.addWidget(self.content_widget)

        # 大小缩放把手 — 透明不可见，固定在右下角功能区
        self.size_grip = QSizeGrip(self)
        self.size_grip.resize(16, 16)
        self.size_grip.setCursor(Qt.SizeFDiagCursor)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                background: transparent;
                border: none;
            }
        """)
        self._position_size_grip()

        # 待办项变化时自适应高度
        self.card_widget.todo_list.items_changed.connect(self._adjust_height)

        # 样式
        self._apply_styles()

    def _apply_styles(self):
        self.content_widget.setStyleSheet(f"""
            #cardContent {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color_start.name()},
                    stop:1 {self.color_end.name()});
                border-radius: {self.CARD_RADIUS}px;
            }}
            #titleBar {{
                background: transparent;
                border-top-left-radius: {self.CARD_RADIUS}px;
                border-top-right-radius: {self.CARD_RADIUS}px;
            }}
            #sizeGrip {{
                background: transparent;
            }}
        """)

    def _on_completed_toggled(self, checked: bool):
        """整卡完成状态切换."""
        self.card_data["is_completed"] = 1 if checked else 0
        if checked:
            self._apply_completed_style()
        else:
            self._remove_completed_style()
        self._emit_save()

    def _apply_completed_style(self):
        """卡片完成：半透明 + 删除线."""
        self.setWindowOpacity(0.55)
        self.card_widget.text_edit.setStyleSheet(
            "color: #888888; text-decoration: line-through;"
        )

    def _remove_completed_style(self):
        """恢复卡片正常样式."""
        self.setWindowOpacity(1.0)
        self.card_widget.text_edit.setStyleSheet("")

    def _setup_menu(self):
        self.context_menu = QMenu(self)
        act_change = self.context_menu.addAction("🎨 更换配色")
        act_change.triggered.connect(self._cycle_color)
        self.context_menu.addSeparator()
        act_delete = self.context_menu.addAction("🗑️ 删除卡片")
        act_delete.triggered.connect(lambda: self.delete_requested.emit(self.card_id))

    def _show_context_menu(self, event):
        self.context_menu.exec(self.mapToGlobal(self.menu_btn.pos()))

    def _cycle_color(self):
        current = self.card_data.get("color_scheme", 0)
        next_idx = (current + 1) % len(SCHEMES)
        self.card_data["color_scheme"] = next_idx
        scheme = get_scheme(next_idx)
        self.color_start = QColor(scheme.light_start)
        self.color_end = QColor(scheme.light_end)
        self._apply_styles()
        self.update()
        # 通知外部保存
        self._emit_save()

    def _emit_save(self):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._do_save())
        self.card_data["content"] = self.card_widget.get_content()
        self.card_data["pos_x"] = self.x()
        self.card_data["pos_y"] = self.y()
        self.card_data["width"] = self.width() - self.SHADOW_MARGIN * 2
        self.card_data["height"] = self.height() - self.SHADOW_MARGIN * 2

    def _do_save(self):
        """由外部 CardManager 绑定."""
        pass  # 会被 CardManager 替换

    def set_save_callback(self, callback):
        self._do_save = callback

    def set_delete_callback(self, callback):
        self._delete_callback = callback

    # ---------- 鼠标事件 ----------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_on_title_bar(event.pos()):
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self.card_data["pos_x"] = self.x()
            self.card_data["pos_y"] = self.y()
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self._emit_save()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.card_widget.focus_edit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setFocus()
            self.card_widget.clearFocus()
        super().keyPressEvent(event)

    def _is_on_title_bar(self, pos: QPoint) -> bool:
        margin = self.SHADOW_MARGIN
        return margin <= pos.y() <= margin + self.TITLE_BAR_HEIGHT

    # ---------- 绘制 ----------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(
            self.SHADOW_MARGIN, self.SHADOW_MARGIN,
            -self.SHADOW_MARGIN, -self.SHADOW_MARGIN
        )

        # 圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRect(rect), self.CARD_RADIUS, self.CARD_RADIUS)

        # 渐变色背景
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, self.color_start)
        gradient.setColorAt(1, self.color_end)
        painter.fillPath(path, QBrush(gradient))

        # 阴影外发光
        painter.setPen(Qt.NoPen)
        for i in range(5):
            alpha = 15 - i * 3
            offset = i * 2
            shadow_rect = rect.adjusted(-offset, -offset, offset, offset)
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(QRect(shadow_rect), self.CARD_RADIUS + offset, self.CARD_RADIUS + offset)
            painter.fillPath(shadow_path, QColor(0, 0, 0, alpha))

    def _animate_delete(self):
        """删除动画并关闭."""
        self._delete_animation = QPropertyAnimation(self, b"geometry")
        self._delete_animation.setDuration(300)
        self._delete_animation.setEasingCurve(QEasingCurve.InOutQuad)
        g = self.geometry()
        center = g.center()
        self._delete_animation.setStartValue(g)
        self._delete_animation.setEndValue(QRect(center.x(), center.y(), 0, 0))
        self._delete_animation.finished.connect(self._on_delete_finished)
        self._delete_animation.start()

    def _on_delete_finished(self):
        if hasattr(self, '_delete_callback'):
            self._delete_callback()
        else:
            self.close()

    def closeEvent(self, event):
        """处理 Alt+F4 或系统关闭: 通知 CardManager 进行清理."""
        if not self._delete_animation or self._delete_animation.state() == QAbstractAnimation.Stopped:
            self.delete_requested.emit(self.card_id)
        super().closeEvent(event)

    def resizeEvent(self, event):
        """窗口大小变化时重定位缩放把手."""
        super().resizeEvent(event)
        self._position_size_grip()

    def _position_size_grip(self):
        """把缩放把手放在窗口右下角."""
        if hasattr(self, 'size_grip'):
            x = self.width() - self.size_grip.width() - 2
            y = self.height() - self.size_grip.height() - 2
            self.size_grip.move(x, y)

    def _adjust_height(self):
        """根据内容自适应高度."""
        content_height = (
            self.TITLE_BAR_HEIGHT
            + self.card_widget.text_edit.document().size().height()
            + self.card_widget.todo_list.sizeHint().height()
            + 40  # margins + padding
        )
        min_h = 180  # 最小高度
        desired = max(min_h, int(content_height) + self.SHADOW_MARGIN * 2)
        current_h = self.height()
        if abs(desired - current_h) > 10:
            self.resize(self.width(), desired)
            self.card_data["height"] = self.width() - self.SHADOW_MARGIN * 2

from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QPushButton, QLabel,
)


class TodoItem(QWidget):
    """单个待办项行: [⠿] [☐] [文字] [🗑️]."""

    toggled = Signal(str, bool)     # todo_id, done
    text_changed = Signal(str, str)  # todo_id, new_text
    deleted = Signal(str)           # todo_id
    drag_started = Signal(str, QPoint)  # todo_id, global_pos

    def __init__(self, todo_id: str, text: str = "", done: bool = False, parent=None):
        super().__init__(parent)
        self.todo_id = todo_id
        self._done = done

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)

        # 拖拽把手
        self.drag_handle = QLabel("⠿")
        self.drag_handle.setFixedWidth(16)
        self.drag_handle.setCursor(Qt.OpenHandCursor)
        self.drag_handle.setStyleSheet("color: rgba(0,0,0,0.25); background: transparent;")
        layout.addWidget(self.drag_handle)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.toggled.connect(self._on_toggled)
        layout.addWidget(self.checkbox)

        self.text_edit = QLineEdit(text)
        self.text_edit.setFrame(False)
        self.text_edit.setPlaceholderText("输入待办事项...")
        self.text_edit.setAttribute(Qt.WA_TranslucentBackground)
        self.text_edit.setAutoFillBackground(False)
        self.text_edit.setStyleSheet("background: transparent; border: none;")
        self.text_edit.editingFinished.connect(self._on_text_changed)
        if done:
            self._apply_done_style()
        layout.addWidget(self.text_edit, 1)

        self.btn_delete = QPushButton("✕")
        self.btn_delete.setFixedSize(20, 20)
        self.btn_delete.setFlat(True)
        self.btn_delete.setVisible(False)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                color: rgba(0,0,0,0.4);
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                color: rgba(200,0,0,0.6);
            }
        """)
        self.btn_delete.clicked.connect(lambda: self.deleted.emit(self.todo_id))
        layout.addWidget(self.btn_delete)

        # 拖拽状态
        self._drag_active = False
        self._drag_start_y = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            if child and child is self.drag_handle:
                self._drag_active = True
                self._drag_start_y = event.globalPosition().y()
                self.drag_handle.setCursor(Qt.ClosedHandCursor)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().y() - self._drag_start_y
            if abs(delta) > 8:
                self.drag_started.emit(self.todo_id, event.globalPosition().toPoint())
                self._drag_start_y = event.globalPosition().y()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_active:
            self._drag_active = False
            self.drag_handle.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.btn_delete.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_delete.setVisible(False)
        super().leaveEvent(event)

    def _on_toggled(self, checked: bool):
        self._done = checked
        self._apply_done_style()
        self.toggled.emit(self.todo_id, checked)

    def _apply_done_style(self):
        if self._done:
            self.text_edit.setStyleSheet(
                "color: #888888; text-decoration: line-through; background: transparent;"
            )
        else:
            self.text_edit.setStyleSheet("background: transparent;")

    def _on_text_changed(self):
        self.text_changed.emit(self.todo_id, self.text_edit.text())


class TodoListWidget(QWidget):
    """待办清单组件，管理多个 TodoItem."""

    todo_added = Signal(str)        # card_id
    todo_toggled = Signal(str, bool)  # todo_id, done
    todo_text_changed = Signal(str, str)  # todo_id, text
    todo_deleted = Signal(str)      # todo_id
    items_changed = Signal()        # 通知外部内容高度变化

    def __init__(self, card_id: str = "", parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.todos: dict[str, TodoItem] = {}
        self._ordered_ids: list[str] = []  # 维护显示顺序

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 8)
        layout.setSpacing(2)

        self.header = QLabel("─── 待办清单 ───")
        self.header.setStyleSheet("color: rgba(0,0,0,0.25); font-size: 11px; background: transparent;")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.items_layout)

        self.add_btn = QPushButton("＋ 添加待办项")
        self.add_btn.setFlat(True)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                text-align: left; color: rgba(0,0,0,0.4); padding: 4px 0;
                background: transparent; border: none;
            }
            QPushButton:hover {
                color: rgba(0,0,0,0.6);
            }
        """)
        self.add_btn.clicked.connect(self._add_item)
        layout.addWidget(self.add_btn)

    def set_card_id(self, card_id: str):
        self.card_id = card_id

    def load_todos(self, items: list[dict]):
        self.clear()
        for item in items:
            self._create_item(item["id"], item["text"], bool(item["done"]))
        self._emit_items_changed()

    def _add_item(self):
        from cardnote.utils.helpers import new_uuid
        todo_id = new_uuid()
        self._create_item(todo_id, "", False)
        self.todo_added.emit(self.card_id)
        self._emit_items_changed()

    def _create_item(self, todo_id: str, text: str, done: bool):
        item = TodoItem(todo_id, text, done)
        item.toggled.connect(lambda tid, d: self.todo_toggled.emit(tid, d))
        item.text_changed.connect(lambda tid, t: self.todo_text_changed.emit(tid, t))
        item.deleted.connect(lambda tid: self._on_item_deleted(tid))
        item.drag_started.connect(self._on_drag_started)
        self.todos[todo_id] = item
        self._ordered_ids.append(todo_id)
        self.items_layout.addWidget(item)

    def _on_drag_started(self, todo_id: str, global_pos: QPoint):
        """拖拽起点 -> 实时检测是否需要交换."""
        item = self.todos.get(todo_id)
        if not item:
            return
        src_idx = self._ordered_ids.index(todo_id)
        # 检查当前鼠标位置是否跨越了相邻项的中点
        mouse_y = self.mapFromGlobal(global_pos).y()
        for i, tid in enumerate(self._ordered_ids):
            if tid == todo_id:
                continue
            other = self.todos[tid]
            mid_y = other.mapTo(self, other.rect().center()).y()
            # 向上拖：鼠标进入上方项下半区 -> 交换
            if i < src_idx and mouse_y <= mid_y + 4:
                self._swap_items(src_idx, i)
                return
            # 向下拖：鼠标进入下方项上半区 -> 交换
            if i > src_idx and mouse_y >= mid_y - 4:
                self._swap_items(src_idx, i)
                return

    def _swap_items(self, idx_a: int, idx_b: int):
        """交换两个位置上的待办项."""
        if idx_a == idx_b:
            return
        # 确保 idx_a < idx_b
        if idx_a > idx_b:
            idx_a, idx_b = idx_b, idx_a
        tid_a = self._ordered_ids[idx_a]
        tid_b = self._ordered_ids[idx_b]
        # 交换在 _ordered_ids 中的位置
        self._ordered_ids[idx_a], self._ordered_ids[idx_b] = \
            self._ordered_ids[idx_b], self._ordered_ids[idx_a]
        # 刷新布局：按新顺序重新插入
        for i, tid in enumerate(self._ordered_ids):
            widget = self.todos[tid]
            self.items_layout.insertWidget(i, widget)
        self._emit_items_changed()

    def _on_item_deleted(self, todo_id: str):
        self.remove_item(todo_id)
        self.todo_deleted.emit(todo_id)
        self._emit_items_changed()

    def remove_item(self, todo_id: str):
        if todo_id in self.todos:
            item = self.todos.pop(todo_id)
            self._ordered_ids.remove(todo_id)
            self.items_layout.removeWidget(item)
            item.deleteLater()

    def clear(self):
        for todo_id in list(self.todos.keys()):
            self.remove_item(todo_id)

    def _emit_items_changed(self):
        QTimer.singleShot(0, self.items_changed.emit)

    def get_all(self) -> list[dict]:
        return [
            {"id": tid, "text": self.todos[tid].text_edit.text(),
             "done": self.todos[tid]._done}
            for tid in self._ordered_ids
        ]

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QPushButton, QLabel,
)


class TodoItem(QWidget):
    """单个待办项行: [☐] [文字] [🗑️]."""

    toggled = Signal(str, bool)   # todo_id, done
    text_changed = Signal(str, str)  # todo_id, new_text
    deleted = Signal(str)         # todo_id

    def __init__(self, todo_id: str, text: str = "", done: bool = False, parent=None):
        super().__init__(parent)
        self.todo_id = todo_id
        self._done = done

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)

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

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 8)
        layout.setSpacing(2)

        # 分隔线 + 标题
        self.header = QLabel("─── 待办清单 ───")
        self.header.setStyleSheet("color: rgba(0,0,0,0.25); font-size: 11px; background: transparent;")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        # 待办项容器
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.items_layout)

        # 添加按钮
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

        # 不要 addStretch，让高度由内容决定

    def set_card_id(self, card_id: str):
        self.card_id = card_id

    def load_todos(self, items: list[dict]):
        """从数据加载待办项."""
        self.clear()
        for item in items:
            self._create_item(item["id"], item["text"], bool(item["done"]))
        self._emit_items_changed()

    def _add_item(self):
        """新增一个空待办项."""
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
        self.todos[todo_id] = item
        self.items_layout.addWidget(item)

    def _on_item_deleted(self, todo_id: str):
        self.remove_item(todo_id)
        self.todo_deleted.emit(todo_id)
        self._emit_items_changed()

    def remove_item(self, todo_id: str):
        if todo_id in self.todos:
            item = self.todos.pop(todo_id)
            self.items_layout.removeWidget(item)
            item.deleteLater()

    def clear(self):
        for todo_id in list(self.todos.keys()):
            self.remove_item(todo_id)

    def _emit_items_changed(self):
        QTimer.singleShot(0, self.items_changed.emit)

    def get_all(self) -> list[dict]:
        return [
            {"id": tid, "text": item.text_edit.text(), "done": item._done}
            for tid, item in self.todos.items()
        ]

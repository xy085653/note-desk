from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from cardnote.ui.todo_list_widget import TodoListWidget


class CardWidget(QWidget):
    """卡片内部内容组件，包含编辑区和待办清单."""

    content_changed = Signal(str)
    editing_finished = Signal()
    todo_added = Signal(str)
    todo_toggled = Signal(str, bool)
    todo_text_changed = Signal(str, str)
    todo_deleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(4)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("在这里写下你的想法...")
        self.text_edit.setFrameShape(QTextEdit.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setAttribute(Qt.WA_TranslucentBackground)
        self.text_edit.viewport().setAutoFillBackground(False)
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)

        self.todo_list = TodoListWidget(parent=self)
        self.todo_list.todo_added.connect(lambda cid: self.todo_added.emit(cid))
        self.todo_list.todo_toggled.connect(lambda tid, d: self.todo_toggled.emit(tid, d))
        self.todo_list.todo_text_changed.connect(lambda tid, t: self.todo_text_changed.emit(tid, t))
        self.todo_list.todo_deleted.connect(lambda tid: self.todo_deleted.emit(tid))
        layout.addWidget(self.todo_list)

    def _on_text_changed(self):
        content = self.text_edit.toPlainText()
        self.content_changed.emit(content)

    def set_content(self, text: str):
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.text_edit.blockSignals(False)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def focus_edit(self):
        self.text_edit.setFocus()
        self.text_edit.selectAll()

    def set_card_id(self, card_id: str):
        self.todo_list.set_card_id(card_id)

    def load_todos(self, items: list[dict]):
        self.todo_list.load_todos(items)

    def get_all_todos(self) -> list[dict]:
        return self.todo_list.get_all()

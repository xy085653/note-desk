from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class CardWidget(QWidget):
    """卡片内部内容组件，包含编辑区和信号."""

    content_changed = Signal(str)
    editing_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("在这里写下你的想法...")
        self.text_edit.setFrameShape(QTextEdit.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 关键：禁止 viewport 绘制默认白色背景，让渐变背景透出来
        self.text_edit.setAttribute(Qt.WA_TranslucentBackground)
        self.text_edit.viewport().setAutoFillBackground(False)
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)

    def _on_text_changed(self):
        content = self.text_edit.toPlainText()
        self.content_changed.emit(content)

    def set_content(self, text: str):
        """设置文本内容（不触发 textChanged 信号循环）. """
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.text_edit.blockSignals(False)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def focus_edit(self):
        """聚焦到编辑区."""
        self.text_edit.setFocus()
        self.text_edit.selectAll()

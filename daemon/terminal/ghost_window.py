"""Safe, visual-only terminal window used for idle auto-typing effects."""

from typing import Optional

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPalette, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class GhostTerminalWindow(QWidget):
    """Display generated terminal text one character at a time without executing it."""

    def __init__(
        self,
        text: str,
        interval_ms: int = 90,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._text = text.strip()
        self._position = 0
        self._interval_ms = interval_ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._type_next_character)

        self._configure_window()
        self._build_editor()

    def _configure_window(self) -> None:
        self.setWindowTitle("daemon://idle-shell")
        self.setWindowFlags(
            Qt.Window
            | Qt.Tool
            | Qt.WindowStaysOnTopHint
            | Qt.WindowDoesNotAcceptFocus
            | Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowOpacity(0.88)
        self.resize(560, 250)

    def _build_editor(self) -> None:
        self.editor = QPlainTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.editor.setPlainText("ghost@daemon:~$ ")

        font = QFont("Consolas", 10)
        self.editor.setFont(font)
        palette = self.editor.palette()
        palette.setColor(QPalette.Base, QColor("#08100d"))
        palette.setColor(QPalette.Text, QColor("#8df5b0"))
        palette.setColor(QPalette.Highlight, QColor("#1c4930"))
        self.editor.setPalette(palette)
        self.editor.setStyleSheet(
            "QPlainTextEdit { border: 1px solid #2e8b57; padding: 8px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

    def start_typing(self) -> None:
        """Start the visual typing animation."""
        self.show()
        self._timer.start(self._interval_ms)

    def _type_next_character(self) -> None:
        if self._position >= len(self._text):
            self._timer.stop()
            return

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(self._text[self._position])
        self.editor.setTextCursor(cursor)
        self._position += 1

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)

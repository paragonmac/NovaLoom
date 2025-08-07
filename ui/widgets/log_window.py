"""
Log window widgets for NovaLoom application.
"""
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor


class LogStream(QObject):
    """Custom stream for redirecting stdout/stderr to the log window"""
    newText = Signal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass


class LogWindow(QTextEdit):
    """Custom log window widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setMaximumHeight(150)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                border: 1px solid #3c3c3c;
            }
        """)
        
    def append(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

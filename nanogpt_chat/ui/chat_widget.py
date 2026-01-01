from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import textwrap


class ChatMessageWidget(QFrame):
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        if self.role == "user":
            header_color = "#1a73e8"
            bubble_color = "#e8f0fe"
            bubble_border = "#c2dbff"
        else:
            header_color = "#137333"
            bubble_color = "#e6f4ea"
            bubble_border = "#ace1af"
        
        role_label = QLabel("You" if self.role == "user" else "Assistant")
        role_font = QFont()
        role_font.setPointSize(11)
        role_font.setWeight(QFont.Weight.DemiBold)
        role_label.setFont(role_font)
        role_label.setStyleSheet(f"color: {header_color};")
        
        layout.addWidget(role_label)
        
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.PlainText)
        content_label.setFont(QFont("", 12))
        content_label.setStyleSheet(f"color: #202124;")
        
        layout.addWidget(content_label)
        
        self.setStyleSheet(f"""
            ChatMessageWidget {{
                background-color: {bubble_color};
                border: 1px solid {bubble_border};
                border-radius: 12px;
            }}
        """)
        
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_layout = QVBoxLayout(self)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()
        
        self.setStyleSheet("""
            ChatWidget {
                background-color: #f1f3f4;
            }
        """)
        
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def add_message(self, role: str, content: str, is_stream: bool = False):
        if is_stream and self.messages_layout.count() > 1:
            last_index = self.messages_layout.count() - 2
            last_widget = self.messages_layout.itemAt(last_index).widget()
            if last_widget and last_widget.role == "assistant":
                for i in range(last_widget.layout().count()):
                    item = last_widget.layout().itemAt(i)
                    if item.widget() and isinstance(item.widget(), QLabel):
                        if i == 1:
                            item.widget().setText(content)
                            last_widget.content = content
                            break
                return
        
        message_widget = ChatMessageWidget(role, content)
        
        self.messages_layout.removeItem(self.messages_layout.itemAt(
            self.messages_layout.count() - 1
        ))
        
        self.messages_layout.addWidget(message_widget)
        self.messages_layout.addStretch()
        
        scroll_area = self.parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )
    
    def clear(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
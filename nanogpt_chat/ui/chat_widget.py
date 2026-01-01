from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor
import markdown
import textwrap


class ChatMessageWidget(QWidget):
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.setup_ui()
        self.update_content()
    
    def update_content(self):
        if self.role == "user":
            text_color = "#ffffff"
        else:
            text_color = "#ececec"
            
        # Render Markdown to HTML
        html_content = markdown.markdown(
            self.content,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
        
        # Add basic CSS for markdown elements
        styled_html = f"""
        <style>
            * {{ color: {text_color}; font-size: 13px; line-height: 1.5; }}
            code {{ background-color: rgba(0,0,0,0.2); padding: 2px 4px; border-radius: 3px; font-family: 'Cascadia Code', 'Consolas', monospace; }}
            pre {{ background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; }}
            pre code {{ background-color: transparent; padding: 0; }}
            a {{ color: #4fc3f7; }}
            p {{ margin: 0; padding: 0; }}
            ul, ol {{ margin-left: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; border: 1px solid #444; }}
            th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
            th {{ background-color: rgba(255,255,255,0.1); font-weight: bold; }}
        </style>
        {html_content}
        """
        self.content_label.setText(styled_html)

    def setup_ui(self):
        # Use QHBoxLayout for horizontal positioning with stretches
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 4, 20, 4)
        main_layout.setSpacing(0)
        
        # Message bubble container
        self.bubble = QFrame()
        self.bubble.setObjectName("bubble")
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(16, 10, 16, 10)
        bubble_layout.setSpacing(0)
        
        if self.role == "user":
            bubble_color = "#007acc" # Modern Blue
            bubble_style = "border-bottom-right-radius: 4px;"
            max_w = 600
        else:
            bubble_color = "#2f2f2f" # Modern Gray
            bubble_style = "border-bottom-left-radius: 4px;"
            max_w = 700
        
        self.bubble.setStyleSheet(f"""
            #bubble {{
                background-color: {bubble_color};
                border-radius: 18px;
                {bubble_style}
            }}
        """)
        
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.TextFormat.RichText)
        self.content_label.setFont(QFont("", 12))
        self.content_label.setStyleSheet("border: none; background: transparent;")
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_label.setOpenExternalLinks(True)
        
        # Use Preferred instead of Expanding to keep bubbles tight
        self.content_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.bubble.setMaximumWidth(max_w)
        
        bubble_layout.addWidget(self.content_label)
        
        if self.role == "user":
            main_layout.addStretch()
            main_layout.addWidget(self.bubble)
        else:
            main_layout.addWidget(self.bubble)
            main_layout.addStretch()
        
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_layout = QVBoxLayout(self)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(0)
        self.messages_layout.addStretch()
        
        self.setStyleSheet("""
            ChatWidget {
                background-color: #171717;
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
                # Direct access to the content label
                if hasattr(last_widget, 'content_label'):
                    # Re-render markdown for every chunk update
                    last_widget.content = content
                    last_widget.update_content()
                    
                    # Force layout recalculation for expansion
                    last_widget.content_label.adjustSize()
                    last_widget.bubble.adjustSize()
                    last_widget.adjustSize()
                return
        
        message_widget = ChatMessageWidget(role, content)
        
        # Insert before the stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Autoscroll
        QApplication.processEvents() # Ensure widget is rendered for scroll calculation
        scroll_area = self.parent().parent() # QScrollArea is grandparent
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )
    
    def clear(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
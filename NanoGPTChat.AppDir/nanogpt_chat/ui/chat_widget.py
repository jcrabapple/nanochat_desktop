from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, 
    QApplication, QPushButton, QMenu, QTextEdit, QDialog, 
    QDialogButtonBox, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QDateTime, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QAction, QClipboard
import textwrap
import re

class TypingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation_timer = None
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 4, 20, 4)
        layout.setSpacing(8)
        
        self.bubble = QFrame()
        self.bubble.setObjectName("typing_bubble")
        bubble_layout = QHBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        bubble_layout.setSpacing(4)
        
        self.dots = []
        for i in range(3):
            dot = QLabel("•")
            dot.setStyleSheet("color: #aaaaaa; font-size: 24px; font-weight: bold; background: transparent;")
            bubble_layout.addWidget(dot)
            self.dots.append(dot)
        
        layout.addWidget(self.bubble)
        layout.addStretch()
        
        self.bubble.setStyleSheet("""
            #typing_bubble {
                background-color: #2f2f2f;
                border-radius: 18px;
                border-bottom-left-radius: 4px;
            }
        """)
        self.hide()
    
    def start_animation(self):
        if self.animation_timer is None:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.animate_dots)
            self.animation_timer.start(300)
    
    def stop_animation(self):
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
    
    def animate_dots(self):
        import random
        for dot in self.dots:
            opacity = random.choice([0.3, 0.6, 1.0])
            dot.setStyleSheet(f"color: rgba(170, 170, 170, {opacity}); font-size: 24px; font-weight: bold; background: transparent;")

class ChatMessageWidget(QWidget):
    edit_requested = pyqtSignal(str, str)
    regenerate_requested = pyqtSignal(str, str)
    delete_requested = pyqtSignal(str, str)
    
    def __init__(self, role: str, content: str, timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp else QDateTime.currentDateTime().toString("h:mm AP")
        self._pending_content = None
        self._render_timer = None
        
        self.setup_ui()
        self.update_content()
        # Removed animation to improve performance and fix crashes

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 4, 20, 4)
        main_layout.setSpacing(0)
        
        self.bubble = QFrame()
        self.bubble.setObjectName("bubble")
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(16, 10, 16, 10)
        bubble_layout.setSpacing(0)
        
        if self.role == "user":
            bubble_color = "#007acc"
            bubble_style = "border-bottom-right-radius: 4px;"
            max_w = 600
        else:
            bubble_color = "#2f2f2f"
            bubble_style = "border-bottom-left-radius: 4px;"
            max_w = 700
        
        self.bubble.setStyleSheet(f"""
            #bubble {{
                background-color: {bubble_color};
                border-radius: 20px;
                {bubble_style}
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        
        # Removed shadow effect to fix QPainter errors and improve performance
        
        meta_layout = QHBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 8)
        meta_layout.setSpacing(8)
        
        self.timestamp_label = QLabel(self.timestamp)
        self.timestamp_label.setStyleSheet("color: #aaaaaa; font-size: 11px; background: transparent;")
        meta_layout.addWidget(self.timestamp_label)
        
        meta_layout.addStretch()
        
        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(24, 24)
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.menu_button.clicked.connect(self.show_context_menu)
        meta_layout.addWidget(self.menu_button)
        bubble_layout.addLayout(meta_layout)
        
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.TextFormat.RichText)
        self.content_label.setFont(QFont("", 12))
        self.content_label.setStyleSheet("border: none; background: transparent;")
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_label.setOpenExternalLinks(True)
        self.content_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.bubble.setMaximumWidth(max_w)
        
        bubble_layout.addWidget(self.content_label)
        
        if self.role == "user":
            main_layout.addStretch()
            main_layout.addWidget(self.bubble)
        else:
            main_layout.addWidget(self.bubble)
            main_layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def update_content(self):
        if self.role == "user":
            text_color = "#ffffff"
        else:
            text_color = "#ececec"
            
        html_content = self.content.replace("\n", "<br>")
        try:
            import markdown
            html_content = markdown.markdown(
                self.content,
                extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
            )
        except Exception:
            pass
        
        styled_html = f"""
        <style>
            * {{ color: {text_color}; font-size: 13px; line-height: 1.5; }}
            code {{ background-color: rgba(0,0,0,0.2); padding: 2px 4px; border-radius: 3px; font-family: 'Cascadia Code', 'Consolas', monospace; }}
            pre {{ background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; position: relative; }}
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

    def update_content_throttled(self, content):
        self.content = content
        self._pending_content = content
        if self._render_timer is None or not self._render_timer.isActive():
            self.update_content()
            self._render_timer = QTimer.singleShot(200, self._clear_pending_update)
    
    def _clear_pending_update(self):
        if self._pending_content is not None:
            self.content = self._pending_content
            self.update_content()
            self._pending_content = None
            self._render_timer = None

    def show_context_menu(self):
        menu = QMenu(self)
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_message)
        menu.addAction(copy_action)
        
        if self.role == "user":
            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(self.edit_message)
            menu.addAction(edit_action)
        else:
            regenerate_action = QAction("Regenerate", self)
            regenerate_action.triggered.connect(self.regenerate_message)
            menu.addAction(regenerate_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_message)
        menu.addAction(delete_action)
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def copy_message(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content)
    
    def edit_message(self):
        from nanogpt_chat.ui.main_window import MessageEditDialog
        dialog = MessageEditDialog(self.content, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_content = dialog.get_content()
            if new_content != self.content:
                self.content = new_content
                self.update_content()
                self.edit_requested.emit(self.role, new_content)
    
    def regenerate_message(self):
        self.regenerate_requested.emit(self.role, self.content)
    
    def delete_message(self):
        self.delete_requested.emit(self.role, self.content)

class ChatWidget(QWidget):
    edit_requested = pyqtSignal(str, str)
    regenerate_requested = pyqtSignal(str, str)
    delete_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_layout = QVBoxLayout(self)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(0)
        self.messages_layout.addStretch()
        
        try:
            from nanogpt_chat.ui.themes import get_chat_widget_stylesheet
            self.setStyleSheet(get_chat_widget_stylesheet())
        except ImportError:
            self.setStyleSheet("background-color: #171717;")
            
        self.typing_indicator = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def show_typing_indicator(self):
        try:
            # Check if indicator is None or its underlying C++ object was deleted
            if self.typing_indicator is None or RuntimeError:
                # We need a proper way to check if a QObject is deleted
                # In PyQt, checking if it still exists can be tricky, 
                # but resetting it in clear() is the primary fix.
                pass
            
            if self.typing_indicator is None:
                self.typing_indicator = TypingIndicator()
                self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.typing_indicator)
            
            self.typing_indicator.show()
            self.typing_indicator.start_animation()
            self._scroll_to_bottom()
        except RuntimeError:
            # Fallback if the object was somehow deleted without setting to None
            self.typing_indicator = TypingIndicator()
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.typing_indicator)
            self.typing_indicator.show()
            self.typing_indicator.start_animation()
            self._scroll_to_bottom()
    
    def hide_typing_indicator(self):
        if self.typing_indicator:
            self.typing_indicator.stop_animation()
            self.typing_indicator.hide()

    def _scroll_to_bottom(self):
        scroll_area = self.parent().parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())

    def add_message(self, role: str, content: str, is_stream: bool = False, timestamp: str = ""):
        if is_stream and self.messages_layout.count() > 1:
            # Look for the last ChatMessageWidget instead of just taking the last index
            for i in range(self.messages_layout.count() - 2, -1, -1):
                last_widget = self.messages_layout.itemAt(i).widget()
                if isinstance(last_widget, ChatMessageWidget) and last_widget.role == "assistant":
                    if hasattr(last_widget, 'content_label'):
                        last_widget.update_content_throttled(content)
                        last_widget.content_label.adjustSize()
                        last_widget.bubble.adjustSize()
                        last_widget.adjustSize()
                    return
                # Stop if we hit a non-message widget that isn't the typing indicator
                if last_widget and not isinstance(last_widget, (ChatMessageWidget, TypingIndicator)):
                    break
         
        message_widget = ChatMessageWidget(role, content, timestamp)
        message_widget.edit_requested.connect(self.edit_requested.emit)
        message_widget.regenerate_requested.connect(self.regenerate_requested.emit)
        message_widget.delete_requested.connect(self.delete_requested.emit)
        
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        self._scroll_to_bottom()
    
    def clear(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                if item.widget() == self.typing_indicator:
                    self.typing_indicator = None
                item.widget().deleteLater()
        self.typing_indicator = None # Ensure it's reset
    
    def add_message_at_top(self, role: str, content: str, timestamp: str = ""):
        message_widget = ChatMessageWidget(role, content, timestamp)
        message_widget.edit_requested.connect(self.edit_requested.emit)
        message_widget.regenerate_requested.connect(self.regenerate_requested.emit)
        message_widget.delete_requested.connect(self.delete_requested.emit)
        
        insert_index = 0
        if self.messages_layout.count() > 1:
            # Check if first is stretch
            first_item = self.messages_layout.itemAt(0)
            if not first_item.widget():
                insert_index = 1
        self.messages_layout.insertWidget(insert_index, message_widget)

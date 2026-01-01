from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime


class SessionItemWidget(QWidget):
    delete_requested = pyqtSignal(str)
    
    def __init__(self, session_id, title, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #cccccc; background: transparent; border: none;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
                color: white;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.session_id))
        self.delete_btn.hide() # Hidden by default, shown on hover
        layout.addWidget(self.delete_btn)
        
    def enterEvent(self, event):
        self.delete_btn.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.delete_btn.hide()
        super().leaveEvent(event)


class Sidebar(QWidget):
    session_selected = pyqtSignal(str)
    session_deleted = pyqtSignal(str)
    new_chat = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setStyleSheet("""
            background-color: #252526;
            border-right: 1px solid #333333;
        """)
        
        header = QLabel("NanoGPT")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            padding: 20px 16px 16px 16px;
            background-color: #252526;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            border-bottom: 1px solid #333333;
        """)
        layout.addWidget(header)
        
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #252526;
                color: #cccccc;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            QListWidget::item:selected {
                background-color: #37373d;
            }
        """)
        self.session_list.itemClicked.connect(self.on_session_clicked)
        layout.addWidget(self.session_list)
        
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #252526; border-top: 1px solid #333333;")
        btn_layout = QVBoxLayout(button_container)
        btn_layout.setContentsMargins(12, 12, 12, 12)
        btn_layout.setSpacing(8)
        
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #118ad3;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat.emit)
        btn_layout.addWidget(new_chat_btn)
        
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        settings_btn.clicked.connect(self.settings_requested.emit)
        btn_layout.addWidget(settings_btn)
        
        layout.addWidget(button_container)
    
    def update_sessions(self, sessions):
        self.session_list.clear()
        for session in sessions:
            item = QListWidgetItem(self.session_list)
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            
            widget = SessionItemWidget(session.id, session.title)
            widget.delete_requested.connect(self.session_deleted.emit)
            
            item.setSizeHint(widget.sizeHint())
            self.session_list.addItem(item)
            self.session_list.setItemWidget(item, widget)
    
    def on_session_clicked(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_selected.emit(session_id)
    
    def select_session(self, session_id):
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == session_id:
                self.session_list.setCurrentItem(item)
                break
    
    def clear(self):
        self.session_list.clear()

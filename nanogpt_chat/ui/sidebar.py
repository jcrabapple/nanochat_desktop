from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime


class Sidebar(QWidget):
    session_selected = pyqtSignal(str)
    new_chat = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setStyleSheet("""
            background-color: #f8f9fa;
        """)
        
        header = QLabel("NanoGPT")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("""
            padding: 20px 16px 16px 16px;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #0066CC, stop: 1 #00A86B
            );
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(header)
        
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #F5F7FA;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-bottom: 1px solid #EAEEF2;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #E8EEF5;
            }
            QListWidget::item:selected {
                background-color: #0066CC;
                color: white;
            }
        """)
        self.session_list.itemClicked.connect(self.on_session_clicked)
        layout.addWidget(self.session_list)
        
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("""
            QPushButton {
                margin: 12px 16px;
                padding: 14px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0066CC, stop: 1 #00A86B
                );
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat.emit)
        layout.addWidget(new_chat_btn)
    
    def update_sessions(self, sessions):
        self.session_list.clear()
        for session in sessions:
            item = QListWidgetItem(session.title)
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            self.session_list.addItem(item)
    
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

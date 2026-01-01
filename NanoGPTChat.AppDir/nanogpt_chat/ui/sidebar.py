from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction
from datetime import datetime


class SessionItemWidget(QWidget):
    delete_requested = pyqtSignal(str)
    rename_requested = pyqtSignal(str, str)  # session_id, new_title
    
    def __init__(self, session_id, title, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.title = title
        self.is_editing = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #cccccc; background: transparent; border: none;")
        self.title_label.mouseDoubleClickEvent = self.start_rename
        layout.addWidget(self.title_label)
        
        self.title_edit = QLineEdit(self.title)
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 4px;
            }
        """)
        self.title_edit.returnPressed.connect(self.finish_rename)
        self.title_edit.editingFinished.connect(self.finish_rename)
        self.title_edit.hide()
        layout.addWidget(self.title_edit)
        
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
        
    def start_rename(self, event):
        self.is_editing = True
        self.title_label.hide()
        self.title_edit.setText(self.title)
        self.title_edit.show()
        self.title_edit.selectAll()
        self.title_edit.setFocus()
        event.accept()
        
    def finish_rename(self):
        if not self.is_editing:
            return
            
        self.is_editing = False
        new_title = self.title_edit.text().strip()
        if new_title and new_title != self.title:
            self.rename_requested.emit(self.session_id, new_title)
            self.title = new_title
            self.title_label.setText(new_title)
            
        self.title_edit.hide()
        self.title_label.show()
        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.start_rename)
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.session_id))
        menu.addAction(delete_action)
        
        menu.exec(event.globalPos())
        
    def enterEvent(self, event):
        self.delete_btn.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.delete_btn.hide()
        super().leaveEvent(event)


class Sidebar(QWidget):
    session_selected = pyqtSignal(str)
    session_deleted = pyqtSignal(str)
    session_renamed = pyqtSignal(str, str)  # session_id, new_title
    search_requested = pyqtSignal(str)      # query
    load_more_requested = pyqtSignal()      # request more sessions
    new_chat = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_sessions = []  # Store all sessions for filtering
        self.displayed_sessions = []  # Sessions currently displayed
        self.page_size = 50
        self.current_offset = 0
        self.has_more_sessions = True
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        from nanogpt_chat.ui.themes import get_sidebar_stylesheet
        self.setStyleSheet(get_sidebar_stylesheet())
        
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
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search chats...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 10px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
        self.search_input.textChanged.connect(self.filter_sessions)
        layout.addWidget(self.search_input)
        
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
        self.session_list.verticalScrollBar().valueChanged.connect(self.on_scroll)
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
        # For initial load, store first batch and set up pagination
        self.all_sessions = []  # Clear for search mode
        self.displayed_sessions = sessions
        self.current_offset = len(sessions)
        self.has_more_sessions = len(sessions) == self.page_size
        self.display_sessions(sessions)
    
    def append_sessions(self, sessions):
        """Append additional sessions for pagination"""
        self.displayed_sessions.extend(sessions)
        self.current_offset += len(sessions)
        self.has_more_sessions = len(sessions) == self.page_size
        # Only append new sessions to the display
        self.display_sessions(sessions, append=True)
    
    def display_sessions(self, sessions, append=False):
        if not append:
            self.session_list.clear()
            
        for session in sessions:
            item = QListWidgetItem(self.session_list)
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            
            widget = SessionItemWidget(session.id, session.title)
            widget.delete_requested.connect(self.session_deleted.emit)
            widget.rename_requested.connect(self.rename_session)
            
            item.setSizeHint(widget.sizeHint())
            self.session_list.addItem(item)
            self.session_list.setItemWidget(item, widget)
    
    def filter_sessions(self, text):
        # Emit signal to let main window handle searching (including DB content)
        self.search_requested.emit(text)
    
    def on_session_clicked(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_selected.emit(session_id)
    
    def on_scroll(self, value):
        # Check if we're near the bottom and have more sessions to load
        scrollbar = self.session_list.verticalScrollBar()
        if (scrollbar.maximum() - value) < 100 and self.has_more_sessions:
            self.load_more_requested.emit()
    
    def select_session(self, session_id):
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == session_id:
                self.session_list.setCurrentItem(item)
                break
    
    def rename_session(self, session_id, new_title):
        # Emit a signal to let the main window handle the database update
        self.session_renamed.emit(session_id, new_title)
    
    def clear(self):
        self.session_list.clear()

import asyncio
from typing import Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QComboBox, QLabel, QLineEdit, QFrame, QScrollArea,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QSlider,
    QGroupBox, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QTextCursor, QAction, QIcon

from nanogpt_chat.ui.chat_widget import ChatWidget
from nanogpt_chat.ui.settings_dialog import SettingsDialog
from nanogpt_chat.ui.sidebar import Sidebar
from nanogpt_chat.utils import get_api_client, get_database


class ChatWorker(QThread):
    response_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, messages, model, temperature, max_tokens):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def run(self):
        try:
            response = self.api_client.chat_completion_sync(
                self.model, self.messages, self.temperature, self.max_tokens, False
            )
            
            if response:
                self.finished.emit(response)
            else:
                self.error.emit("Empty response from API")
                
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoGPT Chat")
        self.setMinimumSize(QSize(900, 650))
        self.current_session_id: Optional[str] = None
        self.messages: list = []
        self.api_client = None
        self.db = None
        
        self.setup_ui()
        self.setup_menubar()
        self.load_data()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(260)
        self.sidebar.session_selected.connect(self.load_session)
        self.sidebar.new_chat.connect(self.new_chat)
        splitter.addWidget(self.sidebar)
        
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        model_toolbar = QWidget()
        model_toolbar.setStyleSheet("""
            background-color: #f8f9fa;
            border-bottom: 1px solid #dadce0;
        """)
        model_layout = QHBoxLayout(model_toolbar)
        model_layout.setContentsMargins(20, 12, 20, 12)
        model_layout.setSpacing(12)
        
        model_label = QLabel("Model:")
        model_label.setFont(QFont("", 11))
        model_label.setStyleSheet("color: #666;")
        model_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(180)
        self.model_combo.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ])
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #0066CC;
            }
        """)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #e8eaed;
                color: #3c4043;
                border: 1px solid #dadce0;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        model_layout.addWidget(settings_btn)
        
        chat_layout.addWidget(model_toolbar)
        
        self.chat_widget = ChatWidget()
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FAFBFC;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #F0F0F0;
            }
            QScrollBar::handle:vertical {
                background: #CCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #BBB;
            }
        """)
        chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(chat_scroll)
        
        input_container = QWidget()
        input_container.setStyleSheet("""
            background-color: #f8f9fa;
            border-top: 1px solid #dadce0;
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 16, 20, 16)
        input_layout.setSpacing(12)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(120)
        self.message_input.setFont(QFont("", 13))
        self.message_input.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                border: 2px solid #dadce0;
                border-radius: 10px;
                background-color: white;
                font-size: 14px;
                color: #3c4043;
            }
            QTextEdit:focus {
                border-color: #1a73e8;
                outline: none;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(120, 44)
        self.send_button.setFont(QFont("", 12, QFont.Weight.DemiBold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0066CC, stop: 1 #00A86B
                );
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
            QPushButton:disabled {
                background-color: #CCC;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        chat_layout.addWidget(input_container)
        
        splitter.addWidget(chat_container)
        splitter.setSizes([260, 640])
        
        main_layout.addWidget(splitter)
    
    def setup_menubar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #E0E0E0;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #F0F0F0;
            }
        """)
        
        file_menu = menubar.addMenu("File")
        
        new_chat = QAction("New Chat", self)
        new_chat.setShortcut("Ctrl+N")
        new_chat.triggered.connect(self.new_chat)
        file_menu.addAction(new_chat)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_data(self):
        try:
            self.api_client = get_api_client()
            self.db = get_database()
            self.refresh_sessions()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to initialize: {e}\n\nPlease configure your API key in Settings."
            )
            self.show_settings()
    
    def refresh_sessions(self):
        if self.db:
            try:
                sessions = self.db.get_all_sessions()
                self.sidebar.update_sessions(sessions)
            except Exception as e:
                print(f"Error loading sessions: {e}")
    
    def load_session(self, session_id: str):
        if not self.db:
            return
            
        try:
            session = self.db.get_session(session_id)
            if session:
                self.current_session_id = session.id
                raw_messages = self.db.get_messages(session_id)
                self.messages = [{"role": m.role, "content": m.content} for m in raw_messages]
                self.update_chat_display()
                
                idx = self.model_combo.findText(session.model)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load session: {e}")
    
    def update_chat_display(self):
        self.chat_widget.clear()
        
        for msg in self.messages:
            self.chat_widget.add_message(msg["role"], msg["content"])
    
    def send_message(self):
        content = self.message_input.toPlainText().strip()
        if not content:
            return
            
        if not self.api_client:
            QMessageBox.warning(self, "Warning", "Please configure your API key first.")
            self.show_settings()
            return
        
        self.chat_widget.add_message("user", content)
        self.message_input.clear()
        
        messages = [msg for msg in self.messages]
        messages.append({"role": "user", "content": content})
        
        model = self.model_combo.currentText()
        temperature = 0.7
        max_tokens = 4096
        
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")
        
        messages_tuples = [(msg["role"], msg["content"]) for msg in messages]
        
        self.worker = ChatWorker(
            self.api_client, messages_tuples, model, temperature, max_tokens
        )
        self.worker.finished.connect(self.on_response_finished)
        self.worker.error.connect(self.on_response_error)
        self.worker.start()
    
    @pyqtSlot(str)
    def on_response_finished(self, content: str):
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
        
        self.chat_widget.add_message("assistant", content)
        self.messages.append({"role": "assistant", "content": content})
        
        if self.current_session_id and self.db:
            try:
                self.db.create_message(
                    self.current_session_id, "assistant", content, None
                )
            except Exception as e:
                print(f"Error saving message: {e}")
    
    @pyqtSlot(str)
    def on_response_error(self, error: str):
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
        QMessageBox.critical(self, "API Error", f"Failed to get response: {error}")
    
    def new_chat(self):
        if not self.db:
            return
            
        try:
            session = self.db.create_session("New Chat", self.model_combo.currentText())
            self.current_session_id = session.id
            self.messages = []
            self.chat_widget.clear()
            self.refresh_sessions()
            self.sidebar.select_session(session.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new chat: {e}")
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
    
    def show_about(self):
        QMessageBox.about(
            self, "About NanoGPT Chat",
            "<h2 style='color: #0066CC;'>NanoGPT Chat</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A beautiful Linux desktop AI chat application.</p>"
            "<p>Built with Rust and PyQt6</p>"
            "<p style='color: #888; margin-top: 16px;'>Powered by NanoGPT API</p>"
        )
    
    def closeEvent(self, event):
        event.accept()
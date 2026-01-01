import asyncio
from typing import Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QComboBox, QLabel, QLineEdit, QFrame, QScrollArea,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QSlider,
    QGroupBox, QSizePolicy, QApplication, QDoubleSpinBox,
    QCompleter
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
                self.model, self.messages, self.temperature, self.max_tokens
            )
            
            if response:
                self.finished.emit(response)
            else:
                self.error.emit("Empty response from API")
                
        except Exception as e:
            self.error.emit(str(e))


class ModelFetchWorker(QThread):
    models_fetched = pyqtSignal(list)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        
    def run(self):
        try:
            models = self.api_client.list_models()
            if models:
                self.models_fetched.emit(models)
        except Exception as e:
            print(f"Background model fetch failed: {e}")


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
        self.sidebar.settings_requested.connect(self.show_settings)
        splitter.addWidget(self.sidebar)
        
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        model_toolbar = QWidget()
        model_toolbar.setStyleSheet("""
            background-color: #252526;
            border-bottom: 1px solid #333333;
        """)
        model_layout = QVBoxLayout(model_toolbar)
        model_layout.setContentsMargins(20, 12, 20, 12)
        model_layout.setSpacing(8)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        model_label = QLabel("Model:")
        model_label.setFont(QFont("", 11))
        model_label.setStyleSheet("color: #aaaaaa;")
        top_row.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(180)
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        self.model_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.model_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                font-size: 13px;
                min-width: 150px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
            QComboBox:focus {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #cccccc;
                selection-background-color: #007acc;
            }
        """)
        top_row.addWidget(self.model_combo)
        
        temp_label = QLabel("Temp:")
        temp_label.setFont(QFont("", 11))
        temp_label.setStyleSheet("color: #aaaaaa; margin-left: 10px;")
        top_row.addWidget(temp_label)
        
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 6px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
        """)
        self.temp_spin.valueChanged.connect(self.on_params_changed)
        top_row.addWidget(self.temp_spin)
        
        top_row.addStretch()
        model_layout.addLayout(top_row)
        
        prompt_row = QHBoxLayout()
        prompt_label = QLabel("System:")
        prompt_label.setFont(QFont("", 11))
        prompt_label.setStyleSheet("color: #aaaaaa;")
        prompt_row.addWidget(prompt_label)
        
        self.system_prompt_input = QLineEdit()
        self.system_prompt_input.setPlaceholderText("Enter system prompt for this chat...")
        self.system_prompt_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        self.system_prompt_input.textChanged.connect(self.on_params_changed)
        prompt_row.addWidget(self.system_prompt_input)
        model_layout.addLayout(prompt_row)
        
        chat_layout.addWidget(model_toolbar)
        
        self.chat_widget = ChatWidget()
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)
        chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(chat_scroll)
        
        input_container = QWidget()
        input_container.setFixedHeight(60)
        input_container.setStyleSheet("""
            background-color: #252526;
            border-top: 1px solid #333333;
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(12, 0, 12, 0)
        input_layout.setSpacing(0)
        
        # Combined input area
        input_bar = QFrame()
        input_bar.setFixedHeight(36)
        input_bar.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #3c3c3c;
                border-radius: 12px;
            }
            QFrame:focus-within {
                border-color: #007acc;
            }
        """)
        input_bar_layout = QHBoxLayout(input_bar)
        input_bar_layout.setContentsMargins(12, 0, 8, 0)
        input_bar_layout.setSpacing(0)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setFont(QFont("", 13))
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                color: #cccccc;
                padding: 6px 0px;
            }
        """)
        input_bar_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(64, 28)
        self.send_button.setFont(QFont("", 9, QFont.Weight.DemiBold))
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
                background-color: #555;
                color: #888;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_bar_layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        input_layout.addWidget(input_bar)
        chat_layout.addWidget(input_container)
        
        splitter.addWidget(chat_container)
        splitter.setSizes([260, 640])
        
        main_layout.addWidget(splitter)
    
    def setup_menubar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #252526;
                color: #cccccc;
                border-bottom: 1px solid #333333;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3e3e3e;
            }
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #454545;
            }
            QMenu::item:selected {
                background-color: #094771;
                color: white;
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
            from nanogpt_chat.utils import get_settings
            settings = get_settings()
            
            self.api_client = get_api_client()
            self.db = get_database()
            self.refresh_sessions()
            
            # Populate models from cache
            cached_models = settings.get("api", "cached_models", [])
            if cached_models:
                self.model_combo.blockSignals(True)
                self.model_combo.clear()
                self.model_combo.addItems(sorted(cached_models))
                
                # Apply default model from settings
                default_model = settings.get("api", "default_model")
                idx = self.model_combo.findText(default_model)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
                self.model_combo.blockSignals(False)
            
            # Fetch fresh models in the background
            if self.api_client:
                self.model_worker = ModelFetchWorker(self.api_client)
                self.model_worker.models_fetched.connect(self.on_models_fetched)
                self.model_worker.start()
                
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to initialize: {e}\n\nPlease configure your API key in Settings."
            )
            self.show_settings()
            
    def on_models_fetched(self, models):
        from nanogpt_chat.utils import get_settings
        settings = get_settings()
        settings.set("api", "cached_models", models)
        
        self.model_combo.blockSignals(True)
        current = self.model_combo.currentText()
        self.model_combo.clear()
        self.model_combo.addItems(sorted(models))
        
        idx = self.model_combo.findText(current)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setEditText(current)
        self.model_combo.blockSignals(False)
    
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
                
                # Update UI controls from session data
                self.model_combo.blockSignals(True)
                self.temp_spin.blockSignals(True)
                self.system_prompt_input.blockSignals(True)
                
                idx = self.model_combo.findText(session.model)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
                else:
                    self.model_combo.setEditText(session.model)
                    
                self.temp_spin.setValue(session.temperature)
                self.system_prompt_input.setText(session.system_prompt)
                
                self.model_combo.blockSignals(False)
                self.temp_spin.blockSignals(False)
                self.system_prompt_input.blockSignals(False)
                
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
        
        # Prepare messages including system prompt if it exists
        messages = []
        system_prompt = self.system_prompt_input.text().strip()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        for msg in self.messages:
            messages.append(msg)
        messages.append({"role": "user", "content": content})
        
        model = self.model_combo.currentText()
        temperature = float(self.temp_spin.value())
        
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")
        
        from nanogpt_chat.utils import get_settings
        settings = get_settings()
        max_tokens = settings.get("api", "max_tokens", 4096)
        
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
    
    def on_model_changed(self, index):
        if self.current_session_id and self.db:
            model = self.model_combo.currentText()
            try:
                self.db.update_session_model(self.current_session_id, model)
            except Exception as e:
                print(f"Error updating session model: {e}")
    
    def on_params_changed(self):
        if self.current_session_id and self.db:
            system_prompt = self.system_prompt_input.text()
            temperature = float(self.temp_spin.value())
            try:
                self.db.update_session_params(self.current_session_id, system_prompt, temperature)
            except Exception as e:
                print(f"Error updating session params: {e}")
    
    def new_chat(self):
        if not self.db:
            return
            
        try:
            from nanogpt_chat.utils import get_settings
            settings = get_settings()
            
            # Use default model from settings
            default_model = settings.get("api", "default_model", "gpt-4o")
            default_system = settings.get("api", "default_system_prompt", "You are a helpful assistant.")
            default_temp = settings.get("api", "temperature", 0.7)
            
            session = self.db.create_session("New Chat", default_model, default_system, default_temp)
            self.current_session_id = session.id
            self.messages = []
            self.chat_widget.clear()
            
            # Update UI controls for the new session
            self.model_combo.blockSignals(True)
            self.system_prompt_input.blockSignals(True)
            self.temp_spin.blockSignals(True)
            
            idx = self.model_combo.findText(default_model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
            else:
                self.model_combo.setEditText(default_model)
                
            self.system_prompt_input.setText(default_system)
            self.temp_spin.setValue(default_temp)
            
            self.model_combo.blockSignals(False)
            self.system_prompt_input.blockSignals(False)
            self.temp_spin.blockSignals(False)
            
            self.refresh_sessions()
            self.sidebar.select_session(session.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new chat: {e}")
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            from nanogpt_chat.utils import get_settings
            settings = get_settings()
            
            # Update model list in main window
            current_model = self.model_combo.currentText()
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            
            # Fetch all models from settings (which are saved there now)
            # Actually we need to make sure models are persisted or re-fetched
            # Let's just re-apply the logic from load_data
            self.load_data()
            self.model_combo.blockSignals(False)
    
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
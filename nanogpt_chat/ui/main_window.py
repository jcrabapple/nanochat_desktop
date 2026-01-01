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
    chunk_received = pyqtSignal(str)
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
            full_response = ""
            for chunk in self.api_client.chat_completion_stream(
                self.model, self.messages, self.temperature, self.max_tokens
            ):
                full_response += chunk
                self.chunk_received.emit(full_response)
            
            if full_response:
                self.finished.emit(full_response)
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
        self.sidebar.session_deleted.connect(self.delete_session)
        self.sidebar.new_chat.connect(self.new_chat)
        self.sidebar.settings_requested.connect(self.show_settings)
        splitter.addWidget(self.sidebar)
        
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        model_toolbar = QWidget()
        model_toolbar.setStyleSheet("""
            background-color: #171717;
            border-bottom: 1px solid #262626;
        """)
        model_layout = QHBoxLayout(model_toolbar)
        model_layout.setContentsMargins(20, 8, 20, 8)
        model_layout.setSpacing(12)
        
        # Model Selector
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.model_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.model_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        
        # Style the combo box to look like a pill itself
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #262626;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox:hover {
                border-color: #444444;
                background-color: #2d2d2d;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #888888;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #262626;
                color: #e0e0e0;
                selection-background-color: #007acc;
                border: 1px solid #333;
                outline: none;
            }
            QComboBox QLineEdit {
                background: transparent;
                color: #e0e0e0;
                border: none;
            }
        """)
        model_layout.addWidget(self.model_combo)
        
        # Temperature Pill
        temp_pill = QFrame()
        temp_pill.setStyleSheet("""
            QFrame {
                background-color: #262626;
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)
        temp_pill_layout = QHBoxLayout(temp_pill)
        temp_pill_layout.setContentsMargins(10, 2, 10, 2)
        temp_pill_layout.setSpacing(6)
        
        temp_icon = QLabel("🌡️")
        temp_icon.setStyleSheet("border: none; background: transparent;")
        temp_pill_layout.addWidget(temp_icon)
        
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setFixedWidth(40)
        self.temp_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: none;
                background-color: transparent;
                color: #e0e0e0;
                font-size: 13px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; }
        """)
        self.temp_spin.valueChanged.connect(self.on_params_changed)
        temp_pill_layout.addWidget(self.temp_spin)
        model_layout.addWidget(temp_pill)
        
        # System Prompt Button Pill
        prompt_pill = QFrame()
        prompt_pill.setStyleSheet("""
            QFrame {
                background-color: #262626;
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)
        prompt_pill_layout = QHBoxLayout(prompt_pill)
        prompt_pill_layout.setContentsMargins(4, 2, 4, 2)
        
        self.system_prompt_btn = QPushButton("📝 System Prompt")
        self.system_prompt_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #e0e0e0;
                font-size: 13px;
                padding: 6px 12px;
                text-align: left;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        self.system_prompt_btn.clicked.connect(self.edit_system_prompt)
        prompt_pill_layout.addWidget(self.system_prompt_btn)
        model_layout.addWidget(prompt_pill)
        
        # Internal hidden field to keep the text
        self.system_prompt_input = QLineEdit()
        self.system_prompt_input.setVisible(False)
        self.system_prompt_input.textChanged.connect(self.on_params_changed)
        
        model_layout.addStretch()
        chat_layout.addWidget(model_toolbar)
        
        self.chat_widget = ChatWidget()
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #171717;
            }
            QScrollBar:vertical {
                border: none;
                background: #171717;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2f2f2f;
                min-height: 20px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3f3f3f;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(chat_scroll)
        
        input_container = QWidget()
        input_container.setFixedHeight(64) # Further reduced height
        input_container.setStyleSheet("""
            background-color: #171717;
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 12) # Lowered position
        input_layout.setSpacing(0)
        
        # Centered input bar like ChatGPT
        input_centering_layout = QHBoxLayout()
        input_centering_layout.addStretch()
        
        input_bar = QFrame()
        input_bar.setFixedWidth(700)
        input_bar.setFixedHeight(52)
        input_bar.setStyleSheet("""
            QFrame {
                background-color: #2f2f2f;
                border: 1px solid #3f3f3f;
                border-radius: 26px;
            }
            QFrame:focus-within {
                border-color: #676767;
            }
        """)
        input_bar_layout = QHBoxLayout(input_bar)
        input_bar_layout.setContentsMargins(20, 0, 12, 0)
        input_bar_layout.setSpacing(0)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Message NanoGPT...")
        self.message_input.setFont(QFont("", 13))
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 15px;
                color: #ffffff;
                padding: 14px 0px;
            }
        """)
        # Install event filter for Enter key
        self.message_input.installEventFilter(self)
        input_bar_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton()
        self.send_button.setFixedSize(32, 32)
        # Use an arrow-like styling for the send button
        self.send_button.setText("↑")
        self.send_button.setFont(QFont("", 16, QFont.Weight.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #d7d7d7;
            }
            QPushButton:pressed {
                background-color: #b7b7b7;
            }
            QPushButton:disabled {
                background-color: #3f3f3f;
                color: #676767;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_bar_layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        input_centering_layout.addWidget(input_bar)
        input_centering_layout.addStretch()
        
        input_layout.addLayout(input_centering_layout)
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
            
            # Start fresh with a new chat on every launch
            self.new_chat()
                
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
        
        # Auto-start new chat on first run if no sessions exist
        if not self.current_session_id and not self.sidebar.session_list.count():
            self.new_chat()
    
    def refresh_sessions(self):
        if self.db:
            try:
                sessions = self.db.get_all_sessions()
                self.sidebar.update_sessions(sessions)
            except Exception as e:
                print(f"Error loading sessions: {e}")
    
    def delete_session(self, session_id: str):
        if not self.db:
            return
            
        reply = QMessageBox.question(
            self, "Delete Chat",
            "Are you sure you want to delete this chat history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_session(session_id)
                if self.current_session_id == session_id:
                    self.current_session_id = None
                    self.messages = []
                    self.chat_widget.clear()
                    self.new_chat()
                else:
                    self.refresh_sessions()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete session: {e}")
    
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
        
        # Immediate UI Update
        self.chat_widget.add_message("user", content)
        self.message_input.clear()
        self.send_button.setEnabled(False)
        QApplication.processEvents()
        
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
        
        from nanogpt_chat.utils import get_settings
        settings = get_settings()
        max_tokens = settings.get("api", "max_tokens", 4096)
        
        messages_tuples = [(msg["role"], msg["content"]) for msg in messages]
        self.worker = ChatWorker(
            self.api_client, messages_tuples, model, temperature, max_tokens
        )
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.finished.connect(self.on_response_finished)
        self.worker.error.connect(self.on_response_error)
        self.worker.start()
    
    @pyqtSlot(str)
    def on_chunk_received(self, content: str):
        self.chat_widget.add_message("assistant", content, is_stream=True)
    
    @pyqtSlot(str)
    def on_response_finished(self, content: str):
        self.send_button.setEnabled(True)
        # Fix: Assistant message was already added/updated during streaming
        # Just update the local message list and database
        
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
        # Fix: Button remains an icon
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
    
    def eventFilter(self, obj, event):
        if hasattr(self, 'message_input') and obj is self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def edit_system_prompt(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(
            self, "System Prompt",
            "Enter instructions for the AI assistant:",
            self.system_prompt_input.text()
        )
        if ok:
            self.system_prompt_input.setText(text)
            
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
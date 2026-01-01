import asyncio
from typing import Optional
from datetime import datetime
import base64
import json

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QComboBox, QLabel, QLineEdit, QFrame, QScrollArea,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QSlider,
    QGroupBox, QSizePolicy, QApplication, QDoubleSpinBox,
    QCompleter, QDialogButtonBox, QFileDialog, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot, QDateTime, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCursor, QAction, QIcon

from nanogpt_chat.ui.chat_widget import ChatWidget
from nanogpt_chat.ui.settings_dialog import SettingsDialog
from nanogpt_chat.ui.sidebar import Sidebar
from nanogpt_chat.utils import get_api_client, get_database

class ChatWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    usage_received = pyqtSignal(dict)
    
    def __init__(self, api_client, messages, model, temperature, max_tokens, 
                 top_p=None, frequency_penalty=None, presence_penalty=None):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self._is_terminated = False
    
    def terminate(self):
        self._is_terminated = True
        super().terminate()
    
    def run(self):
        try:
            full_response = ""
            
            # Fallback for binary version mismatch
            try:
                # Try new signature (7 arguments)
                stream = self.api_client.chat_completion_stream(
                    self.model, self.messages, self.temperature, self.max_tokens,
                    self.top_p, self.frequency_penalty, self.presence_penalty
                )
            except TypeError:
                # Fallback to old signature (3 arguments)
                stream = self.api_client.chat_completion_stream(
                    self.model, self.messages, self.temperature
                )

            for chunk in stream:
                if self._is_terminated:
                    return
                full_response += chunk
                self.chunk_received.emit(full_response)
            
            if self._is_terminated:
                return
                
            if full_response:
                self.finished.emit(full_response)
            else:
                self.error.emit("Empty response from API")
                
        except Exception as e:
            if not self._is_terminated:
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
            from nanogpt_chat.utils.logger import logger
            logger.error(f"Background model fetch failed: {e}")

class MessageEditDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Message")
        self.resize(500, 300)
        self.setup_ui(content)
    
    def setup_ui(self, content):
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_content(self):
        return self.text_edit.toPlainText()

class AdvancedSettingsDialog(QDialog):
    def __init__(self, top_p, frequency_penalty, presence_penalty, max_tokens, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Model Settings")
        self.resize(400, 450)
        self.top_p = top_p if top_p is not None else 1.0
        self.frequency_penalty = frequency_penalty if frequency_penalty is not None else 0.0
        self.presence_penalty = presence_penalty if presence_penalty is not None else 0.0
        self.max_tokens = max_tokens if max_tokens is not None else 4096
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Top-p
        tp_group = QGroupBox("Top-p")
        tp_layout = QVBoxLayout(tp_group)
        self.tp_slider = QSlider(Qt.Orientation.Horizontal)
        self.tp_slider.setRange(0, 100)
        self.tp_slider.setValue(int(self.top_p * 100))
        self.tp_label = QLabel(f"Value: {self.top_p:.2f}")
        self.tp_slider.valueChanged.connect(lambda v: self.tp_label.setText(f"Value: {v/100:.2f}"))
        tp_layout.addWidget(self.tp_slider)
        tp_layout.addWidget(self.tp_label)
        layout.addWidget(tp_group)
        
        # Frequency Penalty
        fp_group = QGroupBox("Frequency Penalty")
        fp_layout = QVBoxLayout(fp_group)
        self.fp_slider = QSlider(Qt.Orientation.Horizontal)
        self.fp_slider.setRange(-200, 200)
        self.fp_slider.setValue(int(self.frequency_penalty * 100))
        self.fp_label = QLabel(f"Value: {self.frequency_penalty:.2f}")
        self.fp_slider.valueChanged.connect(lambda v: self.fp_label.setText(f"Value: {v/100:.2f}"))
        fp_layout.addWidget(self.fp_slider)
        fp_layout.addWidget(self.fp_label)
        layout.addWidget(fp_group)
        
        # Max Tokens
        mt_group = QGroupBox("Max Tokens")
        mt_layout = QVBoxLayout(mt_group)
        self.mt_spin = QSpinBox()
        self.mt_spin.setRange(1, 128000)
        self.mt_spin.setValue(self.max_tokens)
        mt_layout.addWidget(self.mt_spin)
        layout.addWidget(mt_group)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_top_p(self): return self.tp_slider.value() / 100.0
    def get_frequency_penalty(self): return self.fp_slider.value() / 100.0
    def get_presence_penalty(self): return 0.0 
    def get_max_tokens(self): return self.mt_spin.value()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoGPT Chat")
        
        from nanogpt_chat.utils import get_settings
        settings = get_settings()
        self.resize(settings.get("ui", "window_width", 900), settings.get("ui", "window_height", 650))
        
        self.current_session_id = None
        self.messages = []
        self.available_models = [] # Initialize
        self.api_client = None
        self.db = None
        
        # Advanced settings
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        self.max_tokens_setting = 4096
        
        # Offline queue
        self.message_queue = []
        try:
            from nanogpt_chat.utils.connectivity import monitor
            monitor.status_changed.connect(self.on_connectivity_changed)
            monitor.start()
        except ImportError:
            pass
            
        self.setup_ui()
        self.setup_menubar()
        self.load_data()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(260)
        self.sidebar.session_selected.connect(self.load_session)
        self.sidebar.session_deleted.connect(self.delete_session)
        self.sidebar.session_renamed.connect(self.rename_session)
        self.sidebar.search_requested.connect(self.search_sessions)
        self.sidebar.load_more_requested.connect(self.load_more_sessions)
        self.sidebar.new_chat.connect(self.new_chat)
        self.sidebar.settings_requested.connect(self.show_settings)
        splitter.addWidget(self.sidebar)
        
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333;")
        t_layout = QHBoxLayout(toolbar)
        t_layout.setContentsMargins(15, 0, 15, 0)
        t_layout.setSpacing(10)
        
        # Model Label and Picker
        model_label = QLabel("Model:")
        model_label.setStyleSheet("font-weight: bold; color: #888;")
        t_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        t_layout.addWidget(self.model_combo)
        
        t_layout.addStretch()
        
        # Temp Label and Spinner
        temp_label = QLabel("Temp:")
        temp_label.setStyleSheet("font-weight: bold; color: #888;")
        t_layout.addWidget(temp_label)
        
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0, 2)
        self.temp_spin.setValue(0.7)
        self.temp_spin.setSingleStep(0.05)
        self.temp_spin.setDecimals(2)
        self.temp_spin.setFixedWidth(65)
        self.temp_spin.valueChanged.connect(self.on_params_changed)
        t_layout.addWidget(self.temp_spin)
        
        self.adv_btn = QPushButton()
        self.adv_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.adv_btn.setFixedSize(30, 30)
        self.adv_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: 1px solid #444;
                border-radius: 15px;
                color: #aaa;
            }
            QPushButton:hover {
                background-color: #444;
                color: #fff;
            }
        """)
        self.adv_btn.clicked.connect(self.show_advanced_settings)
        t_layout.addWidget(self.adv_btn)
        
        chat_layout.addWidget(toolbar)
        
        # Chat area
        self.chat_widget = ChatWidget()
        self.chat_widget.edit_requested.connect(self.edit_message_requested)
        self.chat_widget.regenerate_requested.connect(self.regenerate_message_requested)
        self.chat_widget.delete_requested.connect(self.delete_message_requested)
        
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setWidget(self.chat_widget)
        self.chat_scroll.verticalScrollBar().valueChanged.connect(self.on_chat_scroll)
        chat_layout.addWidget(self.chat_scroll)
        
        # Input area
        input_frame = QFrame()
        input_frame.setFixedHeight(80)
        i_layout = QHBoxLayout(input_frame)
        i_layout.setContentsMargins(10, 10, 10, 10)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.installEventFilter(self)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 8px;
                color: #eee;
            }
        """)
        i_layout.addWidget(self.message_input)
        
        self.image_button = QPushButton("+")
        self.image_button.setFixedSize(32, 32)
        self.image_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: none;
                border-radius: 16px;
                font-size: 20px;
                font-weight: bold;
                color: #aaa;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: #444;
                color: #fff;
            }
        """)
        self.image_button.clicked.connect(self.attach_image)
        i_layout.addWidget(self.image_button)
        
        self.send_button = QPushButton("↑")
        self.send_button.setFixedSize(32, 32) # Fixed, reasonable size
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #008be5;
            }
            QPushButton:disabled {
                background-color: #222;
                color: #555;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        i_layout.addWidget(self.send_button)
        
        self.stop_button = QPushButton("⬛")
        self.stop_button.setFixedSize(32, 32) # Fixed, reasonable size
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                border: none;
                border-radius: 16px;
                font-size: 14px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #ee0000;
            }
        """)
        self.stop_button.clicked.connect(self.stop_generation)
        self.stop_button.hide()
        i_layout.addWidget(self.stop_button)
        
        chat_layout.addWidget(input_frame)
        splitter.addWidget(chat_container)
        layout.addWidget(splitter)

    def setup_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        
        new_act = QAction("New Chat", self)
        new_act.triggered.connect(self.new_chat)
        file_menu.addAction(new_act)
        
        exp_menu = file_menu.addMenu("Export")
        for fmt in ["markdown", "json", "html"]:
            act = QAction(f"Export as {fmt.upper()}", self)
            act.triggered.connect(lambda checked, f=fmt: self.export_conversation(f))
            exp_menu.addAction(act)
            
        view_menu = menu.addMenu("View")
        theme_menu = view_menu.addMenu("Theme")
        for t in ["light", "dark", "system"]:
            act = QAction(t.capitalize(), self)
            act.triggered.connect(lambda checked, name=t: self.set_theme(name))
            theme_menu.addAction(act)

    def load_data(self):
        try:
            self.api_client = get_api_client()
            self.db = get_database()
            
            # Load default settings and apply to UI
            from nanogpt_chat.utils import get_settings
            settings = get_settings()
            default_model = settings.get("api", "default_model", "gpt-4o")
            default_temp = settings.get("api", "temperature", 0.7)
            default_system = settings.get("api", "default_system_prompt", "You are a helpful assistant.")
            
            self.model_combo.setCurrentText(default_model)
            self.temp_spin.setValue(default_temp)
            self.current_system_prompt = default_system
            
            self.refresh_sessions()
            self.new_chat() # This will create a session with the defaults we just set
            
            if self.api_client:
                self.model_worker = ModelFetchWorker(self.api_client)
                self.model_worker.models_fetched.connect(self.on_models_fetched)
                self.model_worker.start()
        except Exception as e:
            from nanogpt_chat.utils.logger import logger
            logger.error(f"Load data error: {e}")

    def on_models_fetched(self, models):
        self.available_models = models # Store for settings dialog
        
        # Save current selection if any
        current = self.model_combo.currentText()
        
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(sorted(models))
        
        # Priority: 1. Current selection, 2. Default from settings
        from nanogpt_chat.utils import get_settings
        settings = get_settings()
        default_model = settings.get("api", "default_model", "gpt-4o")
        
        target = current if current else default_model
        idx = self.model_combo.findText(target)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setEditText(target)
            
        self.model_combo.blockSignals(False)

    def refresh_sessions(self):
        if self.db:
            try:
                if hasattr(self.db, 'get_sessions_paginated'):
                    sessions = self.db.get_sessions_paginated(50, 0)
                else:
                    sessions = self.db.get_all_sessions()
                self.sidebar.update_sessions(sessions)
            except Exception as e:
                from nanogpt_chat.utils.logger import logger
                logger.error(f"Refresh sessions error: {e}")

    def load_session(self, session_id):
        if not self.db: return
        try:
            session = self.db.get_session(session_id)
            if session:
                self.current_session_id = session.id
                if hasattr(self.db, 'get_messages_paginated'):
                    raw = self.db.get_messages_paginated(session_id, 50, 0)
                else:
                    raw = self.db.get_messages(session_id)
                
                self.messages = [{"role": m.role, "content": m.content} for m in raw]
                
                # Store counts for pagination
                all_msgs = self.db.get_messages(session_id)
                self.total_message_count = len(all_msgs)
                self.loaded_message_count = len(raw)
                self.message_offset = len(raw)
                
                self.update_chat_display()
        except Exception as e:
            from nanogpt_chat.utils.logger import logger
            logger.error(f"Load session error: {e}")

    def update_chat_display(self):
        self.chat_widget.clear()
        for msg in self.messages:
            self.chat_widget.add_message(msg["role"], msg["content"])

    def send_message(self):
        content = self.message_input.toPlainText().strip()
        if not content: return
        
        # Check connectivity
        try:
            from nanogpt_chat.utils.connectivity import monitor
            if not monitor.is_online:
                from nanogpt_chat.utils.logger import logger
                logger.info(f"User is offline. Queueing message.")
                self.message_queue.append(content)
                self.chat_widget.add_message("user", f"[Offline Queue] {content}")
                self.message_input.clear()
                return
        except ImportError:
            pass

        # Auto-title
        if not self.messages and self.current_session_id:
            title = content[:50]
            if hasattr(self.db, 'update_session_title'):
                try:
                    self.db.update_session_title(self.current_session_id, title)
                    self.refresh_sessions()
                except Exception as e:
                    from nanogpt_chat.utils.logger import logger
                    logger.error(f"Auto-title error: {e}")
            
        self.chat_widget.add_message("user", content)
        self.messages.append({"role": "user", "content": content})
        self.message_input.clear()
        
        # Defer worker start to allow UI to update
        QTimer.singleShot(10, lambda: self._start_chat_worker(self.messages))

    def _start_chat_worker(self, messages):
        model = self.model_combo.currentText()
        temp = float(self.temp_spin.value())
        
        # Pre-convert messages to avoid blocking UI
        messages_to_send = [(m["role"], m["content"]) for m in messages]
            
        self.worker = ChatWorker(
            self.api_client, messages_to_send, model, temp, self.max_tokens_setting,
            self.top_p, self.frequency_penalty, self.presence_penalty
        )
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.finished.connect(self.on_response_finished)
        self.worker.error.connect(self.on_response_error)
        self.worker.start()
        
        self.chat_widget.show_typing_indicator()
        self.send_button.hide()
        self.stop_button.show()

    def on_chunk_received(self, chunk):
        self.chat_widget.hide_typing_indicator()
        self.chat_widget.add_message("assistant", chunk, is_stream=True)

    def on_response_finished(self, content):
        self.messages.append({"role": "assistant", "content": content})
        if self.current_session_id:
            self.db.create_message(self.current_session_id, "assistant", content, None)
        self.send_button.show()
        self.stop_button.hide()

    def on_response_error(self, err):
        from nanogpt_chat.utils.logger import logger
        logger.error(f"API Error: {err}")
        QMessageBox.critical(self, "Error", str(err))
        self.send_button.show()
        self.stop_button.hide()

    def stop_generation(self):
        if hasattr(self, 'worker'): self.worker.terminate()
        self.send_button.show()
        self.stop_button.hide()

    def set_theme(self, name):
        from nanogpt_chat.ui.themes import set_theme_mode, ThemeMode, get_app_stylesheet
        mode = {"light": ThemeMode.LIGHT, "dark": ThemeMode.DARK, "system": ThemeMode.SYSTEM}.get(name)
        set_theme_mode(mode)
        self.setStyleSheet(get_app_stylesheet())

    def export_conversation(self, fmt):
        path, _ = QFileDialog.getSaveFileName(self, "Export", f"chat.{fmt}")
        if path:
            with open(path, "w") as f:
                if fmt == "json": json.dump(self.messages, f)
                else: f.write(str(self.messages))

    def show_advanced_settings(self):
        d = AdvancedSettingsDialog(self.top_p, self.frequency_penalty, self.presence_penalty, self.max_tokens_setting, self)
        if d.exec():
            self.top_p = d.get_top_p()
            self.frequency_penalty = d.get_frequency_penalty()
            self.max_tokens_setting = d.get_max_tokens()

    def edit_message_requested(self, role, content):
        d = MessageEditDialog(content, self)
        if d.exec():
            # Logic to resend conversation would go here
            pass

    def regenerate_message_requested(self, role, content):
        pass

    def delete_message_requested(self, role, content):
        pass

    def on_chat_scroll(self, val):
        if val < 50 and not getattr(self, '_loading_messages', False):
            if hasattr(self, 'total_message_count') and self.loaded_message_count < self.total_message_count:
                self.load_more_messages()

    def load_more_messages(self):
        if not self.db or not self.current_session_id: return
        self._loading_messages = True
        try:
            raw = self.db.get_messages_paginated(self.current_session_id, 20, self.message_offset)
            if raw:
                older = [{"role": m.role, "content": m.content} for m in raw]
                self.messages = older + self.messages
                self.loaded_message_count += len(raw)
                self.message_offset += len(raw)
                self.update_chat_display_preserve_position(older)
        finally:
            self._loading_messages = False

    def update_chat_display_preserve_position(self, new_msgs):
        scrollbar = self.chat_scroll.verticalScrollBar()
        old_max = scrollbar.maximum()
        for msg in reversed(new_msgs):
            self.chat_widget.add_message_at_top(msg["role"], msg["content"])
        
        # Use a timer to restore scroll position after layout updates
        def restore_scroll():
            scrollbar.setValue(scrollbar.maximum() - old_max)
        QTimer.singleShot(50, restore_scroll)

    def load_more_sessions(self):
        if self.db and self.sidebar.has_more_sessions:
            sessions = self.db.get_sessions_paginated(50, self.sidebar.current_offset)
            self.sidebar.append_sessions(sessions)

    def rename_session(self, id, title):
        if self.db and hasattr(self.db, 'update_session_title'):
            try:
                self.db.update_session_title(id, title)
                self.refresh_sessions()
            except Exception as e:
                from nanogpt_chat.utils.logger import logger
                logger.error(f"Rename session error: {e}")

    def delete_session(self, id):
        if QMessageBox.question(self, "Delete", "Are you sure?") == QMessageBox.StandardButton.Yes:
            if self.db:
                self.db.delete_session(id)
                self.refresh_sessions()

    def search_sessions(self, q):
        if self.db:
            res = self.db.search_sessions(q)
            self.sidebar.has_more_sessions = False
            self.sidebar.display_sessions(res)

    def new_chat(self):
        if not self.db: return
        try:
            from nanogpt_chat.utils import get_settings
            settings = get_settings()
            model = settings.get("api", "default_model", "gpt-4o")
            system_prompt = settings.get("api", "default_system_prompt", "You are a helpful assistant.")
            temperature = settings.get("api", "temperature", 0.7)
            
            session = self.db.create_session("New Chat", model, system_prompt, temperature)
            self.current_session_id = session.id
            self.messages = []
            self.chat_widget.clear()
            
            # Apply settings to UI
            self.model_combo.setCurrentText(model)
            self.temp_spin.setValue(temperature)
            # Store system prompt for later use
            self.current_system_prompt = system_prompt
            
            self.refresh_sessions()
            self.sidebar.select_session(session.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new chat: {e}")

    def on_connectivity_changed(self, online):
        from nanogpt_chat.utils.logger import logger
        if online:
            logger.info("Connection restored.")
            if self.message_queue:
                self.message_queue.clear()
        else:
            logger.warning("Connection lost.")

    def on_model_changed(self, i):
        if self.current_session_id and self.db:
            self.db.update_session_model(self.current_session_id, self.model_combo.currentText())

    def on_params_changed(self):
        if self.current_session_id and self.db:
            self.db.update_session_params(self.current_session_id, "", float(self.temp_spin.value()))

    def attach_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg)")
        if path:
            if not hasattr(self, 'attached_images'): self.attached_images = []
            self.attached_images.append(path)
            self.message_input.setPlaceholderText(f"Attached: {path.split('/')[-1]}")

    def show_about(self):
        QMessageBox.about(self, "About", "NanoGPT Chat v0.1.0")

    def show_settings(self):
        d = SettingsDialog(self.available_models, self)
        if d.exec(): self.load_data()

    def eventFilter(self, obj, event):
        if obj is self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)


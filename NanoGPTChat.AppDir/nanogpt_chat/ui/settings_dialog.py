from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLabel,
    QMessageBox, QTabWidget, QWidget, QFrame, QTextEdit,
    QCompleter
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QFont, QIcon, QStandardItemModel, QStandardItem


class SettingsDialog(QDialog):
    def __init__(self, available_models=None, parent=None):
        super().__init__(parent)
        self.available_models = available_models or []
        self.setWindowTitle("Settings")
        self.setMinimumWidth(550) # Increased width
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Settings")
        header.setFont(QFont("", 16, QFont.Weight.Bold))
        header.setStyleSheet("""
            padding: 20px 24px;
            background-color: #252526;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 1px solid #333333;
        """)
        layout.addWidget(header)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 13px;
                background-color: #252526;
                color: #888;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:hover {
                background-color: #2d2d2d;
                color: #ccc;
            }
            QTabBar::tab:selected {
                border-bottom: 2px solid #007acc;
                color: #ffffff;
                background-color: #1e1e1e;
            }
        """)
        
        # Shared styles for inputs and buttons
        input_style = """
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 10px;
                border: 1px solid #333333;
                border-radius: 6px;
                background-color: #262626;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #888888;
                width: 0;
                height: 0;
                margin-top: 2px;
            }
        """
        
        button_secondary_style = """
            QPushButton {
                padding: 8px 16px;
                background-color: #333333;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #444444;
                border-color: #555555;
                color: #ffffff;
            }
        """
        
        button_primary_style = """
            QPushButton {
                padding: 8px 24px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #118ad3;
            }
        """
        
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setContentsMargins(30, 30, 30, 30)
        api_layout.setSpacing(20)
        
        api_header = QLabel("API Configuration")
        api_header.setFont(QFont("", 11, QFont.Weight.Bold))
        api_header.setStyleSheet("color: #888; text-transform: uppercase; letter-spacing: 1px;")
        api_layout.addRow(api_header)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Paste your NanoGPT API key here")
        self.api_key_input.setStyleSheet(input_style)
        api_layout.addRow("API Key", self.api_key_input)
        
        api_info = QLabel(
            "Get your key from <a href='https://nano-gpt.com/' style='color: #4fc3f7;'>nano-gpt.com</a>. "
            "It will be stored in your system's secure keyring."
        )
        api_info.setOpenExternalLinks(True)
        api_info.setWordWrap(True)
        api_info.setStyleSheet("color: #777; font-size: 12px; margin-top: -10px;")
        api_layout.addRow("", api_info)
        
        self.test_api_btn = QPushButton("Test Connection")
        self.test_api_btn.setFixedWidth(150)
        self.test_api_btn.setStyleSheet(button_secondary_style)
        self.test_api_btn.clicked.connect(self.test_api)
        api_layout.addRow("", self.test_api_btn)
        
        self.tab_widget.addTab(api_tab, "API")
        
        model_tab = QWidget()
        model_layout = QFormLayout(model_tab)
        model_layout.setContentsMargins(30, 30, 30, 30)
        model_layout.setSpacing(20)
        
        model_header = QLabel("Default Session Defaults")
        model_header.setFont(QFont("", 11, QFont.Weight.Bold))
        model_header.setStyleSheet("color: #888; text-transform: uppercase; letter-spacing: 1px;")
        model_layout.addRow(model_header)
        
        self.default_model = QComboBox()
        self.default_model.setEditable(True)
        self.default_model.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.default_model.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.default_model.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.default_model.setStyleSheet(input_style)
        model_layout.addRow("Default Model", self.default_model)
        
        self.fetch_models_btn = QPushButton("🔄 Fetch All Models")
        self.fetch_models_btn.setFixedWidth(180)
        self.fetch_models_btn.setStyleSheet(button_secondary_style)
        self.fetch_models_btn.clicked.connect(self.fetch_models)
        model_layout.addRow("", self.fetch_models_btn)
        
        self.default_system_prompt = QTextEdit()
        self.default_system_prompt.setMaximumHeight(80)
        self.default_system_prompt.setPlaceholderText("e.g. You are a helpful AI assistant.")
        self.default_system_prompt.setStyleSheet(input_style)
        model_layout.addRow("System Prompt", self.default_system_prompt)
        
        params_layout = QHBoxLayout()
        params_layout.setSpacing(20)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setValue(0.7)
        self.temperature.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        self.temperature.setDecimals(2)
        self.temperature.setStyleSheet(input_style)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 128000)
        self.max_tokens.setValue(4096)
        self.max_tokens.setSuffix(" tokens")
        self.max_tokens.setStyleSheet(input_style)
        
        model_layout.addRow("Temperature", self.temperature)
        model_layout.addRow("Max Tokens", self.max_tokens)
        
        self.tab_widget.addTab(model_tab, "Model")
        
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        appearance_layout.setContentsMargins(30, 30, 30, 30)
        appearance_layout.setSpacing(20)
        
        appearance_header = QLabel("Personalization")
        appearance_header.setFont(QFont("", 11, QFont.Weight.Bold))
        appearance_header.setStyleSheet("color: #888; text-transform: uppercase; letter-spacing: 1px;")
        appearance_layout.addRow(appearance_header)
        
        self.dark_mode = QCheckBox("Enable Dark Theme")
        self.dark_mode.setChecked(True)
        self.dark_mode.setStyleSheet("""
            QCheckBox { color: #e0e0e0; font-size: 13px; spacing: 10px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 1px solid #444; background: #262626; }
            QCheckBox::indicator:checked { background: #007acc; border-color: #007acc; image: none; }
        """)
        appearance_layout.addRow("Interface", self.dark_mode)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(12)
        self.font_size.setSuffix(" pt")
        self.font_size.setStyleSheet(input_style)
        appearance_layout.addRow("Font Size", self.font_size)
        
        self.tab_widget.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(self.tab_widget)
        
        # Bottom Button Row
        bottom_container = QFrame()
        bottom_container.setStyleSheet("background-color: #252526; border-top: 1px solid #333333;")
        button_layout = QHBoxLayout(bottom_container)
        button_layout.setContentsMargins(24, 16, 24, 16)
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(button_secondary_style)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet(button_primary_style)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addWidget(bottom_container)
    
    def fetch_models(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key first.")
            return
            
        self.fetch_models_btn.setEnabled(False)
        self.fetch_models_btn.setText("Fetching...")
        
        try:
            from nanogpt_core import PyNanoGPTClient
            client = PyNanoGPTClient(api_key)
            models = client.list_models()
            
            current_model = self.default_model.currentText()
            self.default_model.clear()
            self.default_model.addItems(sorted(models))
            
            idx = self.default_model.findText(current_model)
            if idx >= 0:
                self.default_model.setCurrentIndex(idx)
            else:
                self.default_model.setEditText(current_model)
            
            QMessageBox.information(self, "Success", f"Fetched {len(models)} models.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch models: {e}")
        finally:
            self.fetch_models_btn.setEnabled(True)
            self.fetch_models_btn.setText("🔄 Fetch All Models")
    
    def load_settings(self):
        try:
            from nanogpt_chat.utils.credentials import SecureCredentialManager
            from nanogpt_chat.utils import get_settings
            
            settings = get_settings()
            api_key = SecureCredentialManager.get_api_key()
            if api_key:
                self.api_key_input.setText(api_key)
            
            # Populate model dropdown if models are provided
            if self.available_models:
                self.default_model.clear()
                self.default_model.addItems(sorted(self.available_models))
            
            # Load model settings
            idx = self.default_model.findText(settings.get("api", "default_model"))
            if idx >= 0:
                self.default_model.setCurrentIndex(idx)
            else:
                self.default_model.setEditText(settings.get("api", "default_model"))
                
            self.default_system_prompt.setPlainText(settings.get("api", "default_system_prompt"))
            self.temperature.setValue(settings.get("api", "temperature"))
            self.max_tokens.setValue(settings.get("api", "max_tokens"))
            
            # Load UI settings
            self.dark_mode.setChecked(settings.get("ui", "dark_mode"))
            self.font_size.setValue(settings.get("ui", "font_size"))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def test_api(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key first.")
            return
        
        try:
            from nanogpt_core import PyNanoGPTClient
            client = PyNanoGPTClient(api_key)
            # Use gpt-4o-mini for a cheap test
            client.chat_completion_sync("gpt-4o-mini", [("user", "hi")], 0.7, 10)
            QMessageBox.information(self, "Success", "API connection successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {e}")
    
    def save_settings(self):
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key.")
            return
        
        try:
            from nanogpt_chat.utils.credentials import SecureCredentialManager
            from nanogpt_chat.utils import get_settings
            
            settings = get_settings()
            
            # Save to keyring
            SecureCredentialManager.set_api_key(api_key)
            
            # Save other settings
            settings.set("api", "default_model", self.default_model.currentText())
            settings.set("api", "default_system_prompt", self.default_system_prompt.toPlainText())
            settings.set("api", "temperature", self.temperature.value())
            settings.set("api", "max_tokens", self.max_tokens.value())
            settings.set("ui", "dark_mode", self.dark_mode.isChecked())
            settings.set("ui", "font_size", self.font_size.value())
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

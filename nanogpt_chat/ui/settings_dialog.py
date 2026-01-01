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
    def __init__(self, parent=None):
        super().__init__(parent)
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
                font-size: 14px;
                background-color: #252526;
                color: #888;
            }
            QTabBar::tab:selected {
                border-bottom: 2px solid #007acc;
                color: #ffffff;
                background-color: #1e1e1e;
            }
        """)
        
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setContentsMargins(24, 24, 24, 24)
        api_layout.setSpacing(16)
        
        api_header = QLabel("API Configuration")
        api_header.setFont(QFont("", 12, QFont.Weight.Bold))
        api_header.setStyleSheet("color: #cccccc;")
        api_layout.addRow(api_header)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your NanoGPT API key")
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                font-size: 14px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
        api_layout.addRow("API Key:", self.api_key_input)
        
        api_info = QLabel(
            "Get your API key from https://nano-gpt.com/\n"
            "Your key is stored securely on your system."
        )
        api_info.setWordWrap(True)
        api_info.setStyleSheet("color: #888; font-size: 12px;")
        api_layout.addRow("", api_info)
        
        self.test_api_btn = QPushButton("Test Connection")
        self.test_api_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        self.test_api_btn.clicked.connect(self.test_api)
        api_layout.addRow("", self.test_api_btn)
        
        self.tab_widget.addTab(api_tab, "API")
        
        model_tab = QWidget()
        model_layout = QFormLayout(model_tab)
        model_layout.setContentsMargins(24, 24, 24, 24)
        model_layout.setSpacing(16)
        
        model_header = QLabel("Model Settings")
        model_header.setFont(QFont("", 12, QFont.Weight.Bold))
        model_header.setStyleSheet("color: #cccccc;")
        model_layout.addRow(model_header)
        
        self.default_model = QComboBox()
        self.default_model.setEditable(True)
        self.default_model.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.default_model.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.default_model.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.default_model.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                font-size: 14px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #cccccc;
                selection-background-color: #007acc;
            }
        """)
        model_layout.addRow("Default Model:", self.default_model)
        
        self.default_system_prompt = QTextEdit()
        self.default_system_prompt.setMaximumHeight(100)
        self.default_system_prompt.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                font-size: 14px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
        """)
        model_layout.addRow("Default System Prompt:", self.default_system_prompt)
        
        self.fetch_models_btn = QPushButton("Fetch Available Models")
        self.fetch_models_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        self.fetch_models_btn.clicked.connect(self.fetch_models)
        model_layout.addRow("", self.fetch_models_btn)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setValue(0.7)
        self.temperature.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        self.temperature.setDecimals(2)
        self.temperature.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
        """)
        model_layout.addRow("Temperature:", self.temperature)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 32768)
        self.max_tokens.setValue(4096)
        self.max_tokens.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
        """)
        model_layout.addRow("Max Tokens:", self.max_tokens)
        
        self.tab_widget.addTab(model_tab, "Model")
        
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        appearance_layout.setContentsMargins(24, 24, 24, 24)
        appearance_layout.setSpacing(16)
        
        appearance_header = QLabel("Appearance")
        appearance_header.setFont(QFont("", 12, QFont.Weight.Bold))
        appearance_header.setStyleSheet("color: #cccccc;")
        appearance_layout.addRow(appearance_header)
        
        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setStyleSheet("""
            QCheckBox {
                padding: 8px;
                font-size: 14px;
                color: #cccccc;
            }
        """)
        appearance_layout.addRow("Theme:", self.dark_mode)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #cccccc;
            }
        """)
        appearance_layout.addRow("Font Size:", self.font_size)
        
        self.tab_widget.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(self.tab_widget)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(24, 20, 24, 20)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background-color: #3c3c3c;
                color: #cccccc;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #118ad3;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
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
            self.fetch_models_btn.setText("Fetch Available Models")
    
    def load_settings(self):
        try:
            from nanogpt_chat.utils.credentials import SecureCredentialManager
            from nanogpt_chat.utils import get_settings
            
            settings = get_settings()
            api_key = SecureCredentialManager.get_api_key()
            if api_key:
                self.api_key_input.setText(api_key)
            
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

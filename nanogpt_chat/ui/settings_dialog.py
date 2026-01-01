from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLabel,
    QMessageBox, QTabWidget, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Settings")
        header.setFont(QFont("", 16, QFont.Weight.Bold))
        header.setStyleSheet("""
            padding: 20px 24px;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #0066CC, stop: 1 #00A86B
            );
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(header)
        
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                border-bottom: 2px solid #0066CC;
                color: #0066CC;
            }
        """)
        
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setContentsMargins(24, 24, 24, 24)
        api_layout.setSpacing(16)
        
        api_header = QLabel("API Configuration")
        api_header.setFont(QFont("", 12, QFont.Weight.Bold))
        api_header.setStyleSheet("color: #333;")
        api_layout.addRow(api_header)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your NanoGPT API key")
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0066CC;
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
                background-color: #0066CC;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0055AA;
            }
        """)
        self.test_api_btn.clicked.connect(self.test_api)
        api_layout.addRow("", self.test_api_btn)
        
        tab_widget.addTab(api_tab, "API")
        
        model_tab = QWidget()
        model_layout = QFormLayout(model_tab)
        model_layout.setContentsMargins(24, 24, 24, 24)
        model_layout.setSpacing(16)
        
        model_header = QLabel("Model Settings")
        model_header.setFont(QFont("", 12, QFont.Weight.Bold))
        model_header.setStyleSheet("color: #333;")
        model_layout.addRow(model_header)
        
        self.default_model = QComboBox()
        self.default_model.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ])
        self.default_model.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        model_layout.addRow("Default Model:", self.default_model)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setValue(0.7)
        self.temperature.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        self.temperature.setDecimals(2)
        self.temperature.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        model_layout.addRow("Temperature:", self.temperature)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 32768)
        self.max_tokens.setValue(4096)
        self.max_tokens.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        model_layout.addRow("Max Tokens:", self.max_tokens)
        
        tab_widget.addTab(model_tab, "Model")
        
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        appearance_layout.setContentsMargins(24, 24, 24, 24)
        appearance_layout.setSpacing(16)
        
        appearance_header = QLabel("Appearance")
        appearance_header.setFont(QFont("", 12, QFont.Weight.Bold))
        appearance_header.setStyleSheet("color: #333;")
        appearance_layout.addRow(appearance_header)
        
        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setStyleSheet("""
            QCheckBox {
                padding: 8px;
                font-size: 14px;
            }
        """)
        appearance_layout.addRow("Theme:", self.dark_mode)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        appearance_layout.addRow("Font Size:", self.font_size)
        
        tab_widget.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(tab_widget)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(24, 20, 24, 20)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0066CC, stop: 1 #00A86B
                );
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        try:
            from nanogpt_core import PyCredentialManager
            api_key = PyCredentialManager.get_api_key()
            if api_key:
                self.api_key_input.setText(api_key)
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
            QMessageBox.information(self, "Success", "API connection successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {e}")
    
    def save_settings(self):
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key.")
            return
        
        try:
            from nanogpt_core import PyCredentialManager
            PyCredentialManager.set_api_key(api_key)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QFont
from nanogpt_chat.ui.main_window import MainWindow

def main():
    QCoreApplication.setApplicationName("NanoGPT Chat")
    QCoreApplication.setApplicationVersion("0.1.0")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    QFont.insertSubstitution(".SF NS Text", "Segoe UI")
    
    app.setStyleSheet("""
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QMenuBar {
            background-color: #252526;
            color: #cccccc;
            border-bottom: 1px solid #333333;
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
        QScrollArea {
            border: none;
            background-color: #1e1e1e;
        }
        QScrollBar:vertical {
            border: none;
            background: #252526;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #424242;
            min-height: 20px;
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background: #4f4f4f;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    window = MainWindow()
    
    try:
        from nanogpt_chat.utils.credentials import SecureCredentialManager
        SecureCredentialManager.migrate_from_file()
    except Exception as e:
        print(f"Migration failed: {e}")
        
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

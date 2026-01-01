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
            background-color: #f8f9fa;
            color: #3c4043;
        }
        QLabel {
            color: #3c4043;
        }
        QMenuBar {
            background-color: #f8f9fa;
            color: #3c4043;
        }
        QMenuBar::item:selected {
            background-color: #e8eaed;
        }
        QMenu {
            background-color: white;
            border: 1px solid #dadce0;
        }
        QMenu::item:selected {
            background-color: #e8f0fe;
            color: #1a73e8;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

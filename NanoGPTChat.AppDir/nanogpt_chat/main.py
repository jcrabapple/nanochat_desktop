import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QFont
from nanogpt_chat.ui.main_window import MainWindow
from nanogpt_chat.ui.themes import get_app_stylesheet, set_theme_mode, ThemeMode
from nanogpt_chat.utils.logger import logger


def main():
    logger.info("Starting NanoGPT Chat...")
    QCoreApplication.setApplicationName("NanoGPT Chat")
    QCoreApplication.setApplicationVersion("0.1.0")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    QFont.insertSubstitution(".SF NS Text", "Segoe UI")
    
    # Set up theme system
    set_theme_mode(ThemeMode.DARK)
    app.setStyleSheet(get_app_stylesheet())
    
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

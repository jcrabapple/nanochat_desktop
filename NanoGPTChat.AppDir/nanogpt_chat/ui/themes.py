from enum import Enum
from typing import Dict, Any


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class Theme:
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors
    
    def get_color(self, key: str, default: str = "#000000") -> str:
        return self.colors.get(key, default)


# Built-in themes
DARK_THEME = Theme("dark", {
    # Main colors
    "background": "#1e1e1e",
    "surface": "#252526",
    "surface_variant": "#2f2f2f",
    "primary": "#007acc",
    "on_primary": "#ffffff",
    "secondary": "#3c3c3c",
    "on_secondary": "#cccccc",
    "error": "#ff4d4d",
    "on_error": "#ffffff",
    
    # Text colors
    "text_primary": "#e0e0e0",
    "text_secondary": "#aaaaaa",
    "text_disabled": "#666666",
    
    # Borders and dividers
    "border": "#333333",
    "divider": "#3c3c3c",
    
    # Message bubbles
    "user_bubble": "#007acc",
    "assistant_bubble": "#2f2f2f",
    "bubble_text": "#ffffff",
    "bubble_text_secondary": "#ececec",
    
    # Scrollbars
    "scrollbar": "#424242",
    "scrollbar_hover": "#4f4f4f",
    
    # Menus
    "menu_background": "#252526",
    "menu_item_hover": "#094771",
})

LIGHT_THEME = Theme("light", {
    # Main colors
    "background": "#ffffff",
    "surface": "#f5f5f5",
    "surface_variant": "#e0e0e0",
    "primary": "#0066cc",
    "on_primary": "#ffffff",
    "secondary": "#e0e0e0",
    "on_secondary": "#333333",
    "error": "#cc0000",
    "on_error": "#ffffff",
    
    # Text colors
    "text_primary": "#212121",
    "text_secondary": "#666666",
    "text_disabled": "#999999",
    
    # Borders and dividers
    "border": "#dddddd",
    "divider": "#e0e0e0",
    
    # Message bubbles
    "user_bubble": "#0066cc",
    "assistant_bubble": "#f0f0f0",
    "bubble_text": "#212121",
    "bubble_text_secondary": "#444444",
    
    # Scrollbars
    "scrollbar": "#c0c0c0",
    "scrollbar_hover": "#a0a0a0",
    
    # Menus
    "menu_background": "#ffffff",
    "menu_item_hover": "#e3f2fd",
})

# Current theme storage
_current_theme = DARK_THEME
_theme_mode = ThemeMode.DARK


def get_current_theme() -> Theme:
    """Get the currently active theme"""
    return _current_theme


def set_theme_mode(mode: ThemeMode):
    """Set the theme mode (light, dark, or system)"""
    global _theme_mode, _current_theme
    
    _theme_mode = mode
    if mode == ThemeMode.LIGHT:
        _current_theme = LIGHT_THEME
    elif mode == ThemeMode.DARK:
        _current_theme = DARK_THEME
    elif mode == ThemeMode.SYSTEM:
        # For simplicity, default to dark in this implementation
        # In a real app, you'd detect system preference
        _current_theme = DARK_THEME


def get_app_stylesheet(theme: Theme = None) -> str:
    """Generate application stylesheet for the given theme"""
    if theme is None:
        theme = get_current_theme()
    
    return f"""
        * {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }}
        QMainWindow {{
            background-color: {theme.get_color('background')};
        }}
        QLabel {{
            background-color: transparent;
            color: {theme.get_color('text_primary')};
        }}
        QMenuBar {{
            background-color: {theme.get_color('surface')};
            color: {theme.get_color('text_primary')};
            border-bottom: 1px solid {theme.get_color('border')};
        }}
        QMenuBar::item:selected {{
            background-color: {theme.get_color('surface_variant')};
        }}
        QMenu {{
            background-color: {theme.get_color('menu_background')};
            color: {theme.get_color('text_primary')};
            border: 1px solid {theme.get_color('border')};
        }}
        QMenu::item:selected {{
            background-color: {theme.get_color('menu_item_hover')};
            color: {theme.get_color('text_primary')};
        }}
        QScrollArea {{
            border: none;
            background-color: {theme.get_color('background')};
        }}
        QScrollBar:vertical {{
            border: none;
            background: {theme.get_color('surface')};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {theme.get_color('scrollbar')};
            min-height: 20px;
            border-radius: 5px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {theme.get_color('scrollbar_hover')};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def get_chat_widget_stylesheet(theme: Theme = None) -> str:
    """Generate chat widget specific stylesheet"""
    if theme is None:
        theme = get_current_theme()
    
    return f"""
        ChatWidget {{
            background-color: {theme.get_color('background')};
        }}
    """


def get_sidebar_stylesheet(theme: Theme = None) -> str:
    """Generate sidebar specific stylesheet"""
    if theme is None:
        theme = get_current_theme()
    
    return f"""
        QWidget {{
            background-color: {theme.get_color('surface')};
            border-right: 1px solid {theme.get_color('border')};
        }}
        QLabel {{
            color: {theme.get_color('text_primary')};
        }}
        QListWidget {{
            border: none;
            background-color: {theme.get_color('surface')};
            color: {theme.get_color('text_primary')};
            outline: none;
        }}
        QListWidget::item {{
            background-color: transparent;
            border-bottom: 1px solid {theme.get_color('divider')};
        }}
        QListWidget::item:hover {{
            background-color: {theme.get_color('surface_variant')};
        }}
        QListWidget::item:selected {{
            background-color: {theme.get_color('secondary')};
        }}
        QLineEdit {{
            background-color: {theme.get_color('surface_variant')};
            color: {theme.get_color('text_primary')};
            border: 1px solid {theme.get_color('border')};
            border-radius: 4px;
        }}
        QLineEdit:focus {{
            border-color: {theme.get_color('primary')};
        }}
        QPushButton {{
            color: {theme.get_color('text_primary')};
        }}
    """
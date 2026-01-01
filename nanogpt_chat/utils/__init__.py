import os
import sys
from pathlib import Path

_package_dir = Path(__file__).parent.parent
if str(_package_dir) not in sys.path:
    sys.path.insert(0, str(_package_dir))

def get_data_dir():
    return Path.home() / ".local" / "share" / "nanogpt-chat"

def get_config_dir():
    return Path.home() / ".config" / "nanogpt-chat"

def get_database_path():
    return get_data_dir() / "chat.db"

from nanogpt_chat.utils.settings import SettingsManager

# Global settings instance
_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = SettingsManager()
    return _settings

def get_api_client():
    try:
        from nanogpt_chat.utils.credentials import SecureCredentialManager
        api_key = SecureCredentialManager.get_api_key()
        if not api_key:
            return None
        from nanogpt_core import PyNanoGPTClient
        return PyNanoGPTClient(api_key)
    except ImportError:
        return None

def get_database():
    try:
        from nanogpt_core import PyDatabase
        db_path = str(get_database_path())
        get_data_dir().mkdir(parents=True, exist_ok=True)
        return PyDatabase(db_path)
    except ImportError:
        return None

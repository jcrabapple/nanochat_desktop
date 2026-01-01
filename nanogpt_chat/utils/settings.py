import toml
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "api": {
        "default_model": "gpt-4o",
        "default_system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
        "max_tokens": 4096,
        "cached_models": [],
    },
    "ui": {
        "dark_mode": True,
        "font_size": 12,
        "window_width": 900,
        "window_height": 650,
    }
}

class SettingsManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "nanogpt-chat"
        self.settings_path = self.config_dir / "settings.toml"
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Load settings from TOML file, creating it with defaults if missing."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r") as f:
                    loaded = toml.load(f)
                    # Deep merge with defaults to handle new keys in updates
                    for section, values in loaded.items():
                        if section in self.settings:
                            self.settings[section].update(values)
                        else:
                            self.settings[section] = values
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            self.save()

    def save(self):
        """Save current settings to TOML file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w") as f:
                toml.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, section, key, default=None):
        """Get a specific setting value."""
        return self.settings.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Set a specific setting value and save."""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()

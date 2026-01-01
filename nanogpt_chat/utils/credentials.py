import keyring
import os
from pathlib import Path

SERVICE_NAME = "nanogpt-chat"
ACCOUNT_NAME = "api_key"

class SecureCredentialManager:
    @staticmethod
    def get_api_key():
        """Retrieve the API key from the system keyring."""
        try:
            return keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        except Exception as e:
            print(f"Error retrieving API key from keyring: {e}")
            return None

    @staticmethod
    def set_api_key(api_key):
        """Store the API key in the system keyring."""
        try:
            keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, api_key)
            return True
        except Exception as e:
            print(f"Error storing API key in keyring: {e}")
            return False

    @staticmethod
    def delete_api_key():
        """Remove the API key from the system keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
            return True
        except Exception as e:
            print(f"Error deleting API key from keyring: {e}")
            return False

    @staticmethod
    def migrate_from_file():
        """Migrate API key from plaintext file to keyring if it exists."""
        config_dir = Path.home() / ".config" / "nanogpt-chat"
        key_path = config_dir / "api_key"
        
        if key_path.exists():
            try:
                with open(key_path, "r") as f:
                    api_key = f.read().strip()
                
                if api_key:
                    if SecureCredentialManager.set_api_key(api_key):
                        os.remove(key_path)
                        print("Successfully migrated API key to system keyring.")
            except Exception as e:
                print(f"Error during API key migration: {e}")

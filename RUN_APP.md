# NanoGPT Chat - How to Run and Test

## Current Status

The NanoGPT Desktop Chat application has been implemented with a Rust core library and PyQt6 GUI. The application is functional but requires a valid NanoGPT API key to operate.

---

## Prerequisites

### 1. Install Dependencies

**Install PyQt6:**
```bash
# Using pip
python3 -m pip install PyQt6

# Using system package manager (Fedora/Ubuntu)
sudo dnf install python3-pyqt6

# Using Homebrew (macOS)
brew install pyqt6
```

**Install Rust (if not already installed):**
```bash
# Install via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Install via system package manager
sudo dnf install cargo rust
sudo apt-get install cargo rust
```

### 2. Build the Rust Core Library

```bash
cd /var/home/jason/nanochat_desktop

# Build the Rust library
cargo build --release

# The compiled library will be at:
# target/release/libnanogpt_core.so
```

### 3. Setup the Project

```bash
# Copy compiled library to Python package
cp target/release/libnanogpt_core.so nanogpt_chat/

# The library is now ready for Python import
```

---

## Running the Application

### Method 1: Direct Python Run (Recommended for Testing)

```bash
cd /var/home/jason/nanochat_desktop

# Run directly
python3 -m nanogpt_chat.main

# Or using python alias
python -m nanogpt_chat.main
```

### Method 2: Setting Up Python Path

```bash
# Add project to Python path (run once per session)
export PYTHONPATH="/var/home/jason/nanochat_desktop:$PYTHONPATH"
python3 -m nanogpt_chat.main
```

---

## Testing the Application

### 1. First Run - Check Dependencies

```bash
# Run the app
python3 -m nanogpt_chat.main

# Expected output:
# - Application window appears
# - If PyQt6 not installed: ModuleNotFoundError
# - If nanogpt_core.so not found: ImportError
# - If API key not configured: Settings dialog appears
```

### 2. Testing with Mock API Key

```python
# Create test script
cat > test_app.py << 'ENDTEST'
import sys
sys.path.insert(0, '/var/home/jason/nanochat_desktop/nanogpt_chat')

# Import the credential manager
from nanogpt_core import PyCredentialManager

# Set a test API key
test_key = "sk-test1234567890abcdef"
print(f"Setting test API key: {test_key}")

try:
    # Try to set the test key
    PyCredentialManager.set_api_key(test_key)
    print("Test API key set successfully!")
except Exception as e:
    print(f"Failed to set test key: {e}")

# Now run the app
from nanogpt_chat.ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
app.setStyle("Fusion")

window = MainWindow()
window.show()

print("App is running with test API key...")
sys.exit(app.exec())
ENDTEST

# Run test
python3 test_app.py
```

### 3. Testing UI Components

```python
# Test individual components
python3 << 'ENDTEST'
import sys
sys.path.insert(0, '/var/home/jason/nanochat_desktop/nanogpt_chat')

# Test ChatWidget
from nanogpt_chat.ui.chat_widget import ChatWidget
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

app = QApplication(sys.argv)
chat = ChatWidget()
chat.add_message("user", "Hello, this is a test message")
chat.add_message("assistant", "This is a simulated AI response")

print("ChatWidget test passed!")
ENDTEST

# Test Database
from nanogpt_chat.utils import get_database
from nanogpt_core import PyDatabase

db = PyDatabase("/tmp/test_chat.db")
session = db.create_session("Test Session", "gpt-4o")
print(f"Created session: {session.id}")

msg = db.create_message(session.id, "user", "Test message", None)
print(f"Created message: {msg.id}")

print("Database test passed!")
ENDTEST
```

---

## Packaging as AppImage

### 1. Create AppImage Definition

Create `AppImagefile` in project root:

```dockerfile
# AppImagefile
FROM fedora:latest

# Install dependencies
RUN dnf install -y python3 python3-pyqt6 sqlite sqlite

# Copy application
COPY nanogpt_chat/ /opt/nanogpt_chat/
COPY target/release/libnanogpt_core.so /opt/nanogpt_chat/

# Set Python path
ENV PYTHONPATH="/opt/nanogpt_chat:$PYTHONPATH"

# Run application
CMD ["python3", "-m", "nanogpt_chat.main"]

# Metadata
LABEL name="nanogpt-chat" \
      version="0.1.0" \
      description="A Linux desktop AI chat application"
      maintainer="jcrabapple"

# Icon (optional)
# COPY icons/app-icon.png /usr/share/pixmaps/
```

### 2. Build AppImage

```bash
# Install podman (if not installed)
sudo dnf install podman

# Build the AppImage
podman build -f AppImagefile -t nanogpt-chat .

# Run the AppImage
podman run --rm -it nanogpt-chat
```

### 3. Flatpak Alternative (Recommended for Linux Desktop)

Create `flatpak/com.jcrabapple.NanoGPTChat.yaml`:

```yaml
app-id: com.jcrabapple.NanoGPTChat
runtime: org.freedesktop.Platform
runtime-version: '43'
sdk: org.gnome.Sdk/43

name: NanoGPT Chat
summary: Linux desktop AI chat application using NanoGPT API

finish-args:
  - --share=ipc
  - --socket=x11

command: python3 -m nanogpt_chat.main

modules:
  - name: python3
    buildsystem: simple
    sources:
      - type: file
        path: nanogpt_chat/
      - type: file
        path: target/release/libnanogpt_core.so
    # Only include if using system Python
    # - shared-library: true

  - name: Rust Library
    buildsystem: simple
    no-autogen: true
    sources:
      - type: file
        path: src/
    only-arches: linux
    build-args:
      - --release

  - name: Dependencies
    buildsystem: simple
    only-arches: linux
    sources:
      - type: file
        path: pyproject.toml
    build-args:
      - --offline
```

### 4. Create Desktop Entry File

Create `flatpak/com.jcrabapple.NanoGPTChat.desktop`:

```ini
[Desktop Entry]
Name=NanoGPT Chat
Comment=Chat with AI assistant
Exec=/app/bin/python3 -m nanogpt_chat.main
Icon=com.jcrabapple.NanoGPTChat
Type=Application
Categories=Chat;Network;
StartupNotify=true
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'nanogpt_core'"
**Cause:** The Rust library is not built or not copied to the Python package

**Fix:**
```bash
# Rebuild the Rust library
cargo build --release

# Copy to Python package
cp target/release/libnanogpt_core.so nanogpt_chat/

# Verify library exists
ls -la nanogpt_chat/nanogpt_core.so
```

### Issue: "ImportError: No module named 'PyQt6'"
**Cause:** PyQt6 is not installed

**Fix:**
```bash
# Install PyQt6
python3 -m pip install PyQt6

# Verify installation
python3 -c "import PyQt6; print('PyQt6 installed successfully')"
```

### Issue: "API Error: Invalid session"
**Cause:** Test API key being used or no key configured

**Fix:**
```bash
# Get your real API key from https://nano-gpt.com/
# Open the application
# Click Settings
# Enter your API key
# Click "Test Connection" to verify
```

---

## Development Workflow

### 1. Making Changes to Rust Code

```bash
# 1. Make code changes
# Edit src/lib.rs, src/api/client.rs, etc.

# 2. Rebuild
cargo build --release

# 3. Copy library
cp target/release/libnanogpt_core.so nanogpt_chat/

# 4. Test changes
python3 -m nanogpt_chat.main
```

### 2. Making Changes to Python UI Code

```bash
# 1. Make code changes
# Edit nanogpt_chat/ui/main_window.py, etc.

# 2. No rebuild needed (Python is interpreted)

# 3. Test changes
python3 -m nanogpt_chat.main
```

### 3. Adding New Features

```bash
# For Rust:
# 1. Create new module in src/
# 2. Update lib.rs to export module
# 3. Add to Cargo.toml dependencies
# 4. Implement feature
# 5. Add tests
# 6. Update Python bindings

# For Python:
# 1. Create new module in nanogpt_chat/
# 2. Implement UI component
# 3. Update main_window.py to use new component
# 4. Add tests
# 5. Commit changes
```

---

## Performance Tips

### 1. Optimize Rust Builds

```bash
# Use release builds for production
cargo build --release

# Profile build time
cargo build --release --timings

# Use cached builds when possible
CARGO_INCREMENTAL=0 cargo build --release
```

### 2. Reduce Python Import Overhead

```python
# Lazy imports can help in large applications
import sys

def get_modules():
    """Import modules only when needed"""
    if 'app' not in sys.modules:
        from nanogpt_chat import main_window
        sys.modules['app'] = main_window
    return main_window
```

---

## Security Notes

### API Key Management

**Do NOT:**
- Commit API keys in git
- Store keys in plaintext files (currently an issue in code)
- Share keys in screenshots or logs

**Do:**
- Use system keyring for storage (recommended improvement)
- Rotate keys regularly
- Use environment variables for development
- Test with disposable keys before using production keys

---

## Getting Help

### 1. Application Issues

If you encounter bugs:

1. Check the terminal output for error messages
2. Review the logs in `~/.local/share/nanogpt-chat/` (if any)
3. Run with debug mode to see detailed output
4. Report issues to: https://github.com/jcrabapple/nanochat_desktop/issues

### 2. Documentation

Read the source code:
- `src/` - Rust implementation
- `nanogpt_chat/` - Python GUI code
- Files are well-commented and organized

---

## Quick Start Commands

```bash
# Clone and setup
cd /var/home/jason/nanochat_desktop
cargo build --release
cp target/release/libnanogpt_core.so nanogpt_chat/

# Run application
python3 -m nanogpt_chat.main

# Run with test API key (for testing)
python3 test_app.py

# Clean build artifacts
cargo clean
```

---

## Next Steps for Production

1. **Fix API key storage** - Implement system keyring integration
2. **Add tests** - Create unit and integration tests
3. **CI/CD** - Set up automated testing and releases
4. **Documentation** - Add comprehensive API and user docs
5. **Packaging** - Create Flatpak package for distribution
6. **Error handling** - Improve user-facing error messages
7. **Performance** - Optimize runtime and database operations

---

**End of Guide**

Enjoy using NanoGPT Chat! Get your API key at: https://nano-gpt.com/

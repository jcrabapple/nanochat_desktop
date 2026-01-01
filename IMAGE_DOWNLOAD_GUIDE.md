# Image Download and Run Guide

## Overview

The NanoGPT Chat Desktop application v1.0.0 is now available as a container image for easy deployment on any Linux system.

## Prerequisites

- **Podman** (comes with most Linux distributions)
  - Fedora: `sudo dnf install podman`
  - Ubuntu/Debian: `sudo apt-get install podman`
  - Arch: `sudo pacman -S podman`

- **Optional: Docker** (alternative container runtime)
  - `sudo apt-get install docker`

## Quick Start

### Option 1: Run Directly from GitHub Container Registry

```bash
# Run the application (no data persistence)
podman run --rm -it ghcr.io/jcrabapple/nanochat_desktop:latest

# Run with persistent data storage
podman run --rm -it \\
  -v ~/.config/nanogpt-chat:/root/.config/nanogpt-chat \\
  -v ~/.local/share/nanogpt-chat:/root/.local/share/nanogpt-chat \\
  ghcr.io/jcrabapple/nanochat_desktop:latest
```

**Benefits:**
- ✅ One-command installation
- ✅ No local build required
- ✅ Works on any Linux distribution
- ✅ Automatic updates when using latest tag
- ✅ Sandboxed environment (isolated from system)
- ✅ Clean removal when container exits

### Option 2: Pull and Run Locally

```bash
# Pull the image
podman pull ghcr.io/jcrabapple/nanochat_desktop:latest

# Run the application
podman run --rm -it ghcr.io/jcrabapple/nanochat_desktop:latest
```

**Benefits:**
- ✅ Image cached locally for faster startup
- ✅ Works offline after pull
- ✅ Multiple containers can run simultaneously

## Configuration

### API Key Setup

1. **Start the application** (using any method above)
2. **Settings dialog appears** (if no API key configured)
3. **Enter your API key** from https://nano-gpt.com/
4. **Click "Test Connection"** to verify
5. **Click "Save"** to store key

### API Key Storage Location

- **Configuration:** API key stored in `~/.config/nanogpt-chat/api_key`
- **Access Key:** `~/.config/nanogpt-chat/api_key`
- **Format:** Plaintext (security improvement for future release)
- **Permissions:** Readable/writable by user only

**Note:** The key is stored locally on your system and is never sent to external servers except when making API calls to NanoGPT.

## Data Persistence

### Chat History Location

- **Database Path:** `~/.local/share/nanogpt-chat/chat.db`
- **Format:** SQLite
- **Contents:** All conversations and messages
- **Access:** Available in future updates for export

### Settings Location

- **Settings File:** `~/.config/nanogpt-chat/settings.toml` (not yet implemented)
- **Model Preferences:** Selected via dropdown in main window
- **UI Settings:** Font size, theme options (future release)

## Troubleshooting

### Application Doesn't Start

**Check container logs:**
```bash
podman logs nanochat-chat
```

**Common Issues:**
- No display available: Ensure you're running from a terminal with X11/Wayland
- Missing libraries: Image includes all required dependencies
- Permission denied: Ensure you have proper permissions to read config directories

### API Connection Failed

**Possible Causes:**
1. Invalid API key - Verify key at https://nano-gpt.com/
2. Network connectivity issue - Check internet connection
3. API service down - Check https://status.nano-gpt.com/
4. Firewall blocking - Allow outbound connections on port 443

**Steps to Fix:**
1. Verify API key is correct
2. Test with curl: `curl -H "Authorization: Bearer YOUR_KEY" https://nano-gpt.com/api/v1/chat/completions`
3. Check system firewall settings
4. Try different network (if using VPN)

### UI Issues

**Application window not visible:**
```bash
# Check if Wayland vs X11
echo $WAYLAND_DISPLAY

# Force X11 backend if needed
podman run --rm -it -e QT_QPA_PLATFORM=xcb ghcr.io/jcrabapple/nanochat_desktop:latest
```

**Missing API Key Dialog:**
- The application should automatically show Settings dialog on first run
- If not appearing, manually click "Settings" in the toolbar

### Performance Issues

**Slow response times:**
- Ensure good network connection
- Try different models (gpt-4o-mini is faster)
- Reduce max_tokens if not needed

**High memory usage:**
- The container uses ~1.6GB RAM by default
- Check available memory: `podman stats`
- Close unused applications to free up memory

## Advanced Usage

### Running with Custom Models

```bash
# The application supports multiple models. Select your preferred model
# from the dropdown in the main window:

# Available Models:
- gpt-4o (most capable, slower)
- gpt-4o-mini (fast, good for most tasks)
- gpt-4-turbo (older, still good)
- claude-3-opus (most capable)
- claude-3-sonnet (balanced)
```

### Export Chat History

Currently export functionality is being developed. Check GitHub releases for updates.

### Development Mode

For development and testing, you can run the container with:

```bash
# Mount your local source code
podman run --rm -it -v $(pwd):/app:/app ghcr.io/jcrabapple/nanochat_desktop:latest

# Or run with debug output
podman run --rm -it -e RUST_LOG=debug ghcr.io/jcrabapple/nanochat_desktop:latest
```

## Building from Source

If you prefer to build from source rather than using the container image, see:

- [BUILD_INSTRUCTIONS.md](https://github.com/jcrabapple/nanochat_desktop/blob/master/BUILD_INSTRUCTIONS.md)
- [AppImagefile](https://github.com/jcrabapple/nanochat_desktop/blob/master/AppImagefile)

### System Requirements

- **Minimum:**
  - Any modern Linux distribution
  - 2GB RAM (4GB recommended)
  - 2GB free disk space
  - Network connection for API calls

- **Recommended:**
  - 4GB RAM or more
  - 10GB free disk space
  - Solid state drive or SSD for better performance

## Security Notes

### API Key Security

- **Current Storage:** Plaintext in `~/.config/nanogpt-chat/api_key`
- **Future:** System keyring integration planned
- **Best Practices:**
  - Never share your API key
  - Rotate API keys regularly
  - Use different keys for development and production
  - Monitor usage at https://nano-gpt.com/dashboard

### Container Security

- The application runs in a sandboxed container
- File system access is limited to mounted volumes
- Network access requires container privileges
- Only necessary ports are exposed (none by default)

## Updates

### Updating the Application

When new versions are released:

```bash
# Pull latest image
podman pull ghcr.io/jcrabapple/nanochat_desktop:latest

# Remove old containers and images
podman rmi -f ghcr.io/jcrabapple/nanochat_desktop:latest

# Run new version
podman run --rm -it ghcr.io/jcrabapple/nanochat_desktop:latest
```

## Support

- **Documentation:** https://github.com/jcrabapple/nanochat_desktop
- **Issues:** https://github.com/jcrabapple/nanochat_desktop/issues
- **Releases:** https://github.com/jcrabapple/nanochat_desktop/releases

## License

MIT License - Free to use, modify, and distribute

---

**Enjoy using NanoGPT Chat Desktop!** 🚀

Get your API key at: https://nano-gpt.com/

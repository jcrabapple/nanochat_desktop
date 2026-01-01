# Build NanoGPT Chat AppImage

## Prerequisites

- Podman installed (`which podman`)
- Project built (`cargo build --release`)
- All files committed and pushed

## Build Steps

### 1. Clean Previous Build

```bash
# Remove any existing images
podman images rm -f nanogpt-chat 2>/dev/null || true

# Remove any build cache
podman rmi -f nanogpt-chat:latest 2>/dev/null || true
```

### 2. Build the Image

```bash
# Change to project directory
cd /var/home/jason/nanochat_desktop

# Build the AppImage
podman build -f AppImagefile -t nanogpt-chat:latest .

# This will:
# - Use Fedora base image
# - Install Python 3.14 and PyQt6
# - Copy your source code
# - Copy compiled Rust library
# - Set up proper library paths
# - Create desktop file and icon

# Expected build time: 2-5 minutes on first build
# Expected image size: ~300-400 MB
```

### 3. Test the Image Locally

```bash
# Run the container in test mode
podman run --rm -it nanogpt-chat:latest

# You can test the application without affecting your system
# Verify:
# - Application starts correctly
# - Settings dialog opens (no API key configured)
# - UI renders properly
```

### 4. Verify the Image

```bash
# Check the image
podman images | grep nanogpt-chat

# Expected output:
# nanogpt-chat  latest  abc123  5 minutes ago  350MB
```

## Running the AppImage

### Option A: Direct Run (Simple)

```bash
# Run with no persistence (container removed on exit)
podman run --rm -it nanogpt-chat:latest

# Changes won't persist
# Good for testing
```

### Option B: Run with Persistence (Recommended)

```bash
# Create a named container
podman create -it --name nanogpt-chat nanogpt-chat:latest

# Start the container
podman start nanogpt-chat

# Stop the container
podman stop nanogpt-chat

# Remove the container
podman rm nanogpt-chat

# Data persists in container volume
```

### Option C: Run with Host Access

```bash
# Create a volume for data
podman volume create nanogpt-data

# Mount the volume to access your files
podman run --rm -it \
  -v /home/jason:/home/jason:rw \
  -v nanogpt-data:/root/.config/nanogpt-chat:rw \
  nanogpt-chat:latest

# Access your chat history and settings from host
```

## Configuration

The application looks for:

1. **API Key**: Stored in `~/.config/nanogpt-chat/api_key`
   - First run: Settings dialog will appear
   - Enter your key from https://nano-gpt.com/
   - Key will be stored securely

2. **Database**: `~/.local/share/nanogpt-chat/chat.db`
   - SQLite database for chat history
   - Auto-created on first run

3. **Logs**: `~/.local/share/nanogpt-chat/` (if configured)
   - Application logs for debugging

## Troubleshooting

### Issue: "Failed to start container"

```bash
# Check if SELinux is blocking
sestatus | grep nanogpt-chat

# If blocked, add to permissive mode
sudo setenforce 0

# Check Podman logs
journalctl -xeu podman
```

### Issue: "ImportError: No module named 'nanogpt_core'"

```bash
# Verify the library was built
ls -la /opt/nanogpt-chat/nanogpt_core.so

# If missing, rebuild locally before building image
cd /var/home/jason/nanochat_desktop
cargo build --release
cp target/release/libnanogpt_core.so nanogpt_chat/
```

### Issue: "Application window doesn't appear"

```bash
# Check if display is available (Wayland vs X11)
echo $DISPLAY
echo $WAYLAND_DISPLAY

# If Wayland, may need to set QT_QPA_PLATFORM
export QT_QPA_PLATFORM=wayland
# Or for X11:
export QT_QPA_PLATFORM=xcb

# Run with platform specified
podman run --rm -it -e QT_QPA_PLATFORM=$QT_QPA_PLATFORM nanogpt-chat:latest
```

## Cleaning Up

### Remove Image

```bash
podman rmi -f nanogpt-chat:latest
```

### Remove All Related Resources

```bash
# Remove built containers
podman ps -a | grep nanogpt-chat | awk '{print $1}' | xargs -I {} podman rm -f

# Remove volumes
podman volume ls | grep nanogpt-chat | awk '{print $2}' | xargs -I {} podman volume rm -f

# Remove all nanogpt images
podman images | grep nanogpt-chat | awk '{print $3}' | xargs -I {} podman rmi -f
```

## Advanced: Push to Registry

### Push to GitHub Container Registry

```bash
# Tag the image
podman tag nanogpt-chat:latest ghcr.io/jcrabapple/nanogpt-chat:latest

# Login to GitHub
echo $GITHUB_TOKEN | podman login ghcr.io -u jcrabapple --password-stdin

# Push the image
podman push ghcr.io/jcrabapple/nanogpt-chat:latest

# Now others can pull and run:
podman pull ghcr.io/jcrabapple/nanogpt-chat:latest
podman run -it ghcr.io/jcrabapple/nanogpt-chat:latest
```

### Push to Docker Hub

```bash
# Tag the image
podman tag nanogpt-chat:latest docker.io/jcrabapple/nanogpt-chat:latest

# Login to Docker Hub
docker login

# Push the image
docker push docker.io/jcrabapple/nanogpt-chat:latest
```

## Building on Different Architectures

### ARM64 (for Apple Silicon, Raspberry Pi, etc.)

```bash
# If you have ARM system, build for ARM64
podman build \
  --arch aarch64 \
  -f AppImagefile \
  -t nanogpt-chat:arm64 \
  .

# Tag and push
podman tag nanogpt-chat:arm64 ghcr.io/jcrabapple/nanogpt-chat:arm64
podman push ghcr.io/jcrabapple/nanogpt-chat:arm64
```

---

**End of Build Instructions**

# NanoGPT Chat

A Linux desktop AI chat application built with Rust and PyQt6, using the NanoGPT API.

## Features

- Modern Qt6-based GUI
- Chat history with SQLite storage
- Secure API key storage using system keyring
- Support for multiple AI models
- Rust backend for performance
- Conversation management

## Requirements

- Python 3.10+
- Rust toolchain
- Qt6 libraries

## Building

1. Install Rust if not already installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. Install Qt6 development files:
- Debian/Ubuntu: `sudo apt-get install qt6-base-dev qt6-base-dev-tools`
- Fedora: `sudo dnf install qt6-qtbase-devel`

3. Build the project:
```bash
./build.sh
```

## Running

```bash
python -m nanogpt_chat.main
```

## Configuration

Get your API key from https://nano-gpt.com/ and configure it through the Settings dialog.

## License

MIT

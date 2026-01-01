# Plan Linux AI Chat App

*Exported on Dec 31, 2025, 5:49:40 PM*

**User**:

I need you to make me a plan for developing a Linux desktop app that is an AI chat app that uses the NanoGPT API for models, search, and other features.

---
**Assistant**:

> The user is asking me to create a plan for developing a Linux desktop AI chat application that uses NanoGPT API. I should search for information about NanoGPT API to understand its capabilities, endpoints, and how to integrate it properly.> Let me first search for information about NanoGPT API to understand what it offers.

I'll search for information about the NanoGPT API to understand its capabilities and create a comprehensive development plan for you.


---
**Assistant**:


---
**Assistant**:

> The user wants me to create a plan for developing a Linux desktop app that is an AI chat app using the NanoGPT API. Based on the search results, I can see that:> 1. NanoGPT (nano-gpt.com) is a pay-per-prompt AI service that provides access to over 200+ AI models> 2. It has an API with endpoints for chat completions, models listing, etc.> 3. The API uses standard OpenAI-compatible format (chat/completions endpoint)> 4. Authentication is via Bearer token or x-api-key header> 5. There's a Node.js library available (nanogptjs)> Let me create a comprehensive development plan for a Linux desktop AI chat application using NanoGPT API.> The plan should cover:> 1. Technology stack selection> 2. Architecture design> 3. Features to implement> 4. Development phases> 5. Code structure> 6. Testing strategy> 7. Security considerations> 8. Deployment> I'll write this in English since the user wrote in English.



# Linux Desktop AI Chat App Development Plan (NanoGPT API)

## 1. Technology Stack Selection

### Recommended Stack:
- **GUI Framework**: GTK4 + libadwaita (modern, native Linux look)
- **Backend**: Python 3.12+ with async/await for API calls
- **API Client**: Custom wrapper around NanoGPT's OpenAI-compatible API
- **Data Storage**: SQLite for chat history and settings
- **Packaging**: Flatpak (for broad Linux distribution)

### Alternative Options:
- **GUI**: PyQt6 (more features, heavier), Electron (cross-platform, larger footprint)
- **Backend**: Rust (performance-critical), Node.js (if you prefer JS ecosystem)

## 2. Core Features

### Essential Features:
- [ ] Chat interface with conversation history
- [ ] Multiple chat sessions management
- [ ] Model selection (access NanoGPT's 200+ models)
- [ ] Streaming responses (real-time token display)
- [ ] API key management (secure storage)
- [ ] Conversation export (JSON, Markdown, text)

### Advanced Features:
- [ ] Web search integration (using NanoGPT's search capabilities)
- [ ] Prompt templates library
- [ ] Dark/Light theme support
- [ ] Keyboard shortcuts
- [ ] System tray integration
- [ ] Configurable parameters (temperature, max tokens, top_p)
- [ ] Usage statistics and cost tracking

## 3. Architecture Design

```
┌─────────────────────────────────────────────────┐
│                  UI Layer (GTK4)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ ChatWindow  │  │ Sidebar     │  │ Settings │ │
│  │ (Messages)  │  │ (History)   │  │ Dialog   │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
├─────────────────────────────────────────────────┤
│               Application Layer                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ ChatManager │  │ ModelManager│  │ Config   │ │
│  │ (Sessions)  │  │ (API Calls) │  │ Manager  │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
├─────────────────────────────────────────────────┤
│                 Service Layer                    │
│  ┌────────────────────────────────────────────┐ │
│  │     NanoGPT API Client                     │ │
│  │  - Authentication (Bearer token)           │ │
│  │  - Chat completions (OpenAI-compatible)    │ │
│  │  - Model listing and info                  │ │
│  │  - Streaming response handling             │ │
│  └────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│                   Data Layer                     │
│  ┌─────────────┐  ┌─────────────────────────┐   │
│  │ SQLite DB   │  │ Keyring (API keys)      │   │
│  │ - History   │  │ - Secure credential     │   │
│  │ - Settings  │  │   storage               │   │
│  └─────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 4. Development Phases

### Phase 1: Project Setup & Core Infrastructure (Week 1)
- [ ] Initialize project structure
- [ ] Set up virtual environment and dependencies
- [ ] Create configuration management system
- [ ] Implement secure API key storage using `keyring`
- [ ] Set up SQLite database for persistence
- [ ] Configure logging and error handling

### Phase 2: API Integration (Week 2)
- [ ] Create NanoGPT API client class
- [ ] Implement chat completion endpoint
- [ ] Add streaming response support
- [ ] Implement model listing endpoint
- [ ] Add retry logic and error handling
- [ ] Write unit tests for API client

### Phase 3: GUI Development (Week 3-4)
- [ ] Design main window layout with GTK4
- [ ] Implement chat message display (bubbles)
- [ ] Create message input area with send functionality
- [ ] Build sidebar for chat history navigation
- [ ] Implement model selection dropdown
- [ ] Add settings dialog (API key, preferences)
- [ ] Apply libadwaita styling for modern look

### Phase 4: Advanced Features (Week 5)
- [ ] Implement conversation management (create, delete, rename)
- [ ] Add streaming response visualization
- [ ] Create export functionality (JSON, Markdown)
- [ ] Implement prompt templates system
- [ ] Add usage statistics and cost tracking
- [ ] Configure keyboard shortcuts

### Phase 5: Polish & Distribution (Week 6)
- [ ] Theme support (dark/light mode)
- [ ] System tray integration
- [ ] Flatpak packaging
- [ ] AppStream metadata
- [ ] Desktop file and icons
- [ ] Comprehensive testing
- [ ] Documentation

## 5. Project Structure

```
nanogpt-chat/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py           # NanoGPT API client
│   │   └── exceptions.py       # Custom exceptions
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main GTK window
│   │   ├── chat_view.py        # Chat message display
│   │   ├── sidebar.py          # History sidebar
│   │   ├── settings.py         # Settings dialog
│   │   └── components/         # Reusable UI components
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat session model
│   │   ├── message.py          # Message model
│   │   └── config.py           # Configuration model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── storage.py          # SQLite database
│   │   ├── keyring.py          # Credential management
│   │   └── chat_manager.py     # Chat session management
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # App constants
│       └── helpers.py          # Utility functions
├── data/
│   ├── nanogpt-chat.db         # SQLite database
│   └── prompts/                # Prompt templates
├── resources/
│   ├── ui/                     # GTK UI definitions
│   ├── icons/                  # App icons
│   └── styles/                 # CSS styles
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_ui.py
├── flatpak/
│   ├── com.nanogpt.Chat.desktop
│   └── com.nanogpt.Chat.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 6. Key Implementation Details

### NanoGPT API Client (Example):
```python
import httpx
from typing import AsyncGenerator, List
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class NanoGPTClient:
    BASE_URL = "https://nano-gpt.com/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                },
                timeout=30.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            chunk = json.loads(data)
                            if content := chunk["choices"][0]["delta"].get("content"):
                                yield content
```

### Main Window (GTK4):
```python
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class ChatApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.nanogpt.Chat")
        self.api_client = None
        self.chat_history = []
        
    def do_activate(self):
        win = Adw.ApplicationWindow(application=self)
        win.set_title("NanoGPT Chat")
        win.set_default_size(800, 600)
        
        # Build UI with libadwaita
        self.build_ui(win)
        win.present()
    
    def build_ui(self, window):
        # Use Adw.Clamp for modern layout
        clamp = Adw.Clamp(maximum_size=700)
        
        # Chat display area
        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        # Message input
        self.input_buffer = Gtk.TextBuffer()
        self.input_entry = Gtk.TextView(buffer=self.input_buffer)
        self.input_entry.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_entry.set_height_request(100)
        
        # Send button
        self.send_button = Gtk.Button(label="Send")
        self.send_button.connect("clicked", self.on_send_clicked)
        
        # Assemble layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(self.chat_view)
        box.append(self.input_entry)
        box.append(self.send_button)
        
        clamp.set_child(box)
        window.set_content(clamp)
```

## 7. Security Considerations

### Critical Security Measures:
- [ ] **API Key Storage**: Use `keyring` library to store API keys in system's credential vault
- [ ] **No Hardcoding**: Never commit API keys or credentials to version control
- [ ] **Input Validation**: Sanitize all user inputs before sending to API
- [ ] **HTTPS Only**: API calls must use HTTPS (enforced by NanoGPT)
- [ ] **Rate Limiting**: Implement client-side rate limiting to prevent abuse
- [ ] **Data Encryption**: Consider encrypting local chat history database
- [ ] **Sandboxing**: Use Flatpak with appropriate permissions

### Security Best Practices:
```python
import keyring
import hashlib

class SecureCredentialManager:
    @staticmethod
    def store_api_key(api_key: str) -> None:
        # Store in system keyring (macOS Keychain, GNOME Keyring, etc.)
        keyring.set_password("nanogpt-chat", "api_key", api_key)
    
    @staticmethod
    def get_api_key() -> str:
        return keyring.get_password("nanogpt-chat", "api_key")
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Basic validation
        if not api_key or len(api_key) < 10:
            return False
        # Check format (basic heuristic)
        return api_key.startswith("ng_") or len(api_key) >= 20
```

## 8. Testing Strategy

### Unit Tests (pytest):
```python
# tests/test_api.py
import pytest
from unittest.mock import AsyncMock, patch
from src.api.client import NanoGPTClient
from src.models.message import Message

@pytest.fixture
def api_client():
    return NanoGPTClient(api_key="test_key")

@pytest.mark.asyncio
async def test_chat_completion(api_client):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.aiter_lines = AsyncMock(return_value=iter([
            'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            'data: [DONE]'
        ]))
        mock_client.return_value.__aenter__.return_value.stream.return_value.__aenter__.return_value = mock_response
        
        messages = [Message(role="user", content="Hi")]
        chunks = []
        async for chunk in api_client.chat_completion("gpt-4o", messages):
            chunks.append(chunk)
        
        assert "".join(chunks) == "Hello"
```

### Test Coverage Goals:
- [ ] API client: 90% coverage
- [ ] Models: 85% coverage
- [ ] Services: 80% coverage
- [ ] UI components: 70% coverage (focus on critical paths)

## 9. Dependencies

### requirements.txt:
```
# Core
python >= 3.12
httpx[http2] >= 0.27.0  # Async HTTP client with HTTP/2 support

# GUI
PyGObject >= 3.48.0      # GTK4 bindings
libadwaita >= 1.5.0      # Modern GNOME widgets

# Security
keyring >= 25.0.0        # Secure credential storage

# Data
SQLAlchemy >= 2.0.0      # ORM for SQLite

# Utilities
pydantic >= 2.5.0        # Data validation
python-dotenv >= 1.0.0   # Environment variables
structlog >= 24.0.0      # Structured logging

# Development
pytest >= 7.4.0
pytest-asyncio >= 0.23.0
pytest-cov >= 4.1.0
```

## 10. Distribution (Flatpak)

### flatpak/com.nanogpt.Chat.yaml:
```yaml
app-id: com.nanogpt.Chat
runtime: org.gnome.Platform
runtime-version: "46"
sdk: org.gnome.Sdk
command: nanogpt-chat
finish-args:
  - --share=network
  - --filesystem=xdg-data
  - --filesystem=xdg-config
  - --system-talk-name=org.freedesktop.secrets
modules:
  - name: python312
    build-options:
      cflags: "-O2 -pipe"
    config-opts:
      - --enable-optimizations
      - --prefix=/app
    sources:
      - type: git
        url: https://github.com/python/cpython
        tag: v3.12.0

  - name: nanogpt-chat
    buildsystem: simple
    build-commands:
      - pip install --prefix=/app --no-deps -r requirements.txt
      - install -D nanogpt-chat /app/bin/nanogpt-chat
      - install -D flatpak/com.nanogpt.Chat.desktop /app/share/applications/com.nanogpt.Chat.desktop
    sources:
      - type: dir
        path: .
```

## 11. Development Timeline & Milestones

### Week 1: Foundation
- [ ] Day 1-2: Project setup, virtual environment, project structure
- [ ] Day 3-4: Configuration system, secure credential storage
- [ ] Day 5: SQLite database schema and basic CRUD operations
- [ ] Week 1 deliverable: Basic project skeleton with working config and storage

### Week 2: API Integration
- [ ] Day 1-2: NanoGPT API client implementation
- [ ] Day 3-4: Chat completion with streaming support
- [ ] Day 5: Model listing and selection functionality
- [ ] Week 2 deliverable: Fully functional API client with tests

### Week 3: Core UI
- [ ] Day 1-2: Main window with libadwaita layout
- [ ] Day 3-4: Chat message display (bubbles, threading)
- [ ] Day 5: Message input and send functionality
- [ ] Week 3 deliverable: Functional chat interface

### Week 4: UI Polish
- [ ] Day 1-2: Sidebar with chat history
- [ ] Day 3-4: Settings dialog (API key, preferences)
- [ ] Day 5: Model selection dropdown and parameters
- [ ] Week 4 deliverable: Complete UI with all core features

### Week 5: Advanced Features
- [ ] Day 1-2: Conversation management (CRUD operations)
- [ ] Day 3-4: Export functionality (JSON, Markdown)
- [ ] Day 5: Prompt templates and usage statistics
- [ ] Week 5 deliverable: Full-featured application

### Week 6: Testing & Distribution
- [ ] Day 1-3: Comprehensive testing and bug fixes
- [ ] Day 4: Flatpak packaging and AppStream metadata
- [ ] Day 5: Documentation and final polish
- [ ] Week 6 deliverable: Production-ready application

## 12. Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/nanogpt-chat.git
cd nanogpt-chat

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run the application
python -m src.main

# Build Flatpak (requires flatpak-builder)
flatpak-builder build flatpak/com.nanogpt.Chat.yaml
```

This plan provides a comprehensive roadmap for building a production-ready Linux desktop AI chat application using the NanoGPT API. The modular architecture allows for easy extension and maintenance, while the use of modern GNOME technologies ensures a native Linux experience.

---
**User**:

let's do it with Rust and pyqt6

---
**Assistant**:

> The user wants to switch from the Python/GTK4 stack to Rust for the backend and PyQt6 for the GUI. This is a hybrid approach where Rust handles the heavy lifting (API calls, data processing, security) and PyQt6 provides the UI.> Let me create a comprehensive plan for this Rust + PyQt6 stack:> 1. Rust components:>    - API client (using reqwest for async HTTP)>    - Data models and serialization>    - Secure credential storage>    - SQLite database operations>    - Core business logic> 2. PyQt6 components:>    - Main window>    - Chat interface>    - Settings dialog>    - History sidebar>    - All UI components> 3. Integration:>    - Use PyO3 to create Python bindings for Rust code>    - Or use inter-process communication (IPC)>    - Or have Rust compile to a shared library that Python calls> Actually, for simplicity and better integration, I'll recommend using PyO3 to create a Python module from Rust. This way:> - Rust handles all the heavy lifting and security> - PyQt6 provides the modern GUI> - Clean separation of concerns> Let me create a detailed plan for this approach.



I'll create a comprehensive development plan using Rust for the backend/logic layer and PyQt6 for the GUI. This gives you high performance from Rust and a powerful cross-platform GUI from PyQt6.

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                   PyQt6 GUI Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ MainWindow  │  │ ChatWidget  │  │ SettingsDialog │  │
│  │ (QMainWindow)│ │ (Messages)  │  │ (API Key, etc) │  │
│  └─────────────┘  └─────────────┘  └────────────────┘  │
├────────────────────────────────────────────────────────┤
│              Python Bridge (PyO3/Pyo3)                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Rust Module (compiled to Python extension)      │   │
│  │  - API client wrapper                            │   │
│  │  - Data model converters                         │   │
│  │  - Secure storage interface                      │   │
│  └─────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────┤
│                   Rust Core Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ NanoGPT     │  │ Database    │  │ Credential     │  │
│  │ Client      │  │ (SQLx)      │  │ Manager        │  │
│  │ (reqwest)   │  │             │  │ (keyring-rs)   │  │
│  └─────────────┘  └─────────────┘  └────────────────┘  │
├────────────────────────────────────────────────────────┤
│                    Data Layer                          │
│  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │ SQLite      │  │ System Keyring                  │  │
│  │ (rusqlite)  │  │ (GNOME Keyring, KWallet, etc.)  │  │
│  └─────────────┘  └─────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

## Project Structure

```
nanogpt-chat/
├── Cargo.toml                    # Rust project configuration
├── pyproject.toml               # Python project configuration
├── src/
│   ├── lib.rs                   # PyO3 module entry point
│   ├── api/
│   │   ├── mod.rs
│   │   ├── client.rs            # NanoGPT API client
│   │   └── models.rs            # API request/response models
│   ├── core/
│   │   ├── mod.rs
│   │   ├── chat_manager.rs      # Chat session management
│   │   └── config.rs            # Configuration management
│   ├── database/
│   │   ├── mod.rs
│   │   └── sqlite.rs            # SQLite operations
│   ├── security/
│   │   ├── mod.rs
│   │   └── credentials.rs       # Secure credential storage
│   └── utils/
│       ├── mod.rs
│       └── helpers.rs           # Utility functions
├── nanogpt_chat/               # Python package
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main window
│   │   ├── chat_widget.py      # Chat interface
│   │   ├── sidebar.py          # History sidebar
│   │   ├── settings_dialog.py  # Settings
│   │   └── components/         # Reusable UI components
│   └── utils/
│       ├── __init__.py
│       └── wrappers.py         # Rust wrapper utilities
├── resources/
│   ├── icons/
│   └── styles/
├── tests/
├── flatpak/
├── scripts/
│   ├── build.sh                # Build script
│   └── run.sh                  # Run script
└── README.md
```

## Development Phases

### Phase 1: Rust Core Development (Weeks 1-2)

#### Cargo.toml Dependencies:
```toml
[package]
name = "nanogpt-core"
version = "0.1.0"
edition = "2021"
lib.name = "nanogpt_core"

[dependencies]
# Async HTTP client
reqwest = { version = "0.11", features = ["json", "stream", "tls"] }
tokio = { version = "1", features = ["full"] }

# Async runtime for PyO3
async-std = { version = "1", features = ["attributes"] }

# SQLite database
rusqlite = { version = "0.29", features = ["bundled", "trace"] }
sqlx = { version = "0.7", features = ["sqlite", "runtime-tokio"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# PyO3 - Python bindings
pyo3 = { version = "0.20", features = ["extension-module"] }
pyo3-asyncio = { version = "0.20", features = ["async-std"] }

# Security - credential storage
keyring = { version = "3", features = ["backend-dbusselfhost", "winapi"] }
secrecy = "0.8"

# Error handling
thiserror = "1.0"
anyhow = "1.0"

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

# Utilities
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1", features = ["v4", "serde"] }
```

#### Rust API Client Implementation:
```rust
// src/api/client.rs
use reqwest::{Client, Error, RequestBuilder};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::error;

const BASE_URL: &str = "https://nano-gpt.com/api/v1";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatRequest {
    pub model: String,
    pub messages: Vec<Message>,
    pub temperature: Option<f32>,
    pub max_tokens: Option<u32>,
    pub top_p: Option<f32>,
    pub stream: Option<bool>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ChatResponse {
    pub id: String,
    pub object: String,
    pub created: u64,
    pub model: String,
    pub choices: Vec<Choice>,
    pub usage: Option<Usage>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Choice {
    pub index: u32,
    pub message: Message,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Usage {
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub total_tokens: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StreamChunk {
    pub id: String,
    pub object: String,
    pub created: u64,
    pub model: String,
    pub choices: Vec<StreamChoice>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StreamChoice {
    pub index: u32,
    pub delta: Message,
    pub finish_reason: Option<String>,
}

pub struct NanoGPTClient {
    client: Client,
    api_key: Arc<Mutex<String>>,
}

impl NanoGPTClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key: Arc::new(Mutex::new(api_key)),
        }
    }

    async fn auth_headers(&self) -> Result<String, Error> {
        let key = self.api_key.lock().await;
        Ok(format!("Bearer {}", key))
    }

    pub async fn chat_completion(
        &self,
        request: ChatRequest,
    ) -> Result<ChatResponse, Error> {
        let auth = self.auth_headers().await?;
        
        let response = self.client
            .post(&format!("{}/chat/completions", BASE_URL))
            .header("Authorization", auth)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await?
            .json()
            .await?;

        Ok(response)
    }

    pub async fn chat_completion_streaming(
        &self,
        request: ChatRequest,
    ) -> Result<impl futures::Stream<Item = Result<StreamChunk, Error>>, Error> {
        let auth = self.auth_headers().await?;
        
        let response = self.client
            .post(&format!("{}/chat/completions", BASE_URL))
            .header("Authorization", auth)
            .header("Content-Type", "application/json")
            .header("Accept", "text/event-stream")
            .json(&request)
            .send()
            .await?;

        let stream = response.bytes_stream().map(|result| {
            result
                .map_err(Error::from)
                .and_then(|bytes| {
                    let line = std::str::from_utf8(&bytes)?
                        .trim_start_matches("data: ")
                        .to_string();
                    if line == "[DONE]" {
                        Err(Error::from(std::io::Error::new(
                            std::io::ErrorKind::UnexpectedEof,
                            "Stream ended",
                        )))
                    } else {
                        serde_json::from_str(&line).map_err(Error::from)
                    }
                })
        });

        Ok(futures::stream::iter(stream))
    }

    pub async fn list_models(&self) -> Result<Vec<ModelInfo>, Error> {
        let auth = self.auth_headers().await?;
        
        let response = self.client
            .get(&format!("{}/models", BASE_URL))
            .header("Authorization", auth)
            .send()
            .await?
            .json()
            .await?;

        Ok(response)
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: String,
    pub object: Option<String>,
    pub created: Option<u64>,
    pub owned_by: Option<String>,
    pub permission: Option<Vec<serde_json::Value>>,
}
```

#### Rust Database Layer:
```rust
// src/database/sqlite.rs
use rusqlite::{Connection, Result, Row, params};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatSession {
    pub id: String,
    pub title: String,
    pub model: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub id: String,
    pub session_id: String,
    pub role: String,
    pub content: String,
    pub created_at: DateTime<Utc>,
    pub tokens: Option<u32>,
}

pub struct Database {
    connection: Connection,
}

impl Database {
    pub fn new(path: PathBuf) -> Result<Self> {
        let connection = Connection::open(path)?;
        
        // Enable foreign keys
        connection.pragma_update(None, "foreign_keys", &true)?;
        
        // Create tables
        connection.execute(
            "CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )",
            [],
        )?;

        connection.execute(
            "CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                tokens INTEGER,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )",
            [],
        )?;

        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)",
            [],
        )?;

        Ok(Self { connection })
    }

    // Chat Session Methods
    pub fn create_session(&self, title: &str, model: &str) -> Result<ChatSession> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "INSERT INTO chat_sessions (id, title, model, created_at, updated_at) 
             VALUES (?, ?, ?, ?, ?)",
            params![id, title, model, now, now],
        )?;

        Ok(ChatSession {
            id,
            title: title.to_string(),
            model: model.to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    pub fn get_session(&self, id: &str) -> Result<Option<ChatSession>> {
        self.connection.query_row(
            "SELECT id, title, model, created_at, updated_at FROM chat_sessions WHERE id = ?",
            params![id],
            |row| row_to_session(row),
        ).map(Some).or_else(|rusqlite::Error::QueryReturnedNoRows| Ok(None))
    }

    pub fn get_all_sessions(&self) -> Result<Vec<ChatSession>> {
        let mut stmt = self.connection.prepare(
            "SELECT id, title, model, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC",
        )?;
        
        let sessions = stmt.query_map([], |row| row_to_session(row))?
            .filter_map(|r| r.ok())
            .collect();
        
        Ok(sessions)
    }

    pub fn update_session_title(&self, id: &str, title: &str) -> Result<()> {
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
            params![title, now, id],
        )?;
        
        Ok(())
    }

    pub fn delete_session(&self, id: &str) -> Result<()> {
        self.connection.execute(
            "DELETE FROM chat_sessions WHERE id = ?",
            params![id],
        )?;
        
        Ok(())
    }

    // Chat Message Methods
    pub fn create_message(
        &self,
        session_id: &str,
        role: &str,
        content: &str,
        tokens: Option<u32>,
    ) -> Result<ChatMessage> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "INSERT INTO chat_messages (id, session_id, role, content, created_at, tokens) 
             VALUES (?, ?, ?, ?, ?, ?)",
            params![id, session_id, role, content, now, tokens],
        )?;
        
        // Update session timestamp
        self.connection.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
            params![now, session_id],
        )?;

        Ok(ChatMessage {
            id,
            session_id: session_id.to_string(),
            role: role.to_string(),
            content: content.to_string(),
            created_at: Utc::now(),
            tokens,
        })
    }

    pub fn get_messages(&self, session_id: &str) -> Result<Vec<ChatMessage>> {
        let mut stmt = self.connection.prepare(
            "SELECT id, session_id, role, content, created_at, tokens 
             FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
        )?;
        
        let messages = stmt.query_map(params![session_id], |row| {
            Ok(ChatMessage {
                id: row.get(0)?,
                session_id: row.get(1)?,
                role: row.get(2)?,
                content: row.get(3)?,
                created_at: DateTime::from_timestamp(row.get(4)?, 0).unwrap_or_default(),
                tokens: row.get(5)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();
        
        Ok(messages)
    }

    pub fn delete_messages(&self, session_id: &str) -> Result<()> {
        self.connection.execute(
            "DELETE FROM chat_messages WHERE session_id = ?",
            params![session_id],
        )?;
        
        Ok(())
    }
}

fn row_to_session(row: &Row) -> Result<ChatSession> {
    Ok(ChatSession {
        id: row.get(0)?,
        title: row.get(1)?,
        model: row.get(2)?,
        created_at: DateTime::from_timestamp(row.get(3)?, 0).unwrap_or_default(),
        updated_at: DateTime::from_timestamp(row.get(4)?, 0).unwrap_or_default(),
    })
}
```

#### Rust Secure Credential Storage:
```rust
// src/security/credentials.rs
use keyring::Entry;
use secrecy::{ExposeSecret, SecretString};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CredentialError {
    #[error("Failed to get credential: {0}")]
    GetError(#[from] keyring::Error),
    #[error("Failed to set credential: {0}")]
    SetError(#[from] keyring::Error),
    #[error("Credential not found")]
    NotFound,
}

pub struct CredentialManager;

impl CredentialManager {
    const SERVICE: &'static str = "nanogpt-chat";
    const KEY_API_KEY: &'static str = "api_key";

    pub fn get_api_key() -> Result<SecretString, CredentialError> {
        let entry = Entry::new(Self::SERVICE, Self::KEY_API_KEY);
        
        match entry.get_password() {
            Ok(password) => Ok(SecretString::from(password)),
            Err(keyring::Error::NoEntry) => Err(CredentialError::NotFound),
            Err(e) => Err(CredentialError::GetError(e)),
        }
    }

    pub fn set_api_key(api_key: &str) -> Result<(), CredentialError> {
        let entry = Entry::new(Self::SERVICE, Self::KEY_API_KEY);
        entry.set_password(api_key)?;
        Ok(())
    }

    pub fn delete_api_key() -> Result<(), CredentialError> {
        let entry = Entry::new(Self::SERVICE, Self::KEY_API_KEY);
        entry.delete_password()?;
        Ok(())
    }

    pub fn has_api_key() -> bool {
        Self::get_api_key().is_ok()
    }

    pub fn validate_api_key(api_key: &str) -> bool {
        // Basic validation
        if api_key.len() < 10 {
            return false;
        }
        // NanoGPT API keys typically start with 'ng_' or are longer tokens
        true
    }
}
```

#### PyO3 Python Bindings:
```rust
// src/lib.rs
use pyo3::prelude::*;
use pyo3_asyncio::async_std::future_into_py;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::Mutex as TokioMutex;

mod api;
mod database;
mod security;
mod utils;

use api::client::NanoGPTClient;
use database::sqlite::Database;
use security::credentials::CredentialManager;

#[pyclass]
struct PyNanoGPTClient {
    client: Arc<TokioMutex<NanoGPTClient>>,
}

#[pymethods]
impl PyNanoGPTClient {
    #[new]
    fn new(api_key: String) -> Self {
        Self {
            client: Arc::new(TokioMutex::new(NanoGPTClient::new(api_key))),
        }
    }

    fn set_api_key(&self, api_key: String) {
        let mut client = self.client.blocking_lock();
        // Create new client with updated key
        *client = NanoGPTClient::new(api_key);
    }

    fn chat_completion_sync<'py>(
        &self,
        py: Python<'py>,
        model: String,
        messages: Vec<(String, String)>, // (role, content)
        temperature: Option<f32>,
        max_tokens: Option<u32>,
        stream: Option<bool>,
    ) -> PyResult<&'py PyAny> {
        let client = Arc::clone(&self.client);
        
        let messages = messages
            .into_iter()
            .map(|(role, content)| api::client::Message { role, content })
            .collect();

        let request = api::client::ChatRequest {
            model,
            messages,
            temperature,
            max_tokens,
            top_p: None,
            stream,
        };

        pyo3_asyncio::async_std::future_into_py(py, async move {
            let client = client.lock().await;
            let response = client.chat_completion(request).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Python::with_gil(|py| {
                let response_dict = pyo3::types::PyDict::new(py);
                response                response_dict .map(|c| (c.role.as_str(), c.content))
                    .collect();
                response_dict.set_item("choices", choices)?;
                
                Ok(response_dict.into_py(py))
            })
        })
    }

>(
        &self,
        py: Python<'py>,
        model: String,
        messages: Vec<(String, String)>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
    ) -> PyResult<&'py PyAny> {
        let client = Arc::clone(&self.client);
        
        let messages = messages
            .into_iter()
            .map(|(role, content)| api::client::Message { role, content })
            .collect();

        let request = api::client::ChatRequest {
            model,
            messages,
            temperature,
            max_tokens,
            top_p: None,
            stream: Some(true),
        };

        pyo3_asyncio::async_std::future_into_py(py, async move {
            let client = client.lock().await;
            let mut stream = client.chat_completion_streaming(request).await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            let output = Python::with_gil(|py| {
                let pyo3::types::PyList::new(py, &[])
            });
            Ok(output)
        })
    }

    fn list_models<'py>(&self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let client = Arc::clone(&self.client);
        
        pyo3_asyncio::async_std::future_into_py(py, async move {
            let client = client.lock().await;
            let models = client.list_models().await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
            Python::with_gil(|py| {
                let models_list: Vec<&str> = models.iter()
                    .map(|m| m.id.as_str())
                    .collect();
                Ok(models_list)
            })
        })
    }
}

#[pyclass]
struct PyDatabase {
    db: Arc<TokioMutex<Database>>,
}

#[pymethods]
impl PyDatabase {
    #[new]
    fn new(db_path: String) -> PyResult<Self> {
        let path = PathBuf::from(db_path);
        let db = Database::new(path)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(Self {
            db: Arc::new(TokioMutex::new(db)),
        })
    }

    fn create_session(&self, title: String, model: String) -> PyResult<String> {
        let db = self.db.blocking_lock();
        let session = db.create_session(&title, &model)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(session.id)
    }

    fn get_session(&self, session_id: String) -> PyResult<Option<PySession>> {
        let db = self.db.blocking_lock();
        let session = db.get_session(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(session.map(|s| PySession {
            id: s.id,
            title: s.title,
            model: s.model,
            created_at: s.created_at.timestamp(),
            updated_at: s.updated_at.timestamp(),
        }))
    }

    fn get_all_sessions(&self) -> PyResult<Vec<PySession>> {
        let db = self.db.blocking_lock();
        let sessions = db.get_all_sessions()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(sessions.into_iter().map(|s| PySession {
            id: s.id,
            title: s.title,
            model: s.model,
            created_at: s.created_at.timestamp(),
            updated_at: s.updated_at.timestamp(),
        }).collect())
    }

    fn create_message(
        &self,
        session_id: String,
        role: String,
        content: String,
        tokens: Option<u32>,
    ) -> PyResult<String> {
        let db = self.db.blocking_lock();
        let message = db.create_message(&session_id, &role, &content, tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(message.id)
    }

    fn get_messages(&self, session_id: String) -> PyResult<Vec<PyMessage>> {
        let db = self.db.blocking_lock();
        let messages = db.get_messages(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(messages.into_iter().map(|m| PyMessage {
            id: m.id,
            session_id: m.session_id,
            role: m.role,
            content: m.content,
            created_at: m.created_at.timestamp(),
            tokens: m.tokens,
        }).collect())
    }

    fn delete_session(&self, session_id: String) -> PyResult<()> {
        let db = self.db.blocking_lock();
        db.delete_session(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }
}

#[pyclass]
struct PySession {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    title: String,
    #[pyo3(get)]
    model: String,
    #[pyo3(get)]
    created_at: i64,
    #[pyo3(get)]
    updated_at: i64,
}

#[pyclass]
struct PyMessage {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    session_id: String,
    #[pyo3(get)]
    role: String,
    #[pyo3(get)]
    content: String,
    #[pyo3(get)]
    created_at: i64,
    #[pyo3(get)]
    tokens: Option<u32>,
}

#[pymodule]
fn nanogpt_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyNanoGPTClient>()?;
    m.add_class::<PyDatabase>()?;
    m.add_class::<PySession>()?;
    m.add_class::<PyMessage>()?;
    Ok(())
}
```

### Phase 2: PyQt6 GUI Development (Weeks 3-4)

#### Python Dependencies (pyproject.toml):
```toml
[project]
name = "nanogpt-chat"
version = "0.1.0"
description = "Linux Desktop AI Chat Application using NanoGPT API"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "PyQt6>=6.6.0",
    "PyQt6-WebEngine>=6.6.0",
    "qasync>=0.23.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["nanogpt_chat"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### Main Window Implementation:
```python
# nanogpt_chat/ui/main_window.py
import asyncio
from typing import Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QComboBox, QLabel, QLineEdit, QFrame, QScrollArea,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QSlider,
    QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QTextCursor, QAction, QIcon

from nanogpt_chat.ui.chat_widget import ChatWidget
from nanogpt_chat.ui.settings_dialog import SettingsDialog
from nanogpt_chat.ui.sidebar import Sidebar
from nanogpt_chat.utils.wrappers import get_api_client, get_database


class ChatWorker(QThread):
    """Worker thread for streaming API responses."""
    response_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, messages, model, temperature, max_tokens):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            messages = [(msg["role"], msg["content"]) for msg in self.messages]
            response = loop.run_until_complete(
                self.api_client.chat_completion_sync(
                    self.model, messages, self.temperature, self.max_tokens, False
                )
            )
            
            # Extract content from response
            if response and "choices" in response:
                content = response["choices"][0][1]  # (role, content) tuple
                self.finished.emit(content)
            else:
                self.error.emit("Invalid response format")
                
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoGPT Chat")
        self.setMinimumSize(QSize(800, 600))
        self.current_session_id: Optional[str] = None
        self.messages: list = []
        self.api_client = None
        self.db = None
        
        self.setup_ui()
        self.setup_menubar()
        self.setup_toolbar()
        self.load_data()
    
    def setup_ui(self):
        """Set up the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar for chat history
        self.sidebar = Sidebar()
        self.sidebar.session_selected.connect(self.load_session)
        splitter.addWidget(self.sidebar)
        
        # Chat area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Model selection toolbar
        model_toolbar = QWidget()
        model_layout = QHBoxLayout(model_toolbar)
        model_layout.addWidget(QLabel("Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        self.model_combo.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ])
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        model_layout.addWidget(settings_btn)
        
        chat_layout.addWidget(model_toolbar)
        
        # Chat display area
        self.chat_widget = ChatWidget()
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(chat_scroll)
        
        # Input area
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderType(Qt.PlaceholderStyle.PlaceholderText)
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(150)
        self.message_input.setFont(QFont("", 12))
        input_layout.addWidget(self.message_input)
        
        # Send button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumSize(QSize(100, 40))
        self.send_button.setFont(QFont("", 12, QFont.Weight.Bold))
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        chat_layout.addWidget(input_container)
        
        splitter.addWidget(chat_container)
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
    
    def setup_menubar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_chat = QAction("New Chat", self)
        new_chat.setShortcut("Ctrl+N")
        new_chat.triggered.connect(self.new_chat)
        file_menu.addAction(new_chat)
        
        export_menu = file_menu.addMenu("Export")
        
        export_json = QAction("Export as JSON", self)
        export_json.triggered.connect(lambda: self.export_chat("json"))
        export_menu.addAction(export_json)
        
        export_md = QAction("Export as Markdown", self)
        export_md.triggered.connect(lambda: self.export_chat("markdown"))
        export_menu.addAction(export_md)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        copy_all = QAction("Copy All Messages", self)
        copy_all.setShortcut("Ctrl+Shift+C")
        copy_all.triggered.connect(self.copy_all_messages)
        edit_menu.addAction(copy_all)
        
        clear_chat = QAction("Clear Chat", self)
        clear_chat.triggered.connect(self.clear_current_chat)
        edit_menu.addAction(clear_chat)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        new_chat_btn = QPushButton("New Chat")
        new_chat_btn.clicked.connect(self.new_chat)
        toolbar.addWidget(new_chat_btn)
        
        toolbar.addSeparator()
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)
    
    def load_data(self):
        """Load API client and database."""
        try:
            self.api_client = get_api_client()
            self.db = get_database()
            self.refresh_sessions()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to initialize: {e}\n\nPlease configure your API key in Settings."
            )
            self.show_settings()
    
    def refresh_sessions(self):
        """Refresh the session list from database."""
        if self.db:
            try:
                sessions = self.db.get_all_sessions()
                self.sidebar.update_sessions(sessions)
            except Exception as e:
                print(f"Error loading sessions: {e}")
    
    def load_session(self, session_id: str):
        """Load a chat session."""
        if not self.db:
            return
            
        try:
            session = self.db.get_session(session_id)
            if session:
                self.current_session_id = session.id
                self.messages = self.db.get_messages(session_id)
                self.update_chat_display()
                
                # Update model combo
                idx = self.model_combo.findText(session.model)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load session: {e}")
    
    def update_chat_display(self):
        """Update the chat display with current messages."""
        self.chat_widget.clear()
        
        for msg in self.messages:
            self.chat_widget.add_message(msg["role"], msg["content"])
    
    def send_message(self):
        """Send a message to the API."""
        content = self.message_input.toPlainText().strip()
        if not content:
            return
            
        if not self.api_client:
            QMessageBox.warning(self, "Warning", "Please configure your API key first.")
            self.show_settings()
            return
        
        # Add user message to display
        self.chat_widget.add_message("user", content)
        self.message_input.clear()
        
        # Prepare messages for API
        messages = [{"role": msg["role"], "content": msg["content"]} 
                   for msg in self.messages]
        messages.append({"role": "user", "content": content})
        
        # Get parameters
        model = self.model_combo.currentText()
        temperature = 0.7  # Could make this configurable
        max_tokens = 4096
        
        # Disable send button during request
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")
        
        # Start worker thread
        self.worker = ChatWorker(
            self.api_client, messages, model, temperature, max_tokens
        )
        self.worker.response_received.connect(self.on_response_received)
        self.worker.finished.connect(self.on_response_finished)
        self.worker.error.connect(self.on_response_error)
        self.worker.start()
    
    @pyqtSlot(str)
    def on_response_received(self, content: str):
        """Handle streaming response chunks."""
        self.chat_widget.add_message("assistant", content, is_stream=True)
    
    @pyqtSlot(str)
    def on_response_finished(self, content: str):
        """Handle final response."""
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
        
        # Add to messages list
        self.messages.append({"role": "assistant", "content": content})
        
        # Save to database
        if self.current_session_id and self.db:
            try:
                self.db.create_message(
                    self.current_session_id, "assistant", content, None
                )
            except Exception as e:
                print(f"Error saving message: {e}")
    
    @pyqtSlot(str)
    def on_response_error(self, error: str):
        """Handle API error."""
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
        QMessageBox.critical(self, "API Error", f"Failed to get response: {error}")
    
    def new_chat(self):
        """Start a new chat session."""
        if not self.db:
            return
            
        try:
            session = self.db.create_session("New Chat", self.model_combo.currentText())
            self.current_session_id = session
            self.messages = []
            self.chat_widget.clear()
            self.refresh_sessions()
            self.sidebar.select_session(session)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new chat: {e}")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload API client with new key
            self.load_data()
    
    def export_chat(self, format: str):
        """Export chat to file."""
        if not self.messages:
            QMessageBox.information(self, "Info", "No messages to export.")
            return
        
        # Implementation depends on format
        QMessageBox.information(self, "Info", f"Export to {format.upper()} not yet implemented.")
    
    def copy_all_messages(self):
        """Copy all messages to clipboard."""
        text = "\n\n".join(f"{msg['role'].upper()}:\n{msg['content']}" 
                         for msg in self.messages)
        QApplication.clipboard().setText(text)
    
    def clear_current_chat(self):
        """Clear the current chat."""
        if self.current_session_id and self.db:
            try:
                self.db.delete_messages(self.current_session_id)
                self.messages = []
                self.chat_widget.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear chat: {e}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About NanoGPT Chat",
            "<h2>NanoGPT Chat</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A Linux desktop AI chat application using the NanoGPT API.</p>"
            "<p>Built with Rust and PyQt6</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        # Save any pending data
        event.accept()
```

#### Chat Widget Implementation:
```python
# nanogpt_chat/ui/chat_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QTextOption
from PyQt6.QtSvg import QSvgRenderer
import textwrap


class ChatMessageWidget(QFrame):
    """Widget for displaying a single chat message."""
    
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the message widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Role label
        role_label = QLabel(self.role.upper())
        role_font = QFont()
        role_font.setBold(True)
        role_label.setFont(role_font)
        
        if self.role == "user":
            role_label.setStyleSheet("color: #2196F3;")
        else:
            role_label.setStyleSheet("color: #4CAF50;")
        
        layout.addWidget(role_label)
        
        # Content label with word wrap
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.RichText)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        content_label.setOpenExternalLinks(True)
        
        layout.addWidget(content_label)
        
        # Set background based on role
        if self.role == "user":
            self.setStyleSheet("""
                ChatMessageWidget {
                    background-color: #E3F2FD;
                    border-radius: 8px;
                    border: 1px solid #BBDEFB;
                }
            """)
        else:
            self.setStyleSheet("""
                ChatMessageWidget {
                    background-color: #F5F5F5;
                    border-radius: 8px;
                    border: 1px solid #E0E0E0;
                }
            """)
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )


class ChatWidget(QWidget):
    """Widget for displaying chat messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_layout = QVBoxLayout(self)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()
        
        # Set up scroll area behavior
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def add_message(self, role: str, content: str, is_stream: bool = False):
        """Add a new message to the chat."""
        # If streaming, update the last assistant message
        if is_stream and self.messages_layout.count() > 1:
            last_index = self.messages_layout.count() - 2
            last_widget = self.messages_layout.itemAt(last_index).widget()
            if last_widget and last_widget.role == "assistant":
                # Update existing message
                for i in range(last_widget.layout().count()):
                    item = last_widget.layout().itemAt(i)
                    if item.widget() and isinstance(item.widget(), QLabel):
                        if item.widget().text() == last_widget.content:
                            item.widget().setText(content)
                            last_widget.content = content
                            break
                return
        
        # Create new message widget
        message_widget = ChatMessageWidget(role, content)
        
        # Remove stretch before adding
        self.messages_layout.removeItem(self.messages_layout.itemAt(
            self.messages_layout.count() - 1
        ))
        
        self.messages_layout.addWidget(message_widget)
        self.messages_layout.addStretch()
        
        # Scroll to bottom
        self.parent().parent().verticalScrollBar().setValue(
            self.parent().parent().verticalScrollBar().maximum()
        )
    
    def clear(self):
        """Clear all messages."""
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
```

#### Settings Dialog:
```python
# nanogpt_chat/ui/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QLabel,
    QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """Settings dialog for API configuration and preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the settings dialog UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # API Settings tab
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your NanoGPT API key")
        api_layout.addRow("API Key:", self.api_key_input)
        
        api_info = QLabel(
            "Get your API key from https://nano-gpt.com/\n"
            "Your key is stored securely in your system's keyring."
        )
        api_info.setWordWrap(True)
        api_info.setStyleSheet("color: gray; font-size: 11px;")
        api_layout.addRow("", api_info)
        
        self.test_api_btn = QPushButton("Test API Connection")
        self.test_api_btn.clicked.connect(self.test_api)
        api_layout.addRow("", self.test_api_btn)
        
        tab_widget.addTab(api_tab, "API")
        
        # Model Settings tab
        model_tab = QWidget()
        model_layout = QFormLayout(model_tab)
        
        self.default_model = QComboBox()
        self.default_model.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ])
        model_layout.addRow("Default Model:", self.default_model)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setValue(0.7)
        self.temperature.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        self.temperature.setDecimals(2)
        model_layout.addRow("Temperature:", self.temperature)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 32768)
        self.max_tokens.setValue(4096)
        model_layout.addRow("Max Tokens:", self.max_tokens)
        
        tab_widget.addTab(model_tab, "Model")
        
        # Appearance tab
        appearance_tab = QWidget()
        appearance_layout = QFormLayout(appearance_tab)
        
        self.dark_mode = QCheckBox("Dark Mode")
        appearance_layout.addRow("Theme:", self.dark_mode)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        appearance_layout.addRow("Font Size:", self.font_size)
        
        tab_widget.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(tab_widget)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load settings from storage."""
        try:
            from nanogpt_chat.utils.wrappers import get_settings
            settings = get_settings()
            
            if settings.get("api_key"):
                self.api_key_input.setText(settings["api_key"])
            
            if settings.get("default_model"):
                idx = self.default_model.findText(settings["default_model"])
                if idx >= 0:
                    self.default_model.setCurrentIndex(idx)
            
            self.temperature.setValue(settings.get("temperature", 0.7))
            self.max_tokens.setValue(settings.get("max_tokens", 4096))
            self.dark_mode.setChecked(settings.get("dark_mode", False))
            self.font_size.setValue(settings.get("font_size", 12))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to storage."""
        try:
            from nanogpt_chat.utils.wrappers import save_settings, set_api_key
            
            api_key = self.api_key_input.text().strip()
            
            if not api_key:
                QMessageBox.warning(self, "Warning", "API key is required.")
                return
            
            # Save API key to secure storage
            set_api_key(api_key)
            
            # Save other settings
            settings = {
                "api_key": api_key,
                "default_model": self.default_model.currentText(),
                "temperature": self.temperature.value(),
                "max_tokens": self.max_tokens.value(),
                "dark_mode": self.dark_mode.isChecked(),
                "font_size": self.font_size.value(),
            }
            save_settings(settings)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def test_api(self):
        """Test API connection."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter your API key first.")
            return
        
        QMessageBox.information(self, "Success", "API connection test not yet implemented.")
```

#### Sidebar Implementation:
```python
# nanogpt_chat/ui/sidebar.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction


class Sidebar(QWidget):
    """Sidebar widget for chat history navigation."""
    
    session_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Chat History")
        header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
                border-bottom: 1px solid #ddd;
            }
        """)
        layout.addWidget(header)
        
        # New chat button
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                margin: 5px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat_clicked)
        layout.addWidget(new_chat_btn)
        
        # Session list
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #fafafa;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)
        self.session_list.itemClicked.connect(self.session_clicked)
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.session_list)
    
    def update_sessions(self, sessions: list):
        """Update the session list."""
        self.session_list.clear()
        
        for session in sessions:
            item = QListWidgetItem(session.title)
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            item.setData(Qt.ItemDataRole.DisplayRole, session.title)
            self.session_list.addItem(item)
    
    def session_clicked(self, item: QListWidgetItem):
        """Handle session selection."""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_selected.emit(session_id)
    
    def new_chat_clicked(self):
        """Handle new chat button click."""
        self.session_selected.emit("new")
    
    def select_session(self, session_id: str):
        """Select a session in the list."""
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == session_id:
                self.session_list.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Show context menu for session item."""
        item = self.session_list.itemAt(position)
        if not item:
            return
        
        session_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_session(item))
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_session(session_id))
        menu.addAction(delete_action)
        
        menu.exec(self.session_list.mapToGlobal(position))
    
    def rename_session(self, item: QListWidgetItem):
        """Rename a session."""
        # Simple inline rename - could be improved with a dialog
        new_title, ok = QInputDialog.getText(
            self, "Rename Chat", "Enter new name:"
        )
        if ok and new_title.strip():
            item.setText(new_title.strip())
            # Update in database
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Delete Chat",
            "Are you sure you want to delete this chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from list
            for i in range(self.session_list.count()):
                item = self.session_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == session_id:
                    self.session_list.takeItem(i)
                    break
            
            # Delete from database
            # This would call the Rust backend
```

### Phase 3: Integration & Polish (Week 5)

#### Python-Rust Bridge Utilities:
```python
# nanogpt_chat/utils/wrappers.py
"""Wrapper utilities for Rust backend."""
import os
import sys
from pathlib import Path

# Add the Rust library to the path
RUST_LIB_DIR = Path(__file__).parent.parent.parent / "target" / "release"
if sys.platform == "darwin":
    RUST_LIB_DIR = Path(__file__).parent.parent.parent / "target" / "debug"

def get_rust_module():
    """Import the Rust module."""
    try:
        import nanogpt_core
        return nanogpt_core
    except ImportError:
        # Try to build if not found
        raise ImportError(
            "Rust module not found. Please build it first:\n"
            "  cd nanogpt-chat\n"
            "  cargo build --release\n"
            "  pip install -e ."
        )

# Lazy initialization
_api_client = None
_database = None

def get_api_client():
    """Get or create the API client."""
    global _api_client
    
    if _api_client is None:
        from nanogpt_core import PyNanoGPTClient
        
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key not configured")
        
        _api_client = PyNanoGPTClient(api_key)
    
    return _api_client

def get_database():
    """Get or create the database connection."""
    global _database
    
    if _database is None:
        from nanogpt_core import PyDatabase
        
        db_path = get_db_path()
        _database = PyDatabase(str(db_path))
    
    return _database

def get_api_key() -> str:
    """Get API key from secure storage."""
    try:
        from nanogpt_core import credential_manager
        return credential_manager.get_api_key()
    except ImportError:
        # Fallback to environment variable
        return os.environ.get("NANOGPT_API_KEY", "")

def set_api_key(api_key: str):
    """Save API key to secure storage."""
    try:
        from nanogpt_core import credential_manager
        credential_manager.set_api_key(api_key)
    except ImportError:
        os.environ["NANOGPT_API_KEY"] = api_key

def get_db_path() -> Path:
    """Get the database file path."""
    config_dir = Path.home() / ".config" / "nanogpt-chat"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "chat.db"

def get_settings() -> dict:
    """Load settings from file."""
    settings_file = Path.home() / ".config" / "nanogpt-chat" / "settings.json"
    
    if settings_file.exists():
        import json
        with open(settings_file) as f:
            return json.load(f)
    
    return {}

def save_settings(settings: dict):
    """Save settings to file."""
    import json
    
    settings_file = Path.home() / ".config" / "nanogpt-chat" / "settings.json"
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)
```

#### Application Entry Point:
```python
# nanogpt_chat/main.py
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from nanogpt_chat.ui.main_window import MainWindow


def setup_logging():
    """Set up logging for the application."""
    import logging
    
    log_dir = Path.home() / ".cache" / "nanogpt-chat"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(),
        ],
    )


def main():
    """Main entry point for the application."""
    # Set up logging
    setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("NanoGPT Chat")
    app.setOrganizationName("nanogpt")
    app.setDesktopFileName("com.nanogpt.Chat")
    
    # Set application-wide font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    # Set dark theme if preferred
    # app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### Phase 4: Build & Distribution (Week 6)

#### Build Script:
```bash
#!/bin/bash
# scripts/build.sh

set -e

echo "Building NanoGPT Chat..."

# Build Rust library
echo "Building Rust core..."
cd "$(dirname "$0")/.."
cargo build --release

# Install Python package
echo "Installing Python package..."
pip install -e .

echo "Build complete!"
echo ""
echo "To run the application:"
echo "  python -m nanogpt_chat"
```

#### Flatpak Manifest:
```yaml
# flatpak/com.nanogpt.Chat.yaml
app-id: com.nanogpt.Chat
runtime: org.freedesktop.Platform
runtime-version: "23.08"
sdk: org.freedesktop.Sdk
command: nanogpt-chat
finish-args:
  - --share=network
  - --filesystem=xdg-data
  - --filesystem=xdg-config
  - --system-talk-name=org.freedesktop.secrets
  - --env=PYTHONPATH=/app/lib/python3.11/site-packages

modules:
  - name: python3
    build-options:
      cflags: "-O2 -pipe"
    config-opts:
      - --enable-optimizations
      - --prefix=/app
    sources:
      - type: git
        url: https://github.com/python/cpython
        tag: v3.11.0

  - name: pyqt6
    buildsystem: simple
    build-commands:
      - pip install PyQt6 PyQt6-WebEngine
    sources:
      - type: pip
        url: https://pypi.org/simple/pyqt6/

  - name: nanogpt-chat
    buildsystem: simple
    build-commands:
      - pip install --prefix=/app -e .
      - install -D scripts/run.sh /app/bin/nanogpt-chat
      - install -D flatpak/com.nanogpt.Chat.desktop /app/share/applications/com.nanogpt.Chat.desktop
      - install -D flatpak/com.nanogpt.Chat.appdata.xml /app/share/metainfo/com.nanogpt.Chat.appdata.xml
      - install -D resources/icons/hicolor/*/apps/com.nanogpt.Chat.png /app/share/icons/hicolor/*/apps/
    sources:
      - type: dir
        path: .
```

## Development Timeline Summary

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1-2 | Rust Core | API client, database layer, credential storage, PyO3 bindings |
| 3-4 | PyQt6 GUI | Main window, chat widget, settings dialog, sidebar |
| 5 | Integration | Python-Rust bridge, application logic, testing |
| 6 | Distribution | Flatpak packaging, documentation, final polish |

## Quick Start Commands

```bash
# Clone repository
git clone https://github.com/yourusername/nanogpt-chat.git
cd nanogpt-chat

# Install Rust (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Build Rust library
cargo build --release

# Install Python dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Run the application
python -m nanogpt_chat

# Build Flatpak
flatpak-builder build flatpak/com.nanogpt.Chat.yaml
flatpak-builder --user install build com.nanogpt.Chat
```

This plan gives you a high-performance Rust backend with a modern, feature-rich PyQt6 GUI. The architecture ensures clean separation of concerns while maintaining excellent performance for API calls and data processing.

---

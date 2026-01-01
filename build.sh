#!/bin/bash
set -e

echo "Building NanoGPT Chat..."

# Create directories
mkdir -p nanogpt_chat/resources

# Build Rust library
echo "Building Rust core library..."
cargo build --release

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -e .

# Copy the Rust library to the Python package
if [ -f "target/release/libnanogpt_core.so" ]; then
    cp target/release/libnanogpt_core.so nanogpt_chat/
    echo "Copied libnanogpt_core.so to nanogpt_chat/"
elif [ -f "target/release/libnanogpt_core.dylib" ]; then
    cp target/release/libnanogpt_core.dylib nanogpt_chat/
    echo "Copied libnanogpt_core.dylib to nanogpt_chat/"
elif [ -f "target/release/nanogpt_core.pyd" ]; then
    cp target/release/nanogpt_core.pyd nanogpt_chat/
    echo "Copied nanogpt_core.pyd to nanogpt_chat/"
else
    echo "Warning: Could not find compiled Rust library"
fi

echo "Build complete!"
echo ""
echo "To run the application:"
echo "  python -m nanogpt_chat.main"

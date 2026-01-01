#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting build process...${NC}"

# Check for required tools
command -v cargo >/dev/null 2>&1 || { echo -e "${RED}Error: cargo is not installed.${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Error: python3 is not installed.${NC}"; exit 1; }

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Build Rust library
echo "Building Rust library..."
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo build --release

# Determine library extension based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    LIB_EXT="dylib"
else
    LIB_EXT="so"
fi

# Copy library to Python package
echo "Updating Python extension..."
cp target/release/libnanogpt_core.${LIB_EXT} nanogpt_chat/nanogpt_core.so

echo -e "${GREEN}Build successful!${NC}"
echo "To run the app: export PYTHONPATH=\$PYTHONPATH:. && python3 -m nanogpt_chat.main"

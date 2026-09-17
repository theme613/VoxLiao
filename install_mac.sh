#!/usr/bin/env bash
# VoxLiao macOS Setup & Dependency Installer
# Usage: ./install_mac.sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================"
echo "      VoxLiao macOS Setup Installer     "
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 was not found."
    if command -v brew &> /dev/null; then
        echo "Installing python3 via Homebrew..."
        brew install python
    else
        echo "Please install Python from https://www.python.org/downloads/mac-osx/"
        exit 1
    fi
fi

# Setup Virtual Environment
VENV_DIR="$DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Virtual Audio Device (BlackHole) option
echo ""
echo "----------------------------------------"
echo "Virtual Audio Driver (for Discord / Voice Chat)"
echo "----------------------------------------"
if command -v brew &> /dev/null; then
    read -p "Would you like to install BlackHole 2ch via Homebrew now? (y/N): " choice
    case "$choice" in 
      y|Y ) 
        echo "Installing BlackHole 2ch..."
        brew install blackhole-2ch || echo "Could not install BlackHole automatically. You can install it manually from https://github.com/ExistentialAudio/BlackHole"
        ;;
      * ) 
        echo "Skipping BlackHole installation."
        ;;
    esac
else
    echo "Tip: To send sounds to Discord, install BlackHole 2ch from:"
    echo "  https://github.com/ExistentialAudio/BlackHole"
fi

echo ""
echo "========================================"
echo "Installation complete! To run VoxLiao:"
echo "  ./run_mac.sh"
echo "========================================"

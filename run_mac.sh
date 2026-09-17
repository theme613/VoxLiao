#!/usr/bin/env bash
# VoxLiao macOS Runner Script
# Usage: ./run_mac.sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================"
echo "          Starting VoxLiao for Mac       "
echo "========================================"

# 1. Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    echo "Please install Python 3.10+ from https://www.python.org/downloads/ or via Homebrew: brew install python"
    exit 1
fi

# 2. Setup Virtual Environment
VENV_DIR="$DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# 3. Check and install dependencies
echo "Checking requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 4. Check for virtual audio driver on macOS
if command -v system_profiler &> /dev/null; then
    if ! system_profiler SPAudioDataType 2>/dev/null | grep -iqE "(blackhole|cable|virtual|loopback)"; then
        echo ""
        echo "Tip: No virtual audio cable detected (like BlackHole)."
        echo "To let others hear your sounds in Discord/game chat:"
        echo "  Install BlackHole via Homebrew: brew install blackhole-2ch"
        echo "  Or visit: https://github.com/ExistentialAudio/BlackHole"
        echo ""
    fi
fi

# 5. Launch VoxLiao
echo "Launching VoxLiao..."
python3 main.py

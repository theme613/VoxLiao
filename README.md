# VoxLiao

Offline Cross-Platform Soundboard for Gaming, Discord, Streaming, and Voice Chat (macOS & Windows).

## Features

- Play custom sound effects from a grid of responsive sound buttons.
- Cross-platform support for **macOS** and **Windows**.
- Built-in soundboard profiles with preloaded sound effects.
- Create, rename, duplicate, and manage profiles.
- Import MP3, WAV, OGG, and FLAC audio files with automatic sample-rate resampling.
- Global hotkeys for every sound (`pynput` on macOS / `keyboard` on Windows).
- Audio device selection with dynamic mono/stereo channel configuration.
- Local sound monitoring through headphones/speakers.
- Voice-chat routing with compatible virtual audio devices (BlackHole on Mac, VB-CABLE on Windows).
- Import and export complete soundboards (`.voxliao` packages).
- System tray / menu bar integration.
- Offline-first local storage.
- No account required.
- Created by Theme613.

---

## Running on macOS

### 1. Quick Start (One-Command Launch)

Open Terminal in the project directory and run:

```bash
chmod +x run_mac.sh
./run_mac.sh
```

This script will automatically:
1. Detect or set up a Python 3 virtual environment (`.venv`).
2. Install all required dependencies from `requirements.txt`.
3. Launch VoxLiao.

Alternatively, you can run manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### 2. macOS Permissions

macOS requires permissions for global hotkeys and microphone input:

1. **Microphone Access:** Prompted on first launch, or enable under:
   *System Settings > Privacy & Security > Microphone > Terminal / Python / VoxLiao*
2. **Global Hotkeys (Accessibility):** To trigger sounds with hotkeys while in other apps/games:
   *System Settings > Privacy & Security > Accessibility > Enable Terminal / Python / VoxLiao*

### 3. Voice Chat Audio Routing on macOS (Discord, Games)

To allow people in Discord or games to hear your sounds and voice:

1. **Install BlackHole (Free & Open Source):**
   ```bash
   brew install blackhole-2ch
   ```
   *Or download the installer from: [ExistentialAudio BlackHole](https://github.com/ExistentialAudio/BlackHole)*
2. In **VoxLiao** (`Settings > Audio Routing` or the Setup Wizard):
   - **Physical Microphone Input:** Set to your Mac mic (e.g., MacBook Microphone or USB Mic).
   - **Local Monitoring Device:** Set to your headphones (e.g., MacBook Speakers or AirPods).
   - **Voice Chat Output Device:** Set to `BlackHole 2ch`.
3. In **Discord** (`User Settings > Voice & Video`):
   - **Input Device:** Set to `BlackHole 2ch`.
   - **Output Device:** Keep as your headphones.
   - *Tip:* Turn off Discord's "Noise Suppression" (Krisp) if your soundboard effects sound muffled.

### 4. Building a Standalone macOS App (`.app` / `.dmg`)

To create a standalone macOS `.app` bundle:

```bash
python3 build_mac.py
```

This creates:
- `dist/VoxLiao.app` (macOS Application bundle)
- `dist/VoxLiao-macOS.zip` (portable release archive)
- `dist/VoxLiao-macOS.dmg` (disk image installer, when built on macOS)

You can launch it directly with:
```bash
open dist/VoxLiao.app
```

---

## Running on Windows

### Quick Start
1. Install VoxLiao using `VoxLiao-Setup.exe` (or run `python main.py` with dependencies from `requirements.txt`).
2. Open VoxLiao.
3. Configure virtual audio cable (`Settings > Audio Routing`).
4. Select sound profiles and play or assign hotkeys.

### Building for Windows
```bash
python build.py
```
Produces `dist/VoxLiao.exe`.

---

## Local Data Locations

VoxLiao stores profiles, settings, and imported sound files locally in standard OS paths:

- **macOS:** `~/Library/Application Support/VoxLiao/`
- **Windows:** `%APPDATA%\VoxLiao\`
- **Linux:** `~/.local/share/VoxLiao/`

---

## Automated Multi-Platform Builds (GitHub Actions)

This repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that automatically builds both:
- **macOS:** `VoxLiao.app` and `VoxLiao-macOS.zip`
- **Windows:** `VoxLiao.exe`

Whenever you push to `main` or trigger a build, you can download prebuilt binaries directly from the **Actions** tab on GitHub without needing a Mac physically present.

---

## Privacy

- VoxLiao works completely offline.
- VoxLiao does not require an account.
- VoxLiao does not upload sound files or microphone audio.
- VoxLiao does not track telemetry or analytics.

---

## Support

VoxLiao is independently created by Theme613.

Support link:
PASTE_YOUR_BUY_ME_A_COFFEE_OR_KO_FI_LINK_HERE

---

## Version

VoxLiao 1.1.0 (Cross-Platform macOS & Windows)

Created by Theme613.

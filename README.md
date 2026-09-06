# VoxLiao

Offline Soundboard for Gaming, Discord, Streaming, and Voice Chat

## Features

- Play custom sound effects from a grid of sound buttons.
- Built-in soundboard profiles.
- Create, rename, duplicate, and manage profiles.
- Import MP3, WAV, OGG, and FLAC sounds where supported.
- Global hotkeys for every sound.
- Audio-device selection.
- Local sound monitoring through headphones/speakers.
- Voice-chat routing with compatible virtual audio cable software.
- Import and export complete soundboards.
- System tray support.
- Offline-first local storage.
- No account required.
- Created by Theme613.

## Requirements

- Windows 10 or Windows 11.
- A working microphone for voice + sound mixing.
- Headphones strongly recommended to prevent echo.
- A compatible virtual audio cable only if you want other people in Discord/game voice chat to hear your sounds.

## Quick Start

1. Install VoxLiao using VoxLiao-Setup.exe.
2. Open VoxLiao from the Start Menu or desktop shortcut.
3. Select a sound profile.
4. Click an empty button with the plus icon.
5. Choose an audio file.
6. Name the sound.
7. Click the sound tile to play it.
8. Optionally assign a global hotkey.

## Let Others Hear Your Sounds

To let people in Discord, Valorant, or another voice-chat app hear VoxLiao sounds, configure a virtual audio cable.

Recommended audio path:

Real Microphone + VoxLiao Sound Effects
→ VoxLiao Audio Mixer
→ CABLE Input
→ CABLE Output
→ Discord/Game Microphone Input

Setup steps:

1. Install a compatible virtual audio cable.
2. In VoxLiao, open Settings > Audio Routing.
3. Set Physical Microphone Input to your real microphone.
4. Set Local Monitoring Device to your headphones.
5. Set Voice Chat Mix Output to CABLE Input.
6. In Discord, open User Settings > Voice & Video.
7. Set Input Device to CABLE Output.
8. Keep Discord Output Device set to your headphones.
9. Use Discord Mic Test and press a VoxLiao sound button.

Troubleshooting tips:

- Use headphones, not speakers, to avoid echo/feedback.
- If Discord cuts off sounds, test disabling Discord Noise Suppression.
- Consider disabling Discord Echo Cancellation and Automatic Gain Control if it removes sound effects.
- Confirm CABLE Input is selected in VoxLiao.
- Confirm CABLE Output is selected as Discord input.
- Restart VoxLiao after installing a virtual audio cable.
- Restart Windows if the virtual cable installer requires it.
- Verify that microphone privacy permission is enabled in Windows.
- Ensure the correct microphone is selected in VoxLiao.

## Importing Sounds

1. Click an empty tile or right-click an existing tile.
2. Select Add/Edit Sound.
3. Select an audio file.
4. Choose a display name, color, icon, volume, and hotkey.
5. Save.

Imported sounds are copied to a local user folder so they remain available even if the original file is moved.

Local data location:

%APPDATA%\VoxLiao\

## Exporting and Importing Soundboards

- Export a profile or all profiles through Settings > Profiles (Data tab).
- VoxLiao exports packages with the `.voxliao` extension.
- Imported packages may contain button configuration, profiles, icons, hotkeys, and audio files.
- Always export a backup before replacing existing profiles.

## Privacy

- VoxLiao works offline.
- VoxLiao does not require an account.
- VoxLiao does not upload sound files.
- VoxLiao does not upload microphone audio.
- VoxLiao does not use analytics or tracking.
- VoxLiao stores profiles and imported sound files locally.

## Support

VoxLiao is independently created by Theme613.

If you enjoy the app and want to support future updates, you can optionally buy the creator a coffee.

Support link:
PASTE_YOUR_BUY_ME_A_COFFEE_OR_KO_FI_LINK_HERE

## Legal Notice

VoxLiao is an independent application created by Theme613.

VoxLiao is not affiliated with, endorsed by, or sponsored by Discord, Riot Games, Valorant, Elgato, Stream Deck, VB-Audio, or any other third-party company or service.

Users are responsible for ensuring they have the rights to use, distribute, and play imported audio files.

Do not include copyrighted sound effects in commercial releases unless redistribution rights have been verified.

## Version

VoxLiao 1.0.0

Created by Theme613.

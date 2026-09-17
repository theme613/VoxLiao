# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('sound', 'sound')],
    hiddenimports=[
        'sounddevice',
        'soundfile',
        'numpy',
        'pynput',
        'pynput.keyboard._darwin',
        'pynput.mouse._darwin'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoxLiao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoxLiao',
)

app = BUNDLE(
    coll,
    name='VoxLiao.app',
    icon='icon.icns' if os.path.exists('icon.icns') else None,
    bundle_identifier='com.theme613.voxliao',
    info_plist={
        'NSMicrophoneUsageDescription': 'VoxLiao needs microphone access to mix your voice with sound effects.',
        'NSAppleEventsUsageDescription': 'VoxLiao needs AppleEvents access for global hotkeys.',
        'CFBundleDisplayName': 'VoxLiao',
        'CFBundleName': 'VoxLiao',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '1.0.0',
    },
)

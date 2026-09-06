import os
import subprocess
import sys

def build():
    print("Building VoxLiao with PyInstaller...")
    
    # ensure sound dir exists for PyInstaller
    if not os.path.exists('sound'):
        os.makedirs('sound')
        
    command = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=VoxLiao",
        "--add-data", "sound;sound",
        "--hidden-import", "sounddevice",
        "--hidden-import", "soundfile",
        "--hidden-import", "numpy",
        "--version-file=version.txt",
        "main.py"
    ]
    
    # Run pyinstaller
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Build successful!")
        print("Executable is located in the 'dist' folder (dist/VoxLiao.exe).")
    else:
        print("Build failed!")
        print(result.stderr)

if __name__ == "__main__":
    build()

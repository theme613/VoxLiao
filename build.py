import os
import subprocess
import sys

def build():
    is_mac = (sys.platform == 'darwin')
    is_win = (sys.platform == 'win32')
    
    print(f"Building VoxLiao for {sys.platform} with PyInstaller...")
    
    # Ensure sound directory exists
    if not os.path.exists('sound'):
        os.makedirs('sound')

    # Path separator for --add-data: ';' on Windows, ':' on Unix/Mac
    data_sep = ';' if is_win else ':'
    
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name=VoxLiao",
        "--add-data", f"sound{data_sep}sound",
        "--hidden-import", "sounddevice",
        "--hidden-import", "soundfile",
        "--hidden-import", "numpy",
        "--hidden-import", "pynput",
    ]
    
    if is_win:
        command.append("--onefile")
        command.extend(["--hidden-import", "keyboard"])
        if os.path.exists("version.txt"):
            command.append("--version-file=version.txt")
    elif is_mac:
        command.extend([
            "--onedir",
            "--osx-bundle-identifier=com.theme613.voxliao",
            "--hidden-import", "pynput.keyboard._darwin",
        ])
        if os.path.exists("icon.icns"):
            command.extend(["--icon", "icon.icns"])
        elif os.path.exists("icon.png"):
            command.extend(["--icon", "icon.png"])

    command.append("main.py")
    
    print("Executing:", " ".join(command))
    result = subprocess.run(command)
    
    if result.returncode == 0:
        print("\n=== Build Successful! ===")
        if is_mac:
            print("macOS Application Bundle is located at: dist/VoxLiao.app")
            print("You can run it via: open dist/VoxLiao.app")
        elif is_win:
            print("Windows Executable is located at: dist/VoxLiao.exe")
        else:
            print("Binary is located in: dist/VoxLiao")
    else:
        print("\n=== Build Failed! ===")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()

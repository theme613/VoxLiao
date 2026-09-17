import os
import subprocess
import sys
import shutil

def build_mac():
    print("=== Building VoxLiao for macOS ===")
    
    # Ensure sound directory exists
    if not os.path.exists('sound'):
        os.makedirs('sound')

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--onedir",
        "--name=VoxLiao",
        "--add-data", "sound:sound",
        "--hidden-import", "sounddevice",
        "--hidden-import", "soundfile",
        "--hidden-import", "numpy",
        "--hidden-import", "pynput",
        "--hidden-import", "pynput.keyboard._darwin",
        "--osx-bundle-identifier=com.theme613.voxliao",
    ]
    
    if os.path.exists("icon.icns"):
        pyinstaller_cmd.extend(["--icon", "icon.icns"])
    elif os.path.exists("icon.png"):
        pyinstaller_cmd.extend(["--icon", "icon.png"])
        
    pyinstaller_cmd.append("main.py")
    
    print("Running PyInstaller...")
    res = subprocess.run(pyinstaller_cmd)
    if res.returncode != 0:
        print("Error: PyInstaller build failed.")
        sys.exit(res.returncode)
        
    app_path = os.path.join("dist", "VoxLiao.app")
    if os.path.exists(app_path):
        print(f"\nCreated macOS Application Bundle: {app_path}")
        
        # Create a distributable zip archive of the .app
        zip_output = os.path.join("dist", "VoxLiao-macOS")
        print(f"Creating release archive: {zip_output}.zip ...")
        shutil.make_archive(zip_output, 'zip', root_dir="dist", base_dir="VoxLiao.app")
        print(f"Release archive created at: {zip_output}.zip")
        
        # Optionally create a DMG if hdiutil is available (native on macOS)
        if sys.platform == 'darwin' and shutil.which('hdiutil'):
            dmg_path = os.path.join("dist", "VoxLiao-macOS.dmg")
            print(f"Creating DMG image: {dmg_path} ...")
            try:
                subprocess.run([
                    "hdiutil", "create", "-volname", "VoxLiao",
                    "-srcfolder", app_path,
                    "-ov", "-format", "UDZO",
                    dmg_path
                ], check=True)
                print(f"DMG created at: {dmg_path}")
            except Exception as e:
                print(f"Warning: DMG creation skipped ({e})")
                
        print("\n=== macOS Build Complete! ===")
        print("To launch on Mac, run:")
        print("  open dist/VoxLiao.app")
    else:
        print(f"Error: Expected app bundle at {app_path} was not found.")

if __name__ == "__main__":
    build_mac()

import os
import subprocess
import sys
import shutil

def generate_icns():
    """ Converts icon.png to Apple icon.icns using native macOS tools (sips + iconutil) """
    if os.path.exists("icon.icns"):
        return "icon.icns"
        
    if not os.path.exists("icon.png") or sys.platform != 'darwin':
        return None
        
    if not shutil.which("sips") or not shutil.which("iconutil"):
        return None

    try:
        print("Generating icon.icns from icon.png...")
        iconset_dir = "VoxLiao.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        sizes = [16, 32, 64, 128, 256, 512]
        for s in sizes:
            subprocess.run([
                "sips", "-z", str(s), str(s), "icon.png", 
                "--out", os.path.join(iconset_dir, f"icon_{s}x{s}.png")
            ], capture_output=True, check=True)
            subprocess.run([
                "sips", "-z", str(s*2), str(s*2), "icon.png", 
                "--out", os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png")
            ], capture_output=True, check=True)
            
        subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", "icon.icns"], check=True)
        shutil.rmtree(iconset_dir, ignore_errors=True)
        print("icon.icns created successfully.")
        return "icon.icns"
    except Exception as e:
        print(f"Warning: Could not create .icns: {e}")
        return None

def build_mac():
    print("=== Building VoxLiao for macOS ===")
    
    # Ensure sound directory exists
    if not os.path.exists('sound'):
        os.makedirs('sound')

    icns_file = generate_icns()

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
    
    # macOS PyInstaller STRICTLY requires .icns format for --icon
    if icns_file and os.path.exists(icns_file):
        pyinstaller_cmd.extend(["--icon", icns_file])
        
    pyinstaller_cmd.append("main.py")
    
    print("Running PyInstaller...")
    print("Command:", " ".join(pyinstaller_cmd))
    res = subprocess.run(pyinstaller_cmd)
    if res.returncode != 0:
        print("Error: PyInstaller build failed.")
        sys.exit(res.returncode)
        
    app_path = os.path.join("dist", "VoxLiao.app")
    if not os.path.exists(app_path):
        print(f"Error: Expected app bundle at {app_path} was not found.")
        sys.exit(1)
        
    print(f"\n[1/3] Created macOS Application Bundle: {app_path}")
    
    # 1. Create a distributable zip archive of the .app
    zip_output = os.path.join("dist", "VoxLiao-macOS")
    print(f"Creating release archive: {zip_output}.zip ...")
    shutil.make_archive(zip_output, 'zip', root_dir="dist", base_dir="VoxLiao.app")
    print(f"Release archive created: {zip_output}.zip")
    
    # 2. Create standard drag-to-install DMG Disk Image
    if sys.platform == 'darwin' and shutil.which('hdiutil'):
        dmg_path = os.path.join("dist", "VoxLiao-macOS.dmg")
        staging_dir = os.path.join("dist", "dmg_staging")
        shutil.rmtree(staging_dir, ignore_errors=True)
        os.makedirs(staging_dir, exist_ok=True)
        
        # Copy VoxLiao.app to staging
        print("Staging files for DMG...")
        subprocess.run(["cp", "-R", app_path, os.path.join(staging_dir, "VoxLiao.app")], check=True)
        
        # Create Applications symlink for drag-and-drop install
        os.symlink("/Applications", os.path.join(staging_dir, "Applications"))
        
        print(f"[2/3] Building drag-and-drop DMG installer: {dmg_path} ...")
        try:
            subprocess.run([
                "hdiutil", "create", 
                "-volname", "VoxLiao Installer",
                "-srcfolder", staging_dir,
                "-ov", "-format", "UDZO",
                dmg_path
            ], check=True)
            print(f"DMG created successfully: {dmg_path}")
        except Exception as e:
            print(f"Warning: DMG creation skipped: {e}")
        finally:
            shutil.rmtree(staging_dir, ignore_errors=True)
            
    # 3. Create native macOS .pkg installer package
    if sys.platform == 'darwin' and shutil.which('pkgbuild'):
        pkg_path = os.path.join("dist", "VoxLiao-macOS.pkg")
        print(f"[3/3] Building Apple .pkg Installer Package: {pkg_path} ...")
        try:
            subprocess.run([
                "pkgbuild",
                "--install-location", "/Applications",
                "--component", app_path,
                pkg_path
            ], check=True)
            print(f".pkg installer created successfully: {pkg_path}")
        except Exception as e:
            print(f"Warning: .pkg creation skipped: {e}")
            
    print("\n=== macOS Build Complete! ===")
    print("Deliverables available in dist/:")
    for item in os.listdir("dist"):
        if item.endswith(('.dmg', '.pkg', '.zip', '.app')):
            print(f"  • dist/{item}")

if __name__ == "__main__":
    build_mac()

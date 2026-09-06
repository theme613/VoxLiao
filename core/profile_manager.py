import os
import sys
import json
import shutil
import zipfile

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

class ProfileManager:
    def __init__(self):
        self.app_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'VoxLiao')
        self.profiles_dir = os.path.join(self.app_data_dir, 'profiles')
        self.imported_sounds_dir = os.path.join(self.app_data_dir, 'imported_sounds')
        self.settings_file = os.path.join(self.app_data_dir, 'settings.json')
        
        self.ensure_directories()
        self.settings = self.load_settings()
        self.profiles = self.load_profiles()
        
        if not self.profiles:
            self.create_default_profiles()
            
    def ensure_directories(self):
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.imported_sounds_dir, exist_ok=True)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self.default_settings()

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def default_settings(self):
        return {
            "output_device": "default",
            "master_volume": 100,
            "theme": "light",
            "start_minimized": False,
            "close_to_tray": True,
            "stop_all_hotkey": "",
            "active_profile": "Profile 1"
        }

    def load_profiles(self):
        profiles = {}
        for f in os.listdir(self.profiles_dir):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(self.profiles_dir, f), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        profiles[data['name']] = data
                except:
                    pass
        return profiles

    def save_profile(self, profile_data):
        name = profile_data['name']
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filepath = os.path.join(self.profiles_dir, f"{safe_name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=4)
        self.profiles[name] = profile_data

    def create_default_profiles(self):
        default_names = ["Profile 1", "Profile 2", "Profile 3", "Profile 4", "Custom"]
        
        # Pre-configured sounds for Profile 1
        default_sounds = [
            ("Ayo Chill", "ayo chill.mp3", "#fef08a"),
            ("Boom", "boom.mp3", "#fca5a5"),
            ("Circus", "circus.mp3", "#bbf7d0"),
            ("Fart", "fart.mp3", "#fed7aa"),
            ("Outro", "outro.mp3", "#bfdbfe"),
            ("Rizz", "rizz.mp3", "#e9d5ff"),
            ("Rommance", "rommance.mp3", "#fbcfe8"),
            ("Shut Ur Mouth", "shut ur mouth.mp3", "#cbd5e1"),
            ("SpongeBob Sad", "spongebob sad.mp3", "#fef9c3"),
            ("What A Good Boy", "what a good boy.mp3", "#a7f3d0")
        ]

        for name in default_names:
            profile = {
                "name": name,
                "buttons": []
            }
            
            for i in range(10):
                if name == "Profile 1" and i < len(default_sounds):
                    d_name, d_file, d_color = default_sounds[i]
                    profile["buttons"].append({
                        "id": i,
                        "name": d_name,
                        "file": resource_path(f"sound/{d_file}"),
                        "hotkey": "",
                        "color": d_color,
                        "text_color": "#000000",
                        "volume": 100,
                        "mode": "play_once"
                    })
                else:
                    profile["buttons"].append({
                        "id": i,
                        "name": "Add sound",
                        "file": "",
                        "hotkey": "",
                        "color": "#ffffff",
                        "text_color": "#000000",
                        "volume": 100,
                        "mode": "play_once"
                    })
            self.save_profile(profile)

    def import_sound_file(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return ""
        # Don't copy if it's one of the built-in sounds in MEIPASS
        if "MEIPASS" in filepath or "sound\\" in filepath or "sound/" in filepath:
            # We assume it's already a built-in sound if it's from our sound folder
            return filepath
            
        filename = os.path.basename(filepath)
        dest = os.path.join(self.imported_sounds_dir, filename)
        if filepath != dest:
            shutil.copy2(filepath, dest)
        return dest

    def export_soundboard(self, dest_zip_path):
        """ Exports profiles and imported sounds to a zip file """
        with zipfile.ZipFile(dest_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add profiles
            for root, dirs, files in os.walk(self.profiles_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    zipf.write(filepath, arcname=os.path.join('profiles', file))
            # Add sounds
            for root, dirs, files in os.walk(self.imported_sounds_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    zipf.write(filepath, arcname=os.path.join('imported_sounds', file))

    def import_soundboard(self, src_zip_path):
        """ Imports profiles and sounds from a zip file """
        with zipfile.ZipFile(src_zip_path, 'r') as zipf:
            zipf.extractall(self.app_data_dir)
        self.profiles = self.load_profiles()

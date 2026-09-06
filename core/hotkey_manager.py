import keyboard
from PySide6.QtCore import QObject, Signal

class HotkeyManager(QObject):
    hotkey_triggered = Signal(int) # button id
    stop_all_triggered = Signal()

    def __init__(self, profile_manager):
        super().__init__()
        self.profile_manager = profile_manager
        self.registered_hotkeys = {}
        self.stop_all_hotkey = None
        
    def refresh_hotkeys(self, current_profile_name):
        keyboard.unhook_all()
        self.registered_hotkeys.clear()
        
        # Stop all hotkey
        stop_all = self.profile_manager.settings.get('stop_all_hotkey', '')
        if stop_all:
            try:
                keyboard.add_hotkey(stop_all, self.stop_all_triggered.emit, suppress=False)
                self.stop_all_hotkey = stop_all
            except Exception as e:
                print(f"Failed to bind stop all hotkey: {e}")

        # Button hotkeys
        profile = self.profile_manager.profiles.get(current_profile_name)
        if not profile:
            return
            
        for button in profile.get('buttons', []):
            hk = button.get('hotkey', '')
            bid = button.get('id')
            if hk:
                try:
                    # Using a default argument in the lambda to bind the current value of bid
                    keyboard.add_hotkey(hk, lambda b=bid: self.hotkey_triggered.emit(b), suppress=False)
                    self.registered_hotkeys[bid] = hk
                except Exception as e:
                    print(f"Failed to bind hotkey {hk} for button {bid}: {e}")

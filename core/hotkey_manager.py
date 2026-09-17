import sys
import threading
from PySide6.QtCore import QObject, Signal

# Try importing pynput (standard for macOS and cross-platform)
try:
    from pynput import keyboard as pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

# Try importing keyboard (Windows fallback)
try:
    import keyboard as win_keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False


def normalize_for_pynput(hotkey_str):
    """
    Convert a hotkey string (e.g., 'ctrl+alt+a', 'F1', 'cmd+shift+x')
    to pynput GlobalHotKeys format (e.g., '<ctrl>+<alt>+a', '<f1>', '<cmd>+<shift>+x').
    """
    if not hotkey_str:
        return ""
        
    parts = [p.strip().lower() for p in hotkey_str.split('+') if p.strip()]
    special_keys = {
        'ctrl': '<ctrl>',
        'control': '<ctrl>',
        'alt': '<alt>',
        'opt': '<alt>',
        'option': '<alt>',
        'shift': '<shift>',
        'cmd': '<cmd>',
        'command': '<cmd>',
        'super': '<cmd>',
        'win': '<cmd>',
        'windows': '<cmd>',
        'space': '<space>',
        'enter': '<enter>',
        'return': '<enter>',
        'esc': '<esc>',
        'escape': '<esc>',
        'tab': '<tab>',
        'backspace': '<backspace>',
        'delete': '<delete>',
        'up': '<up>',
        'down': '<down>',
        'left': '<left>',
        'right': '<right>',
    }
    
    formatted_parts = []
    for p in parts:
        if p in special_keys:
            formatted_parts.append(special_keys[p])
        elif p.startswith('f') and p[1:].isdigit():
            formatted_parts.append(f"<{p}>")
        elif len(p) == 1:
            formatted_parts.append(p)
        else:
            formatted_parts.append(f"<{p}>")
            
    return "+".join(formatted_parts)


class HotkeyManager(QObject):
    hotkey_triggered = Signal(int)  # button id
    stop_all_triggered = Signal()

    def __init__(self, profile_manager):
        super().__init__()
        self.profile_manager = profile_manager
        self.registered_hotkeys = {}
        self.stop_all_hotkey = None
        self.pynput_listener = None
        self._lock = threading.Lock()

    def stop(self):
        """ Stop any active hotkey listeners """
        with self._lock:
            if self.pynput_listener:
                try:
                    self.pynput_listener.stop()
                except Exception:
                    pass
                self.pynput_listener = None
                
            if HAS_KEYBOARD:
                try:
                    win_keyboard.unhook_all()
                except Exception:
                    pass

    def refresh_hotkeys(self, current_profile_name):
        self.stop()
        self.registered_hotkeys.clear()
        
        stop_all = self.profile_manager.settings.get('stop_all_hotkey', '')
        self.stop_all_hotkey = stop_all
        
        profile = self.profile_manager.profiles.get(current_profile_name)
        buttons = profile.get('buttons', []) if profile else []

        # Prefer pynput on macOS or when keyboard is not available
        use_pynput = (sys.platform == 'darwin') or HAS_PYNPUT or not HAS_KEYBOARD

        if use_pynput and HAS_PYNPUT:
            self._setup_pynput(stop_all, buttons)
        elif HAS_KEYBOARD:
            self._setup_win_keyboard(stop_all, buttons)
        else:
            print("[VoxLiao] No compatible hotkey library found (pynput or keyboard). Hotkeys disabled.")

    def _setup_pynput(self, stop_all, buttons):
        hotkey_map = {}
        
        if stop_all:
            norm = normalize_for_pynput(stop_all)
            if norm:
                hotkey_map[norm] = lambda: self.stop_all_triggered.emit()

        for button in buttons:
            hk = button.get('hotkey', '')
            bid = button.get('id')
            if hk:
                norm = normalize_for_pynput(hk)
                if norm:
                    hotkey_map[norm] = lambda b=bid: self.hotkey_triggered.emit(b)
                    self.registered_hotkeys[bid] = hk

        if hotkey_map:
            try:
                self.pynput_listener = pynput_keyboard.GlobalHotKeys(hotkey_map)
                self.pynput_listener.daemon = True
                self.pynput_listener.start()
            except Exception as e:
                print(f"[VoxLiao] Failed to initialize pynput hotkeys: {e}")
                if sys.platform == 'darwin':
                    print("[VoxLiao] Tip: On macOS, enable Accessibility permissions in:")
                    print("  System Settings > Privacy & Security > Accessibility")

    def _setup_win_keyboard(self, stop_all, buttons):
        if stop_all:
            try:
                win_keyboard.add_hotkey(stop_all, self.stop_all_triggered.emit, suppress=False)
            except Exception as e:
                print(f"[VoxLiao] Failed to bind stop-all hotkey '{stop_all}': {e}")

        for button in buttons:
            hk = button.get('hotkey', '')
            bid = button.get('id')
            if hk:
                try:
                    win_keyboard.add_hotkey(hk, lambda b=bid: self.hotkey_triggered.emit(b), suppress=False)
                    self.registered_hotkeys[bid] = hk
                except Exception as e:
                    print(f"[VoxLiao] Failed to bind hotkey '{hk}' for button {bid}: {e}")

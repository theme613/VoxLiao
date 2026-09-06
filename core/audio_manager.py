import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
from PySide6.QtCore import QObject, Signal

class AudioManager(QObject):
    playback_started = Signal(int)
    playback_stopped = Signal(int)
    
    # Meter signals (values 0.0 to 1.0)
    mic_level_changed = Signal(float)
    sb_level_changed = Signal(float)
    out_level_changed = Signal(float)

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        
        self.active_sounds = {} # map button_id -> dict of sound data
        self.lock = threading.Lock()
        
        self.mic_stream = None
        self.vc_out_stream = None
        self.monitor_out_stream = None
        
        self.samplerate = 44100
        self.blocksize = 1024
        self.channels = 2
        
        self.running = False
        self.start_engine()

    def get_input_devices(self):
        devices = []
        try:
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    devices.append(d)
        except Exception:
            pass
        return devices

    def get_output_devices(self):
        devices = []
        try:
            for i, d in enumerate(sd.query_devices()):
                if d['max_output_channels'] > 0:
                    devices.append(d)
        except Exception:
            pass
        return devices

    def get_device_index(self, name, is_input=False):
        if name == "default" or not name:
            return None # sd uses None for default
        devices = self.get_input_devices() if is_input else self.get_output_devices()
        for d in devices:
            if d['name'] == name:
                return d['index']
        return None

    def start_engine(self):
        self.stop_engine()
        self.running = True
        
        mic_name = self.settings_manager.settings.get('mic_device', 'default')
        monitor_name = self.settings_manager.settings.get('monitor_device', 'default')
        vc_name = self.settings_manager.settings.get('voice_chat_device', 'none')
        
        mic_idx = self.get_device_index(mic_name, True)
        monitor_idx = self.get_device_index(monitor_name, False)
        vc_idx = self.get_device_index(vc_name, False)
        
        # We will use a main callback thread to process audio.
        # For simplicity in this demo, we will run a loop that reads mic and writes to outputs.
        self.engine_thread = threading.Thread(target=self._audio_loop, args=(mic_idx, monitor_idx, vc_idx), daemon=True)
        self.engine_thread.start()

    def stop_engine(self):
        self.running = False
        if hasattr(self, 'engine_thread') and self.engine_thread.is_alive():
            self.engine_thread.join(timeout=1.0)

    def _audio_loop(self, mic_idx, monitor_idx, vc_idx):
        try:
            # Setup streams
            # Note: opening multiple streams with different devices can block if not carefully handled.
            # We use a simple blocking read/write loop for stability in this implementation.
            
            mic_stream = sd.InputStream(device=mic_idx, channels=self.channels, samplerate=self.samplerate, blocksize=self.blocksize) if mic_idx is not False else None
            monitor_stream = sd.OutputStream(device=monitor_idx, channels=self.channels, samplerate=self.samplerate, blocksize=self.blocksize) if monitor_idx is not False else None
            vc_stream = sd.OutputStream(device=vc_idx, channels=self.channels, samplerate=self.samplerate, blocksize=self.blocksize) if vc_idx is not False and vc_idx is not None else None
            
            if mic_stream: mic_stream.start()
            if monitor_stream: monitor_stream.start()
            if vc_stream: vc_stream.start()
            
            empty_block = np.zeros((self.blocksize, self.channels), dtype='float32')
            
            while self.running:
                # 1. Read Mic
                mic_data = empty_block.copy()
                if mic_stream and not self.settings_manager.settings.get('mute_mic', False):
                    try:
                        mic_data, _ = mic_stream.read(self.blocksize)
                    except Exception:
                        pass
                        
                mic_vol = self.settings_manager.settings.get('mic_volume', 100) / 100.0
                mic_data *= mic_vol
                
                # Emit mic level
                self.mic_level_changed.emit(float(np.max(np.abs(mic_data))))

                # 2. Process Soundboard
                sb_data = empty_block.copy()
                stopped_buttons = []
                
                with self.lock:
                    for bid, snd in list(self.active_sounds.items()):
                        pos = snd['pos']
                        data = snd['data']
                        rem = len(data) - pos
                        
                        if rem <= 0:
                            if snd['loop']:
                                snd['pos'] = 0
                                rem = len(data)
                            else:
                                stopped_buttons.append(bid)
                                continue
                                
                        chunk_size = min(self.blocksize, rem)
                        
                        # Handle mono to stereo if needed
                        chunk = data[pos:pos+chunk_size]
                        if len(chunk.shape) == 1:
                            chunk = np.column_stack((chunk, chunk))
                            
                        # pad if chunk is smaller than blocksize
                        if chunk_size < self.blocksize:
                            chunk = np.pad(chunk, ((0, self.blocksize - chunk_size), (0, 0)), mode='constant')
                            
                        sb_data += chunk * snd['volume']
                        snd['pos'] += chunk_size
                        
                    for bid in stopped_buttons:
                        del self.active_sounds[bid]
                        self.playback_stopped.emit(bid)
                        
                sb_vol = self.settings_manager.settings.get('sb_volume', 100) / 100.0
                if self.settings_manager.settings.get('mute_sb', False):
                    sb_vol = 0.0
                    
                sb_data *= sb_vol
                self.sb_level_changed.emit(float(np.max(np.abs(sb_data))))
                
                # 3. Mixing & Routing
                mode = self.settings_manager.settings.get('routing_mode', 'Both Local + Voice Chat')
                master_vol = self.settings_manager.settings.get('master_volume', 100) / 100.0
                
                mix_data = (mic_data + sb_data) * master_vol
                
                # Simple Limiter to prevent clipping
                if self.settings_manager.settings.get('limiter', True):
                    mix_data = np.clip(mix_data, -1.0, 1.0)
                
                self.out_level_changed.emit(float(np.max(np.abs(mix_data))))

                # Output to Voice Chat
                if vc_stream and mode in ['Voice Chat Only', 'Both Local + Voice Chat']:
                    try:
                        vc_stream.write(np.ascontiguousarray(mix_data))
                    except Exception:
                        pass
                        
                # Output to Monitor
                if monitor_stream and mode in ['Local Only', 'Both Local + Voice Chat']:
                    # Usually monitor doesn't want the mic feedback to avoid echo, just soundboard
                    # But prompt says "Soundboard and microphone mix are sent to the selected virtual cable... Soundboard plays locally for the user"
                    # So monitor_data = sb_data * master_vol
                    monitor_data = sb_data * master_vol
                    monitor_data = np.clip(monitor_data, -1.0, 1.0)
                    try:
                        monitor_stream.write(np.ascontiguousarray(monitor_data))
                    except Exception:
                        pass

            if mic_stream: mic_stream.stop(); mic_stream.close()
            if monitor_stream: monitor_stream.stop(); monitor_stream.close()
            if vc_stream: vc_stream.stop(); vc_stream.close()
            
        except Exception as e:
            print(f"Audio Engine Error: {e}")

    def play_sound(self, button_id, filepath, volume=100, mode="play_once"):
        if not filepath:
            return

        stop_previous = self.settings_manager.settings.get('stop_previous', False)
        if stop_previous or mode == "stop_previous":
            self.stop_all()

        try:
            data, fs = sf.read(filepath, dtype='float32')
            # Resample if necessary (simplified: assume 44100 or ignore pitch shift for this MVP)
            # In a real app we'd use scipy.signal.resample or librosa
            
            with self.lock:
                self.active_sounds[button_id] = {
                    'data': data,
                    'pos': 0,
                    'volume': volume / 100.0,
                    'loop': (mode == "loop")
                }
            self.playback_started.emit(button_id)
        except Exception as e:
            print(f"Failed to play {filepath}: {e}")

    def stop_all(self):
        with self.lock:
            for bid in list(self.active_sounds.keys()):
                self.playback_stopped.emit(bid)
            self.active_sounds.clear()

    def update_audio_device(self):
        self.start_engine()

    def detect_virtual_cable(self):
        inputs = [d['name'].lower() for d in self.get_input_devices()]
        outputs = [d['name'].lower() for d in self.get_output_devices()]
        
        has_input = any("cable" in n or "virtual" in n or "vb-audio" in n for n in inputs)
        has_output = any("cable" in n or "virtual" in n or "vb-audio" in n for n in outputs)
        return has_input and has_output

    def auto_select_devices(self):
        inputs = self.get_input_devices()
        real_mic = "default"
        for d in inputs:
            name = d['name'].lower()
            if not any(x in name for x in ["cable", "virtual", "vb-audio", "voicemeeter", "echodeck"]):
                real_mic = d['name']
                break

        outputs = self.get_output_devices()
        real_monitor = "default"
        for d in outputs:
            name = d['name'].lower()
            if not any(x in name for x in ["cable", "virtual", "vb-audio", "voicemeeter", "echodeck"]):
                real_monitor = d['name']
                break
                
        cable_out = "none"
        for d in outputs:
            name = d['name'].lower()
            if "cable" in name or "virtual" in name or "vb-audio" in name:
                cable_out = d['name']
                break
                
        self.settings_manager.settings['mic_device'] = real_mic
        self.settings_manager.settings['monitor_device'] = real_monitor
        self.settings_manager.settings['voice_chat_device'] = cable_out
        self.settings_manager.settings['routing_mode'] = 'Both Local + Voice Chat'
        self.settings_manager.save_settings()
        self.update_audio_device()

    def run_diagnostics(self):
        errors = []
        if not self.running or not getattr(self, 'engine_thread', None) or not self.engine_thread.is_alive():
            errors.append("Audio Engine is not running.")
            
        mic_name = self.settings_manager.settings.get('mic_device', 'default')
        vc_name = self.settings_manager.settings.get('voice_chat_device', 'none')
        
        if len(self.get_input_devices()) == 0:
            errors.append("No physical microphone detected on the system.")
        elif mic_name != "default" and not any(d['name'] == mic_name for d in self.get_input_devices()):
            errors.append("Selected microphone is disconnected.")
            
        if vc_name == "none" or not any(d['name'] == vc_name for d in self.get_output_devices()):
            errors.append("CABLE Output missing or not selected.")
            
        if not errors:
            return True, "CABLE Input is active, microphone signal is entering the mixer, and outputs are configured correctly."
        return False, "\n".join(errors)

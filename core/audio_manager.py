import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
from PySide6.QtCore import QObject, Signal

VIRTUAL_AUDIO_KEYWORDS = [
    "cable", "virtual", "vb-audio", "blackhole", 
    "soundflower", "loopback", "voicemeeter", "echodeck"
]

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
        
        self.active_sounds = {}  # map button_id -> dict of sound data
        self.lock = threading.Lock()
        
        self.samplerate = 44100
        self.blocksize = 1024
        self.channels = 2
        
        self.running = False
        self.start_engine()

    def get_input_devices(self):
        devices = []
        try:
            for d in sd.query_devices():
                if d['max_input_channels'] > 0:
                    devices.append(d)
        except Exception:
            pass
        return devices

    def get_output_devices(self):
        devices = []
        try:
            for d in sd.query_devices():
                if d['max_output_channels'] > 0:
                    devices.append(d)
        except Exception:
            pass
        return devices

    def get_device_index(self, name, is_input=False):
        if name == "default" or not name:
            return None  # sd uses None for default
        devices = self.get_input_devices() if is_input else self.get_output_devices()
        for d in devices:
            if d['name'] == name:
                return d['index']
        return None

    def _get_supported_channels(self, dev_idx, is_input=True):
        """ Returns the safe channel count (1 or 2) supported by the device """
        try:
            if dev_idx is None:
                info = sd.query_devices(kind='input' if is_input else 'output')
            else:
                info = sd.query_devices(dev_idx)
            max_ch = info['max_input_channels'] if is_input else info['max_output_channels']
            return max(1, min(self.channels, max_ch))
        except Exception:
            return self.channels

    def start_engine(self):
        self.stop_engine()
        self.running = True
        
        mic_name = self.settings_manager.settings.get('mic_device', 'default')
        monitor_name = self.settings_manager.settings.get('monitor_device', 'default')
        vc_name = self.settings_manager.settings.get('voice_chat_device', 'none')
        
        mic_idx = self.get_device_index(mic_name, True)
        monitor_idx = self.get_device_index(monitor_name, False)
        vc_idx = self.get_device_index(vc_name, False)
        
        self.engine_thread = threading.Thread(
            target=self._audio_loop, 
            args=(mic_idx, monitor_idx, vc_idx), 
            daemon=True
        )
        self.engine_thread.start()

    def stop_engine(self):
        self.running = False
        if hasattr(self, 'engine_thread') and self.engine_thread.is_alive():
            self.engine_thread.join(timeout=1.0)

    def _audio_loop(self, mic_idx, monitor_idx, vc_idx):
        mic_stream = None
        monitor_stream = None
        vc_stream = None
        
        mic_channels = self._get_supported_channels(mic_idx, is_input=True)
        monitor_channels = self._get_supported_channels(monitor_idx, is_input=False)
        vc_channels = self._get_supported_channels(vc_idx, is_input=False) if (vc_idx is not None and vc_idx is not False) else 2

        try:
            # 1. Initialize Microphone Stream
            if mic_idx is not False:
                try:
                    mic_stream = sd.InputStream(
                        device=mic_idx, 
                        channels=mic_channels, 
                        samplerate=self.samplerate, 
                        blocksize=self.blocksize
                    )
                    mic_stream.start()
                except Exception as e:
                    print(f"[VoxLiao] Could not open microphone stream: {e}")
                    mic_stream = None

            # 2. Initialize Monitor Stream (Headphones)
            if monitor_idx is not False:
                try:
                    monitor_stream = sd.OutputStream(
                        device=monitor_idx, 
                        channels=monitor_channels, 
                        samplerate=self.samplerate, 
                        blocksize=self.blocksize
                    )
                    monitor_stream.start()
                except Exception as e:
                    print(f"[VoxLiao] Could not open monitor stream: {e}")
                    monitor_stream = None

            # 3. Initialize Voice Chat Stream (Virtual Cable / BlackHole)
            if vc_idx is not False and vc_idx is not None:
                try:
                    vc_stream = sd.OutputStream(
                        device=vc_idx, 
                        channels=vc_channels, 
                        samplerate=self.samplerate, 
                        blocksize=self.blocksize
                    )
                    vc_stream.start()
                except Exception as e:
                    print(f"[VoxLiao] Could not open voice chat stream: {e}")
                    vc_stream = None
            
            empty_block = np.zeros((self.blocksize, self.channels), dtype='float32')
            
            while self.running:
                # 1. Read Mic
                mic_data = empty_block.copy()
                if mic_stream and not self.settings_manager.settings.get('mute_mic', False):
                    try:
                        raw_mic, _ = mic_stream.read(self.blocksize)
                        if mic_channels == 1:
                            # Expand mono to stereo
                            mic_data = np.column_stack((raw_mic, raw_mic))
                        else:
                            mic_data = raw_mic
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
                        chunk = data[pos:pos+chunk_size]
                        
                        # Handle mono to stereo if needed
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
                        out_chunk = mix_data[:, 0:1] if vc_channels == 1 else mix_data
                        vc_stream.write(np.ascontiguousarray(out_chunk, dtype='float32'))
                    except Exception:
                        pass
                        
                # Output to Monitor (Headphones)
                if monitor_stream and mode in ['Local Only', 'Both Local + Voice Chat']:
                    monitor_data = sb_data * master_vol
                    if self.settings_manager.settings.get('limiter', True):
                        monitor_data = np.clip(monitor_data, -1.0, 1.0)
                    try:
                        out_chunk = monitor_data[:, 0:1] if monitor_channels == 1 else monitor_data
                        monitor_stream.write(np.ascontiguousarray(out_chunk, dtype='float32'))
                    except Exception:
                        pass

        except Exception as e:
            print(f"[VoxLiao] Audio Engine Error: {e}")
        finally:
            if mic_stream:
                try: mic_stream.stop(); mic_stream.close()
                except Exception: pass
            if monitor_stream:
                try: monitor_stream.stop(); monitor_stream.close()
                except Exception: pass
            if vc_stream:
                try: vc_stream.stop(); vc_stream.close()
                except Exception: pass

    def play_sound(self, button_id, filepath, volume=100, mode="play_once"):
        if not filepath:
            return

        stop_previous = self.settings_manager.settings.get('stop_previous', False)
        if stop_previous or mode == "stop_previous":
            self.stop_all()

        try:
            data, fs = sf.read(filepath, dtype='float32')
            
            # Resample audio to match engine sample rate if needed
            if fs != self.samplerate and fs > 0 and len(data) > 0:
                new_len = int(round(len(data) * float(self.samplerate) / fs))
                if len(data.shape) == 1:
                    data = np.interp(
                        np.linspace(0, len(data), new_len, endpoint=False), 
                        np.arange(len(data)), 
                        data
                    ).astype('float32')
                else:
                    chans = [
                        np.interp(
                            np.linspace(0, len(data), new_len, endpoint=False), 
                            np.arange(len(data)), 
                            data[:, c]
                        )
                        for c in range(data.shape[1])
                    ]
                    data = np.column_stack(chans).astype('float32')
            
            with self.lock:
                self.active_sounds[button_id] = {
                    'data': data,
                    'pos': 0,
                    'volume': volume / 100.0,
                    'loop': (mode == "loop")
                }
            self.playback_started.emit(button_id)
        except Exception as e:
            print(f"[VoxLiao] Failed to play {filepath}: {e}")

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
        
        has_input = any(any(k in n for k in VIRTUAL_AUDIO_KEYWORDS) for n in inputs)
        has_output = any(any(k in n for k in VIRTUAL_AUDIO_KEYWORDS) for n in outputs)
        return has_input or has_output

    def auto_select_devices(self):
        inputs = self.get_input_devices()
        real_mic = "default"
        for d in inputs:
            name = d['name'].lower()
            if not any(x in name for x in VIRTUAL_AUDIO_KEYWORDS):
                real_mic = d['name']
                break

        outputs = self.get_output_devices()
        real_monitor = "default"
        for d in outputs:
            name = d['name'].lower()
            if not any(x in name for x in VIRTUAL_AUDIO_KEYWORDS):
                real_monitor = d['name']
                break
                
        cable_out = "none"
        for d in outputs:
            name = d['name'].lower()
            if any(x in name for x in VIRTUAL_AUDIO_KEYWORDS):
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
            errors.append("Virtual audio cable (e.g. BlackHole or CABLE) output is missing or not selected.")
            
        if not errors:
            return True, "Virtual Audio Cable / Output is active, microphone signal is entering the mixer, and outputs are configured correctly."
        return False, "\n".join(errors)

import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "engine": "gemini",  # "gemini" or "local"
    "gemini": {
        "api_key": "",   # Read from GEMINI_API_KEY env var if empty
        "model": "gemini-2.0-flash",
    },
    "local": {
        "endpoint": "http://localhost:11434",  # Ollama running on RTX 4050
        "model": "qwen2-vl:2b",                # Lightweight vision model fitting RTX 4050 6GB VRAM
        "timeout": 30,
    },
    "interaction": {
        "default_mode": "guide",  # "guide" (Show & Guide) or "autopilot" (Clicks for you)
        "hotkey": "<ctrl>+<alt>+c",
        "emergency_abort_key": "esc",
        "mouse_shake_abort": True,
    },
    "audio": {
        "enabled": True,
        "rate": 175,
        "volume": 0.95,
        "voice_index": 0,
        "listen_timeout": 5,
    },
    "visual": {
        "ghost_cursor_color": "#00E5FF",      # Cyber Cyan
        "pulse_ring_color": "#B388FF",        # Electric Lavender
        "highlight_box_color": "#00E676",     # Neon Green
        "text_color": "#FFFFFF",
        "hud_bg": "#12141A",
        "glow_radius": 36,
        "animation_fps": 60,
    }
}

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.data = DEFAULT_CONFIG.copy()
        self._load_env()
        self.load()

    def _load_env(self):
        """Reads .env from current directory or home directory if present."""
        for env_path in [Path(".env"), Path.home() / ".env"]:
            if env_path.exists():
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip("\"'")
                                if k and not os.environ.get(k):
                                    os.environ[k] = v
                except Exception as e:
                    print(f"[Config] Note reading {env_path}: {e}")

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_data = yaml.safe_load(f) or {}
                    self._deep_update(self.data, user_data)
            except Exception as e:
                print(f"[Config] Error loading {self.config_path}: {e}. Using defaults.")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"[Config] Error saving {self.config_path}: {e}")

    def _deep_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def get(self, key_path, default=None):
        keys = key_path.split(".")
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path, value):
        keys = key_path.split(".")
        d = self.data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save()

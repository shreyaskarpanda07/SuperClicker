import sys
import ctypes
import os
import io
import time
from typing import Tuple, Dict, Any, Optional
from PIL import Image
import mss

# Enable DPI awareness on Windows so pixel coordinates are exact
try:
    if sys.platform == "win32":
        # Per-monitor DPI aware (value 2)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    import win32gui
    import win32process
    import psutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class ScreenManager:
    """
    Handles fast screenshot capture, multi-monitor bounds, DPI scaling,
    and active window context detection (DaVinci, FL Studio, Figma, VS Code).
    """
    def __init__(self):
        try:
            self.sct = mss.MSS()
        except AttributeError:
            self.sct = mss.mss()
        self._detect_monitors()

    def _detect_monitors(self):
        # Index 0 is the virtual combined monitor, index 1 is primary
        self.monitors = self.sct.monitors
        self.primary_monitor = self.monitors[1] if len(self.monitors) > 1 else self.monitors[0]
        self.width = self.primary_monitor["width"]
        self.height = self.primary_monitor["height"]
        self.left = self.primary_monitor["left"]
        self.top = self.primary_monitor["top"]

    def capture_screen(self, monitor_idx: int = 1) -> Image.Image:
        """Captures a screenshot of the specified monitor and returns a PIL Image."""
        if monitor_idx >= len(self.monitors):
            monitor_idx = 1 if len(self.monitors) > 1 else 0
        sct_img = self.sct.grab(self.monitors[monitor_idx])
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img

    def capture_screen_bytes(self, monitor_idx: int = 1, format="JPEG", quality=85) -> bytes:
        """Captures screenshot directly as compressed bytes for fast network sending."""
        img = self.capture_screen(monitor_idx)
        buffer = io.BytesIO()
        img.save(buffer, format=format, quality=quality)
        return buffer.getvalue()

    def get_active_window_info(self) -> Dict[str, Any]:
        """
        Returns info about the currently active foreground window:
        title, process name, identified app (e.g. 'davinci', 'fl_studio', 'figma', 'vscode'),
        and bounding box.
        """
        info = {
            "title": "Desktop / Unknown",
            "process": "",
            "app_type": "generic",
            "rect": (0, 0, self.width, self.height)
        }

        if not WIN32_AVAILABLE:
            return info

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return info

            title = win32gui.GetWindowText(hwnd)
            info["title"] = title

            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid:
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name().lower()
                    info["process"] = proc_name
                except Exception:
                    proc_name = ""
            else:
                proc_name = ""

            # Window Rect
            rect = win32gui.GetWindowRect(hwnd)
            info["rect"] = rect

            # App type classification
            title_lower = title.lower()
            if "resolve" in proc_name or "davinci" in title_lower:
                info["app_type"] = "davinci"
            elif "fl" in proc_name or "fl studio" in title_lower:
                info["app_type"] = "fl_studio"
            elif "figma" in proc_name or "figma" in title_lower:
                info["app_type"] = "figma"
            elif "code" in proc_name or "visual studio code" in title_lower or ".py" in title_lower or ".ipynb" in title_lower:
                info["app_type"] = "coding_ml"
            elif any(b in proc_name for b in ["chrome", "msedge", "firefox", "brave", "opera"]):
                if "google" in title_lower or "docs" in title_lower or "sheets" in title_lower or "slides" in title_lower:
                    info["app_type"] = "google_workspace"
                else:
                    info["app_type"] = "browser"

        except Exception as e:
            print(f"[Screen] Error inspecting active window: {e}")

        return info

    def denormalize_coordinate(self, norm_y: float, norm_x: float, monitor_idx: int = 1) -> Tuple[int, int]:
        """
        Converts normalized coordinates (0.0 to 1.0 or 0 to 1000) from vision model
        into absolute desktop pixel coordinates (X, Y).
        """
        # If coordinates are 0-1000 scale (standard Gemini spatial grounding format):
        if norm_y > 1.0 or norm_x > 1.0:
            norm_y = norm_y / 1000.0
            norm_x = norm_x / 1000.0

        target_mon = self.monitors[monitor_idx] if monitor_idx < len(self.monitors) else self.primary_monitor
        abs_x = int(target_mon["left"] + norm_x * target_mon["width"])
        abs_y = int(target_mon["top"] + norm_y * target_mon["height"])
        return abs_x, abs_y

    def denormalize_box(self, ymin, xmin, ymax, xmax, monitor_idx: int = 1) -> Tuple[int, int, int, int]:
        """Converts normalized bounding box to screen pixel rect (x1, y1, x2, y2)."""
        x1, y1 = self.denormalize_coordinate(ymin, xmin, monitor_idx)
        x2, y2 = self.denormalize_coordinate(ymax, xmax, monitor_idx)
        return x1, y1, x2, y2

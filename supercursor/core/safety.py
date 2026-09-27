import time
import math
import threading
import pyautogui

class SafetyKillSwitch:
    """
    Emergency kill-switch for SuperCursor.
    Monitors user input velocity. If the user rapidly shakes their mouse or presses Esc,
    any active autopilot or auto-glide immediately releases control and aborts.
    """
    def __init__(self, shake_threshold=1200, check_interval=0.03):
        self.shake_threshold = shake_threshold
        self.check_interval = check_interval
        self._aborted = threading.Event()
        self._running = False
        self._thread = None
        self._last_pos = pyautogui.position()
        self._last_time = time.time()
        self.on_abort_callbacks = []

    def register_abort_callback(self, cb):
        self.on_abort_callbacks.append(cb)

    def is_aborted(self) -> bool:
        return self._aborted.is_set()

    def reset(self):
        self._aborted.clear()
        self._last_pos = pyautogui.position()
        self._last_time = time.time()

    def trigger_abort(self, reason="Manual Abort"):
        if not self._aborted.is_set():
            print(f"\n[EMERGENCY STOP] {reason} triggered! Halting SuperCursor actions.")
            self._aborted.set()
            for cb in self.on_abort_callbacks:
                try:
                    cb(reason)
                except Exception as e:
                    print(f"[Safety] Error in abort callback: {e}")

    def start_monitoring(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop_monitoring(self):
        self._running = False

    def _monitor_loop(self):
        while self._running:
            time.sleep(self.check_interval)
            try:
                curr_pos = pyautogui.position()
                curr_time = time.time()
                dt = curr_time - self._last_time
                if dt > 0:
                    dx = curr_pos[0] - self._last_pos[0]
                    dy = curr_pos[1] - self._last_pos[1]
                    dist = math.hypot(dx, dy)
                    speed = dist / dt  # pixels per second

                    # If user violently moves or jerks mouse during autopilot, abort!
                    if speed > self.shake_threshold and not self._aborted.is_set():
                        self.trigger_abort("Mouse-Shake Gesture Detected")

                self._last_pos = curr_pos
                self._last_time = curr_time
            except Exception:
                pass

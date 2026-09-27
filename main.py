import sys
import os
import time
import threading
import pyautogui

from supercursor.core.config import Config
from supercursor.core.safety import SafetyKillSwitch
from supercursor.vision.screen import ScreenManager
from supercursor.ai.vision_client import VisionEngine
from supercursor.audio.voice import VoiceNarrator, VoiceListener
from supercursor.autopilot.controller import AutopilotController
from supercursor.overlay.canvas import SuperCursorOverlay
from supercursor.curricula import get_curriculum_for_app, list_all_lessons

try:
    from pynput import keyboard
    KEYBOARD_HOOK_AVAILABLE = True
except ImportError:
    KEYBOARD_HOOK_AVAILABLE = False


class SuperCursorApp:
    def __init__(self):
        print("✦ Starting SuperCursor - AI Screen & Cursor Companion")
        self.config = Config("config.yaml")

        self.safety = SafetyKillSwitch()
        self.safety.start_monitoring()

        self.screen_mgr = ScreenManager()
        self.vision = VisionEngine(self.config)
        self.narrator = VoiceNarrator(self.config)
        self.listener = VoiceListener(self.config)
        self.autopilot = AutopilotController(self.safety)

        # Wire up safety callback to overlay
        self.safety.register_abort_callback(self._on_safety_abort)

        self.overlay = SuperCursorOverlay(
            config=self.config,
            screen_mgr=self.screen_mgr,
            on_query_submit=self.handle_query,
            on_voice_requested=self.handle_voice_input,
            on_autopilot_toggle=self.handle_autopilot_toggle,
            on_engine_toggle=self.handle_engine_toggle,
        )

        self._hotkey_listener = None

    def _on_safety_abort(self, reason):
        if self.overlay and self.overlay.root:
            self.overlay.root.after(0, lambda: self.overlay.set_status(f"⚠️ {reason}! Action halted.", "#FF5252"))
        self.narrator.speak("Action cancelled.")

    def handle_engine_toggle(self) -> str:
        current = self.config.get("engine", "gemini").lower()
        new_engine = "local" if current == "gemini" else "gemini"
        self.config.set("engine", new_engine)
        print(f"[SuperCursor] Switched AI Vision engine to: {new_engine.upper()}")
        self.overlay.set_status(f"Switched engine to {new_engine.upper()}", "#B388FF")
        return new_engine

    def handle_autopilot_toggle(self, enabled: bool):
        mode = "autopilot" if enabled else "guide"
        self.config.set("interaction.default_mode", mode)
        msg = "Autopilot enabled. SuperCursor will perform actions for you." if enabled else "Show & Guide mode active."
        print(f"[SuperCursor] {msg}")
        self.overlay.set_status(msg, "#00E676" if not enabled else "#FF9100")
        self.narrator.speak("Autopilot enabled." if enabled else "Guide mode active.")

    def handle_voice_input(self):
        def _listen_worker():
            spoken_text = self.listener.listen_once()
            if spoken_text:
                self.overlay.root.after(0, lambda: self.overlay.set_query_text(spoken_text))
            else:
                self.overlay.root.after(0, lambda: self.overlay.set_status("Could not hear question. Try typing.", "#FF5252"))

        threading.Thread(target=_listen_worker, daemon=True).start()

    def handle_query(self, query: str):
        def _query_worker():
            try:
                # 1. Inspect active window
                app_info = self.screen_mgr.get_active_window_info()
                active_app = app_info["app_type"]
                app_title = app_info["title"]

                # 2. Capture screen
                img_bytes = self.screen_mgr.capture_screen_bytes()

                # 3. Vision analysis
                result = self.vision.analyze_screen(img_bytes, query, active_app, app_title)

                # 4. Denormalize coordinates to native display pixels
                target_x, target_y = self.screen_mgr.denormalize_coordinate(
                    result.point_norm[0], result.point_norm[1]
                )

                box_pixels = None
                if result.box_norm and len(result.box_norm) == 4:
                    box_pixels = self.screen_mgr.denormalize_box(*result.box_norm)

                # 5. Speak instructions aloud in background
                self.narrator.speak(result.spoken_text)

                # 6. Update UI overlay on main thread
                curr_mouse_x, curr_mouse_y = pyautogui.position()

                def _ui_update():
                    self.overlay.set_status(result.spoken_text, "#FFFFFF")
                    self.overlay.point_to(
                        target_x=target_x,
                        target_y=target_y,
                        box=box_pixels,
                        label=result.hud_label,
                        shortcut=result.shortcut,
                        start_x=curr_mouse_x,
                        start_y=curr_mouse_y
                    )

                self.overlay.root.after(0, _ui_update)

                # 7. Autopilot execution if enabled
                if self.overlay.autopilot_enabled:
                    time.sleep(0.5)
                    self.autopilot.click_at(target_x, target_y)

            except Exception as e:
                print(f"[SuperCursor] Error processing query: {e}")
                if self.overlay and self.overlay.root:
                    self.overlay.root.after(0, lambda: self.overlay.set_status(f"Error: {e}", "#FF5252"))

        threading.Thread(target=_query_worker, daemon=True).start()

    def summon(self):
        """Summons the SuperCursor companion overlay right at the user's focus."""
        if not self.overlay or not self.overlay.root:
            return
        self.safety.reset()
        app_info = self.screen_mgr.get_active_window_info()
        self.overlay.root.after(0, lambda: self.overlay.show(app_info))

    def _start_hotkey_listener(self):
        if not KEYBOARD_HOOK_AVAILABLE:
            print("[SuperCursor] pynput not installed. Use terminal console commands.")
            return

        # Listen for global shortcut <ctrl>+<alt>+c
        try:
            hotkey_str = self.config.get("interaction.hotkey", "<ctrl>+<alt>+c")
            hotkey_map = {hotkey_str: self.summon}
            self._hotkey_listener = keyboard.GlobalHotKeys(hotkey_map)
            self._hotkey_listener.start()
            print(f"[SuperCursor] Global hotkey registered: {hotkey_str}")
        except Exception as e:
            print(f"[SuperCursor] Error setting up global hotkey: {e}")

    def run(self):
        # Create GUI window
        self.overlay.create_window()

        # Start hotkey listener thread
        self._start_hotkey_listener()

        print("\n" + "=" * 60)
        print(" SuperCursor is active and watching your desktop!")
        print(" • Press Ctrl + Alt + C anywhere to summon")
        print(" • Esc to dismiss overlay / Emergency abort")
        print(" • Supports DaVinci Resolve, FL Studio, Figma, VS Code / ML")
        print("=" * 60 + "\n")

        # Automatically summon on first launch so user sees the interface immediately
        self.overlay.root.after(600, self.summon)

        # Run Tkinter event loop
        self.overlay.run_loop()


if __name__ == "__main__":
    app = SuperCursorApp()
    app.run()

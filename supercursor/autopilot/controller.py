import time
import math
import pyautogui

# Set safe PyAutoGUI defaults
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

class AutopilotController:
    """
    Simulates smooth, organic mouse movements and user interactions.
    Strictly checks the SafetyKillSwitch before and during every single movement slice.
    """
    def __init__(self, safety_switch):
        self.safety = safety_switch

    def move_to(self, target_x: int, target_y: int, duration: float = 0.6) -> bool:
        """
        Moves the physical mouse cursor smoothly to (target_x, target_y) using ease-out curve.
        Returns True if successful, False if aborted.
        """
        start_x, start_y = pyautogui.position()
        steps = int(max(20, duration * 60))
        dt = duration / steps

        for i in range(1, steps + 1):
            if self.safety and self.safety.is_aborted():
                print("[Autopilot] Movement aborted by safety switch.")
                return False

            t = i / steps
            # Cubic ease-out formula: 1 - (1 - t)^3
            ease = 1.0 - math.pow(1.0 - t, 3)

            curr_x = int(start_x + (target_x - start_x) * ease)
            curr_y = int(start_y + (target_y - start_y) * ease)

            pyautogui.moveTo(curr_x, curr_y)
            time.sleep(dt)

        return True

    def click_at(self, target_x: int, target_y: int, button: str = "left") -> bool:
        """Smoothly glides to target and performs a click."""
        if not self.move_to(target_x, target_y):
            return False

        if self.safety and self.safety.is_aborted():
            return False

        time.sleep(0.08)
        pyautogui.click(button=button)
        return True

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.8) -> bool:
        """Performs a smooth drag operation from start to end coordinates."""
        if not self.move_to(start_x, start_y):
            return False

        if self.safety and self.safety.is_aborted():
            return False

        pyautogui.mouseDown()
        time.sleep(0.05)
        success = self.move_to(end_x, end_y, duration=duration)
        pyautogui.mouseUp()
        return success

import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supercursor.core.config import Config
from supercursor.core.safety import SafetyKillSwitch
from supercursor.vision.screen import ScreenManager
from supercursor.ai.vision_client import VisionEngine, VisionResult
from supercursor.curricula import get_curriculum_for_app, list_all_lessons


class TestSuperCursor(unittest.TestCase):
    def setUp(self):
        self.config = Config("config.yaml")
        self.screen_mgr = ScreenManager()
        self.vision = VisionEngine(self.config)

    def test_config_defaults(self):
        self.assertEqual(self.config.get("interaction.emergency_abort_key"), "esc")
        self.assertTrue(self.config.get("visual.animation_fps") >= 30)

    def test_screen_dimensions(self):
        self.assertGreater(self.screen_mgr.width, 0)
        self.assertGreater(self.screen_mgr.height, 0)

    def test_coordinate_denormalization(self):
        # 500, 500 normalized should be center of screen
        cx, cy = self.screen_mgr.denormalize_coordinate(500, 500)
        self.assertAlmostEqual(cx, self.screen_mgr.left + self.screen_mgr.width // 2, delta=2)
        self.assertAlmostEqual(cy, self.screen_mgr.top + self.screen_mgr.height // 2, delta=2)

    def test_curricula_loading(self):
        davinci_curr = get_curriculum_for_app("davinci")
        self.assertIsNotNone(davinci_curr)
        self.assertEqual(davinci_curr["name"], "DaVinci Resolve")

        all_lessons = list_all_lessons()
        self.assertGreater(len(all_lessons), 0)
        titles = [l["title"] for l in all_lessons]
        self.assertTrue(any("Color Wheels" in t for t in titles))
        self.assertTrue(any("Auto-Layout" in t for t in titles))
        self.assertTrue(any("Channel Rack" in t for t in titles))

    def test_heuristic_fallback_queries(self):
        res = self.vision._heuristic_fallback("how do I use color wheels", "davinci", "DaVinci Resolve")
        self.assertIn("Color Wheels", res.hud_label)

        res_figma = self.vision._heuristic_fallback("auto layout padding", "figma", "Figma")
        self.assertIn("Auto-Layout", res_figma.hud_label)

    def test_safety_kill_switch(self):
        safety = SafetyKillSwitch()
        self.assertFalse(safety.is_aborted())
        safety.trigger_abort("Test Abort")
        self.assertTrue(safety.is_aborted())
        safety.reset()
        self.assertFalse(safety.is_aborted())


if __name__ == "__main__":
    unittest.main()

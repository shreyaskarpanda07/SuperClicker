import os
import json
import base64
import re
from typing import Dict, Any, Optional
import httpx

class VisionResult:
    def __init__(
        self,
        spoken_text: str,
        hud_label: str,
        point_norm: tuple = (500, 500),  # (y, x) 0-1000
        box_norm: tuple = (450, 450, 550, 550), # (ymin, xmin, ymax, xmax) 0-1000
        step_number: int = 1,
        total_steps: int = 1,
        shortcut: str = "",
        action_type: str = "click"  # "click", "drag", "inspect", "type"
    ):
        self.spoken_text = spoken_text
        self.hud_label = hud_label
        self.point_norm = point_norm
        self.box_norm = box_norm
        self.step_number = step_number
        self.total_steps = total_steps
        self.shortcut = shortcut
        self.action_type = action_type

    def to_dict(self):
        return {
            "spoken_text": self.spoken_text,
            "hud_label": self.hud_label,
            "point_norm": self.point_norm,
            "box_norm": self.box_norm,
            "step_number": self.step_number,
            "total_steps": self.total_steps,
            "shortcut": self.shortcut,
            "action_type": self.action_type,
        }


SYSTEM_PROMPT = """You are SuperCursor, an expert AI tutor sitting right next to the user.
Your job is to look at their computer screen and guide their attention to the exact button, menu, knob, panel, or code element needed to accomplish their goal.

You MUST respond in valid JSON with this exact structure:
{
  "thought": "brief reasoning identifying the element and its location",
  "box_2d": [ymin, xmin, ymax, xmax], // normalized coordinates from 0 to 1000
  "point": [y, x], // normalized center coordinates from 0 to 1000
  "step_number": 1,
  "total_steps": 1,
  "spoken_explanation": "Short, natural, friendly spoken sentence (under 25 words) explaining what to do right now, as if speaking aloud to the user.",
  "hud_label": "Very brief 3-5 word label for the on-screen badge",
  "keyboard_shortcut": "Optional keyboard shortcut if available (e.g. 'Shift+A', 'Ctrl+B', 'Alt+S')",
  "action_type": "click" // "click", "drag", "type", or "inspect"
}
"""

class VisionEngine:
    def __init__(self, config):
        self.config = config

    def analyze_screen(
        self,
        image_bytes: bytes,
        user_query: str,
        active_app: str = "generic",
        app_title: str = ""
    ) -> VisionResult:
        engine_mode = self.config.get("engine", "gemini").lower()
        api_key = self.config.get("gemini.api_key") or os.environ.get("GEMINI_API_KEY", "")

        # Try Gemini if configured or API key present
        if engine_mode == "gemini" and api_key:
            try:
                res = self._call_gemini(image_bytes, user_query, active_app, app_title, api_key)
                if res:
                    return res
            except Exception as e:
                print(f"[VisionEngine] Gemini call failed ({e}). Falling back to local/heuristic.")

        # Try Local Ollama (RTX 4050)
        if engine_mode == "local" or not api_key:
            try:
                res = self._call_local_ollama(image_bytes, user_query, active_app, app_title)
                if res:
                    return res
            except Exception as e:
                print(f"[VisionEngine] Local Ollama call failed ({e}). Falling back to heuristic.")

        # Heuristic offline fallback
        return self._heuristic_fallback(user_query, active_app, app_title)

    def _call_gemini(
        self,
        image_bytes: bytes,
        user_query: str,
        active_app: str,
        app_title: str,
        api_key: str
    ) -> Optional[VisionResult]:
        model = self.config.get("gemini.model", "gemini-flash-latest")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Active Application: {active_app.upper()} (Window: '{app_title}')\n"
            f"User Goal: {user_query}\n"
            "Locate the exact control on screen and provide the coordinates and tutorial explanation."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_result(text, user_query)
            else:
                print(f"[Gemini API Error] {resp.status_code}: {resp.text[:200]}")
                return None

    def _call_local_ollama(
        self,
        image_bytes: bytes,
        user_query: str,
        active_app: str,
        app_title: str
    ) -> Optional[VisionResult]:
        endpoint = self.config.get("local.endpoint", "http://localhost:11434")
        model = self.config.get("local.model", "qwen2-vl:2b")
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Active Application: {active_app}\n"
            f"User Goal: {user_query}\n"
            "Return JSON only."
        )

        payload = {
            "model": model,
            "prompt": prompt_text,
            "images": [img_b64],
            "stream": False,
            "format": "json"
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{endpoint}/api/generate", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "")
                return self._parse_json_result(text, user_query)
            return None

    def _parse_json_result(self, text: str, user_query: str) -> VisionResult:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            raw = match.group(0) if match else text
            d = json.loads(raw)

            box = d.get("box_2d", [450, 450, 550, 550])
            point = d.get("point")
            if not point and len(box) == 4:
                point = [(box[0] + box[2]) // 2, (box[1] + box[3]) // 2]
            elif not point:
                point = [500, 500]

            return VisionResult(
                spoken_text=d.get("spoken_explanation", f"Here is where you can find this in your app."),
                hud_label=d.get("hud_label", user_query[:30]),
                point_norm=tuple(point),
                box_norm=tuple(box),
                step_number=d.get("step_number", 1),
                total_steps=d.get("total_steps", 1),
                shortcut=d.get("keyboard_shortcut", ""),
                action_type=d.get("action_type", "click")
            )
        except Exception as e:
            print(f"[VisionEngine] Error parsing model response: {e}. Raw: {text}")
            return VisionResult(
                spoken_text="I spotted the control right here on your screen.",
                hud_label=user_query[:30],
                point_norm=(500, 500),
                box_norm=(450, 450, 550, 550)
            )

    def _heuristic_fallback(self, query: str, active_app: str, app_title: str) -> VisionResult:
        """
        Smart offline heuristic database for common queries across
        DaVinci Resolve, FL Studio, Figma, and Coding/VS Code.
        """
        q = query.lower()

        # 1. DaVinci Resolve
        if active_app == "davinci" or "resolve" in q:
            if "color" in q or "wheel" in q or "lift" in q or "gain" in q:
                return VisionResult(
                    spoken_text="The Color Wheels are located in the bottom left panel of the Color Page.",
                    hud_label="Color Wheels (Lift, Gamma, Gain)",
                    point_norm=(780, 280),
                    box_norm=(680, 150, 880, 410),
                    shortcut="Shift + 6 (Color Page)",
                    action_type="drag"
                )
            elif "cut" in q or "blade" in q or "split" in q:
                return VisionResult(
                    spoken_text="Press B to activate the Blade tool, or click the razor icon above your timeline.",
                    hud_label="Blade Tool (Split Clip)",
                    point_norm=(530, 480),
                    box_norm=(510, 460, 550, 500),
                    shortcut="B",
                    action_type="click"
                )
            elif "node" in q or "grade" in q:
                return VisionResult(
                    spoken_text="Your Node Graph is in the upper right. Press Alt+S to append a new serial node.",
                    hud_label="Node Graph Panel",
                    point_norm=(320, 820),
                    box_norm=(150, 680, 490, 960),
                    shortcut="Alt + S",
                    action_type="click"
                )

        # 2. FL Studio
        elif active_app == "fl_studio" or "fl" in q:
            if "piano" in q or "roll" in q or "melody" in q or "chord" in q:
                return VisionResult(
                    spoken_text="Press F7 or right-click any channel in your rack to open the Piano Roll.",
                    hud_label="Piano Roll Editor",
                    point_norm=(420, 500),
                    box_norm=(200, 200, 650, 800),
                    shortcut="F7",
                    action_type="click"
                )
            elif "mixer" in q or "route" in q or "sidechain" in q:
                return VisionResult(
                    spoken_text="Press F9 to toggle the Mixer. Select your track and route cables at the bottom.",
                    hud_label="Mixer & Routing Dock",
                    point_norm=(720, 500),
                    box_norm=(550, 100, 900, 900),
                    shortcut="F9",
                    action_type="click"
                )
            elif "channel" in q or "beat" in q or "step" in q or "kick" in q:
                return VisionResult(
                    spoken_text="Here is your Channel Rack. Click the step sequencer boxes to lay down your rhythm.",
                    hud_label="Channel Rack (Step Sequencer)",
                    point_norm=(380, 450),
                    box_norm=(250, 220, 510, 680),
                    shortcut="F6",
                    action_type="click"
                )

        # 3. Figma
        elif active_app == "figma" or "figma" in q:
            if "auto" in q or "layout" in q or "padding" in q:
                return VisionResult(
                    spoken_text="Select your frame and press Shift+A to add Auto-Layout, or click plus on the right panel.",
                    hud_label="Auto-Layout Properties",
                    point_norm=(380, 900),
                    box_norm=(320, 830, 450, 970),
                    shortcut="Shift + A",
                    action_type="click"
                )
            elif "component" in q or "variant" in q:
                return VisionResult(
                    spoken_text="Click the diamond icon in the top toolbar or press Ctrl+Alt+K to create a component.",
                    hud_label="Create Component",
                    point_norm=(45, 520),
                    box_norm=(25, 490, 65, 550),
                    shortcut="Ctrl + Alt + K",
                    action_type="click"
                )

        # 4. Coding & ML / VS Code
        elif active_app == "coding_ml" or "code" in q or "debug" in q or "torch" in q:
            if "run" in q or "debug" in q or "breakpoint" in q:
                return VisionResult(
                    spoken_text="Click next to the line number to set a breakpoint, then press F5 to start debugging.",
                    hud_label="Debugger & Breakpoints",
                    point_norm=(260, 45),
                    box_norm=(100, 15, 450, 65),
                    shortcut="F5",
                    action_type="click"
                )
            elif "terminal" in q or "cuda" in q or "gpu" in q:
                return VisionResult(
                    spoken_text="Toggle the integrated terminal with Ctrl + Backtick to check your GPU environment.",
                    hud_label="Integrated Terminal",
                    point_norm=(820, 500),
                    box_norm=(680, 100, 960, 900),
                    shortcut="Ctrl + `",
                    action_type="type"
                )

        # Generic default
        return VisionResult(
            spoken_text="Here is the target control area on your screen.",
            hud_label=query[:30],
            point_norm=(500, 500),
            box_norm=(450, 450, 550, 550),
            shortcut="",
            action_type="click"
        )

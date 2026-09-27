import tkinter as tk
from tkinter import ttk
import math
import time
import threading
from typing import Optional, Callable, Dict, Any, List

class SuperCursorOverlay:
    """
    Windows-native transparent screen overlay with animated ghost cursor,
    sonar ripple rings, glowing bounding boxes, and an interactive HUD.
    """
    TRANSPARENT_COLOR = "#010101"

    def __init__(
        self,
        config,
        screen_mgr,
        on_query_submit: Optional[Callable[[str], None]] = None,
        on_voice_requested: Optional[Callable[[], None]] = None,
        on_autopilot_toggle: Optional[Callable[[bool], None]] = None,
        on_engine_toggle: Optional[Callable[[], str]] = None,
        on_lesson_selected: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self.screen_mgr = screen_mgr
        self.on_query_submit = on_query_submit
        self.on_voice_requested = on_voice_requested
        self.on_autopilot_toggle = on_autopilot_toggle
        self.on_engine_toggle = on_engine_toggle
        self.on_lesson_selected = on_lesson_selected

        self.root = None
        self.canvas = None
        self.hud_frame = None

        # Colors from config
        self.color_cursor = config.get("visual.ghost_cursor_color", "#00E5FF")
        self.color_pulse = config.get("visual.pulse_ring_color", "#B388FF")
        self.color_box = config.get("visual.highlight_box_color", "#00E676")
        self.hud_bg = config.get("visual.hud_bg", "#12141A")

        # State
        self.is_visible = False
        self.autopilot_enabled = config.get("interaction.default_mode", "guide") == "autopilot"
        self.active_app_name = "Desktop"
        self.current_engine_name = config.get("engine", "gemini").upper()

        # Animation state
        self._ghost_x = 0
        self._ghost_y = 0
        self._target_x = 0
        self._target_y = 0
        self._target_box = None
        self._target_label = ""
        self._target_shortcut = ""
        self._animating = False
        self._pulse_radius = 10
        self._pulse_dir = 1
        self._pulse_job = None
        self._glide_job = None

    def create_window(self):
        """Initializes the transparent topmost window covering the desktop."""
        self.root = tk.Tk()
        self.root.title("SuperCursor Screen Companion")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # Set transparent colorkey on Windows
        self.root.wm_attributes("-transparentcolor", self.TRANSPARENT_COLOR)
        self.root.config(bg=self.TRANSPARENT_COLOR)

        # Size to primary monitor
        width = self.screen_mgr.width
        height = self.screen_mgr.height
        left = self.screen_mgr.left
        top = self.screen_mgr.top
        self.root.geometry(f"{width}x{height}+{left}+{top}")

        # Full-screen drawing canvas
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Escape key closes overlay
        self.root.bind("<Escape>", lambda e: self.hide())

        self._build_hud()
        self.hide()

    def _build_hud(self):
        """Builds the floating control cockpit HUD."""
        self.hud_frame = tk.Frame(
            self.root,
            bg=self.hud_bg,
            bd=2,
            relief=tk.FLAT,
            padx=16,
            pady=12,
            highlightbackground="#2A2F3D",
            highlightthickness=1
        )

        # Header Row: App badge, Engine indicator, Autopilot toggle
        header = tk.Frame(self.hud_frame, bg=self.hud_bg)
        header.pack(fill=tk.X, pady=(0, 8))

        self.lbl_app = tk.Label(
            header,
            text=f"✦ APP: {self.active_app_name.upper()}",
            font=("Segoe UI", 9, "bold"),
            fg="#00E5FF",
            bg="#18202B",
            padx=8,
            pady=3
        )
        self.lbl_app.pack(side=tk.LEFT)

        self.btn_engine = tk.Button(
            header,
            text=f"⚡ {self.current_engine_name}",
            font=("Segoe UI", 8, "bold"),
            fg="#B388FF",
            bg="#1E1C2C",
            activebackground="#2A2640",
            activeforeground="#B388FF",
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._toggle_engine_clicked
        )
        self.btn_engine.pack(side=tk.LEFT, padx=8)

        self.btn_mode = tk.Button(
            header,
            text="🎯 SHOW & GUIDE" if not self.autopilot_enabled else "🚀 AUTOPILOT",
            font=("Segoe UI", 8, "bold"),
            fg="#00E676" if not self.autopilot_enabled else "#FF9100",
            bg="#182A20" if not self.autopilot_enabled else "#332210",
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._toggle_autopilot_clicked
        )
        self.btn_mode.pack(side=tk.RIGHT)

        btn_close = tk.Button(
            header,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg="#7E8B9B",
            bg=self.hud_bg,
            bd=0,
            padx=6,
            cursor="hand2",
            command=self.hide
        )
        btn_close.pack(side=tk.RIGHT, padx=(0, 6))

        # Query Input Row
        input_row = tk.Frame(self.hud_frame, bg=self.hud_bg)
        input_row.pack(fill=tk.X, pady=(0, 6))

        self.entry_query = tk.Entry(
            input_row,
            font=("Segoe UI", 11),
            bg="#1E222D",
            fg="#FFFFFF",
            insertbackground="#00E5FF",
            bd=0,
            highlightbackground="#2E3547",
            highlightthickness=1,
            relief=tk.FLAT
        )
        self.entry_query.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        self.entry_query.bind("<Return>", lambda e: self._submit_query())

        self.btn_voice = tk.Button(
            input_row,
            text="🎙️ Speak",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#3B82F6",
            activebackground="#2563EB",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._voice_clicked
        )
        self.btn_voice.pack(side=tk.RIGHT)

        # Status / Feedback label
        self.lbl_status = tk.Label(
            self.hud_frame,
            text="Ask anything or choose a lesson: 'How do I cut in DaVinci?', 'Figma auto-layout', etc.",
            font=("Segoe UI", 8),
            fg="#8B95A5",
            bg=self.hud_bg,
            anchor="w"
        )
        self.lbl_status.pack(fill=tk.X, pady=(2, 0))

    def _toggle_engine_clicked(self):
        if self.on_engine_toggle:
            new_engine = self.on_engine_toggle()
            self.current_engine_name = new_engine.upper()
            self.btn_engine.config(text=f"⚡ {self.current_engine_name}")

    def _toggle_autopilot_clicked(self):
        self.autopilot_enabled = not self.autopilot_enabled
        if self.autopilot_enabled:
            self.btn_mode.config(text="🚀 AUTOPILOT", fg="#FF9100", bg="#332210")
        else:
            self.btn_mode.config(text="🎯 SHOW & GUIDE", fg="#00E676", bg="#182A20")
        if self.on_autopilot_toggle:
            self.on_autopilot_toggle(self.autopilot_enabled)

    def _voice_clicked(self):
        self.lbl_status.config(text="Listening for voice query...", fg="#FFD600")
        if self.on_voice_requested:
            self.on_voice_requested()

    def set_query_text(self, text: str):
        if self.entry_query:
            self.entry_query.delete(0, tk.END)
            self.entry_query.insert(0, text)
            self._submit_query()

    def set_status(self, text: str, color: str = "#8B95A5"):
        if self.lbl_status:
            self.lbl_status.config(text=text, fg=color)

    def _submit_query(self):
        q = self.entry_query.get().strip()
        if q and self.on_query_submit:
            self.set_status("Analyzing screen context...", "#00E5FF")
            self.on_query_submit(q)

    def show(self, app_info: Optional[Dict[str, Any]] = None):
        """Displays overlay and positions HUD near top-center or cursor."""
        if not self.root:
            return

        if app_info:
            self.active_app_name = app_info.get("app_type", "Desktop")
            self.lbl_app.config(text=f"✦ APP: {self.active_app_name.upper()}")

        # Position HUD at center top
        hud_w = 580
        hud_h = 130
        hud_x = max(20, (self.screen_mgr.width - hud_w) // 2)
        hud_y = 40
        self.hud_frame.place(x=hud_x, y=hud_y, width=hud_w, height=hud_h)

        self.root.deiconify()
        self.root.lift()
        self.is_visible = True
        self.entry_query.focus_set()

    def hide(self):
        """Hides overlay and clears active markups."""
        if not self.root:
            return
        self.clear_annotations()
        self.root.withdraw()
        self.is_visible = False

    def clear_annotations(self):
        """Removes all cursor drawings, ripple rings, and spotlight markers."""
        self._animating = False
        if self._pulse_job and self.root:
            try:
                self.root.after_cancel(self._pulse_job)
            except Exception:
                pass
        if self._glide_job and self.root:
            try:
                self.root.after_cancel(self._glide_job)
            except Exception:
                pass
        if self.canvas:
            self.canvas.delete("all")

    def point_to(
        self,
        target_x: int,
        target_y: int,
        box: Optional[tuple] = None,
        label: str = "",
        shortcut: str = "",
        start_x: Optional[int] = None,
        start_y: Optional[int] = None
    ):
        """
        Draws visual annotations and smoothly glides the ghost cursor
        from start position to the target UI element.
        """
        self.clear_annotations()
        self._target_x = target_x
        self._target_y = target_y
        self._target_box = box
        self._target_label = label
        self._target_shortcut = shortcut

        # Start from current mouse position or center
        if start_x is None or start_y is None:
            start_x = self.screen_mgr.width // 2
            start_y = self.screen_mgr.height // 2

        self._ghost_x = start_x
        self._ghost_y = start_y

        self._start_glide_animation(start_x, start_y, target_x, target_y)
        self._start_pulse_animation()

    def _start_glide_animation(self, x0, y0, x1, y1, steps=25, current=0):
        if not self.is_visible or not self.canvas:
            return

        t = current / steps
        # Cubic ease-out: 1 - (1 - t)^3
        ease = 1.0 - math.pow(1.0 - t, 3)

        curr_x = x0 + (x1 - x0) * ease
        curr_y = y0 + (y1 - y0) * ease

        self._ghost_x = curr_x
        self._ghost_y = curr_y

        self._redraw_frame()

        if current < steps:
            self._glide_job = self.root.after(
                16,
                lambda: self._start_glide_animation(x0, y0, x1, y1, steps, current + 1)
            )

    def _start_pulse_animation(self):
        if not self.is_visible or not self.canvas:
            return

        self._pulse_radius += 1.5 * self._pulse_dir
        if self._pulse_radius >= 32:
            self._pulse_dir = -1
        elif self._pulse_radius <= 14:
            self._pulse_dir = 1

        self._redraw_frame()
        self._pulse_job = self.root.after(30, self._start_pulse_animation)

    def _redraw_frame(self):
        if not self.canvas:
            return
        self.canvas.delete("overlay_element")

        tx = self._target_x
        ty = self._target_y

        # 1. Bounding Box / Spotlight around target element
        if self._target_box:
            bx1, by1, bx2, by2 = self._target_box
            # Outer subtle glow box
            self.canvas.create_rectangle(
                bx1 - 3, by1 - 3, bx2 + 3, by2 + 3,
                outline=self.color_box,
                width=2,
                tags="overlay_element"
            )
            # Reticle corners
            c_len = 10
            self.canvas.create_line(bx1, by1, bx1 + c_len, by1, fill="#FFFFFF", width=3, tags="overlay_element")
            self.canvas.create_line(bx1, by1, bx1, by1 + c_len, fill="#FFFFFF", width=3, tags="overlay_element")
            self.canvas.create_line(bx2, by1, bx2 - c_len, by1, fill="#FFFFFF", width=3, tags="overlay_element")
            self.canvas.create_line(bx2, by1, bx2, by1 + c_len, fill="#FFFFFF", width=3, tags="overlay_element")

        # 2. Pulsing Sonar Ring at target center
        r = self._pulse_radius
        self.canvas.create_oval(
            tx - r, ty - r, tx + r, ty + r,
            outline=self.color_pulse,
            width=2,
            tags="overlay_element"
        )
        self.canvas.create_oval(
            tx - 5, ty - 5, tx + 5, ty + 5,
            fill=self.color_cursor,
            outline="#FFFFFF",
            width=1,
            tags="overlay_element"
        )

        # 3. Floating Callout Badge next to target
        if self._target_label:
            badge_x = tx + 35
            badge_y = max(30, ty - 25)
            badge_text = f"✦ {self._target_label}"
            if self._target_shortcut:
                badge_text += f" [{self._target_shortcut}]"

            # Badge background pill
            text_width = len(badge_text) * 7.5 + 24
            self.canvas.create_rectangle(
                badge_x, badge_y, badge_x + text_width, badge_y + 30,
                fill="#161B26",
                outline="#00E5FF",
                width=1.5,
                tags="overlay_element"
            )
            self.canvas.create_text(
                badge_x + 12, badge_y + 15,
                text=badge_text,
                fill="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                tags="overlay_element"
            )

        # 4. Animated Glowing Ghost Cursor Pointer
        gx = self._ghost_x
        gy = self._ghost_y

        # Cyber neon cursor arrow polygon
        poly = [
            gx, gy,
            gx + 6, gy + 18,
            gx + 12, gy + 13,
            gx + 20, gy + 20,
            gx + 23, gy + 17,
            gx + 15, gy + 10,
            gx + 22, gy + 6
        ]
        self.canvas.create_polygon(
            poly,
            fill=self.color_cursor,
            outline="#FFFFFF",
            width=1.5,
            tags="overlay_element"
        )

    def run_loop(self):
        """Starts the Tkinter main event loop."""
        if self.root:
            self.root.mainloop()

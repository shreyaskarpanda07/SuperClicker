"""
DaVinci Resolve Curriculum for SuperCursor.
Covers timeline editing, node-based color grading, primary wheels, and scopes.
"""

CURRICULUM = {
    "name": "DaVinci Resolve",
    "target_apps": ["resolve", "davinci"],
    "lessons": [
        {
            "id": "color_grading_basics",
            "title": "Primary Color Wheels & Dynamic Range",
            "description": "Learn how Lift, Gamma, Gain, and Offset sculpt contrast and mood.",
            "steps": [
                {
                    "step": 1,
                    "target": "Color Page Navigation",
                    "spoken": "Switch to the Color page by pressing Shift + 6 or clicking the Color icon on the bottom workspace bar.",
                    "label": "Color Page (Shift + 6)",
                    "shortcut": "Shift + 6",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Lift Wheel (Shadows)",
                    "spoken": "The Lift wheel on the far left controls your shadows. Drag the slider under the wheel to set your black point.",
                    "label": "Lift Wheel (Shadows)",
                    "action": "drag"
                },
                {
                    "step": 3,
                    "target": "Gain Wheel (Highlights)",
                    "spoken": "Gain adjusts your highlights. Bring it up until skin tones and bright areas sit naturally on the waveform scope.",
                    "label": "Gain Wheel (Highlights)",
                    "action": "drag"
                },
                {
                    "step": 4,
                    "target": "Gamma Wheel (Midtones)",
                    "spoken": "Now dial the Gamma wheel to balance your midtones and restore natural skin brightness.",
                    "label": "Gamma Wheel (Midtones)",
                    "action": "drag"
                }
            ]
        },
        {
            "id": "node_tree_workflow",
            "title": "Building a Clean Node Tree",
            "description": "Organize your grade into sequential serial nodes for exposure, white balance, skin tones, and look creation.",
            "steps": [
                {
                    "step": 1,
                    "target": "Append Serial Node",
                    "spoken": "Press Alt + S to add a new Serial Node downstream in your grade.",
                    "label": "New Serial Node (Alt + S)",
                    "shortcut": "Alt + S",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Labeling Nodes",
                    "spoken": "Right-click the new node and select Node Label. Always name your nodes to keep your graph readable.",
                    "label": "Node Label",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Scopes Dock",
                    "spoken": "Keep your Waveform or Parade scope open in the bottom right corner to prevent clipping highlights or crushing blacks.",
                    "label": "Scopes (Waveform / Parade)",
                    "shortcut": "Ctrl + Shift + W",
                    "action": "inspect"
                }
            ]
        },
        {
            "id": "editing_timeline_essentials",
            "title": "Fast Cut & Blade Editing",
            "description": "Navigate clips, split heads and tails, and maintain timeline rhythm.",
            "steps": [
                {
                    "step": 1,
                    "target": "Blade Tool",
                    "spoken": "Press B to activate the Blade tool and slice at the playhead position.",
                    "label": "Blade Tool (B)",
                    "shortcut": "B",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Ripple Delete",
                    "spoken": "Use Shift + Backspace or Delete to ripple-delete empty gaps and automatically close the edit.",
                    "label": "Ripple Delete (Shift + Del)",
                    "shortcut": "Shift + Delete",
                    "action": "click"
                }
            ]
        }
    ]
}

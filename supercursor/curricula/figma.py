"""
Figma Curriculum for SuperCursor.
Covers Auto-Layout mastery, responsive constraints, components, variants, and design systems.
"""

CURRICULUM = {
    "name": "Figma",
    "target_apps": ["figma"],
    "lessons": [
        {
            "id": "autolayout_mastery",
            "title": "Mastering Auto-Layout (Shift + A)",
            "description": "Build responsive components that adapt dynamically to any screen width or text length.",
            "steps": [
                {
                    "step": 1,
                    "target": "Convert Frame to Auto-Layout",
                    "spoken": "Select your elements and press Shift + A, or click the plus button on the Auto-layout panel.",
                    "label": "Add Auto-Layout (Shift + A)",
                    "shortcut": "Shift + A",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Direction & Alignment Box",
                    "spoken": "Set the flow direction to Vertical or Horizontal, and click the alignment matrix to pin items.",
                    "label": "Direction & Alignment",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Horizontal & Vertical Resizing",
                    "spoken": "Change child layers from Fixed to Fill Container so they stretch responsively when the parent grows.",
                    "label": "Resizing: Fill Container",
                    "action": "click"
                },
                {
                    "step": 4,
                    "target": "Padding and Item Spacing",
                    "spoken": "Use uniform or independent padding to give your layout breathing room and consistent design tokens.",
                    "label": "Padding & Gap Controls",
                    "action": "drag"
                }
            ]
        },
        {
            "id": "components_and_variants",
            "title": "Creating Reusable Components & Variant Sets",
            "description": "Organize UI elements into scalable states (Default, Hover, Active, Disabled).",
            "steps": [
                {
                    "step": 1,
                    "target": "Create Main Component",
                    "spoken": "Select your finished element and press Ctrl + Alt + K to turn it into a master component.",
                    "label": "Create Component (Ctrl+Alt+K)",
                    "shortcut": "Ctrl + Alt + K",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Add Variant Property",
                    "spoken": "Click Add Variant in the right panel to generate alternate states for this component.",
                    "label": "Add Variant (+)",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Configure Component Properties",
                    "spoken": "Attach boolean switches for icons and text properties so teammates can customize instances effortlessly.",
                    "label": "Component Properties",
                    "action": "click"
                }
            ]
        }
    ]
}

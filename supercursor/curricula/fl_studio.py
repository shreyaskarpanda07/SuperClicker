"""
FL Studio Curriculum for SuperCursor.
Covers Channel Rack rhythm sequencing, Piano Roll composition, Mixer routing, sidechaining, and automation.
"""

CURRICULUM = {
    "name": "FL Studio",
    "target_apps": ["fl64", "fl", "flstudio"],
    "lessons": [
        {
            "id": "beatmaking_channel_rack",
            "title": "First Drum Pattern in the Channel Rack",
            "description": "Sequence crisp 4-on-the-floor kicks, 808 bass, claps, and hi-hat rolls.",
            "steps": [
                {
                    "step": 1,
                    "target": "Open Channel Rack",
                    "spoken": "Press F6 to bring up your Channel Rack and step sequencer.",
                    "label": "Channel Rack (F6)",
                    "shortcut": "F6",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Step Sequencer Grid",
                    "spoken": "Left-click the step buttons to paint your rhythm. Standard beats drop on steps 1, 5, 9, and 13.",
                    "label": "Program Steps",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Hi-Hat Fill Each 2 Steps",
                    "spoken": "Right-click your Hi-Hat channel name and select Fill each 2 steps for an instant rhythmic groove.",
                    "label": "Fill Each 2 Steps",
                    "action": "click"
                }
            ]
        },
        {
            "id": "piano_roll_melodies",
            "title": "Piano Roll Melodies & Chords",
            "description": "Compose harmonies, enable scale snapping, and humanize velocities.",
            "steps": [
                {
                    "step": 1,
                    "target": "Open Piano Roll",
                    "spoken": "Press F7 or right-click any synth instrument and choose Piano roll.",
                    "label": "Piano Roll (F7)",
                    "shortcut": "F7",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Scale Highlighting",
                    "spoken": "Click the dropdown arrow in the top left, go to Helpers, and pick your key scale so notes never sound out of tune.",
                    "label": "Scale Highlighting (Helpers)",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Strumizer Humanize",
                    "spoken": "Press Alt + S to open the Strum tool, staggering chord note start times to sound like an authentic live player.",
                    "label": "Strum Tool (Alt + S)",
                    "shortcut": "Alt + S",
                    "action": "click"
                }
            ]
        },
        {
            "id": "mixer_and_sidechaining",
            "title": "Mixer Routing & Sidechain Compression",
            "description": "Route instruments to dedicated mixer inserts and sidechain your kick to your bass/808.",
            "steps": [
                {
                    "step": 1,
                    "target": "Open Mixer",
                    "spoken": "Press F9 to toggle the Mixer panel.",
                    "label": "Mixer (F9)",
                    "shortcut": "F9",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Assign Channel to Insert",
                    "spoken": "Select your instrument track and use the track offset box or Ctrl + L to route it to an empty mixer track.",
                    "label": "Route Track (Ctrl + L)",
                    "shortcut": "Ctrl + L",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Sidechain to this track",
                    "spoken": "Select your Kick track, right-click the arrow at the bottom of the Bass track, and click Sidechain to this track.",
                    "label": "Sidechain Routing",
                    "action": "click"
                },
                {
                    "step": 4,
                    "target": "Fruity Limiter / Sidechain Tab",
                    "spoken": "Open Fruity Limiter on the Bass track, switch to COMP mode, and set the sidechain input to your Kick.",
                    "label": "Fruity Limiter (Sidechain)",
                    "action": "click"
                }
            ]
        }
    ]
}

# SuperCursor ✦
> **My personal AI screen & cursor companion for Windows.**  
> *Built for private personal use to accelerate hands-on learning across complex creative and engineering tools.*

---

## Why I Built This

Whenever I tried learning complex creative and technical software—whether it was color grading in **DaVinci Resolve**, routing audio in **FL Studio**, setting up auto-layout in **Figma**, or debugging PyTorch training loops in **VS Code**—I kept hitting the same friction:

1. **YouTube Tutorial Fatigue**: Pausing a 30-minute video every 10 seconds, switching back and forth between monitors, trying to locate a tiny hidden button or obscure shortcut.
2. **Context Switching**: Static documentation doesn't see what project I have open or where my settings are misconfigured.
3. **The "HeyClicky" Inspiration**: Recently I saw *HeyClicky* on macOS—an AI that sits by your cursor, sees your screen, moves a pointer, and highlights how things are done. But I'm on Windows with an NVIDIA RTX 4050, and I needed something tailored to my own learning workflow.

So I started engineering **SuperCursor** as my personal companion.

---

## How It Works

SuperCursor lives unobtrusively in the background on Windows. Whenever I get stuck or want to learn a workflow:

1. **Summon (`Ctrl + Alt + C`)**: A transparent HUD overlay summons directly over my desktop, detecting the active window (DaVinci, FL Studio, Figma, VS Code).
2. **Ask by Voice or Text**: I can speak via Push-to-Talk (`🎙️ Speak`) or type a quick question:
   - *"How do I cut this clip?"*
   - *"Where are the lift, gamma, gain wheels?"*
   - *"How do I route this kick to sidechain the 808?"*
   - *"Make this card responsive in Figma."*
   - *"Explain this PyTorch training loop."*
3. **Ghost Cursor & Visual Markup**:
   - Instead of violently seizing my mouse, a smooth, glowing **Ghost Cursor** glides across my screen to the exact button or dial using cubic Bezier curves.
   - It projects expanding **Sonar Ripple Rings** and **Spotlight Reticles** directly around the UI control.
   - A floating glass badge shows the keyboard shortcut (e.g. `Shift + A`, `Alt + S`, `F9`, `B`).
4. **Voice Narration (1-on-1 Mentor)**: It speaks the explanation aloud in real time using local neural speech synthesis so I don't even have to look away from what I'm doing.
5. **Autopilot Toggle**: If I want the AI to click or navigate for me, I toggle **Autopilot Mode**. For safety, shaking the mouse or hitting `Esc` instantly cancels any action.

---

## Architecture & Dual-Brain Engine

I designed this with a modular dual-engine architecture:

- **Gemini Mode (Cloud Precision)**: Uses Google Gemini 2.0 Flash for sub-second spatial grounding, returning normalized bounding coordinates `[ymin, xmin, ymax, xmax]` for pixel-precise targeting on high-DPI screens.
- **Local Mode (RTX 4050 Private)**: Optimized to run offline on my laptop's NVIDIA RTX 4050 GPU (6GB VRAM) using Ollama with lightweight multimodal models (like `qwen2-vl:2b` or `moondream2`), ensuring complete privacy when working on proprietary code or designs.
- **Heuristic Engine**: Instant offline knowledge base for standard shortcuts and panel layouts.

---

## What I'm Using It to Learn

- **Coding & Machine Learning**:
  - Anatomy of PyTorch loops (`model(x)`, `zero_grad()`, `backward()`, `step()`)
  - CUDA GPU checks and VRAM monitoring on RTX 4050
  - VS Code interactive debugging, breakpoints, and Git workflows
- **DaVinci Resolve**:
  - Color Page: Primary wheels (Lift, Gamma, Gain, Offset), waveform scopes
  - Node graph hierarchy (Serial `Alt+S`, Parallel `Alt+P`)
  - Timeline trimming with the Blade tool (`B`) and ripple delete
- **Figma**:
  - Auto-Layout mastery (`Shift+A`), Hug vs Fill container, direction matrices
  - Master components (`Ctrl+Alt+K`) and interactive variant sets
- **FL Studio**:
  - Step sequencer rhythm programming in the Channel Rack (`F6`)
  - Piano Roll (`F7`) chords, scale highlighting, strumming (`Alt+S`)
  - Mixer routing (`F9`) and sidechain compression (Fruity Limiter)

---

## Project Structure

```text
supercursor/
├── main.py                     # App orchestrator & global hotkey listener
├── start_supercursor.bat       # 1-click Windows launcher
├── config.yaml                 # User configuration (hotkeys, voice, engines)
├── requirements.txt            # Python dependencies
├── supercursor/
│   ├── core/                   # Config loader & emergency safety kill-switch
│   ├── vision/                 # Fast screen capture & DPI-aware coordinate mapping
│   ├── ai/                     # Gemini 2.0 + Local RTX 4050 vision engine
│   ├── overlay/                # Transparent layered window, ghost cursor & HUD
│   ├── audio/                  # Non-blocking TTS speech & voice input
│   ├── autopilot/              # Smooth ease-out mouse movement with safety checks
│   └── curricula/              # Interactive modules (Coding/ML, DaVinci, Figma, FL Studio)
└── tests/                      # Verification scripts
```

---

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)
Edit `config.yaml` to set your preferred hotkey or add your Gemini API key (or set `GEMINI_API_KEY` in your environment). If left blank, it automatically uses the smart heuristic engine or local Ollama model.

### 3. Launch
Double-click `start_supercursor.bat` or run:
```bash
python main.py
```

Press **`Ctrl + Alt + C`** anywhere to summon your personal tutor.

---

## Scope & Future Vision

> **Note**: This repository is currently maintained for my own private development environment and personal daily learning. However, the underlying architecture is modular and scalable well beyond my initial scope—it can easily support additional applications (Blender, Premiere, Unreal Engine, Ableton), custom user curricula, and team collaboration down the line.

---

**Crafted by Shreyaskar Panda**

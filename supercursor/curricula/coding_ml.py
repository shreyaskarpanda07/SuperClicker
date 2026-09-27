"""
Coding & Machine Learning Curriculum for SuperCursor.
Designed for hands-on learning in VS Code, Jupyter, PyTorch, CUDA, and Git.
Written from practical engineering experience.
"""

CURRICULUM = {
    "name": "Coding & Machine Learning",
    "target_apps": ["code", "vscode", "terminal", "jupyter"],
    "lessons": [
        {
            "id": "ml_pytorch_loop",
            "title": "Anatomy of a PyTorch Training Loop",
            "description": "Step-by-step breakdown of training neural networks without getting lost in tensor errors.",
            "steps": [
                {
                    "step": 1,
                    "target": "Model Forward Pass",
                    "spoken": "First, we feed our input tensor through the model to get our logits or output predictions.",
                    "label": "outputs = model(inputs)",
                    "action": "inspect",
                    "code_snippet": "outputs = model(inputs)\nloss = criterion(outputs, targets)"
                },
                {
                    "step": 2,
                    "target": "Zero Gradients",
                    "spoken": "Always call optimizer zero grad before backward, otherwise PyTorch accumulates gradients across batches.",
                    "label": "optimizer.zero_grad()",
                    "action": "inspect",
                    "code_snippet": "optimizer.zero_grad()"
                },
                {
                    "step": 3,
                    "target": "Loss Backward Pass",
                    "spoken": "Loss backward calculates dLoss over dW for every trainable parameter using autograd.",
                    "label": "loss.backward()",
                    "action": "inspect",
                    "code_snippet": "loss.backward()"
                },
                {
                    "step": 4,
                    "target": "Optimizer Step",
                    "spoken": "Finally, optimizer step updates the model weights based on the computed gradients.",
                    "label": "optimizer.step()",
                    "action": "inspect",
                    "code_snippet": "optimizer.step()"
                }
            ]
        },
        {
            "id": "vscode_debugging",
            "title": "Interactive Debugging in VS Code",
            "description": "Master breakpoints, variable watches, and call stacks instead of relying only on print statements.",
            "steps": [
                {
                    "step": 1,
                    "target": "Gutter Breakpoint",
                    "spoken": "Click to the left of any line number to drop a red breakpoint indicator.",
                    "label": "Set Breakpoint (F9)",
                    "shortcut": "F9",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Debug Panel / Start Debugging",
                    "spoken": "Press F5 or click the Run and Debug icon in the activity bar to launch execution.",
                    "label": "Run & Debug (F5)",
                    "shortcut": "F5",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Variables & Watch Window",
                    "spoken": "Inspect local tensor shapes, device placement (CPU vs CUDA), and variable types in the watch panel.",
                    "label": "Inspect Variables",
                    "action": "inspect"
                }
            ]
        },
        {
            "id": "cuda_setup_check",
            "title": "CUDA & GPU Sanity Check (RTX 4050)",
            "description": "Ensure PyTorch sees your NVIDIA RTX 4050 GPU and is allocating tensors on device.",
            "steps": [
                {
                    "step": 1,
                    "target": "Integrated Terminal",
                    "spoken": "Open your integrated terminal with Ctrl + Backtick.",
                    "label": "Terminal (Ctrl + `)",
                    "shortcut": "Ctrl + `",
                    "action": "click"
                },
                {
                    "step": 2,
                    "target": "Verify CUDA Device",
                    "spoken": "Run this quick verification check to verify device name and VRAM allocation.",
                    "label": "torch.cuda.is_available()",
                    "action": "type",
                    "code_snippet": "python -c 'import torch; print(\"CUDA Available:\", torch.cuda.is_available(), \"Device:\", torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\")'"
                }
            ]
        }
    ]
}

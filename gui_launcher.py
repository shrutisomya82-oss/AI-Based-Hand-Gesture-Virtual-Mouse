import tkinter as tk
from tkinter import ttk
import threading
import config
from main import run_virtual_mouse


class VirtualMouseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Virtual Mouse Controller")
        self.root.geometry("420x340")
        self.root.resizable(False, False)

        # Style layout
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Title Label
        title_lbl = tk.Label(root, text="AI Gesture Controller", font=("Helvetica", 16, "bold"))
        title_lbl.pack(pady=10)

        # Frame for controls
        control_frame = ttk.LabelFrame(root, text=" Performance & Adjustments ", padding=15)
        control_frame.pack(fill="x", padx=15, pady=5)

        # --- Slider 1: Smoothening (Cursor Stability) ---
        ttk.Label(control_frame, text="Cursor Smoothening (Lower = Faster, Higher = More Stable)").pack(anchor="w")
        self.smooth_val = tk.IntVar(value=config.smoothening)
        self.smooth_scale = ttk.Scale(
            control_frame, from_=1, to=20, orient="horizontal", 
            variable=self.smooth_val, command=self.update_config
        )
        self.smooth_scale.pack(fill="x", pady=(2, 10))

        # --- Slider 2: Click Cooldown Delay ---
        ttk.Label(control_frame, text="Click Cooldown Delay (Seconds)").pack(anchor="w")
        self.delay_val = tk.DoubleVar(value=config.click_delay)
        self.delay_scale = ttk.Scale(
            control_frame, from_=0.1, to=1.5, orient="horizontal", 
            variable=self.delay_val, command=self.update_config
        )
        self.delay_scale.pack(fill="x", pady=(2, 10))

        # --- Running Status ---
        self.status_lbl = tk.Label(root, text="System: STOPPED", font=("Helvetica", 11, "bold"), fg="red")
        self.status_lbl.pack(pady=10)

        # --- Start / Stop Buttons ---
        self.btn_frame = ttk.Frame(root)
        self.btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.btn_frame, text="START MOUSE", command=self.start_system)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = ttk.Button(self.btn_frame, text="STOP MOUSE", command=self.stop_system, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10)

    def update_config(self, *args):
        """Update global configurations in real-time while sliding"""
        config.smoothening = max(1, int(self.smooth_val.get()))
        config.click_delay = round(float(self.delay_val.get()), 2)

    def start_system(self):
        """Launches the OpenCV loop on a background thread"""
        if not config.running:
            config.running = True
            self.status_lbl.config(text="System: RUNNING...", fg="green")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # Use threading to keep the Tkinter GUI fluid and lag-free
            thread = threading.Thread(target=run_virtual_mouse, daemon=True)
            thread.start()

    def stop_system(self):
        """Stops the virtual mouse loop cleanly"""
        config.running = False
        self.status_lbl.config(text="System: STOPPED", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMouseGUI(root)
    root.mainloop()
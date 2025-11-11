#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Keyboard Sound: Manages keyboard click and bell sounds.
#
#  Copyright (c) 2003-2004, Erica Andrews
#  Copyright (c) 2025, DeltaResero
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  SPDX-License-Identifier: GPL-2.0-or-later
################################################################################

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import sys
import os

try:
    from .icewmcp_common import get_data_path
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path


class KeyboardSoundApp:
    """A Tkinter app for managing keyboard click and bell sounds via xset."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Keyboard Sounds")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.resizable(False, False)

        # --- State Variables ---
        self.click_enabled_var = tk.BooleanVar()
        self.click_vol_var = tk.IntVar()
        self.bell_enabled_var = tk.BooleanVar()
        self.bell_vol_var = tk.IntVar()
        self.bell_pitch_var = tk.IntVar()
        self.bell_duration_var = tk.IntVar()

        # --- UI Construction ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        # --- Keyboard Click Frame ---
        click_frame = ttk.Labelframe(main_frame, text="Keyboard Click", padding=10)
        click_frame.pack(fill='x', expand=True, pady=5)

        self.click_check = ttk.Checkbutton(
            click_frame, text="Allow keyboard clicks", variable=self.click_enabled_var,
            command=self.update_widget_states
        )
        self.click_check.pack(anchor='w', pady=(0, 10))

        ttk.Label(click_frame, text="Volume:").pack(anchor='w')
        self.click_scale = ttk.Scale(
            click_frame, from_=0, to=100, orient='horizontal',
            variable=self.click_vol_var, command=self._update_and_apply
        )
        self.click_scale.pack(fill='x', expand=True)

        # --- Keyboard Beep Frame ---
        bell_frame = ttk.Labelframe(main_frame, text="Keyboard Beep", padding=10)
        bell_frame.pack(fill='x', expand=True, pady=5)

        self.bell_check = ttk.Checkbutton(
            bell_frame, text="Allow keyboard beeps", variable=self.bell_enabled_var,
            command=self.update_widget_states
        )
        self.bell_check.pack(anchor='w', pady=(0, 10))

        ttk.Label(bell_frame, text="Volume:").pack(anchor='w')
        self.bell_vol_scale = ttk.Scale(
            bell_frame, from_=0, to=100, orient='horizontal',
            variable=self.bell_vol_var, command=self._update_and_apply
        )
        self.bell_vol_scale.pack(fill='x', expand=True, pady=(0, 5))

        ttk.Label(bell_frame, text="Pitch (Hz):").pack(anchor='w')
        self.bell_pitch_scale = ttk.Scale(
            bell_frame, from_=50, to=2000, orient='horizontal',
            variable=self.bell_pitch_var, command=self._update_and_apply
        )
        self.bell_pitch_scale.pack(fill='x', expand=True, pady=(0, 5))

        ttk.Label(bell_frame, text="Duration (ms):").pack(anchor='w')
        self.bell_duration_scale = ttk.Scale(
            bell_frame, from_=10, to=800, orient='horizontal',
            variable=self.bell_duration_var, command=self._update_and_apply
        )
        self.bell_duration_scale.pack(fill='x', expand=True)

        # --- Buttons ---
        button_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill='x', expand=True)

        self.test_button = ttk.Button(button_frame, text="Test Beep", command=self.test_beep)
        self.test_button.pack(side='left', expand=True, fill='x', padx=2)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_settings)
        self.reset_button.pack(side='left', expand=True, fill='x', padx=2)

        self.close_button = ttk.Button(button_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side='left', expand=True, fill='x', padx=2)

        # Initialization
        self.set_initial_values()
        self.center_window()
        self._check_environment()

    def _check_environment(self):
        """Disable controls if in an unsupported environment like Wayland."""
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            messagebox.showerror(
                "Unsupported Environment",
                "This tool relies on 'xset', which is not supported in a Wayland session. Controls will be disabled."
            )
            # Explicitly disable only the interactive widgets that support the 'state' option.
            widgets_to_disable = [
                self.click_check, self.click_scale,
                self.bell_check, self.bell_vol_scale, self.bell_pitch_scale,
                self.bell_duration_scale, self.test_button, self.reset_button
            ]
            for widget in widgets_to_disable:
                widget.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')

    def get_current_settings(self):
        """Query xset for current sound settings."""
        defaults = {'click': False, 'click_vol': 50, 'bell': False, 'bell_vol': 50, 'bell_pitch': 400, 'bell_duration': 100}
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, check=True)
            output = result.stdout

            # Use raw strings (r'...') for regular expressions to avoid syntax warnings
            defaults['click'] = re.search(r"key click:\s*on", output) is not None
            defaults['bell'] = re.search(r"bell percent:\s*\d+", output) is not None

            m = re.search(r"key click percent:\s*(\d+)", output)
            if m: defaults['click_vol'] = int(m.group(1))

            m = re.search(r"bell percent:\s*(\d+)", output)
            if m: defaults['bell_vol'] = int(m.group(1))

            m = re.search(r"bell pitch:\s*(\d+)", output)
            if m: defaults['bell_pitch'] = int(m.group(1))

            m = re.search(r"bell duration:\s*(\d+)", output)
            if m: defaults['bell_duration'] = int(m.group(1))

        except (FileNotFoundError, subprocess.CalledProcessError):
            pass # Environment check will have already warned the user
        return defaults

    def set_initial_values(self):
        """Populate UI widgets with the current system state."""
        settings = self.get_current_settings()
        self.click_enabled_var.set(settings['click'])
        self.click_vol_var.set(settings['click_vol'])
        self.bell_enabled_var.set(settings['bell'])
        self.bell_vol_var.set(settings['bell_vol'])
        self.bell_pitch_var.set(settings['bell_pitch'])
        self.bell_duration_var.set(settings['bell_duration'])
        self.update_widget_states()

    def update_widget_states(self, *args):
        """Enable or disable sliders based on the checkboxes."""
        self.click_scale.config(state='normal' if self.click_enabled_var.get() else 'disabled')

        bell_state = 'normal' if self.bell_enabled_var.get() else 'disabled'
        for widget in [self.bell_vol_scale, self.bell_pitch_scale, self.bell_duration_scale, self.test_button]:
            widget.config(state=bell_state)

        self.apply_settings()

    def _update_and_apply(self, *args):
        self.apply_settings()

    def apply_settings(self):
        """Apply the selected settings using the 'xset' command."""
        try:
            # Handle key click
            if self.click_enabled_var.get():
                subprocess.run(['xset', 'c', str(self.click_vol_var.get())], check=True)
            else:
                subprocess.run(['xset', '-c'], check=True)

            # Handle bell
            if self.bell_enabled_var.get():
                subprocess.run(['xset', 'b', str(self.bell_vol_var.get()), str(self.bell_pitch_var.get()), str(self.bell_duration_var.get())], check=True)
            else:
                subprocess.run(['xset', 'b', 'off'], check=True)

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def test_beep(self):
        # A simple beep using the root window.
        self.root.bell()

    def reset_settings(self):
        """Reset settings to a reasonable default."""
        self.click_enabled_var.set(True)
        self.click_vol_var.set(50)
        self.bell_enabled_var.set(True)
        self.bell_vol_var.set(50)
        self.bell_pitch_var.set(400)
        self.bell_duration_var.set(100)
        self.update_widget_states()
        self.test_beep()

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = KeyboardSoundApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")
        sys.exit(1)

# EOF

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP-EnergyStar: A utility to manage Energy Star (DPMS) settings.
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

# This block allows the script to be run standalone for testing.
try:
    # Standard relative import for when the app is run as a package.
    from .icewmcp_common import get_data_path
except ImportError:
    # Fallback for standalone execution. Adds the parent 'src' directory
    # to the path to allow finding the 'icewmcp' package.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path


class EnergyStarApp:
    """A Tkinter application for managing DPMS (Energy Star) settings via xset."""

    def __init__(self, root):
        self.root = root

        # --- Window Setup ---
        self.root.title("IceWM CP - Monitor Energy Saving")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.resizable(False, False) # Disable resizing

        # --- Data Mapping (as in the original PyGtk2 version) ---
        self.times = {
            "NEVER": 0, "5 minutes": 300, "10 minutes": 600, "15 minutes": 900,
            "20 minutes": 1200, "30 minutes": 1800, "45 minutes": 2700,
            "1 hour": 3600, "1.5 hours": 5400, "2 hours": 7200,
            "3 hours": 10800, "4 hours": 14400, "5 hours": 18000,
            "6 hours": 21600, "9 hours": 32400, "12 hours": 43200,
            "18 hours": 64800, "24 hours": 86400
        }
        self.time_order = list(self.times.keys())
        self.seconds_to_string = {v: k for k, v in self.times.items()}

        # --- UI Construction ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        try:
            self.logo_image = tk.PhotoImage(file=get_data_path('pixmaps/icewmcp.png'))
            ttk.Label(main_frame, image=self.logo_image).pack(pady=5)
        except Exception as e:
            print(f"Warning: Could not load logo image. {e}", file=sys.stderr)

        ttk.Label(main_frame, text="Monitor Energy Saving (DPMS)", font=("-weight", "bold")).pack(pady=(0, 10))

        self.enabled_var = tk.BooleanVar()
        self.on_off_check = ttk.Checkbutton(
            main_frame,
            text="Enable Monitor Power Saving Features",
            variable=self.enabled_var,
            command=self.update_widget_states
        )
        self.on_off_check.pack(pady=10)

        settings_frame = ttk.Frame(main_frame, padding=5)
        settings_frame.pack(pady=5, fill='x', expand=True)
        self.combos = {}
        labels = [
            "Monitor Standby after:",
            "Monitor Suspend after:",
            "Turn Monitor Off after:"
        ]
        self.keys = ["standby", "suspend", "off"]

        for key, label_text in zip(self.keys, labels):
            row_frame = ttk.Frame(settings_frame)
            row_frame.pack(fill='x', pady=2)
            ttk.Label(row_frame, text=label_text).pack(side='left')
            combo = ttk.Combobox(row_frame, values=self.time_order, state='readonly', width=12)
            combo.pack(side='right')
            combo.bind('<<ComboboxSelected>>', self._on_combo_change)
            self.combos[key] = combo

        button_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill='x', expand=True)

        self.about_button = ttk.Button(button_frame, text="About", command=self.do_about)
        self.about_button.pack(side='left', expand=True, fill='x', padx=2)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.set_initial_values)
        self.reset_button.pack(side='left', expand=True, fill='x', padx=2)

        self.apply_button = ttk.Button(button_frame, text="Apply", command=self.apply_settings)
        self.apply_button.pack(side='left', expand=True, fill='x', padx=2)

        self.close_button = ttk.Button(button_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side='left', expand=True, fill='x', padx=2)

        # --- Finalization ---
        self.set_initial_values()
        self.center_window()
        self._check_environment()

    def _check_environment(self):
        """Check for incompatible environments like Wayland and notify the user."""
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            messagebox.showerror(
                "Unsupported Environment",
                "This tool relies on the 'xset' command, which is not supported in a native Wayland session.\n\n"
                "Controls will be disabled."
            )
            # Disable all controls that modify settings
            self.on_off_check.config(state='disabled')
            self.reset_button.config(state='disabled')
            self.apply_button.config(state='disabled')
            for combo in self.combos.values():
                combo.config(state='disabled')

    def center_window(self):
        """Center the application window and lock its size."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        # Lock the window size to prevent resizing
        self.root.wm_minsize(width, height)
        self.root.wm_maxsize(width, height)

    def get_current_settings(self):
        """Query xset for current DPMS settings and return them in a dictionary."""
        settings = {'enabled': False, 'standby': 0, 'suspend': 0, 'off': 0}
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, check=True)
            output = result.stdout
            settings['enabled'] = "DPMS is Enabled" in output
            values_match = re.search(r"Standby:\s+(\d+)\s+Suspend:\s+(\d+)\s+Off:\s+(\d+)", output)
            if values_match:
                settings['standby'] = int(values_match.group(1))
                settings['suspend'] = int(values_match.group(2))
                settings['off'] = int(values_match.group(3))
        except (FileNotFoundError, subprocess.CalledProcessError):
            # No need for a message box here, as the startup check will have already warned the user
            pass
        return settings

    def set_initial_values(self):
        """Populate all UI widgets with the current system state."""
        settings = self.get_current_settings()
        self.enabled_var.set(settings['enabled'])
        for key, combo in self.combos.items():
            seconds = settings.get(key, 0)
            combo.set(self.seconds_to_string.get(seconds, "NEVER"))
        self.update_widget_states()

    def update_widget_states(self):
        """Enable or disable comboboxes based on the main 'Enable' checkbox."""
        # Don't do anything if controls are already disabled by the environment check
        if self.apply_button['state'] == 'disabled':
            return
        state = 'readonly' if self.enabled_var.get() else 'disabled'
        for combo in self.combos.values():
            combo.config(state=state)

    def _on_combo_change(self, event):
        """
        When a combobox value changes, this function enforces the rule that for
        any non-zero values, standby <= suspend <= off.
        """
        changed_key = None
        for key, combo in self.combos.items():
            if combo == event.widget:
                changed_key = key
                break
        if not changed_key: return

        vals = {k: self.times[c.get()] for k, c in self.combos.items()}

        if changed_key == 'standby':
            if vals['standby'] > vals['suspend'] and vals['suspend'] != 0:
                self.combos['suspend'].set(self.seconds_to_string[vals['standby']])
                vals['suspend'] = vals['standby']
            if vals['suspend'] > vals['off'] and vals['off'] != 0:
                self.combos['off'].set(self.seconds_to_string[vals['suspend']])
        elif changed_key == 'suspend':
            if vals['suspend'] < vals['standby'] and vals['suspend'] != 0:
                self.combos['standby'].set(self.seconds_to_string[vals['suspend']])
            if vals['suspend'] > vals['off'] and vals['off'] != 0:
                self.combos['off'].set(self.seconds_to_string[vals['suspend']])
        elif changed_key == 'off':
            if vals['off'] < vals['suspend'] and vals['off'] != 0:
                self.combos['suspend'].set(self.seconds_to_string[vals['off']])
                vals['suspend'] = vals['off']
            if vals['suspend'] < vals['standby'] and vals['suspend'] != 0:
                self.combos['standby'].set(self.seconds_to_string[vals['suspend']])

    def apply_settings(self):
        """Apply the selected settings to the system using the 'xset' command."""
        try:
            if self.enabled_var.get():
                standby = self.times[self.combos['standby'].get()]
                suspend = self.times[self.combos['suspend'].get()]
                off = self.times[self.combos['off'].get()]
                subprocess.run(['xset', '+dpms'], check=True)
                subprocess.run(['xset', 'dpms', str(standby), str(suspend), str(off)], check=True)
                messagebox.showinfo("Success", "Monitor power settings have been applied.")
            else:
                subprocess.run(['xset', '-dpms'], check=True)
                messagebox.showinfo("Success", "Monitor power saving has been disabled.")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")
        finally:
            self.set_initial_values()

    def do_about(self):
        """Displays the standard About dialog with updated attribution and explanation."""
        messagebox.showinfo(
            "About IceWMCP Energy Star",
            "IceWMCP Energy Star\n\n"
            "Copyright (c) 2003-2004, Erica Andrews\n"
            "Tkinter Port (c) 2025, DeltaResero\n\n"
            "This utility configures your monitor's power saving features using the "
            "Display Power Management Signaling (DPMS) standard, which was widely "
            "adopted as part of the Energy Star program."
        )

if __name__ == '__main__':
    try:
        root = tk.Tk()
        try:
            icon_path = get_data_path('icons/icewmcp-energystar.png')
            if os.path.exists(icon_path):
                 img = tk.PhotoImage(file=icon_path)
                 root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception as e:
            print(f"Warning: Could not set window icon. {e}", file=sys.stderr)
        app = EnergyStarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred on startup:\n{e}")
        sys.exit(1)

# EOF

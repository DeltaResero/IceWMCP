#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Keyboard Repetition: Manages keyboard repeat rate and delay.
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


class KeyboardRepetitionApp:
    """A Tkinter app for managing keyboard auto-repeat settings via xset."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Keyboard Repetition")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.root.withdraw()
        try:
            icon_path = get_data_path('icons/icewmcp-keyboard.png')
            if os.path.exists(icon_path):
                app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

        # Variables to hold the state of the sliders and checkbox
        self.repeat_enabled_var = tk.BooleanVar()
        self.rate_var = tk.IntVar()
        self.delay_var = tk.IntVar()

        # --- UI Construction ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        try:
            self.logo_image = tk.PhotoImage(file=get_data_path('pixmaps/ice-keyboard.png'))
            ttk.Label(main_frame, image=self.logo_image).pack(pady=5)
        except Exception:
            pass  # Fail gracefully

        self.enabled_check = ttk.Checkbutton(main_frame, text="Allow keyboard auto-repeat", variable=self.repeat_enabled_var, command=self.update_widget_states)
        self.enabled_check.pack(pady=10)

        # --- Rate Slider ---
        rate_frame = ttk.Labelframe(main_frame, text="Rate (characters per second)", padding=10)
        rate_frame.pack(fill='x', expand=False, pady=5)
        self.rate_scale = ttk.Scale(rate_frame, from_=5, to=100, orient='horizontal', variable=self.rate_var, command=self._update_and_apply)
        self.rate_scale.pack(fill='x', expand=True)

        # --- Delay Slider ---
        delay_frame = ttk.Labelframe(main_frame, text="Delay (milliseconds)", padding=10)
        delay_frame.pack(fill='x', expand=False, pady=5)
        self.delay_scale = ttk.Scale(delay_frame, from_=200, to=1000, orient='horizontal', variable=self.delay_var, command=self._update_and_apply)
        self.delay_scale.pack(fill='x', expand=True)

        # --- Test Area ---
        test_frame = ttk.Labelframe(main_frame, text="Test Area", padding=10)
        test_frame.pack(fill='x', expand=False, pady=5)
        self.test_entry = ttk.Entry(test_frame)
        self.test_entry.pack(fill='x', expand=True)

        # This spacer pushes the content up and the buttons down when maximized.
        ttk.Frame(main_frame).pack(expand=True, fill='both')

        # --- Buttons ---
        outer_button_frame = ttk.Frame(main_frame)
        outer_button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        inner_button_frame = ttk.Frame(outer_button_frame)
        inner_button_frame.pack() # Center the inner frame

        self.about_button = ttk.Button(inner_button_frame, text="About", command=self.do_about)
        self.about_button.pack(side='left', padx=2)
        self.reset_button = ttk.Button(inner_button_frame, text="Reset", command=self.reset_settings)
        self.reset_button.pack(side='left', padx=2)
        self.close_button = ttk.Button(inner_button_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side='left', padx=2)

        # Initialization
        self.set_initial_values()
        self.center_window()
        self._check_environment()
        self.root.deiconify()

    def _check_environment(self):
        """Disable controls if in an unsupported environment like Wayland."""
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            messagebox.showerror("Unsupported Environment", "This tool relies on 'xset', which is not supported in a Wayland session. Controls will be disabled.")
            for widget in [self.enabled_check, self.rate_scale, self.delay_scale, self.reset_button]:
                widget.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        # Increase minimum width as requested
        min_width = width + 80
        x = (self.root.winfo_screenwidth() // 2) - (min_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{min_width}x{height}+{x}+{y}')
        self.root.minsize(min_width, height)

    def get_current_settings(self):
        """Query xset for current keyboard settings."""
        settings = {'enabled': False, 'rate': 30, 'delay': 500}
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, check=True)
            output = result.stdout
            repeat_match = re.search(r"auto repeat:\s*(\w+)", output)
            if repeat_match:
                settings['enabled'] = (repeat_match.group(1).lower() == 'on')
            values_match = re.search(r"repeat rate:\s*(\d+)\s*delay:\s*(\d+)", output)
            if values_match:
                # xset reports delay then rate.
                settings['delay'] = int(values_match.group(1))
                settings['rate'] = int(values_match.group(2))
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass # Environment check will have already warned the user
        return settings

    def set_initial_values(self):
        """Populate UI widgets with the current system state."""
        settings = self.get_current_settings()
        self.repeat_enabled_var.set(settings['enabled'])
        self.rate_var.set(settings['rate'])
        self.delay_var.set(settings['delay'])
        self.update_widget_states()
        self.test_entry.delete(0, 'end')

    def update_widget_states(self, *args):
        """Enable or disable sliders based on the checkbox."""
        state = 'normal' if self.repeat_enabled_var.get() else 'disabled'
        self.rate_scale.config(state=state)
        self.delay_scale.config(state=state)
        self.apply_settings()

    def _update_and_apply(self, *args):
        """A wrapper to apply settings whenever a slider is moved."""
        self.apply_settings()

    def apply_settings(self):
        """Apply the selected settings using the 'xset' command."""
        try:
            if self.repeat_enabled_var.get():
                rate = self.rate_var.get()
                delay = self.delay_var.get()
                subprocess.run(['xset', 'r', 'rate', str(delay), str(rate)], check=True)
            else:
                subprocess.run(['xset', '-r'], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def reset_settings(self):
        """Reset settings to a reasonable default."""
        self.repeat_enabled_var.set(True)
        self.rate_var.set(30) # A common default rate
        self.delay_var.set(500) # A common default delay
        self.update_widget_states()
        self.test_entry.delete(0, 'end')

    def do_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Keyboard Repetition")
        about_dialog.transient(self.root)
        dialog_width = 380
        dialog_height = 190
        about_dialog.minsize(dialog_width, dialog_height)
        centering_frame = ttk.Frame(about_dialog)
        centering_frame.pack(expand=True, fill='both')
        content_frame = ttk.Frame(centering_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(padx=15, pady=10)
        title_label = ttk.Label(text_frame, text="Keyboard Repetition", font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        copyright_text = ("Copyright (c) 2003-2004, Erica Andrews\n" "Tkinter Port (c) 2025, DeltaResero")
        copyright_label = ttk.Label(text_frame, text=copyright_text, justify=tk.CENTER)
        copyright_label.pack(pady=5)
        desc_label = ttk.Label(text_frame, text="A utility to configure keyboard repeat rate and delay.", justify=tk.CENTER, wraplength=300)
        desc_label.pack(pady=10)
        ok_button = ttk.Button(content_frame, text="OK", command=about_dialog.destroy)
        ok_button.pack(pady=(5, 10))
        about_dialog.update_idletasks()
        root_x, root_y, root_w, root_h = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height()
        x = root_x + (root_w // 2) - (dialog_width // 2)
        y = root_y + (root_h // 2) - (dialog_height // 2)
        about_dialog.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')
        about_dialog.grab_set()
        about_dialog.focus_set()
        ok_button.focus()
        self.root.wait_window(about_dialog)

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = KeyboardRepetitionApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")
        sys.exit(1)

# EOF

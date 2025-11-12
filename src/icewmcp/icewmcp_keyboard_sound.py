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

        self.root.withdraw()
        try:
            icon_path = get_data_path('icons/icewmcp-keyboard.png')
            if os.path.exists(icon_path):
                app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

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
        click_frame.pack(fill='x', expand=False, pady=5)
        self.click_check = ttk.Checkbutton(click_frame, text="Allow keyboard clicks", variable=self.click_enabled_var, command=self.update_widget_states)
        self.click_check.pack(anchor='w', pady=(0, 10))
        ttk.Label(click_frame, text="Volume:").pack(anchor='w')
        self.click_scale = ttk.Scale(click_frame, from_=0, to=100, orient='horizontal', variable=self.click_vol_var, command=self._update_and_apply)
        self.click_scale.pack(fill='x', expand=True)

        # --- Keyboard Beep Frame ---
        bell_frame = ttk.Labelframe(main_frame, text="Keyboard Beep", padding=10)
        bell_frame.pack(fill='x', expand=False, pady=5)
        self.bell_check = ttk.Checkbutton(bell_frame, text="Allow keyboard beeps", variable=self.bell_enabled_var, command=self.update_widget_states)
        self.bell_check.pack(anchor='w', pady=(0, 10))
        ttk.Label(bell_frame, text="Volume:").pack(anchor='w')
        self.bell_vol_scale = ttk.Scale(bell_frame, from_=0, to=100, orient='horizontal', variable=self.bell_vol_var, command=self._update_and_apply)
        self.bell_vol_scale.pack(fill='x', expand=True, pady=(0, 5))
        ttk.Label(bell_frame, text="Pitch (Hz):").pack(anchor='w')
        self.bell_pitch_scale = ttk.Scale(bell_frame, from_=50, to=2000, orient='horizontal', variable=self.bell_pitch_var, command=self._update_and_apply)
        self.bell_pitch_scale.pack(fill='x', expand=True, pady=(0, 5))
        ttk.Label(bell_frame, text="Duration (ms):").pack(anchor='w')
        self.bell_duration_scale = ttk.Scale(bell_frame, from_=10, to=800, orient='horizontal', variable=self.bell_duration_var, command=self._update_and_apply)
        self.bell_duration_scale.pack(fill='x', expand=True)

        # This spacer pushes the content up and the buttons down when maximized.
        ttk.Frame(main_frame).pack(expand=True, fill='both')

        # --- Buttons ---
        outer_button_frame = ttk.Frame(main_frame)
        outer_button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        inner_button_frame = ttk.Frame(outer_button_frame)
        inner_button_frame.pack() # Center the inner frame

        self.about_button = ttk.Button(inner_button_frame, text="About", command=self.do_about)
        self.about_button.pack(side='left', padx=2)
        self.test_button = ttk.Button(inner_button_frame, text="Test Beep", command=self.test_beep)
        self.test_button.pack(side='left', padx=2)
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
            widgets_to_disable = [self.click_check, self.click_scale, self.bell_check, self.bell_vol_scale, self.bell_pitch_scale, self.bell_duration_scale, self.test_button, self.reset_button]
            for widget in widgets_to_disable:
                widget.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.minsize(width, height)

    def do_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Keyboard Sounds")
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
        title_label = ttk.Label(text_frame, text="Keyboard Sounds", font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        copyright_text = ("Copyright (c) 2003-2004, Erica Andrews\n" "Tkinter Port (c) 2025, DeltaResero")
        copyright_label = ttk.Label(text_frame, text=copyright_text, justify=tk.CENTER)
        copyright_label.pack(pady=5)
        desc_label = ttk.Label(text_frame, text="A utility to configure keyboard click and bell sounds.", justify=tk.CENTER, wraplength=300)
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

    def get_current_settings(self):
        """Query xset for current sound settings."""
        defaults = {'click': False, 'click_vol': 50, 'bell': False, 'bell_vol': 50, 'bell_pitch': 400, 'bell_duration': 100}
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, check=True)
            output = result.stdout
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
            pass
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
            if self.click_enabled_var.get():
                subprocess.run(['xset', 'c', str(self.click_vol_var.get())], check=True)
            else:
                subprocess.run(['xset', '-c'], check=True)
            if self.bell_enabled_var.get():
                subprocess.run(['xset', 'b', str(self.bell_vol_var.get()), str(self.bell_pitch_var.get()), str(self.bell_duration_var.get())], check=True)
            else:
                subprocess.run(['xset', 'b', 'off'], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def test_beep(self):
        # This is the correct Tkinter method to trigger the low-level system bell,
        # equivalent to the original PyGTK's GDK.beep().
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Mouse Speed: A utility for setting mouse acceleration.
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


class MouseSpeedApp:
    """A Tkinter app for managing mouse acceleration settings via xset."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Mouse Speed")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.resizable(False, False)

        self.original_acceleration = "4/1"
        self.original_threshold = "4"
        self.timeout_id = None

        self.acceleration_var = tk.IntVar(value=4)
        self.threshold_var = tk.IntVar(value=4)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        try:
            self.logo_image = tk.PhotoImage(file=get_data_path('pixmaps/ps2-mouse.png'))
            ttk.Label(main_frame, image=self.logo_image).pack(pady=5)
        except Exception:
            pass

        accel_frame = ttk.Labelframe(main_frame, text="Acceleration", padding=10)
        accel_frame.pack(fill='x', expand=True, pady=5)
        self.accel_scale = ttk.Scale(accel_frame, from_=1, to=20, orient='horizontal', variable=self.acceleration_var)
        self.accel_scale.pack(fill='x', expand=True)

        thresh_frame = ttk.Labelframe(main_frame, text="Threshold (pixels)", padding=10)
        thresh_frame.pack(fill='x', expand=True, pady=5)
        self.thresh_scale = ttk.Scale(thresh_frame, from_=1, to=10, orient='horizontal', variable=self.threshold_var)
        self.thresh_scale.pack(fill='x', expand=True)

        button_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill='x', expand=True)

        self.about_button = ttk.Button(button_frame, text="About", command=self.do_about)
        self.apply_button = ttk.Button(button_frame, text="Apply", command=self.apply_settings)
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_settings)
        self.close_button = ttk.Button(button_frame, text="Close", command=self.root.destroy)

        for btn in [self.about_button, self.apply_button, self.reset_button, self.close_button]:
            btn.pack(side='left', expand=True, fill='x', padx=2)

        self.set_initial_values()
        self.center_window()
        self._check_environment()

    def _check_environment(self):
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            messagebox.showerror("Unsupported Environment", "This tool relies on 'xset' and is not supported in a Wayland session. Controls will be disabled.")
            # Disable all interactive controls except "About" and "Close"
            widgets_to_disable = [
                self.accel_scale, self.thresh_scale,
                self.apply_button, self.reset_button
            ]
            for widget in widgets_to_disable:
                widget.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')

    def get_current_settings(self):
        try:
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, check=True)
            output = result.stdout
            match = re.search(r"pointer acceleration:\s*(\d+/\d+)\s*threshold:\s*(\d+)", output)
            if match:
                self.original_acceleration = match.group(1)
                self.original_threshold = match.group(2)

                accel_val = int(self.original_acceleration.split('/')[0])
                thresh_val = int(self.original_threshold)
                self.acceleration_var.set(accel_val)
                self.threshold_var.set(thresh_val)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    def set_initial_values(self):
        self.get_current_settings()

    def apply_settings(self):
        accel = self.acceleration_var.get()
        thresh = self.threshold_var.get()
        try:
            subprocess.run(['xset', 'm', str(accel), str(thresh)], check=True)
            self.show_confirmation_dialog()
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def reset_settings(self):
        self.acceleration_var.set(4)
        self.threshold_var.set(4)
        self.apply_settings()

    def revert_settings(self):
        try:
            subprocess.run(['xset', 'm', self.original_acceleration, self.original_threshold], check=True)
            messagebox.showinfo("Reverted", "Mouse settings have been reverted to their original values.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to revert settings:\n{e}")

    def show_confirmation_dialog(self):
        if self.timeout_id:
            self.root.after_cancel(self.timeout_id)
            self.timeout_id = None

        dialog = tk.Toplevel(self.root)
        dialog.title("Confirm Mouse Speed")
        dialog.transient(self.root)
        dialog.grab_set()

        message = "Your mouse speed has been changed.\nIf your mouse becomes unusable, wait 7 seconds for the settings to revert."
        ttk.Label(dialog, text=message, padding=20).pack()

        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill='x')

        def keep():
            if self.timeout_id:
                self.root.after_cancel(self.timeout_id)
            self.timeout_id = None
            dialog.destroy()

        def revert_and_close():
            if self.timeout_id: # Ensure it hasn't already been cancelled
                self.revert_settings()
            dialog.destroy()
            self.timeout_id = None

        ttk.Button(btn_frame, text="Keep New Speed", command=keep).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(btn_frame, text="Revert to Original", command=revert_and_close).pack(side='left', expand=True, fill='x', padx=5)

        self.timeout_id = self.root.after(7000, revert_and_close)

    def do_about(self):
        messagebox.showinfo(
            "About Mouse Speed",
            "IceWMCP Mouse Speed\n\n"
            "Copyright (c) 2003-2004, Erica Andrews\n"
            "Tkinter Port (c) 2025, DeltaResero\n\n"
            "A utility for setting mouse acceleration and threshold."
        )

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = MouseSpeedApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")

# EOF

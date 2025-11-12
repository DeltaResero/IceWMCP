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

        self.root.withdraw()
        try:
            icon_path = get_data_path('icons/icewmcp-mouse.png')
            if os.path.exists(icon_path):
                app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

        self.original_acceleration = "4/1"
        self.original_threshold = "4"
        self.timeout_id = None

        self.acceleration_var = tk.IntVar(value=4)
        self.threshold_var = tk.IntVar(value=4)

        self._create_menu()

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        try:
            self.logo_image = tk.PhotoImage(file=get_data_path('pixmaps/ps2-mouse.png'))
            ttk.Label(main_frame, image=self.logo_image).pack(pady=5)
        except Exception:
            pass

        accel_frame = ttk.Labelframe(main_frame, text="Acceleration", padding=10)
        accel_frame.pack(fill='x', expand=False, pady=5)
        self.accel_scale = ttk.Scale(accel_frame, from_=1, to=20, orient='horizontal', variable=self.acceleration_var)
        self.accel_scale.pack(fill='x', expand=True)

        thresh_frame = ttk.Labelframe(main_frame, text="Threshold (pixels)", padding=10)
        thresh_frame.pack(fill='x', expand=False, pady=5)
        self.thresh_scale = ttk.Scale(thresh_frame, from_=1, to=10, orient='horizontal', variable=self.threshold_var)
        self.thresh_scale.pack(fill='x', expand=True)

        ttk.Frame(main_frame).pack(expand=True, fill='both')

        outer_button_frame = ttk.Frame(main_frame)
        outer_button_frame.pack(fill='x', pady=(10, 0))
        inner_button_frame = ttk.Frame(outer_button_frame)
        inner_button_frame.pack()

        self.apply_button = ttk.Button(inner_button_frame, text="Apply", command=self.apply_settings)
        self.reset_button = ttk.Button(inner_button_frame, text="Reset", command=self.reset_settings)
        for btn in [self.apply_button, self.reset_button]:
            btn.pack(side='left', padx=2)

        self.set_initial_values()
        self.center_window()
        self._check_environment()
        self.root.deiconify()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Close", command=self.root.destroy)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.do_about)

    def _check_environment(self):
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            messagebox.showerror("Unsupported Environment", "This tool relies on 'xset' and is not supported in a Wayland session. Controls will be disabled.")
            widgets_to_disable = [self.accel_scale, self.thresh_scale, self.apply_button, self.reset_button]
            for widget in widgets_to_disable:
                widget.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()

        min_width = width + 107
        min_height = height + 1

        x = (self.root.winfo_screenwidth() // 2) - (min_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (min_height // 2)
        self.root.geometry(f'{min_width}x{min_height}+{x}+{y}')
        self.root.minsize(min_width, min_height)

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

        countdown_var = tk.StringVar()
        ttk.Label(dialog, text="Your mouse speed has changed.\nSettings will revert in:", padding=20).pack()
        ttk.Label(dialog, textvariable=countdown_var, font=("Helvetica", 14, "bold")).pack(pady=(0, 15))

        countdown_job_id = [None]
        def update_countdown(seconds):
            if seconds >= 0:
                countdown_var.set(f"{seconds}...")
                countdown_job_id[0] = dialog.after(1000, update_countdown, seconds - 1)

        update_countdown(7)

        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill='x')

        def keep():
            if self.timeout_id: self.root.after_cancel(self.timeout_id)
            if countdown_job_id[0]: dialog.after_cancel(countdown_job_id[0])
            self.timeout_id = None
            dialog.destroy()

        def revert_and_close():
            if self.timeout_id: self.revert_settings()
            if countdown_job_id[0]: dialog.after_cancel(countdown_job_id[0])
            self.timeout_id = None
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", revert_and_close)
        self.timeout_id = self.root.after(7000, revert_and_close)

        ttk.Button(btn_frame, text="Keep New Speed", command=keep).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(btn_frame, text="Revert to Original", command=revert_and_close).pack(side='left', expand=True, fill='x', padx=5)

    def do_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Mouse Speed")
        about_dialog.transient(self.root)
        dialog_width, dialog_height = 380, 190
        about_dialog.minsize(dialog_width, dialog_height)
        centering_frame = ttk.Frame(about_dialog); centering_frame.pack(expand=True, fill='both')
        content_frame = ttk.Frame(centering_frame); content_frame.place(relx=0.5, rely=0.5, anchor='center')
        text_frame = ttk.Frame(content_frame); text_frame.pack(padx=15, pady=10)
        title_label = ttk.Label(text_frame, text="Mouse Speed", font=('Helvetica', 14, 'bold')); title_label.pack(pady=(0, 10))
        copyright_text = ("Copyright (c) 2003-2004, Erica Andrews\n" "Tkinter Port (c) 2025, DeltaResero")
        copyright_label = ttk.Label(text_frame, text=copyright_text, justify=tk.CENTER); copyright_label.pack(pady=5)
        desc_label = ttk.Label(text_frame, text="A utility for setting mouse acceleration and threshold.", justify=tk.CENTER, wraplength=300); desc_label.pack(pady=10)
        ok_button = ttk.Button(content_frame, text="OK", command=about_dialog.destroy); ok_button.pack(pady=(5, 10))
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
        app = MouseSpeedApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")

# EOF

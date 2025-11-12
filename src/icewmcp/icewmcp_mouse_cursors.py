#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Mouse Cursors: A utility for managing the IceWM cursor theme.
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
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import subprocess

try:
    from .icewmcp_common import get_data_path
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path


class CursorRow:
    """A custom widget to manage a single row in the cursor editor UI."""
    def __init__(self, parent, role_name, target_filename, cursor_dir):
        # The main app is now several levels up due to the canvas/frame structure
        self.parent_app = parent.master.master.master.master
        self.target_filename = target_filename
        self.cursor_dir = cursor_dir
        self.full_path = os.path.join(self.cursor_dir, self.target_filename)

        self.frame = ttk.Frame(parent, padding=5)
        self.frame.pack(fill='x', expand=True)

        self.label = ttk.Label(self.frame, text=f"{role_name} ({target_filename})", width=25)
        self.label.pack(side='left')

        self.image_preview = tk.Label(self.frame, relief='sunken', width=5, height=2, bg="white")
        self.image_preview.pack(side='left', padx=10)

        self.change_button = ttk.Button(self.frame, text="Change...", command=self.change_cursor)
        self.change_button.pack(side='right', padx=10)

        self.image = None # To prevent garbage collection
        self.load_preview()

    def load_preview(self):
        try:
            if os.path.exists(self.full_path):
                self.image = tk.PhotoImage(file=self.full_path)
                self.image_preview.config(image=self.image)
            else:
                self.image_preview.config(image='')
        except tk.TclError:
            self.image_preview.config(image='')

    def change_cursor(self):
        source_path = filedialog.askopenfilename(
            title=f"Select new cursor for {self.target_filename}",
            filetypes=[("XPM Images", "*.xpm"), ("All files", "*.*")]
        )
        if not source_path: return

        try:
            os.makedirs(self.cursor_dir, exist_ok=True)
            shutil.copy(source_path, self.full_path)
            self.load_preview()
            self.parent_app.status_var.set(f"Updated {self.target_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file:\n{e}")
            self.parent_app.status_var.set(f"Error updating {self.target_filename}")


class MouseCursorsApp:
    """A Tkinter app for managing the files in IceWM's cursor theme directory."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Mouse Cursors")

        self.root.withdraw()
        try:
            icon_path = get_data_path('icons/icewmcp-mouse.png')
            if os.path.exists(icon_path):
                app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

        self.cursor_dir = os.path.join(os.environ.get('HOME', ''), '.icewm', 'cursors')
        self.status_var = tk.StringVar(value="Ready.")

        self.cursor_definitions = {
            "Normal Pointer": "left.xpm", "Move Pointer": "move.xpm", "Right Pointer": "right.xpm",
            "Resize Bottom": "sizeB.xpm", "Resize Bottom-Left": "sizeBL.xpm", "Resize Bottom-Right": "sizeBR.xpm",
            "Resize Left": "sizeL.xpm", "Resize Right": "sizeR.xpm", "Resize Top": "sizeT.xpm",
            "Resize Top-Left": "sizeTL.xpm", "Resize Top-Right": "sizeTR.xpm",
        }

        self._create_menu()
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        self.warning_label = ttk.Label(main_frame, text="Warning: Not in an IceWM session. Changes may not be visible.", background="yellow", foreground="black", padding=5, anchor='center')
        self.warning_label.pack(fill='x', pady=(0, 10))
        self.warning_label.pack_forget()

        container = ttk.Frame(main_frame)
        container.pack(fill='both', expand=True)

        style = ttk.Style()
        theme_bg = style.lookup('TFrame', 'background')

        canvas = tk.Canvas(container, bg=theme_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cursor_rows = []
        for name, filename in self.cursor_definitions.items():
            row = CursorRow(scrollable_frame, name, filename, self.cursor_dir)
            self.cursor_rows.append(row)

        outer_button_frame = ttk.Frame(main_frame)
        outer_button_frame.pack(fill='x', pady=(10, 0))
        inner_button_frame = ttk.Frame(outer_button_frame)
        inner_button_frame.pack()
        self.restart_button = ttk.Button(inner_button_frame, text="Restart IceWM to Apply", command=self.restart_icewm)
        self.restart_button.pack(side='left', padx=2)

        ttk.Label(main_frame, textvariable=self.status_var, relief='sunken').pack(fill='x', pady=(10, 0))

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
        session = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if "icewm" not in session:
            self.warning_label.pack(fill='x', pady=(0, 10))
            self.restart_button.config(state='disabled')
            self.status_var.set("Warning: Not in an IceWM session.")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()

        min_height = height + 34

        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (min_height // 2)
        self.root.geometry(f'{width}x{min_height}+{x}+{y}')
        self.root.minsize(width, min_height)

    def restart_icewm(self):
        if messagebox.askyesno("Confirm Restart", "This will attempt to restart IceWM to apply the new cursors.\n\nContinue?"):
            try:
                subprocess.run(['killall', '-HUP', 'icewm'], check=True)
                self.status_var.set("IceWM restart signal sent.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send restart signal to IceWM:\n{e}")

    def do_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Mouse Cursors")
        about_dialog.transient(self.root)
        dialog_width, dialog_height = 380, 190
        about_dialog.minsize(dialog_width, dialog_height)
        centering_frame = ttk.Frame(about_dialog); centering_frame.pack(expand=True, fill='both')
        content_frame = ttk.Frame(centering_frame); content_frame.place(relx=0.5, rely=0.5, anchor='center')
        text_frame = ttk.Frame(content_frame); text_frame.pack(padx=15, pady=10)
        title_label = ttk.Label(text_frame, text="Mouse Cursors", font=('Helvetica', 14, 'bold')); title_label.pack(pady=(0, 10))
        copyright_text = ("Copyright (c) 2003-2004, Erica Andrews\n" "Tkinter Port (c) 2025, DeltaResero")
        copyright_label = ttk.Label(text_frame, text=copyright_text, justify=tk.CENTER); copyright_label.pack(pady=5)
        desc_label = ttk.Label(text_frame, text="A utility for managing the IceWM cursor theme.", justify=tk.CENTER, wraplength=300); desc_label.pack(pady=10)
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
        app = MouseCursorsApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")

# EOF

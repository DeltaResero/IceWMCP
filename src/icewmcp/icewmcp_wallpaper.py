#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Wallpaper Settings: A utility to manage IceWM desktop background.
#
#  Copyright (c) 2003, David Moore <djm6202@yahoo.co.nz>
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
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
import sys
import subprocess

try:
    from .icewmcp_common import get_data_path
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path

PREF_FILE_NAME = "preferences"
DEFAULT_BG_COLOR = "#000000"

class WallpaperApp:
    """Manages IceWM wallpaper and background color settings."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Wallpaper Settings")

        self.root.withdraw()
        try:
            icon_path = get_data_path('icons/icewmcp-wallpaper.png')
            if os.path.exists(icon_path):
                app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

        self.pref_file = os.path.join(os.environ.get('HOME', ''), '.icewm', PREF_FILE_NAME)

        self.bg_color_var = tk.StringVar(value=DEFAULT_BG_COLOR)
        self.image_path_var = tk.StringVar(value="")
        self.dir_path_var = tk.StringVar(value=os.path.expanduser("~"))
        self.scaling_mode_var = tk.StringVar(value="Scaled")
        self.status_var = tk.StringVar(value="Ready.")

        self._create_menu()
        self._build_ui()
        self._load_preferences()
        self._refresh_file_list()

        self.root.deiconify()
        self.root.update_idletasks()
        self._center_window()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Apply Changes Now...", command=self._apply_settings, accelerator="Ctrl+A")
        self.root.bind("<Control-a>", lambda e: self._apply_settings())
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy, accelerator="Ctrl+Q")
        self.root.bind("<Control-q>", lambda e: self.root.destroy())

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self._show_about)

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill='both', expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(side='top', fill='x', pady=(0, 3))
        ttk.Label(header_frame, text="IceWM Control Panel - Wallpaper Settings",
                  font=('Helvetica', 11, 'bold')).pack(side='left')

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side='top', fill='both', expand=True)

        # Image browser
        top_frame = ttk.LabelFrame(content_frame, text="Images", padding=3)
        top_frame.pack(side='top', fill='x', pady=(0, 3))

        dir_frame = ttk.Frame(top_frame)
        dir_frame.pack(fill='x', pady=(0, 2))
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_path_var, width=30)
        self.dir_entry.pack(side='left', padx=(0, 2))
        self.dir_entry.bind('<Return>', lambda e: self._refresh_file_list())
        ttk.Button(dir_frame, text="Go", width=4, command=self._refresh_file_list).pack(side='left', padx=(0, 2))
        ttk.Button(dir_frame, text="Up", width=4, command=self._go_up_dir).pack(side='left', padx=(0, 2))
        ttk.Button(dir_frame, text="Browse", width=7, command=self._browse_dir).pack(side='left', padx=(0, 10))
        ttk.Button(dir_frame, text="Apply", command=self._apply_settings).pack(side='left', padx=(0, 2))
        ttk.Button(dir_frame, text="Close", command=self.root.destroy).pack(side='left')

        list_frame = ttk.Frame(top_frame)
        list_frame.pack(fill='x')
        self.file_list = tk.Listbox(list_frame, selectmode='single', exportselection=False, height=3)
        self.file_list.pack(side='left', fill='x', expand=True)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        vsb.pack(side='right', fill='y')
        self.file_list.config(yscrollcommand=vsb.set)
        self.file_list.bind('<<ListboxSelect>>', self._on_list_select)

        # Preview and options
        bottom_frame = ttk.Frame(content_frame)
        bottom_frame.pack(side='top', fill='both', expand=True)

        preview_container = ttk.LabelFrame(bottom_frame, text="Preview", padding=3)
        preview_container.pack(side='left', padx=(0, 3))
        self.preview_canvas = tk.Canvas(preview_container, width=206, height=160,
                                        bg='#000000', highlightthickness=0)
        self.preview_canvas.pack()

        options_frame = ttk.Frame(bottom_frame)
        options_frame.pack(side='left', fill='both', expand=True)

        color_frame = ttk.LabelFrame(options_frame, text="Desktop Color", padding=3)
        color_frame.pack(fill='x', pady=(0, 3))

        self.color_entry = ttk.Entry(color_frame, textvariable=self.bg_color_var, width=12)
        self.color_entry.pack(side='left', padx=(0, 3))
        self.color_entry.bind('<FocusOut>', lambda e: self._update_preview())
        self.color_entry.bind('<Return>', lambda e: self._update_preview())

        self.color_btn = tk.Button(color_frame, text=" ", width=3, relief='sunken', command=self._pick_color)
        self.color_btn.pack(side='left')
        self._update_color_btn()

        opts_frame = ttk.LabelFrame(options_frame, text="Scaling", padding=3)
        opts_frame.pack(fill='x', pady=(0, 3))

        ttk.Radiobutton(opts_frame, text="Center", variable=self.scaling_mode_var,
                       value="Centered", command=self._update_preview).pack(side='left', padx=3)
        ttk.Radiobutton(opts_frame, text="Tile", variable=self.scaling_mode_var,
                       value="Tiled", command=self._update_preview).pack(side='left', padx=3)
        ttk.Radiobutton(opts_frame, text="Scale", variable=self.scaling_mode_var,
                       value="Scaled", command=self._update_preview).pack(side='left', padx=3)

        sel_frame = ttk.LabelFrame(options_frame, text="Selected", padding=3)
        sel_frame.pack(fill='both', expand=True)

        self.sel_lbl = ttk.Label(sel_frame, text="[NONE]", anchor='w',
                                font=('Helvetica', 8), wraplength=200)
        self.sel_lbl.pack(fill='x', pady=(0, 2))

        self.edit_btn = ttk.Button(sel_frame, text="Edit Image",
                                   command=self._edit_image, state='disabled')
        self.edit_btn.pack(fill='x')

        status_lbl = ttk.Label(main_frame, textvariable=self.status_var,
                              relief='sunken', anchor='w')
        status_lbl.pack(side='bottom', fill='x', pady=(3, 0))

    def _center_window(self):
        w, h = 620, 380
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

    def _load_preferences(self):
        """Load settings from IceWM preferences file."""
        if not os.path.exists(self.pref_file):
            return

        try:
            with open(self.pref_file, 'r') as f:
                lines = f.readlines()

            p_img, p_color, p_scaled, p_center = "", "", "0", "0"

            for line in lines:
                line = line.strip()
                if line.startswith("#"):
                    continue

                if "DesktopBackgroundImage=" in line:
                    p_img = line.split("=", 1)[1].strip('"')
                elif "DesktopBackgroundColor=" in line:
                    p_color = line.split("=", 1)[1].strip('"')
                elif "DesktopBackgroundScaled=" in line:
                    p_scaled = line.split("=", 1)[1].strip()
                elif "DesktopBackgroundCenter=" in line:
                    p_center = line.split("=", 1)[1].strip()

            if p_color:
                self.bg_color_var.set(p_color)
                self._update_color_btn()

            if p_img:
                self.image_path_var.set(p_img)
                dirname = os.path.dirname(p_img)
                if dirname:
                    self.dir_path_var.set(dirname)
                else:
                    self.dir_path_var.set(os.path.join(os.environ.get('HOME', ''), '.icewm'))

            if p_scaled == "1":
                self.scaling_mode_var.set("Scaled")
            elif p_center == "1":
                self.scaling_mode_var.set("Centered")
            else:
                self.scaling_mode_var.set("Tiled")

        except Exception as e:
            print(f"Error loading preferences: {e}", file=sys.stderr)

    def _refresh_file_list(self):
        d = self.dir_path_var.get()
        if not os.path.isdir(d):
            self.status_var.set(f"Invalid directory: {d}")
            return

        self.file_list.delete(0, 'end')
        self.file_list.insert('end', "[NONE]")

        try:
            files = []
            for f in os.listdir(d):
                full = os.path.join(d, f)
                if os.path.isfile(full):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in ['.xpm', '.png', '.jpg', '.jpeg', '.gif']:
                        files.append(f)

            for f in sorted(files):
                self.file_list.insert('end', f)

            curr = os.path.basename(self.image_path_var.get())
            try:
                idx = files.index(curr)
                self.file_list.selection_set(idx + 1)
                self.file_list.see(idx + 1)
            except:
                pass

            self.status_var.set(f"Loaded {len(files)} images from {d}")
        except Exception as e:
            self.status_var.set(f"Error reading directory: {e}")

    def _go_up_dir(self):
        curr = self.dir_path_var.get()
        parent = os.path.dirname(curr)
        if parent and os.path.isdir(parent):
            self.dir_path_var.set(parent)
            self._refresh_file_list()

    def _browse_dir(self):
        curr = self.dir_path_var.get()
        new_dir = filedialog.askdirectory(initialdir=curr, title="Select Image Directory")
        if new_dir:
            self.dir_path_var.set(new_dir)
            self._refresh_file_list()

    def _on_list_select(self, event):
        sel = self.file_list.curselection()
        if not sel:
            return

        fname = self.file_list.get(sel[0])
        if fname == "[NONE]":
            self.image_path_var.set("")
            self.sel_lbl.config(text="[NONE]")
            self.edit_btn.config(state='disabled')
        else:
            full = os.path.join(self.dir_path_var.get(), fname)
            self.image_path_var.set(full)
            self.sel_lbl.config(text=fname)
            self.edit_btn.config(state='normal')

        self._update_preview()

    def _pick_color(self):
        curr = self.bg_color_var.get()
        c = colorchooser.askcolor(initialcolor=curr, title="Select Desktop Color")
        if c[1]:
            self.bg_color_var.set(c[1])
            self._update_color_btn()
            self._update_preview()

    def _update_color_btn(self):
        try:
            c = self.bg_color_var.get()
            self.color_btn.config(bg=c, activebackground=c)
        except:
            pass

    def _update_preview(self):
        self.preview_canvas.delete("all")

        try:
            bg = self.bg_color_var.get()
            self.preview_canvas.config(bg=bg if bg else "#000000")
        except:
            self.preview_canvas.config(bg="#000000")

        path = self.image_path_var.get()
        if path and os.path.exists(path):
            try:
                img = tk.PhotoImage(file=path)
                self.preview_img_ref = img
                self.preview_canvas.create_image(103, 80, image=img, anchor='center')
            except Exception as e:
                print(f"Preview error: {e}", file=sys.stderr)

    def _apply_settings(self):
        lines = []
        if os.path.exists(self.pref_file):
            with open(self.pref_file, 'r') as f:
                lines = f.readlines()
        else:
            lines = ["# IceWM preferences (managed by IceWMCP)\n"]

        new_lines = []
        keys_handled = []

        updates = {
            "DesktopBackgroundImage": f"\"{self.image_path_var.get()}\"",
            "DesktopBackgroundColor": f"\"{self.bg_color_var.get()}\"",
            "DesktopBackgroundScaled": "1" if self.scaling_mode_var.get() == "Scaled" else "0",
            "DesktopBackgroundCenter": "1" if self.scaling_mode_var.get() == "Centered" else "0",
            "DesktopBackgroundTiled": "1" if self.scaling_mode_var.get() == "Tiled" else "0"
        }

        for line in lines:
            handled = False
            for k, v in updates.items():
                if line.strip().startswith(k + "="):
                    new_lines.append(f"{k}={v}\n")
                    keys_handled.append(k)
                    handled = True
                    break
            if not handled:
                new_lines.append(line)

        for k, v in updates.items():
            if k not in keys_handled:
                new_lines.append(f"{k}={v}\n")

        try:
            with open(self.pref_file, 'w') as f:
                f.writelines(new_lines)

            subprocess.Popen(["icewmbg", "-r"])
            self.status_var.set("Settings applied. Restarted icewmbg.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences:\n{e}")

    def _find_image_editor(self):
        """Search for available image editors on the system."""

        # First, try to get the system's default image editor via xdg-mime
        try:
            result = subprocess.run(
                ['xdg-mime', 'query', 'default', 'image/png'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                desktop_file = result.stdout.strip()
                if desktop_file:
                    # Extract executable name from .desktop file
                    # e.g., "gimp.desktop" -> try "gimp"
                    app_name = desktop_file.replace('.desktop', '')

                    # Verify the command exists
                    check = subprocess.run(['which', app_name],
                                         capture_output=True,
                                         timeout=1)
                    if check.returncode == 0:
                        return app_name
        except:
            pass

        # Fallback: search for common image editors
        editors = [
            'gimp', 'krita', 'kolourpaint', 'mtpaint', 'gpaint',
            'pinta', 'xpaint', 'gthumb', 'eog', 'feh', 'display'
        ]

        for editor in editors:
            try:
                result = subprocess.run(['which', editor],
                                      capture_output=True,
                                      text=True,
                                      timeout=1)
                if result.returncode == 0:
                    return editor
            except:
                continue

        return None

    def _edit_image(self):
        path = self.image_path_var.get()
        if not path or not os.path.exists(path):
            return

        editor = self._find_image_editor()

        if editor:
            try:
                subprocess.Popen([editor, path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch {editor}:\n{e}")
        else:
            messagebox.showwarning(
                "No Image Editor Found",
                "No image editor was found on your system.\n\n"
                "To edit images, please install one of the following:\n"
                "• GIMP (gimp)\n"
                "• Krita (krita)\n"
                "• mtPaint (mtpaint)\n"
                "• KolourPaint (kolourpaint)\n"
                "• Pinta (pinta)\n"
                "\nOr use your system's package manager to install\n"
                "an image editor of your choice."
            )

    def _show_about(self):
        msg = (
            "IceWMCP Wallpaper Settings\n\n"
            "Copyright (c) 2003, David Moore <djm6202@yahoo.co.nz>\n"
            "Copyright (c) 2003-2004, Erica Andrews\n"
            "Copyright (c) 2025, DeltaResero\n\n"
            "A utility to manage the desktop background for IceWM."
        )
        messagebox.showinfo("About", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperApp(root)
    root.mainloop()

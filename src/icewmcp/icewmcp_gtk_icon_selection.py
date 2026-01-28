#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Icon Selection Dialog
#
#  Copyright (c) 2000-2002, Dirk Moebius <dmoebius@gmx.net>
#  Copyright (c) 2000-2002, Mike Hostetler <thehaas@binary.net>
#  Copyright (c) 2003, David Moore <djm6202@yahoo.co.nz>
#  Copyright (c) 2003-2004, Erica Andrews <PhrozenSmoke@yahoo.com>
#  Copyright (c) 2026, DeltaResero
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  SPDX-License-Identifier: GPL-2.0-or-later
################################################################################

import os
import sys
import glob
import tkinter as tk
from tkinter import ttk

# --- Helper Functions (Local) ---

def getIceWMConfigPath():
    """Returns the path to the IceWM config directory."""
    home = os.path.expanduser("~/.icewm")
    if os.path.isdir(home):
        return home
    return "/etc/icewm"

def _(somestr):
    """Translation stub (pass-through for now)."""
    return somestr

# --- Icon Cache ---
CACHED = {}

def findIcons(paths):
    """
    Scans directories for icons (.xpm, .png) under a size threshold.
    Ported from original logic by Erica Andrews.
    
    Returns dict: {filepath: filepath}
    """
    icons = {}
    
    for d in paths:
        if not os.path.isdir(d):
            continue
            
        # 1. *_16x16.xpm < 12kb
        for f in glob.glob(os.path.join(d, "*_16x16.xpm")):
            try:
                if os.path.getsize(f) < 12000:
                    icons[f] = f
            except:
                pass

        # 2. mini/*.xpm < 12kb
        for f in glob.glob(os.path.join(d, "mini", "*.xpm")):
            try:
                if os.path.getsize(f) < 12000:
                    icons[f] = f
            except:
                pass

        # 3. *.xpm < 12kb
        for f in glob.glob(os.path.join(d, "*.xpm")):
            try:
                if os.path.getsize(f) < 12000:
                    icons[f] = f
            except:
                pass

        # 4. *.png < 11kb
        for f in glob.glob(os.path.join(d, "*.png")):
            try:
                if os.path.getsize(f) < 11000:
                    icons[f] = f
            except:
                pass
            
    return icons


class IconSelectionDialog(tk.Toplevel):
    """
    A dialog for browsing and selecting icons from the filesystem.
    """
    
    def __init__(self, parent=None, num_columns=9, my_paths=None, update_meth=None):
        super().__init__(parent)
        
        self.MYPATHS = my_paths if my_paths else []
        self.UPDATER = update_meth
        self.num_columns = num_columns
        self.selected = (None, None)  # (name, filepath)
        
        self.buttons = []
        self.photo_refs = []  # Keep references alive to prevent GC
        
        self.title(_("IceWMCP Icon Browser"))
        self.geometry("550x500")
        
        self.protocol("WM_DELETE_WINDOW", self.do_close)
        
        # Build the UI
        self._init_gui()
        
        # Center on screen (or parent if visible)
        self._center_window(parent)
        
        # Start loading icons after a brief delay
        self.after(100, self._load_icons)

    def _center_window(self, parent):
        """Centers the window on screen or relative to parent."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100:
            w = 550
        if h < 100:
            h = 500
            
        if parent and parent.winfo_viewable():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        else:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = (sw // 2) - (w // 2)
            y = (sh // 2) - (h // 2)
            
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

    def _init_gui(self):
        """Constructs the dialog UI."""
        main_frame = ttk.Frame(self, padding=5)
        main_frame.pack(fill='both', expand=True)

        # 1. Top Entry (Selected File)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=5)
        
        ttk.Label(top_frame, text=_("Selected:")).pack(side='left')
        self.file_entry = ttk.Entry(top_frame)
        self.file_entry.pack(side='left', fill='x', expand=True, padx=5)

        # 2. Scrollable Canvas for Icon Grid
        canvas_frame = ttk.Frame(main_frame, relief='sunken', borderwidth=1)
        canvas_frame.pack(fill='both', expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, background='#ffffff')
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # 3. Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill='x', pady=2)
        self.status_lbl = ttk.Label(main_frame, text=_("Ready"), font=("Sans", 8))
        self.status_lbl.pack(fill='x')

        # 4. Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)
        
        # Columns Spinner
        ttk.Label(control_frame, text=_("Columns:")).pack(side='left')
        self.spin_col = ttk.Spinbox(control_frame, from_=1, to=20, width=3, command=self._on_columns_change)
        self.spin_col.set(self.num_columns)
        self.spin_col.pack(side='left', padx=5)
        self.spin_col.bind('<Return>', self._on_columns_change)

        # Buttons on the right
        btn_box = ttk.Frame(control_frame)
        btn_box.pack(side='right')
        
        ttk.Button(btn_box, text=_("Icon Paths..."), command=self._show_paths_dialog).pack(side='left', padx=2)
        ttk.Button(btn_box, text=_("Reload"), command=self.do_reload).pack(side='left', padx=2)
        ttk.Button(btn_box, text=_("Close"), command=self.do_close).pack(side='left', padx=2)
        
        self.btn_select = ttk.Button(btn_box, text=_("SELECT"), command=self.do_ok, state='disabled')
        self.btn_select.pack(side='left', padx=2)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _load_icons(self):
        """Scans for icons and populates the grid."""
        self.status_lbl.config(text=_("Scanning for icons..."))
        self.update()
        
        icons_map = findIcons(self.MYPATHS)
        sorted_items = sorted(icons_map.items(), key=lambda x: x[0])
        
        total = len(sorted_items)
        self.progress['maximum'] = total if total > 0 else 1
        self.progress['value'] = 0
        
        self.buttons = []
        self.photo_refs = []
        
        # Clear old widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        count = 0
        
        for name, path in sorted_items:
            img = self._load_image(path)
            if img:
                self.photo_refs.append(img)
                btn = ttk.Button(self.scroll_frame, image=img, takefocus=True)
                btn.path = path
                btn.name = name
                btn.config(command=lambda b=btn: self._on_icon_click(b))
                self.buttons.append(btn)
                
            count += 1
            if count % 20 == 0:
                self.progress['value'] = count
                self.status_lbl.config(text=f"Loading {count}/{total}...")
                self.update()
                
        self.status_lbl.config(text=f"Found {len(self.buttons)} icons.")
        self.progress['value'] = 0
        
        self._reflow_grid()

    def _load_image(self, path):
        """Loads an image, caching the result."""
        if path in CACHED:
            return CACHED[path]
        try:
            img = tk.PhotoImage(file=path)
            CACHED[path] = img
            return img
        except Exception:
            return None

    def _reflow_grid(self):
        """Arranges icons in a grid based on the current column count."""
        cols = int(self.spin_col.get())
        
        for i, btn in enumerate(self.buttons):
            r = i // cols
            c = i % cols
            btn.grid(row=r, column=c, padx=2, pady=2)

    def _on_columns_change(self, *args):
        """Handles column count spinner changes."""
        try:
            val = int(self.spin_col.get())
            if val < 1:
                val = 1
            self.num_columns = val
            self._reflow_grid()
        except:
            pass

    def _on_icon_click(self, btn):
        """Handles clicking on an icon button."""
        self.selected = (btn.name, btn.path)
        self.file_entry.delete(0, 'end')
        self.file_entry.insert(0, btn.path)
        self.btn_select.config(state='normal')
        self.status_lbl.config(text=os.path.basename(btn.path))

    def do_reload(self):
        """Reloads the icon list."""
        self._load_icons()

    def _show_paths_dialog(self):
        """Shows a dialog to edit icon search paths."""
        d = tk.Toplevel(self)
        d.title(_("Icon Paths"))
        d.geometry("400x200")
        d.transient(self)
        
        # Position near parent
        self.update_idletasks()
        dx = self.winfo_rootx() + 50
        dy = self.winfo_rooty() + 50
        d.geometry(f"+{dx}+{dy}")
        
        lbl = ttk.Label(d, text=_("Enter icon paths, separated by colons:"))
        lbl.pack(padx=10, pady=5, anchor='w')
        
        txt = tk.Text(d, height=5)
        txt.pack(padx=10, pady=5, fill='both', expand=True)
        current_paths = ":".join(self.MYPATHS)
        txt.insert('1.0', current_paths)
        
        def save_and_reload():
            raw = txt.get('1.0', 'end').strip().replace("\n", "")
            new_paths = [p.strip() for p in raw.split(':') if p.strip()]
            self.MYPATHS = new_paths
            # Save to file
            try:
                with open(os.path.expanduser("~/.icewmcp_icons"), "w") as f:
                    f.write(raw)
            except:
                pass
            
            d.destroy()
            self.do_reload()
            
        ttk.Button(d, text=_("Save & Reload"), command=save_and_reload).pack(pady=10)

    def do_ok(self, event=None):
        """Confirms the selection and closes the dialog."""
        if self.selected[1]:
            if self.UPDATER:
                self.UPDATER(self.selected[1])
            else:
                print(self.selected[1])  # Debug fallback
        self.destroy()

    def do_close(self):
        """Closes the dialog without selection."""
        self.destroy()


# --- Default Icon Paths ---

DEFAULT_ICON_PATHS = [
    getIceWMConfigPath() + "/icons",
    "/usr/share/icons",
    "/usr/share/pixmaps",
    "/usr/share/icewmcp/applet-icons",
    "/usr/local/share/icons",
    "/usr/share/icons/hicolor/48x48/apps",
    "/usr/share/icons/hicolor/48x48/devices",
]


def getMyIcons():
    """Loads custom icon paths from ~/.icewmcp_icons or returns defaults."""
    try:
        path_file = os.path.expanduser("~/.icewmcp_icons")
        if os.path.exists(path_file):
            with open(path_file, 'r') as f:
                content = f.read().strip().replace("\n", "")
                return [p for p in content.split(':') if p]
    except:
        pass
    return DEFAULT_ICON_PATHS


def show_dlg(updater=None):
    """Shows the Icon Selection Dialog (standalone mode)."""
    root = tk.Tk()
    root.withdraw()  # Hidden root
    
    paths = getMyIcons()
    
    dlg = IconSelectionDialog(parent=root, my_paths=paths, update_meth=updater)
    
    # Wait for the dialog to close
    dlg.wait_window()
    
    # Clean up root
    root.destroy()


if __name__ == "__main__":
    # Test Mode
    def test_update(path):
        print(f"SELECTED: {path}")
        
    show_dlg(updater=test_update)

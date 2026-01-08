#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWM Control Panel
#
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

import tkinter as tk
from tkinter import ttk
import os
import sys
import glob
import subprocess
import shutil
from pathlib import Path

# Local imports
try:
    from . import icewmcp_common
    from .icewmcp_dialogs import message, ICON_ERROR, ICON_INFO
except ImportError:
    # Fallback for running directly from source tree
    import icewmcp_common
    from icewmcp_dialogs import message, ICON_ERROR, ICON_INFO

# Constants
WM_TITLE = "IceWM Control Panel"
WM_CLASS = "IceWMControlPanel"
APP_VERSION = "3.3" # Updated for Python 3 port

class ControlPanelApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(WM_TITLE)
        
        # Responsive Default Geometry
        screen_width = self.winfo_screenwidth()
        if screen_width > 1024:
            self.geometry("880x680") # Large display
        else:
            self.geometry("590x390") # Wii / Legacy restore size
            
            # Force update to ensure WM registers the restore geometry
            self.update_idletasks()
            
            # Default to maximized on small screens for best experience
            try:
                self.attributes('-zoomed', True)
            except Exception:
                pass
            
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Attempt to set window icon
        try:
            # Try to find the icon in standard locations
            icon_path = self.find_resource("icewmcp.png")
            if icon_path:
                icon_img = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon_img)
        except Exception:
            pass

        # Styles
        style = ttk.Style()
        # Icon View Style: Centered, Top image
        style.configure("Icon.TButton", compound="top", anchor="center", justify="center", wraplength=100, padding=4)
        # List View Style: Left aligned, Left image
        style.configure("List.TButton", compound="left", anchor="w", justify="left", wraplength=180, padding=4)

        # --- Menu Bar ---
        self.create_menu()

        # --- Toolbar / Header ---
        self.create_toolbar()

        # --- Main View Area ---
        self.create_main_view()

        # Data
        self.applets = {}
        self.applet_buttons = [] # Store widgets for reflow
        self.ignore_list = self.load_ignore_list()
        self.icon_cache = []
        
        # View State
        self.view_mode = 'icon' # 'icon' or 'list'

        # Load and verify applets
        self.applet_dir = self.find_applet_dir()
        
        # Initial View Load
        self.refresh_view()

    def create_menu(self):
        menubar = tk.Menu(self)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Refresh View", command=self.refresh_view, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Icon View", command=lambda: self.set_view_mode('icon'))
        view_menu.add_command(label="List View", command=lambda: self.set_view_mode('list'))
        menubar.add_cascade(label="View", menu=view_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<Control-r>", lambda e: self.refresh_view())
        self.bind("<Control-q>", lambda e: self.quit_app())

    def create_toolbar(self):
        # A simple header area
        header_frame = ttk.Frame(self, relief='groove', padding=5)
        header_frame.pack(fill='x', side='top')
        
        # Title Label
        title_lbl = ttk.Label(header_frame, text=WM_TITLE, font=("Sans", 12, "bold"))
        title_lbl.pack(side='left', padx=10)

        # View Switcher Buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Icons", width=6, command=lambda: self.set_view_mode('icon')).pack(side='left', padx=1)
        ttk.Button(btn_frame, text="List", width=6, command=lambda: self.set_view_mode('list')).pack(side='left', padx=1)

    def create_main_view(self):
        # Canvas + Scrollbar for scrollable area
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True, padx=2, pady=2)

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        
        # The scrollable frame sits inside the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Bind configuration events
        # 1. Update scroll region when frame content changes size
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Bind canvas resize to trigger reflow
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _on_canvas_resize(self, event):
        """Reflow buttons when canvas width changes."""
        self.reflow_icons(event.width)

    def find_resource(self, filename):
        """Find a resource file (icon, etc) in common locations."""
        # 1. Check local source tree (src/icewmcp/filename)
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(local_path):
            return local_path
            
        # 2. Check ../../share/icewmcp (development run)
        dev_share = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'share', filename)
        if os.path.exists(dev_share):
            return dev_share

        # 3. Standard install path
        if os.path.exists(os.path.join("/usr/share/icewmcp", filename)):
            return os.path.join("/usr/share/icewmcp", filename)
            
        return None

    def find_applet_dir(self):
        """Locate the directory containing .cpl files."""
        # 1. Dev environment: ../../share/applets
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dev_applets = os.path.join(root_dir, 'share', 'applets')
        if os.path.isdir(dev_applets):
            return dev_applets
            
        # 2. Standard installation
        if os.path.isdir("/usr/share/icewmcp/applets"):
            return "/usr/share/icewmcp/applets"
            
        return None

    def load_applets(self):
        """Parse .cpl files in the applet directory."""
        applets = {}
        if not self.applet_dir:
            return applets
            
        cpl_files = glob.glob(os.path.join(self.applet_dir, "*.cpl"))
        
        for cpl_path in cpl_files:
            try:
                data = {}
                with open(cpl_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        key, val = line.split('=', 1)
                        data[key.strip().lower()] = val.strip()
                
                # Validation
                name = data.get('name', '').replace(r'\n', ' ')
                exe = data.get('exec', '')
                icon = data.get('icon', 'default.xpm')
                hint = data.get('hint', '')
                
                if name and exe:
                    applets[name] = {
                        'name': name,
                        'exec': exe,
                        'icon': icon,
                        'hint': hint
                    }
            except Exception:
                continue
                
        return applets

    def load_ignore_list(self):
        """Load list of ignored applets from ~/.icecp_ignore"""
        ignore = []
        try:
            path = os.path.expanduser("~/.icecp_ignore")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    ignore = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception:
            pass
        return ignore

    def set_view_mode(self, mode):
        if self.view_mode != mode:
            self.view_mode = mode
            self.refresh_view()

    def refresh_view(self):
        # Clear existing widgets
        for btn in self.applet_buttons:
            btn.destroy()
        self.applet_buttons = []
        self.icon_cache = [] 

        self.applets = self.load_applets()
        sorted_names = sorted(self.applets.keys())
        
        # Apply style based on mode
        current_style = "Icon.TButton" if self.view_mode == 'icon' else "List.TButton"
        compound_val = "top" if self.view_mode == 'icon' else "left"
        
        # Search paths for icons
        search_paths = []
        if self.applet_dir:
             search_paths.append(os.path.join(os.path.dirname(self.applet_dir), 'applet-icons'))
        search_paths.append('/usr/share/icewmcp/applet-icons')

        for name in sorted_names:
            if name in self.ignore_list:
                continue
                
            data = self.applets[name]
            
            # --- Icon Loading ---
            icon_file = data['icon']
            icon_path = None
            
            for p in search_paths:
                if os.path.exists(os.path.join(p, icon_file)):
                    icon_path = os.path.join(p, icon_file)
                    break
            
            # Fallback
            if not icon_path:
                for p in search_paths:
                     if os.path.exists(os.path.join(p, "default.xpm")):
                         icon_path = os.path.join(p, "default.xpm")
                         break

            img = None
            if icon_path:
                try:
                    img = tk.PhotoImage(file=icon_path)
                except Exception:
                    pass
            
            if img:
                self.icon_cache.append(img)
                # Apply style for wrapping
                btn = ttk.Button(self.scrollable_frame, text=name, image=img, 
                                 compound=compound_val,
                                 style=current_style,
                                 command=lambda e=data['exec']: self.run_selected_applet(e))
            else:
                btn = ttk.Button(self.scrollable_frame, text=name,
                                 style=current_style,
                                 command=lambda e=data['exec']: self.run_selected_applet(e))
                                 
            # Store button reference (don't grid yet)
            self.applet_buttons.append(btn)

        # Initial Layout
        self.update_idletasks() # Ensure widget exist
        self.reflow_icons(self.canvas.winfo_width())

    def reflow_icons(self, width):
        """Reflow buttons using fixed tile size and centered grid."""
        if not self.applet_buttons:
            return

        # Fixed Button Size Logic
        if self.view_mode == 'icon':
            btn_w = 120
            btn_h = 105
            max_cols = 10
        else:
            btn_w = 280
            btn_h = 60 # Increased for better spacing
            max_cols = 6
        
        # Calculate Packing
        item_w = btn_w + 2 # Width + Padding
        
        # How many fit?
        available_slots = (width - 4) // item_w
        if available_slots < 1: available_slots = 1
        
        # Apply Cap
        cols = min(available_slots, max_cols)
        
        # Left Align (no centering)
        start_x = 2
        
        current_x = start_x
        current_y = 2
        col_count = 0

        for btn in self.applet_buttons:
            btn.grid_forget()
            btn.place_forget()
            
            # Place button
            btn.place(x=current_x, y=current_y, width=btn_w, height=btn_h-4)
            
            # Advance
            current_x += item_w
            col_count += 1
            
            # Wrap
            if col_count >= cols:
                col_count = 0
                current_x = start_x
                current_y += btn_h
            
        # Update scrollable frame height
        # If we just wrapped, current_y is already pointing to next row, so we use it.
        # If we didn't just wrap, we need to account for the current row height.
        total_height = current_y + btn_h if col_count > 0 else current_y
        
        self.scrollable_frame.configure(width=width, height=total_height)
        self.canvas.configure(scrollregion=(0, 0, width, total_height))

    def run_selected_applet(self, exec_cmd):
        """Execute the applet command."""
        cmd = exec_cmd
        
        # Handle internal substitutions
        if "[PHROZEN-INTERNAL]" in cmd:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = cmd.replace("[PHROZEN-INTERNAL]", f"python3 {base_dir}/")
        
        cmd = cmd.replace("[EQUAL]", "=")
        
        # Check simple availability
        binary = cmd.split()[0]
        if binary == "python3":
             pass
        elif not shutil.which(binary) and not os.path.exists(binary):
            message("Error", f"Program not found:\n{binary}", pixmap=ICON_ERROR)
            return

        print(f"Executing: {cmd}")
        # Run in background
        subprocess.Popen(cmd, shell=True, start_new_session=True)

    def show_about(self):
        message("About", f"{WM_TITLE}\nVersion {APP_VERSION}\n\nRunning on Python {sys.version.split()[0]} / Tkinter", pixmap=ICON_INFO)

    def quit_app(self):
        self.destroy()
        sys.exit(0)

def run():
    app = ControlPanelApp()
    app.mainloop()

if __name__ == "__main__":
    run()

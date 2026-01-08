#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceMe - Message Boxes
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

import tkinter as tk
from tkinter import ttk
import sys
import os

# Retro-compatibility constants
ICON_STOP     = 4
ICON_ALERT    = 1
ICON_INFO     = 2
ICON_QUESTION = 3
ICON_ERROR    = 4

class CustomDialog(tk.Toplevel):
    """
    A custom dialog box that mimics the behavior of the legacy IceWMCP message box,
    supporting arbitrary button labels and icons.
    """
    def __init__(self, title="Message", message="", buttons=("Ok",), pixmap=ICON_INFO, parent=None):
        super().__init__(parent)
        self.withdraw()  # Hide initially to prevent flashing before centering
        
        self.result = None
        self.title(title)
        
        # Ensure it behaves like a dialog
        if parent:
            self.transient(parent)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- UI Construction ---
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill='both', expand=True)
        
        # Icon & Message Area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Icon handling
        icon_widget = None
        
        # 1. Handle Integer Constants
        if isinstance(pixmap, int):
            icon_name = "info" # default
            if pixmap == ICON_STOP or pixmap == ICON_ERROR:
                icon_name = "error"
            elif pixmap == ICON_ALERT:
                icon_name = "warning"
            elif pixmap == ICON_QUESTION:
                icon_name = "question"
            
            try:
                icon_widget = ttk.Label(content_frame, image=f"::tk::icons::{icon_name}")
            except tk.TclError:
                pass

        # 2. Handle Filenames (String)
        elif isinstance(pixmap, str) and os.path.exists(pixmap):
            try:
                # Keep a reference to the image to prevent garbage collection
                self.icon_image = tk.PhotoImage(file=pixmap) 
                icon_widget = ttk.Label(content_frame, image=self.icon_image)
            except Exception:
                pass

        if icon_widget:
            icon_widget.pack(side='left', anchor='n', padx=(0, 15))

        # Message Text
        if isinstance(message, list):
            display_text = "\n".join(message)
        else:
            display_text = str(message)
            
        msg_label = ttk.Label(content_frame, text=display_text, justify='left', wraplength=400)
        msg_label.pack(side='left', fill='both', expand=True)
        
        # Button Area
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        # Center buttons
        inner_btn_frame = ttk.Frame(button_frame)
        inner_btn_frame.pack(side='bottom', anchor='center')
        
        self.first_button = None
        
        for text in buttons:
            btn = ttk.Button(inner_btn_frame, text=text, command=lambda t=text: self.on_button(t))
            btn.pack(side='left', padx=5)
            if self.first_button is None:
                self.first_button = btn
                # Bind Enter key to the first button (default)
                self.bind('<Return>', lambda e, t=text: self.on_button(t))
        
        # Center the dialog relative to parent or screen
        self.update_idletasks()
        self.center_me(parent)
        self.deiconify()
        
        # Set focus and grab (modal)
        if self.first_button:
            self.first_button.focus_set()
        
        self.grab_set()

    def center_me(self, parent):
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        if parent and parent.winfo_viewable():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        else:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            
        self.geometry(f'+{x}+{y}')
        self.minsize(width, height)

    def on_button(self, value):
        self.result = value
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()

def message(title="Message", message="", buttons=("Ok",),
            pixmap=ICON_INFO, modal=True, stock_icons=[]):
    """
    Create a custom message box and return which button was pressed.
    
    Args:
        title (str): Window title.
        message (str or list): The message to display.
        buttons (tuple): List of button labels.
        pixmap (int key or str filename): Icon to display.
        modal (bool): Whether the dialog should be modal (default True).
        stock_icons (list): Ignored in this port, kept for compatibility.
        
    Returns:
        str: The text of the button clicked, or None if closed.
    """
    
    # Check for existing root
    root = tk._default_root
    created_root = False
    
    if root is None:
        root = tk.Tk()
        root.withdraw()
        created_root = True
        
    dlg = CustomDialog(title, message, buttons, pixmap, parent=root)
    
    # Wait for the window to be destroyed
    root.wait_window(dlg)
    
    ret = dlg.result
    
    if created_root:
        root.destroy()
        
    return ret

# Wrapper class for compatibility if anything specifically instantiated _MessageBox
class _MessageBox(CustomDialog):
    pass

if __name__ == "__main__":
    # Test cases similar to the original file
    print("Running functionality tests...")
    
    # Need a persistent root for multiple sequential dialogs if we want to mimic a full app run,
    # or just let message() create/destroy roots for each test.
    # Letting message() handle it to test standalone behavior.
    
    ret = message("Test MessageBox #1",
                  ["This is a test for the message box.", "", "Enjoy."], ('Ok',), ICON_INFO)
    print(f"Result 1: {ret}")

    ret = message("Test MessageBox #2", 
                  "This is a test with\ncustom buttons.",
                  ("Yes", "No", "Maybe"), ICON_QUESTION)
    print(f"Result 2: {ret}")

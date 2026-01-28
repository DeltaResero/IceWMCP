#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Menu Editor
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

"""
IceWM Menu Editor - A graphical editor for IceWM menu, programs, and toolbar files.

This module consolidates the legacy IceMe suite (IceMe.py, MenuParser.py,
IceMenuTree.py, PreviewWindow.py, Preferences.py, constants.py) into a single,
modern Tkinter application.
"""

import os
import sys
import string
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from .icewmcp_common import get_data_path
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path


# =============================================================================
# Constants (from legacy constants.py)
# =============================================================================

# Menu entry types
MENUTREE_PROG = 1
MENUTREE_RESTART = 2
MENUTREE_SUBMENU = 3
MENUTREE_SUBMENU_END = 4
MENUTREE_SEPARATOR = 5
MENUTREE_MENUFILE = 6
MENUTREE_UNKNOWN = 42

# Visual separator string
SEP_STRING = "------------------------"

# Icon patterns and types
ICON_PATTERNS = ["mini/*", "*"]
ICON_TYPES = ['xpm', 'png']

# User paths
HOME = os.path.expanduser("~")
HOME_ICEWM = os.path.join(HOME, ".icewm")

# System PATH for executable detection
PATH = os.environ.get("PATH", "").split(os.pathsep)

# Access constants
R_OK = os.R_OK
W_OK = os.W_OK
X_OK = os.X_OK
F_OK = os.F_OK


def getIceWMPrivConfigPath():
    """Returns the user's private IceWM config directory."""
    return HOME_ICEWM + os.sep


def getIceWMConfigPath():
    """Returns the system IceWM config directory."""
    for path in ["/etc/icewm/", "/usr/share/icewm/", "/usr/local/share/icewm/"]:
        if os.path.isdir(path):
            return path
    return "/etc/icewm/"


# =============================================================================
# MenuParser (from legacy menu_parser.py)
# =============================================================================

class MenuParser:
    """Parses IceWM menu files (menu, programs, toolbar)."""

    def __init__(self, filename):
        self.lines = []
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                self.lines = f.readlines()
        except Exception:
            pass

    def _get_next_line(self):
        """Returns the next non-empty, non-comment line."""
        while self.lines:
            line = self.lines.pop(0).strip()
            if line and not line.startswith('#'):
                return line
        return None

    def get_next_entry(self):
        """
        Parses the next menu entry.
        Returns: [type, name, icon, command] or None if EOF.
        """
        line = self._get_next_line()
        if line is None:
            return None

        parts = line.split(None, 1)
        tag = parts[0].lower() if parts else ""

        if tag == "separator":
            return [MENUTREE_SEPARATOR, None, None, None]
        elif tag == "prog":
            return [MENUTREE_PROG] + self._parse_prog(line[5:])
        elif tag == "menuprog":
            # Embedded menus like Gnome integration
            return [MENUTREE_PROG] + self._parse_prog(line[9:])
        elif tag == "includeprog":
            # includeprog entries are dynamic program generators (treat as prog)
            return [MENUTREE_PROG] + self._parse_prog(line[12:])
        elif tag == "restart":
            return [MENUTREE_RESTART] + self._parse_prog(line[8:])
        elif tag == "menu":
            return [MENUTREE_SUBMENU] + self._parse_menu(line[5:])
        elif tag == "menufile":
            # menufile references are handled externally, skip in parsing
            return [MENUTREE_MENUFILE, None, None, None]
        elif tag == "}":
            return [MENUTREE_SUBMENU_END, None, None, None]
        else:
            return [MENUTREE_UNKNOWN, None, None, None]

    def _parse_word(self, s, start=0):
        """Extracts a quoted or unquoted word from a string."""
        in_quotes = False
        at_start = True
        word = ""
        i = start

        while i < len(s):
            c = s[i]
            i += 1
            if c in string.whitespace:
                if in_quotes:
                    word += c
                elif at_start:
                    pass
                else:
                    return (word, i)
            elif c == '"':
                in_quotes = not in_quotes
                at_start = False
            else:
                word += c
                at_start = False
        return (word, i)

    def _parse_prog(self, s):
        """Parses: prog "Name" icon command"""
        name, pos = self._parse_word(s)
        icon, pos = self._parse_word(s, pos)
        command = s[pos:].strip()
        return [name, icon, command]

    def _parse_menu(self, s):
        """Parses: menu "Name" icon {"""
        name, pos = self._parse_word(s)
        icon, pos = self._parse_word(s, pos)
        return [name, icon, None]


# =============================================================================
# MenuWriter
# =============================================================================

class MenuWriter:
    """Writes IceWM menu files from a tree structure."""

    def __init__(self, tree_data, filename):
        self.tree_data = tree_data
        self.filename = filename

    def write(self):
        """Writes the menu data to file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                self._write_entries(f, self.tree_data, 0)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")
            return False

    def _write_entries(self, f, entries, level):
        """Recursively writes menu entries."""
        indent = "    " * level
        for entry in entries:
            entry_type = entry.get('type', MENUTREE_UNKNOWN)

            if entry_type == MENUTREE_SEPARATOR:
                f.write(f"{indent}separator\n")
            elif entry_type == MENUTREE_PROG:
                name = entry.get('name', '')
                icon = entry.get('icon', '-')
                cmd = entry.get('command', '')
                f.write(f'{indent}prog "{name}" {icon or "-"} {cmd}\n')
            elif entry_type == MENUTREE_RESTART:
                name = entry.get('name', '')
                icon = entry.get('icon', '-')
                cmd = entry.get('command', '')
                f.write(f'{indent}restart "{name}" {icon or "-"} {cmd}\n')
            elif entry_type == MENUTREE_SUBMENU:
                name = entry.get('name', '')
                icon = entry.get('icon', '-')
                f.write(f'{indent}menu "{name}" {icon or "-"} {{\n')
                children = entry.get('children', [])
                self._write_entries(f, children, level + 1)
                f.write(f"{indent}}}\n")


# =============================================================================
# MenuEditorApp
# =============================================================================

class MenuEditorApp:
    """Main Menu Editor application."""

    VERSION = "3.3"

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Menu Editor")
        self.root.withdraw()  # Hide during setup

        # Data storage
        self.menu_data = []  # Tree data for main menu
        self.programs_data = []  # Tree data for programs
        self.toolbar_data = []  # Tree data for toolbar
        self.clipboard = None  # For cut/copy/paste
        self.modified = False
        self.icon_cache = {}  # PhotoImage cache

        # File paths (always user dir)
        self.menu_file = os.path.join(HOME_ICEWM, "menu")
        self.programs_file = os.path.join(HOME_ICEWM, "programs")
        self.toolbar_file = os.path.join(HOME_ICEWM, "toolbar")
        
        # Ensure ~/.icewm exists for saving
        os.makedirs(HOME_ICEWM, exist_ok=True)

        # Build UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_ui()
        self._create_statusbar()

        # Load data
        self._load_files()

        # Center and show
        self._center_window(800, 600)
        self.root.deiconify()

        # Keyboard bindings
        self.root.bind('<Control-s>', lambda e: self._on_save())
        self.root.bind('<Control-q>', lambda e: self._on_exit())
        self.root.bind('<Delete>', lambda e: self._on_delete())

    def _center_window(self, w, h):
        """Centers the window on screen."""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _create_menu(self):
        """Creates the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self._on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Revert", command=self._on_revert)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self._on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._on_paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete", command=self._on_delete, accelerator="Del")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self._on_about)

    def _create_toolbar(self):
        """Creates the toolbar."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side='top', fill='x', padx=2, pady=2)

        # Button definitions: (text, command)
        buttons = [
            ("Save", self._on_save),
            ("Revert", self._on_revert),
            ("|", None),
            ("+ Entry", self._on_new_entry),
            ("+ Sep", self._on_new_separator),
            ("+ Menu", self._on_new_submenu),
            ("|", None),
            ("Cut", self._on_cut),
            ("Copy", self._on_copy),
            ("Paste", self._on_paste),
            ("Delete", self._on_delete),
            ("|", None),
            ("↑", self._on_move_up),
            ("↓", self._on_move_down),
        ]

        for text, cmd in buttons:
            if text == "|":
                ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5, pady=2)
            else:
                btn = ttk.Button(toolbar, text=text, command=cmd, width=8)
                btn.pack(side='left', padx=1)

    def _create_main_ui(self):
        """Creates the main UI with tree and edit panel."""
        # Main paned window
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        # Left side: Treeview
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        self.tree = ttk.Treeview(left_frame, columns=('Command',), selectmode='browse')
        self.tree.heading('#0', text='Menu', anchor='w')
        self.tree.heading('Command', text='Command', anchor='w')
        self.tree.column('#0', width=200)
        self.tree.column('Command', width=200)

        tree_scroll = ttk.Scrollbar(left_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        # Right side: Edit panel
        right_frame = ttk.LabelFrame(paned, text="Menu Entry", padding=10)
        paned.add(right_frame, weight=0)

        # Name
        ttk.Label(right_frame, text="Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(right_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)
        self.name_var.trace_add('write', self._on_field_change)

        # Command
        ttk.Label(right_frame, text="Command:").grid(row=1, column=0, sticky='e', pady=5)
        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(right_frame, textvariable=self.cmd_var, width=30)
        self.cmd_entry.grid(row=1, column=1, sticky='ew', pady=5)
        self.cmd_var.trace_add('write', self._on_field_change)
        ttk.Button(right_frame, text="...", width=3, command=self._browse_command).grid(row=1, column=2, pady=5)

        # Icon
        ttk.Label(right_frame, text="Icon:").grid(row=2, column=0, sticky='e', pady=5)
        self.icon_var = tk.StringVar()
        self.icon_entry = ttk.Entry(right_frame, textvariable=self.icon_var, width=30)
        self.icon_entry.grid(row=2, column=1, sticky='ew', pady=5)
        self.icon_var.trace_add('write', self._on_field_change)
        ttk.Button(right_frame, text="...", width=3, command=self._browse_icon).grid(row=2, column=2, pady=5)

        # Restart checkbox
        self.restart_var = tk.BooleanVar()
        self.restart_check = ttk.Checkbutton(
            right_frame, text="Start as new window manager",
            variable=self.restart_var, command=self._on_restart_toggle
        )
        self.restart_check.grid(row=3, column=0, columnspan=3, sticky='w', pady=10)

        right_frame.columnconfigure(1, weight=1)

    def _create_statusbar(self):
        """Creates the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        status.pack(side='bottom', fill='x')

    def _set_status(self, msg):
        """Updates the status bar message."""
        self.status_var.set(msg)

    # =========================================================================
    # File Operations
    # =========================================================================

    def _check_and_copy_system_files(self):
        """Checks for missing user config files and offers to copy system defaults."""
        files_to_check = ["menu", "programs", "toolbar"]
        missing_system_files = []  # List of (name, sys_path, user_path)

        for name in files_to_check:
            user_path = os.path.join(HOME_ICEWM, name)
            if os.path.exists(user_path):
                continue
            
            # Check system paths
            found_sys = None
            for sys_dir in ["/etc/icewm", "/usr/share/icewm", "/usr/local/share/icewm"]:
                sys_path = os.path.join(sys_dir, name)
                if os.path.exists(sys_path):
                    found_sys = sys_path
                    break
            
            if found_sys:
                missing_system_files.append((name, found_sys, user_path))

        if not missing_system_files:
            return

        # Build prompt message
        msg = "The following user IceWM menu configuration files were not found:\n\n"
        for name, src, _ in missing_system_files:
             msg += f"• {name}\n"
        
        msg += "\nSystem defaults were found at:\n"
        unique_paths = list(set([os.path.dirname(src) for _, src, _ in missing_system_files]))
        for p in unique_paths:
            msg += f"{p}\n"

        msg += "\nWould you like to copy these system defaults to your user IceWM configuration folder to begin editing?"

        if messagebox.askyesno("IceWM Menu Setup", msg):
            import shutil
            copied_count = 0
            for name, src, dst in missing_system_files:
                try:
                    shutil.copy2(src, dst)
                    copied_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy {name}:\n{e}")
            
            if copied_count > 0:
                self._set_status(f"Copied {copied_count} system files to user configuration.")

    def _load_files(self):
        """Loads menu, programs, and toolbar files into the tree."""
        self.tree.delete(*self.tree.get_children())
        self._item_data = {}  # Reset item data

        # Check for initial setup (offer to copy system files)
        self._check_and_copy_system_files()

        # Set paths (always user dir)
        self.menu_file = os.path.join(HOME_ICEWM, "menu")
        self.programs_file = os.path.join(HOME_ICEWM, "programs")
        self.toolbar_file = os.path.join(HOME_ICEWM, "toolbar")

        # Main Menu
        self.menu_root = self.tree.insert('', 'end', text="Main Menu", open=True, tags=('root',))
        self._set_item_data(self.menu_root, MENUTREE_MENUFILE, "Main Menu", "", "")
        # Only load if file exists in user dir
        loaded_menu = 0
        if os.path.exists(self.menu_file):
            loaded_menu = self._load_file_into_tree(self.menu_file, self.menu_root)

        # Programs
        self.programs_root = self.tree.insert('', 'end', text="Programs", open=True, tags=('root',))
        self._set_item_data(self.programs_root, MENUTREE_MENUFILE, "Programs", "", "")
        loaded_programs = 0
        if os.path.exists(self.programs_file):
             loaded_programs = self._load_file_into_tree(self.programs_file, self.programs_root)

        # Toolbar
        self.toolbar_root = self.tree.insert('', 'end', text="Toolbar", open=True, tags=('root',))
        self._set_item_data(self.toolbar_root, MENUTREE_MENUFILE, "Toolbar", "", "")
        loaded_toolbar = 0
        if os.path.exists(self.toolbar_file):
            loaded_toolbar = self._load_file_into_tree(self.toolbar_file, self.toolbar_root)

        # Report status
        count = loaded_menu + loaded_programs + loaded_toolbar
        if count > 0:
            self._set_status(f"Loaded {count} menu entries.")
        else:
            self._set_status("No user menu files found (empty session).")

        self.modified = False

    def _load_file_into_tree(self, filepath, parent_node):
        """Parses a file and inserts entries into the treeview. Returns count of entries loaded."""
        if not filepath or not os.path.exists(filepath):
            return 0

        parser = MenuParser(filepath)
        return self._insert_entries_from_parser(parser, parent_node)

    def _insert_entries_from_parser(self, parser, parent_node):
        """Recursively inserts menu entries from parser into tree. Returns count."""
        count = 0
        while True:
            entry = parser.get_next_entry()
            if entry is None:
                break

            entry_type, name, icon, command = entry

            if entry_type == MENUTREE_SUBMENU_END:
                break
            elif entry_type == MENUTREE_SEPARATOR:
                node = self.tree.insert(parent_node, 'end', text=SEP_STRING, values=('',),
                                 tags=('separator',))
                self._set_item_data(node, entry_type, None, None, None)
                count += 1
            elif entry_type == MENUTREE_SUBMENU:
                submenu_node = self.tree.insert(parent_node, 'end', text=f"▶ {name}",
                                                 values=('',), tags=('submenu',))
                self.tree.set(submenu_node, 'Command', '')
                self.tree.item(submenu_node, open=True)
                # Store metadata
                self._set_item_data(submenu_node, entry_type, name, icon, '')
                # Recurse
                count += 1 + self._insert_entries_from_parser(parser, submenu_node)
            elif entry_type in (MENUTREE_PROG, MENUTREE_RESTART):
                node = self.tree.insert(parent_node, 'end', text=name or "(unnamed)",
                                        values=(command or '',), tags=('prog',))
                self._set_item_data(node, entry_type, name, icon, command)
                count += 1
            # Ignore MENUTREE_UNKNOWN
        return count

    def _set_item_data(self, item, entry_type, name, icon, command):
        """Stores metadata on a tree item using tags."""
        # We'll use a simple approach: store as custom properties
        # Treeview doesn't have built-in data storage, so we use a dict
        if not hasattr(self, '_item_data'):
            self._item_data = {}
        self._item_data[item] = {
            'type': entry_type,
            'name': name or '',
            'icon': icon or '',
            'command': command or ''
        }

    def _get_item_data(self, item):
        """Retrieves metadata for a tree item."""
        if not hasattr(self, '_item_data'):
            self._item_data = {}
        return self._item_data.get(item, {'type': MENUTREE_UNKNOWN, 'name': '', 'icon': '', 'command': ''})

    def _on_save(self):
        """Saves all menu files."""
        success = True
        
        # Save each root section
        if hasattr(self, 'menu_root'):
            menu_path = os.path.join(HOME_ICEWM, "menu")
            if not self._save_tree_to_file(self.menu_root, menu_path):
                success = False
        
        if hasattr(self, 'programs_root'):
            programs_path = os.path.join(HOME_ICEWM, "programs")
            if not self._save_tree_to_file(self.programs_root, programs_path):
                success = False
        
        if hasattr(self, 'toolbar_root'):
            toolbar_path = os.path.join(HOME_ICEWM, "toolbar")
            if not self._save_tree_to_file(self.toolbar_root, toolbar_path):
                success = False
        
        if success:
            self.modified = False
            self._set_status("Files saved successfully.")
            messagebox.showinfo("Saved", f"Menu files saved to:\n{HOME_ICEWM}")
        else:
            self._set_status("Error saving files.")

    def _save_tree_to_file(self, root_item, filepath):
        """Saves a tree branch to a menu file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# IceWM Menu File\n")
                f.write("# Generated by IceWM Control Panel Menu Editor\n\n")
                self._write_tree_entries(f, root_item, 0)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save {filepath}:\n{e}")
            return False

    def _write_tree_entries(self, f, parent, level):
        """Recursively writes tree entries to file."""
        indent = "    " * level
        
        for item in self.tree.get_children(parent):
            data = self._get_item_data(item)
            entry_type = data.get('type', MENUTREE_UNKNOWN)
            name = data.get('name', '')
            icon = data.get('icon', '') or '-'
            command = data.get('command', '')
            
            if entry_type == MENUTREE_SEPARATOR:
                f.write(f"{indent}separator\n")
            elif entry_type == MENUTREE_PROG:
                f.write(f'{indent}prog "{name}" {icon} {command}\n')
            elif entry_type == MENUTREE_RESTART:
                f.write(f'{indent}restart "{name}" {icon} {command}\n')
            elif entry_type == MENUTREE_SUBMENU:
                f.write(f'{indent}menu "{name}" {icon} {{\n')
                self._write_tree_entries(f, item, level + 1)
                f.write(f"{indent}}}\n")

    def _on_revert(self):
        """Reverts to last saved version."""
        if messagebox.askyesno("Revert", "Discard all changes and reload from disk?"):
            self._load_files()

    # =========================================================================
    # Tree Selection
    # =========================================================================

    def _on_tree_select(self, event):
        """Handles tree selection change."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        data = self._get_item_data(item)

        # Populate edit panel
        self.name_var.set(data.get('name', ''))
        self.cmd_var.set(data.get('command', ''))
        self.icon_var.set(data.get('icon', ''))
        self.restart_var.set(data.get('type') == MENUTREE_RESTART)

    def _on_field_change(self, *args):
        """Called when any edit field changes."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        data = self._get_item_data(item)

        # Update data
        data['name'] = self.name_var.get()
        data['command'] = self.cmd_var.get()
        data['icon'] = self.icon_var.get()

        # Update tree display
        if 'separator' not in self.tree.item(item, 'tags'):
            display_name = data['name'] or "(unnamed)"
            if 'submenu' in self.tree.item(item, 'tags'):
                display_name = f"▶ {display_name}"
            self.tree.item(item, text=display_name)
            self.tree.set(item, 'Command', data['command'])

        self.modified = True

    def _on_restart_toggle(self):
        """Handles restart checkbox toggle."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        data = self._get_item_data(item)
        data['type'] = MENUTREE_RESTART if self.restart_var.get() else MENUTREE_PROG
        self.modified = True

    # =========================================================================
    # Edit Operations
    # =========================================================================

    def _on_new_entry(self):
        """Adds a new program entry."""
        self._add_entry(MENUTREE_PROG, "New Entry", "", "")

    def _on_new_separator(self):
        """Adds a new separator."""
        self._add_entry(MENUTREE_SEPARATOR, None, None, None)

    def _on_new_submenu(self):
        """Adds a new submenu."""
        self._add_entry(MENUTREE_SUBMENU, "New Menu", "", None)

    def _add_entry(self, entry_type, name, icon, command):
        """Adds a new entry to the tree."""
        selection = self.tree.selection()
        parent = selection[0] if selection else ''

        # If selected item is not a submenu or root, use its parent
        if parent:
            tags = self.tree.item(parent, 'tags')
            if 'submenu' not in tags and 'root' not in tags:
                parent = self.tree.parent(parent)

        if entry_type == MENUTREE_SEPARATOR:
            node = self.tree.insert(parent, 'end', text=SEP_STRING, values=('',), tags=('separator',))
        elif entry_type == MENUTREE_SUBMENU:
            node = self.tree.insert(parent, 'end', text=f"▶ {name}", values=('',), tags=('submenu',))
        else:
            node = self.tree.insert(parent, 'end', text=name, values=(command or '',), tags=('prog',))

        self._set_item_data(node, entry_type, name, icon, command)
        self.tree.selection_set(node)
        self.tree.see(node)
        self.modified = True

    def _on_cut(self):
        """Cuts the selected item."""
        self._on_copy()
        self._on_delete()

    def _on_copy(self):
        """Copies the selected item to clipboard."""
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        self.clipboard = self._get_item_data(item).copy()
        self._set_status("Copied to clipboard.")

    def _on_paste(self):
        """Pastes from clipboard."""
        if not self.clipboard:
            return
        self._add_entry(
            self.clipboard.get('type', MENUTREE_PROG),
            self.clipboard.get('name', ''),
            self.clipboard.get('icon', ''),
            self.clipboard.get('command', '')
        )
        self._set_status("Pasted from clipboard.")

    def _on_delete(self):
        """Deletes the selected item."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')

        # Don't delete root nodes
        if 'root' in tags:
            messagebox.showwarning("Warning", "Cannot delete root menu nodes.")
            return

        self.tree.delete(item)
        if hasattr(self, '_item_data') and item in self._item_data:
            del self._item_data[item]
        self.modified = True

    def _on_move_up(self):
        """Moves the selected item up."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        parent = self.tree.parent(item)
        index = self.tree.index(item)

        if index > 0:
            self.tree.move(item, parent, index - 1)
            self.modified = True

    def _on_move_down(self):
        """Moves the selected item down."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        parent = self.tree.parent(item)
        siblings = self.tree.get_children(parent)
        index = self.tree.index(item)

        if index < len(siblings) - 1:
            self.tree.move(item, parent, index + 1)
            self.modified = True

    # =========================================================================
    # Browsing
    # =========================================================================

    def _browse_command(self):
        """Opens a file dialog to select a command executable."""
        filepath = filedialog.askopenfilename(
            title="Select Executable",
            initialdir="/usr/bin"
        )
        if filepath:
            self.cmd_var.set(filepath)

    def _browse_icon(self):
        """Opens the icon selection dialog."""
        try:
            from . import icewmcp_gtk_icon_selection as icon_sel
            # Create a callback to receive the selected icon
            def on_icon_selected(path):
                self.icon_var.set(path)

            # Show the dialog
            icon_sel.show_dlg(updater=on_icon_selected)
        except Exception as e:
            # Fallback to file dialog
            filepath = filedialog.askopenfilename(
                title="Select Icon",
                filetypes=[("Images", "*.png *.xpm"), ("All Files", "*.*")]
            )
            if filepath:
                self.icon_var.set(filepath)



    # =========================================================================
    # Other Actions
    # =========================================================================

    def _on_exit(self):
        """Exits the application."""
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Exit anyway?"):
                return
        self.root.destroy()

    def _on_about(self):
        """Shows the About dialog."""
        about_text = f"""IceWM CP - Menu Editor
Version {self.VERSION}

A graphical editor for IceWM menu files.

Original Authors:
• Dirk Moebius & Mike Hostetler (2000-2002)
• David Moore (2003) - PyGTK-2 Port
• Erica Andrews (2003-2004) - Modifications

Tkinter Port:
• DeltaResero (2026)

Licensed under GPL-2.0-or-later"""
        messagebox.showinfo("About", about_text)


# =============================================================================
# Main Entry Point
# =============================================================================

def run():
    """Entry point for the Menu Editor."""
    root = tk.Tk()
    app = MenuEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()

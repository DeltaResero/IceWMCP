#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Keyboard Shortcuts: Manages custom user-defined keyboard shortcuts.
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
import shlex
import subprocess

try:
    from .icewmcp_common import get_data_path
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import get_data_path


class KeyShortcutsApp:
    """A Tkinter app for editing IceWM's custom keyboard shortcut 'keys' file."""

    def __init__(self, root):
        self.root = root
        self.root.title("IceWM CP - Keyboard Shortcuts")

        self.keys_file = os.path.join(os.environ.get('HOME', ''), '.icewm', 'keys')
        self.keys_data = {}
        self.selected_key_id = None

        self.alt_var = tk.BooleanVar()
        self.ctrl_var = tk.BooleanVar()
        self.shift_var = tk.BooleanVar()
        self.key_var = tk.StringVar()
        self.command_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1) # Allow treeview to expand

        # --- Warning Label (Context-Aware) ---
        self.warning_label = ttk.Label(
            main_frame,
            text="Warning: Not in an IceWM session. Changes will not apply to the current desktop.",
            background="yellow", foreground="black", padding=5, anchor='center',
            font=("-weight", "bold")
        )
        # This will be shown or hidden by _check_environment

        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('keys', 'command'), show='headings', selectmode='browse')
        self.tree.heading('keys', text='Keys')
        self.tree.heading('command', text='Command')
        self.tree.column('keys', width=150)
        self.tree.column('command', width=350)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        entry_frame = ttk.Labelframe(main_frame, text="Shortcut Details", padding=10)
        entry_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        entry_frame.columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Key:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        key_fields_frame = ttk.Frame(entry_frame)
        key_fields_frame.grid(row=0, column=1, sticky='ew')

        ttk.Checkbutton(key_fields_frame, text="Ctrl", variable=self.ctrl_var).pack(side='left', padx=2)
        ttk.Checkbutton(key_fields_frame, text="Alt", variable=self.alt_var).pack(side='left', padx=2)
        ttk.Checkbutton(key_fields_frame, text="Shift", variable=self.shift_var).pack(side='left', padx=2)
        self.key_entry = ttk.Entry(key_fields_frame, textvariable=self.key_var)
        self.key_entry.pack(side='left', fill='x', expand=True, padx=5)

        ttk.Label(entry_frame, text="Command:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        cmd_frame = ttk.Frame(entry_frame)
        cmd_frame.grid(row=1, column=1, sticky='ew')
        cmd_frame.columnconfigure(0, weight=1)
        self.command_entry = ttk.Entry(cmd_frame, textvariable=self.command_var)
        self.command_entry.grid(row=0, column=0, sticky='ew')
        browse_btn = ttk.Button(cmd_frame, text="...", width=3, command=self.browse_for_command)
        browse_btn.grid(row=0, column=1, padx=5)

        button_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        button_frame.grid(row=3, column=0, columnspan=2, sticky='ew')

        self.new_btn = ttk.Button(button_frame, text="New", command=self.clear_selection)
        self.add_btn = ttk.Button(button_frame, text="Add", command=self.add_key)
        self.update_btn = ttk.Button(button_frame, text="Update", command=self.update_key)
        self.delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_key)
        self.test_btn = ttk.Button(button_frame, text="Test", command=self.test_command)
        for btn in [self.new_btn, self.add_btn, self.update_btn, self.delete_btn, self.test_btn]:
            btn.pack(side='left', expand=True, fill='x', padx=2)

        action_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        action_frame.grid(row=4, column=0, columnspan=2, sticky='ew')

        self.save_button = ttk.Button(action_frame, text="Save to File", command=self.save_file)
        self.restart_button = ttk.Button(action_frame, text="Restart IceWM", command=self.restart_icewm)
        self.close_button = ttk.Button(action_frame, text="Close", command=self.root.destroy)
        for btn in [self.save_button, self.restart_button, self.close_button]:
            btn.pack(side='left', expand=True, fill='x', padx=2)

        ttk.Label(main_frame, textvariable=self.status_var, relief='sunken').grid(row=5, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        self.load_file()
        self.update_ui_state()
        self.center_window()
        self._check_environment()

    def _check_environment(self):
        """Check for IceWM session and adapt UI for safety."""
        session = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if "icewm" not in session:
            self.warning_label.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
            self.restart_button.config(state='disabled')

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')

    def build_key_string(self):
        parts = []
        if self.ctrl_var.get(): parts.append("Ctrl")
        if self.alt_var.get(): parts.append("Alt")
        if self.shift_var.get(): parts.append("Shift")
        key_part = self.key_var.get().strip()
        if key_part: parts.append(key_part)
        return "+".join(parts)

    def parse_key_string(self, key_str):
        parts = set(key_str.split('+'))
        self.ctrl_var.set("Ctrl" in parts)
        self.alt_var.set("Alt" in parts)
        self.shift_var.set("Shift" in parts)

        non_modifier_keys = [p for p in parts if p not in {"Ctrl", "Alt", "Shift"}]
        self.key_var.set("+".join(non_modifier_keys))

    def on_item_select(self, event):
        selection = self.tree.selection()
        if not selection: return
        self.selected_key_id = selection[0]
        key_str, command = self.tree.item(self.selected_key_id, 'values')
        self.parse_key_string(key_str)
        self.command_var.set(command)
        self.update_ui_state()

    def clear_selection(self):
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])
        self.selected_key_id = None
        for var in [self.alt_var, self.ctrl_var, self.shift_var]: var.set(False)
        for var in [self.key_var, self.command_var]: var.set("")
        self.key_entry.focus()
        self.update_ui_state()

    def update_ui_state(self):
        is_item_selected = bool(self.selected_key_id)
        self.add_btn.config(state='disabled' if is_item_selected else 'normal')
        self.update_btn.config(state='normal' if is_item_selected else 'disabled')
        self.delete_btn.config(state='normal' if is_item_selected else 'disabled')
        self.test_btn.config(state='normal' if is_item_selected else 'disabled')

        is_editable = not is_item_selected
        self.key_entry.config(state='normal' if is_editable else 'disabled')
        for cb in self.key_entry.master.winfo_children():
            if isinstance(cb, ttk.Checkbutton):
                cb.config(state='normal' if is_editable else 'disabled')

    def refresh_treeview(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for key_str in sorted(self.keys_data.keys()):
            self.tree.insert('', 'end', values=(key_str, self.keys_data[key_str]))

    def load_file(self):
        self.keys_data = {}
        if not os.path.exists(self.keys_file):
            self.status_var.set("File not found. Will be created on save.")
            return
        try:
            with open(self.keys_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line.startswith("key"): continue
                    parts = shlex.split(line)
                    if len(parts) >= 3:
                        self.keys_data[parts[1]] = " ".join(parts[2:])
            self.refresh_treeview()
            self.status_var.set("Keys file loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read keys file:\n{e}")

    def save_file(self):
        if not self.keys_data: return
        if os.path.exists(self.keys_file) and not messagebox.askyesno("Confirm Save", f"Overwrite {self.keys_file}?"): return
        try:
            os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
            with open(self.keys_file, 'w') as f:
                f.write("# IceWM custom keyboard shortcuts\n# Generated by IceWMCP\n\n")
                for key_str in sorted(self.keys_data.keys()):
                    f.write(f'key "{key_str}"\t\t{self.keys_data[key_str]}\n')
            self.status_var.set("File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save keys file:\n{e}")

    def add_key(self):
        key_str = self.build_key_string()
        command = self.command_var.get().strip()
        if not key_str or not command:
            messagebox.showwarning("Missing Information", "Both a key and a command must be specified.")
            return
        if key_str in self.keys_data:
            messagebox.showwarning("Duplicate Key", f"The key '{key_str}' already exists.")
            return
        self.keys_data[key_str] = command
        self.refresh_treeview()
        self.clear_selection()
        self.status_var.set(f"Added key: {key_str}")

    def update_key(self):
        if not self.selected_key_id: return
        key_str, _ = self.tree.item(self.selected_key_id, 'values')
        new_command = self.command_var.get().strip()
        if not new_command:
            messagebox.showwarning("Missing Information", "Command cannot be empty.")
            return
        self.keys_data[key_str] = new_command
        self.refresh_treeview()
        self.status_var.set(f"Updated key: {key_str}")

    def delete_key(self):
        if not self.selected_key_id: return
        key_str, _ = self.tree.item(self.selected_key_id, 'values')
        if messagebox.askyesno("Confirm Delete", f"Delete the shortcut for '{key_str}'?"):
            del self.keys_data[key_str]
            self.refresh_treeview()
            self.clear_selection()
            self.status_var.set(f"Deleted key: {key_str}")

    def test_command(self):
        command = self.command_var.get().strip()
        if not command: return
        try:
            subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run command:\n{e}")

    def browse_for_command(self):
        path = filedialog.askopenfilename(title="Select a Command")
        if path: self.command_var.set(path)

    def restart_icewm(self):
        if messagebox.askyesno("Confirm Restart", "This will save your changes and then attempt to restart IceWM to apply them.\n\nContinue?"):
            self.save_file()
            try:
                subprocess.run(['killall', '-HUP', 'icewm'], check=True)
                self.status_var.set("IceWM restart signal sent.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send restart signal:\n{e}")

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = KeyShortcutsApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")

# EOF

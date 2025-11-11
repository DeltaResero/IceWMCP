#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  PhrozenClock: A utility to manage the system date, time, and timezone.
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
from tkcalendar import Calendar
import time
import os
import sys
import subprocess
import shlex

try:
    from .icewmcp_common import *
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from icewmcp.icewmcp_common import *


class ClockApp:
    """A Tkinter application for managing system time, date, and timezone."""
    def __init__(self, root):
        self.root = root
        self.root.title("Phrozen Clock")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Withdraw the window so it is not visible during the setup process.
        self.root.withdraw()

        # Set application icon
        try:
            icon_path = get_data_path('icons/icewmcp-phrozenclock.png')
            if os.path.exists(icon_path):
                phrozen_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, phrozen_icon)
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}", file=sys.stderr)

        self.is_relaunch = False
        for arg in sys.argv[1:]:
            if '+' in arg and 'x' in arg:
                self.root.geometry(arg); self.is_relaunch = True; break

        # --- Core application logic setup ---
        self.ZONE_DIRS = ['/usr/share/zoneinfo/', '/usr/lib/zoneinfo/', '/usr/share/lib/zoneinfo/', '/usr/local/share/zoneinfo/', '/usr/local/share/lib/zoneinfo/', '/etc/zoneinfo/']
        if 'TZDIR' in os.environ and os.environ['TZDIR'].strip(): self.ZONE_DIRS.insert(0, os.environ['TZDIR'].strip() + "/")
        self.LOCALTIME_FILES = ['/etc/localtime'] + [os.path.join(d, "localtime") for d in self.ZONE_DIRS]
        self.TIMEZONE_FILES = ['/etc/timezone']; self.IGNORE_EXT = ['*.ics', '*.ICS']
        self.ZONEINFO_DIR = '/usr/share/zoneinfo/'; self.TIME_ZONE_INFO_FILE = '/etc/localtime'
        self.TIME_ZONE_DESC_FILE = '/etc/timezone'; self.TZ_DICT = {}
        if self.locateZoneinfo() == -1: sys.exit(1)
        self.locateLocaltimeFile(); self.locateTimezoneFile(); self.loadTimeZones()

        # --- UI Construction ---
        self._create_menu()
        main_frame = ttk.Frame(self.root, padding="5"); main_frame.pack(expand=True, fill='both')
        self.notebook = ttk.Notebook(main_frame); self.notebook.pack(expand=True, fill='both')
        self.tab1 = ttk.Frame(self.notebook, padding="10"); self.tab2 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab1, text='Date & Time'); self.notebook.add(self.tab2, text='Time Zone')
        self.ntp_var = tk.BooleanVar(); self.initial_ntp_state = False
        self.create_tab1_widgets(); self.create_tab2_widgets()
        self.set_initial_values(); self.update_clock()

        if not self.is_relaunch: self.center_window()

        # Now that setup is complete and the window is centered, make it visible.
        self.root.deiconify()

    def center_window(self):
        """Calculates and sets the window geometry to center it on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.minsize(width, height)


    def _create_menu(self):
        """Creates the main application menu bar."""
        self.menubar = tk.Menu(self.root); self.root.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator(); file_menu.add_command(label="Exit", command=self.root.destroy)
        help_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.do_about)

    def update_clock(self):
        """Periodically updates the time display label."""
        try:
            tz_abbr = subprocess.check_output(["date", "+%Z"], text=True).strip()
            time_str = time.strftime(f'%I:%M:%S %p'); self.time_label.config(text=f"{time_str} {tz_abbr}")
        except Exception: self.time_label.config(text=time.strftime('%I:%M:%S %p %Z'))
        self.root.after(1000, self.update_clock)

    def set_initial_values(self):
        """Populates all UI widgets with the current system state."""
        self.calendar.selection_set(time.strftime('%Y-%m-%d')); self.hour_combo.set(time.strftime('%I'))
        self.minute_combo.set(time.strftime('%M')); self.second_combo.set(time.strftime('%S')); self.ampm_combo.set(time.strftime('%p'))
        tz_names = sorted(self.TZ_DICT.keys()); self.timezone_combo['values'] = tz_names
        current_tz_name = self.getCurrentTZName()
        if current_tz_name in tz_names: self.timezone_combo.set(current_tz_name)
        try:
            tz_abbr = subprocess.check_output(["date", "+%Z"], text=True).strip()
            self.current_tz_entry.config(state='normal'); self.current_tz_entry.delete(0, 'end')
            self.current_tz_entry.insert(0, tz_abbr); self.current_tz_entry.config(state='readonly')
        except Exception as e: print(f"Could not get timezone abbreviation: {e}")
        try:
            # Suppress stderr to prevent the RTC local time zone warning on dual-boot systems.
            status_output = subprocess.check_output(
                ["timedatectl", "status"], text=True, stderr=subprocess.DEVNULL
            )
            self.initial_ntp_state = "NTP service: active" in status_output; self.ntp_var.set(self.initial_ntp_state)
        except (FileNotFoundError, subprocess.CalledProcessError): self.initial_ntp_state = False; self.ntp_var.set(False)
        self.update_widget_states()

    def update_widget_states(self):
        """Enables or disables widgets based on the NTP checkbox state."""
        state = 'disabled' if self.ntp_var.get() else 'normal'
        for widget in [self.calendar, self.hour_combo, self.minute_combo, self.second_combo, self.ampm_combo]:
            widget.config(state=state)

    def create_tab1_widgets(self):
        """Creates and places all widgets for the 'Date & Time' tab."""
        top_frame = ttk.Frame(self.tab1); top_frame.pack(expand=True, fill='both', pady=5)
        self.calendar = Calendar(top_frame, selectmode='day', date_pattern='yyyy-mm-dd'); self.calendar.pack(side='left', padx=10, fill='both', expand=True)
        right_frame = ttk.Frame(top_frame); right_frame.pack(side='left', padx=10, fill='y')
        self.time_label = ttk.Label(right_frame, text="Current Time", font=('Helvetica', 12)); self.time_label.pack(pady=10)
        time_entry_frame = ttk.Frame(right_frame); time_entry_frame.pack(pady=10)
        self.hour_combo = ttk.Combobox(time_entry_frame, values=[str(h) for h in range(1, 13)], width=3)
        self.minute_combo = ttk.Combobox(time_entry_frame, values=[f"{m:02d}" for m in range(60)], width=3)
        self.second_combo = ttk.Combobox(time_entry_frame, values=[f"{s:02d}" for s in range(60)], width=3)
        self.ampm_combo = ttk.Combobox(time_entry_frame, values=["AM", "PM"], width=3)
        for widget in [self.hour_combo, ttk.Label(time_entry_frame, text=":"), self.minute_combo, ttk.Label(time_entry_frame, text=":"), self.second_combo]: widget.pack(side='left')
        self.ampm_combo.pack(side='left', padx=5)
        ntp_check = ttk.Checkbutton(right_frame, text="Synchronize with network time servers", variable=self.ntp_var, command=self.update_widget_states); ntp_check.pack(pady=20)
        button_frame = ttk.Frame(self.tab1); button_frame.pack(fill='x', pady=10)
        for text, command in [("About", self.do_about), ("Reset", self.set_initial_values), ("OK", self.apply_and_quit), ("Apply", self.apply_changes), ("Cancel", self.root.destroy)]:
            ttk.Button(button_frame, text=text, command=command).pack(side='left', expand=True)

    def create_tab2_widgets(self):
        """Creates and places all widgets for the 'Time Zone' tab."""
        current_tz_frame = ttk.Frame(self.tab2); current_tz_frame.pack(fill='x', pady=5)
        ttk.Label(current_tz_frame, text="Current Time Zone:").pack(side='left')
        self.current_tz_entry = ttk.Entry(current_tz_frame, state='readonly'); self.current_tz_entry.pack(side='left', expand=True, fill='x', padx=5)
        ttk.Label(self.tab2, text="To change the timezone, select your area from the list below:").pack(fill='x', pady=(10, 5))
        selection_frame = ttk.Frame(self.tab2); selection_frame.pack(fill='x', pady=5)
        self.timezone_combo = ttk.Combobox(selection_frame, state='readonly'); self.timezone_combo.pack(side='left', expand=True, fill='x')
        ttk.Button(selection_frame, text="Set Time Zone", command=self.apply_zone).pack(side='left', padx=10)

    # --- Action/Command Logic ---
    def _run_privileged(self, command_str, success_msg="System settings updated."):
        """
        Runs a command string with root privileges using pkexec.
        This is a centralized helper to ensure consistent error handling
        and user feedback for all privileged operations.
        Returns True on success, False on failure or cancellation.
        """
        try:
            # pkexec runs a shell (-c) to execute our command string. This allows
            # us to chain multiple commands together (e.g., with &&).
            full_command = ["pkexec", "sh", "-c", command_str]
            subprocess.run(full_command, check=True, capture_output=True, text=True)
            messagebox.showinfo("Success", success_msg)
            return True
        except subprocess.CalledProcessError as e:
            # pkexec returns specific codes if the user cancels the dialog.
            if e.returncode in [126, 127]:
                messagebox.showwarning("Cancelled", "Authentication was cancelled. No changes were made.")
            else:
                messagebox.showerror("Error", f"Command failed:\n\n{e.stderr or e.stdout}")
            return False
        except FileNotFoundError:
            messagebox.showerror("Error", "The 'pkexec' command was not found. Please ensure Polkit is installed.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{e}")
            return False
        finally:
            # No matter what happens, ensure the clock timer is restarted, as this
            # entire function is a blocking call that freezes the UI.
            self.update_clock()

    def apply_changes(self):
        """Main function for the Apply button. Bundles all changes into one pkexec call."""
        commands_to_run = []
        ntp_state_changed = self.ntp_var.get() != self.initial_ntp_state

        if ntp_state_changed:
            ntp_command = "true" if self.ntp_var.get() else "false"
            commands_to_run.append(f"timedatectl set-ntp {ntp_command}")

        # Only consider setting the time if NTP is being turned off or is already off.
        if not self.ntp_var.get():
            date_str = self.calendar.get_date(); y, m, d = map(int, date_str.split('-'))
            h12=int(self.hour_combo.get()); mn=int(self.minute_combo.get()); s=int(self.second_combo.get())
            ampm=self.ampm_combo.get(); h24=h12
            if ampm=='PM' and h12!=12: h24+=12
            elif ampm=='AM' and h12==12: h24=0
            dt_str = f"{y}-{m:02d}-{d:02d} {h24:02d}:{mn:02d}:{s:02d}"
            commands_to_run.append(f"timedatectl set-time {shlex.quote(dt_str)}")

        if not commands_to_run:
            messagebox.showinfo("No Changes", "System is already configured as requested.")
            return

        if self._run_privileged(" && ".join(commands_to_run)):
            # On success, re-sync Python's time and update the UI to the new state.
            time.tzset()
            self.set_initial_values()
        else:
            # On failure or cancellation, revert the UI to match the actual system state.
            self.set_initial_values()

    def apply_and_quit(self):
        """Applies changes and then closes the application."""
        self.apply_changes(); self.root.destroy()

    def do_about(self):
        """Displays a custom, centered 'About' dialog."""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Phrozen Clock")
        about_dialog.transient(self.root)

        # Define a reliable, fixed size for the dialog.
        dialog_width = 380
        dialog_height = 202

        # Prevent the user from shrinking the window smaller than its intended size.
        about_dialog.minsize(dialog_width, dialog_height)

        # This outer frame expands if the window is resized, keeping the content centered.
        centering_frame = ttk.Frame(about_dialog)
        centering_frame.pack(expand=True, fill='both')

        # This inner frame holds the content and is placed in the middle.
        content_frame = ttk.Frame(centering_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

        text_frame = ttk.Frame(content_frame)
        text_frame.pack(padx=15, pady=10)

        title_label = ttk.Label(text_frame, text="Phrozen Clock", font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=(0, 10))

        copyright_text = ("Copyright (c) 2003-2004, Erica Andrews\n"
                          "Tkinter Port (c) 2025, DeltaResero")
        copyright_label = ttk.Label(text_frame, text=copyright_text, justify=tk.CENTER)
        copyright_label.pack(pady=5)

        desc_label = ttk.Label(text_frame, text="A simple clock management application for lightweight desktops.", justify=tk.CENTER, wraplength=300)
        desc_label.pack(pady=10)

        ok_button = ttk.Button(content_frame, text="OK", command=about_dialog.destroy)
        ok_button.pack(pady=(5, 10))

        # Ensure any pending Tkinter tasks are done before we get geometry info.
        about_dialog.update_idletasks()

        # Get parent window's position and size for centering.
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        # Calculate the position to perfectly center the dialog.
        x = root_x + (root_w // 2) - (dialog_width // 2)
        y = root_y + (root_h // 2) - (dialog_height // 2)

        # Set the final size and position of the dialog.
        about_dialog.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')

        # Make the dialog modal.
        about_dialog.grab_set()
        about_dialog.focus_set()
        ok_button.focus()
        self.root.wait_window(about_dialog)

    def apply_zone(self):
        """Sets the system timezone and relaunches the application."""
        current_geometry = self.root.geometry()
        new_zone = self.timezone_combo.get()
        if not new_zone: return
        zone_file = os.path.join(self.ZONEINFO_DIR, new_zone)
        if not os.path.exists(zone_file): return

        rm_cmd = f"rm -f {shlex.quote(self.TIME_ZONE_INFO_FILE)}"
        ln_cmd = f"ln -s {shlex.quote(zone_file)} {shlex.quote(self.TIME_ZONE_INFO_FILE)}"

        # We must relaunch because many parts of the system and the Python runtime
        # itself cache the timezone at startup.
        if self._run_privileged(f"{rm_cmd} && {ln_cmd}", success_msg="Time zone changed. The application will now restart."):
            args = [sys.executable] + [sys.argv[0], current_geometry]
            subprocess.Popen(args)
            self.root.destroy()

    # --- Core File/System Logic Methods ---
    def isGlibc(self, d):
        if d is None or not os.path.isdir(d): return False
        import glob
        for ext in self.IGNORE_EXT:
            if glob.glob(os.path.join(d,ext)): return False
            for s in ['America/','posix/','Africa/','Canada/','Asia/','right/','Indian/']:
                if glob.glob(os.path.join(d,s,ext)): return False
        return True
    def locateZoneinfo(self):
        if self.isGlibc(self.ZONEINFO_DIR): return 0
        for d in self.ZONE_DIRS:
            if self.isGlibc(d): self.ZONEINFO_DIR=d; return 0
        messagebox.showerror("Critical Error", "Could not locate 'zoneinfo' files."); return -1
    def locateLocaltimeFile(self):
        for f in self.LOCALTIME_FILES:
            if os.path.exists(f): self.TIME_ZONE_INFO_FILE=f; return
    def locateTimezoneFile(self):
        for f in self.TIMEZONE_FILES:
            if os.path.exists(f): self.TIME_ZONE_DESC_FILE=f; return
    def getCurrentTZName(self):
        try:
            if not os.path.islink(self.TIME_ZONE_INFO_FILE): return "Unknown"
            rpath = os.path.realpath(self.TIME_ZONE_INFO_FILE); zdir = os.path.realpath(self.ZONEINFO_DIR)
            return os.path.relpath(rpath, zdir)
        except: return "Unknown"
    def loadTimeZones(self):
        self.TZ_DICT = {}
        if not self.ZONEINFO_DIR: return
        for r, d, f in os.walk(self.ZONEINFO_DIR):
            for file in f:
                fp = os.path.join(r, file)
                if '.' not in file and not file.endswith('~'): self.TZ_DICT[os.path.relpath(fp, self.ZONEINFO_DIR)] = True

if __name__ == '__main__':
    root = tk.Tk()
    app = ClockApp(root)
    root.mainloop()

# EOF

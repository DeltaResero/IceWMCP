#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP IceWM Keys: Placeholder for a future module.
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
from tkinter import messagebox
import sys

class PlaceholderApp:
    """
    A placeholder application that informs the user that this feature is not
    yet implemented.
    """
    def __init__(self, root):
        # Hide the main, empty root window.
        root.withdraw()

        messagebox.showinfo(
            "Feature Not Implemented",
            "The 'IceWM Keys' configuration module, which is part of the larger 'icepref' "
            "utility, has not yet been modernized.\n\n"
            "This feature is planned for a future update."
        )

        # Once the user clicks OK, destroy the hidden root window and exit.
        root.destroy()

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = PlaceholderApp(root)
        # No mainloop is needed as the app exits immediately.
    except Exception as e:
        # Fallback for any unexpected GUI error.
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

# EOF

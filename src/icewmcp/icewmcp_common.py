#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#  IceWMCP Common Module (Python 3 / Tkinter)
#
#  This is the modernized common library for the IceWMCP suite. It contains
#  shared, UI-agnostic helper functions.
#
#  Based on original work by:
#  Copyright (c) 2003-2004, Erica Andrews
#
#  Modernization by:
#  Copyright (c) 2025, DeltaResero
#
#  SPDX-License-Identifier: GPL-2.0-or-later
################################################################################

import sysconfig
import os
import sys

def get_data_path(resource_path):
    """
    Calculates the absolute path to a resource, intelligently handling both
    development (running from source) and installed environments.

    Args:
        resource_path (str): The relative path to the resource from within the
                             'share' directory (e.g., 'pixmaps/icon.png').

    Returns:
        str: The absolute path to the resource.
    """
    # Determine the project root, which is two levels up from this file's directory
    # i.e., from src/icewmcp/ -> src/ -> ./
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Check for a local 'share' directory first. This indicates a development environment.
    local_share_dir = os.path.join(project_root, 'share')

    if os.path.isdir(local_share_dir):
        # DEVELOPMENT MODE: Use the local 'share' directory as the base.
        return os.path.join(local_share_dir, resource_path)
    else:
        # INSTALLED MODE: Use the system's shared data directory.
        # The installation prefix (e.g., /usr or /usr/local)
        install_prefix = sysconfig.get_path('data')

        # The data files are installed in a namespaced subdirectory.
        return os.path.join(install_prefix, 'share', 'icewmcp', resource_path)

# As other modules are modernized, any other required common functions will be added here.

# EOF

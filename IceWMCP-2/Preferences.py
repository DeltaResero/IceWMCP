# IceMe
# =====
#
# Copyright 2000-2002, Dirk Moebius <dmoebius@gmx.net> 
# and Mike Hostetler <thehaas@binary.net>
#
# This work comes with no warranty regarding its suitability for any purpose.
# The author is not responsible for any damages caused by the use of this
# program.
#
# This software is distributed under the GNU General Public License
#################################################
########
# With Modifications by Erica Andrews (PhrozenSmoke@yahoo.com), February-June 2003
# This is a modified version of IceMe 1.0.0 ("IceWMCP Edition"), optimized for IceWM ControlPanel.
# Copyright (c) 2003 Erica Andrews
##################

import sys
import string
import os
import os.path
import getopt
from constants import *


class Preferences:

    def __init__(self, args):
        self.ERROR = 0
        self.HELP_OPTION = 0
        self.IGNORE_HOME = 0
        self.GLOBAL_ICEWM_DIR = 0

        # parse options and arguments:
        try:
            optlist, _args = getopt.getopt(args[1:], "hr",
                                          ["help", "run-as-root"])
        except getopt.error, msg:
            sys.stderr.write("%s: error: %s\n" % (args[0], msg))
            self.ERROR = 2
            return

        # process options:
        for opt,val in optlist:
            if opt == "-h" or opt == "--help":
                self.HELP_OPTION = 1
            elif opt == "-r" or opt == "--run-as-root":
                self.IGNORE_HOME = 1
            else:
		pass
		# fixed here - 4.21.2003 - Erica Andrews, dont quit just because of bad cmdline option
                #sys.stderr.write("%s: error: unknown option\n" % args[0])
                #self.ERROR = 2
                #return

        # process arguments:
        if len(_args) > 1:
            sys.stderr.write("%s: error: more than one dir\n" % args[0])
            self.ERROR = 2
            return
        if len(_args) == 1:
            if not os.path.isdir(_args[0]):
                sys.stderr.write("%s: error: %s is not an directory.\n" % \
                                 (args[0], _args[0]))
		# fixed here - 4.21.2003 - Erica Andrews, dont quit just because of bad cmdline option
                #self.ERROR = 1
                #return
            self.GLOBAL_ICEWM_DIR = _args[0]

        # set the global icewm directory, if not set already:

	#  PhrozenSmoke@yahoo.com - edition, Erica Andrews: 
	# 4.21.2003 - fixed a bug here that could leave a null (None) value for self.GLOBAL_ICEWM_DIR
	#  fixes bug reported by Francesco <fr4nk ['at'] email.it> on  April 16, 2003

	""" 	> Traceback (most recent call last):
		>    File "<string>", line 26, in ?
		>    File "/usr/share/IceWMCP/IceMe.py", line 848, in main
		>    File "/usr/share/IceWMCP/IceMe.py", line 50, in __init__
		>    File "/usr/share/IceWMCP/IceMe.py", line 197, in __initTree
		>    File "/usr/share/IceWMCP/Preferences.py", line 160, in getIceWMFile
		>    File "/usr/lib/python2.2/posixpath.py", line 44, in join
		>      def join(a, *p):   """

	#  The bug was caused by calling os.path.join on a null-None value for self.GLOBAL_ICEWM_DIR -fixed

        if not self.GLOBAL_ICEWM_DIR: self.GLOBAL_ICEWM_DIR=getIceWMConfigPath()   
	# from 'icewmcp_common.py', this at least returns a default non-null value if all else fails

	#  old, buggy code below is commented out - 4.21.2003, Erica Andrews
        """ if not self.GLOBAL_ICEWM_DIR:
            for dir in ("/etc/X11/icewm",
		        "/usr/lib/icewm",
		        "/usr/share/icewm",
                        "/usr/local/lib/icewm",
                        "/usr/local/lib/X11/icewm",
                        "/usr/X11R6/lib/X11/icewm"):
                if os.path.isdir(dir):
                    self.GLOBAL_ICEWM_DIR = dir
                    break;  """

        # get some preferences:
        prefs = self.getPreferences("Theme", "IconPath")
        theme_string = prefs.get("Theme", "")
        slashpos = string.find(theme_string, "/")
        theme = theme_string[1:slashpos]
        iconpath_string = prefs.get("IconPath", "")
        prefs_iconpath = string.split(iconpath_string[1:-1], ":")

        # construct ICONPATH from GLOBAL_ICEWM_DIR and PREFS_ICONPATH:
        ip = []
        # 1. append "icons" subdirs in $HOME:
        if not self.IGNORE_HOME:
            self.appendDir(ip, os.path.join(HOME_ICEWM, "themes", theme, "icons"))
            self.appendDir(ip, os.path.join(HOME_ICEWM, "icons"))
        # 2. append "icons" subdirs in global directory:
        if self.GLOBAL_ICEWM_DIR:
            self.appendDir(ip, os.path.join(self.GLOBAL_ICEWM_DIR, "themes", theme, "icons"))
            self.appendDir(ip, os.path.join(self.GLOBAL_ICEWM_DIR, "icons"))
        # 3. append dirs from IconPath preference:
        for dir in prefs_iconpath:
            if dir:
                self.appendDir(ip, dir)
        self.ICONPATH = tuple(ip)


    def getErrorCode(self):
        return self.ERROR

    def getHelpOption(self):
        return self.HELP_OPTION

    def getIgnoreHomeOption(self):
        return self.IGNORE_HOME

    def getIconPaths(self):
        return self.ICONPATH


    def getPreferences(self, *args):
        """getPreferences(string1, string2, ...) -> dict

        Get preferences from either the local or the global preference file.
        At first the global preference file is searched in various standard
        locations. After that, the local preferences file
        $HOME/.icewm/preferences is scanned, overriding the global
        preferences. You may provide a single keyword string or a list of
        keyword strings. Each file is scanned exactly once for the keywords.
        The function returns a dictionary with the keywords as keys and the
        entries from the preferences files as values.

        If ignore_home is true, menu files in $HOME are ignored and only
        global menu files are returned.

        Example:
        getPreferences("Theme", "IconPath") ->
            { 'Theme' : '"microGUI/default.theme"',
              'IconPath' : '"/usr/local/share/icons:/opt/kde/share/icons"' }
        """
        values = {}
        if self.GLOBAL_ICEWM_DIR:
            global_pref = os.path.join(self.GLOBAL_ICEWM_DIR, "preferences")
            if self.canRead(global_pref):
                for line in open(global_pref).readlines():
                    if not line or line[0] == "#": continue
                    pos = string.find(line, "=")
                    label = string.strip(line[:pos])
                    if label in args:
                        values[label] = string.strip(line[pos+1:])
        if not self.IGNORE_HOME:
            local_pref = os.path.join(HOME_ICEWM, "preferences")
            if self.canRead(local_pref):
                for line in open(local_pref).readlines():
                    if not line or line[0] == "#": continue
                    pos = string.find(line, "=")
                    label = string.strip(line[:pos])
                    if label in args:
                        values[label] = string.strip(line[pos+1:])
        return values


    def getIceWMFile(self, name, for_read_only=1):
        global_file = os.path.join(self.GLOBAL_ICEWM_DIR, name)
        home_file = os.path.join(HOME_ICEWM, name)
        if self.IGNORE_HOME:
            if for_read_only and not self.canRead(global_file):
                return None
            else:
                return global_file
        else:
            if for_read_only:
                if self.canRead(home_file): return home_file
                if self.canRead(global_file): return global_file
                return None
            else:
                return home_file


    def canRead(self, path, file=None):
        if file:
            filename = os.path.join(path, file)
        else:
            filename = path
        try:
            f = open(filename, "r")
            f.close()
            return 1
        except:
            return 0
        return 0


    def appendDir(self, where, what):
        if os.path.isdir(what):
            where.append(what)
				


def test():
    prefs = Preferences("")
    print "IconPath:", prefs.getIconPaths()
    print "IceWM uses the following files:"
    print prefs.getIceWMFile("menu")
    print prefs.getIceWMFile("programs")
    print prefs.getIceWMFile("toolbar")
    print prefs.getIceWMFile("keys")

if __name__ == "__main__":
    test()

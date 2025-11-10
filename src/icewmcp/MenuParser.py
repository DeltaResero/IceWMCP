# -*- coding: ISO-8859-1 -*-

################################################
## IceMe
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
#################################
#  With Modifications by Erica Andrews 
#  (PhrozenSmoke ['at'] yahoo.com)
#  February 2003-February 2004
#  
#  This is a modified version of IceMe 
#  1.0.0 ("IceWMCP Edition"), optimized for 
#  IceWM ControlPanel.
#  
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
#################################
#############################################
#	This program is free software; you can redistribute
#	it and/or modify it under the terms of the GNU 
#	General Public License as published by the 
#	Free Software Foundation; either version 2 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will 
#	be useful, but WITHOUT ANY WARRANTY; 
#	without even the implied warranty of 
#	MERCHANTABILITY or FITNESS FOR A 
#	PARTICULAR PURPOSE.
#
#	You should have received a copy of the GNU 
#	General Public License along with this program; 
#	if not, write to the Free Software Foundation, Inc., 
#	59 Temple Place - Suite 330, Boston, MA 
#	02111-1307, USA.
#############################################
#############################
#  PyGtk-2 Port Started By: 
#  	David Moore (djm6202@yahoo.co.nz)
#	March 2003
#############################
#############################
#  PyGtk-2 Port Continued By: 
#	Erica Andrews
#  	PhrozenSmoke ['at'] yahoo.com
#	October/November 2003
#############################

import string, sys
from .constants import *


class MenuParser:

    def __init__(self, filename):  # changed 12.20.2003, Erica Andrews - error catching
	try:
        	file = open(filename)
        	self.lines = file.readlines()
       		file.close()
	except:
		self.lines=""

    def __getNextLine(self):
        line = None
        while len(self.lines) > 0:
            line = string.strip(self.lines[0])
            del self.lines[0]
            if line != "" and line[0] != "#":
                return line
        return None

    def getNextEntry(self):
        line = self.__getNextLine()
        if line is None:
            return None
        tag = string.split(line)[0].strip()
        if tag == "separator":
            return [MENUTREE_SEPARATOR, None, None, None]
        elif tag == "prog":
            return [MENUTREE_PROG,] + self.__parseProg(line[5:])

        elif tag == "menuprog":
	    # added 12.20.2003, Erica Andrews, support for 'embedded' menus
	    # like those from the embedded Gnome1 and Gnome2 menus...to 
	    # handle menu lines like: 
	    # menuprog "Gnome Menu" gnome icewm-menu-gnome1 --list /usr/share/gnome/apps
	    # Fixes Bug Report/Feature Request #488846
	    # Received from: klaumikli ['at'] gmx.de, at: Fri Oct 17 14:46:01 2003

            return [MENUTREE_PROG,] + self.__parseProg(line[9:])

        elif tag == "restart":
            return [MENUTREE_RESTART,] + self.__parseProg(line[8:])
        elif tag == "menu":
            return [MENUTREE_SUBMENU,] + self.__parseMenu(line[5:])
        elif tag == "}":
            return [MENUTREE_SUBMENU_END, None, None, None]
        else:
            sys.stderr.write("*** Unknown tag in menu file. The line was: %s\n" % line)
            return [MENUTREE_UNKNOWN, None, None, None]

    def __parseWord(self, s, start=0):
        inQuotes = 0
        atStart = 1
        word = ""
        i = start
        while i < len(s):
            c = s[i]
            i = i + 1
            if c in string.whitespace:
                if inQuotes:
                    word = word + c
                elif atStart:
                    pass
                else:
                    return (word, i)
            elif c == '"':
                inQuotes = not inQuotes
                atStart = 0
            else:
                word = word + c
                atStart = 0
        return (word, i)

    def __parseProg(self, s):
        name, next_pos = self.__parseWord(s)
        icon, next_pos = self.__parseWord(s, next_pos)
        command = string.strip(s[next_pos:])
        return [name, icon, command]

    def __parseMenu(self, s):
        name, next_pos = self.__parseWord(s)
        icon, next_pos = self.__parseWord(s, next_pos)
        return [name, icon, None]



def prettyprint(filename):
    m = MenuParser(filename)
    level = 0
    while 1:
        entry = m.getNextEntry()
        if entry is None:
            return
        else:
            if entry[0] == MENUTREE_SEPARATOR:
                print("%sseparator" % ("    "*level))
            elif entry[0] == MENUTREE_SUBMENU_END:
                level = level - 1
                print("%s}" % ("    "*level))
            elif entry[0] == MENUTREE_UNKNOWN:
                pass
            else:
                if entry[2] == "":
                    icon = "- "
                else:
                    icon = '"' + entry[2] + '" '
                if entry[0] == MENUTREE_PROG:
                    print('%sprog "%s" %s%s' % ("    "*level, entry[1], icon, entry[3]))
                elif entry[0] == MENUTREE_RESTART:
                    print('%srestart "%s" %s%s' % ("    "*level, entry[1], icon, entry[3]))
                elif entry[0] == MENUTREE_SUBMENU:
                    print('%smenu "%s" %s{' % ("    "*level, entry[1], icon))
                    level = level + 1


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.stderr.write("Usage: python %s <icewmmenufile>\n" % sys.argv[0])
    else:
        prettyprint(sys.argv[1])

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
# With Modifications by Erica Andrews (PhrozenSmoke ['at'] yahoo.com), February-December 2003
# This is a modified version of IceMe 1.0.0 ("IceWMCP Edition"), optimized for IceWM ControlPanel.
# Copyright (c) 2003 Erica Andrews
########

import string, sys
from constants import *


class MenuParser:

    def __init__(self, filename):
        file = open(filename)
        self.lines = file.readlines()
        file.close()

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
        tag = string.split(line)[0]
        if tag == "separator":
            return [MENUTREE_SEPARATOR, None, None, None]
        elif tag == "prog":
            return [MENUTREE_PROG,] + self.__parseProg(line[5:])
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
                print "%sseparator" % ("    "*level)
            elif entry[0] == MENUTREE_SUBMENU_END:
                level = level - 1
                print "%s}" % ("    "*level)
            elif entry[0] == MENUTREE_UNKNOWN:
                pass
            else:
                if entry[2] == "":
                    icon = "- "
                else:
                    icon = '"' + entry[2] + '" '
                if entry[0] == MENUTREE_PROG:
                    print '%sprog "%s" %s%s' % ("    "*level, entry[1], icon, entry[3])
                elif entry[0] == MENUTREE_RESTART:
                    print '%srestart "%s" %s%s' % ("    "*level, entry[1], icon, entry[3])
                elif entry[0] == MENUTREE_SUBMENU:
                    print '%smenu "%s" %s{' % ("    "*level, entry[1], icon)
                    level = level + 1


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.stderr.write("Usage: python %s <icewmmenufile>\n" % sys.argv[0])
    else:
        prettyprint(sys.argv[1])

#! /usr/bin/env python

######################################
# IceWM Control Panel Starter 
# 
# Copyright 2003 by Erica Andrews 
# (PhrozenSmoke@yahoo.com)
# http://icesoundmanager.sourceforge.net
# 
# A starter script for static binaries built with Installer
# 
# This program is distributed under the GNU General
# Public License (open source).
#######################################

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

# seems to help some Debian systems
try:
	import pygtk
	pygtk.require("2.0")
except:
	pass

# Some PyGtk2 path settings while we upgrade from PyGtk-1 to PyGtk2
try:
	import sys
	sys.path=["/usr/lib/python2.2/site-packages/gtk-2.0"]+sys.path
	sys.path=["/usr/lib/python2.3/site-packages/gtk-2.0"]+sys.path
	import gtk
	import gtk.gdk 
	GDK=gtk.gdk
	GTK=gtk
	from gtk import *
	import pango
except:
	print "You do not have PyGtk-2 or one of its libraries properly installed."
	print "This application requires PyGtk-2 1.99/2.00 or better."
	sys.exit(0)
	pass


import icewmcp_common,ICEWMCP_BugReport
icewmcp_common.setSplash(icewmcp_common.getLocaleDir)
icewmcp_common.showSplash(0)
icewmcp_common.IS_STATIC_BINARY="yes"
ICEWMCP_BugReport.IS_STATIC_BINARY="yes"
icewmcp_common.NOSPLASH=1  # disable splash window from icepref_td
while gtk.events_pending():
	gtk.mainiteration()

import os,sys,IceWMCP,IceWMCPWinOptions,IceWMCPMouse,IceWMCPKeyboard,IceWMCPWallpaper,IceMe,phrozenclock,icepref,pyspool,icesound,icepref_td,IceWMCPGtkIconSelection,IceWMCP_GtkPCCard,IceWMCPEnergyStar

global HW_SUPPORT
try:
	import IceWMCPSystem
	HW_SUPPORT=1
except:
	HW_SUPPORT=0


if __name__== "__main__" :
	mods=["IceWMCP.py","IceWMCPWinOptions.py","IceMe.py","IceWMCPKeyEdit.py","IceWMCPMouse.py","IceWMCPKeyboard.py","IceWMCPWallpaper.py","icepref.py","icesound.py","pyspool.py","phrozenclock.py","IceWMCPGtkIconSelection.py","IceWMCPCursors.py","icepref_td.py","IceWMCP_GtkPCCard.py","IceWMCPSystem.py","IceWMCPEnergyStar.py"]
	mods.sort()
	if len(sys.argv)>1:
		ar=sys.argv[1]
		if ar=="IceWMCP.py": IceWMCP.run(1)
		if ar=="IceWMCPWinOptions.py": IceWMCPWinOptions.run()
		if ar=="IceMe.py": 
			icewmcp_common.hideSplash()
			IceMe.main()
		if ar=="IceWMCPMouse.py": IceWMCPMouse.run()
		if ar=="IceWMCPKeyboard.py": IceWMCPKeyboard.run()
		if ar=="IceWMCPWallpaper.py": IceWMCPWallpaper.run()
		if ar=="icepref.py": 
			icepref.run()
		if ar=="IceWMCPEnergyStar.py": IceWMCPEnergyStar.run()
		if ar=="icesound.py": icesound.run()
		if ar=="pyspool.py": pyspool.run()
		if ar=="phrozenclock.py": phrozenclock.run()
		if ar=="icepref_td.py": 
			icepref_td.run()
		if ar=="IceWMCPGtkIconSelection.py": IceWMCPGtkIconSelection.run_icons()
		if ar=="IceWMCP_GtkPCCard.py": IceWMCP_GtkPCCard.run()
		if ar=="IceWMCPSystem.py": 
			if HW_SUPPORT==1:
				IceWMCPSystem.run()
			else:
				print "Sorry, the IceWMCPSystem.py plug-in module is not available or could not be loaded."
				print "You may download the module from http://icesoundmanager.sourceforge.net/download.php"
				sys.exit(0)
		if ar not in mods:
			print "\n\nAvailable IceWM Control Panel Modules:\n"
			for ii in mods:
				print "\t"+ii
			print "\nUSAGE: "+sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]+"icewmcp [module]\n\n"
			sys.exit(0)
	else: IceWMCP.run(1)
	
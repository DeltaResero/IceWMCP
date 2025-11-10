# -*- coding: ISO-8859-1 -*-

######################################
# IceWM Control Panel 
#  Drag-and-Drop support
# 
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
# 
# Centralized drag-n-drop support
# 
# This program is distributed under the GNU General
# Public License (open source).
#######################################
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

import binascii
from .icewmcp_common import *

# drag-n-drop support, added 2.23.2003
# for basic 'string'-based drag-n-drop

def addDragSupport(widget, drag_callback): 
	widget.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('STRING', 0, 0), ('text/plain', 0,1), ('text/uri-list', 0, 2) ], GDK.ACTION_COPY | GDK.ACTION_MOVE)
	widget.connect("drag_drop",drag_callback)
	widget.connect("drag_begin",drag_callback)
	widget.connect("drag_data_received",drag_callback)


def initColorDrag():   # mainly for IcePref2, IcePref-TD, and IceWMCPWallpaper - 'color buttons'
	# added 5.16.2003, a hidden color dialog for handling drag-n-drop color support on 'color buttons'
	# define these method only if drag-n-drop color support is requested

	# setDrag2 has been re-written, 12.2.2003, Erica Andrews
	# We no longer need the hidden color dialog thanks to some snooping I did on the 
	# binascii module - HAPPY haPPy JoY jOY!

	global setDrag2
	def setDrag2(*args): # drag-n-drop callback, added 5.16.2003, drag-n-drop support for 'color buttons'
		drago=args		
		if len(drago)==7: 
			try:			
				if str(drago[4].type)==str("application/x-color"):
					# returns a string that looks something like 'ffffb9b9ffffffff'
					rgbhex=binascii.hexlify(drago[4].data)
					#print "rgbhex  " +rgbhex	
					#print "len :  "+str(len(rgbhex))				
					if not len(rgbhex)==16: return   # something weird happened
					# translate to 6-char html-style color string like #FF00EE
					rgbhex2="#"+rgbhex[2:4]+rgbhex[6:8]+rgbhex[10:12]
					#print "rgb2  : "+rgbhex2
					r,g,b=getRGBForHex(rgbhex2)  # from icewmcp_common
					#print "Colors:  "+str(r) +"  "+str(g)+"  "+str(b)

					# update the color on the 'color button' can called this drag-n-drop
					drago[0].get_data("colorbutton").updateColorProperties(r,g,b)
			except:
				pass


	global addDragSupportColor
	def addDragSupportColor(widget): # drag-n-drop support, added 5.15.2003 , for color buttons
		widget.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('application/x-icewmcp-color', 0, 0), ("application/x-color", 0, 0)], GDK.ACTION_COPY | GDK.ACTION_MOVE)
		widget.connect("drag_drop",setDrag2)
		widget.connect("drag_begin",setDrag2)
		widget.connect("drag_data_received",setDrag2)


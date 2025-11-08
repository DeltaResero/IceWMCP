# -*- coding: ISO-8859-1 -*-

######################################
# IceWM Control Panel  
# Pango Font Description to XLFD translator
# 
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
# 
# A module for converting between legacy XLFD
# font strings and Pango's new stupid 
# "descriptions"
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

from icewmcp_common import *


# "Houston we have a problem..."
"""
	The problem between IceWM and Gtk+2/PyGtk-2 is the new 
	Pango font 'descriptions' which use "Arial Bold 18" instead of 
	the more standardized XLFD font strings like:
	'-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*'
	The new Gtk Font Selection dialogs FORCE us to use the new 
	Pango 'descriptions' for setting and getting the selected font.
	BUT, IceWM needs XLFD strings in the preferences file.  This 
	wouldn't be a problem if the makers of Pango weren't stupid 
	enough to completely *get rid* of all ways of retrieving an 
	XLFD string, which many applications still use.  So now, 
	we must reverse-engineer the Pango 'description' to get a 
	real XLFD font name.  Hmm...maybe Gtk is getting a little 
	too Microsoft-ish: Dummy-ing things up and not allowing you to 
	'touch' anything for fear you might be too stupid to handle it.
	The problem with the Pango 'description' format is that it loses 
	*important* things about the font like the Foundry and the char-set.
	Boy, Pango really SUCKS...Font loading issues and 'utf8_validate'
	warnings quickly take the fun out of programming.

	I'm sure this new module alone will create tons of bug reports - 
	but I know of no other way to get an XLFD string out of the 
	'Pango Description' FontSelectionDialogs Gtk-2 has made mandatory.	

	Anyways....here goes...Let's see if we can get Pango to play nice with 
	IceWM...	
"""

# Character set to assume for reconstructed fonts, wildcards for all other systems
ASSUME_CHARSET="-*-*"

# I want to force charset 'iso8859-1' on my own system
# This shouldnt affect you unless your computer's host name is the same
# as my email address!  (and that would be pretty damn scary!)
try:
	if os.uname()[1].lower().find("phrozensmoke")>-1:
		ASSUME_CHARSET="iso8859-1"
except:
	pass


def get_pango_font_weight(some_val):
	weights={
	pango.WEIGHT_BOLD: "bold",
	pango.WEIGHT_HEAVY: "heavy", 
	pango.WEIGHT_LIGHT: "thin",
	pango.WEIGHT_NORMAL: "medium",
	pango.WEIGHT_ULTRABOLD: "ultrabold",
	pango.WEIGHT_ULTRALIGHT:"ultralight"
				}
	if weights.has_key(some_val): 
		return weights[some_val]
	return "*"  # wildcard


def get_pango_font_condense(some_val):
	condense={
	pango.STRETCH_CONDENSED: "condensed",
	pango.STRETCH_EXPANDED: "expanded", 
	pango.STRETCH_EXTRA_CONDENSED: "extracondensed", 
	pango.STRETCH_EXTRA_EXPANDED: "extraexpanded",
	pango.STRETCH_NORMAL: "normal",
	pango.STRETCH_SEMI_CONDENSED: "semicondensed",
	pango.STRETCH_SEMI_EXPANDED: "semiexpanded", 
	pango.STRETCH_ULTRA_CONDENSED: "ultracondensed",
	pango.STRETCH_ULTRA_EXPANDED: "ultraexpanded",
				}
	if condense.has_key(some_val): 
		return condense[some_val]
	return "*"  # wildcard

def get_pango_font_style(some_val):
	if some_val==pango.STYLE_OBLIQUE: return "o"
	if some_val==pango.STYLE_ITALIC: return "i"	
	return "r"  #Normal

def get_valid_pango_font_desc(mystr):
	# added 12.13.2003, fixes the bug where the whole app crashed if an invalid font 
	# was supplied to the FontSelection dialog...
	# to prevent against invalid Pango font descriptions the user may type in like "Arial -2"
	# We also want to avoid trying to load fonts like "Arial 1500", 1500pts=kinda dangerous
	# so the maximum font size we'll allow is 100pts - which is HUGE, about half the screen's height
	# Ridiculously large fonts can crash the FontSelection dialog (and the whole application) or 
	# create a FontSelection window so big that it completely blocks the rest of the screen and 
	# makes the Font dialog's 'close' button unreachable.
	# all Pango font sizes are a multiple of 1024

	try:
		fontdesc=pango.FontDescription(mystr)
		if fontdesc.get_size()>1023:  # should be at least a size of 1pt
			if fontdesc.get_size()< (101 * 1024):  # should be 100pts or smaller
				return mystr  # it's okay, leave as is
		return "arial 10"   # a default
	except:
		return "arial 10"   # a default
	

def pango2XLFD(pango_str):
    try:
	mystr=pango_str
	print "here1"
	fontdesc=pango.FontDescription(get_valid_pango_font_desc(mystr))
	print "here2"
	face=fontdesc.get_family().strip()
	weight=get_pango_font_weight(fontdesc.get_weight())
	fsize=fontdesc.get_size()/1024
	if fsize<1: fsize=1  # bug fix 12.19.2003, dont allow fonts sizes of '0' or less, EVER
	fsize=str(fsize*10)
	condense=get_pango_font_condense(fontdesc.get_stretch()).strip()
	fstyle=get_pango_font_style(fontdesc.get_style()).strip()
	#now reconstruct an XLFD compatible string and hope for the best
	fontval="-*-"+face+"-"+weight+"-"+fstyle+"-"+condense+"-*-*-"+fsize+"-*-*-p-*-"+str(ASSUME_CHARSET)
	return fontval.lower().strip()
    except:
	return pango_str

def XLFD2pango(xlfd_str):
    try:
	mystr=xlfd_str
	# support legacy fonts like '-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*'
	# This should convert '-adobe-courier-medium-r-*-*-*-140-*-*-'
	# to something like "courier medium 14", it's imperfect but works for most fonts
	valls=mystr.split("-")
	if len(valls)<9: return mystr  # something odd or incomplete
	face=valls[2].strip()
	weight="medium"
	if not valls[3].strip()=="*": 
		weight=valls[3].strip()
	fsize=valls[8].strip()

	# bug fix 12.19.2003, make sure 'fsize' is a valid integer and is greater than 0
	try:
		if int(fsize)>1: 
			if int(fsize)<21: 
				# bug fix 12.19.2003, allow for mal-formed 
				# font sizes like '13' instead of '130', '6' instead of '60' etc.
				fsize=fsize+"0"     # add the necessary '0'

		if int(fsize)<1: 
			# bug fix 12.19.2003, make sure 'fsize' is greater than 0
			fsize="100"
	except:
		fsize="100"  # VERY malformed, not even an integer, default to a 10 pt font

	fsize=str(int(fsize.strip())/10)  # convert sizes like '130' to '13'

	if int(fsize)<1: # bug fix 12.19.2003, make sure 'fsize' is greater than 0
		fsize="10"  # cant allow a font of size less than 1, fall back to 10 pt

	condense=""
	fstyle=""
	if valls[4].strip()=="i": 
		fstyle=" italic "
	if valls[4].strip()=="o": 
		fstyle=" oblique "
	if not valls[5].strip()=="*": 
		if not valls[5].lower().strip()=="normal":  
			if not valls[5].lower().strip()=="regular":  
				condense=valls[5].strip()+" "
	fontval=face+", "+weight+fstyle+" "+condense+fsize
	return get_valid_pango_font_desc(fontval.lower().replace("*","").replace("  "," ").strip())
    except:
	return get_valid_pango_font_desc(xlfd_str)



def XLFD2Xft(xlfd_str):
    try:
	mystr=xlfd_str
	# support legacy fonts like '-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*'
	# This should convert '-adobe-courier-medium-r-*-*-*-140-*-*-'
	# to something like "courier:size=14:bold", it's imperfect but works for most fonts
	valls=str(mystr).replace("\"", "").split("-")
	if len(valls)<9: return mystr  # something odd or incomplete
	face=valls[2].strip()
	weight=""
	if not valls[3].strip()=="*": 
		weight=":"+valls[3].strip()
	fsize=valls[8].strip()

	# bug fix 12.19.2003, make sure 'fsize' is a valid integer and is greater than 0
	try:
		if int(fsize)>1: 
			if int(fsize)<21: 
				# bug fix 12.19.2003, allow for mal-formed 
				# font sizes like '13' instead of '130', '6' instead of '60' etc.
				fsize=fsize+"0"     # add the necessary '0'

		if int(fsize)<1: 
			# bug fix 12.19.2003, make sure 'fsize' is greater than 0
			fsize="100"
	except:
		fsize="100"  # VERY malformed, not even an integer, default to a 10 pt font

	fsize=str(int(fsize.strip())/10)  # convert sizes like '130' to '13'

	if int(fsize)<1: # bug fix 12.19.2003, make sure 'fsize' is greater than 0
		fsize="12"  # cant allow a font of size less than 1, fall back to 10 pt

	condense=""
	fstyle=""
	if valls[4].strip()=="i": 
		fstyle=":italic"
	if valls[4].strip()=="o": 
		fstyle=":oblique"
	if not valls[5].strip()=="*": 
		if not valls[5].lower().strip()=="normal":  
			if not valls[5].lower().strip()=="regular":  
				condense=valls[5].strip()+" "
	fontval=face+":size="+str(fsize)+str(weight)+str(fstyle)
	return fontval
    except:
	return "sans-serif:size=12"




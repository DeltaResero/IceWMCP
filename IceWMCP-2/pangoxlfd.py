######################################
# IceWM Control Panel  
# 
# Copyright 2003 by Erica Andrews 
# (PhrozenSmoke@yahoo.com)
# http://icesoundmanager.sourceforge.net
# 
# A module for converting between legacy XLFD
# font strings and Pango's new stupid 
# "descriptions"
#
# This program is distributed under the GNU General
# Public License (open source).
# 
#######################################

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

def pango2XLFD(pango_str):
	mystr=pango_str
	fontdesc=pango.FontDescription(mystr)
	face=fontdesc.get_family()
	weight=get_pango_font_weight(fontdesc.get_weight())
	fsize=fontdesc.get_size()/1024
	fsize=str(fsize*10)
	condense=get_pango_font_condense(fontdesc.get_stretch())
	fstyle=get_pango_font_style(fontdesc.get_style())
	#now reconstruct an XLFD compatible string and hope for the best
	fontval="-*-"+face+"-"+weight+"-"+fstyle+"-"+condense+"-*-*-"+fsize+"-*-*-p-*-"+str(ASSUME_CHARSET)
	return fontval.lower().strip()

def XLFD2pango(xlfd_str):
	mystr=xlfd_str
	# support legacy fonts like '-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*'
	# This should convert '-adobe-courier-medium-r-*-*-*-140-*-*-'
	# to something like "courier medium 14", it's imperfect but works for most fonts
	valls=mystr.split("-")
	if len(valls)<9: return mystr  # something odd or incomplete
	face=valls[2]
	weight="medium"
	if not valls[3]=="*": 
		weight=valls[3]
	fsize=valls[8][:2]  # shave off the trailing zero
	condense=""
	fstyle=""
	if valls[4]=="i": 
		fstyle=" italic "
	if valls[4]=="o": 
		fstyle=" oblique "
	if not valls[5]=="*": 
		if not valls[5].lower()=="normal":  
			if not valls[5].lower()=="regular":  
				condense=valls[5]+" "
	fontval=face+", "+weight+fstyle+" "+condense+fsize
	return fontval.lower().replace("  "," ").strip()


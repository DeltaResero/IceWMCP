#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

#######################################
# IceMe - Message Boxes
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
#  April 2003-February 2004
#  
#  This is a modified version of IceMe 
#  1.0.0 ("IceWMCP Edition"), optimized for 
#  IceWM ControlPanel. This is a modified 
#  version of the 'MessageBox.py" module 
#  from IceMe 1.0.0
#
#  Changes to the original IceMe message 
#  box code are noted throughout the 
#  source as comments.
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

from string import join

try:
	import sys
	sys.path=["/usr/lib/python2.2/site-packages/gtk-2.0"]+sys.path
except:
	pass


import gtk


ICON_STOP     = 4 # changed, 4.2.2003 - Erica Andrews, 'icon_stop' changed 
                  # from 1st to 5th list element

ICON_ALERT    = 1
ICON_INFO     = 2
ICON_QUESTION = 3
ICON_ERROR    = 4

# will be defined later by icewmcp_common, leave alone
icon_setter_method=None
pix_button_setter=None

class _MessageBox(gtk.Dialog):
    def __init__(self, 
                 title="Message", 
                 message="", 
                 buttons=("Ok",),
                 pixmap=ICON_INFO, 
                 modal=gtk.TRUE,
		 stock_icons=[]):
        """
        message: either a string or a list of strings
        pixmap: either a filename string, or one of: ICON_STOP, ICON_ALERT,
                ICON_INFO or ICON_QUESTION, or None

        """
        gtk.Dialog.__init__(self)
        self.set_title(title)
	if icon_setter_method:  icon_setter_method(self,icon_info)
        self.set_wmclass("icewmcontrolpanel","IceWMControlPanel") # added, 4.2.2003 - Erica Andrews
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)
        self.connect("key-press-event", self.__press)
        self.set_modal(gtk.TRUE)
        hbox = gtk.HBox(spacing=5)
        hbox.set_border_width(10)
        self.vbox.pack_start(hbox)
        hbox.show()
        if pixmap:
            self.realize()
            pic = gtk.Image()
	    selicon=pixmap
	    if type(selicon)==type(1): selicon=icons[pixmap]
            if type(selicon) == type(""):
		try:
                	pic.set_from_stock(selicon, gtk.ICON_SIZE_DIALOG)
		except:
			pic.set_from_file(selicon)
            else:
                p, m = gtk.gdk.pixmap_create_from_xpm_d(self.window, 
                                                        None, 
                                                        selicon)
                pic.set_from_pixmap(p, m)
            pic.set_alignment(0.5, 0.0)
            hbox.pack_start(pic, expand=gtk.FALSE)
            pic.show()
        if type(message) == type(""):
            label = gtk.Label(message)
        else:
            label = gtk.Label(join(message, "\n"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_line_wrap(1)  # added 4.4.2003 - for better readibility on low-res screens, Erica Andrews
        hbox.pack_start(label)
        label.show()
        if not buttons:
            buttons = ("Ok",)
        tips=gtk.Tooltips()
        use_stock=0
        if len(stock_icons)>0:
		if len(buttons)==len(stock_icons):
			if pix_button_setter: use_stock=1
	bcount=0
        for text in buttons:
	    if use_stock: b=pix_button_setter(None, stock_icons[bcount] , text)
            else : b = gtk.Button(text)
            tips.set_tip(b,text)
	    bcount=bcount+1
            if text == buttons[0]:
                # the first button will always be the default button:
                b.set_flags(gtk.CAN_FOCUS|gtk.CAN_DEFAULT|gtk.HAS_FOCUS|gtk.HAS_DEFAULT)
            b.set_flags(gtk.CAN_DEFAULT)
            b.set_data("user_data", text)
            b.connect("clicked", self.__click)
            self.action_area.pack_start(b)
            b.show()
        self.default = buttons[0]
        self.ret = None

    def quit(self, *args):
        self.hide()
        self.destroy()
        gtk.mainquit()

    def __click(self, button):
        self.ret = button.get_data("user_data")
        self.quit()

    def __press(self, widget, event):
        if event.keyval == gtk.keysyms.Return:
            self.ret = self.default
            self.quit()
#        elif event.keyval == gtk.keysyms.Escape:
#            self.quit()


def message(title="Message", message="", buttons=("Ok",),
            pixmap=ICON_INFO, modal=gtk.TRUE, stock_icons=[]):
    "create a message box, and return which button was pressed"
    win = _MessageBox(title, message, buttons, pixmap, modal, stock_icons)
    win.show()
    gtk.mainloop()
    return win.ret



# changed 4.2.2003 - Erica Andrews:  new icon colors
# We are now using stock icons for most dialogs (UGH! I caved)...but this icon is needed
# for the window icon on dialogs

icon_info = [
"32 32 127 2",
"   c opaque",
".  c #00001b",
"X  c #000030",
"o  c #002b66",
"O  c #004b9f",
"+  c #004ea6",
"@  c #0052ab",
"#  c #005cbc",
"$  c #1f72bd",
"%  c #005dc0",
"&  c #0062c3",
"*  c #006cca",
"=  c #0074cf",
"-  c #0876ce",
";  c #007bd3",
":  c #106ac5",
">  c #1775c3",
",  c #177bc6",
"<  c #177fc9",
"1  c #1a7ace",
"2  c #207dcf",
"3  c #2874c6",
"4  c #337dca",
"5  c #0681d5",
"6  c #0084d8",
"7  c #008add",
"8  c #0d8ddc",
"9  c #1d83c8",
"0  c #1394df",
"q  c #0093e2",
"w  c #238cca",
"e  c #2f85c0",
"r  c #2081d2",
"t  c #2b85d2",
"y  c #3384ce",
"u  c #3086d2",
"i  c #3d8bd4",
"p  c #3a95da",
"a  c #4189b8",
"s  c #4884b1",
"d  c #5284ac",
"f  c #5d81a4",
"g  c #408cd3",
"h  c #4a8cd2",
"j  c #4094d9",
"k  c #4d94d7",
"l  c #4899db",
"z  c #5296c0",
"x  c #5e99d7",
"c  c #54aee2",
"v  c #6c9bd0",
"b  c #7d9cc8",
"n  c #65a4dd",
"m  c #72a6dc",
"M  c #77a9dd",
"N  c #70b3d7",
"B  c #75ade0",
"V  c #75bde2",
"C  c #6dc6f1",
"Z  c #78c0ec",
"A  c #7dd2f6",
"S  c #8495b1",
"D  c #85aad4",
"F  c #8eb1d8",
"G  c #99a9c4",
"H  c #97badd",
"J  c #98b9dc",
"K  c #85b2e1",
"L  c #95bce5",
"P  c #9abfe6",
"I  c #a2aec3",
"U  c #a5b1c4",
"Y  c #a3bad8",
"T  c #aabcd5",
"R  c #aebedb",
"E  c #81c6e7",
"W  c #87ccef",
"Q  c #8ac0e0",
"!  c #8bc3ea",
"~  c #88cded",
"^  c #8fd1f3",
"/  c #9bc0e2",
"(  c #99d1ed",
")  c #b5c3dc",
"_  c #b9c6df",
"`  c #bcc9dd",
"'  c #a4c5e9",
"]  c #aecbeb",
"[  c #acd7f2",
"{  c #b5c5e0",
"}  c #b3cfec",
"|  c #bdcae2",
" . c #bfd7ef",
".. c #bfd9f0",
"X. c #bce8fa",
"o. c #c3cdde",
"O. c #c1cee4",
"+. c #c4d0e5",
"@. c #c4d1e8",
"#. c #ccd3e2",
"$. c #cad6ea",
"%. c #ced9ec",
"&. c #c2d8f0",
"*. c #cedaf0",
"=. c #d2d6e1",
"-. c #d4d9e3",
";. c #d2dcec",
":. c #d3def0",
">. c #d9e0ee",
",. c #d5e3f3",
"<. c #dbe4f4",
"1. c #dbe6f8",
"2. c #dce9f4",
"3. c #deeaf9",
"4. c #e5e7ed",
"5. c #eaeaee",
"6. c #e0e7f6",
"7. c #e1e9f6",
"8. c #e3ebf9",
"9. c #e9ecf0",
"0. c #e8eefb",
"q. c #ebf0f4",
"w. c #ebf1fc",
"e. c #f0f6fe",
"r. c #f4f9fe",
"t. c #fefeff",
"y. c None",
"y.y.y.y.y.y.y.+.o.+.+.+.+.+.+.+.+.+.+.+.+.+.G y.y.y.y.y.y.y.y.y.",
"y.y.y.y.y.y.y.+.r.t.t.t.t.t.t.t.t.t.r.w.7.<.O.U y.y.y.y.y.y.y.y.",
"y.y.y.y.y.y.y.+.t.t.t.t.t.t.t.t.t.r.e.w.7.;.O.w.I y.y.y.y.y.y.y.",
"y.y.y.y.y.y.y.+.t.t.t.t.t.t.t.t.t.t.r.w.8.<.O.e.3.I y.y.y.y.y.y.",
"y.y.y.y.y.y.y.+.t.t.t.t.t.t.t.t.t.t.t.e.w.<.O.t.0.1.I y.y.y.y.y.",
"y.y.y.y.y.y.y.+.t.t.t.t.t.t.t.t.t.t.r.e.w.2.O.t.t.w.3.U y.y.y.y.",
"y.y.y.y.y.y.y.+.t.t.t.t.t.t.t.t.t.t.t.r.w.8.| e.w.7.<.%.G y.y.y.",
"y.y.y.y.y.y.f T >.>.-.r.t.t.t.t.t.t.t.r.e.0.$.G G G G G G G y.y.",
"y.y.y.y.f z N ~ X.X.A V Z 2.t.t.t.t.t.r.r.0.0.7.:.O.) ) R S   y.",
"y.y.y.d ! 3.0.w.0.w.w.q.w.W ( t.t.t.t.t.r.0.8.7.$.| | | ) S   y.",
"y.y.a ! ,.,.,.,.w.w.2.,.1.,.[ C t.t.t.r.r.0.0.:.$.O.O.O.| S   y.",
"y.d c &.&.&.&.,.t.t.w...&.&.&.V ^ t.t.t.t.0.:.;.$.$.#.O.@.S   y.",
"f w ! ] ] ] ] &.t.t.w.] ] ] ] ] q 3.t.r.0.2.:.;.;.$.$.$.$.S   y.",
"s 7 / / P P P } t.t.0.! P P P P 0 c e.w.2.<.<.:.:.:.;.;.%.S   y.",
"e 7 B K K K K ' t.t.7.F F K K K 7 8 >.8.7.6.<.<.:.:.:.;.:.S   y.",
"9 6 p m m m m L t.t.2.m m m m l 6 6 / 8.8.8.7.6.6.1.:.<.,.S   y.",
"9 ; ; k x x v K t.t.,.x x v k ; 5 ; H 0.0.7.7.3.1.2.<.<.:.S   y.",
"< ; ; = t h g M t.t.,.h h u ; ; ; ; J 7.0.0.0.7.8.1.<.2.1.S   y.",
"> = = = = - 1 i 3.t.n 1 - = = = = = J 7.w.0.0.8.8.7.6.6.1.S   y.",
": = * = * = * * r j * * = = * = * * o.7.w.0.0.0.8.7.6.6.3.S   y.",
"$ * & * * * * 2 t.t.K * * * & * * y #.e.w.w.0.8.8.7.6.6.7.S   y.",
"f : & & & & & i t.t...& & * & & & F -.e.w.w.0.0.8.8.8.8.3.S   y.",
"y.# & # % & & : ]  .4 & & # # # 4 #.9.e.e.w.w.0.0.8.7.8.3.S   y.",
"y.y.@ % % % % % % % % % % % & 3 o.-.e.e.w.w.w.0.8.8.1.8.3.S   y.",
"y.y.y.+ # % % % # & % % % % 4 o.-.w.e.e.w.w.w.0.8.8.8.7.1.S   y.",
"y.y.y.X o + # % # # % % 3 D =.-.w.e.e.e.w.w.w.8.8.8.8.7.3.S   y.",
"y.y.y.y.y.. . b D v Y ` -.-.4.r.r.r.e.e.w.w.w.8.8.8.7.6.3.S   y.",
"y.y.y.y.y.y.  ` 5.5.4.9.q.r.r.r.r.e.e.e.w.w.0.0.8.7.8.6.3.S   y.",
"y.y.y.y.y.y.y.+.r.t.t.r.t.r.r.r.r.e.e.e.w.w.w.8.0.7.7.7.3.S   y.",
"y.y.y.y.y.y.y.+.S S S S S S S S S S S S S S S S S S S S S S   y.",
"y.y.y.y.y.y.y.y.                                              y.",
"y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y.y."
]


# changed, 4.2.2003 - Erica Andrews, added 'icon_stop' as 5th list element
icons = [ gtk.STOCK_STOP, gtk.STOCK_DIALOG_WARNING, gtk.STOCK_DIALOG_INFO, gtk.STOCK_DIALOG_QUESTION, gtk.STOCK_STOP ]



#############
# test case
#############

# changed 4.2.2003 - Erica Andrews:  'test' method now tests all 4 built-in icon types

if __name__ == "__main__":
    import pygtk
    pygtk.require("2.0")
    import gtk
    from gtk import *
    ret = message("Test MessageBox #1",
                  ["This is a test for the message box.", "", "Enjoy."], ('Ok',) ,2,1, [STOCK_OK])
    ret = message("Test MessageBox #1", 
                  ["This is a test for the message box.", "", "Enjoy."],
                  ("Ok",),ICON_STOP,gtk.FALSE)
    ret = message("Test MessageBox #1", 
                  ["This is a test for the message box.", "", "Enjoy."],
                  ("Ok",),ICON_ALERT,gtk.FALSE)
    ret = message("Test MessageBox #1", "America\n\nRich and\nPowerful".split("\n"),
                  ("Ok",),ICON_QUESTION,gtk.FALSE)
    print "ret:  "+str(message("Test","Sample\nMessage".split("\n"),("OK","Cancel",),3,1))






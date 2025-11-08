#! /usr/bin/env python

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

print_type=0

gicons= { 
		"STOCK_ADD" : STOCK_ADD,
		"STOCK_APPLY" : STOCK_APPLY,
		"STOCK_BOLD" : STOCK_BOLD,
		"STOCK_CANCEL" : STOCK_CANCEL,
		"STOCK_CDROM" : STOCK_CDROM,
		"STOCK_CLEAR" : STOCK_CLEAR,
		"STOCK_CLOSE" : STOCK_CLOSE,
		"STOCK_CONVERT" : STOCK_CONVERT,
		"STOCK_COPY" : STOCK_COPY,
		"STOCK_CUT" : STOCK_CUT,
		"STOCK_DELETE" : STOCK_DELETE,
		"STOCK_DIALOG_ERROR" : STOCK_DIALOG_ERROR,
		"STOCK_DIALOG_INFO" : STOCK_DIALOG_INFO,
		"STOCK_DIALOG_QUESTION" : STOCK_DIALOG_QUESTION,
		"STOCK_DIALOG_WARNING" : STOCK_DIALOG_WARNING,
		"STOCK_DND" : STOCK_DND,
		"STOCK_DND_MULTIPLE" : STOCK_DND_MULTIPLE,
		"STOCK_EXECUTE" : STOCK_EXECUTE,
		"STOCK_FIND" : STOCK_FIND,
		"STOCK_FIND_AND_REPLACE" : STOCK_FIND_AND_REPLACE,
		"STOCK_FLOPPY" : STOCK_FLOPPY,
		"STOCK_GOTO_BOTTOM" : STOCK_GOTO_BOTTOM,
		"STOCK_GOTO_FIRST" : STOCK_GOTO_FIRST,
		"STOCK_GOTO_LAST" : STOCK_GOTO_LAST,
		"STOCK_GOTO_TOP" : STOCK_GOTO_TOP,
		"STOCK_GO_BACK" : STOCK_GO_BACK,
		"STOCK_GO_DOWN" : STOCK_GO_DOWN,
		"STOCK_GO_FORWARD" : STOCK_GO_FORWARD,
		"STOCK_GO_UP" : STOCK_GO_UP,
		"STOCK_HELP" : STOCK_HELP,
		"STOCK_HOME" : STOCK_HOME,
		"STOCK_INDEX" : STOCK_INDEX,
		"STOCK_ITALIC" : STOCK_ITALIC,
		"STOCK_JUMP_TO" : STOCK_JUMP_TO,
		"STOCK_JUSTIFY_CENTER" : STOCK_JUSTIFY_CENTER,
		"STOCK_JUSTIFY_FILL" : STOCK_JUSTIFY_FILL,
		"STOCK_JUSTIFY_LEFT" : STOCK_JUSTIFY_LEFT,
		"STOCK_JUSTIFY_RIGHT" : STOCK_JUSTIFY_RIGHT,
		"STOCK_MISSING_IMAGE" : STOCK_MISSING_IMAGE,
		"STOCK_NEW" : STOCK_NEW,
		"STOCK_NO" : STOCK_NO,
		"STOCK_OK" : STOCK_OK,
		"STOCK_OPEN" : STOCK_OPEN,
		"STOCK_PASTE" : STOCK_PASTE,
		"STOCK_PREFERENCES" : STOCK_PREFERENCES,
		"STOCK_PRINT" : STOCK_PRINT,
		"STOCK_PRINT_PREVIEW" : STOCK_PRINT_PREVIEW,
		"STOCK_PROPERTIES" : STOCK_PROPERTIES,
		"STOCK_QUIT" : STOCK_QUIT,
		"STOCK_REDO" : STOCK_REDO,
		"STOCK_REFRESH" : STOCK_REFRESH,
		"STOCK_REMOVE" : STOCK_REMOVE,
		"STOCK_REVERT_TO_SAVED" : STOCK_REVERT_TO_SAVED,
		"STOCK_SAVE" : STOCK_SAVE,
		"STOCK_SAVE_AS" : STOCK_SAVE_AS,
		"STOCK_SELECT_COLOR" : STOCK_SELECT_COLOR,
		"STOCK_SELECT_FONT" : STOCK_SELECT_FONT,
		"STOCK_SORT_ASCENDING" : STOCK_SORT_ASCENDING,
		"STOCK_SORT_DESCENDING" : STOCK_SORT_DESCENDING,
		"STOCK_SPELL_CHECK" : STOCK_SPELL_CHECK,
		"STOCK_STOP" : STOCK_STOP,
		"STOCK_STRIKETHROUGH" : STOCK_STRIKETHROUGH,
		"STOCK_UNDELETE" : STOCK_UNDELETE,
		"STOCK_UNDERLINE" : STOCK_UNDERLINE,
		"STOCK_UNDO" : STOCK_UNDO,
		"STOCK_YES" : STOCK_YES,
		"STOCK_ZOOM_100" : STOCK_ZOOM_100,
		"STOCK_ZOOM_FIT" : STOCK_ZOOM_FIT,
		"STOCK_ZOOM_IN" : STOCK_ZOOM_IN,
		"STOCK_ZOOM_OUT" : STOCK_ZOOM_OUT,
 }


class controlwin:
    def __init__(self) :
	controlwin=Window(WINDOW_TOPLEVEL)
	controlwin.set_title("Icons")
	controlwin.set_position(WIN_POS_CENTER)
	controlwin.realize()
	mainvbox=VBox(0,1)
	mainvbox.set_spacing(0)
	sc=ScrolledWindow()
	glayout=Layout()
	self.glayout=glayout
	self.sc=sc
	sc.add(glayout)
	mainvbox.pack_start(sc,1,1,0)
	mainvbox.set_border_width(3)
	controlwin.add(mainvbox)
	controlwin.connect("destroy",self.doQuit)
	self.loadIcons()
	controlwin.set_size_request(450,395)
	controlwin.show_all()

    def doQuit(self,*args) :
	gtk.mainquit()

    def loadIcons(self,*args) :
	a_list=gicons.keys()
	a_list.sort()
	movex=3
	movey=3
	for ii in a_list:
		b=Button()
		clbox=HBox(0,0)
		clbox.set_spacing(3)
		clbox.set_border_width(2)
		bimage=Image()
		blab=Label(ii)
		bimage.set_from_stock(gicons[ii],ICON_SIZE_BUTTON)
		if print_type==1: print str(gicons[ii])
		clbox.pack_start(bimage,0,0,0)
		clbox.pack_start(Label("  "),0,0,0)
		clbox.pack_start(blab,0,0,0)
		clbox.pack_start(Label(" "),1,1,0)
		b.add(clbox)
		b.show_all()
		self.glayout.put(b,movex,movey)
		movey=movey+45
	self.glayout.set_size(400,movey+50)
	

def run() :
	controlwin()
	gtk.mainloop()

if __name__== "__main__" :
	run()

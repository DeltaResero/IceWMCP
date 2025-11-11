#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

######################################
# IceWM Control Panel Wallpaper Settings
# 
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
# 
# A simple Gtk-based utility for setting the background 
# color and wallpaper settings in IceWM (written in 100% 
# Python).
# 
# This program is distributed under the GNU General
# Public License (open source).
# 
# WARNING: Some newer IceWM themes override the wallpaper 
# and background colors set here. If you see no changes, it 
# may be that your theme controls the background colors 
# and images.
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

import math
from string import atoi

#set translation support
from .icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py


# import drag-n-drop support, 5.16.2003
from . import icewmcp_dnd
from .icewmcp_dnd import *
initColorDrag()      # enable dnd support for 'color buttons'
addDragSupportColor=icewmcp_dnd.addDragSupportColor

class wallwin:
    def __init__(self) :
	self.colvalue="rgb:fb/f9/f5"
	self.dirvalue=""
	self.preffile=""
	self.imvalue=""
	self.version=this_software_version
	self.imlist=[".gif",".png",".jpeg",".jpe",".bmp",".xpm",".xbm",".ppm",".dib",".pnm",".tiff",".tif",".jpg",".ps"]
	global WMCLASS
	WMCLASS="icewmcontrolpanelwallpaper"
	global WMNAME
	WMNAME="IceWMControlPanelWallpaper"
	wallwin=Window(WINDOW_TOPLEVEL)
	wallwin.set_wmclass(WMCLASS,WMNAME)
	set_basic_window_icon(wallwin)
	wallwin.realize()
	wallwin.set_title("IceWM CP - "+_("Wallpaper Settings")+" "+self.version)
	wallwin.set_position(WIN_POS_CENTER)
	self.wallwin=wallwin

	menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
 				(_("/_File")+"/_"+FILE_RUN,'<control>R', rundlg,421,""),
  				(_("/_File")+"/_"+_("Check for newer versions of this program..."), '<control>U', checkSoftUpdate,420,""),
				(_('/File/sep1'), None, None, 1, '<Separator>'),
				(_('/File/_Apply Changes Now...'), '<control>A', self.restart_ice, 0, ''),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
				(_('/File/_Exit'), '<control>Q', self.doQuit, 0, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About...'), "F2", self.about_cb, 0, ''),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5003, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5003, ""),
					]

	ag = AccelGroup()
	itemf = ItemFactory(MenuBar, '<main>', ag)
	self.ag=ag
	self.itemf=itemf
	wallwin.add_accel_group(ag)
	itemf.create_items(menu_items)
	self.menubar = itemf.get_widget('<main>')

	# added 6.21.2003 - "run as root" menu selector
	self.leftmenu=self.menubar.get_children()[0].get_submenu()
	self.run_root_button=CheckMenuItem(" "+RUN_AS_ROOT)
	self.leftmenu.prepend(self.run_root_button)
	self.run_root_button.connect("toggled",self.run_as_root)

	mainvbox1=VBox(0,1)
	mainvbox=VBox(0,1)
	mainvbox1.pack_start(self.menubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,0)
	self.menubar.show()
	mainvbox.set_border_width(4)
	mainvbox.set_spacing(2)
	mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png",DIALOG_TITLE),0,0,2)
	mainvbox.pack_start(Label(" "+_("Wallpaper Settings")+" "),0,0,3)	

	#color box
	topbox=HBox(0,0)

	colbox=HBox(0,0)
	colbox.set_spacing(10)
	colbox.set_border_width(3)
	colframe=Frame()
	colframe.set_label(_(" Desktop Color "))
	self.colentry=Entry()
	self.colentry.connect("key-press-event",self.enter_on_color_choose_cb)
	TIPS.set_tip(self.colentry,_(" Desktop Color ").strip())
	self.colbutton=ColorButton(self.selectcol,self.colentry)
	TIPS.set_tip(self.colbutton,_(" Change... ").strip())
	self.colchooser=getIconButton(None,STOCK_OPEN,_(" Change... ").strip())
	addDragSupportColor(self.colchooser)
	self.colchooser.set_data("colorbutton",self.colbutton)
	addDragSupportColor(self.colentry)
	self.colentry.set_data("colorbutton",self.colbutton)
	self.colchooser.connect("clicked",self.selectcol)
	TIPS.set_tip(self.colchooser,_(" Change... ").strip())
	colbox.pack_start(self.colentry,1,1,0)	
	colbox.pack_start(self.colbutton,0,0,0)	
	colbox.pack_start(self.colchooser,0,0,0)	
	colbox.show_all()
	colframe.add(colbox)
	colframe.show_all()
	topbox.pack_start(colframe,0,0,0)	
	topbox.pack_start(Label("   "),0,0,0)	
	mainvbox.pack_start(topbox,0,0,0)

	#imabe box
	imbox=HBox(0,0)
	imbox.set_spacing(10)
	imbox.set_border_width(3)
	imframe=Frame()
	imframe.set_label(_(" Image "))

	leftbox=VBox(0,0)
	leftbox.set_spacing(3)
	self.sc=ScrolledWindow()
	self.clist=CList(1)
	self.clist.set_column_width(0,395)
	self.clist.connect('select_row', self.clist_cb)
	self.clist.set_size_request(215,-1)
	self.sc.add(self.clist)
	leftbox.pack_start(self.sc,1,1,0)
	reloadbutt=getPixmapButton(None, STOCK_REFRESH ,_(" Reload Images ").strip())
	TIPS.set_tip(reloadbutt,_(" Reload Images ").strip())
	reloadbutt.connect("clicked",self.reloadImages)
	leftbox.pack_start(reloadbutt,0,0,0)
	imbox.pack_start(leftbox,0,0,0)
	leftbox.show_all()

	rightbox=VBox(0,0)
	rightbox.set_spacing(2)

	dirbox=HBox(0,0)
	dirbox.set_spacing(10)
	dirbox.set_border_width(3)
	dirframe=Frame()
	dirframe.set_label(_(" Directory "))
	self.direntry=Entry()
	self.direntry.connect("key-press-event",self.enter_on_dir_choose_cb)
	TIPS.set_tip(self.direntry,_(" Directory ").strip())
	addDragSupport(self.direntry,self.setDrag) # drag-n-drop support, added 2.23.2003
	try:
		self.direntry.set_text(os.environ['HOME']+os.sep)
		self.preffile=getIceWMPrivConfigPath()+"preferences"
	except:
		pass
	self.dirchooser=getIconButton(None,STOCK_OPEN,_(" Select... "))
	TIPS.set_tip(self.dirchooser,_(" Select... ").strip())
	self.dirchooser.connect("clicked",self.selectfile)
	addDragSupport(self.dirchooser,self.setDrag) # drag-n-drop support, added 2.23.2003
	dirbox.pack_start(self.direntry,1,1,0)	
	dirbox.pack_start(self.dirchooser,0,0,0)	
	dirbox.show_all()
	dirframe.add(dirbox)
	dirframe.show()
	topbox.pack_start(dirframe,1,1,0)

	checkbox=HBox(0,0)
	checkbox.set_spacing(18)
	checkbox.set_border_width(2)
	self.checkbutton=RadioButton(None,_(" Centered "))	
	self.checkbutton2=RadioButton(self.checkbutton,_(" Tiled "))

	self.checkbutton36=CheckButton(_(" Scaled "))
	TIPS.set_tip(self.checkbutton36,_(" Scaled ").strip())

	TIPS.set_tip(self.checkbutton,_(" Centered ").strip())
	TIPS.set_tip(self.checkbutton2,_(" Tiled ").strip())
	checkbox.pack_start(self.checkbutton,0,0,0)
	checkbox.pack_start(self.checkbutton2,0,0,0)
	checkbox.pack_start(self.checkbutton36,0,0,0)
	checkbox.pack_start(Label(" "),1,1,0)
	edbutton=getPixmapButton(None, STOCK_SELECT_COLOR ,_("Edit"))
	TIPS.set_tip(edbutton,_("Edit with Gimp"))
	edbutton.connect("clicked",self.editWall)
	checkbox.pack_start(edbutton,0,0,0)
	rightbox.pack_start(checkbox,0,0,1)

	prevtable = Table (3, 3, 0)
	prevtabbox=HBox(0,0)
	prevtabbox.pack_start(Label(" "),1,1,0)
	sclay=Layout()
	self.gl=sclay
	self.cutoff1=356  #314
	self.cutoff2=267
	sclay.set_size_request( self.cutoff1,self.cutoff2)
	# top row
	prevtable.attach( Label(""), 0, 1, 0, 1, (EXPAND+FILL), (0), 0, 0)

	try:
		prevtable.attach( loadScaledImage(getPixDir()+"monitor_top1.png",411,22), 1, 2, 0, 1, (), (0), 0, 0)
	except:
		prevtable.attach( Label(""), 1, 2, 0, 1, (EXPAND+FILL), (0), 0, 0)

	prevtable.attach( Label(""), 2, 3, 0, 1, (EXPAND+FILL), (0), 0, 0)

	# middle row
	middlebox=HBox(0,0)
	prevtable.attach( Label(""), 0, 1, 1, 2, (EXPAND+FILL), (0), 0, 0)
	prevtable.attach( middlebox, 1, 2, 1, 2, (EXPAND+FILL), (0), 0, 0)
	prevtable.attach( Label(""), 2, 3, 1, 2, (EXPAND+FILL), (0), 0, 0)
	try:
		middlebox.pack_start( loadScaledImage(getPixDir()+"monitor_left1.png",27,268), 0, 0, 0)
	except:
		middlebox.pack_start( Label(""), 0, 0,0)

	evbox=EventBox()
	addDragSupport(sclay,self.setDrag)
	evbox.add(sclay)
	middlebox.pack_start( evbox, 1, 1, 0)

	try:
		middlebox.pack_start(loadScaledImage(getPixDir()+"monitor_right1.png",27,268), 0, 0, 0)
	except:
		middlebox.pack_start( Label(""), 0, 0, 0)


	# bottom row
	prevtable.attach( Label(""), 0, 1, 2, 3, (EXPAND+FILL), (0), 0, 0)
	try:
		prevtable.attach( loadScaledImage(getPixDir()+"monitor_bottom1.png",411,29), 1, 2, 2, 3, (), (0), 0, 0)
	except:
		prevtable.attach( Label(""), 1, 2, 2, 3, (EXPAND+FILL), (0), 0, 0)
	prevtable.attach( Label(""), 2, 3, 2, 3, (EXPAND+FILL), (0), 0, 0)


	prevtabbox.pack_start(prevtable,0,0,0)
	prevtabbox.pack_start(Label(" "),1,1,0)
	rightbox.pack_start(prevtabbox,1,1,0)

	imbox.pack_start(rightbox,1,1,0)
	rightbox.show_all()

	imbox.show_all()
	imframe.add(imbox)
	imframe.show_all()
	mainvbox.pack_start(imframe,1,1,0)
	self.status=Label("  ")
	mainvbox.pack_start(self.status,0,0,2)
	buttonbox=HBox(0,0)
	buttonbox.set_homogeneous(1)
	buttonbox.set_spacing(4)
	okbutt=getPixmapButton(None, STOCK_OK ,_("Ok"))
	applybutt=getPixmapButton(None, STOCK_APPLY ,_("Apply"))
	cancelbutt=getPixmapButton(None, STOCK_QUIT ,_("Close"))
	TIPS.set_tip(okbutt,_("Ok"))
	TIPS.set_tip(applybutt,_("Apply"))
	TIPS.set_tip(cancelbutt,_("Close"))
	buttonbox.pack_start(okbutt,1,1,0)
	buttonbox.pack_start(applybutt,1,1,0)
	buttonbox.pack_start(cancelbutt,1,1,0)

	okbutt.connect("clicked",self.ok_quit)
	applybutt.connect("clicked",self.restart_ice)
	cancelbutt.connect("clicked",self.doQuit)
	mainvbox.pack_start(buttonbox,0,0,0)

	wallwin.add(mainvbox1)
	wallwin.connect("destroy",self.doQuit)
	#wallwin.set_default_size(690, -1)
	self.checkbutton.set_active(1)
	self.set_prefs()
	self.reloadImages()
	self.displayImage()
	self.checkbutton.connect("toggled",self.displayImage)
	self.checkbutton36.connect("toggled",self.displayImage)
	wallwin.show_all()


    def run_as_root(self,*args):
	# added 6.21.2003 - 'Run as Root' functionality
	if self.run_root_button.get_active():
		self.preffile=getIceWMConfigPath()+"preferences"
		self.wallwin.set_title("IceWM CP - "+_("Wallpaper Settings")+" "+self.version+"   [ROOT]")
		status_stuff= "[ROOT]    "+str(self.preffile)
	else:
		self.preffile=getIceWMPrivConfigPath()+"preferences"
		self.wallwin.set_title("IceWM CP - "+_("Wallpaper Settings")+" "+self.version)
		status_stuff= str(self.preffile)
	self.menubar.deactivate()
	self.set_prefs()
	self.reloadImages()
	self.displayImage()
	if len(status_stuff)>55: status_stuff=status_stuff[:54]+"..."
	self.status.set_text(status_stuff)


    def setDrag(self,*args): # drag-n-drop support, added 2.23.2003
	drago=args
	if len(drago)<7: 
		args[0].drag_highlight()
		args[0].grab_focus()
	else: 
		#print str(drago[4].data)  # file:/root/something.txt
		try:
			imfile=""+str(drago[4].data).replace("\r\n","").replace("\x00","").replace("file:","").strip()
			imf=imfile[imfile.rfind(os.sep)+1:len(imfile)].strip()
			imdir=imfile[0:imfile.rfind(os.sep)+1].strip()
			self.direntry.set_text(imdir)
			self.imvalue=imfile
			self.displayImage()
			self.reloadImages()
		except: 
			pass
		args[0].drag_unhighlight()

    def about_cb(self,*args) :
		commonAbout(_("Wallpaper Settings")+" "+self.version,  DIALOG_TITLE+": "+_("Wallpaper Settings")+" "+self.version+"\n\n"+_("A simple Gtk-based utility for setting the background color\nand wallpaper settings in IceWM (written in 100% Python).\nThis program is distributed under the GNU General\nPublic License (open source).\n\nWARNING: Some newer IceWM themes override the wallpaper and\nbackground colors set here. If you see no changes, it may be that your\ntheme controls the background colors and images."))

    def ok_quit(self,*args) :
	self.restart_ice()
	self.doQuit()

    def parse_icewm_version(self,*args) :  # added 12.11.2003
      try:
	iversion="IceWM 0.0.0,"
	if get_pidof("icewm"): 
		iversion=os.popen("icewm --version").read().replace("\n","").replace("\t","")
	if get_pidof("icewm-gnome"): 
		iversion=os.popen("icewm-gnome --version").read().replace("\n","").replace("\t","")
	if iversion.find(",")>iversion.find("IceWM"):
		iversion=iversion[iversion.find("IceWM")+len("IceWM"):iversion.find(",")].strip()
		ivers=iversion.split(".")
		vers=[]
		for ii in ivers:
			myint=""
			for gg in ii:
				if not gg.isdigit(): break
				myint=myint+gg
			vers.append(int(myint))
		if len(vers)==3: return vers
		else: return [0,0,0]
	else: return [0,0,0]
      except:
	pass


    def restart_ice(self,*args) :
	i=self.save_prefs()
	if i==1:
		# changed, 12.11.2003, we can set the background without restarting IceWM for 
		# versions of IceWM of 1.2.11 and above
		old_restart=1
		icewm_vers=self.parse_icewm_version()
		if not len(icewm_vers)==3: icewm_vers=[0,0,0]
		if icewm_vers[0] >= 1:
			if icewm_vers[1] >= 2:
				if icewm_vers[2] >= 11:
					old_restart=0
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		if old_restart==1: # IceWM 1.2.10 and below, also unknown versions
			if get_pidof("icewm"): 
				fork_process("killall -HUP -q icewm")
			if get_pidof("icewm-gnome"): 
				fork_process("killall -HUP -q icewm-gnome")

		# The rest of this should have no effecton lower versions of IceWM
		# added  8.14.2003, needed by IceWM 1.2.10 and above
		if not get_pidof("icewmbg"): 
			fork_process("icewmbg")
		else: 
			fork_process("killall -HUP -q icewmbg") # slightly older versions, and newer versions
			# os.system('icewmbg -r')  # newer versions, questionable, doesnt work consistently
		if not get_pidof("icewmbg"): 
			fork_process("icewmbg")
	
    def save_prefs(self,*args) :
	g=self.get_prefs()
	try: # make a backup of the preferences file
		os.popen("cp -f "+self.preffile+" "+self.preffile+".backup-file")
	except:
		msg_err(DIALOG_TITLE,_("Error backing up IceWM preferences to:\n")+self.preffile+".backup-file")
		return 0

	try:
		b_write=0
		bc_write=0
		wc_write=0
		ws_write=0
		b="DesktopBackgroundImage=\""+self.imvalue+"\""
		if (len(self.imvalue)==0) or (self.imvalue=="[NONE]"):
			b="#"+b
		bc="DesktopBackgroundColor=\""+self.colentry.get_text().strip()+"\""
		if len(bc)==0: bc="DesktopBackgroundColor=\"rgb:FF/FF/FF\""
		wc="DesktopBackgroundCenter="+str(int(self.checkbutton.get_active()))
		ws="DesktopBackgroundScaled="+str(int(self.checkbutton36.get_active()))
		f=open(self.preffile,"w")
		for ii in g:
			if ii.find("DesktopBackgroundImage=")>-1:
				f.write(b+"\n")
				b_write=1
			elif ii.find("DesktopBackgroundColor=")>-1:
				f.write(bc+"\n")
				bc_write=1
			elif ii.find("DesktopBackgroundScaled=")>-1:
				f.write(ws+"\n")
				ws_write=1
			elif ii.find("DesktopBackgroundCenter=")>-1:
				f.write(wc+"\n")
				wc_write=1
			else:
				f.write(ii+"\n")
		if b_write==0: f.write(b+"\n")
		if bc_write==0: f.write(bc+"\n")
		if wc_write==0: f.write(wc+"\n")
		if ws_write==0: f.write(ws+"\n")
		f.flush()
		f.close()
	except:
		msg_err(DIALOG_TITLE,_("Error while saving IceWM preferences to:\n")+self.preffile)
		return 0
	return 1


    def set_prefs(self,*args) :
	g=self.get_prefs()
	cent="1"
	cent2="0"
	for ii in g:
		if ii.find("DesktopBackgroundImage=")>-1:
			while ii.strip().find("#")>5:
				ii=ii[0:ii.rfind("#")].strip()
			self.imvalue=ii.replace("#","").replace("DesktopBackgroundImage=","").replace("\"","").strip()
		if ii.find("DesktopBackgroundColor=")>-1:
			while ii.strip().find("#")>5:
				ii=ii[0:ii.rfind("#")].strip()
			self.colvalue=ii.replace("#","").replace("DesktopBackgroundColor=","").replace("\"","").strip()
		if ii.find("DesktopBackgroundCenter=")>-1:
			while ii.strip().find("#")>5:
				ii=ii[0:ii.rfind("#")].strip()
			cent=ii.replace("#","").replace("DesktopBackgroundCenter=","").replace("\"","").strip()
		if ii.find("DesktopBackgroundScaled=")>-1:
			while ii.strip().find("#")>5:
				ii=ii[0:ii.rfind("#")].strip()
			cent2=ii.replace("#","").replace("DesktopBackgroundScaled=","").replace("\"","").strip()
	#self.checkbutton.set_active(str(cent)=="1")
	#print cent
	self.checkbutton2.set_active(str(cent)=="0")
	self.checkbutton36.set_active(str(cent2)=="1")
	self.colentry.set_text(self.colvalue)
	self.colbutton.set_value(self.colvalue)
	if self.imvalue.find(os.sep)>-1:
		self.dirvalue=self.imvalue[0:self.imvalue.rfind(os.sep)+1]
		self.direntry.set_text(self.dirvalue)

    def get_prefs(self,*args) :
	try:
		f=open(self.preffile)
		ff=f.read().split("\n")
		f.close()
		return ff
	except:
		pass
	try: # this happens if we got an empty prefs file - try system prefs
		f=open(getIceWMConfigPath()+"preferences")
		ff=f.read().split("\n")
		f.close()
		return ff
	except:
		pass
	return []

    def doQuit(self,*args) :
	gtk.mainquit()

    def update_desktop_color(self,*args):
		# added 12.3.2003, we can now preview the background color under the wallpaper!
		colvalue = self.colentry.get_text().strip()
		if colvalue != '':
			try:
				r=g=b=0
            			r = atoi(colvalue[4:6], 16) << 8
            			g = atoi(colvalue[7:9], 16) << 8
            			b = atoi(colvalue[10:12], 16) << 8
				colour = self.gl.get_colormap().alloc_color(r, g, b)
				for gg in [STATE_NORMAL, STATE_ACTIVE, STATE_PRELIGHT,
					STATE_SELECTED, STATE_INSENSITIVE]:
					self.gl.modify_bg(gg,colour)
				# make sure colors stay synchronized
				self.colbutton.ok((r >> 8,g >> 8,b >> 8,))
			except:
				pass

    def selectcol(self, *args):
		colvalue = self.colentry.get_text().strip()
		self.colwin = ColorSelectionDialog(_('Select Color'))
		set_basic_window_icon(self.colwin)
		self.colwin.set_position(WIN_POS_CENTER)
		self.colwin.ok_button.connect('clicked', self.colok)
		self.colwin.cancel_button.connect('clicked', self.colcancel)
		self.colwin.help_button.destroy()
		if colvalue != '':
			r=g=b=0
			try:
            			r = atoi(colvalue[4:6], 16) << 8
            			g = atoi(colvalue[7:9], 16) << 8
            			b = atoi(colvalue[10:12], 16) << 8
			except:
				pass
            		colour = self.colwin.get_colormap().alloc_color(r, g, b)
            		self.colwin.colorsel.set_current_color(colour)
			self.colvalue=colvalue
		self.colwin.set_modal(TRUE)
		self.colwin.show()

    def colcancel(self,*args):
		self.colwin.destroy()
		self.colwin.unmap()
    def colok(self, *args):
		colour = self.colwin.colorsel.get_current_color()
        	r = colour.red   >> 8
        	g = colour.green >> 8
        	b = colour.blue  >> 8
		rstr="%02x" % r
		gstr="%02x" % g
		bstr="%02x" % b			
		self.colvalue = "rgb:"+rstr+"/"+gstr+"/"+bstr
		self.colentry.set_text(self.colvalue)
		self.colbutton.ok((r,g,b,))
		self.update_desktop_color()
		self.colwin.hide()
		self.colwin.destroy()
		self.colwin.unmap()

    def selectfile(self, *args):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		value = self.direntry.get_text().strip()
		if value != '""':
			SET_SELECTED_FILE(value)
		SELECT_A_FILE(self.fileok)
		
    def fileok(self, *args):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		self.dirvalue=GET_SELECTED_FILE()   # from icewmcp_common
		if self.dirvalue.find(os.sep)>-1:
			self.dirvalue=self.dirvalue[0:self.dirvalue.rfind(os.sep)+1]
		self.direntry.set_text(self.dirvalue)
		self.reloadImages()
		self.wallwin.set_title("IceWM CP - "+_("Wallpaper Settings")+" "+self.version)

    def enter_on_dir_choose_cb(self, widget, event,*args):
		if event.keyval == gtk.keysyms.Return:
			self.reloadImages()

    def enter_on_color_choose_cb(self, widget, event,*args):
	if event.keyval == gtk.keysyms.Return:		
		colvalue = self.colentry.get_text().strip()
		if colvalue != '':			
			try:
				r=g=b=0
            			r = atoi(colvalue[4:6], 16) 
            			g = atoi(colvalue[7:9], 16) 
            			b = atoi(colvalue[10:12], 16) 
				rstr="%02x" % r
				gstr="%02x" % g
				bstr="%02x" % b			
				self.colvalue = "rgb:"+rstr+"/"+gstr+"/"+bstr
				self.colentry.set_text(self.colvalue)
				self.colbutton.ok((r,g,b,))
				self.update_desktop_color()
			except:
				pass

    def editWall(self, *args):  # added 5.10.2003, feature to launch Gimp for editing
	if self.imvalue==None: return
	if self.imvalue=='': return
	#   changed 12.19.2003 - use common Bash shell probing
	#   to fix BUG NUMBER: 1523884
	#   Reported By: david ['-at-'] jetnet.co.uk
	#   Reported At: Fri Oct 31 23:47:12 2003
	fork_process("gimp-remote -n "+str(self.imvalue).replace(" ","\\ "))

    def clist_cb(self, widget, row, col, event):
	self.imvalue = widget.get_row_data(row)
	self.status.set_text(self.imvalue[self.imvalue.rfind(os.sep)+1:len(self.imvalue)])
	self.displayImage()

    def displayImage(self,*args):
	if not len(self.imvalue)>0: return
	if self.checkbutton.get_active(): self.update_image(self.imvalue,0)
	else: self.update_image(self.imvalue,1)
	self.update_desktop_color()
	
    def reloadImages(self, *args):
	self.clist.freeze()
	self.clist.clear()
	self.clist.append(["[NONE]"])
	self.clist.set_row_data(0,"[NONE]")
	selrow=0
	try:
		d=self.direntry.get_text().strip()
		if not d.endswith(os.sep): d=d+os.sep
		plist=os.listdir(d)
		usable=[]
		for ii in plist:
			if not os.path.isdir(d+ii):
				ifile=ii
				for yy in self.imlist:
					if ifile.lower().find(yy)>-1:
						usable.append(ifile)
						break
		usable.sort()
		inum=1
		for ii in usable:
			self.clist.append([ii])
			self.clist.set_row_data(inum,d+ii)
			if str(d+ii)==self.imvalue: selrow=inum
			inum=inum+1
	except:
		pass
	self.selrow=selrow
	self.clist.thaw()	
	self.jumpInList()

    def jumpInList(self, *args):
	try:
		self.clist.select_row(self.selrow,0)
		self.clist.moveto(self.selrow,0,0,0)
	except:
		pass

    def update_image(self,image_file,tile=0):
		for ii in self.gl.get_children():
			try:
				self.gl.remove(ii)
				ii.destroy()
				ii.unmap()
			except:
				pass
		try:			
			stats=image_file[image_file.rfind(os.sep)+1:len(image_file)]

			# Note, we could use a combination of loadImage and loadScaledImage here
			# But, that would lead to the image file having to be read TWICE, a slow-down
			# so we are by-passing the 'common' image loading methods

			# create temporary pixmap to check its size
			pixtemp=GDK.pixbuf_new_from_file(str(image_file).strip())
			dims=[pixtemp.get_width(), pixtemp.get_height()]
			cutoff1=self.cutoff1
			cutoff2=self.cutoff2
			aspect=float(dims[0])/float(dims[1])
			sug_x=cutoff1

			# This feature tries to make the 'preview' monitor emulate the typical resolution 
			# on the user's computer, using gtk's screen_width() and screen_height()

			# float scale_aspect comes from  cutoff1/1024: reduce images and pretend to 
			#  be a  1024x768 screen if the image is smaller than the screen width 
			# Gtk reports

			scale_aspect=float(cutoff1/1024.00000)
			if dims[0]<GDK.screen_height(): sug_x=int( math.floor(float(dims[0]*scale_aspect ) ))
			else:
				if tile==1:
					if dims[0]<GDK.screen_height(): sug_x=int( math.floor(sug_x*scale_aspect)  )
					else:
						stats=stats+"  ("+_("Too large to tile")+")" 
			
			#print "sug_x:  "+str(sug_x)
			sug_y=int( math.floor( sug_x/aspect)   ) 
			scale_aspect_y=float(float(1024/768.000) / float(cutoff1/(cutoff2*1.0000))  )
			#print str(scale_aspect_y) 
			sug_y= int( math.ceil(sug_y * scale_aspect_y)  )
			#print str(sug_y)
			if self.checkbutton36.get_active():
				sug_x=cutoff1
				sug_y=cutoff2
			xput=0
			yput=0
			xlim=sug_x
			ylim=sug_y
			if tile==1:
				xlim=cutoff1
				ylim=cutoff2

			if not tile:
				if not self.checkbutton36.get_active():  # regular centered, non-scaled
					xput=(cutoff1/2)-(sug_x/2)
					yput=(cutoff2/2)-(sug_y/2)
					#print "XPUTS: "+str(cutoff1)+"   "+str(sug_x)
					#print "YPUTS: "+str(cutoff2)+"   "+str(sug_y)
					#print "PUTS: "+str(xput)+"   "+str(yput)
					if yput<0: yput=0
					if xput<0: xput=0
					xlim=cutoff1
					ylim=cutoff2

			while yput<ylim:
				if xput>=xlim: 
					xput=0
					yput=yput+sug_y
        			img2 = pixtemp.scale_simple( sug_x,sug_y,GDK.INTERP_BILINEAR)
        			pix,mask = img2.render_pixmap_and_mask()
       				pixreal = gtk.Image()
        			pixreal.set_from_pixmap(pix, mask)
        			pixreal.show()
				TIPS.set_tip(pixreal,str(image_file).strip())
				self.gl.put(pixreal,xput,yput)
				if tile==0: break
				xput=xput+sug_x
			del pixtemp  # clear this obj. from memory just to be safe
			stats=stats+"   ["+str(dims[0])+" x "+str(dims[1])+"]"
			self.status.set_text(stats)
		except:
			lab=Label(" "+_("SORRY:\n Image could not\n be previewed."))
			TIPS.set_tip(lab,str(image_file).strip())
			lab.show()
			self.gl.put(lab,2,2)
		TIPS.set_tip(self.gl,str(image_file).strip())


class ColorButton(Button):
	def __init__(self,select_method,col_entry):
		Button.__init__(self)
		self.colentry=col_entry
		self.set_relief(2)
		self.connect('clicked',select_method)
		self.gc=None
		self.color_i16=[0,0,0]
		f=Frame()
		f.set_shadow_type(SHADOW_ETCHED_OUT)
		drawing_area = DrawingArea()
		drawing_area.set_size_request(22, 18)
		drawing_area.show() 
		self.drawing_area=drawing_area
		f.add(drawing_area)
		self.drawwin=drawing_area.window
		drawing_area.connect("expose_event", self.setColor)
		drawing_area.set_events(GDK.EXPOSURE_MASK |
		GDK.LEAVE_NOTIFY_MASK |
		GDK.BUTTON_PRESS_MASK )
		self.add(f)
		self.set_data("colorbutton",self)  # added 5.16.2003
		addDragSupportColor(self)  # added 5.16.2003
		self.show_all()

	def setColor(self,*args):
	  try:
        	if not self.drawwin: self.drawwin=self.drawing_area.window
       		if not self.gc: self.gc=self.drawwin.new_gc()
       		self.gc.foreground=self.drawwin.get_colormap().alloc_color(self.color_i16[0] << 8,
                                                                   self.color_i16[1] << 8,
                                                                   self.color_i16[2] << 8)
        	width, height = self.drawwin.get_size()
        	self.drawwin.draw_rectangle(self.gc,gtk.TRUE,0,0,width,height)
	  except:
		pass
	

	def updateColorProperties(self, r, g, b): # new method,functionality separation, 5.16.2003
        	self.color_i16=[r,g,b]
		rstr="%02x" % r
		gstr="%02x" % g
		bstr="%02x" % b		
		self.colentry.set_text("rgb:"+rstr+"/"+gstr+"/"+bstr)
		self.setColor()
	
	def ok(self, raw_values):
		r,g,b = raw_values
		self.updateColorProperties(r,g,b)

	def set_value(self, value):
		# make allowances for HTML-style color specs
		value=value.lower().replace("\"","").replace("'","").replace("/","").replace("rgb:","").replace(" ","").replace("#","").strip()
		if not len(value)==6: 
			return
		hvalue=""+value
		value="rgb:"+ hvalue[0:2]+"/"+hvalue[2:4]+ "/"  +hvalue[4:6]
		r,g,b=getRGBForHex(hvalue)		
		self.color_i16=[r/255.0,g/255.0,b/255.0]
		try:
			self.setColor()
		except:
			pass


def run() :
	wallwin()
	hideSplash()
	gtk.mainloop()

if __name__== "__main__" :
	run()

#! /usr/bin/env python

#############################
#  IceWM Control Panel - Window Options 
#  
#  Copyright 2003 by Erica Andrews
#  PhrozenSmoke@yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  A simple Gtk-based window optiosn editor
#  for IceWM (written in 100% Python).
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

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

import string
import IceWMCPGtkIconSelection as icons_dlg

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py

from icewmcp_dnd import *  # 5.16.2003 - drag-n-drop support

class wallwin:
    def __init__(self) :
	self.version=this_software_version
	self.x_comments="# Created by IceWM Control Panel - Window Options version "+self.version+"\n# http://icesoundmanager.sourceforge.net\n# This is an example for IceWM's window options file.\n#\n# Place your variants in ${sysconfdir}/X11/icewm or in $HOME/.icewm\n# since modifications to this file will be discarded when you\n# (re)install icewm.\n\n#userpasswd.layer: OnTop \n#kdepasswd.layer: OnTop\n\n#This controls Wharf geometry for 1024x768\n#licq.Wharf.dBorder: 0\n#licq.Wharf.ignoreTaskBar: 1\n#licq.Wharf.ignoreQuickSwitch: 1\n#licq.Wharf.dTitleBar: 0\n#licq.Wharf.layer: AboveDock\n#licq.Wharf.allWorkspaces: 1\n#licq.Wharf.geometry: +870+790\n\n"
	global WMCLASS
	WMCLASS="icewmcpwinoptions"
	global WMNAME
	WMNAME="IceWMCPWinOptions"
	wallwin=Window(WINDOW_TOPLEVEL)
	wallwin.set_wmclass(WMCLASS,WMNAME)
	set_basic_window_icon(wallwin)
	wallwin.realize()
	wallwin.set_title("IceWM CP - "+_("Window Options")+" "+self.version)
	wallwin.set_position(WIN_POS_CENTER)
	self.wallwin=wallwin
	# added 2.18.2003 - more locale support
	self.LAYER_NORMAL=_("Normal")
	self.LAYER_ABOVED=_("AboveDock")
	self.LAYER_DOCK=_("Dock")
	self.LAYER_BELOW=_("Below")
	self.LAYER_DESKTOP=_("Desktop")
	self.LAYER_ONTOP=_("OnTop")
	self.LAYER_MENU=_("Menu")


	self.layer_conv={"Normal":self.LAYER_NORMAL , "AboveDock":self.LAYER_ABOVED, "Dock":self.LAYER_DOCK  , "Menu":self.LAYER_MENU , "Desktop":self.LAYER_DESKTOP  , "OnTop":self.LAYER_ONTOP  , "Below":self.LAYER_BELOW}

	self.rlayer_conv={}
	for i,v in self.layer_conv.items():
		self.rlayer_conv[v]=i

	self.layers_list=[self.LAYER_NORMAL,self.LAYER_ABOVED,self.LAYER_BELOW,self.LAYER_DESKTOP,self.LAYER_DOCK,self.LAYER_ONTOP,self.LAYER_MENU]

	menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
				(_('/File/_Open...'), '<control>O', self.openKey, 0, ''),
				(_('/File/_Save'), '<control>S', self.doSave, 0, ''),
				(_('/File/sep1'), None, None, 1, '<Separator>'),
				(_('/File/_Apply Changes Now...'), "<control>A", self.restart_ice, 0, ''),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
 				(_("/_File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
  				(_("/_File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
				(_('/File/_Exit'), '<control>Q', self.doQuit, 0, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About...'), "F2", self.do_about, 0, ''),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5004, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5004, ""),
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

	self.preffile=""
	try:
		self.preffile=getIceWMPrivConfigPath()+"winoptions"
	except:
		pass
	mainvbox1=VBox(0,1)
	mainvbox=VBox(0,1)
	mainvbox1.pack_start(self.menubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,0)
	mainvbox.set_border_width(4)
	mainvbox.set_spacing(4)
	mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png",DIALOG_TITLE),0,0,2)
	mainvbox.pack_start(Label(_("Window Options")),0,0,2)	
	hbox1=HBox(0,0)
	hbox1.set_spacing(5)
	sc=ScrolledWindow()
	self.winlist=CList(2,[' '+'wm_class',' '+'wm_name'])
	self.sc=sc
	sc.add(self.winlist)
	sc.set_size_request(300,-1)
	self.winlist.set_column_width(0,120)

	vb=VBox(0,0)
	edbox=HBox(1,0)
	edbox.set_spacing(4)
	vb.pack_start(sc,1,1,0)
	TIPS.set_tip(self.winlist,"Program windows")
	addbutt=getPixmapButton(None, STOCK_ADD ,_("Add..."))
	TIPS.set_tip(addbutt,_("Add...").replace(".",""))
	addbutt.connect("clicked",self.show_addkey)
	delbutt=getPixmapButton(None, STOCK_DIALOG_ERROR ,_("Delete"))
	TIPS.set_tip(delbutt,_("Delete"))
	delbutt.connect("clicked",self.del_key)
	edbox.pack_start(addbutt,1,1,1)
	edbox.pack_start(delbutt,1,1,1)
	vb.pack_start(edbox,0,0,2)
	vb.pack_start(HSeparator(),0,0,1)
	anstr=_('/File/_Apply Changes Now...')[_('/File/_Apply Changes Now...').rfind("/")+1:len(_('/File/_Apply Changes Now...'))].replace(".","").replace("_","") 
	anbutt=getPixmapButton(None, STOCK_APPLY ,anstr)
	TIPS.set_tip(anbutt,anstr)
	anbutt.connect("clicked", self.restart_ice)
	svnbutt=getPixmapButton(None, STOCK_SAVE ,_("Save"))
	TIPS.set_tip(svnbutt,_("Save"))
	svnbutt.connect("clicked",self.doSave )
	vb.pack_start(svnbutt,0,0,1)
	vb.pack_start(anbutt,0,0,3)
	hbox1.pack_start(vb,1,1,1)


	vb2=VBox(0,0)
	vb2.set_spacing(2)
	h1=HBox(0,0)
	h1.set_spacing(3)
	h1.pack_start(Label(_("Icon: ")),0,0,0)
	self.iconentry=Entry()
	h1.pack_start(self.iconentry,1,1,0)
	browsebutt=getIconButton(None,STOCK_OPEN,_(" Browse... "))
	TIPS.set_tip(browsebutt,_(" Browse... "))
	browsebutt.connect("clicked",self.openIcon)
	h1.pack_start(browsebutt,0,0,0)
	addDragSupport(self.iconentry,self.setDrag)
	addDragSupport(browsebutt,self.setDrag)

	prevframe=Frame()
	self.prevlay=Layout()
	self.prevlay.set_size(30,30)
	prevframe.set_size_request(33,33)
	self.prevlay.show()
	prevframe.add(self.prevlay)
	h1.pack_start(Label("  "),0,0,0)
	h1.pack_start(prevframe,0,0,0)
	addDragSupport(prevframe,self.setDrag)

	h2=HBox(0,0)
	h2.set_spacing(3)
	h2.pack_start(Label(_("WorkSpace: ")),0,0,0)
	workentry=Entry()
	self.workentry=workentry
	h2.pack_start(workentry,1,1,0)

	h3=HBox(0,0)
	h3.set_spacing(3)
	h3.pack_start(Label(_("Layer: ")),0,0,0)
	laycom=Combo()
	self.layentry=laycom.entry
	self.layentry.set_editable(0)
	laycom.set_popdown_strings(self.layers_list)
	h3.pack_start(laycom,1,1,0)

	h4=HBox(0,0)
	h4.set_spacing(3)
	h4.pack_start(Label(_("Geometry: ")),0,0,0)
	geoentry=Entry()
	self.geoentry=geoentry
	h4.pack_start(geoentry,1,1,0)

	h5=HBox(0,0)
	h5.set_spacing(3)
	h5.pack_start(Label(_("Tray Icon: ")),0,0,0)
	traycom=Combo()
	self.trayentry=traycom.entry
	self.trayentry.set_editable(0)
	traycom.set_popdown_strings(['No tray icon','When minimized','Tray icon only'])
	h5.pack_start(traycom,1,1,0)
	
	vb2.pack_start(h1,0,0,3)
	vb2.pack_start(h2,0,0,1)
	vb2.pack_start(h3,0,0,1)
	vb2.pack_start(h4,0,0,1)
	vb2.pack_start(h5,0,0,1)

	scwin=ScrolledWindow()
	winoptlay=Layout()
	self.winoptlay=winoptlay
	winoptlay.set_size(330,500)
	scwin.add(winoptlay)
	self.warn_ok=0

	worder=['allWorkspaces','startFullscreen','startMaximized','startMaximizedVert','startMaximizedHorz','startMinimized','ignoreWinList','ignoreTaskBar','ignoreQuickSwitch','fullKeys','fMove','fResize','fClose','fMinimize', 'fMaximize','fHide','fRollup','dTitleBar','dSysMenu','dBorder','dResize','dClose','dMinimize','dMaximize','dHide','dRollup','dDepth','ignorePositionHint','doNotFocus','noFocusOnAppRaise','ignoreNoFocusHint','doNotCover','nonICCCMconfigureRequest','forcedClose']
	self.winwidgets={}
	self.windefaults={'allWorkspaces':0,'startFullscreen':0,'startMaximized':0,'startMaximizedVert':0,'startMaximizedHorz':0,'startMinimized':0,'ignoreWinList':0,'ignoreTaskBar':0,'ignoreQuickSwitch':0,'fullKeys':0,'fMove':1,'fResize':1,'fClose':1,'fMinimize':1, 'fMaximize':1,'fHide':1,'fRollup':1,'dTitleBar':1,'dSysMenu':1,'dBorder':1,'dResize':1,'dClose':1,'dMinimize':1,'dMaximize':1,'dHide':1,'dRollup':1,'dDepth':1,'ignorePositionHint':0,'doNotFocus':0, 'noFocusOnAppRaise':0,'ignoreNoFocusHint':0,'doNotCover':0,'nonICCCMconfigureRequest':0,"tray":"Ignore","geometry":"","layer":self.LAYER_NORMAL,"icon":"","workspace":"[DEFAULT]","forcedClose":0}

	self.winhints={'allWorkspaces':"Visible on all workspaces",'startFullscreen':"Start full-screen",'startMaximized':"Start maximized",'startMaximizedVert':"Start vertically maximized",'startMaximizedHorz':"Start horizontally maximized",'startMinimized':"Start minimized",'ignoreWinList':"Do not show in Window List" ,'ignoreTaskBar':"Do not show on taskbar",'ignoreQuickSwitch':"Do not show in Quick-switch window",'fullKeys':"Reserve extra 'F[num]' keys",'fMove':"Moveable",'fResize':"Resizeable",'fClose':"Closeable",'fMinimize':"Minimizeable",'fMaximize':"Maximizeable",'fHide':"Hideable",'fRollup':"Can be rolled up",'dTitleBar':"Has title bar",'dSysMenu':"Has system menu",'dBorder':"Has border",'dResize':"Has resize border",'dClose':"Has CLOSE button",'dMinimize':"Has MINIMIZE button",'dMaximize':"Has MAXIMIZE button",'dHide':"Has HIDE button (if applicable)",'dRollup':"Has ROLLUP button (if applicable)",'dDepth':"Has LAYER button (if applicable)",'ignorePositionHint':"Ignore pre-set window positions",'doNotFocus':"Do not focus",'noFocusOnAppRaise':"Do not focus when app is raised",'ignoreNoFocusHint':"Force focusing",'doNotCover':"Do not cover",'nonICCCMconfigureRequest':"App is non-ICCCM compliant",'forcedClose':'Do not show a confirmation dialog when closing the window'}

	self.window_options={}

	layx=3
	layy=2
	maxx=layx
	for ii in worder:
		ck=CheckButton(_(self.winhints[ii]))
		TIPS.set_tip(ck,_(self.winhints[ii])+"\n["+ii+"]")
		ck.set_active(self.windefaults[ii])
		ck.show()
		self.winwidgets[ii]=ck
		self.winoptlay.put(ck,layx,layy)
		layy=layy+ck.size_request()[1]+3
		if ck.size_request()[0]>maxx: maxx=ck.size_request()[0]

	self.winoptlay.set_size(maxx+20,layy+20)

	vb2.pack_start(scwin,1,1,0)
	setbutt=getPixmapButton(None, STOCK_YES ,_("Set"))
	TIPS.set_tip(setbutt,_("Set"))
	setbutt.connect("clicked",self.set_key)
	vb2.pack_start(setbutt,0,0,3)

	hbox1.pack_start(vb2,1,1,1)
	mainvbox.pack_start(hbox1,1,1,1)
		
	self.status=Label(_("Ready."))
	mainvbox.pack_start(self.status,0,0,0)
	wallwin.add(mainvbox1)
	wallwin.connect("destroy",self.doQuit)
	wallwin.set_default_size(565,600)
	self.last_icon=None
	self.loadUp()
	self.winlist.connect("select_row",self.clist_cb)
	self.winlist.connect("unselect_row",self.clist_unselect)
	self.wallwin=wallwin
	wallwin.show_all()

    def run_as_root(self,*args):
	# added 6.21.2003 - 'Run as Root' functionality
	if self.run_root_button.get_active():
		self.preffile=getIceWMConfigPath()+"winoptions"
		self.wallwin.set_title("IceWM CP - "+_("Window Options")+" "+self.version+"   [ROOT]")
		status_stuff= "[ROOT]    "+str(self.preffile)
	else:
		self.preffile=getIceWMPrivConfigPath()+"winoptions"
		self.wallwin.set_title("IceWM CP - "+_("Window Options")+" "+self.version)
		status_stuff= str(self.preffile)
	self.menubar.deactivate()
	self.loadUp()
	if len(status_stuff)>55: status_stuff=status_stuff[:54]+"..."
	self.status.set_text(status_stuff)
	# clear the picture by requesting non-existent image
	self.update_image("diifififickdiiridhdhdhf384hgtk203930dke")
	self.iconentry.set_text("")
	self.select_first_row()
	self.wallwin.show_all()


    def loadUp(self,*args) :
	self.current_row=-1
	self.current_wmclass=None
	self.get_keys()
	self.show_keys()

    def show_keys(self,*args) :
	self.winlist.freeze()
	self.winlist.clear()
	klist=self.window_options.keys()
	klist.sort()
	inum=0
	for ii in klist:
		try:
			k=ii.split(".")
			if len(k)==1: k.append("")
			if len(k)>2: # we have a long wm_class/wm_name prop - for it it 2 fields - added 2/18/2003
				k=[string.join(k[0:2] ,"."),string.join(k[2:len(k)], ".")]
			self.winlist.append(k)
			self.winlist.set_row_data(inum,ii)
			inum=inum+1
		except:
			pass

	self.winlist.thaw()

    def backup(self,file_name): # create backup of prefs file before editing
	try:
		f=open(file_name)
		ff=f.read()
		f.close()
		f=open(file_name+".backup-file","w")
		f.write(ff)
		f.flush()
		f.close()
	except:
		pass

    def restart_ice(self,*args) :
	if (self.warn_ok==1) or (msg_confirm(DIALOG_TITLE,_("WARNING:\nThis feature doesn't work perfectly on all systems.\nBSD and some other systems may experience problems."))	==1):
		self.warn_ok=1
		i=self.doSave()
		if i==1:
			os.system('killall -HUP -q icewm &')
			os.system('killall -HUP -q icewm-gnome &')

    def setStatus(self,stattext):
	self.status.set_text(_(str(stattext)))

    def doQuit(self,*args) :
	gtk.mainquit()

    def parseWinOpt(self,some_string) :
	s=some_string.strip()
	ss=s
	if ss.find(":")>-1: 
		ss=ss[0:ss.find(":")].strip()
		s=s[s.find(":")+1:len(s)].strip()
	l=[]
	for ii in ss.split("."):
		l.append(ii)
	l.append(s)
	return l

    def createDefaults(self,mywmclass):
	if not self.window_options.has_key(mywmclass):
		d={}
		for ii in self.windefaults.keys():
			d[ii]=self.windefaults[ii]
		self.window_options[mywmclass]=d

    def parseLineList(self,string_list):
	ff=string_list
	self.window_options.clear()
	try:
		for ii in ff:
			if ii.strip().startswith("#"): continue
			iline=ii.replace("\t"," ").strip()
			wlist=self.parseWinOpt(iline)
			if len(wlist)<3: continue  		# some mal-formed value, ignore
			else:  
				# changed parsing for long WM_CLASS names 
				#  ->  phrozenclock.py.PhrozenClock.py now dont get chopped off, 2/18/2003
				mnum=1
				snum=len(wlist)-2
				myprop=wlist[snum]
				myval=wlist[len(wlist)-1]
				mywmclass=wlist[0]
				while mnum<(snum):
					mywmclass=mywmclass+"."+wlist[mnum]
					mnum=mnum+1
			self.createDefaults(mywmclass)
			d=self.window_options[mywmclass]
			d[myprop]=myval
			if myprop=="layer":
				if myval in self.layer_conv.keys(): d[myprop]=self.layer_conv[myval] #locale support 2/18/2003
			#if str(mywmclass).lower().find("callerid")>-1: print "GtkCallerID:  "+myval
			self.window_options[mywmclass]=d
		return {}
	except:
		return {}

    def get_keys(self,*args) :
	try:
		self.backup(self.preffile) # create a backup
		f=open(self.preffile)
		ff=f.read().split("\n")
		f.close()
		return self.parseLineList(ff)
	except:
		pass
	try: # this happens if we got an empty prefs file - try system default
		f=open(getIceWMConfigPath()+"winoptions")
		ff=f.read().split("\n")
		f.close()
		return self.parseLineList(ff)
	except:
		pass
	return {}

    def clist_unselect(self,*args):
	self.current_wmclass=None
	self.current_row=-1

    def clist_cb(self,widget, row, col, event):
	rowd = widget.get_row_data(row)
	self.current_row=row
	self.current_wmclass=str(rowd)
	if self.window_options.has_key(rowd):
		d=self.window_options[rowd]
		for ival in d.keys():
			iprop=d[ival]
			if ival in self.winwidgets.keys():
				if str(iprop)=="0": self.winwidgets[ival].set_active(0)
				elif str(iprop)=="1": self.winwidgets[ival].set_active(1)
				else: self.winwidgets[ival].set_active(self.windefaults[ival])
			if ival =="tray":
				if iprop.lower().find("exclusive")>-1: self.trayentry.set_text("Tray icon only")
				elif iprop.lower().find("minimized")>-1: self.trayentry.set_text("When minimized")
				elif iprop.strip() in ["Tray icon only","No tray icon","When minimized"]: self.trayentry.set_text(iprop.strip())
				else: self.trayentry.set_text("No tray icon")
				#print "iprop:  "+iprop+"END"
			if ival=="layer":
				if iprop in self.layers_list:
					self.layentry.set_text(iprop)
				elif _(iprop) in self.layers_list:
					self.layentry.set_text(_(iprop))
				else: self.layentry.set_text(self.LAYER_NORMAL)
			if ival=="geometry":
				self.geoentry.set_text(iprop)
			if ival=="icon":
				self.iconentry.set_text(iprop)
				if len(iprop.strip())>0:
					if iprop.find(os.sep)==-1: # icewm icon
						self.update_image(getIceWMConfigPath()+"icons"+os.sep+iprop+"_32x32.xpm")
					else: self.update_image(iprop)
				else: # clear the picture by requesting non-existent image
					self.update_image("diifififickdiiridhdhdhf384hgtk203930dke")
			if ival=="workspace":
				self.workentry.set_text(iprop)


    def setDrag(self,*args): # drag-n-drop support, added 3.14.2003
	drago=args
	if len(drago)<7: 
		return 
	else: 
		#print str(drago[4].data)  # file:/root/something.txt
		try:
			imfile=""+str(drago[4].data).replace("\r\n","").replace("\x00","").replace("file:","").strip()
			self.run_image_update(imfile)
		except: 
			pass

    def run_image_update(self,imfile):
	self.iconentry.set_text(imfile)
	self.update_image(imfile)
	self.set_key()

    def openIcon(self,*args):
	icons_dlg.run_icons(self.run_image_update)

    def update_image(self,image_file):
		#print image_file
		for ii in self.prevlay.get_children():
			try:
				self.prevlay.remove(ii)
				ii.destroy()
				ii.unmap()
			except:
				pass
		try:
			if str(image_file).find(os.sep)==-1:
				image_file=getIceWMConfigPath()+"icons"+os.sep+str(image_file).strip()+"_32x32.xpm"
			pixreal=loadScaledImage(str(image_file).strip() ,28,28)
			pixreal.show()
			self.prevlay.put(pixreal,0,0)
			self.last_icon=str(image_file).strip()
		except:
			self.prevlay.put(Label(" "),1,1)

    def openKey(self, *args):
	self.selectfile(0)

    def show_addkey(self,*args):
	w=Window(WINDOW_TOPLEVEL)
	w.set_wmclass(WMCLASS,WMNAME)
	set_basic_window_icon(w)
    	w.set_data("ignore_return",1)  # don't close the window on 'Return' key press, just 'Esc' , 4/27/2003
    	w.connect("key-press-event", keyPressClose)
	w.realize()
	w.set_title(DIALOG_TITLE)
	w.set_position(WIN_POS_CENTER)
	mb=VBox(0,0)
	mb.set_spacing(2)
	labelist=[_("Step 1: Open the program you wish to set properties for."),_("Step 2: Click the 'Grab...' button below."),_("Step 3: Click the crosshairs on the program you opened.")]
	for ii in labelist:
		lab=Label(" "+ii+"  ")
		lab.set_alignment(0.0,0.5)
		mb.pack_start(lab,0,0,0)
	mb.pack_start(HSeparator(),0,0,4)
	hb=HBox(0,0)
	hb2=HBox(0,0)
	wmctext=Entry()
	wmntext=Entry()
	hb.pack_start(Label("WM_CLASS:  "),0,0,0)
	hb.pack_start(wmctext,1,1,0)
	mb.pack_start(hb,1,1,1)
	hb2.pack_start(Label("WM_NAME:   "),0,0,0)
	hb2.pack_start(wmntext,1,1,0)
	mb.pack_start(hb2,1,1,1)
	hb3=HBox(0,0)
	hb3.set_spacing(10)
	hb3.set_border_width(3)
	addbutt=Button(_("ADD"))
	TIPS.set_tip(addbutt,_("ADD"))
	addbutt.set_data("window",w)
	addbutt.set_data("wm_class",wmctext)
	addbutt.set_data("wm_name",wmntext)	
	closebutt=Button(_("Cancel"))
	TIPS.set_tip(closebutt,_("Cancel"))
	closebutt.set_data("window",w)
	grabbutt=Button(_("Grab..."))
	TIPS.set_tip(grabbutt,_("Grab..."))
	grabbutt.set_data("window",w)
	grabbutt.set_data("wm_class",wmctext)
	grabbutt.set_data("wm_name",wmntext)	
	hb3.pack_start(grabbutt,1,1,1)
	hb3.pack_start(Label("     "),1,1,1)
	hb3.pack_start(addbutt,1,1,1)
	hb3.pack_start(closebutt,1,1,1)
	mb.pack_start(hb3,1,1,1)
	mb.set_border_width(3)
	w.add(mb)
	closebutt.connect("clicked",self.add_key)
	grabbutt.connect("clicked",self.grab_wmclass)
	addbutt.connect("clicked",self.add_key)
	w.set_modal(1)
	w.show_all()

    def grab_wmclass(self,*args):
	f=os.popen("xprop")
	flines=f.readlines()
	f.close()
	for ii in flines:
		if ii.startswith("WM_CLASS"):
			if ii.find("=")>0:
				iline=ii[ii.find("=")+1:len(ii)].strip()
				iline=iline.split(",")
				if len(iline)==2:
					wmc=iline[0].replace("\t"," ").replace("\"","").strip()
					wmn=iline[1].replace("\t"," ").replace("\"","").strip()
					args[0].get_data("wm_class").set_text(wmc)
					args[0].get_data("wm_name").set_text(wmn)
				
	
    def add_key(self,*args):
	if args[0].get_data("wm_class")==None:
		args[0].get_data("window").destroy()
		args[0].get_data("window").unmap()
	else:
		if len(args[0].get_data("wm_class").get_text().strip())==0:
			msg_err(DIALOG_TITLE,_("You must complete at least the 'wm_class' field."))	
			return
		wm=args[0].get_data("wm_class").get_text().strip()
		if len(args[0].get_data("wm_name").get_text().strip())>0:
			wm=wm+"."+args[0].get_data("wm_name").get_text().strip()
		if self.window_options.has_key(wm):
			msg_err(DIALOG_TITLE,_("The wm_class/wm_name '")+wm+_("' already exists.\nEither edit or delete the existing '")+wm+_("' window settings."))	
			try:
				k=self.window_options.keys()
				k.sort()
				self.winlist.moveto(k.index(wm),0,0,0)
				self.winlist.select_row(k.index(wm),0)
			except:
				pass
			return		
		self.createDefaults(wm)
		self.current_wmclass=None
		self.current_row=-1
		self.show_keys()
		self.setStatus(_("Modified."))
		try:
			k=self.window_options.keys()
			k.sort()
			self.winlist.select_row(k.index(wm),0)
			self.winlist.moveto(k.index(wm),0,0,0)
		except:
			pass
		
		args[0].get_data("window").destroy()
		args[0].get_data("window").unmap()

    def set_key(self,*args):
	if self.current_row==-1: return
	if self.current_wmclass==None: return
	try:
			d=self.window_options[self.current_wmclass]
			d["tray"]=self.trayentry.get_text().strip()
			d["icon"]=self.iconentry.get_text().strip()
			d["workspace"]=self.workentry.get_text().strip()
			d["geometry"]=self.geoentry.get_text().strip()
			d["layer"]=self.rlayer_conv[self.layentry.get_text().strip()]
			for ii in self.winwidgets.keys():
				d[ii]=self.winwidgets[ii].get_active()
			self.setStatus(_("Modified."))
			if len(self.iconentry.get_text().strip())>0: 
				self.update_image(self.iconentry.get_text().strip())
			else: # clear the preview image by requesting non-existent image
				self.update_image("diifififickdiiridhdhdhf38d8d8g8r8dkwweieie2")
	except:
		pass

    def del_key(self,*args):
	if self.current_row==-1: return
	if self.current_wmclass==None: return
	try:
		if msg_confirm(DIALOG_TITLE,_("Are you sure you want to delete\nthe window options associated with:\n")+self.current_wmclass)==1:
			myrow=self.current_row-1
			del self.window_options[self.current_wmclass]
			self.show_keys()
			if myrow<0: myrow=0
			self.current_row=self.current_row-1
			self.current_wmclass=None
			self.setStatus(_("Modified."))
			self.winlist.select_row(myrow,0)
			self.winlist.moveto(myrow,0,0,0)
	except:
		pass

    def selectfile(self, program=1):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		if program==1: value=self.last_icon
		else: value=self.preffile
		if not value==None:
			if value != '""':
				SET_SELECTED_FILE(value)
		SELECT_A_FILE(self.fileok)

    def select_first_row(self,*args):
			try:
				if len(self.window_options.keys())>0:
					self.winlist.moveto(0,0,0,0)
					self.winlist.select_row(0,0)
					self.current_row=0
			except:
				pass
		
    def fileok(self, *args):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		dirvalue=GET_SELECTED_FILE()   # from icewmcp_common
		if os.path.exists(dirvalue):
				self.preffile=dirvalue
				self.loadUp()
				# clear the picture by requesting non-existent image
				self.update_image("diifififickdiiridhdhdhf384hgtk203930dke")
				self.iconentry.set_text("")
				self.wallwin.set_title("IceWM CP - "+_("Window Options")+" "+self.version)
				self.select_first_row()
				self.setStatus(_("Ready."))
		else:				
				msg_err(DIALOG_TITLE,_("No such file or directory:\n")+dirvalue)	
				return

    def doSave(self,*args):	
	try:
		f=open(self.preffile,"w")
		f.write(self.x_comments)
		f.flush()
		k=self.window_options.keys()
		k.sort()
		for ii in k:
			kdict=self.window_options[ii]
			h=kdict.keys()
			h.sort()
			for jj in h:
				if jj=="icon":
					if len(str(kdict[jj]).strip())==0: continue
					f.write(str(ii)+"."+str(jj)+": "+str(kdict[jj])+"\n")
				elif jj=="geometry":
					if len(str(kdict[jj]).strip())==0: continue
					f.write(str(ii)+"."+str(jj)+": "+str(kdict[jj])+"\n")
				elif jj=="workspace":
					if len(str(kdict[jj]).strip())==0: continue
					if str(kdict[jj]).strip()=="[DEFAULT]": continue
					f.write(str(ii)+"."+str(jj)+": "+str(kdict[jj])+"\n")
				elif jj=="tray":
					iprop=str(kdict[jj]).strip()
					ival="Ignore"
					if iprop.lower().find("only")>-1: ival="Exclusive"
					if iprop.lower().find("exclusive")>-1: ival="Exclusive"
					if iprop.lower().find("minimized")>-1: ival="Minimized"
					f.write(str(ii)+"."+str(jj)+": "+ival+"\n")
					#if str(ii).lower().find("callerid")>-1: print "GtkCallerID:  "+ival
				else: 
					# dont write default stuff - wastes space
					if self.windefaults.has_key(str(jj)):
						if str(self.windefaults[str(jj)])==str(kdict[jj]): continue
					f.write(str(ii)+"."+str(jj)+": "+str(kdict[jj])+"\n")
			f.write("\n")
		f.flush()
		f.close()
		self.setStatus(_("Saved."))
		return 1
	except:
		msg_err(DIALOG_TITLE,_("There was an ERROR saving your window options to the file:\n")+self.preffile)	
		return 0
	return 0

    def do_about(self,*args):
	commonAbout(_("About")+" IceWMCP - "+_("Window Options")+"  "+self.version,  "IceWMCP - "+_("Window Options Editor")+" "+self.version+"\n\n"+_("A simple Gtk-based window options configuration utility\nfor IceWM (written in 100% Python).\nOptimized for IceWM version 1.2.7.\n\nThis program is distributed free\nof charge (open source) under the GNU\nGeneral Public License."))	

def run() :
	wallwin()
	hideSplash()
	gtk.mainloop()

if __name__== "__main__" :
	run()

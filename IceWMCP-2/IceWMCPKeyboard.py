#! /usr/bin/env python

######################################
# IceWM Control Panel Keyboard Settings
# 
# Copyright 2003 by Erica Andrews 
# (PhrozenSmoke@yahoo.com)
# http://icesoundmanager.sourceforge.net
#
#  This program incorporates 4 tools:
#
#  A simple Gtk-based shortcut key configuration utility
#  for IceWM (written in 100% Python).  The old 
#  'IceWMCPKeyEdit.py' module
#
#  A simple Gtk-based utility for configuring the keyboard
#  beep and key-click sounds  It's a simple frontend 
#  for 'xset'.  
# 
#  A simple Gtk-based utility for setting the keyboard repeat
#  rate and delay.  It's a simple frontend for 'xset'.  
#
#  An embedded module from IcePref2 for configuring 
#  keyboard shortcuts under IceWM.
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

import time

#set translation support
import icewmcp_common
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py

icewmcp_common.NOSPLASH=1  # disable splash window from icepref_td,icepref

import icepref

global ICE_TAB
ICE_TAB=None
global KEY_TAB
KEY_TAB=None
global SHORT_TAB
SHORT_TAB=None
global BELL_TAB
BELL_TAB=None
global BSD_WARN
BSD_WARN=0
global KB_SETTINGS
KB_SETTINGS=['','','','','']  # holds 5 keyboard settings: rate, bell-on, bell-vol, click-on, click-vol
global C_WINDOW
C_WINDOW=None
global DO_QUIT
DO_QUIT=1

# shared methods

def restart_ice(*args) :
	global BSD_WARN
	if not BSD_WARN==1:
		if not msg_confirm(DIALOG_TITLE,_("WARNING:\nThis feature doesn't work perfectly on all systems.\nBSD and some other systems may experience problems."))==1:
			return
	BSD_WARN=1
	global ICE_TAB
	global SHORT_TAB
	global KEY_TAB
	global BELL_TAB
	BELL_TAB.doApply()
	KEY_TAB.doApply()
	ICE_TAB.save_current_settings("nowarn")
	SHORT_TAB.doSave()
	os.system('killall -HUP -q icewm &')
	os.system('killall -HUP -q icewm-gnome &')

def doQuit(*args):
	mainquit()

def reapplySettings1(*args):
	#this method used to reapply settings before we exit, because Gtk's 'destroy' call 
	# triggers some 'disable' checkbuttons and messes everything up - disabling ALL 
	# keyboard repeat and sound, you are advised not to tamper with this method unless
	# you truly know what you are doing
	time.sleep(0.2)
	#print "reapply"
	global KB_SETTINGS
	global DO_QUIT
	for ii in KB_SETTINGS:  # execute all of our 'saved' settings commands on exit
		if ii==None: continue
		if ii.strip()=='': continue
		os.popen(ii+" &")
	if DO_QUIT==1: sys.exit(1)  # better to call sys.exit instead of mainquit in this situation


def reapplySettings(*args):
	global C_WINDOW
	try:
		C_WINDOW.hide()
		C_WINDOW.destroy()
		C_WINDOW.unmap()
	except:
		pass
	timeout_add(2,reapplySettings1)



####################################
## Shortcut Key tool - from the old IceWMCPKeyEdit
####################################
class keypanel:
    def createPanel(self,with_logo=1):
	mainvbox=VBox(0,2)
	mainvbox.set_border_width(5)
	mainvbox.set_spacing(4)
	if with_logo==1:  mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png",DIALOG_TITLE),0,0,2)
	mainvbox.pack_start(Label(_("Key Editor")),0,0,1)	
	
	self.clist=CList(2,[' '+_('Keys'),' '+_('Command')])
	self.sc=ScrolledWindow()
	self.clist.set_column_width(0,150)
	self.clist.set_column_width(1,350)
	self.sc.add(self.clist)

	mainvbox.pack_start(self.sc,1,1,0)
	keybox=HBox(0,0)
	keybox.set_spacing(6)
	keybox.pack_start(Label(_("Key:  ")),0,0,0)
	self.alt=CheckButton("Alt")
	self.ctrl=CheckButton("Ctrl")
	self.shift=CheckButton("Shift")
	TIPS.set_tip(self.alt,"Alt")
	TIPS.set_tip(self.ctrl,"Ctrl")
	TIPS.set_tip(self.shift,"Shift")
	keybox.pack_start(self.alt,0,0,0)
	keybox.pack_start(self.ctrl,0,0,0)
	keybox.pack_start(self.shift,0,0,0)
	self.keyentry=Entry()
	keybox.pack_start(self.keyentry,1,1,0)
	progbox=HBox(0,0)
	progbox.set_spacing(4)
	progbox.pack_start(Label(_("Program:  ")),0,0,0)
	self.progentry=Entry()
	progbox.pack_start(self.progentry,1,1,0)
	TIPS.set_tip(self.progentry,_("Program:  ").replace(":","").strip())
	browse=Button()
	try:
			browse.add(  loadScaledImage(getPixDir()+"ism_load.png",24,24)  )
	except:
			browse.add(Label(_(" Browse... ")))
	TIPS.set_tip(browse,_(" Browse... ").replace(".","").strip())
	browse.connect("clicked",self.openProg)
	progbox.pack_start(browse,0,0,0)
	buttbox=HBox(1,0)
	buttbox.set_spacing(4)
	buttbox2=HBox(1,0)
	buttbox2.set_spacing(4)
	newb=Button(_(" New Key "))
	setb=Button(_(" Set "))
	addb=Button(_(" Add "))
	delb=Button(_(" Delete "))
	testb=Button(_(" Test Key "))
	saveb=Button(" "+_("Save")+" ")
	TIPS.set_tip(saveb,_("Save"))
	TIPS.set_tip(testb,_(" Test Key ").strip())
	TIPS.set_tip(delb,_(" Delete ").strip())
	TIPS.set_tip(addb,_(" Add ").strip())
	TIPS.set_tip(setb,_(" Set ").strip())
	TIPS.set_tip(newb,_(" New Key ").strip())
	newb.connect("clicked",self.new_key2)
	self.newb=newb
	setb.connect("clicked",self.set_key)
	addb.connect("clicked",self.add_key)
	delb.connect("clicked",self.del_key)
	testb.connect("clicked",self.test_key)
	saveb.connect("clicked",self.doSave)
	self.addb=addb
	self.setb=setb
	self.delb=delb
	self.testb=testb
	buttbox.pack_start(newb,1,1,0)
	buttbox.pack_start(setb,1,1,0)
	buttbox.pack_start(addb,1,1,0)
	buttbox2.pack_start(delb,1,1,0)
	buttbox2.pack_start(testb,1,1,0)
	buttbox2.pack_start(saveb,1,1,0)
	mainvbox.pack_start(keybox,0,0,0)	
	mainvbox.pack_start(progbox,0,0,0)	
	mainvbox.pack_start(buttbox,0,0,0)	
	mainvbox.pack_start(buttbox2,0,0,0)	
	appst=_('/File/_Apply Changes Now...')[_('/File/_Apply Changes Now...').rfind("/")+1:len(_('/File/_Apply Changes Now...'))].replace(".","").replace("_","").strip()
	appbutt=Button(appst)
	self.appbutt=appbutt
	TIPS.set_tip(appbutt,appst)	
	mainvbox.pack_start(appbutt,0,0,2)		
	self.status=Label(_("Ready."))
	self.mainvbox=mainvbox
	mainvbox.show_all()
	mainvbox.pack_start(self.status,0,0,2)	
	self.clist.connect('select_row', self.clist_cb)
	self.clist.connect('unselect_row', self.new_key1)
	self.loadUp()
	return mainvbox	

    def __init__(self,noclose=0,start_pref_file=None) :
	self.start_comment="# This is an example for IceWM's hotkey definition file.\n#\n# Place your variants in /usr/X11R6/lib/X11/icewm or in $HOME/.icewm\n# since modifications to this file will be discarded when you\n# (re)install icewm.\n#\n# A list of all valid keyboard symbols can be found in\n# /usr/include/X11/keysym.h, keysymdefs.h,XF86keysym.h, ...\n# You'll have to omit XK_ prefixs and to replace XF86XK_ prefixes by\n# XF86. Valid modifiers are Alt, Ctrl, Shift, Meta, Super and Hyper.\n#\n#\n#\n\n"
	self.x_comment="\n\n# Multimedia key bindings for XFree86. Gather the keycodes of your\n# advanced function keys by watching the output of the xev command whilest\n# pressing those keys and map those symbols by using xmodmap.\n\n"
	self.version=this_software_version
	self.NOCLOSE=noclose
	self.preffile=""
	self.keys={}
	try:
		self.preffile=getIceWMPrivConfigPath()+"keys"
	except:
		pass
	if not start_pref_file==None:
		self.preffile=start_pref_file
	self.lastprog=""

    def createWindow(self):
	global WMCLASS
	WMCLASS="icewmcontrolpanelkeyedit"
	global WMNAME
	WMNAME="IceWMControlPanelKeyEdit"
	wallwin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(wallwin)
	if self.NOCLOSE==1:
		wallwin.set_data("ignore_return",1)
		wallwin.connect("key-press-event",keyPressClose)
	wallwin.set_wmclass(WMCLASS,WMNAME)
	wallwin.realize()
	wallwin.set_title(_("IceWM CP - Key Editor"))
	wallwin.set_position(WIN_POS_CENTER)
	self.wallwin=wallwin

	menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
				(_('/File/_Open...'), '<control>O', self.openKey, 0, ''),
				(_('/File/_Save'), '<control>S', self.doSave, 0, ''),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
 				(_("/_File")+"/_"+FILE_RUN,'<control>R', rundlg,421,""),
 				(_("/_File")+"/_"+_("Check for newer versions of this program..."), '<control>U', checkSoftUpdate,420,""),
				(_('/File/sep1'), None, None, 1, '<Separator>'),
				(_('/File/_Apply Changes Now...'), '<control>A', self.restart_ice, 0, ''),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
				(_('/File/_Exit'), '<control>Q', self.doQuit, 0, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About...'), "F2", self.do_about, 0, ''),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5002, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5002, ""),
					]

	ag = AccelGroup()
	itemf = ItemFactory(MenuBar, '<main>', ag)
	self.ag=ag
	self.itemf=itemf
	wallwin.add_accel_group(ag)
	itemf.create_items(menu_items)
	self.menubar = itemf.get_widget('<main>')
	menubox=HBox(0,0)
	menubox.pack_start(self.menubar,1,1,0)
	mainvbox1=VBox(0,2)
	mainvbox1.pack_start(menubox,0,0,0)
	mainvbox1.pack_start(self.createPanel(1),1,1,2)
	wallwin.add(mainvbox1)
	wallwin.connect("destroy",self.doQuit)
	wallwin.set_default_size(-1,440)
	self.appbutt.connect("clicked",self.restart_ice)
	wallwin.show_all()

    def loadUp(self,*args) :
	self.current_row=-1
	self.current_key=None
	self.mykeys=self.get_keys()
	self.display_keys(self.mykeys)
	self.new_key()
	if len(self.mykeys.keys())>0:
		self.clist.select_row(0,0)
	self.setStatus(_("Ready."))

    def doQuit(self,*args) :
	if self.NOCLOSE==0: 
		gtk.mainquit()
	else: 
		self.wallwin.destroy()
		self.wallwin.hide()

    def build_key(self,*args):
	s=""
	if self.ctrl.get_active(): s="Ctrl"
	if self.alt.get_active():
		if len(s)==0: s="Alt"
		else: s=s+"+Alt"
	if self.shift.get_active():
		if len(s)==0: s="Shift"
		else: s=s+"+Shift"
	if len(self.keyentry.get_text().strip())>0:
		if len(s)==0: s=self.keyentry.get_text().strip()
		else: s=s+"+"+self.keyentry.get_text().strip()
	return s

    def set_key(self,*args):
	if self.current_key==None: return
	if not self.mykeys.has_key(self.current_key):
		msg_warn(DIALOG_TITLE,_("This key does not exist.\nPlease create it by clicking the 'New Key' button."))	
		return
	if not len(self.progentry.get_text().strip())>0:
		msg_warn(DIALOG_TITLE,_("You must specify a program for this key combination"))	
		return
	self.clist.freeze()
	self.mykeys[self.current_key]=self.progentry.get_text().strip()
	self.display_keys(self.mykeys)
	self.new_key(1)
	self.setStatus(_("Modified."))
	try:
		l=self.mykeys.keys()
		l.sort()
		self.clist.select_row(l.index(self.current_key),0)
		self.clist.moveto(l.index(self.current_key),0,0,0)
	except:
		pass
	self.clist.thaw()

    def add_key(self,*args):
	s=self.build_key()
	if not len(s)>0: return
	if not len(self.progentry.get_text().strip())>0:
		msg_warn(DIALOG_TITLE,_("You must specify a program for this key combination")+":\n"+s)	
		return
	if self.mykeys.has_key(s):
		msg_warn(DIALOG_TITLE,_("The key '")+s+_("' already exists and\ntriggers the program: ")+self.mykeys[s]+"\n\n"+_("You must either delete the existing key,\nor change the existing key's action using 'Set'."))
		return
	self.clist.freeze()
	self.mykeys[s]=self.progentry.get_text().strip()
	self.display_keys(self.mykeys)
	self.setStatus(_("Modified."))
	try:
		l=self.mykeys.keys()
		l.sort()
		self.clist.select_row(l.index(s),0)
		self.clist.moveto(l.index(s),0,0,0)
	except:
		pass
	self.clist.thaw()

    def del_key(self,*args):
	if self.current_key==None: return
	self.clist.thaw()
	try:
		if msg_confirm(DIALOG_TITLE,_("Are you sure you want to delete this key?")+"\n\n"+self.current_key+"\n"+self.mykeys[self.current_key])==1:

			l=self.mykeys.keys()
			l.sort()
			prev_row=l.index(self.current_key)-1

			del self.mykeys[self.current_key]
			self.display_keys(self.mykeys)
			self.new_key(0)
			self.current_key=None
			self.setStatus(_("Modified."))
			try:
				self.clist.select_row(prev_row,0)
				self.clist.moveto(prev_row,0,0,0)
			except:
				pass
	except:
		pass
	self.clist.freeze()

    def new_key1(self,*args):
	self.new_key(0)

    def new_key2(self,*args):
	self.clist.unselect_row(self.current_row,0)
	self.new_key(0)

    def new_key(self,desense=0):
	self.progentry.set_text("")
	self.alt.set_active(0)
	self.ctrl.set_active(0)
	self.shift.set_active(0)
	self.keyentry.set_text("")
	if desense==1:
		self.keyentry.set_sensitive(0)
		self.alt.set_sensitive(0)
		self.shift.set_sensitive(0)
		self.ctrl.set_sensitive(0)
		self.addb.set_sensitive(0)
		self.delb.set_sensitive(1)
		self.setb.set_sensitive(1)
		self.testb.set_sensitive(1)
	else:
		self.keyentry.set_sensitive(1)
		self.alt.set_sensitive(1)
		self.shift.set_sensitive(1)
		self.ctrl.set_sensitive(1)
		self.addb.set_sensitive(1)
		self.delb.set_sensitive(0)
		self.setb.set_sensitive(0)
		self.testb.set_sensitive(0)
		self.current_key=None

    def clist_cb(self,widget, row, col, event):
	rowlist = widget.get_row_data(row)
	self.current_row=row
	self.new_key(1)
	self.progentry.set_text(rowlist[1])
	ikeys=rowlist[0].split("+")
	self.current_key=rowlist[0]
	for ii in ikeys:
		if ii=="Ctrl": self.ctrl.set_active(1)
		elif ii=="Alt": self.alt.set_active(1)
		elif ii=="Shift": self.shift.set_active(1)
		else:
			if  len(self.keyentry.get_text())>0: self.keyentry.set_text(self.keyentry.get_text()+"+"+ii)
			else: self.keyentry.set_text(ii)
	

    def display_keys(self,key_dict):
	klist=key_dict.keys()
	klist.sort()
	self.clist.freeze()
	self.clist.clear()	
	inum=0
	for ii in klist:
		try:
			self.clist.append([ii,key_dict[ii]])
			self.clist.set_row_data(inum,[ii,key_dict[ii],inum])
			inum=inum+1
		except:
			pass
	self.clist.thaw()
		

    def parseLineList(self,string_list):
	ff=string_list
	try:
		d={}
		for ii in ff:
			if not ii.strip().startswith("key "): continue
			iline=ii[ii.find("key ")+4:len(ii)].strip()
			if iline.startswith("\""):
				ikey=iline[0:iline.rfind("\"")+1].strip()
				iprog=iline.replace(ikey,"").replace("\t","").replace("\t","").replace("\t","").strip()
				if iprog.find("#")>0: iprog=iprog[0:iprog.find("#")]
				ikey=ikey.replace("\"","").strip()
				if (len(ikey)>0) and (len(iprog)>0):
					keylist=ikey.split("+")
					arkeys=""
					if ikey.find("Ctrl")>-1: arkeys="Ctrl"
					if ikey.find("Alt")>-1:
						if len(arkeys)>0: arkeys=arkeys+"+Alt"
						else: arkeys="Alt"
					if ikey.find("Shift")>-1:
						if len(arkeys)>0: arkeys=arkeys+"+Shift"
						else: arkeys="Shift"
					for h in keylist:
						if h.strip() in ['Alt','Ctrl','Shift']: continue
						if len(arkeys)>0: arkeys=arkeys+"+"+h.strip()
						if len(arkeys)==0: arkeys=h.strip()					
					d[arkeys]=iprog
		return d
	except:
		return {}

    def get_keys(self,*args) :
	try:
		#print "KEYS:  "+str(self.preffile)
		self.backup(self.preffile) # create a backup
		f=open(self.preffile)
		ff=f.read().split("\n")
		f.close()
		return self.parseLineList(ff)
	except:
		pass
	try: # this happens if we got an empty prefs file - try system prefs in a universal way, new in version 1.2
		f=open(getIceWMConfigPath()+"keys")
		ff=f.read().split("\n")
		f.close()
		return self.parseLineList(ff)
	except:
		pass
	return {}

    def openKey(self, *args):
	self.selectfile(0)

    def openProg(self, *args):
	self.selectfile(1)

    def selectfile(self, program=1):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		if program==1: 
			value=self.lastprog
			self.is_prog_select=1
		else: 
			value=self.preffile
			self.is_prog_select=0
		if value != '""':
			SET_SELECTED_FILE(value)
		SELECT_A_FILE(self.fileok)
		
    def fileok(self, *args):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		dirvalue=GET_SELECTED_FILE()   # from icewmcp_common
		if self.is_prog_select==1:
			self.progentry.set_text(str(dirvalue))
		else:
			if os.path.exists(dirvalue):
				self.preffile=dirvalue
				self.loadUp()
			else:				
				msg_err(DIALOG_TITLE,_("No such file or directory:\n")+dirvalue)	
				return

    def run_as_root(self, root_bool): 
	# added 6.22.2003 - Run As Root functionality
	if root_bool==1:
		self.preffile= getIceWMConfigPath()+'keys'
	else:  # turn 'root' OFF
		self.preffile=getIceWMPrivConfigPath()+"keys"
	self.loadUp()

    def doSave(self,*args):
	try:
		f=open(self.preffile,"w")
		flist=self.mykeys.keys()
		flist.sort()
		wrotex=0
		f.write(self.start_comment)
		for ii in flist:
			if (ii.startswith("XF86")) and (wrotex==0):
				f.write(self.x_comment+"\n")
				wrotex=1
				f.write("key \""+ii+"\"\t\t"+self.mykeys[ii]+"\n")
			else:
				f.write("key \""+ii+"\"\t\t"+self.mykeys[ii]+"\n")
		self.setStatus(_("Saved."))
		return 1
	except:
		msg_err(DIALOG_TITLE,_("ERROR saving key configuration file:\n")+self.preffile)	
		self.setStatus(_("Error saving."))
		return 0

    def restart_ice(self,*args) :
	if msg_confirm(DIALOG_TITLE,_("WARNING:\nThis feature doesn't work perfectly on all systems.\nBSD and some other systems may experience problems."))	== 1:
		i=self.doSave()
		if i==1:
			os.system('killall -HUP -q icewm &')
			os.system('killall -HUP -q icewm-gnome &')

    def setStatus(self,stattext):
	self.status.set_text(_(str(stattext)))

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

    def do_about(self,*args):  # this method is needed for when running under IceMe
	commonAbout(_("About IceWM CP - Key Editor")+" "+self.version,_("IceWM CP - Key Editor")+" "+self.version+"\n\n"+_("A simple Gtk-based key configuration utility\nfor IceWM (written in 100% Python).\n\nThis program is distributed free\nof charge (open source) under the GNU\nGeneral Public License."))	

    def test_key(self,*args):
	if self.current_key==None: return
	exec_n=self.mykeys[self.current_key]
	if not self.progentry.get_text().strip()==exec_n:  
		self.set_key()  # update the key if text entry changed
		if self.current_key==None: return
		exec_n=self.mykeys[self.current_key]
	path_find=self.is_on_path(""+exec_n)
	if path_find==1:  
		# launch the app and see if it works
		os.popen(exec_n+" &") # for to bash/bourne
	else:
		if path_find==0: # no full path given and not on system $PATH
			msg_warn(DIALOG_TITLE,_("The executable is not on your PATH")+":\n"+self.get_exec_short(""+exec_n))	
		if path_find==-1:  # full path given, but file doesnt exist	
			msg_warn(DIALOG_TITLE,_("The executable file does not exist")+":\n"+self.get_exec_short(""+exec_n))	

    def get_exec_short(self,exec_short):
	if exec_short.find(" ")>-1: exec_short=exec_short[0:exec_short.find(" ")] # "aumix -v +5" -> "aumix" is exec
	return exec_short.strip()

    def is_on_path(self,exec_name):  # new in version 1.2, check to see if an executable is on the path
	exec_name=self.get_exec_short(exec_name)

	try:
		if exec_name.find(os.sep)>-1:  # check first to see if exec_name is a FULL path
			if os.path.exists(exec_name): return 1
			else: return -1  # full path given, but not in system	
		else:
			paths=os.environ['PATH'].split(":")
			for ii in paths:
				if os.path.exists(ii+os.sep+exec_name): return 1
			return 0 # no full path given, and not on path
	except:
		pass
	return 1



##########################################
## Keyboard repeat rate tool - from the old IceWMCPKeyboard
##########################################

class keywintab:
    def __init__(self) :
	mainvbox=VBox(0,1)
	mainvbox.set_border_width(4)
	mainvbox.set_spacing(4)
	self.mainvbox=mainvbox
	try:
		mainvbox.pack_start(loadScaledImage(getPixDir()+"ice-keyboard.png",63,45),0,0,3)
	except:
		pass

	mainvbox.pack_start(Label(_(" Select your desired keyboard repeat rate: ")),0,0,3)	

	self.clickcheck=CheckButton(" "+_("Allow keyboard auto-repeat"))
	TIPS.set_tip(self.clickcheck,_("Allow keyboard auto-repeat"))
	self.mainvbox.pack_start(self.clickcheck,0,0,2)
	self.clickcheck.set_active(1)
	mainframe=Frame()
	mainframe.set_label(_("Rate: "))
	self.adj1=Adjustment(20,1,150,1,1,1)
	c=HScale(self.adj1)
	TIPS.set_tip(c,_("Rate: ").replace(":","").strip())
	c.set_digits(0)
	c.set_draw_value(1)
	c.set_update_policy(UPDATE_DISCONTINUOUS)
	c.set_value_pos(POS_TOP)
	cbox=VBox(0,0)	
	cbox.set_spacing(8)
	cbox.set_border_width(5)
	cbox.pack_start(c,1,1,0)
	cbox.show_all()
	mainframe.add(cbox)
	mainvbox.pack_start(mainframe,1,1,5)

	mainframe2=Frame()
	mainframe2.set_label(_("Delay: "))
	self.adj2=Adjustment(400,1,3000,1,1,1)
	c2=HScale(self.adj2)
	TIPS.set_tip(c2,_("Delay: ").replace(":","").strip())
	c2.set_digits(0)
	c2.set_draw_value(1)
	c2.set_update_policy(UPDATE_DISCONTINUOUS)
	c2.set_value_pos(POS_TOP)
	cbox2=VBox(0,0)	
	cbox2.set_spacing(8)
	cbox2.set_border_width(5)
	cbox2.pack_start(c2,1,1,0)
	cbox2.show_all()
	mainframe2.add(cbox2)
	mainvbox.pack_start(mainframe2,1,1,5)

	mainframe=Frame()
	mainframe.set_label(_("To test the repetition, hold a key for a few seconds")+":")
	self.entry=Entry()
	TIPS.set_tip(self.entry,_("Test")+"\n"+_("To test the repetition, hold a key for a few seconds")+".")
	cbox=HBox(0,0)	
	cbox.set_border_width(8)
	cbox.pack_start(self.entry,1,1,0)
	cbox.show_all()
	mainframe.add(cbox)
	mainvbox.pack_start(mainframe,1,1,5)

	self.adj1.connect("value_changed",self.doApply)
	self.adj2.connect("value_changed",self.doApply)
	self.clickcheck.connect("clicked",self.doApply)
	abutton=Button(_("Apply"))
	TIPS.set_tip(abutton,_("Apply"))
	rbutton=Button(_("Reset"))
	TIPS.set_tip(rbutton,_("Reset"))
	cbutton=Button(_("Close"))
	TIPS.set_tip(cbutton,_("Close"))
	hb=HBox(0,0)
	hb.pack_start(abutton,1,1,0)
	hb.pack_start(rbutton,1,1,0)
	hb.pack_start(cbutton,1,1,0)
	hb.set_spacing(4)
	hb.set_border_width(2)
	mainvbox.pack_start(hb,0,0,2)
	abutton.connect("clicked",self.doApply)
	rbutton.connect("clicked",self.doReset)
	cbutton.connect("clicked",reapplySettings)
	mainvbox.show_all()

    def doReset(self,*args) : # reset to a reasonable speed
	global KB_SETTINGS
	os.popen("xset r rate 400 20 &> /dev/null &")
	KB_SETTINGS[0]="xset r rate 400 20"
	self.adj2.set_value(400)
	self.adj1.set_value(20)
	self.entry.set_text("")

    def doApply(self,*args) : # set to desired speed
	#print "doApply-11"
	global KB_SETTINGS
	if self.clickcheck.get_active():
		os.popen("xset r rate "+str(int(self.adj2.value))+" "+str(int(self.adj1.value))).readlines()
		KB_SETTINGS[0]="xset r rate "+str(int(self.adj2.value))+" "+str(int(self.adj1.value))
	else:
		os.popen("xset -r ").readlines()
		KB_SETTINGS[0]="xset -r"
	self.entry.set_text("")


##########################################
## Keyboard bell and key-click sound tool
##########################################

class keysoundtab:
    def __init__(self) :
	mainvbox=VBox(0,1)
	mainvbox.set_border_width(4)
	mainvbox.set_spacing(4)
	self.mainvbox=mainvbox
	mainvbox.pack_start(Label(_("Keyboard Sounds")),0,0,8)	

	mainframe=Frame()
	mainframe.set_label(_("Keyboard Click"))
	self.clickcheck=CheckButton(" "+_("Allow keyboard clicks"))
	TIPS.set_tip(self.clickcheck,_("Allow keyboard clicks"))
	self.clickcheck.set_active(1)
	
	chb=HBox(0,0)
	chb.set_spacing(3)
	chb.pack_start(Label(_("Volume")+" "),0,0,0)
	self.adj1=Adjustment(5,0,100,1,1,1)
	c=HScale(self.adj1)
	TIPS.set_tip(c,_("Volume"))
	c.set_digits(0)
	c.set_draw_value(1)
	c.set_update_policy(UPDATE_DISCONTINUOUS)
	c.set_value_pos(POS_TOP)
	cbox=VBox(0,0)	
	cbox.set_spacing(8)
	cbox.set_border_width(10)
	chb.pack_start(c,1,1,0)
	cbox.pack_start(self.clickcheck,1,1,0)
	cbox.pack_start(chb,1,1,0)
	cbox.show_all()
	mainframe.add(cbox)
	mainvbox.pack_start(mainframe,1,1,5)

	mainframe2=Frame()
	mainframe2.set_label(_("Keyboard Beep"))
	chb1=HBox(0,0)
	chb1.set_spacing(3)
	chb1.pack_start(Label(_("Volume")+" "),0,0,0)
	self.clickcheck1=CheckButton(" "+_("Allow keyboard beeps"))
	TIPS.set_tip(self.clickcheck1,_("Allow keyboard beeps"))
	self.clickcheck1.set_active(1)
	self.adj2=Adjustment(50,0,100,1,1,1)
	c2=HScale(self.adj2)
	chb1.pack_start(c2,1,1,0)
	TIPS.set_tip(c2,_("Volume"))
	c2.set_digits(0)
	c2.set_draw_value(1)
	c2.set_update_policy(UPDATE_DISCONTINUOUS)
	c2.set_value_pos(POS_TOP)

	chb2=HBox(0,0)
	chb2.set_spacing(3)
	chb2.pack_start(Label(_("Pitch")+" (hz) "),0,0,0)
	self.adj3=Adjustment(400,1,2000,1,1,1)
	c3=HScale(self.adj3)
	chb2.pack_start(c3,1,1,0)
	TIPS.set_tip(c3,_("Pitch")+" (hz)")
	c3.set_digits(0)
	c3.set_draw_value(1)
	c3.set_update_policy(UPDATE_DISCONTINUOUS)
	c3.set_value_pos(POS_TOP)

	chb3=HBox(0,0)
	chb3.set_spacing(3)
	chb3.pack_start(Label(_("Duration")+" (ms) "),0,0,0)
	self.adj4=Adjustment(100,1,800,1,1,1)
	c4=HScale(self.adj4)
	chb3.pack_start(c4,1,1,0)
	TIPS.set_tip(c4,_("Duration")+" (ms)")
	c4.set_digits(0)
	c4.set_draw_value(1)
	c4.set_update_policy(UPDATE_DISCONTINUOUS)
	c4.set_value_pos(POS_TOP)

	cbox2=VBox(0,0)	
	cbox2.set_spacing(10)
	cbox2.set_border_width(10)
	cbox2.pack_start(self.clickcheck1,1,1,0)
	cbox2.pack_start(chb1,1,1,0)
	cbox2.pack_start(chb2,1,1,0)
	cbox2.pack_start(chb3,1,1,0)
	testbutt=Button()
	butbox=HBox(0,0)
	butbox.set_border_width(2)
	butbox.set_spacing(3)
	lab=Label(" "+_("Test")+"  ")
	try:
		butbox.pack_start(loadScaledImage(getPixDir()+"ism_choosesnd.png",24,24),0,0) 
	except:
		lab=Label("     "+_("Test")+"     ")
	butbox.pack_start(lab,1,1,0)
	testbutt.add(butbox)
	TIPS.set_tip(testbutt,_("Test"))
	testbutt.connect("clicked",self.runTest)
	bhb=HBox(0,0)
	bhb.pack_start(testbutt,0,0,0)
	bhb.pack_start(Label(" "),1,1,0)
	cbox2.pack_start(bhb,0,0,0)
	cbox2.show_all()
	mainframe2.add(cbox2)
	mainvbox.pack_start(mainframe2,1,1,5)

	for ii in [self.adj1,self.adj2, self.adj3,self.adj4]:
		ii.connect("value_changed",self.doApply)

	self.clickcheck.connect("clicked",self.doApply)
	self.clickcheck1.connect("clicked",self.doApply)
	for ii in [chb1,chb2,chb3,chb]:
		ii.get_children()[0].set_alignment(0.0,1.0)
	abutton=Button(_("Apply"))
	TIPS.set_tip(abutton,_("Apply"))
	rbutton=Button(_("Reset"))
	TIPS.set_tip(rbutton,_("Reset"))
	cbutton=Button(_("Close"))
	TIPS.set_tip(cbutton,_("Close"))
	hb=HBox(0,0)
	hb.pack_start(abutton,1,1,0)
	hb.pack_start(rbutton,1,1,0)
	hb.pack_start(cbutton,1,1,0)
	hb.set_spacing(4)
	hb.set_border_width(2)
	mainvbox.pack_start(hb,0,0,2)
	abutton.connect("clicked",self.doApply)
	rbutton.connect("clicked",self.doReset)
	cbutton.connect("clicked",reapplySettings)
	mainvbox.show_all()

    def runTest(self,*args) :
	GDK.beep()  # test the keyboard beep

    def doReset(self,*args) : # reset to a reasonable speed
	global KB_SETTINGS
	os.popen("xset c on").readlines()  # click on
	os.popen("xset c 5").readlines()
	os.popen("xset b on").readlines()  # bell on
	os.popen("xset b 50 400 100").readlines()
	KB_SETTINGS[1]="xset b on"
	KB_SETTINGS[2]="xset b 50 400 100"
	KB_SETTINGS[3]="xset c on"
	KB_SETTINGS[4]="xset c 5"
	self.adj4.set_value(100)
	self.adj3.set_value(400)
	self.adj2.set_value(50)
	self.adj1.set_value(5)
	self.clickcheck.set_active(1)
	self.runTest()

    def doApply(self,*args) : # click and beep
	#print "doApply"
	global KB_SETTINGS
	if self.clickcheck1.get_active():
		os.popen("xset b on").readlines()  # bell on
		KB_SETTINGS[1]="xset b on"
		os.popen("xset b "+str(int(self.adj2.value))+" "+str(int(self.adj3.value))+" "+str(int(self.adj4.value))).readlines()
		KB_SETTINGS[2]="xset b "+str(int(self.adj2.value))+" "+str(int(self.adj3.value))+" "+str(int(self.adj4.value))
	else:
		os.popen("xset -b").readlines()  # bell off
		KB_SETTINGS[1]="xset -b"
		KB_SETTINGS[2]=""
	if self.clickcheck.get_active():
		os.popen("xset c on").readlines()  # click on
		os.popen("xset c "+str(int(self.adj1.value))).readlines()
		KB_SETTINGS[3]="xset c on"
		KB_SETTINGS[4]="xset c "+str(int(self.adj1.value))
	else:
		os.popen("xset -c").readlines()  # click off
		KB_SETTINGS[3]="xset -c"
		KB_SETTINGS[4]=""



###################
## Keyboard - main class
###################
class keywin:
    def __init__(self) :
	self.version=this_software_version
	cwin=Window()
	cwin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(cwin)
	cwin.set_wmclass("icewmcp-keyboard","icewmcp-Keyboard")
	cwin.realize()
	cwin.set_title(_("IceWM CP - Keyboard Settings")+" "+self.version)
	cwin.set_position(WIN_POS_CENTER)
	self.cwin=cwin

	self.vbox=VBox(0,0)

	menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
				(_('/_File')+"/_"+_("Open Shortcut Key Configuration")+"...", '<control>O', self.openKey, 0, ''),
				(_('/File/_Apply Changes Now...'), "<control>A", restart_ice, 0, ''),
				(_('/File/sep1'), None, None, 1, '<Separator>'),
 				(_("/_File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
 				(_("/_File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
				(_('/File/sep1'), None, None, 1, '<Separator>'),
				(_('/File/_Exit'), '<control>Q', reapplySettings, 0, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About...'), "F2", self.do_about, 0, ''),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5013, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5013, ""),
					]

	ag = AccelGroup()
	itemf = ItemFactory(MenuBar, '<main>', ag)
	self.ag=ag
	self.itemf=itemf
	cwin.add_accel_group(ag)
	itemf.create_items(menu_items)
	self.menubar = itemf.get_widget('<main>')	

	# added 6.21.2003 - "run as root" menu selector
	self.leftmenu=self.menubar.get_children()[0].get_submenu()
	self.run_root_button=CheckMenuItem(" "+RUN_AS_ROOT)
	self.leftmenu.prepend(self.run_root_button)
	self.run_root_button.connect("toggled",self.run_as_root)

	vbox1=VBox(0,0)
	vbox=self.vbox
	vbox.set_border_width(4)
	vbox1.pack_start(self.menubar,0,0,0)
	vbox1.pack_start(vbox,1,1,0)
	vbox.pack_start(getImage(getBaseDir()+"icewmcp.png",DIALOG_TITLE),0,0,1)
	self.title_lab=Label(_("Keyboard"))
	vbox.pack_start(self.title_lab,0,0,1)
	vbox.set_spacing(2)
	notebook = Notebook()
	self.notebook=notebook
	notebook.set_tab_pos(POS_TOP)
	notebook.set_scrollable(TRUE)
	vbox.pack_start(notebook,1,1,2)
	global KEY_TAB
	keywinta=keywintab()
	KEY_TAB=keywinta
	global BELL_TAB
	BELL_TAB=keysoundtab()
	global SHORT_TAB
	short_tab=keypanel(0)
	SHORT_TAB=short_tab
	global ICE_TAB
	ICE_TAB=icepref.PullTab("Key Bindings")
	icetab=ICE_TAB.get_tab()
	icepan=VBox(0,0)
	icepan.set_spacing(3)
	icepan.pack_start(Label(_("Additional IceWM Shortcut Keys")),0,0,3)
	icepan.pack_start(icetab,1,1,0)
	actstr=_('/File/_Apply Changes Now...')[_('/File/_Apply Changes Now...').rfind("/")+1:len(_('/File/_Apply Changes Now...'))].replace("_","").replace(".","").strip()
	abutt=Button(" "+actstr+" ")
	abutt.connect("clicked",restart_ice)
	TIPS.set_tip(abutt,actstr)
	ccbutton=Button(_("Close"))
	TIPS.set_tip(ccbutton,_("Close"))
	ccbutton.connect("clicked",reapplySettings)
	hbox1=HBox(1,0)
	hbox1.set_border_width(3)
	hbox1.set_spacing(5)
	hbox1.pack_start(abutt,1,1,0)
	hbox1.pack_start(ccbutton,1,1,0)
	icepan.pack_start(hbox1,0,0,2)

	notebook.append_page(keywinta.mainvbox, Label(_("Repetition")))
	notebook.append_page(BELL_TAB.mainvbox, Label(_("Sound")))
	notebook.append_page(short_tab.createPanel(0), Label(_("Shortcut Keys")))
	notebook.append_page(icepan, Label(_("IceWM Keys")))

	short_tab.appbutt.connect("clicked",restart_ice)
	cwin.set_default_size(435,500)
	cwin.add(vbox1)
	cwin.connect("destroy",reapplySettings)
	global C_WINDOW
	C_WINDOW=cwin
	cwin.show_all()

    def openKey(self,*args):
	self.notebook.set_current_page(2)
	global SHORT_TAB
	SHORT_TAB.openKey()

    def run_as_root(self,*args):
	# added 6.22.2003 - Run As Root functionality
	global ICE_TAB
	global SHORT_TAB
	if self.run_root_button.get_active():
		ICE_TAB.run_as_root(1)
		SHORT_TAB.run_as_root(1)
		self.cwin.set_title(_("IceWM CP - Keyboard Settings")+" "+self.version+"   [ROOT]")
		self.title_lab.set_text(_("Keyboard")+"   [ROOT]")
	else:
		ICE_TAB.run_as_root(0)
		SHORT_TAB.run_as_root(0)
		self.cwin.set_title(_("IceWM CP - Keyboard Settings")+" "+self.version)
		self.title_lab.set_text(_("Keyboard"))
	self.menubar.deactivate()
	

    def do_about(self,*args):
	commonAbout(_("IceWM CP - Keyboard Settings"),_("IceWM CP - Keyboard Settings")+" "+self.version+" "+_("for IceWM (written in 100% Python).")+"\n\n"+_("About IceWM CP - Key Editor")+" "+self.version+"\n\n"+_("A simple Gtk-based key configuration utility\nfor IceWM (written in 100% Python).\n\nThis program is distributed free\nof charge (open source) under the GNU\nGeneral Public License."))



# main methods
def run(doquit=1) :
	global DO_QUIT
	DO_QUIT=doquit	
	keywin()
	hideSplash()
	if doquit==1: gtk.mainloop()


if __name__== "__main__" :
	run()

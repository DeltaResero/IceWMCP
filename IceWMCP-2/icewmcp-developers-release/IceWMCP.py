#! /usr/bin/env python

######################################
# IceWM Control Panel  
# 
# Copyright 2003 by Erica Andrews 
# (PhrozenSmoke@yahoo.com)
# http://icesoundmanager.sourceforge.net
# 
# A simple Gtk-based control panel for IceWM - for people 
# that prefer Gtk over the Qt-based "IceCC". It is 
# modular, easy to use, with a Windows Control Panel like
# look. Although created for IceWM, it can be easily
# used as a control panel for any other window manager.
#
# This program is distributed under the GNU General
# Public License (open source).
# 
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

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py


global APPLET_DIRECTORY
APPLET_DIRECTORY=None

class controlwin:
    def __init__(self,use_loader=0) :
	self.use_loader=use_loader
	global WMCLASS
	WMCLASS="icewmcontrolpanel"
	global WMNAME
	WMNAME="IceWMControlPanel"
	self.version=this_software_version
	controlwin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(controlwin)
	controlwin.set_wmclass(WMCLASS,WMNAME)
	controlwin.realize()
	controlwin.set_title(_("IceWM Control Panel"))
	controlwin.set_position(WIN_POS_CENTER)
	self.controlwin=controlwin
	mainvbox1=VBox(0,1)
	mainvbox1.set_spacing(1)
	mainvbox=VBox(0,1)
	mainvbox.set_spacing(0)
	mymenubar=MenuBar()
	self.mymenubar=mymenubar

        ag=AccelGroup()
        itemf=ItemFactory(MenuBar, "<main>", ag)
	self.itemf=itemf
	self.ag=ag
        itemf.create_items([
            # path              key           callback    action#  type
  (_("/ _File"),  "<alt>F",  None,  0,"<Branch>"),
  (_("/ _File/_Refresh View"), "<control>V", self.refreshAppletView,2,""),
  (_("/ _File/_Configuration..."), "<control>C", self.showConfig,4,""),
  (_("/ _File/sep4"), None,  None,  49, "<Separator>"),
 				(_("/ _File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
  (_("/ _File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
  (_("/ _File/sep4"), None,  None,  49, "<Separator>"),
  (_("/ _File/_Quit"), "<control>Q", self.doQuit,10,""),
  (_("/_View"),  "<alt>V",  None,  0,"<Branch>"),   # add to .pot
  (_("/_View/_Icon View"),  "<control>I",  self.iconView,  0,""),   # add to .pot
  (_("/_View/_List View"),  "<control>L",  self.listView,  0,""),   # add to .pot
  (_("/_View")+"/_"+_("Column View"),  "<control>B",  self.columnView,  0,""),   # add to .pot
  (_("/_Help"),  "<alt>H",  None,16, "<LastBranch>"), 
  (_("/_Help/_About IceWM Control Panel..."), "F2", self.doAbout,17, ""),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5000, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5000, ""),
        ])

        controlwin.add_accel_group(ag)
        mymenubar=itemf.get_widget("<main>")
        mymenubar.show()
	self.mymenubar=mymenubar
	mainvbox1.pack_start(mymenubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,0)

	titlebar=HBox(0,0)
	titlebar.set_spacing(0)
	mainvbox.pack_start(titlebar,0,0,0)
	titlebar.pack_start(Label(" "),1,1,0)
	titlebar.pack_start(getImage(getBaseDir()+"icewmcp.png","IceWM Control Panel"),0,0,0)
	titlebar.pack_start(Label(" "),1,1,0)

	try:   # added 5.6.2003 - add a 'button box' for changing views
		buttonbox=VBox(0,0)
		buttonbox.set_spacing(0)
		for buttons in  [ ['view_icon.png',_("/_View/_Icon View"),self.iconView] , ['view_list.png',_("/_View/_List View"), self.listView] , ['view_col.png',_("Column View"),self.columnView]]:
			# seem complicated, but needed to use already gettext-translated strings
			butname=buttons[1]
			butname=butname[butname.rfind("/")+1:len(butname)].replace("_","").strip()
			bicon=Button()
			bicon.add(loadScaledImage(getBaseDir()+buttons[0],20,20))
			bicon.connect("clicked",buttons[2])
			bicon.set_relief(2)
			TIPS.set_tip(bicon,butname)
			buttonbox.pack_start(bicon,1,1,0)
		titlebar.pack_start(buttonbox,0,0,2)
	except:
		pass

	sc=ScrolledWindow()
	glayout=Layout()
	self.glayout=glayout
	self.sc=sc
	self.LIST_VIEW=0
	self.readView()
	self.ignore_list=[]
	self.loadIgnoreList()
	self.refreshAppletView()
	sc.add(glayout)
	mainvbox.pack_start(sc,1,1,0)

	mainvbox.set_border_width(3)
	controlwin.add(mainvbox1)
	#controlwin.set_default_size(450,375)
	controlwin.connect("destroy",self.doQuit)
	controlwin.show_all()
	try:
		if not os.path.exists(os.environ["HOME"]+os.sep+".icecp_ignore"):
			msg_info(DIALOG_TITLE,_("HINT: Use SINGLE clicks instead of double-clicks.\nYou will not see this message again."))
			os.popen("touch "+os.environ["HOME"]+os.sep+".icecp_ignore")
	except:
		pass

    def saveView(self):  # added in version 0.3
	try:
		f=open(os.environ["HOME"]+os.sep+".icewmcp_view","w")
		f.write(str(self.LIST_VIEW))
		f.flush()
		f.close()
	except:
		pass

    def readView(self):  # added in version 0.3
	try:
		f=open(os.environ["HOME"]+os.sep+".icewmcp_view")
		self.LIST_VIEW=int(f.read().replace("\n","").replace("\t","").replace("\r","").strip())
	except:
		self.LIST_VIEW=0

    def listView(self,*args) :  # added in version 0.3
	self.LIST_VIEW=1
	self.refreshAppletView()
	self.saveView()

    def iconView(self,*args) :  # added in version 0.3
	self.LIST_VIEW=0
	self.refreshAppletView()
	self.saveView()

    def columnView(self,*args) :  # added in version 2.3
	self.LIST_VIEW=2
	self.refreshAppletView()
	self.saveView()

    def showConfig(self,*args) :
	applets=self.loadApplets()
	alist=applets.keys()
	alist.sort()
	global WMCLASS
	global WMNAME
	confwin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(confwin)
	confwin.set_wmclass(WMCLASS,WMNAME)
	confwin.realize()
	confwin.set_title(_("IceWM Control Panel"))
	confwin.set_position(WIN_POS_CENTER)
	mainvbox=VBox(0,1)
	mainvbox.set_spacing(2)
	mainvbox.pack_start(Label(_("  Choose which icons to hide or show:  ")),0,0,3)
	sc=ScrolledWindow()
	gl=Layout()
	max_x=5
	max_y=3
	yspacing=8
	for ii in alist:
		myapp=applets[ii]
		hb=HBox(0,0)
		hb.set_spacing(3)
		cb=CheckButton(_("Hide"))				
		TIPS.set_tip(cb,_("Hide"))
		if myapp.get_data("my_name") in self.ignore_list:
			myapp.set_data("ignored",1)
			cb.set_active(1)
		else: 
			myapp.set_data("ignored",0)
		cb.set_data("applet",myapp)
		cb.connect("clicked",self.doToggle)
		hb.pack_start(myapp,0,0,0)
		hb.pack_start(cb)
		hb.show_all()
		gl.put(hb,4,max_y)
		if max_x<hb.size_request()[0]: max_x=max_x<hb.size_request()[0]
		max_y=max_y+hb.size_request()[1]+yspacing
	gl.set_size(max_x+3,max_y+3)
	sc.add(gl)
	mainvbox.pack_start(sc,1,1,0)
	mainvbox.set_border_width(4)
	hb2=HBox(0,0)
	hb2.set_spacing(10)
	sbutton=getPixmapButton(None, STOCK_SAVE ,_("Save"))
	TIPS.set_tip(sbutton,_("Save"))
	cbutton=getPixmapButton(None, STOCK_CANCEL ,DIALOG_CANCEL)
	TIPS.set_tip(cbutton,DIALOG_CANCEL)
	sbutton.connect("clicked",self.saveConfig)
	sbutton.set_data("applets",applets)
	cbutton.set_data("window",confwin)
	sbutton.set_data("window",confwin)
	cbutton.connect("clicked",self.destroyConfig)
	hb2.pack_start(sbutton,1,1,0)
	hb2.pack_start(cbutton,1,1,0)	
	mainvbox.pack_start(hb2,0,0,5)
	confwin.connect("destroy",self.destroyConfig)
	confwin.add(mainvbox)
	confwin.set_modal(1)
	confwin.set_default_size(275,400)
	confwin.show_all()

    def saveConfig(self,*args) :
	if not args[0].get_data("applets")==None:
		self.ignore_list=[]
		for ii in args[0].get_data("applets").values():
			if ii.get_data("ignored")==1:
				ig=ii.get_data("my_name")
				if not ig in self.ignore_list: self.ignore_list.append(ig)
		self.saveIgnoreList()
		self.refreshAppletView()
		args[0].get_data("window").destroy()
		args[0].get_data("window").unmap()

    def destroyConfig(self,*args) :
	if not args[0].get_data("window")==None:
		args[0].get_data("window").destroy()
		args[0].get_data("window").unmap()
		return
	args[0].destroy()
	args[0].unmap()

    def doToggle(self,*args) :
	args[0].get_data("applet").set_data("ignored", args[0].get_active()==1 )
	#print str(args[0].get_data("applet").get_data("ignored"))

    def saveIgnoreList(self,*args) :
	try:
		igfile=os.environ["HOME"]+os.sep+".icecp_ignore"
		f=open(igfile,"w")
		for ii in self.ignore_list:
			f.write(ii.replace("\n","\\n")+"\n")
		f.flush()
		f.close()
	except:
		pass

    def loadIgnoreList(self,*args) :
	try:
		igfile=os.environ["HOME"]+os.sep+".icecp_ignore"
		f=open(igfile)
		ff=f.read()
		f.close()
		flist=ff.split("\n")
		for ii in flist:
			if not len(ii.strip())>0: continue
			if ii.find("#")>-1: continue
			if not ii in self.ignore_list: self.ignore_list.append(ii.replace("\\n","\n"))
	except:
		pass

    def doQuit(self,*args) :
	self.saveView()
	gtk.mainquit()

    def doAbout(self,*args) :
	commonAbout(_("About IceWM Control Panel"), _("IceWM Control Panel")+" "+self.version+"\n\n"+_("A simple Gtk-based control panel for IceWM - for people that prefer Gtk over the Qt-based 'IceCC'. It is modular, easy to use, with a Windows Control Panel like look. Although created for IceWM, it can be easily used as a control panel for any other window manager. It is highly configurable, and control panel applets can be created easily (simple text files).\n\nThis program is distributed under the GNU General Public License (open source).")  )


    def refreshAppletView(self,*args) :
	myapplets=self.loadApplets(self.LIST_VIEW)
	self.myapplets=myapplets
	c=self.glayout.get_children()
	for ii in c:
		try:
			self.glayout.remove(ii)
		except:
			pass
	self.displayApplets(myapplets)
	if self.LIST_VIEW==1:  # list view
		self.controlwin.set_default_size(385,395)
		self.controlwin.set_size_request(385,395)
	elif self.LIST_VIEW==2:  # column view
		self.controlwin.set_default_size(500,395)
		self.controlwin.set_size_request(500,395)
	else: 
		self.controlwin.set_default_size(450,395)
		self.controlwin.set_size_request(450,395)

    def displayApplets(self,applet_dict) :
	startx=5
	starty=3
	yspacing=12
	spacing=10
	movex=startx
	movey=starty
	totalx=startx
	totaly=starty
	col_count=0
	max_y=starty
	a_list=applet_dict.keys()
	a_list.sort()
	col_x=0
	for ii in a_list:  # get the width of the widest applet, 5/6/2003
		applet=applet_dict[ii]
		if applet.get_data("my_size")[0] > col_x: col_x=applet.get_data("my_size")[0]
	colBreak=4
	if self.LIST_VIEW==1:  # list view
		colBreak=1
		yspacing=4
	if self.LIST_VIEW==2:  # column view
		colBreak=2
		yspacing=4
	for ii in a_list:
		applet=applet_dict[ii]
		if applet.get_data("my_name") in self.ignore_list: continue
		self.glayout.put(applet,movex,movey)
		movex=movex+applet.get_data("my_size")[0]+spacing
		if self.LIST_VIEW==2: movex=5+col_x+spacing
		if applet.get_data("my_size")[1]>max_y: max_y=applet.get_data("my_size")[1]
		col_count=col_count+1
		if col_count==colBreak:
			movey=movey+max_y+yspacing
			totaly=movey
			max_y=starty
			col_count=0
			if movex>totalx: totalx=movex
			movex=startx
	totaly=totaly+max_y+yspacing
	self.glayout.set_size(totalx,totaly)
	
    def loadApplets(self,list_view=0) :  # load .cpl files
	myapplets={}
	global APPLET_DIRECTORY
	try:
	  #added 2.23.2003 - allow international (foreign language applets), based on the person's set language in os.environ["LANG"]
	  # English applets are in ./applets/, Spanish applets in  ./applets/es/ , French applets would be in ./applets/fr/ , etc.	  

	  try:
		if APPLET_DIRECTORY==None:  # set it once
			APPLET_DIRECTORY=getBaseDir()+"applets"+os.sep   # default is top applet directory, English
			# try the locale-specific sub-directory for applets: icewmcp_common -> getLocaleDir
			if len(glob.glob(APPLET_DIRECTORY+getLocaleDir()+"*.cpl"))>0:  # make sure this language directory exists and has applets
				APPLET_DIRECTORY=APPLET_DIRECTORY+getLocaleDir()
	  except:
		APPLET_DIRECTORY=getBaseDir()+"applets"+os.sep

	  #print APPLET_DIRECTORY
	  flist=glob.glob(APPLET_DIRECTORY+"*.cpl")  # changed 2.23.2003 - use glob.glob()  instead of os.listdir()
	  for ii in flist:
	     try:
		if not ii.lower().endswith(".cpl"): continue
		f=open(ii)
		ff=f.read()
		f.close()
		mylist=ff.split("\n")
		a_name=""
		a_exec=""
		a_icon="default.xpm"
		a_tip=""
		for yy in mylist:
			yy=yy.replace("\t"," ").replace("  "," ").replace("\r","").strip()
			if yy.startswith("#"): continue
			if yy.find("=")==-1: continue
			ypair=yy.split("=")
			if len(ypair)==2:
				yname=ypair[0].strip().lower()
				yval=ypair[1].strip()
				if yname=="name": a_name=yval.replace("\\n","\n")
				if yname=="exec": a_exec=yval
				if yname=="icon": a_icon=yval
				if yname=="hint": a_tip=yval
				if (len(a_exec)>0) and (len(a_name)>0): myapplets[a_name.replace("\n"," ").lower()]=self.getCPIcon(a_icon,a_name,a_exec,a_tip,list_view)				
	     except:
		pass
	except:
	  pass
	return myapplets


    def checkAvail(self,to_run) :  # added, 5/6/2003 - check for availability of applet programs
	appc=str(to_run)
	if appc.startswith("python "): # 'internal' applets

		# we can check for the 'existence' if internal applets on static binary 
		# versions of IceWMCP, because the actual .py files are embedded in the 
		# 'icewmcp' executable, and don't exist as actual 'files' on the file system.
		# The alternatives are to: 1. assume all 'internal' applets exist   or 
		# 2. implement some expensive 'import' test, which will greatly slow down
		# the launching of the applet and possibly create unknown/unwanted 
		# side effects....so, for static-binary versions, we will simply ASSUME that 
		# all internal applets 'exist' - since there is no way for the use to 
		# 'delete' internal applets without deleting the 'icewmcp'
		# executable itself , except 'plugins'

		appc=appc.replace("python ","")		
		if IS_STATIC_BINARY=='yes':
			found_one=0
			plugins=['IceWMCPSystem.py']  # list used, for future compat. with new plugins
			for ii in plugins:
				if appc.find(ii)>-1:
					found_one=1  # found a plugin, stay in this method and check for existence
					break
			if found_one==0: return 1 # this isn't a plugin, just assume it exists

	appc=appc.strip()
	if appc.find(" ")>-1:  # clip any 'command-line args', i.e. 'icepref module=Themes'
		appc=appc[0:appc.find(" ")].strip()

	if appc.find(os.sep)==-1: # stuff with no path given...i.e. 'userinfo'
		try:
			if os.path.exists(getBaseDir()+appc): return 1
		except:
			pass
		try:
			for ii in os.environ['PATH'].split(":"):
				if os.path.exists(ii+os.sep+appc): return 1
		except:
			pass
	else:
		try:  # full path was given, just check to see if it exists on the fs
			return os.path.exists(appc)
		except:
			pass
	return 0

    def runApplet(self,*args) :
	if len(args)<1: return
	try:
		to_run=args[0].get_data("my_app")
		if self.use_loader==1:
			to_run=to_run.replace("[PHROZEN-INTERNAL]",sys.argv[0]+" ").replace("[EQUAL]","=")
		else:
			to_run=to_run.replace("[PHROZEN-INTERNAL]","python  "+getBaseDir()).replace("[EQUAL]","=")
		if not to_run==None:
			if not self.checkAvail(to_run)==1:
				if to_run.find("IceWMCPSystem")>-1:
					msg_err(DIALOG_TITLE,_("You do not have the extra IceWMCPSystem program installed.  You must first download it from")+":\n\n"+"http://icesoundmanager.sourceforge.net")
				else:
					msg_err(DIALOG_TITLE,_("The program this applet points to does not exist on your system.")+"\n\n"+to_run)
				return  # program not available, return
			os.popen(to_run+" &> /dev/null &")
	except:
		pass

    def getCPIcon(self,micon,mdesc,mexec,mtooltip,listvw=0) :
	newwidth=40
	newh=40
	listview=listvw
	if listvw==2: listview=1
	if listview==1: newwidth=newh=22

	# added 6.8.2003 - load an appropriate font for Russian locale
	# This should help fix a bug reported by Vasya, where applets didn't 
	# appear correctly on Russian locale on Mandrake, probably because 
	# loading a Helvetica font with a 'wildcard' instead of 'cronyx' probably 
	# loaded a regular english-latin language font, So, let's explicitly load 
	# a Russian 'cronyx' font when running under Russian locale, and 
	# create a dictionary for looking up 'special' fonts in the future...Finnish?

	# These are 'default' fonts: seem to work well with English, Spanish
	font1="Arial 10"  # big applets
	font2="Helvetica 9"  # small applets: lists/columns

	# some locales use more than one font, like Chinese
	rc_style=None

	mylocale=getLocaleDir().replace(os.sep,"").lower()

	APPLET_DIRECTORY=getBaseDir()+"applets"+os.sep   # default is top applet directory, English
	# try the locale-specific sub-directory for applets: icewmcp_common -> getLocaleDir
	# Will only load special fonts if the applets for this locale are there...
	if len(glob.glob(APPLET_DIRECTORY+getLocaleDir()+"*.cpl"))>0: 
		APPLET_DIRECTORY=APPLET_DIRECTORY+getLocaleDir()
		if special_fonts_map.has_key(mylocale):
			font1=special_fonts_map[mylocale][0]
			font2=special_fonts_map[mylocale][1]

	p=loadScaledImage(getBaseDir()+"applet-icons"+os.sep+str(micon),newh,newwidth)
	if p==None: p=loadScaledImage(getBaseDir()+"applet-icons"+os.sep+"default.xpm",newh,newwidth)
	relief=2

	if rc_style==None: 
			if listview==1: MYFONT=font1 
			else: MYFONT=font2
	if p:
		if listview==1:  v=HBox(0,0)
		else: v=VBox(0,0)
		v.set_spacing(1)
		v.pack_start(p,0,0,0)
		if listview==1:		labname=Label(to_utf8("  "+str(mdesc).replace("\n"," ").replace("\r"," ").replace("\t"," ").replace("  "," ").replace(" -","-").replace("- ","-").strip()))
		else:		labname=Label(to_utf8(str(mdesc).strip()))
		try:			
			if rc_style==None: 				
				#style =labname.get_style().copy()				
				#cont=labname.get_pango_context()
				#cont.load_fontset(MYFONT, mylocale)
				#lang=pango.pango_language_from_string("en_US")
				#layo=labname.get_layout()
				#attr=pango.AttrList()
				#attr.insert(pango.AttrLanguage(lang))
				#layo.set_attributes(attr)
				#print "LOC: "+mylocale
				#cont.set_language(lang)
				#cont.set_font_description(pango.FontDescription(MYFONT))
				#print "MYFONT: "+MYFONT
				labname.modify_font(pango.FontDescription(MYFONT))
			else: rc_parse_string(rc_style)
			labname.ensure_style()
		except:
			#print "ERR"
			pass

		v.pack_start(labname,0,0,0)
		v.show_all()
		if listvw==1: v.set_size_request(445,-1)
		elif listvw==2: v.set_size_request(v.size_request()[0]+8,v.size_request()[1]+3)
		else: v.set_size_request(90,-1)
		
		b=Button()
		b.add(v)
		b.set_relief(relief)
		b.show_all()
	else:
		if listview==1: b=Button(to_utf8("  "+str(mdesc).replace("\n"," ").replace("\r"," ").replace("\t"," ").replace("  "," ").replace(" -","-").replace("- ","-").strip()))
		else: b=Button(to_utf8(str(mdesc).strip()))
		try:
			labname=b.get_children()[0]			
			if rc_style==None: 
				style =labname.get_style().copy()
				labname.modify_font(pango.FontDescription(MYFONT))
			else: rc_parse_string(rc_style)			
			labname.ensure_style()
		except:
			pass
		b.set_relief(relief)
		b.show_all()
	b.set_data("my_size",b.size_request())
	b.set_data("my_app",str(mexec).strip())
	b.set_data("my_name",str(mdesc).strip())
	if len(str(mtooltip).strip())>0: TIPS.set_tip(b,to_utf8(str(mtooltip).strip()))
	b.connect("clicked",self.runApplet)
	return b

#### Main methods ####


def run(use_load=0) :
	controlwin(use_load)
	hideSplash()
	gtk.mainloop()

if __name__== "__main__" :
	run()
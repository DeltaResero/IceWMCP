#! /usr/bin/env python

#############################
#  IceWM Control Panel - Hardware and 
#  System Information Viewer
#  
#  Copyright (c) 2003 by Erica Andrews
#  PhrozenSmoke@yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

global ADDITIONAL_INFO
ADDITIONAL_INFO=[]

import random,string,copy


#sys.path.append("/Compile/IceWMCP")

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateHW(somestr))  # from icewmcp_common.py

from icewmcphw import *
import DndCTree
from constants import *


def getHwIconDir():
	return getPixDir()+"hw-pixmaps"+os.sep


class hardwaregui:
    def __init__(self):
	self.version="1.4-beta"
	hideSplash()

	self.locales= {
"bokmal":"no_" ,
"bokmål":"no_" ,
"catalan":"ca_" ,
"croatian":"hr_" ,
"czech":"cs_" ,
"danish":"da_" ,
"dansk":"da_" ,
"deutsch":"de_" ,
"dutch":"nl_" ,
"english":"en_" ,
"eesti":"et_" ,
"estonian":"et_" ,
"finnish":"fi_" ,
"français":"fr_" ,
"french":"fr_" ,
"galego":"gl_" ,
"galician":"gl_" ,
"german":"de_" ,
"greek":"el_" ,
"hebrew":"he_" ,
"hrvatski":"hr_" ,
"hungarian":"hu_" ,
"icelandic":"is_" ,
"italian":"it_" ,
"japanese":"ja_" ,
"korean":"ko_" ,
"lithuanian":"lt_" ,
"norwegian":"no_" ,
"nynorsk":"nn_" ,
"polish":"pl_" ,
"portuguese":"pt_" ,
"romanian":"ro_" ,
"russian":"ru_" ,
"slovak":"sk_" ,
"slovene":"sl_" ,
"slovenian":"sl_" ,
"spanish":"es_" ,
"español":"es_" ,
"swedish":"sv_" ,
"thai":"th_" ,
"turkish":"tr_" ,
	}

	self.probeOther()
	#hideSplash()
	self.__initWidgets()
	setSplash(self.probeHw, "IceWMCP - "+_("Hardware and System Information")+"\n\n"+_("Collecting system hardware information...please wait."))
	showSplash(1)


    def __initWidgets(self) :

	hwwin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(hwwin)
	hwwin.set_wmclass("icewmcp-hw","IceWMCP-HW")
	self.hwwin=hwwin
	hwwin.realize()
	hwwin.set_title("IceWMCP: "+_("Hardware and System Information"))
	hwwin.set_position(WIN_POS_CENTER)
	mainvbox=VBox(0,0)
	mainvbox.set_border_width(4)
	mainvbox1=VBox(0,0)

	menu_items = [
				(FILE_MENU, None, None, 0, '<Branch>'),
 				(FILE_MENU+"/_"+FILE_RUN,'<control>R', rundlg,421,""),
 				(FILE_MENU+"/_"+UPDATE_MENU, '<control>U', checkSoftUpdate,420,""),
				(FILE_MENU+'/sep1', None, None, 1, '<Separator>'),
				(EXIT_MENU, '<control>Q', self.doQuit, 0, ''),

				('/_'+_('Tools'), None, None, 0, '<Branch>'),
 				('/_'+_('Tools')+'/'+_('Configure Keyboard')+"...", '<control>K', self.menu_cb,530,""),
 				('/_'+_('Tools')+'/'+_('Configure Mouse')+"...", '<control>M', self.menu_cb,531,""),
 				('/_'+_('Tools')+'/'+_('Configure PC Cards')+"...", '<control>P', self.menu_cb,532,""),
 				('/_'+_('Tools')+'/'+_('Eject')+"/"+_('CD-ROM'), None, self.menu_cb,533,""),
 				('/_'+_('Tools')+'/'+_('Eject')+"/"+_('Floppy'), None, self.menu_cb,534,""),
 				('/_'+_('Tools')+'/'+_('Eject')+"/"+_('SCSI'), None, self.menu_cb,535,""),
 				('/_'+_('Tools')+'/'+_('Eject')+"/"+_('Tape'), None, self.menu_cb,536,""),

				(HELP_MENU, None, None, 0, '<LastBranch>'),
				(ABOUT_MENU, "F2", self.do_about, 0, ''),
  (HELP_MENU+"/_"+APP_HELP_STR, "F4", displayHelp,5014, ""),
  (HELP_MENU+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),

  # no bug reporting - this is an 'unsupported' plug-in
  # (HELP_MENU+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5014, ""),

					]

	ag = AccelGroup()
	itemf = ItemFactory(MenuBar, '<main>', ag)
	self.ag=ag
	self.itemf=itemf
	hwwin.add_accel_group(ag)
	itemf.create_items(menu_items)
	self.menubar = itemf.get_widget('<main>')
	mainvbox1.pack_start(self.menubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,2)

	mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png","IceWM Control Panel"),0,0,2)

	mainvbox.pack_start(Label(_("Hardware and System Information")),0,0,4)

	hpaned=HPaned()
	hpaned.set_position(315)
	self.hpaned=hpaned
	scrolledleft=ScrolledWindow()
	scrolledleft.set_policy(POLICY_ALWAYS,POLICY_ALWAYS)
	self.scrolledleft=scrolledleft
	treeleft=hwtree()
	self.treeleft=treeleft
	scrolledleft.add(treeleft)
	hpaned.add(scrolledleft)
	scrolledright=ScrolledWindow()
	self.textfield=TextView()
	self.textfield.set_wrap_mode(WRAP_WORD)
	scrolledright.add(self.textfield)
	hpaned.add(scrolledright)
	mainvbox.pack_start(hpaned,1,1,2)

	hwwin.add(mainvbox1)
	hwwin.connect("destroy",self.doQuit)

	self.mycats={ 
	"Mouse":_("Mouse and Joystick"),
	"USB":_("USB"),
	"Display":_("Display"),
	"Network":_("Network"),
	"Miscellaneous":_("Miscellaneous"),
	"Keyboard":_("Keyboard"),
	"Modem":_("Modem"),
	"Storage":_("Storage"),
	"Multimedia":_("Multimedia"),
	"Braille":_("Braille"),
	"System":_("System"),
	"Printer":_("Printer"),
	"Camera":_("Cameras, Scanners, and TV"),
	"PCI":_("PCI"),
	"ISAPNP":_("Plug-N-Play"),
	"PCMCIA":_("PCMCIA"),
	"SCSI":_("SCSI"),
	"Firewire":_("Firewire"),
	"Hotplug":_("Hotplug"),
	"Proc":"Proc",
					}

	self.icons={

	"Mouse":"hwmouse.png",
	"USB":"hwusb.png",
	"Display":"hwdisplay.png",
	"Network":"hwnetwork.png",
	"Miscellaneous":"hwunknown.png",
	"Keyboard":"hwkeyboard.png",
	"Modem":"hwmodem.png",
	"Storage":"hwstorage.png",
	"Multimedia":"hwmultimedia.png",
	"Braille":"hwbraille.png",
	"System":"hwsystem.png",
	"Printer":"hwprinter.png",
	"Camera":"hwscanner.png",
	"PCI":"hwpci.png",
	"ISAPNP":"hwisapnp.png",
	"PCMCIA":"hwpcmcia.png",
	"SCSI":"hwscsi.png",
	"Firewire":"hwfirewire.png",
	"Hotplug":"hwhotplug.png",
	"Proc":"hwproc.png",

				  }

	self.special_icons = {
		"cdrom":"hwcdrom.png",
		"cd-rom":"hwcdrom.png",
		"joystick":"hwjoystick.png",
		"jstick":"hwjoystick.png",
		"game control":"hwjoystick.png",
		"dvd":"hwdvd.png",
		"zip":"hwzip.png",
		"ide.":"hwide.png",
		"locale":"hwlocale.png",
		"floppy":"hwfloppy.png",
		"1.44":"hwfloppy.png",
		"camera":"hwcamera.png",
		"webcam":"hwcamera.png",
		"ov511":"hwcamera.png",
		"clock":"hwtimer.png",
		"rtc":"hwtimer.png",
		"timer":"hwtimer.png",
		"x display":"hwx.png",
		"mounts":"hwmounts.png",
		"memory":"hwmemory.png",
		"framebuffer":"hwmemory.png",
		"mtrr":"hwmemory.png",
		"meminfo":"hwmemory.png",
		"iomem":"hwmemory.png",
		"swaps":"hwmemory.png",
		"flash":"hwmemory.png",
		"serial.":"hwserial.png",
		"partitions":"hwpartitions.png",
		"cpu":"hwcpu.png",
		"monitor":"hwmonitor.png",
		"blue tooth":"hwbluetooth.png",
		"bluetooth":"hwbluetooth.png",
								}

	self.cats_order=[   # a preferred order for parsing/organizing hardware

	"Proc",
	"Braille",
	"Mouse",
	"System",
	"Keyboard",
	"Printer",
	"Camera",
	"USB",
	"Display",
	"Network",
	"Modem",
	"Multimedia",
	"Storage",
	"PCMCIA",
	"SCSI",
	"Firewire",
	"Hotplug",
	"ISAPNP",
	"PCI",
	"Miscellaneous"
					]


	self.aliases={ 
	"Mouse":["mouse","ps/2","ps2"],
	"USB":["usb","ohci","uhci","hub"],
	"Display":["monitor","graphics card","framebuffer","xfree","display","locale","language"],
	"Network":["ppp","loopback","network","isdn","ethernet","tuntap"," wifi ","bluetooth"],
	"Miscellaneous":[],
	"Keyboard":["keyboard","Xkbmodel"],
	"Proc":["Hardware Class: proc filesystem"],
	"Modem":["modem"],
	"Storage":["cdrom","cd-rom","floppy","storage","disk"," IDE ","ide."," flash","tape","pda"],
	"Multimedia":["sound","awe64","audio","microphone","dvd","mp3","audio","radio"],
	"Braille":["braille"],
	"System":["cpu","memory","timer","RTC","DMA","PIC","mtrr","bios","apm","vesa","FPU","architecture","SMP"],
	"Printer":["parallel","printer","/dev/lp","inkjet","laserjet","deskjet"],
	"Camera":["camera","ov511","scanner","Hardware Class: tv","dvr","dvb","tv card"," tivo "],
	"PCI":["pci.","Hardware Class: pci","Hardware Class: bridge"],
	"ISAPNP":["isapnp"],
	"PCMCIA":["pcmcia","pccard","pc card"],
	"SCSI":["scsi"],
	"Firewire":["firewire","ieee1394"],
	"Hotplug":["hotplug"],
					}

	l=self.mycats.values()
	self.info={}  # holds all hardware info
	self.mynodes={}
	self.hw_real={}
	for ii in l:
		self.mynodes[ii]=None
	self.createTree()

	#gtk.timeout_add(25,self.probeHw)

	hwwin.set_default_size(640,480)



    def menu_cb(self, appnum, *args):
	if appnum==530:
		try:
			import IceWMCPKeyboard
			IceWMCPKeyboard.run(0)
		except: 
			pass
	if appnum==531:
		try:
			import IceWMCPMouse
			IceWMCPMouse.run(0)
		except: 
			pass
	if appnum==532:
		try:
			import IceWMCP_GtkPCCard
			IceWMCP_GtkPCCard.run(0)
		except: 
			pass
	if appnum==533:
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		fork_process("eject -r")  # cdrom
	if appnum==534:
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		fork_process("eject -f")  # floppy
	if appnum==535:
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		fork_process("eject -s")  # scsi
	if appnum==536:
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		fork_process("eject -q")  # tape
	

    def doQuit(self,*args):
	gtk.mainquit()


    def setText(self, helpstuff):
		try:
			self.textfield.get_buffer().set_text("")
		except:
			pass
		try:					
			if str(helpstuff).find(_("Hardware and System Information"))> -1:
				text_buffer_insert(self.textfield.get_buffer(), 
					   get_renderable_tab(self.textfield.get_buffer(),
					   HELP_FONT3,COL_WHITE,LANGCODE),str(helpstuff))
				colour=COL_PURPLE
			else: 
				text_buffer_insert(self.textfield.get_buffer(), 
					   get_renderable_tab(self.textfield.get_buffer(),
					   HELP_FONT2,COL_BLACK,LANGCODE),str(helpstuff))
				colour=COL_WHITE

			for gg in [STATE_NORMAL, STATE_ACTIVE, STATE_PRELIGHT,
					STATE_SELECTED, STATE_INSENSITIVE]:
					self.textfield.modify_base(gg,colour)
		except:
			pass


    def probeGUI(self,*args):  # the Suse HW library returns WRONG X Server info, work-around
	global ADDITIONAL_INFO
	ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
	ADDITIONAL_INFO.append("Model: GUI Configuration")
	ADDITIONAL_INFO.append("Device: Graphical User Interface")
	ADDITIONAL_INFO.append("Hardware Class: display")
	ADDITIONAL_INFO.append("Exec-cmd: IceWMCPSystem\n")
	sys_info=""
        sys_info=sys_info+"\tIceWM Control Panel Version :  "+this_software_version +"\n"
        sys_info=sys_info+"\tSCREEN RESOLUTION : "+str(GDK.screen_width())+" x "+ str(GDK.screen_height())+"\n"
        sys_info=sys_info+"\tPYTHON VERSION : "+sys.version.replace("\n","  ")+"\n"
        sys_info=sys_info+"\tGTK VERSION : "+str(gtk_version).replace(",",".").replace(" ","")+"\n"
        sys_info=sys_info+"\tPYGTK VERSION : "+str(pygtk_version).replace(",",".").replace(" ","")+"\n"
        sys_info=sys_info+"\tIMLIB VERSION : "+str(os.popen("imlib-config --version").readline()) +"\n"
        sys_info=sys_info+"\tGdk-PIXBUF VERSION : "+str(os.popen("gdk-pixbuf-config --version").readline()) +"\n\n"      
        sys_info=sys_info+"\tICEWM VERSION : "+str(os.popen("icewm --version").readline()) +"\n"
        sys_info=sys_info+"\tICEWM-GNOME VERSION : "+str(os.popen("icewm-gnome --version").readline()) +"\n"
        sys_info=sys_info+"\tICESOUND VERSION : "+str(os.popen("icesound --version").readline()) +"\n"
        sys_info=sys_info+"\tICESOUND-GNOME VERSION : "+str(os.popen("icesound-gnome --version").readline()) +"\n"	
	ADDITIONAL_INFO.append(sys_info)



    def probeX(self,*args):  # the Suse HW library returns WRONG X Server info, work-around
	global ADDITIONAL_INFO
	try:
		flist=os.popen("xdpyinfo").readlines()
		if len(flist)> 2:
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: X display information")
			ADDITIONAL_INFO.append("Device: X display information")
			ADDITIONAL_INFO.append("Hardware Class: display")
			ADDITIONAL_INFO.append("Exec-cmd: xdpyinfo\n")
			for ii in flist:
					ADDITIONAL_INFO.append(ii)
	except:
		pass
	try:  # get locale/language
		if os.environ.has_key("LANG") or os.environ.has_key("LANGUAGE"):
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: Language (locale)")
			ADDITIONAL_INFO.append("Device: Language")
			ADDITIONAL_INFO.append("Hardware Class: display\n")		
			vals=['LANG','LANGUAGE']
			for myval in vals:
			  if os.environ.has_key(myval):
				lang1=os.environ[myval]
				lang2=None
				for ii in self.locales.keys():
					if lang1.lower().find(ii)>-1: 
						lang2=ii
						break
					if lang1.lower().find(self.locales[ii])>-1: 
						lang2=ii
						break
				if lang2==None: lang2=lang1
				ADDITIONAL_INFO.append(myval+": "+lang2+"  ("+lang1+")")		
	except:
		pass
	try:  # get display name 
		if os.environ.has_key("DISPLAY"):
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: X Display")
			ADDITIONAL_INFO.append("Device: X Display")
			ADDITIONAL_INFO.append("Hardware Class: display\n")		
			ADDITIONAL_INFO.append("Display / Screen:  "+str(os.environ['DISPLAY']))
	except:
		pass


    def probeUptime(self,*args):
	global ADDITIONAL_INFO
	try:
		flist=os.popen("uptime").readlines()
		if len(flist[0])>3:			
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: System Uptime")
			ADDITIONAL_INFO.append("Device: Uptime")
			ADDITIONAL_INFO.append("Hardware Class: system")
			ADDITIONAL_INFO.append("Exec-cmd: uptime\n")
			for ii in flist:
					ADDITIONAL_INFO.append(ii)
	except:
		pass
	try:
		flist=os.popen("printenv").readlines()
		if len(flist[0])>3:			
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: Shell Environment")
			ADDITIONAL_INFO.append("Device: Shell Environment")
			ADDITIONAL_INFO.append("Hardware Class: miscellaneous")
			ADDITIONAL_INFO.append("Exec-cmd: printenv\n")
			for ii in flist:
					ADDITIONAL_INFO.append(ii)
	except:
		pass

    def probeProc(self,*args):
	global ADDITIONAL_INFO  # fb, mtrr
	proc_files=['cmdline','cpuinfo','dma','e820info','execdomains','interrupts','iomem','ioports','irq','isapnp','meminfo','misc','modules','mounts','partitions','slabinfo','swaps','stat','version', 'filesystems', 'apm']
	for yy in proc_files:
	   try:
		flist=open("/proc/"+yy).readlines()
		if len(flist[0])>3:			
			ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
			ADDITIONAL_INFO.append("Model: "+yy.capitalize())
			ADDITIONAL_INFO.append("Device: "+yy.capitalize())
			if yy=="mounts":
				ADDITIONAL_INFO.append("Hardware Class: storage")			
			elif yy=="partitions":
				ADDITIONAL_INFO.append("Hardware Class: storage")	
			elif yy=="isapnp":
				ADDITIONAL_INFO.append("Hardware Class: isapnp")						
			else:
				ADDITIONAL_INFO.append("Hardware Class: proc filesystem")
			ADDITIONAL_INFO.append("Exec-cmd: cat "+"/proc/"+yy+"\n")
			for ii in flist:
					ADDITIONAL_INFO.append(ii)
	   except:
		pass

	proc_files=['mtrr']  # check for fb,mtrr support, more reliable than SuSe's library
	for yy in proc_files:
	   try:
		if os.path.getsize("/proc/"+yy)<1:  # file is empty, mtrr should contain data
			raise TypeError   #throw except, treat like non-existent file
		ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
		ADDITIONAL_INFO.append("Model: "+yy.upper()+" Support")
		ADDITIONAL_INFO.append("Device: "+yy.upper())
		ADDITIONAL_INFO.append("Hardware Class: "+yy)
		ADDITIONAL_INFO.append(yy.upper()+" Support:  Yes")
	   except:
		ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
		ADDITIONAL_INFO.append("Model: "+yy.upper()+" Support")
		ADDITIONAL_INFO.append("Device: "+yy.upper())
		ADDITIONAL_INFO.append("Hardware Class: "+yy)
		ADDITIONAL_INFO.append(yy.upper()+" Support:  No")
	proc_files=['fb', 'fb0','fb1']
	got_fb=0
	for ii in proc_files:
		try:
			f=open("/dev/"+ii)  # can we open it for reading? 'dead' framebuffers fail to open
			got_fb=1
			f.close()
		except:
			pass
	ADDITIONAL_INFO.append("[HARDWARE-ENTRY]")
	ADDITIONAL_INFO.append("Model: Frambuffer Support")
	ADDITIONAL_INFO.append("Device: Frambuffer")
	ADDITIONAL_INFO.append("Hardware Class: display")
	if got_fb: ADDITIONAL_INFO.append("Frambuffer Support:  Yes")
	else: ADDITIONAL_INFO.append("Frambuffer Support:  No")
	
    def probeOther(self,*args):
	self.probeUptime()
	self.probeX()
	self.probeGUI()
	self.probeProc()
	return 0

    def probeHw(self,*args):
	global ADDITIONAL_INFO
	done_init=0
	#plist=['mouse', 'display']
	plist=['reallyall', 'arch']
	for ii in plist:
		hwlist=list_hardware(ii)
		if done_init==0:
			hwlist=hwlist+ADDITIONAL_INFO  # add proc sys info the first time around
			done_init=1
		hwlist=string.join(hwlist,"\n").split("[HARDWARE-ENTRY]\n")		
		for yy in hwlist:
			#if yy.lower().find("flop")>-1 :  print "FLOPPY:  "+yy
			HW_ID=None
			HW_ID_REAL=None
			hwsmall=yy.split("\n")
			if len(hwsmall)<2: continue
			hwinfo=['','','','']
			for zz in hwsmall:
				if zz.find("Created at")>-1:  hwinfo[3]=zz
				if zz.find("Model:")>-1: 
					if len(zz.replace("Model:","").replace("\"","").strip())>0: 
						HW_ID=zz.replace("Model:","").replace("\"","").strip()
						hwinfo[0]=HW_ID
						break
			for zz in hwsmall:
				if (zz.find("Hardware Class:")>-1) and (zz.lower().find("unknown")==-1):		
					if not HW_ID: 
						if len(zz.replace("Hardware Class:","").replace("\"","").strip())>0: 
							HW_ID=zz.replace("Hardware Class:","").replace("\"","").strip()
					if str(HW_ID).lower().find("unknown")>-1: 
						if len(zz.replace("Hardware Class:","").replace("\"","").strip())>0: 
							HW_ID=zz.replace("Hardware Class:","").replace("\"","").strip()
					hwinfo[2]=zz.replace("Hardware Class:","").strip()
					break
			for zz in hwsmall:
				if zz.find("Device:")>-1: 			
					if not HW_ID: 
						if len(zz.replace("Device:","").replace("\"","").strip())>0: 
							HW_ID=zz.replace("Device:","").replace("\"","").strip()
					hwinfo[1]=zz.replace("Device:","").strip()
					break
			for zz in hwsmall:
				if zz[0:5].find(":") > -1: 
					HW_ID_REAL=zz.strip()
					break
			if HW_ID==None: HW_ID=_("Unknown")+"-"+str(random.randrange(9000))+str(random.randrange(9000))
			if HW_ID_REAL==None: HW_ID_REAL=_("Unknown")+"-"+str(random.randrange(9000))+str(random.randrange(9000))

			HW_ID=HW_ID.replace("\"","").strip().title()
			if HW_ID=='bios': HW_ID="Bios"
			self.info[HW_ID_REAL]=yy
			#print "Hard:  "+str(HW_ID)+"  "+str(hwinfo)
			HW_CLASS=self.getHwClass(hwsmall)
			HW_ICON=self.getSpecialIcon(hwinfo)
			if HW_ICON==None: HW_ICON=self.getIcon(self.treeleft.getNodeName(HW_CLASS))
			dd=self.treeleft.insertNode(HW_CLASS, MENUTREE_SUBMENU,HW_ID, HW_ICON, None)
			#print self.treeleft.getNodeName(HW_CLASS)
			self.treeleft.move(dd, HW_CLASS, None)
			self.hw_real[dd]=HW_ID_REAL				

	hideSplash()
	hideSplash()	
	self.hwwin.show_all()
	return 0


    def do_about(self,*args):
	commonAbout("IceWMCP : "+_("Hardware and System Information"),"IceWMCP : "+_("Hardware and System Information")+" "+self.version+"\n\n"+_("This is an unsupported plug-in for IceWMCP.")+"  "+_("This software uses a modified version of the 'libhd' and 'hwinfo' software library from SuSe.")+"  "+_("No technical support is provided for this plug-in."))


    def click_cb(self,*args):
	if len(args)>1:
		nodename=self.treeleft.getNodeName(args[1])
		hw_real=None
		if self.hw_real.has_key(args[1]): hw_real=self.hw_real[args[1]]
		#hw_real=args[1].get_data("hw_real")
		#print "NODE:   "+nodename+"     hw_real:  "+str(hw_real)
		if not hw_real==None:
			if self.info.has_key(hw_real):
				self.setText("\n "+string.join(self.info[hw_real],"").replace("\n","\n    "))

		else:
				self.setText("\n  "+string.join([_("Hardware and System Information")+" :\n\t "+nodename],"")+"\n\n\t")
				try:
					pix,mask=self.treeleft.getNodeIcon(args[1])
					secicon=Image()
					secicon.set_from_pixmap(pix,mask)
					secicon.show_all()
					tbuff=self.textfield.get_buffer()
					tanch=tbuff.create_child_anchor(tbuff.get_end_iter())
					self.textfield.add_child_at_anchor(secicon, tanch)
				except:
					pass

    def getSpecialIcon(self,hw_list):
	for ii in self.special_icons.keys():
		if hw_list[0].lower().find(ii)>-1: return getHwIconDir()+self.special_icons[ii]
		if hw_list[1].lower().find(ii)>-1: return getHwIconDir()+self.special_icons[ii]
		if hw_list[2].lower().find(ii)>-1: return getHwIconDir()+self.special_icons[ii]
		if hw_list[3].lower().find(ii)>-1: return getHwIconDir()+self.special_icons[ii]
	return None

    def getIcon(self,hw_cat_str):  # make more specific
	if self.icons.has_key(hw_cat_str):
		return getHwIconDir()+self.icons[hw_cat_str]
	eng_cat=hw_cat_str
	for ii in self.mycats.keys():
		if self.mycats[ii]==hw_cat_str:
			eng_cat=ii
			break
	if self.icons.has_key(eng_cat):
		return getHwIconDir()+self.icons[eng_cat]
	return getHwIconDir()+"hwunknown.png"

    def getHwClass(self,hw_list): 
		for ii in hw_list:
			if ii.find("Hardware Class:")>-1:
				for yy in self.cats_order:
					if ii.lower().find(yy.lower())>-1:  
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
			if ii.find("Model:")>-1:
				for yy in self.cats_order:
					if ii.lower().replace("pci","").replace("isapnp","").replace("system","").find(yy.lower())>-1:
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
			if ii.find("Device:")>-1:
				for yy in self.cats_order:
					if ii.lower().replace("pci","").replace("isapnp","").replace("system","").find(yy.lower())>-1: 
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
		for ii in hw_list:
			if ii.find("Created at")>-1:
				for yy in self.cats_order:
					if ii.lower().find(yy.lower())>-1:  
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
			if ii.find("Device:")>-1:
				for yy in self.cats_order:
					if ii.lower().find(yy.lower())>-1:  
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
			if ii.find("Model:")>-1:
				for yy in self.cats_order:
					if ii.lower().find(yy.lower())>-1:
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
		for ii in hw_list:
				for yy in self.cats_order:
					if ii.lower().find(yy.lower())>-1:  
						return self.mynodes[self.mycats[yy]]
					for zz in self.aliases[yy]:
						if ii.lower().find(zz.lower())>-1:  return self.mynodes[self.mycats[yy]]
		return self.mynodes[self.mycats["Miscellaneous"]]  # return a default


    def createTree(self,*args):
	rootnode=self.treeleft.init()
	self.treeleft.connect("tree-select-row",self.click_cb)
	self.rootnote=rootnode
	l=self.mynodes.keys()
	l.sort()
	l.reverse()
	for ii in l:
		dd=self.treeleft.insertNode(rootnode, MENUTREE_SUBMENU,ii, self.getIcon(ii), None)
		#dd.parent=rootnode
		self.mynodes[ii]=dd


############################################
## This code come from IceMe - an adapted version of DndTree
############################################



class hwtree(DndCTree.DndCTree):

    
    def __init__(self):
        DndCTree.DndCTree.__init__(self, 1, 0, [" "+sys.platform])
        self.app = None
	self.column_titles_height=45
	self.set_row_height(32)
        self.set_selection_mode(SELECTION_BROWSE)
        self.column_titles_passive()
        self.connect("tree-expand", self.on_tree_expand)

    def on_tree_expand(self, tree, node):
        for i in range(0,2):
	    opt=self.optimal_column_width(i)
	    if opt<280:  opt=281
            self.set_column_width(i, opt+220)

    def init(self, *args):
        self.clear()
        self.freeze()
        # insert root node:
        root = self.__insertNode(None, None, MENUTREE_SUBMENU,
                                 "["+sys.platform+"]", getHwIconDir()+"hwmain.png", None, TRUE)
        self.expand(root)
        self.columns_autosize()
        self.thaw()
        return root

    def __insertSep(self, parent, sibling, inactive = FALSE):
        return self.__insertNode(parent, sibling, MENUTREE_SEPARATOR,
                                 "", None, None, inactive)

    def PinsertNode(self, parent, sibling,
                     type, text, iconname, command,
                     inactive = FALSE):

	return self.__insertNode( parent, sibling,type, text, iconname, command,FALSE)

    def __insertNode(self, parent, sibling,
                     type, text, iconname, command,
                     inactive = FALSE):
	pix=None
	mask=None
        if type not in (MENUTREE_PROG, MENUTREE_RESTART):
            command = ""
        if type == MENUTREE_SEPARATOR:
            text = SEP_STRING
            pix = mask = iconname = None
        else:
	    try:
		img = GDK.pixbuf_new_from_file(iconname)
		img2 = img.scale_simple(30,30,GDK.INTERP_BILINEAR)
		pix,mask = img2.render_pixmap_and_mask()
	    except: 
		pix = mask = None
        is_leaf = (type != MENUTREE_SUBMENU)
        # insert node:
        node = self.insert_node(parent, sibling, [text, command], 5,
                                pix, mask, pix, mask, is_leaf)
        # store additional data: iconname, whether it's a restart button
        # and whether the entry is inactive:
        self.node_set_row_data(node, [iconname, type, inactive])
	return node


    def insertNode(self, node, type, text, iconname, command):
        "Insert a new entry under node 'node'."
	#parent = node.parent
        if self.isInactive(node):
            parent = node
            self.expand(parent)
            if node.children:
                sibling = node.children[0]
            else:
                sibling = None
        else:            
            sibling = node.sibling
	    parent = node.parent
	#print "parent: "+self.getNodeName(parent)
        return self.__insertNode(parent, sibling, type, text, iconname, command)


    def getNodeName(self, node):
        return self.__getNodeText(node, 0)

    def getNodeCommand(self, node):
        return self.__getNodeText(node, 1)

    def __getNodeText(self, node, col):
        cell_type = self.node_get_cell_type(node, col)
        if cell_type == CELL_TEXT:
            return self.node_get_text(node, col)
        elif cell_type == CELL_PIXTEXT:
            return self.node_get_pixtext(node, col)[0]
        return ""

    def setNodeName(self, node, name):
        self.__setNodeText(node, name, 0)

    def setNodeCommand(self, node, name):
        self.__setNodeText(node, name, 1)

    def __setNodeText(self, node, name, col):
        cell_type = self.node_get_cell_type(node, col)
        if cell_type == CELL_TEXT:
            self.node_set_text(node, col, name)
        elif cell_type == CELL_PIXTEXT:
            old_text, sp, pix, mask = self.node_get_pixtext(node, col)
            if pix == None:
                self.node_set_text(node, col, name)
            else:
                self.node_set_pixtext(node, col, name, sp, pix, mask)

    def getNodeIcon(self, node):
        cell_type = self.node_get_cell_type(node, 0)
        if cell_type == CELL_PIXTEXT:
            text, sp, pix, mask = self.node_get_pixtext(node, 0)
            return (pix, mask)
        elif cell_type == CELL_PIXMAP:
            return self.node_get_pixmap(node, 0)
        else:
            return (None, None)

    def setNodeIcon(self, node, pix, mask):
        cell_type = self.node_get_cell_type(node, 0)
        if cell_type == CELL_PIXTEXT:
            text, sp, old_pix, old_mask = self.node_get_pixtext(node, 0)
            self.node_set_pixtext(node, 0, text, sp, pix, mask)
        elif cell_type == CELL_PIXMAP:
            self.node_set_pixmap(node, 0, pix, mask)

    def getNodeUpperSibling(self, node):
        if node.parent is None:
            nodes = self.base_nodes()
        else:
            nodes = node.parent.children
        upper_sibling = None
        for n in nodes:
            if n == node:
                return upper_sibling
            upper_sibling = n
        return None

    def isSeparator(self, node):
        return self.getNodeType(node) == MENUTREE_SEPARATOR

    def isInactive(self, node):
        return self.node_get_row_data(node)[2]

    def getNodeType(self, node):
        return self.node_get_row_data(node)[1]

    def setNodeType(self, node, type):
        self.node_get_row_data(node)[1] = type

    def getNodeIconName(self, node):
        return self.node_get_row_data(node)[0]

    def setNodeIconName(self, node, iconname):
        self.node_get_row_data(node)[0] = iconname

    def getMainMenuNode(self):
        # the main menu node is always the first root node
        return self.base_nodes()[0]

    def getProgramsNode(self):
        # the programs node is always the last child of the
        # first root node (the "IceWM" node)
        return self.base_nodes()[0].children[-1]

    def getToolbarNode(self):
        # the toolbar node is always the third root node
        return self.base_nodes()[2]

    def isOnClipboard(self, node):
        "Check whether the node is currently on the clipboard."
        return self.is_ancestor(self.clipboard, node)

    def canMoveUp(self, node):
        "Check whether the node can be moved up in the current subtree."
        upper_sibling = self.getNodeUpperSibling(node)
        if upper_sibling is None: return 0
        return not self.isInactive(upper_sibling)

    def canMoveDown(self, node):
        "Check whether the node can be moved down in the current subtree."
        if node.sibling is None: return 0
        return not self.isInactive(node.sibling)

    def canDelete(self, node):
        "Check whether the node may be deleted."
        return not self.isInactive(node)

    def canInsertOn(self, node):
        return not (self.isInactive(node) and self.isSeparator(node))

    def move_is_permitted(self, source_node, target_node,
                          new_parent, new_sibling):
        return self.canDelete(source_node) and self.canInsertOn(target_node)

    def cut(self, node):
        if not self.canDelete(node) or self.isOnClipboard(node):
            gdk_beep()
            return
        # empty the current contents of the clipboard:
        if self.clipboard.children:
            for c in self.clipboard.children:
                self.remove_node(c)
        # move node to the clibboard:
        self.move(node, self.clipboard, None)

    def copy(self, node):
        if self.isOnClipboard(node):
            gdk_beep()
            return
        # empty the current contents of the clipboard:
        if self.clipboard.children:
            for c in self.clipboard.children:
                self.remove_node(c)
        # copy node and decessors recursively to the clipboard:
        self.freeze()
        self.__copy_recursive(self.clipboard, node, 1)
        self.thaw()

    def paste(self, node):
        if not self.clipboard.children:
            # the clipboard is empty
            gdk_beep()
            return
        if not self.canInsertOn(node) or self.isOnClipboard(node):
            # contents of clipboard may not be copied to the node:
            gdk_beep()
            return
        self.freeze()
        self.__copy_recursive(node, self.clipboard.children[0])
        self.thaw()

    def delete(self, node):
        if not self.canDelete(node):
            gdk_beep()
            return
        self.remove_node(node)

    def hasPasteData(self):
        return len(self.clipboard.children)

    def __copy_recursive(self, target_node,
                         source_node, as_child=0):
        if self.isInactive(target_node) or as_child:
            parent = target_node
            self.expand(parent)
            if target_node.children:
                sibling = target_node.children[0]
            else:
                sibling = None
        else:
            parent = target_node.parent
            sibling = target_node.sibling

        new_node = self.__insertNode(parent, sibling,
                                     self.getNodeType(source_node),
                                     self.getNodeName(source_node),
                                     self.getNodeIconName(source_node),
                                     self.getNodeCommand(source_node))

        if not source_node.is_leaf:
            for c in source_node.children:
                self.__copy_recursive(new_node, c, 1)

############################################
## end tree code
############################################


def run() :
	#timeout_add(20,hardwaregui)
	hardwaregui()
	gtk.mainloop()
	#gtk.mainloop()

if __name__== "__main__" :
	run()
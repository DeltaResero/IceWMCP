#! /usr/bin/env python

#############################
#  IceWM Control Panel - Energy Star 
#  
#  Copyright 2003 by Erica Andrews
#  PhrozenSmoke@yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  A simple Gtk-based application for managing
#  Energy Star/DPMS features through xset.
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py



class energywin:
    def __init__(self) :
	self.version=this_software_version
	global WMCLASS
	WMCLASS="icewmcpEnergyStar"
	global WMNAME
	WMNAME="IceWMCPEnergyStar"
	energywin=Window(WINDOW_TOPLEVEL)
	set_basic_window_icon(energywin)
	energywin.set_wmclass(WMCLASS,WMNAME)
	energywin.realize()
	energywin.set_title("IceWM CP - Energy Star "+self.version)
	energywin.set_position(WIN_POS_CENTER)
	self.energywin=energywin

	menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
 				(_("/_File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
  				(_("/_File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
				(_('/File/sep2'), None, None, 2, '<Separator>'),
				(_('/File/_Exit'), '<control>Q', self.doQuit, 0, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About...'), "F2", self.do_about, 0, ''),
				(_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5015, ""),
  				(_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  				(_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5015, ""),
					]

	ag = AccelGroup()
	self.ag=ag
	itemf = ItemFactory(MenuBar, '<main>', ag)
	self.itemf=itemf
	energywin.add_accel_group(ag)
	itemf.create_items(menu_items)
	self.menubar = itemf.get_widget('<main>')
	mainvbox1=VBox(0,1)
	mainvbox=VBox(0,1)
	mainvbox1.pack_start(self.menubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,0)
	mainvbox.set_border_width(4)
	mainvbox.set_spacing(4)
	mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png",DIALOG_TITLE),0,0,2)
	mainvbox.pack_start(Label("Energy Star  (DPMS)"),0,0,1)	


	self.onoff=CheckButton(" "+_("Enable Energy Star Features"))
	TIPS.set_tip(self.onoff,_("Enable Energy Star Features"))
	mainvbox.pack_start(self.onoff,0,0,3)
	self.onoff.set_active(1)

	self.times={
		_("NEVER"):0,
		"5 "+_("minutes"):5*60,
		"10 "+_("minutes"):10*60,
		"15 "+_("minutes"):15*60,
		"20 "+_("minutes"):20*60,
		"30 "+_("minutes"):30*60,
		"45 "+_("minutes"):45*60,
		"1 "+_("hour"):60*60,
		"1.5 "+_("hours"):90*60,
		"2 "+_("hours"):120*60,
		"3 "+_("hours"):180*60,
		"4 "+_("hours"):240*60,
		"5 "+_("hours"):300*60,
		"6 "+_("hours"):360*60,
		"9 "+_("hours"):540*60,
		"12 "+_("hours"):720*60,
		"18 "+_("hours"):1080*60,
		"24 "+_("hours"):1440*60,
				}

	timeorder=[
		_("NEVER"),
		"5 "+_("minutes"),
		"10 "+_("minutes"),
		"15 "+_("minutes"),
		"20 "+_("minutes"),
		"30 "+_("minutes"),
		"45 "+_("minutes"),
		"1 "+_("hour"),
		"1.5 "+_("hours"),
		"2 "+_("hours"),
		"3 "+_("hours"),
		"4 "+_("hours"),
		"5 "+_("hours"),
		"6 "+_("hours"),
		"9 "+_("hours"),
		"12 "+_("hours"),
		"18 "+_("hours"),
		"24 "+_("hours"),
				]

	self.combos=[]
	dpms=[_("'Standby' after being idle for"),_("Suspend the computer after"),_("Turn the computer off after")]

	for ii in dpms:
		combo=Combo()
		combo.entry.set_editable(0)
		combo.set_popdown_strings(timeorder)
		self.combos.append(combo)
		hbox=HBox(0,0)
		hbox.pack_start(Label(ii),0,0,0)
		hbox.pack_start(Label(":  "),1,1,0)
		hbox.pack_start(combo,0,0,0)
		mainvbox.pack_start(hbox,0,0,1)

	mainvbox.pack_start(Label("  "),0,0,2)
	botbox=HBox(0,0)
	botbox.set_border_width(3)
	appbutt=getPixmapButton(None, STOCK_APPLY ,_("Apply"))
	closebutt=getPixmapButton(None, STOCK_CANCEL ,_("Close"))
	botbox.pack_start(appbutt,1,1,0)
	botbox.pack_start(Label("          "),0,0,0)
	botbox.pack_start(closebutt,1,1,0)
	mainvbox.pack_start(botbox,0,0,2)
	appbutt.connect("clicked",self.apply_settings)
	closebutt.connect("clicked",self.doQuit)
	TIPS.set_tip(closebutt,_("Close"))
	TIPS.set_tip(appbutt,_("Apply"))

	energywin.add(mainvbox1)
	energywin.connect("destroy",self.doQuit)
	#energywin.set_default_size(450,375)
	energywin.show_all()

    def apply_settings(self,*args) :
	if self.onoff.get_active():
		# turn Energy Star features on
		os.popen("xset +dpms")

		standby=0
		suspend=0
		compoff=0
		if self.times.has_key(self.combos[0].entry.get_text()): 
			standby=self.times[self.combos[0].entry.get_text()]
		if self.times.has_key(self.combos[1].entry.get_text()): 
			suspend=self.times[self.combos[1].entry.get_text()]
		if self.times.has_key(self.combos[2].entry.get_text()): 
			compoff=self.times[self.combos[2].entry.get_text()]
		enline="xset dpms "+str(standby)+" "+str(suspend)+" "+str(compoff)
		#print "CMDLINE:  "+enline
		os.popen(enline)

	else:  # turn EnergyStar features off
		os.popen("xset -dpms")


    def doQuit(self,*args) :
	gtk.mainquit()

    def do_about(self,*args):
	commonAbout(_("About")+" IceWMCP - Energy Star  "+self.version,  "IceWMCP - Energy Star "+self.version+"\n\n"+_("A simple Gtk-based application for managing Energy Star/DPMS features through xset."))	

def run() :
	energywin()
	hideSplash()
	gtk.mainloop()

if __name__== "__main__" :
	run()



#! /usr/bin/env python

#############################
#  IceWM Control Panel - GtkPCCard
#  
#  Copyright (c) 2002-2003 by Erica Andrews
#  PhrozenSmoke@yahoo.com
#  http://icesoundmanager.sourceforge.net
#
#  Monitor and control your PCMCIA cards.
#  A frontend to the 'cardctl' program.
#
#  This is a Gtk-based re-write of the old 
#   tkPCCard, which was originally written to
#   use Tk/Tkinter.  tkPCCard is 
#   Copyright (c) 2002-2003 by Erica Andrews
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

import time

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py

global DO_QUIT
DO_QUIT=1

class gtkpccard:
    def __init__(self) :
	self.version="1.4"
	self.socket_count=0
	gtkpccardwin=Window(WINDOW_TOPLEVEL)
	gtkpccardwin.set_wmclass("gtkpccard","GtkPCCard")
	set_basic_window_icon(gtkpccardwin)
	self.tips=TIPS
	gtkpccardwin.realize()
	gtkpccardwin.set_title("GtkPCCard"+" v."+self.version)
	gtkpccardwin.set_position(WIN_POS_CENTER)
	self.gtkpccardwin=gtkpccardwin
	mainvbox1=VBox(0,1)
	mainvbox1.set_spacing(2)
	mainvbox=VBox(0,1)
	mainvbox.set_spacing(2)
	mymenubar=MenuBar()
	self.mymenubar=mymenubar

        ag=AccelGroup()
        itemf=ItemFactory(MenuBar, "<main>", ag)
	self.ag=ag
	self.itemf=itemf
        itemf.create_items([
            # path              key           callback    action#  type
  (_("/ _File"),  "<alt>F",  None,  0,"<Branch>"),
  (_("/ _File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
  (_("/ _File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
  (_("/ _File/sep4"), None,  None,  49, "<Separator>"),
  (_("/ _File/_Quit"), "<control>Q", self.doQuit,10,""),
  (_("/_Help"),  "<alt>H",  None,16, "<LastBranch>"), 
  (_("/Help/_About..."), "F2", self.doAbout,17, ""),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5011, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5011, ""),
        ])

        gtkpccardwin.add_accel_group(ag)
        mymenubar=itemf.get_widget("<main>")
        mymenubar.show()
	self.menubar=mymenubar
	mainvbox1.pack_start(mymenubar,0,0,0)
	mainvbox1.pack_start(mainvbox,1,1,0)

	mainvbox.pack_start(getImage(getBaseDir()+"icewmcp.png","IceWM Control Panel"),0,0,2)
	mainvbox.pack_start(Label("GtkPCCard: "+_("PC Card Manager")),0,0,2)
	self.mynotebook=Notebook()
	self.mynotebook.set_scrollable(1)
	self.addWidgets()
	mainvbox.pack_start(self.mynotebook,1,1,2)
	gtkpccardwin.add(mainvbox1)
	self.gtkpccardwin=gtkpccardwin
	gtkpccardwin.set_default_size(-1,440)
	gtkpccardwin.connect("destroy",self.doQuit)
	gtkpccardwin.show_all()


    def doQuit(self,*args) :
	global DO_QUIT
	if DO_QUIT==1: gtk.mainquit()
	else: 
		self.gtkpccardwin.hide()
		self.gtkpccardwin.destroy()
		self.gtkpccardwin.unmap()

    def doAbout(self,*args) :
    	commonAbout("IceWMCP GtkPCCard Manager","IceWMCP GtkPCCard Manager "+self.version+"\n\nThis is a simple PC Card (PCMCIA) manager.  It is a basic frontend for the 'cardctl' program for PC Cards.  To be useful, this program requires the 'cardctl' program and one or more PC card slots.  Generally, you have to be 'root' to use this program.")

    def getSocketCount(self):
     try:
      f=os.popen("cardctl status")
      i=1
      while i:
        s=f.readline().strip()
        if s.startswith("Socket"):
          self.socket_count=self.socket_count+1
        if s=="": break
     except:
      self.socket_count=0
     return self.socket_count

    def addWidgets(self):
	card_warn=0
    	if not self.getSocketCount():
		msg_warn("GtkPCCard",_("No PCMCIA slots detected on this computer."))
		self.socket_count=1
		card_warn=1
	icounter=0
	while icounter<self.socket_count:
		mi_tarjeta=miTarjeta()
		mi_tarjeta.setSocketNum(icounter)
		# Changed here, 12.3.2003, Don't attempt to load card facts if no cards are available
		if card_warn==1:
			mi_tarjeta.insertFact("No PCMCIA slots detected on this computer.")
		else:
			mi_tarjeta.loadFacts(icounter)
		self.mynotebook.append_page(mi_tarjeta,Label(_("Slot  ")+str(icounter)))
		icounter=icounter+1


# A class for each PC Card
class miTarjeta(VBox):
  def __init__(self):
		VBox.__init__(self)
		self.socket_num=0
		self.set_spacing(3)
		self.set_border_width(5)
		self.slot_lab=Label("Slot")
		self.pack_start(self.slot_lab,0,0,3)
		sc=ScrolledWindow()
		self.infobox=TextView()
		self.infobox.set_editable(0)
		self.infobox.set_wrap_mode(WRAP_WORD)
		self.infoboxbuf=self.infobox.get_buffer()
		sc.add(self.infobox)
		self.pack_start(sc,1,1,0)
		buttbox=HBox(2,1)
		buttbox.set_spacing(3)
		buttbox.set_border_width(3)
		ebutt=getPixmapButton(None, STOCK_REMOVE ,_("Eject"))
		ebutt.connect("clicked",self.eject)
		ibutt=getPixmapButton(None, STOCK_ADD ,_("Insert"))
		ibutt.connect("clicked",self.insert)
		rbutt=getPixmapButton(None, STOCK_UNDO ,_("Reset"))
		rbutt.connect("clicked",self.reset)
		sbutt=getPixmapButton(None, STOCK_STOP ,_("Suspend"))
		sbutt.connect("clicked",self.suspend)
		rrbutt=getPixmapButton(None, STOCK_REFRESH ,_("Resume"))
		TIPS.set_tip(rrbutt,_("Resume"))
		TIPS.set_tip(sbutt,_("Suspend"))
		TIPS.set_tip(rbutt,_("Reset"))
		TIPS.set_tip(ibutt,_("Insert"))
		TIPS.set_tip(ebutt,_("Eject"))
		rrbutt.connect("clicked",self.resume)
		for yy in [ebutt,ibutt,rbutt,sbutt,rrbutt]:
			buttbox.pack_start(yy,1,1,0)
		self.pack_start(buttbox,0,0,2)
		self.show_all()

  def clearText(self):
	self.infoboxbuf.set_text("")

  def showMessage(self,mess):
    msg_info("GtkPCCard",mess)

  def insertFact(self,mess):
    text_buffer_insert(self.infoboxbuf, 					  get_renderable_tab(self.infoboxbuf,HELP_FONT2,
	COL_BLACK,"iso8859-1"), to_utf8(str(mess)+"\n")
					 )

  def setSocketNum(self,num):
    self.socket_num=num
    self.slot_lab.set_text(_("Slot  ")+str(num))

  def loadFacts(self,num):
    self.clearText()
    has_facts=1
    try:
      f=os.popen("cardctl ident "+str(self.socket_num))
      i=1
      while i:
        s=f.readline().strip()
        if s=="": 
          break
        elif s.find("no card") > -1:
          has_facts=0
          self.insertFact(_("Empty"))
          break
        elif (s.find("product info:") > -1) and (s.find(",") > -1 ):
          ss=s[s.find("product info:")+13:len(s)].strip()
          sss=ss.split(",")
          for y in sss:
            self.insertFact(y.strip())
        else:
          self.insertFact(s)
      f.close()
      if has_facts:
        f=os.popen("cardctl status "+str(self.socket_num))
        i=1
        while i:
          s=f.readline().strip()
          if s=="": break
          self.insertFact(s)
    except:
      self.insertFact(_("Error loading card data"))

  def eject(self,*args):
    try:
      f=os.popen("cardctl eject "+str(self.socket_num))
      f.close()
      time.sleep(2)
      self.showMessage(_("This card has been ejected.\nYou may safely remove this device."))
      self.loadFacts(self.socket_num)
    except:
      msg_err("GtkPCCard",_("An error occurred while ejecting this card."))

  def suspend(self,*args):
    try:
      f=os.popen("cardctl suspend "+str(self.socket_num))
      time.sleep(2)
      f.close()
      self.showMessage(_("This card's activity has been suspended"))
      self.loadFacts(self.socket_num)
    except:
      msg_err("GtkPCCard",_("An error occurred while suspending this card."))

  def resume(self,*args):
    try:
      f=os.popen("cardctl resume "+str(self.socket_num))
      time.sleep(2)
      f.close()
      self.showMessage(_("This card's activity has been resumed."))
      self.loadFacts(self.socket_num)
    except:
      msg_err("GtkPCCard",_("An error occurred while resuming this card."))

  def insert(self,*args):
    try:
      f=os.popen("cardctl insert "+str(self.socket_num))
      time.sleep(2)
      f.close()
      self.showMessage(_("This card has been inserted."))
      self.loadFacts(self.socket_num)
    except:
      msg_err("GtkPCCard",_("An error occurred while inserting this card."))

  def reset(self,*args):
    try:
      f=os.popen("cardctl eject "+str(self.socket_num))
      time.sleep(2)
      f.close()
      f=os.popen("cardctl insert "+str(self.socket_num))
      time.sleep(1)
      f.close()
      self.showMessage(_("This card has been reset."))
      self.loadFacts(self.socket_num)
    except:
      msg_err("GtkPCCard",_("An error occurred while resetting this card."))

#### Main methods ####

def run(doquit=1) :
	global DO_QUIT
	DO_QUIT=doquit
	gtkpccard()
	hideSplash()
	if doquit==1: mainloop()

if __name__== "__main__" :
	run()
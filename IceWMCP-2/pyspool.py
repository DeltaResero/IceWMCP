#! /usr/bin/env python

#############################################
#  PySpool 0.3
#  Copyright (c) 2002-2003 by Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  
#  PySpool is a simple Gtk-based spool monitor and 
#  manager written in 100% Python. It is intended to 
#  monitor LPRng and LPR-based printer spools. 
#  This is BETA code. PySpool has only been tested 
#  with LPRng 3.8.12 on local printers. PySpool 
#  requires the following executables on your PATH: 
#  lpstat, cancel, checkpc
#  
#  PySpool is open source under the General Public 
#  License (GPL). PySpool is part of the PyPrint
#  utility package (same author).
#  
#  NO technical support will be provided for this 
#  application. 
#  Enjoy!
#############################################

import copy
from pyprintcommon import *

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py


class pyspoolwin :
    def __init__(self) :
	pyspoolwin=Window(WINDOW_TOPLEVEL)
	pyspoolwin.set_wmclass("pyspool","PySpool")
	set_basic_window_icon(pyspoolwin)
	self._root=pyspoolwin
	pyspoolwin.realize()
	pyspoolwin.set_title('PySpool: '+_("Printer Queue")+' version '+PYPRINT_VERSION)	
	pyspoolwin.set_position(WIN_POS_CENTER)
	self.pyspoolwin=pyspoolwin
	mainvbox=VBox(0,0)
	self.mainvbox=mainvbox
	mymenu=MenuBar()
	self.mymenu=mymenu

        ag = AccelGroup()
        itemf = ItemFactory(MenuBar, "<main>", ag)
	self.ag=ag
	self.itemf=itemf
        itemf.create_items([
            # path              key           callback    action#  type
  (_("/ _File"),  "<alt>F",  None,  0, "<Branch>"),
  (_("/ _File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
  (_("/ _File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
  (_("/ _File/_Quit"), "<control>Q", self.doQuit, 10, ""),
  (_("/_Help"),  "<alt>H",  None, 16, "<LastBranch>"), 
  (_("/_Help/_About")+" PySpool...", "F2", self.doAbout, 17, ""),
  (_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5008, ""),
  (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5008, ""),

        ])
        pyspoolwin.add_accel_group(ag)
        mymenu = itemf.get_widget("<main>")
        mymenu.show()

	mainvbox.pack_start(mymenu,0,0,0)
	mainvbox.set_border_width(3)
	hbox1=HBox(0,12)
	hbox1.set_border_width(5)
	pic=loadImage(getPixDir()+"pyprint_printer_big.xpm",pyspoolwin)
	if pic: 	mainvbox.pack_start(pic,0,0,0)
	self.hbox1=hbox1
	label8=Label(_('Select Printer:'))
	self.label8=label8
	pyspoolwin.set_size_request(680,-1)
	hbox1.pack_start(label8,0,0,0)
	printcombo=Combo()
	printcombo.set_size_request(200,-1)
	self.printcombo=printcombo
	combo_entry=printcombo.entry
	combo_entry.set_editable(0)
	self.combo_entry=combo_entry
	hbox1.pack_start(printcombo,0,0,0)
	viewbutt=getPixmapButton(None, STOCK_ZOOM_100 ,_('  View  ').strip())
	TIPS.set_tip(viewbutt,_('  View  '))
	viewbutt.connect("clicked",self.changeView)
	self.viewbutt=viewbutt
	hbox1.pack_start(viewbutt,0,0,0)
	mainvbox.pack_start(hbox1,0,0,0)
	hbox3=HBox(0,8)
	hbox3.set_border_width( 4)
	self.hbox3=hbox3
	mytable=Table(5,2,0)
	mytable.set_row_spacings(3)
	mytable.set_col_spacings(7)
	self.mytable=mytable
	label15=Label(_('Description:'))
	label15.set_alignment(0,0.5)
	self.label15=label15
	mytable.attach(label15,0,1,0,1,(FILL),(0),0,0)
	label16=Label(_('Queue:'))
	label16.set_alignment( 0,0.5)
	self.label16=label16
	mytable.attach(label16,0,1,1,2,(FILL),(0),0,0)
	label17=Label(_('Server:'))
	label17.set_alignment(0,0.5)
	self.label17=label17
	mytable.attach(label17,0,1,2,3,(FILL),(0),0,0)
	label18=Label(_('Status:'))
	label18.set_alignment( 0,0.5)
	self.label18=label18
	mytable.attach(label18,0,1,3,4,(FILL),(0),0,0)
	label19=Label(_('Info:'))
	label19.set_alignment( 0,0.5)
	self.label19=label19
	mytable.attach(label19,0,1,4,5,(FILL),(0),0,0)
	desc_text=Entry()
	self.desc_text=desc_text
	desc_text.set_editable(0)
	mytable.attach(desc_text,1,2,0,1,(EXPAND+FILL),(0),0,0)
	q_text=Entry()
	self.q_text=q_text
	q_text.set_editable(0)
	mytable.attach(q_text,1,2,1,2,(EXPAND+FILL),(0),0,0)
	server_text=Entry()
	self.server_text=server_text
	server_text.set_editable(0)
	mytable.attach(server_text,1,2,2,3,(EXPAND+FILL),(0),0,0)
	status_text=Entry()
	self.status_text=status_text
	status_text.set_editable(0)
	mytable.attach(status_text,1,2,3,4,(EXPAND+FILL),(0),0,0)
	info_text=Entry()
	info_text.set_editable(0)
	self.info_text=info_text
	mytable.attach(info_text,1,2,4,5,(EXPAND+FILL),(0),0,0)
	hbox3.pack_start( mytable,1,1,0)
	vbox3=VBox(1,7)
	self.vbox3=vbox3
	refreshbutt=getPixmapButton(None, STOCK_REFRESH ,_("Refresh Queue Details") )
	TIPS.set_tip(refreshbutt,_("Refresh Queue Details"))
	refreshbutt.connect("clicked",self.loadDetailsR)
	self.refreshbutt=refreshbutt
	vbox3.pack_start( refreshbutt,0,0,0)
	cancelbutt=getPixmapButton(None, STOCK_DIALOG_ERROR ,_("Cancel Selected Print Job"))
	TIPS.set_tip(cancelbutt,_("Cancel Selected Print Job"))
	cancelbutt.connect("clicked",self.cancelJob)
	self.cancelbutt=cancelbutt
	vbox3.pack_start( cancelbutt,0,0,0)
	hbox3.pack_start( vbox3,0,0,0)
	mainvbox.pack_start(hbox3,0,0,4)
	scrollwin=ScrolledWindow()
	scrollwin.set_border_width(3)
	scrollwin.set_size_request(-1,170)
	self.scrollwin=scrollwin
	myclist=CList(7)
	myclist.connect("unselect_row",self.startUpdates)
	myclist.connect("select_row",self.makeSelection)
	myclist.column_titles_show()
	myclist.set_column_width(0,80)
	myclist.set_column_width(1,73)
	myclist.set_column_width(2,91)
	myclist.set_column_width(3,120)
	myclist.set_column_width(4,127)
	myclist.set_column_width(5,88)
	myclist.set_column_width(6,320)
	self.myclist=myclist
	label1=Label(_('State'))
	self.label1=label1
	myclist.set_column_widget(0,label1)
	label2=Label(_('Job ID'))
	self.label2=label2
	myclist.set_column_widget(1,label2)
	label3=Label(_('Size'))
	self.label3=label3
	myclist.set_column_widget(2,label3)
	label4=Label(_('Files'))
	self.label4=label4
	myclist.set_column_widget(3,label4)
	label5=Label(_('Owner/ID'))
	self.label5=label5
	myclist.set_column_widget(4,label5)
	label6=Label(_('Time'))
	self.label6=label6
	myclist.set_column_widget(5,label6)
	label7=Label(_('Class'))
	self.label7=label7
	myclist.set_column_widget(6,label7)
	scrollwin.add(myclist)
	mainvbox.pack_start(scrollwin,1,1,0)
	mystatusbar=Statusbar()
	self.mystatusbar=mystatusbar
	statid=mystatusbar.get_context_id("spooler")
	self.statid=statid
	mainvbox.pack_start(mystatusbar,0,0,0)
	pyspoolwin.add( mainvbox)
	pyspoolwin.connect("destroy",self.doQuit)
	global SELECTED_PRINTER
	SELECTED_PRINTER=None
	global SELECTING
	SELECTING=0
	global JOB_ID
	JOB_ID=-1
	pyspoolwin.show_all()
	self.checkPath() # check for needed executables
	# correct any problems with the printer queue directories
	launch("checkpc -f > /dev/null")
	try:
		self.loadDetails()
	except:
		pass
	gtk.timeout_add(1500,self.autoLoad) # reload the details every 1.5 seconds


    def changeView(self,*args) :
	if not self.combo_entry.get_text().strip()=="":
		global SELECTED_PRINTER
		SELECTED_PRINTER=self.combo_entry.get_text().strip()
		self.loadDetails()
		self.startUpdates()

    def startUpdates(self,*args) :	
	global JOB_ID
	JOB_ID=-1
	global SELECTING
	SELECTING=0

    def stopUpdates(self,*args) :	
	global SELECTING
	SELECTING=1

    def makeSelection(self,clist=None,crow=-1,*args) :
	global JOB_ID
	if crow>-1: 
		JOB_ID=self.myclist.get_text(crow,1).strip()
		#self.showMessage("Job ID is:  "+str(JOB_ID))
	self.stopUpdates()

    def cancelJob(self,*args) :
	self.stopUpdates()
	global JOB_ID
	if str(JOB_ID)=="-1": 
		self.startUpdates()
		return
	global SELECTED_PRINTER
	if SELECTED_PRINTER==_("NONE FOUND"): 
		self.startUpdates()
		return
	if self.showConfirm(_("Are you SURE you want to cancel print job ")+" '"+str(JOB_ID)+"' "+_(" on printer '")+str(SELECTED_PRINTER)+"' ?")==1:  
		fflines=readOSLines("cancel -P "+str(SELECTED_PRINTER)+" "+str(JOB_ID))
		ss=_("Cancel Print Job ")+str(JOB_ID)+" - "+_("Result")+":\n\n"
		for ii in fflines: 
			ss=ss+ii+"\n"
		self.showMessage(ss)
	self.loadDetailsR()	

    def autoLoad(self,*args) :	
	global SELECTING
	if SELECTING==1: return TRUE
	try:
		self.loadDetails()
	except:
		pass
	return TRUE

    def loadDetailsR(self,*args) :		
	self.loadDetails()
	self.startUpdates()

    def loadDetails(self,*args) :
	self.loadPrinterNames()
	readit=self.readPrinterInfo()
	self.loadQueue(copy.copy(readit))
	self.loadInfo(copy.copy(readit))
	global PRINTER_COUNT
	global SELECTED_PRINTER
	self.mystatusbar.push(self.statid,_(" Available printers: ")+str(PRINTER_COUNT)+_("        Current printer: ")+str(SELECTED_PRINTER))

    def loadInfoDefaults(self) :
	self.desc_text.set_text(_("description unavailable"))
	self.q_text.set_text(_("queue status unavailable"))
	self.server_text.set_text(_("server status unavailable"))
	self.status_text.set_text(_("status unavailable"))
	self.info_text.set_text(_("info unavailable"))

    def clearInfo(self) :
	self.desc_text.set_text("")
	self.q_text.set_text("")
	self.server_text.set_text("")
	self.status_text.set_text("")
	self.info_text.set_text("")

    def loadInfo(self,readit) :
	self.info_text
	global SELECTED_PRINTER
	if not SELECTED_PRINTER: 
		self.loadInfoDefaults()
		return
	if SELECTED_PRINTER.strip()=="": 
		self.loadInfoDefaults()
		return
	if not len(readit):
		self.loadInfoDefaults()
		return
	self.clearInfo()
	try:
		for iinfo in readit:
			infoline=iinfo.strip()
			if infoline.lower().startswith("printer"): 
				self.info_text.set_text(self.info_text.get_text()+infoline.replace("printer","").replace("Printer:","").strip()+"  ")
			if infoline.startswith("Status:"): self.status_text.set_text(infoline.replace("Status:","").strip())
			if infoline.startswith("Server:"): 
				self.server_text.set_text(infoline.replace("Server:","").strip())
				if infoline.lower().find("no server active") > -1: self.server_text.set_text(self.server_text.get_text()+"    (No clients currently printing)")
			if infoline.startswith("Description:"): self.desc_text.set_text(infoline.replace("Description:","").strip())
			if infoline.startswith("Queue:"): self.q_text.set_text(infoline.replace("Queue:","").strip())
	except:
		self.loadInfoDefaults()				

    def loadPrinterNames(self) :
	global SELECTED_PRINTER
	global PRINTER_COUNT
	global JOB_ID
	PRINTER_COUNT="0"
	if not self.combo_entry.get_text().strip()=="": SELECTED_PRINTER=self.combo_entry.get_text().strip()
	try:
		printers=getPrinterNames()
		if len(printers)==0: 
			self.printcombo.set_popdown_strings([_('NONE FOUND')])
			self.combo_entry.set_text(_('NONE FOUND'))
			JOB_ID=-1 # if there are no printers all old job ids are invalid
		else: 
			printers.sort()
			self.printcombo.set_popdown_strings(printers)
			self.printcombo.show_all()
			if not SELECTED_PRINTER: SELECTED_PRINTER=printers[0].strip()
			if SELECTED_PRINTER=="": SELECTED_PRINTER=printers[0].strip()
			self.combo_entry.set_text(SELECTED_PRINTER.strip())
			PRINTER_COUNT=str(len(printers))
	except:
		self.printcombo.set_popdown_strings([_('NONE FOUND')])
		self.combo_entry.set_text(_('NONE FOUND'))
		JOB_ID=-1

    def readPrinterInfo(self) :
	global SELECTED_PRINTER
	if not SELECTED_PRINTER: return []
	if SELECTED_PRINTER.strip()=="": return []
	if SELECTED_PRINTER==_("NONE FOUND"): return []
	return readOSLines("lpstat -D -p "+SELECTED_PRINTER.strip())

    def loadQueue(self,xreadlines_list) :	
	self.myclist.freeze()
	self.myclist.clear()
	try:
		foundQ=0
		for ii in xreadlines_list:
			if ii.lower().strip().startswith("rank"): 
				foundQ=1
				continue
			if foundQ==1:
				qline=ii.replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").strip().split(" ")
				qinfo=[qline[0],qline[3],qline[5],qline[4],qline[1],qline[6],qline[2]]
				self.myclist.append(qinfo)
	except:
		jj=_("Error")
		self.myclist.append([jj,jj,jj,jj,jj,jj,jj])
	self.myclist.thaw()

    def showMessage(self,message_text):
	return showMessage(message_text,"PySpool")

    def showConfirm(self,message_text):
	return showConfirm(message_text,"PySpool")

    def doAbout(self,*args):
	showAbout(_("PySpool is a simple Gtk-based spool monitor and manager written\nin 100% Python. It is intended to monitor LPRng and LPR-based\nprinter spools. This is BETA code. PySpool has only been\ntested with LPRng 3.8.12 on local printers.\nPySpool requires the following executables on your PATH:\nlpstat, cancel, checkpc"),"PySpool")

    def runPyPrint(self,*args):
	launch("pyprint &")

    def doQuit(self,*args) :
	gtk.mainquit()

    def checkPath(self) :
	executables=['lpstat','cancel','checkpc']
	for iexec in executables:
		if not isOnPath(iexec): self.showMessage(_("The following executable does not appear to be on your PATH:\n\n")+iexec+"\n\n"+_("You may experience problems running PySpool properly.\nPlease install '")+iexec+_("' into your PATH first."))

def run() :
    pyspoolwin()
    hideSplash()
    gtk.mainloop()

if __name__== "__main__" :
    run()

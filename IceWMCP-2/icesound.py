#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

######################################
# ICE SOUND MANAGER 
# 
#  Copyright (c) 2002-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
# 
# Ice Sound Manager was designed to ease 
# the management of sound events, sound themes, 
# and the sound server in the IceWM environment.  It 
# is also intended to be an improvement upon the 
# noble, but primitive icesndcfg.
# 
# Ice Sound Manager is in no way 'officially' affiliated 
# with IceWM, IceSound Server, or its creators.  Ice 
# Sound Manager is a FRONTEND to the IceSound Server. 
# 
# This program is distributed under the GNU General
# Public License (open source).
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

from icewmcp_common import *

import types, string, signal, copy, time
from threading import RLock, Thread

#set translation support
def _(somestr):
	return to_utf8(translateISM(somestr))  # from icewmcp_common.py


WHATS_THIS=_("What's this?")
CLICK_HELP=_("Click for help")

ism_version="v. "+this_software_version
global icemain
global statid
global statmessid
global statusbar
global iceo
global fs
global isetup
global exec_run
global audio_run
global wav_run
global pref_run
global server_exec
global sel_file
sel_file=None
global fdir
global themew
global icea
global wav_dir
global wav_cmd
global need_setup
global wav_edit
global use_terminal
use_terminal=0
global copy_wavs
copy_wavs=0
global start_server
start_server=0
global wav_pid
global themes
global audio_file
audio_file=".IceSoundManagerAudioRC"
global pref_file
pref_file=".IceSoundManagerRC"
themes={}
wav_pid=0
wav_edit="sweep %f &"
wav_cmd="wavplay -q %f &"
wav_dir=getIceWMPrivConfigPath()+"sounds"+os.sep
fs=None
global disabled_sounds
disabled_sounds={}
global sound_events
global event_desc
global icey
global xterm
xterm="xterm"
global filelock
filelock=RLock()
global filelock2
filelock2=RLock()
global reg_lock
reg_lock=RLock()
need_setup=0
global audio_defaults
global server_version
global help_file
audio_defaults={"oss_dev":"/dev/dsp","yiff_host":"localhost","yiff_port":"9433","yiff_auto":"1","esd_host":"localhost","esd_port":"16001","interface":"esd","esd_local":"1"}
sound_events={"startup":"[NONE]","shutdown":"","restart":"[NONE]","closeAll":"[NONE]","launchApp":"[NONE]","workspaceChange":"[NONE]","windowOpen":"[NONE]","windowClose":"[NONE]","dialogOpen":"[NONE]","dialogClose":"[NONE]","windowMin":"[NONE]","windowMax":"[NONE]","windowRestore":"[NONE]","windowHide":"[NONE]","windowLower":"[NONE]","windowRollup":"[NONE]","windowSized":"[NONE]","windowMoved":"[NONE]","startMenu":"[NONE]"}
event_desc={_("IceWM Startup"):"startup",_("IceWM Shutdown"):"shutdown",_("IceWM Restart"):"restart",_("Close All"):"closeAll",_("Launch Application"):"launchApp",_("Work Space Changed"):"workspaceChange",_("Window Opened"):"windowOpen",_("Window Closed"):"windowClose",_("Dialog Opened"):"dialogOpen",_("Dialog Closed"):"dialogClose",_("Window Minimized"):"windowMin",_("Window Maximized"):"windowMax",_("Window Restored"):"windowRestore",_("Window Hidden"):"windowHide",_("Window Lowered"):"windowLower",_("Window Rolled Up"):"windowRollup",_("Window Sized"):"windowSized",_("Window Moved"):"windowMoved",_("Start Menu Clicked"):"startMenu"}
global current_theme_file
global current_theme
current_theme=_("[NONE]")
current_theme_file=getIceWMPrivConfigPath()+"sample_theme.stheme"
server_exec="/usr/X11R6/bin/icesound"

global sound_status_last
sound_status_last=""

def getServerExec(*args):
   global server_exec
   return str(server_exec).strip()

def getServerExecShort(*args):
   return getServerExec()[getServerExec().rfind("/")+1:len(getServerExec())].strip()

def getSuggestedCommandLine(*args):
   global server_exec
   global wav_dir
   global audio_defaults
   wavd=str(wav_dir)
   if wavd.endswith("/"):  wavd=wavd[0:len(wavd)-1]
   def_se=getServerExec()+" --interface=ESD --server=localhost:16001 -v --sample-dir="+wavd+" &"
   if str(wav_dir).endswith("/"):
     def_se=getServerExec()+" --interface=ESD --server=localhost:16001 -v  --sample-dir="+wavd+" &"
   try:
     se=getServerExec()+" "
     if audio_defaults.has_key("interface"):
       iface=str(audio_defaults["interface"]).lower()
       se=se+"--interface="+iface.upper()
       if iface=="oss":
         if audio_defaults.has_key("oss_dev"): se=se+" --device="+str(audio_defaults["oss_dev"])
       if iface=="esd":
	 is_loc=0
	 if audio_defaults.has_key("esd_local"):
		if str(audio_defaults["esd_local"])=="1": 
			is_loc=1
	 if is_loc==0:
         	if audio_defaults.has_key("esd_host"): 
			se=se+" --server="+str(audio_defaults["esd_host"])+":"
         		if audio_defaults.has_key("esd_port"): 
           			se=se+str(audio_defaults["esd_port"])
        	 	else:
           			se=se+"16001"
       if iface=="yiff":
         if audio_defaults.has_key("yiff_host"): se=se+"  --server="+str(audio_defaults["yiff_host"])+":"
         if audio_defaults.has_key("yiff_port"): 
           se=se+str(audio_defaults["yiff_port"])
         else:
           se=se+"9433"
         if audio_defaults.has_key("yiff_auto"): 
           if str(audio_defaults["yiff_auto"])=="1":
             se=se+" --audio-mode-auto"
       return se+" -v --sample-dir="+wavd+" &"
     else:
       return def_se
   except:
      pass
     #return def_se

class icewindow :
    def __init__ (self) :
	icewindow = Window (WINDOW_TOPLEVEL)
        global icey
        icey=self
        tips = TIPS   # icewmcp_common
	icewindow.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(icewindow)
	icewindow.set_title (_("Ice Sound Manager")+" "+ism_version)
	icewindow.set_position (WIN_POS_CENTER)
        icewindow.realize()
        self.tips=tips
	self.icewindow = icewindow
	mainvbox1 = VBox (0, 0)
	mainvbox = VBox (0, 0)
	mainvbox.set_border_width (2)
	self.mainvbox = mainvbox

        # MENUS
        ag = AccelGroup()
        itemf = ItemFactory(MenuBar, "<main>", ag)
	self.ag=ag
	self.itemf=itemf
        itemf.create_items([
            # path              key           callback    action#  type
            (_("/_File"),          "<alt>F",         None,             0, "<Branch>"),
            (_("/_File/_Load Sound Theme..."),    "<control>O", showThemeLoad,     1, ""),
            (_("/_File/_Save Sound Theme..."),  "<control>S", showThemeWindow,   2, ""),
	    (_('/_File/sep1'), None, None, 2, '<Separator>'),
 	    (_("/_File")+"/_"+FILE_RUN,"<control>R", rundlg,421,""),
 	    (_("/_File")+"/_"+_("Check for newer versions of this program..."), "<control>U", checkSoftUpdate,420,""),
            (_("/_File/sep1"),     None,         None,             3, "<Separator>"),
            (_("/_File/_Quit"),    "<control>Q", quit,         4, ""),
            (_("/_IceSound Server"),           "<alt>I",         None,             5, "<Branch>"),
            (_("/_IceSound Server/_Wav Storage Directory"),     "<control>W", askWavDir,      6, ""),
            (_("/_IceSound Server/_Audio Interface"),    "<control>A", showAudio,     7, ""),
            (_("/_IceSound Server/IceSound _Executable"),   "<control>E", askExec,    9, ""),
            (_("/_IceSound Server/sep2"),     None,         None,            10, "<Separator>"),
            (_("/_IceSound Server/_Stop Sound Server"),  None,         stopServer,  11, ""),
            (_("/_IceSound Server/sep3"),     None,         None,            12, "<Separator>"),
            (_("/_IceSound Server/(_Re)Start Sound Server"), None, startServer, 13, ""),
            (_("/_Options"), "<alt>O",       None, 14, "<Branch>"),
            (_("/_Options/_Preferences..."),  "<control>P",         showOptions,  15, ""),
            (_("/_Options/Run _Setup"),  None, runSetup,  21, ""),
            (_("/_Help"),          "<alt>H",         None,            16, "<LastBranch>"), 
            (_("/_Help/_About..."), "F2",        showAbout,   17, ""),
  (_("/_Help/Ice Sound _Manager Help")+"...", "F4", displayHelp,5005, ""),  #added, 4/26/2003
            (_("/_Help/IceSound _Server Help"), "F6",        showServerHelp,   19, ""),
            (_("/_Help/_Sample Server Script"), "F7",        showScriptHelp,   20, ""),
            (_("/_Help/_Bug Reports and Comments"), "F8",        showBugHelp,   22, ""),
  	    (_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  	    (_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5005, ""),
        ])
        icewindow.add_accel_group(ag)
        menubar1 = itemf.get_widget("<main>")
	self.menubar=menubar1

	# added 6.21.2003 - "run as root" menu selector
	self.leftmenu=self.menubar.get_children()[0].get_submenu()
	self.run_root_button=CheckMenuItem(" "+RUN_AS_ROOT)
	self.leftmenu.prepend(self.run_root_button)

	mainvbox1.pack_start( menubar1, 0, 0, 0)
	mainvbox1.pack_start(mainvbox,1,1,0)
	mainvbox.pack_start( getImage(getPixDir()+"ism_header.png",_("Ice Sound Manager")), 0, 0, 4)
	themehbox = HBox (0, 0)
	themehbox.pack_start( Label (_("Sound Theme")+":") , 0, 0, 8)
        themelist=Combo()
        self.themelist=themelist
	themetext = themelist.entry
	themetext.set_text ( _('[NONE]'))
	themetext.set_editable ( 1)
	tips.set_tip (themetext, _("The current sound theme, if any"))
	self.themetext = themetext
	themehbox.pack_start( themelist, 1, 1, 0)
        themeselbutton=getIconButton(icewindow,STOCK_REFRESH,_("Reload"))
        themeselbutton.connect("clicked",selectTheme)
        themehbox.pack_start(themeselbutton,0,0,5)
        self.themeselbutton=themeselbutton
        tips.set_tip(themeselbutton,_("Switch to the selected theme"))
	themehbox.set_border_width(2)
	mainvbox.pack_start( themehbox, 0, 0, 3)

	themehbox2 = HBox (0, 0)
	themehbox2.pack_start(  Label(" "), 1, 1, 3)
        savebutt=getPixmapButton(icewindow,STOCK_SAVE,_("Save..."))
        tips.set_tip(savebutt,_("Click to SAVE this theme."))
        savebutt.connect("clicked",showThemeWindow)
	self.savebutt = savebutt
	themehbox2.pack_start( savebutt, 0, 0, 4)
        loadbutt=getPixmapButton(icewindow,STOCK_OPEN,_("Load..."))
        tips.set_tip(loadbutt,_("Click to LOAD a new theme."))
        loadbutt.connect("clicked",showThemeLoad)
	self.loadbutt = loadbutt
	themehbox2.pack_start( loadbutt, 0, 0, 0)
	themehbox2.pack_start(  Label(" "), 1, 1, 3)
	mainvbox.pack_start( themehbox2, 0, 0, 3)
	mainvbox.pack_start( HSeparator(), 0, 0, 3)

	eventvbox = VBox (0, 0)
	self.eventvbox = eventvbox
	eventtable = Table (3, 3, 0)
	eventtable.set_row_spacing(2,6)
	self.eventtable = eventtable
	selsoundtext = Entry ()
	selsoundtext.set_text ( _('[NONE]'))
	selsoundtext.set_editable ( 0)
	tips.set_tip (selsoundtext, _("Click 'Change' to change this sound"))
	self.selsoundtext = selsoundtext

	eventlab = Label (_("Sound Event")+":")
	eventlab.set_padding ( 9, 0)
	eventlab.set_alignment ( 0, 0.5)
	self.eventlab = eventlab
	eventtable.attach( eventlab, 0, 1, 0, 1, (FILL), (0), 2, 0)
	selsoundlab = Label (_("Selected Sound")+":")
	selsoundlab.set_padding ( 2, 0)
	selsoundlab.set_alignment ( 0, 0.5)
	self.selsoundlab = selsoundlab
	eventtable.attach( selsoundlab, 1, 2, 0, 1, (FILL), (0), 0, 0)
	#eventtable.attach( Label(" "), 2, 3, 0, 1, (FILL), (FILL), 0, 0)
	#eventtable.attach( Label(" "), 4, 5, 0, 1, (FILL), (FILL), 0, 0)

	eventcombo = Combo ()
        global event_desc
        el=event_desc.keys()
        el.sort()
        eventcombo.set_popdown_strings(el)
	eventcombo.set_border_width ( 3)
	self.eventcombo = eventcombo
	event_entry =eventcombo.entry
	event_entry.set_editable ( 1)
	self.event_entry  = event_entry 
	global last_to
	last_to=None
	eventtable.attach( eventcombo, 0, 1, 1, 2, (EXPAND+FILL), (0), 9, 0)
	eventtable.attach( selsoundtext, 1, 2, 1, 2, (EXPAND+FILL), (0), 0, 0)
	selsoundbutt = getPixmapButton(icewindow, STOCK_CDROM,_("Change..."))
        selsoundbutt.connect("clicked",changeSound)
	tips.set_tip (selsoundbutt, _("Select a sound for this event"))
	self.selsoundbutt = selsoundbutt
	eventtable.attach( selsoundbutt, 0, 1, 2, 3, (FILL), (0), 13, 0)
	nosoundbutt = getPixmapButton(icewindow, STOCK_DIALOG_ERROR ,_("No Sound"))
        nosoundbutt.connect("clicked",doNoSound)
	tips.set_tip (nosoundbutt, _("Set the sound for this event to NO sound"))
	self.nosoundbutt = nosoundbutt
	eventtable.attach( nosoundbutt, 1, 2, 2, 3, (FILL), (0), 0, 0)
	enablebutt = CheckButton (_("Enabled"))
        enablebutt.connect("toggled",checkEnable)
	enablebutt.set_border_width ( 2)
	tips.set_tip (enablebutt, _("Enable/Disable the sound for the selected event"))
	self.enablebutt = enablebutt
	eventtable.attach( enablebutt, 2, 3, 2, 3, (FILL), (0), 6, 0)

	playbox=HBox(0,0)
	playbox.set_spacing(2)
	playbutt = getIconButton(icewindow, STOCK_GO_FORWARD , _("Play"))
        playbutt.connect("clicked",playSound)
	tips.set_tip (playbutt, _("Play this sound with your chosen wav player"))
	self.playbutt = playbutt
	playbox.pack_start(playbutt,0,0,2)
	stopbutt = getIconButton(icewindow, STOCK_STOP ,_("Stop"))
        stopbutt.connect("clicked",stopSound)
	tips.set_tip (stopbutt, _("Stop playing this sound"))
	self.stopbutt = stopbutt
	playbox.pack_start(stopbutt,0,0,2)
	editbutt = getIconButton(icewindow, STOCK_SELECT_COLOR ,_("Edit"))
        editbutt.connect("clicked",editSound)
	tips.set_tip (editbutt, _("Edit this sound with your chosen sound editor"))
	self.editbutt = editbutt
	playbox.pack_start(editbutt,0,0,2)
	eventtable.attach( playbox, 2, 3, 1, 2, (0), (0), 10, 2)

	eventvbox.pack_start(eventtable, 1, 1, 0)
	mainvbox.pack_start( eventvbox, 0, 0, 7)
	mainvbox.pack_start(Label ("  "), 1, 1, 0)
	mainvbox.pack_start(HSeparator (), 0, 0, 3)
	servervbox = VBox (0, 0)
	self.servervbox = servervbox
	cmdlinelab = Label (_("Suggested Sound Server Command Line:"))
	cmdlinelab.set_justify ( JUSTIFY_LEFT)
	cmdlinelab.set_alignment ( 0.0200001, 0.5)
	self.cmdlinelab = cmdlinelab
	servervbox.pack_start ( cmdlinelab, 0, 0, 0)
	cmdlinehbox = HBox (0, 0)
	entry2 = Entry ()
	self.entry2 = entry2
	cmdlinehbox.pack_start( entry2, 1, 1, 4)
	cmdlinehbox.pack_start( Label(" "), 0, 0, 2)
        serverwhat=getPixmapButton(icewindow, STOCK_DIALOG_INFO ,WHATS_THIS)
        serverwhat.connect("clicked",showCmdHelp)
	tips.set_tip (serverwhat, _("Help on the Sound Server Command Line"))
	self.serverwhat = serverwhat
	cmdlinehbox.pack_start( serverwhat, 0, 0, 5)
	servervbox.pack_start( cmdlinehbox, 0, 0, 0)

	servbuttonhbox = HBox (0, 0)
	servbuttonhbox.set_border_width(4)
	servbuttonhbox.set_spacing(5)
	serverstartbutt = getPixmapButton(icewindow, STOCK_YES ,_("(Re)start IceSound Server"))
        serverstartbutt.connect("clicked",startServer)
	tips.set_tip (serverstartbutt, _("(Re)start  the IceSound Server to enable IceWM sound events"))
	self.serverstartbutt = serverstartbutt
	servbuttonhbox.pack_start( serverstartbutt, 0, 0, 0)
	stopserverbutt = getPixmapButton(icewindow, STOCK_NO ,_("Stop IceSound Server"))
        stopserverbutt.connect("clicked",stopServer)
	tips.set_tip (stopserverbutt, _("Stopping the IceSound server will disable IceWM sound events"))
	self.stopserverbutt = stopserverbutt
	servbuttonhbox.pack_start(  Label(""), 1, 1, 1)
	servbuttonhbox.pack_start(stopserverbutt, 0, 0, 0)
	servervbox.pack_start( servbuttonhbox, 0, 0, 2)

	applybox = HBox (0, 0)
	applybox.set_border_width(4)
	applybox.set_spacing(5)
	atbutt = getPixmapButton(icewindow, STOCK_CONVERT ,_("Apply Sound Theme"))
        atbutt.connect("clicked",applySoundTheme)
	tips.set_tip (atbutt, _("Apply this sound theme and start using this set of sounds now."))
	apphelp = getPixmapButton(icewindow, STOCK_DIALOG_QUESTION ,APP_HELP_STRR)
        apphelp.connect("clicked",self.app_help_cb)
	tips.set_tip (apphelp, APP_HELP_STRR)
	applybox.pack_start(atbutt, 0, 0, 0)
	applybox.pack_start(  Label(""), 1, 1, 1)
	applybox.pack_start(apphelp, 0, 0, 0)
	servervbox.pack_start(applybox, 0, 0,3)

	mainvbox.pack_start( servervbox, 1, 1, 0)
        global statusbar
	statusbar =Statusbar ()
	self.statusbar = statusbar
        global statid
        global statmessid
        statid=statusbar.get_context_id("icesound context")
        #Startup stuff
        setupFiles()
        loadOptions()
        global current_theme_file
        searchForThemes()
        serrors=loadTheme(current_theme_file,1,0)
        try:
           icey.entry2.set_text(getSuggestedCommandLine())
        except:
          pass
        getServerVersion()
	global wav_dir
	if wav_dir==getIceWMConfigPath()+"sounds"+os.sep:
		self.run_root_button.set_active(1)
	self.run_root_button.connect("toggled",run_as_root)      
        showStatus(_("Ice Sound Manager")+" "+ism_version+".")
	mainvbox.pack_start( statusbar, 0, 0, 0)
	statusbarcopy =Statusbar ()
	mainvbox.pack_start( statusbarcopy, 0, 0, 0)
	statusbarcopy.push(statusbarcopy.get_context_id("icesoundCopyRight")," Ice Sound Manager Copyright (c) 2002-2004 Erica Andrews.")
	self.statusbarcopy=statusbarcopy
	icewindow.add ( mainvbox1)	
	icewindow.show_all()
	gtk.timeout_add(60,updateStatusTimeout)
	gtk.timeout_add(8,showSoundEventTO)
        global need_setup
        if need_setup: runSetup()
        else:
          if serrors: showSoundSetError(serrors)

    def app_help_cb(self, *args) :
	displayHelp(5005)




def showStatus(statustext,*args):
	global sound_status
	sound_status=str(statustext)	

def updateStatusTimeout(*args):
    global statid
    global statmessid
    global statusbar
    global sound_status
    global sound_status_last
    if sound_status_last==sound_status: return 1
    statmessid=statusbar.push(statid," "+_(sound_status))
    sound_status_last=sound_status
    return 1

def hideit(*args):
   global icemain
   icemain.hide()
   icemain.destroy()
   return TRUE

class iceoptions:
    def __init__ (self) :
	iceoptions = Window (WINDOW_TOPLEVEL)
	iceoptions.set_data("ignore_return",1)
	iceoptions.connect("key-press-event",keyPressClose)
	self._root = iceoptions
        tips = TIPS
	iceoptions.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(iceoptions)
	iceoptions.set_title (_("Ice Sound Manager Options"))
        iceoptions.connect("destroy", hideo)
	iceoptions.set_position ( WIN_POS_CENTER)
        iceoptions.realize()
	self.iceoptions = iceoptions
	vbox1 = VBox(0, 0)
	self.vbox1 = vbox1
	titlelab = Label (_("Ice Sound Manager Options"))
	self.titlelab = titlelab
	vbox1.pack_start( titlelab, 0, 0, 11)
	table1 = Table (2, 3, 0)
	self.table1 = table1
	playtext = Entry ()
	self.playtext = playtext
	table1.attach(playtext, 1, 2, 0, 1, (EXPAND+FILL), (0), 0, 0)
	edittext = Entry ()
	self.edittext = edittext
	table1.attach(edittext, 1, 2, 1, 2, (EXPAND+FILL), (0), 0, 0)
	playerlab = Label (_("Wav Player Command Line"))
	playerlab.set_alignment ( 0, 0.5)
	self.playerlab = playerlab
	table1.attach(playerlab, 0, 1, 0, 1, (FILL), (0), 4, 0)
	editorlab = Label (_("Wav Editor Command Line"))
	editorlab.set_alignment ( 0, 0.5)
	self.editorlab = editorlab
	table1.attach(editorlab, 0, 1, 1, 2, (FILL), (0), 4, 0)
	what1 = getPixmapButton(iceoptions, STOCK_DIALOG_INFO ,WHATS_THIS)
        what1.connect("clicked",showPlayHelp)
	tips.set_tip (what1,CLICK_HELP)
	self.what1 = what1
	table1.attach(what1, 2, 3, 0, 1, (FILL), (0), 4, 0)
	what2 = getPixmapButton(iceoptions, STOCK_DIALOG_INFO ,WHATS_THIS)
        what2.connect("clicked",showEditHelp)
	tips.set_tip (what2,CLICK_HELP)
	self.what2 = what2
	table1.attach(what2, 2, 3, 1, 2, (FILL), (0), 4, 0)
	vbox1.pack_start( table1, 1, 1, 0)
	hseparator1 = HSeparator ()
	self.hseparator1 = hseparator1
	vbox1.pack_start( hseparator1, 1, 1, 8)
	table2 = Table (3, 2, 0)
	self.table2 = table2
	autocheck = CheckButton(_("Automatically start IceSound server when Ice Sound Manager starts"))
	autocheck.set_active (1)
	tips.set_tip (autocheck,_("Automatically start IceSound server when Ice Sound Manager starts"))
	self.autocheck = autocheck
	table2.attach ( autocheck, 0, 1, 0, 1, (EXPAND+FILL), (0), 4, 0)
	copycheck = CheckButton(_("Copy files instead of linking them"))
	tips.set_tip (copycheck,_("Copy files instead of linking them"))
	self.copycheck = copycheck
	table2.attach ( copycheck, 0, 1, 1, 2, (EXPAND+FILL), (0), 4, 0)
	stdouttext = CheckButton(_("Launch the IceSound Server in a terminal window"))
	stdouttext.set_active ( 1)
	tips.set_tip (stdouttext,_("Launch the IceSound Server in a terminal window"))
	self.stdouttext = stdouttext
	table2.attach ( stdouttext, 0, 1, 2, 3, (EXPAND+FILL), (0), 4, 0)
	what4 = getPixmapButton(iceoptions,STOCK_DIALOG_INFO,WHATS_THIS)
	tips.set_tip (what4,CLICK_HELP)
	self.what4 = what4
        what4.connect("clicked",showCopyHelp)
	table2.attach ( what4, 1, 2, 1, 2, (FILL), (0), 4, 0)
	what5 = getPixmapButton(iceoptions,STOCK_DIALOG_INFO,WHATS_THIS)
	tips.set_tip (what5,CLICK_HELP)
	self.what5 = what5
        what5.connect("clicked",showTerminalHelp)
	table2.attach ( what5, 1, 2, 2, 3, (FILL), (0), 4, 0)
	what3 = getPixmapButton(iceoptions,STOCK_DIALOG_INFO,WHATS_THIS)
        what3.connect("clicked",showAutoHelp)
	tips.set_tip (what3,CLICK_HELP)
	self.what3 = what3
	table2.attach ( what3, 1, 2, 0, 1, (FILL), (0), 4, 0)
	vbox1.pack_start( table2, 1, 1, 0)
	hseparator2 = HSeparator ()
	self.hseparator2 = hseparator2
	vbox1.pack_start( hseparator2, 1, 1, 12)
	hbox1 = HBox (0, 0)
	self.hbox1 = hbox1
	cancelbutt = getPixmapButton(iceoptions, STOCK_CANCEL ,_("Cancel"))
        cancelbutt.connect("clicked",hideo)
	tips.set_tip (cancelbutt,_("Cancel without saving changes"))
	self.cancelbutt = cancelbutt
	hbox1.pack_start( cancelbutt, 1, 1, 6)
	frame1 =Label("            ")
	self.frame1 = frame1
   	hbox1.pack_start( frame1, 1, 1, 0)
	savebutt = getPixmapButton(iceoptions, STOCK_SAVE ,_("Save"))
        savebutt.connect("clicked",hideOptions)
   	tips.set_tip (savebutt,_("Save changes and close this window"))
	self.savebutt = savebutt
        iceoptions.set_modal(1)
	hbox1.pack_start( savebutt, 1, 1, 6)
	vbox1.pack_start( hbox1, 1, 1, 5)
	vbox1.set_border_width(2)
	iceoptions.add( vbox1)

def hideo(*args):
   global iceo
   iceo.iceoptions.hide()
   iceo.iceoptions.destroy()
   return TRUE

def showOptions(*args):
   global iceo
   global wav_cmd
   global wav_edit
   global use_terminal
   global copy_wavs
   global start_server
   iceo=iceoptions()
   iceo.playtext.set_text(str(wav_cmd).strip())
   iceo.edittext.set_text(str(wav_edit).strip())
   iceo.copycheck.set_active(str(copy_wavs)=="1")
   iceo.autocheck.set_active(str(start_server)=="1")
   iceo.stdouttext.set_active(str(use_terminal)=="1")
   iceo.iceoptions.show_all()

def hideOptions(*args):
  global iceo
  global wav_cmd
  global wav_edit
  global use_terminal
  global copy_wavs
  global start_server
  global current_theme_file
  use_terminal=(int(iceo.stdouttext.get_active())==1)
  start_server=(int(iceo.autocheck.get_active())==1)
  copy_wavs=(int(iceo.copycheck.get_active())==1)  
  wav_cmd=iceo.playtext.get_text().strip()
  wav_edit=iceo.edittext.get_text().strip()
  iceo.iceoptions.hide()
  iceo.iceoptions.destroy()
  saveOptions()
  if iceo.playtext.get_text().find("%f") == -1 :
    showStatus(_("WARNING: '%f' needed in Wav Player Command Line for Ice Sound Manager to play them."))
  if iceo.edittext.get_text().find("%f") == -1 :
    showStatus(_("WARNING: '%f' needed in Wav Editor Command Line for Ice Sound Manager to edit them."))
  loadTheme(current_theme_file,0,1)



############  HELP Section  ##############

def showModalHelp(helpText="Help text here.",*args):
	commonAbout(_("Ice Sound Manager Help")+" "+ism_version,  
			str(helpText), 0, getPixDir()+"ism_header.png", "", 0,1)


def showCmdHelp(*args):
	showModalHelp(_("This section of Ice Sound Manager deals with your IceSound Server itself.\n\nSUGGESTED SOUND SERVER COMMAND LINE:\nThis field shows you the auto-generated command line that is being used to launch your IceSound Server.  It is provided so YOU can see exactly what is being launched on your system and how, and may be useful for troubleshooting.  You can copy and paste the text in this field into a terminal window to aid in any troubleshooting you must do.  This field contains the EXACT same command that is executed when you click '(Re)Start IceSound Server' and is the command that will be executed if you have enabled automatic starting of your IceSound Server when Ice Sound Manager starts. NOTE: Editing the text in this field doeshas NOT effect command Ice Sound Manager launches to start your server. Anything you type here is ignored by Ice Sound Manager.  The 'Suggested Sound Server Command Line' is provided for informational purposes only.  You may also find this field useful for pasting into scripts, etc.\n\n(RE)START ICESOUND SERVER:\nThis will execute the UNEDITED version of the command line that appears in 'Suggested Sound Server Command Line'  to start/restart your IceSound Server.  Your IceWM sound events will NOT be enabled until the sound server has been started.  It is a good idea to restart the server whenever you have changed your sound theme, though Ice Sound Manager attempts to do this for you.\n\nSTOP ICESOUND SERVER:\nVery simply, this feature stops your IceSound Server, disabling all future sound events in IceWM.  NOTE:  Ice Sound Manager does not shutdown your sound server automatically when you exit Ice Sound Manager (it is assumed you want to keep your sound events enabled).  If you quit Ice Sound Manager, your IceSound Server will continue running, until you either click 'Stop IceSound Server' or issue a 'kill' command to your IceSound Server process. However, on most systems, the IceSound Server will shutdown automatically if you quit/restart your X Server."))

def showTerminalHelp(*args):
	showModalHelp(_("If CHECKED, your Ice Sound Server will be started in a terminal window.  The terminal application to be used is determined by the value of your $TERM environment variable (generally, xterm, gnome-terminal, kterm, or eterm).  You can determine the terminal application used to launch your Ice Sound Server, by setting the environment variable $TERM.  Type 'echo $TERM' to see what your default terminal application is.  NOTE: Your default terminal application in $TERM must accept the -e command line option and must understand it in a way similiar to xterm  for this option to work.  The only exception to this rule is gnome-terminal."))

def showAutoHelp(*args):
	showModalHelp(_("This option only applies to when ICE SOUND MANAGER is started, not when IceWM is started.  If CHECKED, Ice Sound Manager will start your Ice Sound Server (if it is not already running) whenever you start Ice Sound Manager.  Your Ice Sound Server will be started with the command shown in the field 'Suggested Sound Server Command Line'.  Leave this option unchecked if you do NOT want automatic starting of your Ice Sound Server when Ice Sound Manager is launched."))

def showCopyHelp(*args):
	showModalHelp(_("This option determines whether your .wav sounds will be LINKED or COPIED into your IceSound Server's Wav Storage Directory (as defined under the menu 'IceSound Server' -> 'Wav Directory'.  Leave this option UNCHECKED if you would rather your files be LINKED into your IceSound Server's Wav Storage Directory.  (This will save disk space, but your sound events will not play if you move/delete the original files.  Be sure to keep your sound themes current if you choose this method.)   CHECK this option if you would rather your .wav sounds be COPIED to your IceSound Server's Wav Storage Directory.  (This method uses more disk space, but ensures that your sound events will be unaffected should you move/delete the original .wav files.)  Which method you choose is up to you."))

def showPlayHelp(*args):
	showModalHelp(_("If you want to be able to PLAY your sounds in Ice Sound Manager, you must enter the command to launch a .wav sound player on your system.  Most people should be able to use the default command.  However, you may want or need to change this command.   NOTE:  Any command line you enter MUST contain the string '%f' somewhere in the command line  (this signifies where the .wav's filename should go in the command line.)  It is YOUR job to know or find out what command line to use to launch your .wav player.  If you fail to include '%f' in your command line, you will see an error message on the status bar when you attempt to play your sounds.  I personally suggest you use a command line that opens a fast, console-based .wav player (like wavplay) for the sake of speed. "))

def showEditHelp(*args):
	showModalHelp(_("If you want to be able to EDIT your sounds in Ice Sound Manager, you must enter the command to launch a .wav sound editor on your system.  Most people should be able to use the default command, IF they have the Sweep sound editor installed.  However, you may want or need to change this command.   NOTE:  Any command line you enter MUST contain the string '%f' somewhere in the command line  (this signifies where the .wav's filename should go in the command line.)  It is YOUR job to know or find out what command line to use to launch your .wav editor.  If you fail to include '%f' in your command line, you will see an error message on the status bar when you attempt to edit your sounds."))

def showBugHelp(*args):
	showModalHelp(_("Ice Sound Manager is in no way 'officially' affiliated with IceWM, IceSound Server, or its creators.  Ice Sound Manager is a FRONTEND to the IceSound Server.  The project is still in its formative stages.  Expect bugs. COURTEOUSLY report bugs in Ice Sound Manager to PhrozenSmoke [at] yahoo.com.  If you have any other comments or suggestions, those are welcomed as well.  Please do NOT report bugs in your IceSound Server, your IceWM environment, or ask me for help on getting your IceSound Server to run.  Also, please read 'Ice Sound Manager Help' under the 'Help' menu (or press F4) before reporting a 'bug'. You will find useful troubleshooting suggestions there. ".replace(" [at] ","@") ))

def showServerHelp(*args):
	showModalHelp(_("ICESOUND SERVER HELP")+"\n"+_("You are running IceSound Server version")+": "+server_version+"\n\n"+_("The following is the output returned by running your IceSound Server executable")+" ("+str(getServerExec())+") "+_("with the --help switch.")+"  "+_("You may find it useful for trouble shooting problems with your sound server.  If you see nothing below or see an error message, try modifying your IceSound Server command line, by clicking 'IceSound Server' on the menu. Also, make sure you have the permissions necessary to run the server executable")+":\n\n\n"+string.join( os.popen(str(getServerExec())+" --help").readlines()," ") +"\n")

def showScriptHelp(*args):
	showModalHelp(_("SAMPLE SERVER SCRIPT\nHere is a simple bourne/bash shell script you can use to easily start and stop your IceSound server.  All you should have to do is copy and paste it to a file.  Save it as /usr/bin/icesoundsh.  Type 'chmod 755 /usr/bin/icesoundsh' at a terminal.  You can start the server by typing 'icesoundsh start', and shutdown the server by typing 'icesoundsh stop'.  Hopefully, this is useful.  Note: It's probably not a smart idea to save this script under /usr/bin/icesound, especially if the server executable itself is called 'icesound'.  Copy and paste the section below this line")+":\n\n---------------\n#! /bin/sh\n#\n# icesound          Start/Stop the icesound server.\n#\n# chkconfig: 2345 40 60\n# description: The IceWM sound events sound server\n# processname: icesound\n\n\n# Source function library.\n. /etc/rc.d/init.d/functions\n\nRETVAL=0\n\n# See how we were called.\ncase \"$1\" in\n  start)\n\techo -n \"Starting IceSound Server (version "+server_version+"): \"\n\texec "+str(getSuggestedCommandLine())+"  > /dev/null\n\tRETVAL=$?\n\techo\n\tRETVAL=$?\n\t;;\n  stop)\n\techo -n \"Stopping IceSound server: \"\n\tkillall -9 "+getServerExecShort()+"\n\tRETVAL=$?\n\techo\n\tRETVAL=$?\n\t;;\n  status)\n\tstatus icesound\n\tRETVAL=$?\n\t;;\n  restart)\n  \t$0 stop\n\t$0 start\n\tRETVAL=$?\n\t;;\n  reload)\n\tkillall -HUP "+getServerExecShort()+"\n\tRETVAL=$?\n\t;;\n  *)\n\techo \"Usage: icesound {start|stop|status|restart}\"\n\texit 1\nesac\n\nexit $RETVAL\n")


def showAbout(*args):
	commonAbout(_("ABOUT ICE SOUND MANAGER")+" "+ism_version,_("ABOUT ICE SOUND MANAGER")+" "+ism_version+"\n\n"+"Copyright (c) 2002-2004\nErica Andrews\nPhrozenSmoke ['at'] yahoo.com\n                http://icesoundmanager.sourceforge.net\nLicense: GNU General Public License\n\n"+_("Ice Sound Manager is in no way 'officially' affiliated with IceWM, IceSound Server, or its creators.  Ice Sound Manager is a FRONTEND to the IceSound Server.  Ice Sound Manager is freeware and open source. In addition, Ice Sound Manager is now part of a larger project, called IceWM Control Panel.  As of version 0.2-beta-2, Ice Sound Manager is distributed under the General Public License (GPL). See the 'IceSoundManager-LICENSE' file for details.  This software is distributed as-is, without any warranty or guarantee of any kind. Use at your own risk!\n\nIce Sound Manager was designed to ease the management of sound events, sound themes, and the sound server in the IceWM environment.  It is also intended to be an improvement upon the noble, but primitive icesndcfg."),0 ,getPixDir()+"ism_header.png")	  


# Directory Browsing

class dirdialog :
    def __init__ (self) :
	dirdialog = Window (WINDOW_TOPLEVEL)
	dirdialog.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(dirdialog)
	dirdialog.set_data("ignore_return",1)
	dirdialog.connect("key-press-event",keyPressClose)
	self._root = dirdialog
	dirdialog.set_position (WIN_POS_CENTER)
	dirdialog.set_modal ( 1)
	dirdialog.set_title ( _("Ice Sound Manager"))
        tips =TIPS
	self.dirdialog = dirdialog
	vbox1 = VBox (0, 0)
	vbox1.set_border_width ( 2)
	#vbox1.set_size_request (355, 158)
	self.vbox1 = vbox1
	scrolledwindow1 =ScrolledWindow ()
	self.scrolledwindow1 = scrolledwindow1
	scrolledwindow1.set_size_request(-1,120)
	htext = TextView ()
	htext.set_editable (0)
        htext.set_wrap_mode(WRAP_WORD)
    	# Force white background, make sure all colors are viewable
   	for gg in [STATE_NORMAL, STATE_ACTIVE, STATE_PRELIGHT,
					STATE_SELECTED, STATE_INSENSITIVE]:
					htext.modify_base(gg,COL_WHITE)
	self.htext = htext
	scrolledwindow1.add ( htext)
	vbox1.pack_start ( scrolledwindow1, 1, 1, 6)
	hbox1 =HBox (0, 0)
	self.hbox1 = hbox1
	ltext = Entry ()
        ltext.set_editable (0)
	ltext.set_size_request (240, -1)
	self.ltext = ltext
	hbox1.pack_start ( ltext, 1, 1, 4)
	lbutton =getPixmapButton(dirdialog, STOCK_OPEN ,_("Browse..."))
	TIPS.set_tip(lbutton,_("Browse..."))
	self.lbutton = lbutton
	hbox1.pack_start ( lbutton, 0, 0, 5)
	vbox1.pack_start ( hbox1, 1, 1, 0)
	hbox2 = HBox (0, 0)
	self.hbox2 = hbox2
	label1 = Label ("  ")
	self.label1 = label1
	hbox2.pack_start ( label1, 1, 1, 0)
	closebutton = getPixmapButton(dirdialog, STOCK_APPLY ,_("OK"))
        tips.set_tip(closebutton,_("Close and save changes"))
	self.closebutton = closebutton
	hbox2.pack_start ( closebutton, 1, 1, 0)
	label2 = Label ("  ")
	self.label2 = label2
	hbox2.pack_start ( label2, 1, 1, 0)
	vbox1.pack_start ( hbox2, 0, 0, 6)
	dirdialog.add ( vbox1)

    def setHelpText(self, helpstuff):
	hbuf=self.htext.get_buffer()
	hbuf.set_text("")
	text_buffer_insert(hbuf,  get_renderable_tab(hbuf, 
		HELP_FONT2,COL_BLACK,LANGCODE), str(helpstuff) )	

def hideDir(*args):
   global fdir
   fdir.dirdialog.hide()
   fdir.dirdialog.destroy()
   return TRUE

def askExec(*args):
   global fdir
   global server_exec
   d=dirdialog()
   fdir=d
   d.closebutton.connect("clicked",updateExec) 
   d.lbutton.connect("clicked",doExecDia)
   d.ltext.set_text(str(server_exec))
   d.setHelpText(_("Select your IceSound Server executable.  This is generally either in the /usr/X11R6/bin/  or  /usr/bin/  directory and is generally named either 'icesound' or 'icesound-gnome'.  Be sure you have the correct permissions to execute the IceSound Server and that you have the permissions to run servers/daemons on your system."))
   d.dirdialog.show_all()

def updateExec(*args):
   global server_exec
   global fdir
   if checkExec(str(fdir.ltext.get_text())):
     server_exec=checkExec(str(fdir.ltext.get_text()))
     saveOptions()
     hideDir()  
   else:
     showStatus(_("ERROR!  Select your IceSound Server executable file first."))

def doExecDia(*args):
   global sel_file
   global server_exec
   sel_file=server_exec
   f=showFileSelection(_("Select Your IceSound Server Executable"),execFile,execCancel)

def execFile(*args):
   global fdir
   fdir.ltext.set_text(checkExec(grabFile()))

def execCancel(*args):
  global fdir
  ffile=checkExec(str(fdir.ltext.get_text()))
  doFsHide()
  fdir.ltext.set_text(ffile)

def checkExec(fname,defname=""):
  if not fname:
    return defname
  if fname.strip().endswith("/"):
    return defname
  return fname

def askWavDir(*args):
   global fdir
   global wav_dir
   d=dirdialog()
   fdir=d
   d.closebutton.connect("clicked",updateWavDir) 
   d.ltext.set_text(str(wav_dir))
   d.lbutton.connect("clicked",doWavDia)
   d.setHelpText(_("Select the directory where your IceSound server looks  for its .wav files.  On most systems, this directory will be either    ~/.icesound/sounds/  or  /usr/X11R6/lib/X11/icewm/sounds/.  If you aren't sure, check the documentation for your IceSound server or do the trial-and-error method.   Generally, you should not go wrong with ~/.icesound/sounds/  under your home directory (example: /home/phrozen/.icewm/sounds/).  You may have to create this directory yourself if Ice Sound Manager can't. Be sure to select only directories where you have both 'read' and 'write' permissions. See the section entitled 'Wav Storage Directory' under 'Help' -> 'Ice Sound Manager Help' (or press F4)."))
   d.dirdialog.show_all()

def updateWavDir(*args):
   global fdir
   f=extractDirectory(str(fdir.ltext.get_text()))
   if f:
     hideDir()  
     setWavDir(f)
   else:
     showStatus(_("ERROR!  Select the IceSound Server's Wav storage directory first."))


# added 6.22.2003 - "run as root" functionality
def run_as_root(*args):
        global icey
	if icey.run_root_button.get_active():
		icey.menubar.deactivate()
		setWavDir(getIceWMConfigPath()+"sounds"+os.sep)
		showStatus(_("Done.")+"    [ROOT]:  "+getIceWMConfigPath()+"sounds"+os.sep)
		icey.icewindow.set_title (_("Ice Sound Manager")+" "+ism_version+"   [ROOT]")
	else:  # turn 'root' OFF
		icey.menubar.deactivate()
		setWavDir(getIceWMPrivConfigPath()+"sounds"+os.sep)
		showStatus(_("Done.")+":  "+getIceWMPrivConfigPath()+"sounds"+os.sep)
		icey.icewindow.set_title (_("Ice Sound Manager")+" "+ism_version)
	
	

def setWavDir(wdir,*args):
  global wav_dir
  global sound_events
  if wdir:
    serr=[]
    showStatus(_("Updating Wav Storage Directory..."))
    try:  # try to delete any old sound event files in the new wav_directory
      s=sound_events.keys()
      for i in s:
        try:
          f=os.popen("rm -f "+wdir+s+".wav > /dev/null")
        except:
          pass
    except:
      pass
    try: # try to remove the old directory ONLY if its empty, we won't remove .wavs
      os.rmdir(wav_dir)
    except:
      pass
    wav_dir=wdir # set the new directory    
    try: # try to create the new directory
      os.mkdir(wav_dir)
    except:
      pass
    try:  # transfer the new sound events to new directory
      s=sound_events.keys()
      for i in s:
        try:
          stat=setSoundForEvent(i,sound_events[i],0,0,1)
          if not stat: serr.append(_("Link/Copy")+"  "+sound_events[i]+_(" to ")+wav_dir+" : "+_("TRANSFER TO NEW DIRECTORY FAILED"))
        except:
          pass
    except:
      pass
    saveOptions()
    startServer()
    showStatus(_("Done."))
    if len(serr): showSoundSetError(serr)

def doWavDia(*args):
   global sel_file
   global wav_dir
   sel_file=wav_dir
   showFileSelection(_("Wav Storage Directory Selection"),wavFile,wavCancel)

def wavFile(*args):
   global fdir
   fdir.ltext.set_text(extractDirectory(grabFile()))

def wavCancel(*args):
  global fdir
  ffile=extractDirectory(str(fdir.ltext.get_text()))
  doFsHide()
  fdir.ltext.set_text(ffile)

def extractDirectory(fname):
    if not fname:  
      return ""
    fname=fname.strip()
    try:
      fname=fname.replace("~",os.environ["HOME"])
    except:
      pass
    if fname.endswith("/"):
     return fname
    else: 
      if fname.find("/") > -1:
        return fname[0:fname.rfind("/")+1].strip()
      else:
        return "/"
    return fname
   
def createFileSel(winTitle,ok_method,cancel_method,*args):
        global fs
        global sel_file
        fs = FileSelection()
	fs.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(fs)
	fs.set_data("ignore_return",1)
	fs.connect("key-press-event",keyPressClose)
        fs.set_title(str(winTitle))
        fs.set_position (WIN_POS_CENTER)
        fs.connect('destroy', cancel_method)
        if sel_file:
          fs.set_filename(sel_file)
        fs.ok_button.remove(fs.ok_button.get_children()[0])
        fs.ok_button.add(getPixmapVBox(fs, STOCK_APPLY ,_("OK")))
        fs.ok_button.connect('clicked', ok_method)
        fs.set_modal(1)
        fs.cancel_button.remove(fs.cancel_button.get_children()[0])
        fs.cancel_button.add(getPixmapVBox(fs, STOCK_CANCEL ,_("Cancel")))
        fs.cancel_button.connect('clicked', cancel_method)
        return fs

def grabFile(*args):   
        global fs
        global sel_file
        if not fs:
          return ""
 	sel_file=str(fs.get_filename()).strip()
	fs.hide()
        return sel_file

def doFsHide(*args):
     global fs
     fs.hide()
     fs.destroy()
     return TRUE

def showFileSelection(winTitle,ok_method,cancel_method,*args):
    f=createFileSel(winTitle,ok_method,cancel_method)
    f.show_all()
    return f


# Theme Management

class themewindow  :
    def __init__ (self) :
	themewindow = Window (WINDOW_TOPLEVEL)
	self._root = themewindow
        global themes
	themewindow.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(themewindow)
	themewindow.set_title (_("Save Theme..."))
	themewindow.set_data("ignore_return",1)
	themewindow.connect("key-press-event",keyPressClose)
	themewindow.set_position (WIN_POS_CENTER)
        themewindow.set_modal(1)
        tips=TIPS
	self.themewindow = themewindow
	vbox1 = VBox (0, 3)
	vbox1.set_border_width ( 10)
	self.vbox1 = vbox1
	label1 = Label (_("Theme Name:"))
	self.label1 = label1
	vbox1.pack_start( label1, 0, 0, 0)
	namecombo = Combo ()
	self.namecombo = namecombo
	nameentry = namecombo.entry
	tips.set_tip (nameentry,  _("Enter a descriptive name for your IceWM sound theme"))
	self.nameentry = nameentry
	vbox1.pack_start( namecombo, 0, 0, 0)
	label2 = Label ("  ")
	self.label2 = label2
	vbox1.pack_start( label2, 0, 0, 0)
	label3 = Label (_("Theme File:"))
	self.label3 = label3
	vbox1.pack_start( label3, 0, 0, 0)
	hbox1 = HBox (0, 12)
	self.hbox1 = hbox1
	filecombo = Combo ()
        filecombo.set_size_request(400,25)
	self.filecombo = filecombo
	file_entry = filecombo.entry
        if len(themes):
          tf=themes.values()
          tf.sort()
          filecombo.set_popdown_strings(copy.copy(tf))
          tf=themes.keys()
          tf.sort()
          namecombo.set_popdown_strings(copy.copy(tf))
	tips.set_tip (file_entry, _("Theme files"))
	self.file_entry = file_entry
        file_entry.set_editable(0)
	hbox1.pack_start( filecombo, 1, 1, 0)
	filebutton = getPixmapButton(themewindow, STOCK_OPEN ,_("Browse..."))
        filebutton.connect("clicked",chooseThemeFile)
	tips.set_tip (filebutton, _("Browse to select a file for saving"))
	self.filebutton = filebutton
	hbox1.pack_start( filebutton, 0, 0, 0)
	vbox1.pack_start( hbox1, 1, 1, 0)
	label6 = Label ("  ")
	self.label6 = label6
	vbox1.pack_start( label6, 0, 0, 0)
	hbox2 = HBox (1, 0)
	self.hbox2 = hbox2
	cancelbutt = getPixmapButton(themewindow, STOCK_CANCEL ,_("Cancel"))
        cancelbutt.connect("clicked",hideThemeWindow)
        themewindow.connect("destroy",hideThemeWindow)
	tips.set_tip (cancelbutt, _("Close this window and discard all changes"))
	self.cancelbutt = cancelbutt
	hbox2.pack_start( cancelbutt, 1, 1, 0)
	label7 = Label( "  ")
	self.label7 = label7
	hbox2.pack_start( label7, 1, 1, 0)
	savebutt = getPixmapButton(themewindow, STOCK_SAVE ,_("SAVE"))
        savebutt.connect("clicked",saveTheme)
	tips.set_tip (savebutt, _("Save theme and close this window"))
	self.savebutt = savebutt
	hbox2.pack_start( savebutt, 1, 1, 0)
	vbox1.pack_start( hbox2, 1, 1, 0)
	themewindow.add ( vbox1)


def showThemeWindow(*args):
  global themew
  global current_theme_file
  global current_theme
  themew=themewindow()
  if current_theme_file:
     themew.file_entry.set_text(current_theme_file)
  if current_theme:
     themew.nameentry.set_text(current_theme)
  themew.themewindow.show_all()
  
def hideThemeWindow(*args):
   global themew
   themew.themewindow.hide()
   themew.themewindow.destroy()
   return TRUE


def chooseThemeFile(*args):
   global sel_file
   global current_theme_file
   if current_theme_file:
     sel_file=current_theme_file
   showFileSelection(_("Save Sound Theme As..."),themeFile,themeCancel)

def themeFile(*args):
   global themew
   c=checkExec(grabFile(),"")
   themew.file_entry.set_text(c)
   global current_theme_file
   current_theme_file=c

def themeCancel(*args):
  global themew
  ffile=checkExec(str(themew.file_entry.get_text()))
  doFsHide()
  themew.file_entry.set_text(ffile)
   
def saveTheme(*args):
   global themew
   global current_theme_file
   global current_theme
   tname=themew.nameentry.get_text().strip()
   current_theme_file=themew.file_entry.get_text()
   if current_theme_file:
     if tname:
       current_theme=tname
       associateTheme(current_theme,current_theme_file)
       saveThemeFile()
       hideThemeWindow()
   else:
     showStatus(_("ERROR!  Enter a theme NAME and theme FILE first."))

def saveThemeFile(*args):
  global current_theme_file
  global current_theme
  global icey
  global disabled_sounds
  
  global filelock
  if current_theme_file:
    if current_theme:
      filelock.acquire(1)
      try:
        f=open(remove_utf8(str(current_theme_file)),"w")
        f.write("# Ice Sound Manager "+ism_version+" Sound Theme\n# The line below is necessary for Ice Sound Manager to identify this as a legitimate theme.\n# Include NO spaces at the end of the next 2 lines. Comments must be on their OWN line.\nTYPE=PhrozenSoundTheme\nThemeName="+remove_utf8(current_theme)+"\nstartup="+getSoundForEvent("startup",3)+"\nshutdown="+getSoundForEvent("shutdown",3)+"\nrestart="+getSoundForEvent("restart",3)+"\ncloseAll="+getSoundForEvent("closeAll",3)+"\nlaunchApp="+getSoundForEvent("launchApp",3)+"\nworkspaceChange="+getSoundForEvent("workspaceChange",3)+"\nwindowOpen="+getSoundForEvent("windowOpen",3)+"\nwindowClose="+getSoundForEvent("windowClose",3)+"\ndialogOpen="+getSoundForEvent("dialogOpen",3)+"\ndialogClose="+getSoundForEvent("dialogClose",3)+"\nwindowMin="+getSoundForEvent("windowMin",3)+"\nwindowMax="+getSoundForEvent("windowMax",3)+"\nwindowRestore="+getSoundForEvent("windowRestore",3)+"\nwindowHide="+getSoundForEvent("windowHide",3)+"\nwindowLower="+getSoundForEvent("windowLower",3)+"\nwindowRollup="+getSoundForEvent("windowRollup",3)+"\nwindowSized="+getSoundForEvent("windowSized",3)+"\nwindowMoved="+getSoundForEvent("windowMoved",3)+"\nstartMenu="+getSoundForEvent("startMenu",3)+"\n")
        for y in disabled_sounds.keys():
          f.write(str(y)+"=[DISABLED]\n")
        f.flush()
        f.close()
        icey.themetext.set_text(current_theme)
        showStatus(_("Theme")+" '"+current_theme+"' "+_("successfully saved to")+": "+current_theme_file)
      except:
        showStatus(_("ERROR while saving theme")+" '"+str(current_theme)+"' "+_("to")+"  '"+str(current_theme_file)+"'!")
      filelock.release()
     

def disableSoundEvent(sevt,refresh=1,doSave=1,doCheck=1,quiet=0,*args):
   global sound_events
   global disabled_sounds
   if sound_events.has_key(str(sevt)):
     disabled_sounds[str(sevt)]=str(sevt)
     try:
       i=setSoundForEvent(str(sevt),getSoundForEvent(str(sevt)),refresh,doSave,doCheck)
       if not quiet:
         if not i:   showSoundSetError([_("Remove")+": "+str(evt)+"    "+getSoundForEvent(str(sevt)) ])
     except:
       pass

def enableSoundEvent(sevt,*args):
   if disabled_sounds.has_key(str(sevt)):
     del disabled_sounds[str(sevt)]
     try:
       i=setSoundForEvent(str(sevt),getSoundForEvent(str(sevt)))
       if not i:   showSoundSetError([_("Link/Copy")+": "+str(sevt)+"    "+getSoundForEvent(str(sevt))])
     except:
       pass

def checkEnable(*args):
   global icey
   if icey.enablebutt.get_active():
     enableSoundEvent(getSoundEventForDesc(icey.event_entry.get_text()))
   else:
     disableSoundEvent(getSoundEventForDesc(icey.event_entry.get_text()))


def isDisabled(sevt,*args):
   global disabled_sounds
   return disabled_sounds.has_key(str(sevt))

def getSoundForEvent(sevt,fixit=0,*args):
   global sound_events
   if sound_events.has_key(str(sevt)):
     iisound=str(sound_events[str(sevt)])
     if fixit==3: 
	if iisound==_("[NONE]"): iisound="[NONE]" # ignore foreign language and save in English
     return iisound

def setSoundForEvent(sevt,sfile,refresh=1,doSave=1,doCheck=1,*args):
   global sound_events
   global wav_dir
   global copy_wavs
   global disabled_sounds
   if sound_events.has_key(str(sevt)):
     if str(sfile).strip():
       sound_events[str(sevt)]=str(sfile).strip()
       if doSave: 
         try: 
           t=Thread(None,saveThemeFile)
           t.start()
         except: 
           showStatus(_("Could not save Theme File:  Unknown thread error."))
       if not doCheck: return 1
       wavd=str(wav_dir)
       if not wavd.endswith("/") : wavd=wavd+"/"
       try:
         deregisterWav(wavd+str(sevt).strip()+".wav") # erase old file
         if disabled_sounds.has_key(str(sevt)) or str(sfile)==_("[NONE]"): 
           if refresh:  refreshServer()
           if not doCheck: return 1
           return fileExists(wavd+str(sevt).strip()+".wav")==0  #done removing/disabling
         registerWav(str(sfile).strip(),wavd+str(sevt).strip()+".wav" , copy_wavs==0)
         if refresh:  refreshServer()
         if not doCheck: return 1
         return fileExists(wavd+str(sevt).strip()+".wav")        # check to see if it's there
       except:
         pass
   return 1

def registerWav(fromFile,toFile,link=1): # put the wav on the file system
  if not fromFile: return
  if not toFile: return
  global reg_lock
  reg_lock.acquire()
  try:
    if link:
      os.popen("ln -sf "+str(fromFile).strip()+" "+str(toFile).strip())
    else: #copy
      os.popen("cp -f "+str(fromFile).strip()+" "+str(toFile).strip())
  except:
    pass
  reg_lock.release()

def deregisterWav(wavFile):
  if not wavFile: return
  global reg_lock
  reg_lock.acquire()
  try:
    os.popen("rm -f "+str(wavFile).strip()+" > /dev/null")
  except:
    pass
  reg_lock.release()


def getSoundEventForDesc(desc,*args):
   global event_desc
   if event_desc.has_key(str(desc).strip()):
     return str(event_desc[str(desc).strip()])


def showSoundEventTO(*args):
   global icey
   global last_to
   if last_to==icey.event_entry.get_text(): return 1
   last_to=icey.event_entry.get_text()
   showSoundEvent(0)
   return 1

def showSoundEvent(quiet=0,*args):
   global icey
   global wav_dir
   global sound_events
   try:
     wavd=str(wav_dir)
     if not str(wav_dir).endswith("/"): wavd=wav_dir+"/"
     icey.selsoundtext.set_text(showSoundShort( getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())))  )
     e=isDisabled(getSoundEventForDesc(icey.event_entry.get_text()))
     if e:
       icey.enablebutt.set_active(FALSE)
     else:
       icey.enablebutt.set_active(TRUE)
     i=setSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()), getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())),0,0,1)
     if not i : 
       if not quiet: 
         showSoundSetError([_("Link/Copy")+":  "+getSoundEventForDesc(icey.event_entry.get_text())+"   "+ getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()))])
   except:
     pass


def showSoundShort(csound,*args):
   csound=str(csound)
   return csound[csound.rfind("/")+1:len(csound)].strip()


def doNoSound(*args):
  global icey
  global wav_dir
  icey.selsoundtext.set_text(_("[NONE]"))
  sstat=setSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()),_("[NONE]"))
  if not sstat:
    showSoundSetError([_("Remove")+"  "+getSoundEventForDesc(icey.event_entry.get_text())+".wav  in  "+str(wav_dir) +"   "+_("FAILED")])


def changeSound(*args):
   doSoundDia()

def doSoundDia(*args):
   global sel_file
   global icey
   csound=checkFile(getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())))
   if not csound==_("[NONE]"):
     sel_file=csound
   f=showFileSelection(_("Select Wav File"),soundFile,soundCancel)


def soundFile(*args):
   global icey
   global wav_dir
   ff=grabFile()
   sstat=setSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()),checkFile(ff))
   if not sstat:
    showSoundSetError([_("Link/Copy")+"   "+ff+"  "+_("to")+"   "+getSoundEventForDesc(icey.event_entry.get_text())+".wav  "+_("in")+"  "+str(wav_dir) +"   "+_("FAILED")])
   showSoundEvent(1)

def soundCancel(*args):
  global fdir
  global icey
  csound=checkFile(getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())))
  doFsHide()
  i=setSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()),csound)
  showSoundEvent()


def checkFile(fname,*args):
  return checkExec(fname,_("[NONE]"))

def playSound(*args):
   global wav_cmd
   global wav_pid
   global icey
   if wav_cmd.strip():
     if getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())) == _("[NONE]"):
       return
     stopSound()
     pl=wav_cmd.strip().replace("%f",getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())) ).split(" ")
     if len(pl) > 1: # need at least 2 arguments
       if not wav_pid: # something already playing?
        wcmd=pl[0]
        pargs=pl[1:len(pl)+1]
        pargs.insert(0,"")
        wav_pid=os.spawnvpe(os.P_NOWAIT,wcmd,pargs,os.environ)
        showStatus(_("Playing sound")+"  '"+getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text()))+"' ...")
   else:
     showStatus(_("ERROR: No Wav player configured.  Click 'Options -> Preferences' on the menu."))

def stopSound(*args):
    global wav_pid
    try:
     if not wav_pid:
       return 
     #    changed 12.24.2003 - use common Bash shell probing
     #    to fix BUG NUMBER: 1523884
     #    Reported By: david ['-at-'] jetnet.co.uk
     #    Reported At: Fri Oct 31 23:47:12 2003
     os.popen(BASH_SHELL_EXEC+" -c \""+"kill -9 "+str(wav_pid) +" > /dev/null"+"\"")
     os.popen(BASH_SHELL_EXEC+" -c \""+"kill -9 "+str(wav_pid) +" > /dev/null"+"\"")
    except:
     pass
    wav_pid=0

def editSound(*args):
   global wav_edit
   try:
     if wav_edit.strip():
        if getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())) == _("[NONE]"):
          return
        #    changed 12.24.2003 - use common Bash shell probing
        #    to fix BUG NUMBER: 1523884
        #    Reported By: david ['-at-'] jetnet.co.uk
        #    Reported At: Fri Oct 31 23:47:12 2003
        sd=wav_edit.strip().replace("%f",getSoundForEvent(getSoundEventForDesc(icey.event_entry.get_text())))
	sd=sd.replace("&","")
        fork_process(sd)
     else:
        showStatus(_("ERROR: No Wav editor configured.  Click 'Options -> Preferences' on the menu."))
   except:
     pass

def showSoundSetError(serrors,*args):
        global wav_dir
        serr="UH OH!:\n\n"+str(len(serrors))+" "+_("error(s) occurred setting your sound events for the IceSound server.  The errors were as follows")+":\n\n"
        for si in serrors:
           serr=serr+str(si)+"\n"
        serr=serr+"\n\n"+_("These types of errors generally mean that Ice Sound Manager experienced trouble linking, copying, or removing Wav files from your selected Wav Storage Directory")+" ("+str(wav_dir)+").  "+_("Please check that the files you are linking/copying exist, that you have the proper read/write permissions for this directory and these files, AND that you have correctly configured your Wav Storage Directory in the menu under 'IceSound Server'. Also, make sure you haven't run out of disk space.")
        showModalHelp(serr)

def isTheme(ttext,*args):
  try:
     ttext.index("TYPE=PhrozenSoundTheme\n") 
     tt=ttext[ttext.index("ThemeName=")+10:len(ttext)]
     return tt[0:tt.index("\n")].strip() # return name of theme
  except: # this will throw exception of it's not a real theme
    return 0

def searchForThemes(*args):
  global current_theme_file
  try:
    tdir=extractDirectory(current_theme_file)
    l=os.listdir(tdir)
    for tfile in l:
      if tfile.lower().find("theme") > -1:
        if not os.path.isdir(tdir+tfile):
          f=open(tdir+tfile)
          ttext=f.read()
          f.close()
          tname=isTheme(ttext)
          if tname:  associateTheme(tname,tdir+tfile)
  except:
    pass

def loadTheme(fname,quiet=0,refresh=1,*args):
   global current_theme_file
   global current_theme
   global sound_events
   global icey
   serrors=[]
   if not fname: return
   try:
     f=open(fname,"r")
     th=f.read().strip()
     f.close()
     if not isTheme(th): raise TypeError
     thl=th.split("\n")
     current_theme_file=fname
     s=copy.copy(sound_events)
     for i in thl:
       tline=i.strip()
       if tline:
         if not tline.startswith("#"):
           if not tline=="TYPE=PhrozenSoundTheme":
             parts=tline.split("=")
             if parts > 1:
               propname=parts[0].strip()
               propval=parts[1].strip()
               if propname=="ThemeName":
                 current_theme=to_utf8(propval)
                 icey.themetext.set_text(current_theme)
                 showStatus(_("Loading theme")+" '"+current_theme+"'...")
               else: 
                 if propval.upper()=="[DISABLED]":
                   disableSoundEvent(propname,0,0,0,1)
                   if s.has_key(propname): del s[propname]
                 else: 
                   sstat=setSoundForEvent(propname,checkFile(_(propval)),0,0,1) # dont refresh, save, or check while loading
                   if s.has_key(propname): del s[propname]
                   if not sstat:  serrors.append(propname+"  :    "+propval)
     if len(s): # any unaccounted for sounds get set to None
       for i in s.keys():
         sstat=setSoundForEvent(i,_("[NONE]"),0,0,0)
     associateTheme(current_theme,current_theme_file)
     refreshServer()
     showSoundEvent(1) 
     if not len(serrors):
       showStatus(_("Theme")+" '"+current_theme+"' "+_("successfully loaded."))
     else:
       if not quiet:
         showSoundSetError(serrors)
   except:
     showStatus(_("ERROR loading theme from file")+" '"+fname+"'! "+_("Unknown file type."))
   icey.themetext.set_text(str(current_theme))
   return serrors

def updateThemes(*args):
   global themes
   global icey
   global current_theme
   if  len(themes):
     try: 
       l=themes.keys()
       l.sort()
       icey.themelist.set_popdown_strings(l)
       icey.themelist.show_all()
     except:
       pass
     try:
       if current_theme: icey.themetext.set_text(current_theme)
     except:
       pass

def associateTheme(tname,tfile,*args):
    global themes
    themes[str(tname)]=str(tfile)
    updateThemes()

def showThemeLoad(*args):
   doThemeLoadDia()

def doThemeLoadDia(*args):
   global sel_file
   global current_theme_file
   sel_file=current_theme_file
   f=showFileSelection(_("Select Ice Sound Manager Theme File"),lthemeFile,lthemeCancel)

def lthemeFile(*args):
   tfile=checkFile(grabFile())
   loadTheme(tfile)
   updateThemes()


def lthemeCancel(*args):
   doFsHide()

def selectTheme(*args):
    global icey
    global themes
    t=icey.themetext.get_text()
    if not t==_("[NONE]"):
      if themes.has_key(t):
        loadTheme(themes[t],0,1)
    return TRUE

  

# Audio Interface

class iceaudio :
    def __init__ (self) :
	iceaudio = Window(WINDOW_TOPLEVEL)
	self._root = iceaudio
	iceaudio.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(iceaudio)
	iceaudio.set_data("ignore_return",1)
	iceaudio.connect("key-press-event",keyPressClose)
	iceaudio.set_title (_("Ice Sound Manager: Audio Interface"))
	iceaudio.set_position ( WIN_POS_CENTER)
	iceaudio.set_modal ( 1)
        iceaudio.realize()
        tips=TIPS
	self.iceaudio = iceaudio
	frame1 = VBox(0,0)
	self.frame1 = frame1
	table1 = Table (7, 3, 0)
	table1.set_row_spacings (3)
	table1.set_col_spacings ( 26)
	table1.set_border_width ( 3)
	self.table1 = table1
	oss = RadioButton (None,"OSS")
        oss.connect("clicked",doAudioToggle,1)
	tips.set_tip (oss, _("Select to use the OSS audio interface"))
	self.oss = oss
	table1.attach(oss, 0, 1, 0, 1, (EXPAND+FILL), (0), 0, 0)
	esd = RadioButton (self.oss, "ESD")
	tips.set_tip (esd, _("Select to use the ESD audio interface"))
        esd.connect("clicked",doAudioToggle,2)
	self.esd = esd
	table1.attach(esd, 1, 2, 0, 1, (EXPAND+FILL), (0), 0, 0)
	yiff =RadioButton (self.oss, "YIFF")
	tips.set_tip (yiff, _("Select to use the YIFF audio interface"))
        yiff.connect("clicked",doAudioToggle,3)
	self.yiff = yiff
	table1.attach(yiff, 2, 3, 0, 1, (EXPAND+FILL), (0), 0, 0)
	label1 = Label (_("Device"))
	label1.set_alignment ( 0, 0.5)
	self.label1 = label1
	table1.attach(label1, 0, 1, 1, 2, (FILL), (0), 0, 0)
	label2 = Label (_("Host"))
	label2.set_alignment ( 0, 0.5)
	self.label2 = label2
	table1.attach(label2, 1, 2, 1, 2, (FILL), (0), 0, 0)
	label3 = Label (_("Host"))
	label3.set_alignment ( 0, 0.5)
	self.label3 = label3
	table1.attach(label3, 2, 3, 1, 2, (FILL), (0), 0, 0)
	devtext = Entry ()
	tips.set_tip (devtext, _("Enter the Digital Signal Processing  DSP  to use"))
	self.devtext = devtext
	table1.attach(devtext, 0, 1, 2, 3, (EXPAND+FILL), (0), 0, 0)
	host1text = Entry ()
	tips.set_tip (host1text, _("Enter the host of the ESD server"))
	self.host1text = host1text
	table1.attach(host1text, 1, 2, 2, 3, (EXPAND+FILL), (0), 0, 0)
	host2text = Entry ()
	tips.set_tip (host2text, _("Enter the host of the YIFF server"))
	self.host2text = host2text
	table1.attach(host2text, 2, 3, 2, 3, (EXPAND+FILL), (0), 0, 0)
	label4 = Label (_("Port"))
	label4.set_alignment ( 0, 0.5)
	self.label4 = label4
	table1.attach(label4, 1, 2, 3, 4, (FILL), (0), 0, 0)
	label5 = Label (_("Port"))
	label5.set_alignment ( 0, 0.5)
	self.label5 = label5
	table1.attach(label5, 2, 3, 3, 4, (FILL), (0), 0, 0)
	port1text = Entry ()
	tips.set_tip (port1text, _("Enter the port number of the ESD server"))
	self.port1text = port1text
	table1.attach(port1text, 1, 2, 4, 5, (EXPAND+FILL), (0), 0, 0)

	localcheck = CheckButton(_("Local Interface"))
	tips.set_tip (localcheck, _("If checked  the local (non-TCP) ESD server will be used. The 'Host' and 'Port' will be ignored, since it is not needed if this option is checked."))
	self.localcheck = localcheck
	table1.attach(localcheck, 1, 2, 5, 6, (FILL), (0), 0, 0)

	port2text = Entry ()
	tips.set_tip (port2text, _("Enter the port number of the YIFF server"))
	self.port2text = port2text
	table1.attach(port2text, 2, 3, 4, 5, (EXPAND+FILL), (0), 0, 0)
	autocheck = CheckButton(_("Auto Audio Mode"))
	tips.set_tip (autocheck, _("If checked  the YIFF server will attempt to automatically adjust to the correct audio mode"))
	self.autocheck = autocheck
	table1.attach(autocheck, 2, 3, 5, 6, (FILL), (0), 0, 0)
	helpbutton = getPixmapButton(iceaudio,STOCK_DIALOG_INFO,_("Help"))
        helpbutton.connect("clicked",showAudioHelp)
	tips.set_tip (helpbutton, _("Click for help on the audio interface options"))
	self.helpbutton = helpbutton
	table1.attach(helpbutton, 0, 1, 6, 7, (FILL), (0), 0, 3)
	label7 = Label ("  ")
	label7.set_alignment ( 0, 0.5)
	self.label7 = label7
	table1.attach(label7, 0, 1, 3, 4, (FILL), (0), 0, 0)
	label8 = Label ("  ")
	label8.set_alignment ( 0, 0.5)
	self.label8 = label8
	table1.attach(label8, 0, 1, 4, 5, (FILL), (0), 0, 0)
	label9 = Label ("  ")
	label9.set_alignment ( 0, 0.5)
	self.label9 = label9
	table1.attach(label9, 0, 1, 5, 6, (FILL), (0), 0, 0)

	okbutton = getPixmapButton(iceaudio, STOCK_APPLY ,_("OK"))
        okbutton.connect("clicked",closeAudio)
	tips.set_tip (okbutton, _("Save changes and close this window"))
	self.okbutton = okbutton
	table1.attach(okbutton, 1, 2, 6, 7, (FILL), (0), 0, 3)
	label11 = Label ("  ")
	label11.set_alignment ( 0, 0.5)
	self.label11 = label11
	table1.attach(label11, 2, 3, 6, 7, (FILL), (0), 0, 0)
	frame1.pack_start(table1,1,1,0)
	frame1.set_border_width(4)
	iceaudio.add(frame1)

def showAudio(*args):
   global icea
   global audio_defaults
   icea=iceaudio()
   setAudioDefaults()
   doAudioToggle()
   icea.iceaudio.show_all()

def closeAudio(*args):
    global icea
    global audio_defaults
    try:
      string.atoi(icea.port2text.get_text().strip())
      string.atoi(icea.port1text.get_text().strip())
    except:
      showStatus(_("ERROR!   The port number must be an INTEGER!"))
      return
    setAudioProp("yiff_port",icea.port2text.get_text())
    setAudioProp("yiff_host",icea.host2text.get_text())
    setAudioProp("esd_port",icea.port1text.get_text())
    setAudioProp("esd_host",icea.host1text.get_text())
    setAudioProp("oss_dev",icea.devtext.get_text())
    setAudioProp("esd_local",str(int(icea.localcheck.get_active())))
    setAudioProp("yiff_auto",str(int(icea.autocheck.get_active())))
    if icea.esd.get_active():
      setAudioProp("interface","esd")
    if icea.oss.get_active():
      setAudioProp("interface","oss")
    if icea.yiff.get_active():
      setAudioProp("interface","yiff")
    icea.iceaudio.hide()
    icea.iceaudio.destroy()
    saveOptions()
    return TRUE

def saveAudioOptions(*args):
   global audio_defaults
   global audio_file
   
   if audio_file:
     try:
       f=open(audio_file,"w")
       f.write("")
       f.write("# Ice Sound Manager "+ism_version+" audio interface preferences\n# DO NOT EDIT!\n")
       for i in audio_defaults.keys():
         f.write(str(i).strip().lower()+"="+str(audio_defaults[i]).strip().lower()+"\n")
       f.flush()
       f.close()
       showStatus(_("Audio interface options successfully saved."))
     except:
       showStatus(_("ERROR:  While saving audio interface preferences to")+" '"+str(audio_file)+"'!")

def loadAudioOptions(*args):
   global audio_defaults
   global audio_file
   if audio_file:
     try:
       f=open(audio_file,"r")
       atext=f.read()
       f.close()
       alist=atext.split("\n")
       for i in alist:
         aline=i.strip()
         if not aline.startswith("#"):
            if aline.find("=") > -1:
              apair=aline.split("=")
              if len(apair) > 1:
                setAudioProp(apair[0],apair[1])
     except:
       pass

def showAudioHelp(*args):
    showModalHelp(_("Here is where you can configure the sound device you want your IceSound Server to use to play your sound events.  Most people will probably use either ESD or OSS.  It is YOUR job to know what kind of sound device your system uses. \n\nOSS:\nFor OSS, click 'OSS' and type in the 'dev' location of your digital signal processing device (i.e. /dev/dsp)\n\nESD:\nFor ESD, click 'ESD' and enter the host and port of the ESD sound server running on your system.  For most people, this will be host 'localhost' and port '16001'.  You can find out what port ESD is running on your system by typing 'netstat -lp' in a terminal window, then looking for any process named 'esound' or 'esd'.  If you dont see either of these, you probably don't have a currently running ESD sound server on your system and will not be able to use ESD as your interface until you get an ESD server running.\n\nYIFF:  If you know that you need to use YIFF, please make sure that your copy of the IceSound Server has been compiled with YIFF support (not all copies are YIFF-enabled.).  To use the YIFF interface, click 'YIFF', then enter the host and port of your YIFF sound server.  You may also check 'Auto Audio Mode' to enable your IceSound Server to automatically choose the best sampling rate and playback mode for your sounds. "))

def setAudioProp(propname,propval):
   global audio_defaults
   if audio_defaults.has_key(str(propname).strip().lower()):
     if str(propval).strip():
       audio_defaults[str(propname).strip().lower()]=str(propval).strip().lower()

def doAudioToggle(*args):
    global icea
    if icea.yiff.get_active():
      icea.autocheck.set_sensitive(1)
      icea.localcheck.set_sensitive(0)
      icea.host2text.set_editable(1)
      icea.port2text.set_editable(1)
      icea.host1text.set_editable(0)
      icea.port1text.set_editable(0)
      icea.devtext.set_editable(0)
    if icea.oss.get_active():
      icea.devtext.set_editable(1)
      icea.host2text.set_editable(0)
      icea.port2text.set_editable(0)
      icea.autocheck.set_sensitive(0)
      icea.localcheck.set_sensitive(0)
      icea.host1text.set_editable(0)
      icea.port1text.set_editable(0)
    if icea.esd.get_active():
      icea.host1text.set_editable(1)
      icea.port1text.set_editable(1)
      icea.devtext.set_editable(0)
      icea.host2text.set_editable(0)
      icea.port2text.set_editable(0)
      icea.autocheck.set_sensitive(0)
      icea.localcheck.set_sensitive(1)

def setAudioDefaults(*args):
   global icea
   global audio_defaults
   icea.esd.set_active(1)
   icea.oss.set_active(str(audio_defaults["interface"])=="oss")
   icea.yiff.set_active(str(audio_defaults["interface"])=="yiff")
   icea.host2text.set_text(audio_defaults["yiff_host"])
   icea.port2text.set_text(audio_defaults["yiff_port"])
   icea.autocheck.set_active(str(audio_defaults["yiff_auto"])=="1")
   icea.localcheck.set_active(str(audio_defaults["esd_local"])=="1")
   icea.devtext.set_text(audio_defaults["oss_dev"])
   icea.host1text.set_text(audio_defaults["esd_host"])
   icea.port1text.set_text(audio_defaults["esd_port"])
   

def fileExists(fname, *args):
  try:
     return os.path.exists(str(fname).strip())
  except:
     return 0

# SETUP 

class icesetup :
    def __init__ (self) :
	icesetup = Window (WINDOW_TOPLEVEL)
	self._root = icesetup
	icesetup.set_wmclass("icesoundmanager","IceSoundManager")
	set_basic_window_icon(icesetup)
	icesetup.set_data("ignore_return",1)
	icesetup.connect("key-press-event",keyPressClose)
	icesetup.set_title ( _("Ice Sound Manager Setup"))
	icesetup.set_position ( WIN_POS_CENTER)
        icesetup.set_size_request(450,400)
        icesetup.realize()
        tips = TIPS
	self.icesetup = icesetup
	vbox1 = VBox (0, 0)
	vbox1.set_border_width ( 11)
	self.vbox1 = vbox1
	vbox1.pack_start ( getImage(getPixDir()+"ism_header.png",_("Ice Sound Manager")), 1, 1, 2)
	vbox1.pack_start ( getImage(getPixDir()+"ism_setup.png",_("SETUP")), 1, 1, 2)
        spacer=Label("  ")
	vbox1.pack_start ( spacer, 1, 1, 3)         
	scrolledwindow1 = ScrolledWindow ()
	self.scrolledwindow1 = scrolledwindow1
        scrolledwindow1.set_size_request(430,250)
	helptext =TextView ()
	helptext.set_editable ( 0)
        helptext.set_wrap_mode(WRAP_WORD)
	self.helptext = helptext
	scrolledwindow1.add ( helptext)
	vbox1.pack_start ( scrolledwindow1, 1, 1, 0)
	closebutt = getPixmapButton(icesetup, STOCK_GO_FORWARD ,_("Next"))
        closebutt.connect("clicked",returnSetup)
	tips.set_tip (closebutt, _("Proceed with Setup"))
	self.closebutt = closebutt
	vbox1.pack_start ( closebutt, 0, 0, 13)
	icesetup.add (vbox1)
        self.setHelpText(_("WELCOME TO ICE SOUND MANAGER SETUP\n\nSetup will guide you through setting up your IceSound Server (the sound server for IceWM) as well as help you easily customize your settings in 4 easy steps. You may run this setup program at anytime by clicking 'Options', then 'Setup' on the menu.  Note: You will also see this setup window if Ice Sound Manager was unable to load your preferences files in your home directory. \n\nSTEP ONE:  Select the executable for your IceSound Server.   Click the 'Next' button to proceed."))

    def setHelpText(self, helpstuff):
	hbuf=self.helptext.get_buffer()
	hbuf.set_text("")
	text_buffer_insert(hbuf,  get_renderable_tab(hbuf, 
		HELP_FONT2,COL_BLACK,LANGCODE), str(helpstuff) )	


def runSetup(*args):
  global isetup
  global exec_run
  global audio_run
  global wav_run
  global pref_run
  exec_run=0
  audio_run=0
  wav_run=0
  pref_run=0
  isetup=icesetup()
  isetup.icesetup.set_modal(1)
  isetup.icesetup.show_all()

def returnSetup(*args):
  global isetup
  global exec_run
  global audio_run
  global wav_run
  global pref_run
  
  if not exec_run: 
    askExec()
    exec_run=1
    isetup.setHelpText(_("STEP TWO:  Configure the audio device your IceSound Server will use to play sound events.  Most people can probably use the ESD interface on localhost, port 16001.\n\nClick the 'Next' button to proceed."))
    return
  if not audio_run: 
    showAudio()
    audio_run=1
    isetup.setHelpText(_("STEP THREE:  Select the directory where your IceSound Server should look for the .wav files for sound events.  Normally, this directory is either ~/.icewm/sounds/ or /usr/X11R6/lib/X11/icewm/sounds/, but you should check the documentation for YOUR IceSound Server.   If you are unsure, your best bet is probably choosing the directory /home/yourUsername/.icewm/sounds/.  This may take a moment: So be patient.\n\nClick the 'Next' button to proceed."))
    return
  if not wav_run: 
    askWavDir()
    wav_run=1
    isetup.setHelpText(_("STEP FOUR:  This is the LAST step.  You can now configure your personal preferences for Ice Sound Manager")+" "+ism_version+".\n\n"+_("Click the 'Next' button to proceed."))
    return
  if not pref_run: 
    showOptions()
    pref_run=1
    isetup.setHelpText(_("Setup for Ice Sound Manager is now COMPLETE.  Click the 'Next' button to exit setup.  Enjoy!"))
    return
  isetup.icesetup.hide()
  isetup.icesetup.destroy()
  isetup=None
  return TRUE

#  MAIN methods

def setupFiles(*args):
  global audio_file
  global pref_file
  global xterm
  if os.environ.has_key("HOME"):
    audio_file=os.path.join(str(os.environ["HOME"]),".IceSoundManagerAudioRC")
    pref_file=os.path.join(str(os.environ["HOME"]),".IceSoundManagerRC")
  if os.environ.has_key("TERM"):
    if str(os.environ["TERM"]).strip():
      xterm=str(os.environ["TERM"])


def savePreferences(*args):
   global pref_file
   
   global wav_cmd
   global wav_edit
   global use_terminal
   global copy_wavs
   global start_server
   global server_exec
   global wav_dir
   global current_theme_file
   global icey
   if pref_file:
      try:
        f=open(pref_file,"w")
        f.write("# Ice Sound Manager "+ism_version+" preferences file\n# DO NOT EDIT!\n")
        f.write("current_theme_file="+str(current_theme_file)+"\nserver_exec="+str(server_exec)+"\nstart_server="+str(start_server)+"\ncopy_wavs="+str(copy_wavs)+"\nuse_terminal="+str(use_terminal)+"\nwav_edit="+str(wav_edit)+"\nwav_cmd="+str(wav_cmd)+"\nwav_dir="+str(wav_dir))
        f.flush()
        f.close()
        showStatus(_("Preferences successfully saved."))
      except:
        showStatus(_("ERROR:  While saving preferences to")+" '"+str(pref_file)+"'!")
   icey.entry2.set_text(getSuggestedCommandLine())

def loadPreferences(*args):
   global pref_file
   global wav_cmd
   global wav_edit
   global use_terminal
   global copy_wavs
   global start_server
   global server_exec
   global wav_dir
   global current_theme_file
   global need_setup
   global sel_file
   try:
     f=open(pref_file,"r")
     ptext=f.read()
     f.close()
     plist=ptext.split("\n")
     for i in plist:
        pline=i.strip()
        if not pline.startswith("#"):
          if pline.find("=") > -1:
            ppair=pline.split("=")
            if len(ppair) > 1:
              propname=ppair[0].strip().lower()
              propval=ppair[1].strip()
              if propval: #ignore blank values
                if propname=="server_exec": server_exec=propval
                if propname=="wav_cmd": wav_cmd=propval
                if propname=="wav_edit": wav_edit=propval
                if propname=="current_theme_file": current_theme_file=propval
                if propname=="wav_dir": wav_dir=propval
                if propname=="start_server": start_server=(propval=="1")
                if propname=="copy_wavs": copy_wavs=(propval=="1")
                if propname=="use_terminal": use_terminal=(propval=="1")
     if str(current_theme_file).find("/") > -1:  sel_file=extractDirectory(str(current_theme_file))
     if start_server:
       if not serverIsRunning():  startServer()
   except:
     need_setup=1 # Couldn't load preferences - run setup

def loadOptions(*args):
  loadAudioOptions()
  loadPreferences() 

def saveOptions(*args):
   global filelock2
   filelock2.acquire()
   try:
     saveAudioOptions()
   except:
     pass
   try:
     savePreferences()
   except:
     pass
   filelock2.release()

def startServer(*args):
  global xterm
  global server_exec
  global wav_dir
  global use_terminal
  global server_version

  if not xterm:  xterm="xterm"
  if xterm.lower().find("term") == -1: xterm="xterm" # the $TERM envir. variable was showing up as 'linux' when ISM not launched from a console

  #xterm="gnome-terminal"     # Uncomment and EDIT this line if you want to force the use of something other than your DEFAULT terminal in $TERM

  if not server_exec:       
    showStatus(_("ERROR: No IceSound SERVER EXECUTABLE selected!  Click 'IceSound Server' on the menu."))
    return 
  if not wav_dir:       
    showStatus(_("ERROR: No IceSound server WAV DIRECTORY selected!  Click 'IceSound Server' on the menu."))
    return
  if not stopServer():
    showStatus(_("ERROR: Your IceSound server could not be (re)started because it could not be STOPPED!"))
    return
  if use_terminal:
    if xterm.lower()=="gnome-terminal": 
      f=os.popen(xterm+" -x "+getSuggestedCommandLine())
    else:  # for any other terminals that accept the -e command, i.e. xterm, etc.
      f=os.popen(xterm+" -e "+getSuggestedCommandLine())
  else:
    #    changed 12.24.2003 - use common Bash shell probing
    #    to fix BUG NUMBER: 1523884
    #    Reported By: david ['-at-'] jetnet.co.uk
    #    Reported At: Fri Oct 31 23:47:12 2003
    f=os.popen(BASH_SHELL_EXEC+" -c \""+getSuggestedCommandLine()+" &> /dev/null"+"\"")
  try:
    time.sleep(3)
    if serverIsRunning():
      showStatus(_("IceSound Server (version")+" "+server_version+") "+_("successfully (RE)STARTED."))
    else:
      showStatus(_("ERROR!  IceSound server could NOT be (re)started!  Check 'Options' and 'IceSound Server' on the menu."))
  except:
    pass

def clearESDCache(*args):
	samp_names=[]
	f=os.popen("esdctl allinfo")
	fl=f.readlines()
	f.close()
	for ii in fl:
		if ii.find("icesound")>-1:
			if ii.find("=")< ii.find("icesound"):
				samp_names.append(ii[ii.find("=")+1:len(ii)].strip())
	for ii in samp_names:
		f=os.popen("esdctl free "+ii)
		f.readlines()

def stopServer(*args):
   global server_version
   global audio_defaults
   try:
     #    changed 12.24.2003 - use common Bash shell probing
     #    to fix BUG NUMBER: 1523884
     #    Reported By: david ['-at-'] jetnet.co.uk
     #    Reported At: Fri Oct 31 23:47:12 2003
     f=os.popen(BASH_SHELL_EXEC+" -c \""+"killall -q -9 "+getServerExecShort() +" &> /dev/null"+"\"")
     f=os.popen(BASH_SHELL_EXEC+" -c \""+"killall -q -9 "+getServerExecShort() +" &> /dev/null"+"\"")
     f=os.popen(BASH_SHELL_EXEC+" -c \""+"killall -q -9 "+getServerExecShort() +" &> /dev/null"+"\"")
     #if we are using the ESD interface, we need to clear the 'icesound' samples from ESD's server cache
     iface=str(audio_defaults["interface"]).lower()
     if iface=="esd":
	clearESDCache()
     s=serverIsRunning()
     if not s: showStatus(_("IceSound Server (version")+" "+server_version+") "+_("successfully STOPPED.  Future sound events disabled until server re-start."))
     return s==0
   except:
     return 1

def applySoundTheme(*args):
	selectTheme() 
	startServer()

def serverIsRunning(*args):
   try:
     # changed 8.25.2003, use 'common' lib for checking for process id	
     i=get_pidof(getServerExecShort())
     if not i: return 0
     if i[0].isdigit(): 
       return 1
     else:
       return 0
   except:
     return 0
   return 0

def getServerVersion(*args):
   global server_version
   server_version=_("unknown")
   try:
     f=os.popen(getServerExec() + " -V")
     i=f.readline()
     f.close()
     if not i: return
     if i[0].isdigit(): 
       server_version=str(i).strip()
   except:
     pass
  
def refreshServer(*args):
   try:
     #    changed 12.24.2003 - use common Bash shell probing
     #    to fix BUG NUMBER: 1523884
     #    Reported By: david ['-at-'] jetnet.co.uk
     #    Reported At: Fri Oct 31 23:47:12 2003
     f=os.popen(BASH_SHELL_EXEC+" -c \""+"killall -HUP "+getServerExecShort()+"\"")
   except:
     pass

###  HELP FILE #### # new in version 1.1, now read in from the text file
# 4/26/2003 - disabled, main help is now displayed through the centralized 'Help' system of icewmcp_common.py
"""
help_file=_("SPANISH HELP IS AVAILABLE IN THE 'icesound-es-help.html'  FILE.")+" ("+os.path.abspath(getDocDir())+")\n\n\n"
try:
	fhelp=open(getDocDir()+"IceSoundManager_Help.txt")
	help_en=fhelp.read()
	fhelp.close()
except:
	help_en="Error: Could not open help document: '"+os.path.abspath(getDocDir())+"IceSoundManager_Help.txt'"
help_file=help_file+help_en
"""


### MAIN METHODS ####
def quit (*args) :
    saveOptions()
    gtk.mainquit ()

def run () :
    global icemain
    global icey
    w=icewindow ()
    icey=w
    icemain=w.icewindow
    w.icewindow.connect("destroy", quit)
    icemain.show_all() 
    hideSplash()
    gtk.mainloop ()

def t_start():    
    t=Thread(None,run)
    t.start()

if __name__ == "__main__" :
	t_start()
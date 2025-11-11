# -*- coding: ISO-8859-1 -*-

#############################
#  IceWM Control Panel
#  Bug Report Module
#  
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  This program is distributed free
#  of charge (open source) under the 
#  GNU General Public License
#############################
#       Bug Report Module
#
#       Added in version 2.0: Allows users to email
#       bug reports from within most IceWMCP 
#       programs, while collecting all useful
#       system information needed for bug-fixes,
#       such as relevant software versions that
#       users almost always forget to include in
#       their emails.  This will speed up bug-fixes
#       and help eliminate time wasted trying to 
#       fix 'bugs' when the user is using old or 
#       unsupported software libraries.
#
#       This bug report module does not provide
#       support of SMTP mail servers that 
#       require authentication or require 
#       'pop-before-smtp': The user is on their
#       own if they use such a mail server.
#############################
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


import smtplib,random,time,os,sys,string

BUG_REPORT_ADDRESS="PhrozenSmoke [at] yahoo.com"   # who to send bug reports to
DEFAULT_SMTP_PORT="25"


from .icewmcp_common import getImage, getBaseDir, msg_err, msg_info, checkSoftUpdate 
from .icewmcp_common import msg_confirm,app_map, this_software_version, keyPressClose
from .icewmcp_common import TIPS, IS_STATIC_BINARY, GTK, GDK, translateCP, getPixmapButton
from .icewmcp_common import to_utf8 , set_basic_window_icon , STOCK_GO_FORWARD

from gtk import *

def _(somestr):
	return to_utf8(translateCP(somestr))

BUG_REPORT_SUBJECT="IceWMCP BUG-REPORT: v. "+this_software_version  # e-mail Subject line

def sendEmail(msgtext,sserver,from_addie):
        do_fail=0
        if len(str(sserver).strip())==0:
                msg_err(_("Bug Report"),_("You did not specify a valid SMTP host."))            
                return 0
        bad_mail=0
        from_parts=from_addie.strip().split("@")
        if not len(from_parts)==2:  bad_mail=1  # no '@' was found
        else:
                if (len(from_parts[0])<2) or (from_parts[0].find(" ")>-1): bad_mail=1
                if (len(from_parts[1])<2) or (from_parts[1].find(" ")>-1): bad_mail=1
                if (from_parts[1].find(".")==-1) or (from_parts[1].startswith(".")) or  (from_parts[1].endswith(".")): bad_mail=1
        if bad_mail==1:
                msg_err(_("Bug Report"),_("The FROM e-mail address you provided is invalid."))          
                return 0
        try:
                smtpserver=smtplib.SMTP(str(sserver).strip(),DEFAULT_SMTP_PORT)
        except:
                smtpserver=None
        if not smtpserver:
                msg_err(_("Bug Report"),_("Unable to connect to SMTP server")+":\n\nHost: "+str(sserver).strip()+"\nPort: "+DEFAULT_SMTP_PORT)
                return 0
        try:
                smtpserver.sendmail(str(from_addie).strip(),
			BUG_REPORT_ADDRESS.replace(" [at] ","@"),str(msgtext))
        except:
                do_fail=1
        try:
                smtpserver.rset()
        except:
                pass
        try:
                smtpserver.quit()
        except:
                pass
        if do_fail==1:
                msg_err(_("Bug Report"),_("Unable to send your bug report message")+"\n\n"+_("Your SMTP server may require a password or may require you to check your POP3 mail first.")+"\n\n"+_("Be sure that you are connected to the internet."))
                return 0  
        msg_info(_("Bug Report"),_("Your bug report message was successfully sent to")+":\n\n"+BUG_REPORT_ADDRESS.replace(" [at] ","@"))
        return 1

def getSysInfo(*args): # gather useful system information for bug-reporting, info users always fail to send
        sys_info="DATE :  "+time.ctime()+"\n\nSTATIC BINARY :   "+str(IS_STATIC_BINARY)+"\n\n"

        os_v=['USER','OSTYPE','MACHTYPE', 'CPU', 'LANG','LANGUAGE','LOCALE', 'SHELL', 'TERM']
        # explanation:  USER - username, some apps require 'root' access, 
        #  OSTYPE - Linux, BSD, etc. ,   LANG/LANGUAGE = language 'locale' for gettext/locale problems,
        # MACHTYPE -  machine type

        for ii in os_v:
                try:
                        sys_info=sys_info+ii+" :  "+os.environ[ii]+"\n"
                except:
                        pass
        sys_info=sys_info+"CURRENT WORKING DIRECTORY : "+str(os.getcwd())+"\n"
        sys_info=sys_info+"UNAME : "+str(os.uname()).replace(",","  /  ")+"\n\n"
        # We need to know the versions of the various libraries IceWMCP relies upon, we don't want to try 
        # to make bug fixes if people are using unsupported/very old versions
        sys_info=sys_info+"IceWM Control Panel Version :  "+this_software_version +"\n"
        sys_info=sys_info+"SCREEN RESOLUTION : "+str(GDK.screen_width())+" x "+ str(GDK.screen_height())+"\n"
        sys_info=sys_info+"PYTHON VERSION : "+sys.version.replace("\n","  ")+"\n"
        sys_info=sys_info+"GTK VERSION : "+str(gtk_version).replace(",",".").replace(" ","")+"\n"
        sys_info=sys_info+"PYGTK VERSION : "+str(pygtk_version).replace(",",".").replace(" ","")+"\n"
        sys_info=sys_info+"IMLIB VERSION : "+str(os.popen("imlib-config --version").readline()) +"\n"
        sys_info=sys_info+"Gdk-PIXBUF VERSION : "+str(os.popen("gdk-pixbuf-config --version").readline()) +"\n\n"
        
        # finally, we need to know the versions of IceWM and IceSound on this computer, so that we 
        # aren't trying to fix bugs in very old, unsupported versions of IceWM
        sys_info=sys_info+"ICEWM VERSION : "+str(os.popen("icewm --version").readline()) +"\n"
        sys_info=sys_info+"ICEWM-GNOME VERSION : "+str(os.popen("icewm-gnome --version").readline()) +"\n"
        sys_info=sys_info+"ICESOUND VERSION : "+str(os.popen("icesound --version").readline()) +"\n"
        sys_info=sys_info+"ICESOUND-GNOME VERSION : "+str(os.popen("icesound-gnome --version").readline()) +"\n"

        return sys_info

def sendBugReport(*args):
        sctext=args[0].get_data("bugform")
	sctextbuf=sctext.get_buffer()
	bugform=sctextbuf.get_text(sctextbuf.get_start_iter(),sctextbuf.get_end_iter())
        if len(bugform)< 101:  
                # don't accept bug reports less than 100 characters, such as "it doesn't work!"
                # It's a waste of time to send bug reports less than a couple sentences in length

                msg_err(_("Bug Report"),_("You did not describe the bug or problem IN DETAIL in the 'bug report' area.")+"\n\n"+_("There is not enough information to send a bug report."))
                return
        window=args[0].get_data("window")
        fromadd=args[0].get_data("from").get_text().strip()
        sserver=args[0].get_data("server").get_text().strip()
        sysinfo=getSysInfo()
        appname=args[0].get_data("appname")
        mailmessage="Return-Path: <"+fromadd+">\nFrom:"+fromadd+"\nSubject: "+BUG_REPORT_SUBJECT+"\nMIME-Version: 1.0\nX-Mailer: IceWMCP Bug Tracker "+this_software_version+"\nContent-Type: text/plain; charset=iso-8859-1\nContent-Transfer-Encoding: 8bit\nSender: "+fromadd+"\nX-Priority: 3\nX-MSMail-Priority: Normal\n\n"
        mailmessage=mailmessage+"\n____________________\n  BUG REPORT FOR "+appname+" \n____________________\n\n\n"+bugform+"\n\n\n____________________\n  SYSTEM INFORMATION\n____________________\n\n"+sysinfo+"\n____________________\n\nBUG NUMBER: "+str(random.randrange(9000))+str(random.randrange(900))+"\n\n"

        if sendEmail(mailmessage,sserver,fromadd)==1:
                window.hide()
                window.destroy()
                window.unmap()



def file_bug_report(app_num=5000,*args):
        if app_num not in app_map:
                msg_err(_("Bug Report"),_("Unknown application"))  # we called an un-mapped application number
                return
        app_name=app_map[app_num][0]
        #print "app_name:   "+app_name    # for testing

        # make sure user has newest version before reporting a bug
        # no sense in handling bug reports of outdated versions of the software
        if not msg_confirm(_("Bug Report"),string.join([_("Before reporting a bug, please make sure you have the NEWEST version of this software."),"",_("Please do not submit bug reports if you are using an older version of this software."),_("If you are using an older version of this software, first upgrade to the NEWEST version."),"",_("Send your bug report ONLY if you continue to have the same problem with the NEWEST version of this software."),"",_("A check for the NEWEST version of this software will now be conducted."),"",_("Do you wish to continue?")] , "\n")  )==1:  
                return  
        bugwin=Window(GTK.WINDOW_TOPLEVEL)
	set_basic_window_icon(bugwin)
        bugwin.set_wmclass("icewmcontrolpanel","IceWMControlPanel")
        bugwin.realize()
        bugwin.set_title("IceWMCP: "+_("Bug Report"))
        bugwin.set_position(GTK.WIN_POS_CENTER)
        mainvbox=VBox(0,1)
        mainvbox.set_spacing(3)
        mainvbox.set_border_width(5)
        p=getImage(getBaseDir()+"icewmcp_short.png","IceWMCP")
        if not p: p=Label(wintitle)
        mainvbox.pack_start(p,0,0,0)
        mainvbox.pack_start(Label(_("Bug Report")),0,0,2)
        mainvbox.pack_start(HSeparator(),0,0,2)
        table1 = Table (3, 2, 0)
        table1.set_col_spacings (8)
        table1.set_row_spacings (2)
        table1.set_border_width (4)
        table1.attach(Label(_("To")+":"), 0, 1, 0, 1, (GTK.FILL), (0), 0, 0)
        table1.attach(Label(_("From")+":"), 0, 1, 1, 2, (GTK.FILL), (0), 0, 0)
        table1.attach(Label(_("SMTP Server")+":"), 0, 1, 2, 3, (GTK.FILL), (0), 0, 0)
        table1.attach(Label("<"+BUG_REPORT_ADDRESS.replace(" [at] ","@")+">"), 1, 2, 0, 1, (GTK.EXPAND+GTK.FILL), (0), 0, 0)
        sserver=Entry()
        sfrom=Entry()
        table1.attach(sfrom, 1, 2, 1, 2, (GTK.EXPAND+GTK.FILL), (0), 0, 0)
        table1.attach(sserver, 1, 2, 2, 3, (GTK.EXPAND+GTK.FILL), (0), 0, 0)
        try:
                sserver.set_text(os.environ['HOSTNAME'])
        except:
                sserver.set_text("localhost")   
        mainvbox.pack_start(table1,0,0,4)
        mainvbox.pack_start(Label(_("Please describe the bug or problem in detail")+":"),0,0,4)
        sc=ScrolledWindow()
        sctext=TextView()
        sctext.set_editable(TRUE)
        sctext.set_wrap_mode(WRAP_WORD)
        #sctext.get_buffer().set_text(app_name)   # for testing
        sc.add(sctext)
        mainvbox.pack_start(sc,1,1,0)
        mainvbox.pack_start(Label(_("The following system information will be sent with your bug report")+":"),0,0,6)
        sc1=ScrolledWindow()
        sctext1=TextView()
        sctext1.set_editable(0)
        sctext1.get_buffer().set_text(getSysInfo())
        sctext1.set_wrap_mode(WRAP_WORD)
        sc1.add(sctext1)
        mainvbox.pack_start(sc1,1,1,0)
        sendbutt=getPixmapButton(None, STOCK_GO_FORWARD ,_("SEND NOW"))
        TIPS.set_tip(sendbutt,_("SEND NOW"))
        sendbutt.set_data("window",bugwin)
        sendbutt.set_data("from",sfrom)
        sendbutt.set_data("server",sserver)
        sendbutt.set_data("bugform",sctext)
        sendbutt.set_data("sysinfo",sctext1)
        sendbutt.set_data("appname",str(app_name))
        sendbutt.connect("clicked",sendBugReport)
        mainvbox.pack_start(sendbutt,0,0,9)
        bugwin.add(mainvbox)
        bugwin.set_default_size(395,460)
        bugwin.set_data("ignore_return",1)  # don't close the window on 'Return' key press, just 'Esc'
        bugwin.connect("key-press-event", keyPressClose)
        bugwin.show_all()
        checkSoftUpdate()







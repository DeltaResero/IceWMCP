# -*- coding: ISO-8859-1 -*-

#############################################
#  PySpool, PyPrint-Common Library
#
#  Copyright (c) 2003-2004
#  Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
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

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateCP(somestr))  # from icewmcp_common.py

global PYPRINT_VERSION
PYPRINT_VERSION="0.3.1"

def launch(launch_command):
	#    changed 12.24.2003 - use common Bash shell probing
	#    to fix BUG NUMBER: 1523884
	#    Reported By: david ['-at-'] jetnet.co.uk
	#    Reported At: Fri Oct 31 23:47:12 2003
	os.popen(BASH_SHELL_EXEC+" -c \""+str(launch_command)+"\"")

def showMessage(message_text,wintitle="PyPrint"):
	global PYPRINT_VERSION
	msg_info(str(wintitle)+" "+PYPRINT_VERSION,str(message_text))

def showConfirm(message_text,wintitle="PyPrint"):
	global PYPRINT_VERSION
	return msg_confirm(str(wintitle)+" "+PYPRINT_VERSION,str(message_text),_('Yes'),_('No'))


def showAbout(message_text,myappname="PyPrint"):
	showHelp(str(myappname)+" "+PYPRINT_VERSION+"\n\nCopyright (c) 2002-2004 Erica Andrews\nPhrozenSmoke [at] yahoo.com\n"+_("All rights reserved.")+"\n\n" +str(message_text) +"\n\n"+str(myappname)+_(" is open source under the General Public License (GPL).\nNO technical support will be provided for this application.\nEnjoy!"),_("About ")+" "+myappname)

def readOSLines(os_popen_cmd):
	try:
		return list(os.popen(str(os_popen_cmd)).xreadlines())
	except:
		return []

def getPrinterNames() :
	xlines=readOSLines("lpstat -v")
	printers=[]
	for pp in xlines:
		pline=pp.strip()
		if pline.find("system for") > -1:
			if pline.find(":")> pline.find("system for"):
				printer_name=pline[pline.find("system for")+len("system for"):pline.find(":")].strip()
				if not printer_name=="all": printers.append(printer_name)
	return printers

def isOnPath(binary):
  if os.environ.has_key("PATH"):
    paths=os.environ["PATH"].split(":")
    for i in paths:
      p=i
      if not p.endswith("/"): p=p+"/"
      if os.path.exists(p+str(binary)):
        return 1
  return 0


def showHelp(helptext,wintitle="PyPrint"):
	commonAbout(wintitle,helptext,0)

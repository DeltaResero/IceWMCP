#############################
#  IceWM Control Panel - Hardware Detection
#  Module - Hardware Options Module
#  
#  Copyright (c) 2003 by Erica Andrews
#  PhrozenSmoke@yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

"""
	EXAMPLE USAGE:

	from icewmcphw import *
	import pyicewmcphw as hardware

	probe_list=getSuggestedProbeList()
	for yy in probe_list:
		found_count=hardware.probe_hardware(yy)
		if found_count>0:
			counter=0
			while (counter<found_count):
				print str(hardware.get_search_result_line(counter))
				counter=counter+1

"""
import pyicewmcphw as hardware

hw_options= [
   "packages",
   "test", 
   "x11",
   "oem",
   "cdrom",
   "floppy",
   "disk", 
   "network",
   "display",
   "gfxcard",
   "framebuffer",
   "monitor",
   "camera",
   "mouse", 
   "joystick",
   "keyboard",
   "chipcard",
   "sound",
   "isdn", 
   "modem",
   "storage-ctrl",
   "storage_ctrl",
   "netcard", 
   "netcards", 
   "network-ctrl",
   "network_ctrl", 
   "printer",
   "tv", 
   "dvb", 
   "scanner", 
   "braille",
   "sys",
   "bios", 
   "cpu", 
   "partition", 
   "usb-ctrl",
   "usb_ctrl",  
   "usb",
   "pci", 
   "isapnp",
   "scsi",
   "ide", 
   "bridge",
   "hub",
   "memory", 
   "manual",
   "pcmcia", 
   "pcmcia-ctrl",
   "ieee1394",
   "ieee1394-ctrl",
   "firewire",
   "firewire-ctrl",
   "hotplug", 
   "hotplug-ctrl",
   "zip",
   "all",
   "reallyall",
   "gtkall",
   "gtkpre",
   "smp",
   "arch" ]

hw_options.sort()

def optionExists(opt_name):
	return str(opt_name).lower().strip() in hw_options

def getHardwareOptions():
	return hw_options

def getSuggestedProbeList():
	return ['gtkall','pcmcia','zip']

def list_hardware(hw_name):
		if not optionExists(str(hw_name).strip()): return []
		probe_list=[]
		found_count=hardware.probe_hardware(str(hw_name).strip())
		if found_count>0:
			counter=0
			while (counter<found_count):
				sresult=hardware.get_search_result_line(counter)
				if sresult==None: break
				sres=str(sresult).strip()
				if len(sres)>0: probe_list.append(sres)
				counter=counter+1
		return probe_list


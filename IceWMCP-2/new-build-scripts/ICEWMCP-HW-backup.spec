Summary: The hardware and system information plugin for IceWM Control Panel
Name: IceWMCP-Hardware-plugin
Version: 1.2beta
Release: 1
Copyright: Erica Andrews (PhrozenSmoke@yahoo.com)
Group: Desktop/IceWM
Vendor: Phrozen Smoke
Url: http://icesoundmanager.sourceforge.net
Provides: IceWMCP-Hardware-plugin,IceWMCP-Hardware,IceWMCP-System,IceWMCPSystem
Requires: python >= 2.2,pygtk >= 0.6.9,icewm >= 1.2.0,/bin/sh,IceWMControlPanel,GtkPCCard
Excludeos: noarch

%description
The hardware and system information plugin for IceWM Control Panel.


%files
/usr/X11R6/bin/IceWMCP-System
/usr/share/IceWMCP/IceWMCPSystem.py
/usr/share/IceWMCP/_pyicewmcphw.so
/usr/share/IceWMCP/icewmcphw.py
/usr/share/IceWMCP/pyicewmcphw.py
/usr/share/IceWMCP/libicewmcphw.so
/usr/share/IceWMCP/applet-icons/sysinfo.png
/usr/share/IceWMCP/applets/es/sysinfo.cpl
/usr/share/IceWMCP/applets/ru/sysinfo.cpl
/usr/share/IceWMCP/applets/sysinfo.cpl
/usr/share/IceWMCP/help/IceWMCPSystem.txt
/usr/share/IceWMCP/locale/es/LC_MESSAGES/icewmcp-hw.mo
/usr/share/IceWMCP/locale/ru/LC_MESSAGES/icewmcp-hw.mo
/usr/share/IceWMCP/locale/zh_TW/LC_MESSAGES/icewmcp-hw.mo
/usr/share/IceWMCP/pixmaps/hw-pixmaps/
/usr/share/icons/icewmcp-system.png
/var/lib/hardware/hd.ids

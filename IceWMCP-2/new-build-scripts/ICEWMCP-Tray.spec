Summary: A small icon in the 'icewmtray' system tray for quick access to all IceWMCP programs
Name: IceWMCP-TrayIcon-plugin
Version: 0.1
Release: 1
Copyright: Erica Andrews (PhrozenSmoke@yahoo.com)
Group: Desktop/IceWM
Vendor: Phrozen Smoke
Url: http://icesoundmanager.sourceforge.net
Provides: IceWMCP-TrayIcon-plugin,IceWMCP-TrayIcon
Requires: python >= 2.2,pygtk >= 1.9.9,icewm >= 1.2.10,/bin/sh,IceWMControlPanel
Excludeos: noarch

%description
One of IceWMCP's newest plugins: This is the IceWMCP Tray Icon program. It shows a small icon in the 'icewmtray' system tray for quick access to all IceWMCP programs for easily configuring IceWM.  It is considered a 'plugin' to IceWMCP.  	IceWMCP-TrayIcon is known to work on IceWM (version 1.2.10+) but should also work with Gnome-2, KDE-3, and any other window manager with a  NETWM/FreeDesktop.org-compliant tray notification area.  The IceWMCP Tray Icon plugin is written in C, not Python.  Requirements: You need Gtk+-2 version 2.0.6 or better and  IceWM version 1.2.10 or better WITH the 'icewmtray' program built, installed, and running on your system.  If the  'icewmtray' program is not currently running, you will need to start it before the IceWMCP-TrayIcon will work.  Since IceWM Tray Icon is considered a 'plugin', no technical support is provided for it.


%files
/usr/X11R6/bin/IceWMCP-TrayIcon
/usr/share/IceWMCP/locale/es/LC_MESSAGES/icewmcp-trayicon.mo
/usr/share/IceWMCP/doc/IceWMCP-TrayIcon-LICENSE
/usr/share/IceWMCP/doc/IceWMCP-TrayIcon-README.txt

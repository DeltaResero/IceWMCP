#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

###################################################
#	This is IcePref2:  It is an updated, overhauled, 
#	improved, and perfected version of the original IcePref 
#	(see credits above).  IcePref appears to have been 
#	abandoned by the original author, as it had not been 
#	updated since 2000. This new version, distributed under 
#	the same GNU GPL as the original IcePref, includes new 
#	features and bug fixes, optimized for IceWM 1.2.2 
#	and better. It's been tested on IceWM 1.2.2 - 1.2.14.  
#
#	Updates by: 
#		Erica Andrews (PhrozenSmoke ['at'] yahoo.com) 
#		February 2003 -February 2004
#
#	Copyright (c) 2003-2004, Erica Andrews
#
#	License: GNU General Public License
#
#	This work comes with no warranty regarding its 
#	suitability for any purpose. The author is not 
#	responsible for any damages caused by the 
#	use of this program.
###################################################
###################################################
#                                IcePref
#
# This is (or will be) the best IceWM configuration utility
# known to man.  It requires a recent version of python as well as Gtk ( >
# 1.2.0) and PyGtk.  It should work well with versions of icewm around
# 0.9.54. You may place it anywhere in your path. You are free to copy,
# change, and distribute this program under the terms of the GNU GPL.  You
# can obtain the latest version of this script from via http at
# http://members.xoom.com/SaintChoj/icepref.html.  Please report all bugs
# to Dave at SLQTN@cc.usu.edu.  Please include IcePref in the subject line.
#
# Copyright 1999, David Mortensen
#
# This work comes with no warranty regarding its suitability for any purpose.
# The author is not responsible for any damages caused by the use of this
# program.
####################################################
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

from string import *
import re,commands,math,icepref_search
import pangoxlfd

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateP(somestr))  # from icewmcp_common.py


## new in version 2.8 - 4/27/2003, IcePref2 can take a moment to start...show a nice splash screen while we load

def donada(*args):  # does nothing, just a 'dummy' method for the Splash screen, app=Application() does all the real work
	pass

# import drag-n-drop support, 5.16.2003
import icewmcp_dnd
from icewmcp_dnd import *
initColorDrag()      # enable dnd support for 'color buttons'
addDragSupportColor=icewmcp_dnd.addDragSupportColor


# added 4/27/2003 - Erica Andrews, new prettier start-up process, more informative with Splash screen
# code comes from 'icewmcp_common.py'

if NOSPLASH==0:
	setSplash(donada, "    IcePref2:  "+_("Loading...please wait.")+"    ",getBaseDir()+"icepref2.png")
	showSplash(0)
	while events_pending():
		mainiteration()

#############################
# Constants in a Changing World
#############################

VERSION = "3.4"
ICE_VERSION = "1.2.14"

# these define the types of configuration widgets

TOGGLE = 0	#done
RANGE = 1 	#done
FILE = 2	#done
PATH = 3	#done
COLOR = 4 	#done
FONT = 5	#done
ENTRY = 6 	#done
KEYSTROKE = 7	#done
MULTI = 8 	#done
THEME = 9 	#done
BITMASK = 10	#done
MOUSEBUTTON = 11 #done

# these define the indexes for the data in DEFAULTS and self.settings

TYPE = 0
VALUE = 1
TITLE = 2
MIN = 3
MAX = 4
NUM = 3

# the standard spacing and border width, respectively

SP = 5
BD = 5

# some environmental variables -- more than are needed, really.

if os.environ.has_key('OSTYPE'):
    OSTYPE   = os.environ['OSTYPE']
else:
    OSTYPE   = os.uname()[0]

if os.environ.has_key('MACHTYPE'):
    MACHTYPE = os.environ['MACHTYPE']
else:
    MACHTYPE = 'i386-pc-linux-gnu'

if os.environ.has_key('HOME'):
    HOME     = os.environ['HOME']
else:
    import user
    HOME     = user.home

if os.environ.has_key('USER'):
    USER     = os.environ['USER']
else:
    USER = os.uname()[1]
    
if os.environ.has_key('PATH'):
    PATH     = os.environ['PATH']
else:
    PATH = ''

# finally, the file we're editing
global CONFIG_FILE
CONFIG_FILE = getIceWMPrivConfigPath()+'preferences'

# added 8.18.2003
global THEME_SET_FILE
THEME_SET_FILE= getIceWMPrivConfigPath()+'theme'

# and the paths to all your themes
# (If the path to your themes is not here, simply add it.  Just follow the
# example of the other paths!)

THEME_PATH = [	getIceWMConfigPath()+'themes/*',
		HOME + '/.icewm/themes/*',getIceWMPrivConfigPath()+'themes/*'	]
			
SAMPLE_TEXT = 'IcePref2, for IceWM (http://icesoundmanager.sourceforge.net):\n AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp\nQqRrSsTtUuVvWwXxYyZz1234567890'
ERROR_TEXT = 'Invalid Font'

## added 1.27.2003 - variables that require image previewers after them
REQUIRE_PREVIEW=['Theme','DesktopBackgroundImage']

## added 1.27.2003 - allow displaying of only one module (or tab) with command line option "module=Themes"
##  default behavior is to show ALL modules and tabs
SHOW_MODULE=None

# aded 5.5.2003 - allow pulling of selected 'tabs'
global PULL_TAB
PULL_TAB=None

#############################################
# Cofiguration Options Data
#
# In order to add a new item, it must be added to each of the following three
# data structures.  DEFAULTS is a dictionary containing information about the
# widget to be used, the parameter's default value (as a string), the title/label
# and the min and max for range type controls.  The keys are, of course, the
# name of the variables in the preferences file.
##############################################

DEFAULTS = {	

		#added 8.19.2003, icewm 1.2.10
		'MoveSizeInterior': [RANGE, '0', 'Bitmask for inner decorations', 0, 31],
		'MoveSizeDimensionLines': [RANGE, '0', 'Bitmask for dimension lines', 0, 4095],
		'MoveSizeGaugeLines': [RANGE, '0', 'Bitmask for gauge lines', 0, 15],
		'MoveSizeDimensionLabels': [RANGE, '0', 'Bitmask for dimension labels', 0, 4095],
		'MoveSizeGeometryLabels': [RANGE, '0', 'Bitmask for geometry labels', 0, 127],
		'FocusRequestFlashTime': [RANGE, '0', 'Number of seconds the taskbar application will blink when requesting focus', 0, 86400],
		'moveSizeFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-100-*-*-*-*-*-*"', "Font for the window's move/resize status"],


		'ClickToFocus': [TOGGLE, '1', 'Focus windows by clicking'],

		# new WINDOW stuff - added 3.14.2003 - PhrozenSmoke
		'ShapesProtectClientWindow': [TOGGLE, '1', 'Shaped pixmaps protect client window'],
		## DEPRECATED ##  'SizeMaximized': [TOGGLE, '1', 'Maximized windows can be resized'],
		'AllowFullscreen': [TOGGLE, '1', 'Enable full-screen mode for windows'],

		# new MENU stuff - added 3.14.2003 - PhrozenSmoke
		'ShowProgramsMenu': [TOGGLE, '1', 'Show "Programs" menu'],
		'ShowRun': [TOGGLE, '1', 'Show "Run..." on the menu'],
		'ShowLogoutSubMenu': [TOGGLE, '1', 'Show logout sub-menu'],
		'ShowWindowList': [TOGGLE, '1', 'Show window list on the menu'],
		'ShowAbout': [TOGGLE, '1', 'Show "About" on the menu'],

		# New TASKBAR STUFF - added 1/25/2003 by PhrozenSmoke
		'TaskBarShowAPMTime': [TOGGLE, '1', 'Show Advanced Power Management time'],

			# added 6.16.2003 - new in icewm 1.2.8, but what's the difference 
			# 'EnableAddressBar' and 'ShowAddressBar'??
		'EnableAddressBar': [TOGGLE, '1', 'Enable address bar on the task bar'],

		'ShowAddressBar': [TOGGLE, '1', 'Show address bar on the task bar'],
		'TaskBarShowWindowIcons': [TOGGLE, '1', 'Show window icons on the task bar'],
		'TaskBarKeepBelow': [TOGGLE, '0', 'Keep tasbar below all other windows'],
		'TrayShowAllWindows': [TOGGLE, '1', 'Show all windows on the taskbar'],
		'TaskBarShowTray': [TOGGLE, '1', 'Show task tray on task bar'],
		'TrayDrawBevel': [TOGGLE, '0', 'Task tray has a bevel around it (Like the Windows system tray)'],
		'TaskBarLaunchOnSingleClick': [TOGGLE, '1', 'Launch task bar programs (clock, etc.) on a single click'],
		'ShowWorkspaceStatus': [TOGGLE, '1', 'Show workspace tooltip when changing workspaces'],
		'WorkspaceStatusTime': [RANGE, '2500', 'Number of milliseconds to display the workspace tooltip when changing workspaces', 0, 6000],

		# more QUICKSWITCH STUFF - 3.14.2003 - PhrozenSmoke
		'QuickSwitchGroupWorkspaces': [TOGGLE, '1', 'Quick-Switch groups windows on current workspace'],

		# New QUICKSWITCH STUFF - added 1/25/2003 by PhrozenSmoke
		'QuickSwitchSmallWindow': [TOGGLE, '0', 'Show a small window'],
		'QuickSwitchFillSelection': [TOGGLE, '0', 'Fill highlight rectangle'],
		'QuickSwitchAllIcons': [TOGGLE, '1', 'Show all icons'],
		'QuickSwitchHugeIcon': [TOGGLE, '0', 'Use large (48x48) icons in quick switch window'],
		'QuickSwitchTextFirst': [TOGGLE, '0', 'Show text above icons'],
		'QuickSwitchIconBorder': [RANGE, '2', 'Border size of quick-switch icons', 0, 30],
		'QuickSwitchIconMargin': [RANGE, '4', 'Size of icon margins of quick-switch icons', 0, 30],
		'QuickSwitchHorzMargin': [RANGE, '3', 'Horizontal margin of quick-switch window', 0, 30],
		'QuickSwitchVertMargin': [RANGE, '3', 'Vertical margin of quick-switch window', 0, 30],
		'QuickSwitchSeparatorSize': [RANGE, '6', 'Size of the quick-switch window separator', 0, 30],
		'ColorQuickSwitchActive': [COLOR, '"rgb:00/EE/FF"', 'Color of quick-switch highlight rectangle'],

		'RaiseOnFocus': [TOGGLE, '1', 'Raise windows when focused'],
		'FocusOnClickClient': [TOGGLE, '1', 'Focus window when client area clicked'],
		'RaiseOnClickClient': [TOGGLE, '1', 'Raise window when client area clicked'],
		'RaiseOnClickTitleBar': [TOGGLE, '1', 'Raise window when title bar is clicked'],
		'RaiseOnClickButton': [TOGGLE, '1', 'Raise when frame button is clicked'],
		'RaiseOnClickFrame': [TOGGLE, '1', 'Raise when frame border is clicked'],
		'PassFirstClickToClient': [TOGGLE, '1', 'Pass focusing click on client area to client'],


		# added 1.26.2003 - new focus stuff
		'FocusOnAppRaise': [TOGGLE, '1', 'Focus window when application window is raised'],
		'FocusChangesWorkspace': [TOGGLE, '1', 'Change workspaces when focusing on a window on another workspace'],
		'LowerOnClickWhenRaised': [TOGGLE, '0', 'Lower a raised window if clicked a second time'],
		'ContinuousEdgeSwitch': [TOGGLE, '1', 'Taking the mouse pointer to the edge of the screen moves to the next workspace'],
		'HorizontalEdgeSwitch': [TOGGLE, '0', 'Enable horizontal edge switch for the desktop'],
		'VerticalEdgeSwitch': [TOGGLE, '0', 'Enable vertical edge switch for the desktop'],


		'FocusOnMap': [TOGGLE, '1', 'Focus normal window when initially mapped'],
		'FocusOnMapTransient': [TOGGLE, '1', 'Focus dialog window when initally mapped'],
		'FocusOnMapTransientActive': [TOGGLE, '1', 'Focus dialog window when initially mapped only if parent frame focused'],
		'PointerColormap': [TOGGLE, '1', 'Colormap follows pointer'],
		'LimitSize': [TOGGLE, '1', 'Limit initial size of windows to screen'],
		'LimitPosition': [TOGGLE, '1', 'Limit initial position of windows to screen'],
		## DEPRECATED ##   'SizeMaximized': [TOGGLE, '0', 'Maximized windows can be resized'],
		'ShowMoveSizeStatus': [TOGGLE, '1', 'Show position status window during move/resize'],
		'MinimizeToDesktop': [TOGGLE, '0', 'Display mini-icons on desktop for minimized windows'],
		'StrongPointerFocus': [TOGGLE, '0', 'Always maintain focus under mouse window (makes some keyboard support non-functional)'],
		'OpaqueMove': [TOGGLE, '1', 'Opaque window move'],
		'OpaqueResize': [TOGGLE, '1', 'Opaque window resize'],
		'ManualPlacement': [TOGGLE, '0', 'Windows initially placed manually by user'],
		'SmartPlacement': [TOGGLE, '1', 'Smart window placement (minimize overlap)'],
		'CenterTransientsOnOwner': [TOGGLE, '1', 'Center dialogs on owner window'],

		# added 1.26.2003 - new window placement stuff
		'LimitByDockLayer': [TOGGLE, '1', 'Limit by dock layer'],
		'CenterMaximizedWindows': [TOGGLE, '0', 'Center maximixed windows'],

		'MenuMouseTracking': [TOGGLE, '0', 'Menus track mouse even with no mouse buttons held'],
		'AutoRaise': [TOGGLE, '0', 'Auto raise windows after delay'],
		'DelayPointerFocus': [TOGGLE, '0', 'Delay pointer focusing when mouse moves'],
		'Win95Keys': [TOGGLE, '1', 'Support Windows95/98-style keyboard keys'],



		# deprecated options removed: ModMetaIsCtrlAlt  - 6.16.2003
		'ModSuperIsCtrlAlt': [TOGGLE, '1', _('Treat Penguin/Meta_L/Meta_R/Windows keys as Ctrl+Alt')+' ('+_('support the "Windows" key')+')'],


		'UseMouseWheel': [TOGGLE, '0', 'Support mouse wheel'],
		'ShowPopupsAbovePointer': [TOGGLE, '0', 'Show popup menus above mouse pointer'],
		'ReplayMenuCancelClick': [TOGGLE, '0', 'Send the clicks outside menus to target window'],
		'QuickSwitch': [TOGGLE, '1', 'Enable Quick-switch (Alt+Tab) window switching'],
		'QuickSwitchToMinimized': [TOGGLE, '1', 'Enable Alt+Tab to minimized windows'],
		'QuickSwitchToHidden': [TOGGLE, '1', 'Enable Alt-Tab to hidden windows'],
		'QuickSwitchToAllWorkspaces': [TOGGLE, '0', 'Enable Alt+Tab to windows on other workspaces'],
		'GrabRootWindow': [TOGGLE, '1', 'IceWM manages the root window'],
		'SnapMove': [TOGGLE, '1', 'Snap to nearest screen edge/window when moving windows'],
		'EdgeSwitch': [TOGGLE, '0', 'Workspace switches by moving mouse to left/right screen edge'],
		'DesktopBackgroundCenter': [TOGGLE, '0', 'Display desktop wallpaper centered, instead of tiled.'],
		'AutoReloadMenus':[TOGGLE, '1', 'Reload menu files automatically'],
		'ShowMenuButtonIcon':[TOGGLE, '1', 'Show application icon over menu button'],

		# NEW Stuff - added 12.11.2003, IceWM 1.2.13
		'DesktopBackgroundScaled':[TOGGLE, '0', 'Desktop background scaled to full screen'],
		'TaskBarShowShowDesktopButton':[TOGGLE, '1', "Show the 'Show Desktop' button on taskbar"],
		'TaskBarWorkspacesLeft':[TOGGLE, '1', 'Place workspace buttons on the left, instead of the right'],
		'DoubleBuffer':[TOGGLE, '1', 'Use double buffering when redrawing the display'],

		# NEW Stuff - added 1.26.2003 - scrollbars
		'ScrollBarX': [RANGE, '16', 'Horizontal scrollbar button size', 0, 100],
		'ScrollBarY': [RANGE, '16', 'Vertical scrollbar button size', 0, 100],
		'ColorScrollBarButton': [COLOR, '"rgb:C0/C0/C0"', 'Scrollbar button color'],
		'ColorScrollBarButtonArrow': [COLOR, '"rgb:00/00/00"', 'Scrollbar button arrow color'],
		'ColorScrollBarInactiveArrow': [COLOR, '"rgb:80/80/80"', 'Inactive scrollbar button arrow color'],


		# NEW Stuff - added 1.26.2003 - desktop
		'SupportSemitransparency':[TOGGLE, '1', 'Support semi-transparent applications like gnome-terminal'],
		'DesktopTransparencyColor':[COLOR, '"rgb:FF/FF/FF"', 'Color to use for transparent applications'],
		'DesktopTransparencyImage': [FILE, '""', 'Image to use for transparent applications'],


		# NEW Stuff - added 1.26.2003 - title bars
		'TitleBarJoinRight':[TOGGLE, '0', 'Title bar join right'],
		'TitleBarJoinLeft':[TOGGLE, '0', 'Title bar join left'],
		'TitleBarJustify': [RANGE, '0', 'Title bar text position', 0, 100],
		'TitleBarHorzOffset': [RANGE, '0', 'Title bar text horizontal offset', -128, 128],
		'TitleBarVertOffset': [RANGE, '0', 'Title bar text vertical offset', -128, 128],
		'ColorActiveTitleBarShadow': [COLOR, '"rgb:00/00/00"', 'Active title bar shadow'],
		'ColorNormalTitleBarShadow': [COLOR, '"rgb:00/00/00"', 'Inactive title bar shadow'],


		# NEW Stuff - added 1.26.2003 - misc. features
		'DisableImlibCaches':[TOGGLE, '1', 'Disable Gdk-Imlib image cache use'],
		'XFreeType':[TOGGLE, '1', 'Enable XFreeType extension (buggy, may result in font-loading errors)'],
		'XineramaPrimaryScreen':[RANGE, '0', 'Xinerama primary screen', 0, 63],


		# NEW MENU Stuff - added 1.26.2003
		'DontRotateMenuPointer':[TOGGLE, '1', 'Do not rotate the mouse cursor when displaying a menu'],
		'ShowHelp':[TOGGLE, '1', 'Show the IceWM "help" item on the task bar menu'],
		'ShowLogoutMenu':[TOGGLE, '1', 'Show the "logout" menu on the task bar menu'],
		'ColorDisabledMenuItemShadow':[COLOR, '"rgb:00/EE/FF"', 'Color of disabled menu items'],
		'MenuMaximalWidth':[RANGE, '0', 'Maximum menu width (0 to let IceWM decide)', 0, 20000],

		'AutoDetectGNOME': [TOGGLE, '1', 'Automatically disable some functions when running under GNOME'],
		'ShowTaskBar': [TOGGLE, '1', 'Show task bar'],
		'TaskBarAtTop': [TOGGLE, '0', 'Task bar at top of the screen'],
		'TaskBarAutoHide': [TOGGLE, '0', 'Auto hide task bar after delay'],
		'TaskBarShowClock': [TOGGLE, '1', 'Show clock on task bar'],
		'TaskBarShowAPMStatus': [TOGGLE, '0', 'Show Advanced Power Management (APM) status on task bar'],
		'TaskBarClockLeds': [TOGGLE, '1', 'Task bar clock uses nice pixmapped LCD display'],
		'TaskBarShowMailboxStatus': [TOGGLE, '1', 'Show mailbox status on the task bar'],
		'TaskBarMailboxStatusBeepOnNewMail': [TOGGLE, '0', 'Beep when new mail arrives'],
		'TaskBarMailboxStatusCountMessages': [TOGGLE, '0', 'Count messages in mailbox'],
		'TaskBarShowWorkspaces': [TOGGLE, '1', 'Show workspace switching buttons on task bar'],
		'TaskBarShowWindows':[TOGGLE, '1', 'Show windows on the task bar'],
		'TaskBarShowAllWindows': [TOGGLE, '0', 'Show windows from all workspaces on task bar'],
		'TaskBarShowStartMenu': [TOGGLE, '1', 'Show "Start" menu on task bar'],
		'TaskBarShowWindowListMenu': [TOGGLE, '1', 'Show "window list" menu on task bar'],
		'TaskBarShowCPUStatus': [TOGGLE, '1', 'Show CPU status on task bar'],
		'TaskBarShowNetStatus': [TOGGLE, '1', 'Show network status on task bar'],
		'TaskBarDoubleHeight': [TOGGLE, '1', 'Use double height task bar (highly recommended)'],
		'WarpPointer': [TOGGLE, '0', 'Move mouse when doing focusing in pointer focus mode'],
		'ClientWindowMouseActions': [TOGGLE, '1', 'Allow mouse actions on client windows (buggy with some programs)'],
		'ShowThemesMenu': [TOGGLE, '1', 'Show the submenu for selecting themes'],
                'MultiByte': [TOGGLE, '1', 'Multibyte internationalization support'],
		'ConfirmLogout': [TOGGLE, '1', 'Ask for confirmation on logout'],
		'BorderSizeX': [RANGE, '6', 'Horizontal window border', 0, 128],
		'BorderSizeY': [RANGE, '6', 'Veritical window border', 0, 128],
		'DlgBorderSizeX': [RANGE, '2', 'Horizontal dialog window border', 0, 128],
		'DlgBorderSizeY': [RANGE, '2', 'Vertical dialog window border', 0, 128],

		# added 1.26.2003
		'MsgBoxDefaultAction': [RANGE, '0', 'Default IceWM dialog action (0 for "Cancel", 1 for "OK")', 0, 1],

		'TitleBarHeight': [RANGE, '20', 'Title bar height', 0, 128],
		'CornerSizeX': [RANGE, '24', 'Resize corner width', 0, 64],
		'CornerSizeY': [RANGE, '24', 'Resize corner height', 0, 64],
		'ClickMotionDistance': [RANGE, '4', 'Pointer motion distance before click gets interpreted as drag', 0, 32],
		'ClickMotionDelay': [RANGE, '200', 'Delay before click gets interpreted as drag', 0, 2000],
		'MultiClickTime': [RANGE, '400', 'Mouse double-click speed', 0, 5000],
		'MenuActivateDelay': [RANGE, '40', 'Delay before activating menu items', 0, 5000],
		'SubmenuMenuActivateDelay': [RANGE, '300', 'Delay before activating menu submenus', 0, 5000],
		'ToolTipDelay': [RANGE, '1000', 'Delay before tooltip window is displayed', 0, 5000],
                'ToolTipTime': [RANGE, '0', 'Time before tooltip is hidden', 0, 5000],
		'AutoHideDelay': [RANGE, '300', 'Delay before task bar is automatically hidden', 0, 5000],
		'AutoRaiseDelay': [RANGE, '400', 'Delay before windows are auto raised', 0, 5000],
		'EdgeResistance': [RANGE, '32', 'Resistance in pixels when trying to move windows off the screen', 0, 10000],
		'PointerFocusDelay': [RANGE, '200', 'Delay for pointer focus switching', 0, 1000],
		'SnapDistance': [RANGE, '8', 'Distance in pixels before windows snap together', 0, 128],
		'EdgeSwitchDelay': [RANGE, '600', 'Screen edge workspace switching delay', 0, 5000],
		'ScrollBarStartDelay': [RANGE, '500', 'Initial scrollbar autoscroll delay', 0, 5000],
		'ScrollBarDelay': [RANGE, '30', 'Scroll bar delay', 0, 5000],
		'AutoScrollStartDelay': [RANGE, '500', 'Autoscroll start delay', 0, 5000],
		'AutoScrollDelay': [RANGE, '60', 'Auto scroll delay', 0, 5000],
		'UseRootButtons': [BITMASK, '255', 'Bitmask of root window button click to use in window manager', 0, 255],
		'ButtonRaiseMask': [BITMASK, '1', 'Bitmask of buttons that raise the window when pressed', 0, 255],
		'DesktopWinMenuButton': [MOUSEBUTTON, '0', 'Mouse-button clicked on desktop to show window list menu', 0, 5],
		'DesktopWinListButton': [MOUSEBUTTON, '2', 'Mouse-button clicked on desktop to show window list', 0, 5],
		'DesktopMenuButton': [MOUSEBUTTON, '3', 'Mouse-button clicked on desktop to show menu', 0, 5],
		'TitleBarMaximizeButton': [MOUSEBUTTON, '1', 'Mouse-button clicked on titlebar to maximize window', 0, 8],
		'TitleBarRollupButton': [MOUSEBUTTON, '2', 'Mouse-button clicked on titlebar to roll up window', 0, 8],
		'MailCheckDelay': [RANGE, '30', 'Delay between new-mail checks in seconds', 0, 3600],
		'TaskBarCPUSamples': [RANGE, '20', 'Width of CPU Monitor', 2, 1000,],
		'TitleButtonsLeft': [ENTRY, '"s"', 'Titlebar buttons from left to right (x=close, m=max, i=min, h=hide, r=rollup, s=sysmenu)'],
		'TitleButtonsRight': [ENTRY, '"xmir"', 'Titlebar buttons from right to left (x=close, m=max, i=min, h=hide, r=rollup, s=sysmenu)'],
		'TitleButtonsSupported' : [ENTRY, '"xmis"', 'Titlebar buttons supported by theme (x, m, i, r, h, s, d)'],
		'IconPath': [PATH, '""+getIceWMConfigPath()+"icons/:/usr/share/icons/:/usr/share/pixmaps/"', 'Icon search path (colon separated)'],
		'MailBoxPath': [FILE, '""', 'Mailbox path ($MAIL is used if no value is specified).  Example: file:///var/spool/mail/my_username       Example: pop3://my_username:my_password@my.mail-host.com/      Example: imap://my_username@my.mail-host.com/INBOX.mail.icewm-user'],
		
		#added 1.26.2003
		'KDEDataDir': [FILE, '"/usr/share/applnk"', 'KDE menu data directory'],

		'MailCommand': [FILE, '"xterm -name pine -title PINE -e pine"', 'Command to run when mailbox icon is clicked'],
		'NewMailCommand': [FILE, '""', 'Command to run when new mail arrives'],
		'LockCommand': [FILE, '"xlock"', 'Command to lock display or show screensaver'],
		'ClockCommand': [FILE, '"xclock -name icewm -title Clock"', 'Command to run when the taskbar clock is clicked'],
		'RunCommand': [FILE, '""', 'Command to select and run a program (The "Run..." command on the taskbar menu)'],
		'OpenCommand': [FILE, '""', 'Open command'],
		'TerminalCommand': [FILE, '"xterm"', 'Terminal emulator (must accept -e option)'],
		'LogoutCommand': [FILE, '""', 'Command to start logout'],
		'LogoutCancelCommand': [FILE, '""', 'Command to cancel logout'],
		'ShutdownCommand' : [FILE, '"shutdown -h now"', 'Command to shut down the system'],
		'RebootCommand' : [FILE, '"shutdown -r now"', 'Command to reboot the system'],
		'CPUStatusCommand' : [FILE, '"xterm -name top -title Process\ Status -e top"', 'Command to run when CPU status monitor is clicked'],
		'NetStatusCommand' : [FILE, '"xterm -name netstat -title Network\ Status -e netstat -c"', 'Command to run when net status monitor is clicked'],
		'AddressBarCommand' : [FILE, '""', 'Command to run for address bar entries when [Enter] is pressed on the address bar'],
		'NetworkStatusDevice': [ENTRY, '"ppp0"', 'Network device for which to show network status (examples:  ppp0, lo, eth0)'],
		'TimeFormat': [ENTRY, '"%H:%M:%S"', 'Clock time format (strftime format string - see man page "strftime" for more info)'],
		'DateFormat': [ENTRY, '"%B %A %Y/%m/%d %H:%M:%S %Z"', 'Clock date format for tooltip (strftime format string - see man page "strftime" for more info)'],

		# added 1.26.2003 - applet stuff
		'TimeFormatAlt': [ENTRY, '"%H:%M:%S"', 'Alternate clock time format (for "flashing" effects - strftime format string - see man page "strftime" for more info)  Note: Leaving this blank may result in NO clock showing at all.'],
		'NetStatusClassHint': [ENTRY, '"netstat.XTerm"', 'Net status WM_CLASS hint'],
		'ClockClassHint': [ENTRY, '"icewm.XClock"', 'Clock status WM_CLASS hint'],
		'MailClassHint': [ENTRY, '"pine.XTerm"', 'Mail status WM_CLASS hint'],
		'CPUStatusClassHint': [ENTRY, '"top.XTerm"', 'CPU status WM_CLASS hint'],
		'AcpiIgnoreBatteries': [ENTRY, '""', 'List of battery names (directories) in /proc/acpi/battery to ignore for APM'],

		'Theme': [THEME, '"icedesert/default.theme"', 'IceWM Themes'],
		'ThemeAuthor': [ENTRY, '""', 'Theme author'],
		'ThemeDescription': [ENTRY, '""', 'Theme description'],

		# added 1.26.2003
		'Gradients' : [FILE, '""', 'List of gradient images in the current theme'],

		'TitleFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Title bar font'],
		'MenuFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Menu font'],
		'StatusFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Status font'],
		'QuickSwitchFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Quick switch window font'],
		'NormalButtonFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'Normal button font'],
		'ActiveButtonFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Active button font'],
		'NormalTaskBarFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'Normal taskbar font'],
		'ActiveTaskBarFontName': [FONT, '"-adobe-helvetica-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Active taskbar font'],
		'MinimizedWindowFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'Minimized window font'],
		'ListBoxFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'List box font (Window list box)'],
		'ToolTipFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'Tooltip font'],
		'ClockFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-120-*-*-*-*-*-*"', 'Clock font'],
		'ApmFontName': [FONT, '"-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*"', 'APM font'],
		'LabelFontName': [FONT, '"-adobe-helvetica-medium-r-*-*-*-140-*-*-*-*-*-*"', 'Dialog Label font'],

		# NEW FONT STUFF added 1.25.2003
		'FxFontName': [FONT, '"-adobe-courier-bold-r-*-*-*-120-*-*-*-*-*-*"', 'FX Font font'],
		'InputFontName': [FONT, '"-adobe-courier-bold-r-*-*-*-140-*-*-*-*-*-*"', 'Address bar font'],
		'ToolButtonFontName': [FONT,'"-adobe-courier-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Tool Button font'],
		'ActiveWorkspaceFontName': [FONT,'"-adobe-courier-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Active workspace  font'],
		'NormalWorkspaceFontName': [FONT,'"-adobe-courier-bold-r-*-*-*-120-*-*-*-*-*-*"', 'Normal workspace  font'],

		# added 1.26.2003 - toolbar button colors
		'ColorToolButton': [COLOR, '"rgb:C0/C0/C0"', 'Toolbar button color'],
		'ColorToolButtonText': [COLOR, '"rgb:00/00/00"', 'Toolbar button text color'],

		'ColorDialog': [COLOR, '"rgb:C0/C0/C0"', 'Dialog box color'],
		'ColorActiveBorder': [COLOR, '"rgb:C0/C0/C0"', 'Active border color'],
		'ColorNormalBorder': [COLOR,'"rgb:C0/C0/C0"', 'Normal border color'],
		'ColorNormalTitleButton': [COLOR, '"rgb:C0/C0/C0"', 'Normal title button color'],
		'ColorNormalTitleButtonText': [COLOR, '"rgb:00/00/00"', 'Normal title button text color'],
		'ColorNormalButton': [COLOR, '"rgb:C0/C0/C0"', 'Normal button color'],
		'ColorNormalButtonText': [COLOR, '"rgb:00/00/00"', 'Normal button text color'],
		'ColorActiveButton': [COLOR, '"rgb:E0/E0/E0"', 'Active button color'],
		'ColorActiveButtonText': [COLOR, '"rgb:00/00/00"', 'Active button text color'],
		'ColorActiveTitleBar': [COLOR, '"rgb:00/00/A0"', 'Active title bar color'],
		'ColorNormalTitleBar': [COLOR, '"rgb:80/80/80"', 'Normal title bar color'],
		'ColorActiveTitleBarText': [COLOR, '"rgb:FF/FF/FF"', 'Active title bar text color'],
		'ColorNormalTitleBarText': [COLOR, '"rgb:00/00/00"', 'Normal title bar text color'],
		'ColorNormalMinimizedWindow': [COLOR, '"rgb:C0/C0/C0"', 'Normal minimized window color'],
		'ColorNormalMinimizedWindowText': [COLOR, '"rgb:00/00/00"', 'Normal minimized window text color'],
		'ColorActiveMinimizedWindow': [COLOR, '"rgb:E0/E0/E0"', 'Active minimized window color'],
		'ColorActiveMinimizedWindowText': [COLOR, '"rgb:00/00/00"', 'Active minimized window text color'],
		'ColorNormalMenu': [COLOR, '"rgb:C0/C0/C0"', 'Normal menu color'],
		'ColorActiveMenuItem': [COLOR, '"rgb:A0/A0/A0"', 'Active menu item color'],
		'ColorActiveMenuItemText': [COLOR, '"rgb:00/00/00"', 'Active menu item text color'],
		'ColorNormalMenuItemText': [COLOR, '"rgb:00/00/00"', 'Normal menu item text color'],
		'ColorDisabledMenuItemText': [COLOR, '"rgb:80/80/80"', 'Disabled menu item text color'],
		'ColorMoveSizeStatus': [COLOR, '"rgb:C0/C0/C0"', 'Move/size status color'],
		'ColorMoveSizeStatusText': [COLOR, '"rgb:00/00/00"', 'Move/size status text color'],
		'ColorQuickSwitch': [COLOR, '"rgb:C0/C0/C0"', 'Quick switch window color'],
		'ColorQuickSwitchText': [COLOR, '"rgb:00/00/00"', 'Quick switch text color'],
		'ColorDefaultTaskBar': [COLOR, '"rgb:C0/C0/C0"', 'Default taskbar color'],
		'ColorNormalTaskBarApp': [COLOR, '"rgb:C0/C0/C0"', 'Normal taskbar color'],
		'ColorNormalTaskBarAppText': [COLOR, '"rgb:00/00/00"', 'Normal taskbar app text color'],
		'ColorActiveTaskBarApp': [COLOR, '"rgb:E0/E0/E0"', 'Active taskbar app color'],
		'ColorActiveTaskBarAppText': [COLOR, '"rgb:00/00/00"', 'Active taskbar app text color'],
		'ColorMinimizedTaskBarApp': [COLOR, '"rgb:A0/A0/A0"', 'Minimized taskbar app color'],
		'ColorMinimizedTaskBarAppText': [COLOR, '"rgb:00/00/00"', 'Minimized taskbar app text'],
		'ColorInvisibleTaskBarApp': [COLOR, '"rgb:80/80/80"', 'Invisible taskbar app color'],
		'ColorInvisibleTaskBarAppText': [COLOR, '"rgb:00/00/00"', 'Invisible taskbar app text'],
		'ColorScrollBar': [COLOR, '"rgb:A0/A0/A0"', 'Scroll bar color'],
		'ColorScrollBarArrow': [COLOR, '"rgb:C0/C0/C0"', 'Scroll bar arrow color'],
		'ColorScrollBarSlider': [COLOR, '"rgb:C0/C0/C0"', 'Scroll bar slider color'],
		'ColorListBox': [COLOR, '"rgb:C0/C0/C0"', 'List box color (Window list)'],
		'ColorListBoxText': [COLOR, '"rgb:00/00/00"', 'List box text color (Window list)'],
		'ColorListBoxSelection': [COLOR, '"rgb:80/80/80"', 'List box selection color (Window list)'],
		'ColorListBoxSelectionText': [COLOR, '"rgb:00/00/00"', 'List box selection text color (Window list)'],
		'ColorToolTip': [COLOR, '"rgb:E0/E0/00"', 'Tooltip color'],
		'ColorToolTipText': [COLOR, '"rgb:00/00/00"', 'Tooltip text color'],
		'ColorClock': [COLOR, '"rgb:00/00/00"', 'Clock color'],
		'ColorClockText': [COLOR, '"rgb:00/FF/00"', 'Clock text color'],
		'ColorApm': [COLOR, '"rgb:00/00/00"', 'APM color'],
		'ColorApmText': [COLOR, '"rgb:00/FF/00"', 'APM text color'],
		'ColorLabel': [COLOR, '"rgb:C0/C0/C0"', 'Dialog Label color'],
		'ColorLabelText': [COLOR, '"rgb:00/00/00"', 'Dialog Label text color'],
		'ColorInput': [COLOR, '"rgb:FF/FF/FF"', 'Input color (Address bar)'],
		'ColorInputText': [COLOR, '"rgb:00/00/00"', 'Input text color (Address bar)'],
		'ColorInputSelection': [COLOR, '"rgb:80/80/80"', 'Input selection color (Address bar)'],
		'ColorInputSelectionText': [COLOR, '"rgb:00/00/00"', 'Input selection text color (Address bar)'],
		'DesktopBackgroundColor': [COLOR, '"rgb:00/20/40"', 'Desktop background color'],
		'DesktopBackgroundImage': [FILE, '""', 'Desktop wallpaper image'],
		'ColorCPUStatusUser': [COLOR, '"rgb:00/FF/00"', 'User CPU usage color'],
		'ColorCPUStatusSystem': [COLOR, '"rgb:FF/00/00"', 'System CPU usage color'],
		'ColorCPUStatusNice': [COLOR, '"rgb:00/00/FF"', 'Nice CPU usage color'],
		'ColorCPUStatusIdle': [COLOR, '"rgb:00/00/00"', 'CPU Idle color'],
		'ColorNetSend': [COLOR, '"rgb:FF/FF/00"', 'Color of sent data on net monitor'],
		'ColorNetReceive': [COLOR, '"rgb:FF/00/FF"', 'Color of received data on net monitor'],
		'ColorNetIdle': [COLOR, '"rgb:00/00/00"', 'Color representing idle on net monitor'],

		#NEW KEYSTROKES - added 1.26.2003
		'KeyWinFullscreen': [KEYSTROKE, '"Alt+F11"', '"Window full-screen" shortcut'],
		'KeySysWorkspaceLast': [KEYSTROKE, '"Alt+Ctrl+Down"', '"Go to last workspace" shortcut'],
		'KeySysUndoArrange': [KEYSTROKE, '"Alt+Shift+F7"', '"Undo arrange" shortcut'],
		'KeySysTileHorizontal': [KEYSTROKE, '"Alt+Shift+F3"', '"Tile windows horizontally" shortcut'],
		'KeySysTileVertical': [KEYSTROKE, '"Alt+Shift+F2', '"Tile windows vertically" shortcut'],
		'KeySysArrange': [KEYSTROKE, '"Alt+Shift+F5"', '"Arrange windows" shortcut'],
		'KeySysArrangeIcons': [KEYSTROKE, '"Alt+Shift+F8"', '"Arrange icons" shortcut'],
		'KeySysMinimizeAll': [KEYSTROKE, '"Alt+Shift+F9"', '"Minimize all windows" shortcut'],
		'KeySysCascade': [KEYSTROKE, '"Alt+Shift+F4"', '"Cascade windows" shortcut'],
		'KeySysWorkspaceLastTakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+Down"', '"Workspace take last window" shortcut'],
		'KeySysHideAll': [KEYSTROKE, '"Alt+Shift+F11"', '"Hide all windows" shortcut'],

		'KeyWinRaise': [KEYSTROKE, '"Alt+F1"', '"Raise window" shortcut'],
		'KeyWinOccupyAll': [KEYSTROKE, '"Alt+F2"', '"Occupy all" shortcut'],
		'KeyWinLower': [KEYSTROKE, '"Alt+F3"', '"Lower window" shortcut'],
		'KeyWinClose': [KEYSTROKE, '"Alt+F4"', '"Close window" shortcut'],
		'KeyWinRestore': [KEYSTROKE, '"Alt+F5"', '"Restore window" shortcut'],
		'KeyWinPrev': [KEYSTROKE, '"Alt+Shift+F6"', '"Previous window" shortcut'],
		'KeyWinNext': [KEYSTROKE, '"Alt+F6"', '"Next window" shortcut'],
		'KeyWinMove': [KEYSTROKE, '"Alt+F7"', '"Move window" shortcut'],
		'KeyWinSize': [KEYSTROKE, '"Alt+F8"', '"Size window" shortcut'],
		'KeyWinMinimize': [KEYSTROKE, '"Alt+F9"', '"Minimize window" shortcut'],
		'KeyWinMaximize': [KEYSTROKE, '"Alt+F10"', '"Maximize window" shortcut'],
		'KeyWinMaximizeVert': [KEYSTROKE, '"Alt+Shift+F10"', '"Maximize window vertically" shortcut'],
		'KeyWinHide': [KEYSTROKE, '"Alt+Shift+F12"', '"Hide window" shortcut'],
		'KeyWinRollup': [KEYSTROKE, '"Alt+F12"', '"Rollup window" shortcut'],
		'KeyWinMenu': [KEYSTROKE, '"Alt+Space"', '"Window menu" shortcut'],
		'KeySysSwitchNext': [KEYSTROKE, '"Alt+Tab"', '"Next item" shortcut'],
		'KeySysSwitchLast': [KEYSTROKE, '"Alt+Shift+Tab"', '"Last item" shortcut'],
		'KeySysWinNext': [KEYSTROKE, '"Alt+Esc"', '"Next sys window" shortcut'],
		'KeySysWinPrev': [KEYSTROKE, '"Alt+Shift+Esc"', '"Previous sys window" shortcut'],
		'KeySysWinMenu': [KEYSTROKE, '"Shift+Esc"', '"Window menu" shortcut'],
		'KeySysDialog': [KEYSTROKE, '"Alt+Ctrl+Del"', '"Logout / screenlock dialog" shortcut'],
		'KeySysMenu': [KEYSTROKE, '"Ctrl+Esc"', '"Program menu" shortcut'],

		# disabled, not supported in icewm 1.2.8 - 6.16.2003
		# 'KeySysRun': [KEYSTROKE, '"Alt+Ctrl+R"', '"Run" shortcut'],

		'KeySysWindowList': [KEYSTROKE, '"Alt+Ctrl+Esc"', '"Window list" shortcut'],
		'KeySysWinListMenu': [KEYSTROKE, '""', '"Window list" menu shortcut'],
		'KeySysAddressBar': [KEYSTROKE, '"Alt+Ctrl+Space"', '"Address bar" shortcut'],
		'KeySysWorkspacePrev': [KEYSTROKE, '"Alt+Ctrl+Left"', '"Previous workspace" shortcut'],
		'KeySysWorkspaceNext': [KEYSTROKE, '"Alt+Ctrl+Right"', '"Next workspace" shortcut'],
		'KeySysWorkspacePrevTakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+Left"', '"Take window to previous workspace" shortcut'],
		'KeySysWorkspaceNextTakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+Right"', '"Take window to next workspace" shortcut'],
		'KeySysWorkspace1': [KEYSTROKE, '"Alt+Ctrl+1"', '"Workspace 1" shortcut'],
		'KeySysWorkspace2': [KEYSTROKE, '"Alt+Ctrl+2"', '"Workspace 2" shortcut'],
		'KeySysWorkspace3': [KEYSTROKE, '"Alt+Ctrl+3"', '"Workspace 3" shortcut'],
		'KeySysWorkspace4': [KEYSTROKE, '"Alt+Ctrl+4"', '"Workspace 4" shortcut'],
		'KeySysWorkspace5': [KEYSTROKE, '"Alt+Ctrl+5"', '"Workspace 5" shortcut'],
		'KeySysWorkspace6': [KEYSTROKE, '"Alt+Ctrl+6"', '"Workspace 6" shortcut'],
		'KeySysWorkspace7': [KEYSTROKE, '"Alt+Ctrl+7"', '"Workspace 7" shortcut'],
		'KeySysWorkspace8': [KEYSTROKE, '"Alt+Ctrl+8"', '"Workspace 8" shortcut'],
		'KeySysWorkspace9': [KEYSTROKE, '"Alt+Ctrl+9"', '"Workspace 9" shortcut'],
		'KeySysWorkspace10': [KEYSTROKE, '"Alt+Ctrl+0"', '"Workspace 10" shortcut'],
                'KeySysWorkspace11': [KEYSTROKE, '""', '"Workspace 11" shortcut'],
                'KeySysWorkspace12': [KEYSTROKE, '""', '"Workspace 12" shortcut'],
		'KeySysWorkspace1TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+1"', '"Take window to workspace 1" shortcut'],
		'KeySysWorkspace2TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+2"', '"Take window to workspace 2" shortcut'],
		'KeySysWorkspace3TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+3"', '"Take window to workspace 3" shortcut'],
		'KeySysWorkspace4TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+4"', '"Take window to workspace 4" shortcut'],
		'KeySysWorkspace5TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+5"', '"Take window to workspace 5" shortcut'],
		'KeySysWorkspace6TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+6"', '"Take window to workspace 6" shortcut'],
		'KeySysWorkspace7TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+7"', '"Take window to workspace 7" shortcut'],
		'KeySysWorkspace8TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+8"', '"Take window to workspace 8" shortcut'],
		'KeySysWorkspace9TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+9"', '"Take window to workspace 9" shortcut'],
		'KeySysWorkspace10TakeWin': [KEYSTROKE, '"Alt+Ctrl+Shift+0"', '"Take window to workspace 10" shortcut'],
                'KeySysWorkspace11TakeWin': [KEYSTROKE, '""', '"Take window to workspace 11" shortcut'],
                'KeySysWorkspace12TakeWin': [KEYSTROKE, '""', '"Take window to workspace 12" shortcut'],
		'WorkspaceNames': [MULTI, '" 1 ", " 2 ", " 3 ", " 4 "', 'Names of the Workspaces', 12],

		# added 1.26.2003
		'ColorNormalWorkspaceButtonText': [COLOR, '"rgb:00/00/00"', 'Color of normal workspace button text'],
		'ColorActiveWorkspaceButtonText': [COLOR, '"rgb:00/00/EE"', 'Color of active workspace button text'],
		'ColorNormalWorkspaceButton': [COLOR, '"rgb:C0/C0/C0"', 'Color of normal workspace button'],
		'ColorActiveWorkspaceButton': [COLOR, '"rgb:A0/A0/A0"', 'Color of active workspace button'],
	}
		

########################## ORDER ########################

# This list defines the order in which options will be output to the
# '.icewm/preferences' file.

##  NEW ADDITION - 1.26.2003  - 'ORDER' is now based on the logic arrangement of the TABS....see below
## THIS will help the order of the options saved in the preferences file to directly map over to the order 
## of stuff on the tabs

ORDER=[]  # initialize an empty list instead



########################## TABS ########################


# This list controls how the various configuration options are distributed
# on the tabs of the note book.  It is a list of two item sublists.  Each of
# these sublists contains the label of a tab and a list of the configuration
# options associated with that tab.  
TABS = [

		[_('Windows'),
		        [
			'ManualPlacement',
			'SmartPlacement',
			'ShapesProtectClientWindow',
			'AllowFullscreen',

			'LimitByDockLayer',
			'CenterMaximizedWindows',
			## DEPRECATED ##   'ConsiderHBorder',
			## DEPRECATED ##   'ConsiderVBorder',
			'RaiseOnFocus',
			'RaiseOnClickClient',
			'RaiseOnClickTitleBar',
			'RaiseOnClickButton',
			'RaiseOnClickFrame',
			'PassFirstClickToClient',

			# added 1.26.2003 - new focus stuff
		        'FocusOnClickClient',
			'ClickToFocus',
			'FocusOnMap',
			'FocusOnAppRaise',
			'FocusChangesWorkspace',
			'LowerOnClickWhenRaised',
			'ButtonRaiseMask',

			'LimitSize',
			'LimitPosition',
			## DEPRECATED ##   'SizeMaximized',
			'ShowMoveSizeStatus',
		'moveSizeFontName',
			'OpaqueMove',
			'OpaqueResize',
			'AutoRaise',
			'SnapMove',
			'ClientWindowMouseActions',
			'AutoRaiseDelay',		
			'EdgeResistance',
			'SnapDistance',


			'BorderSizeX',
			'BorderSizeY',
			'CornerSizeX',
			'CornerSizeY',
			'ColorActiveBorder',
			'ColorNormalBorder',
			'MinimizedWindowFontName',
			'ColorNormalMinimizedWindow',
			'ColorNormalMinimizedWindowText',
			'ColorActiveMinimizedWindow',
			'ColorActiveMinimizedWindowText',
			'ColorMoveSizeStatus',
			'ColorMoveSizeStatusText',
			]],


		[_('Quick Switch'),
		        [
			'QuickSwitch',
			'QuickSwitchToMinimized',
			'QuickSwitchToHidden',
			'QuickSwitchToAllWorkspaces',
			'QuickSwitchGroupWorkspaces',
			# added 1.25.2003
			'QuickSwitchSmallWindow',
			'QuickSwitchFillSelection',
			'QuickSwitchAllIcons',
			'QuickSwitchHugeIcon',
			'QuickSwitchTextFirst',
			'QuickSwitchIconBorder',
			'QuickSwitchIconMargin',
			'QuickSwitchHorzMargin',
			'QuickSwitchVertMargin',
			'QuickSwitchSeparatorSize',
			'QuickSwitchFontName',
			'ColorQuickSwitch',
			'ColorQuickSwitchText',
			'ColorQuickSwitchActive',

		        ]],


		[_('Dialogs'),
		        [
			'DlgBorderSizeX',
			'DlgBorderSizeY',
			'MsgBoxDefaultAction',
			'CenterTransientsOnOwner',
			'FocusOnMapTransient',
			'FocusOnMapTransientActive',
			'NormalButtonFontName',
			'ActiveButtonFontName',
			'ListBoxFontName',
			'LabelFontName',
			'ColorDialog',
			'ColorListBox',
			'ColorListBoxText',
			'ColorListBoxSelection',
			'ColorListBoxSelectionText',
			'ColorLabel',
			'ColorLabelText',
			'ColorNormalButton',
			'ColorNormalButtonText',
			'ColorActiveButton',
			'ColorActiveButtonText',
			]],

		[_('Menus'),
			[
			'AutoReloadMenus',
			'ShowMenuButtonIcon',
			'MenuFontName',
			'ColorNormalMenu',
			'ColorActiveMenuItem',
			'ColorActiveMenuItemText',
			'ColorNormalMenuItemText',
			'ColorDisabledMenuItemText',

			'ShowThemesMenu',

			# NEW MENU Stuff - added 1.26.2003
			'ShowHelp',
			'ShowLogoutMenu',
			'ShowProgramsMenu',
			'ShowRun',
			'ShowLogoutSubMenu',
			'ShowWindowList',
			'ShowAbout',
			'DontRotateMenuPointer',
			'ColorDisabledMenuItemShadow',
			'MenuMaximalWidth',

			'MenuActivateDelay',
			'SubmenuMenuActivateDelay',
			'ReplayMenuCancelClick',
			'MenuMouseTracking',
			'ShowPopupsAbovePointer',
			'RunCommand',
			'OpenCommand',
			'LogoutCommand',
			'LogoutCancelCommand',
			]],
		[_('Task Bar'),
			[
			'ShowTaskBar',
			'TaskBarAtTop',
			'TaskBarAutoHide',
			'AutoHideDelay',	

			# added 1.25.2003
			'TaskBarShowWindowIcons',
			'TaskBarShowShowDesktopButton',
			'TaskBarKeepBelow',
			'TrayShowAllWindows',
			'TaskBarShowTray',
			'TrayDrawBevel',
			'TaskBarLaunchOnSingleClick',

			'TaskBarShowWindows',
			'TaskBarShowAllWindows',
			'TaskBarShowStartMenu',
			'TaskBarShowWindowListMenu',
			'TaskBarDoubleHeight',
			'NormalTaskBarFontName',
			'ActiveTaskBarFontName',
			'ColorDefaultTaskBar',
			'ColorNormalTaskBarApp',
			'ColorNormalTaskBarAppText',
			'ColorActiveTaskBarApp',
			'ColorActiveTaskBarAppText',
			'ColorMinimizedTaskBarApp',
			'ColorMinimizedTaskBarAppText',
			'ColorInvisibleTaskBarApp',
			'ColorInvisibleTaskBarAppText',

			# added 1.26.2003
			'ToolButtonFontName',
			'ColorToolButton',
			'ColorToolButtonText',

		'FocusRequestFlashTime',
			]],

		[_('Task Bar Applets'),
			[
			'TaskBarShowClock',
			'TaskBarClockLeds',
			'ColorClock',
			'ColorClockText',
			'ClockCommand',
			'ClockFontName',
			'ClockClassHint',
			'TimeFormat',
			'DateFormat',
			'TimeFormatAlt',

			'TaskBarShowMailboxStatus',
			'TaskBarMailboxStatusBeepOnNewMail',
			'TaskBarMailboxStatusCountMessages',
			'MailCheckDelay',
			'MailCommand',
			'NewMailCommand',
			'MailBoxPath',
			'MailClassHint',

			'TaskBarShowCPUStatus',
			'TaskBarCPUSamples',
			'ColorCPUStatusUser',
			'ColorCPUStatusSystem',
			'ColorCPUStatusNice',
			'ColorCPUStatusIdle',
			'CPUStatusCommand',
			'CPUStatusClassHint',

			'TaskBarShowNetStatus',
			'NetworkStatusDevice',
			'ColorNetSend',
			'ColorNetReceive',
			'ColorNetIdle',
			'NetStatusCommand',
			'NetStatusClassHint',

			'TaskBarShowAPMTime',		
			'TaskBarShowAPMStatus',	
			'ColorApm',
			'ApmFontName',
			'ColorApmText',
			'AcpiIgnoreBatteries',
			]],

		[_('Scroll Bars'),
			[
			# NEW MENU Stuff - added 1.26.2003 - scrollbars
			'ScrollBarX',
			'ScrollBarY',
			'ScrollBarDelay',
			'ScrollBarStartDelay',
			'AutoScrollDelay',
			'AutoScrollStartDelay',
			'ColorScrollBar',
			'ColorScrollBarArrow',
			'ColorScrollBarSlider',
			'ColorScrollBarButton',
			'ColorScrollBarButtonArrow',
			'ColorScrollBarInactiveArrow',
			]],

		[_('Tool Tips'),
			[	
			'ToolTipDelay',
                        'ToolTipTime',
			'ToolTipFontName',
			'ColorToolTip',
			'ColorToolTipText',
			]],
		[_('Mouse'),
			[
			'ClickMotionDistance',
			'DelayPointerFocus',
			'StrongPointerFocus',
			'PointerColormap',
			'EdgeSwitch',
			'UseMouseWheel',
			'WarpPointer',
			'ClickMotionDelay',
			'MultiClickTime',
			'PointerFocusDelay',
			# added 1.26.2003 - new behavior stuff
			'ContinuousEdgeSwitch',
			'HorizontalEdgeSwitch',
			'VerticalEdgeSwitch',
			'UseRootButtons',
			'DesktopWinMenuButton',
			'DesktopWinListButton',
			'DesktopMenuButton',
			]],

		[_('Title Bars'),
			[
			'TitleButtonsSupported',
			'TitleButtonsLeft',
			'TitleButtonsRight',	
			'TitleBarHeight',
			'TitleFontName',
			'ColorActiveTitleBar',
			'ColorNormalTitleBar',
			'ColorActiveTitleBarText',
			'ColorNormalTitleBarText',

			# NEW Stuff - added 1.26.2003 - title bars
			'ColorActiveTitleBarShadow',
			'ColorNormalTitleBarShadow',
			'ColorNormalTitleButton',
			'ColorNormalTitleButtonText',
			'TitleBarJoinRight',
			'TitleBarJoinLeft',
			'TitleBarJustify',
			'TitleBarHorzOffset',
			'TitleBarVertOffset',

			'TitleBarMaximizeButton',
			'TitleBarRollupButton',		
			## DEPRECATED ## 'TitleBarCentered',
			]],
		[_('Miscellaneous'),
			[
			'IconPath',
			'KDEDataDir',
			'AutoDetectGNOME',
			'DisableImlibCaches',
			'XFreeType',
			'DoubleBuffer',
			'XineramaPrimaryScreen',
			'ConfirmLogout',
			'LockCommand',
			'TerminalCommand',
			'RebootCommand',
			'ShutdownCommand',
                     'MultiByte',
			'FxFontName',

		'MoveSizeInterior',
		'MoveSizeDimensionLines',
		'MoveSizeGaugeLines',
		'MoveSizeDimensionLabels',
		'MoveSizeGeometryLabels',
			]],

		[_('Themes'),
			[
			'Theme',
			'ThemeAuthor',
			'ThemeDescription',
			'Gradients'
			]],

		[_('Address Bar'),
			[
			# added 6.16.2003 - new in icewm 1.2.8, but what's the difference 
			# 'EnableAddressBar' and 'ShowAddressBar'??
			'EnableAddressBar',

			# added 1.26.2003
			'ShowAddressBar',
			'InputFontName',
			'ColorInput',
			'ColorInputText',
			'ColorInputSelection',
			'ColorInputSelectionText',
			'AddressBarCommand',
			]],

		[_('Desktop'),
			[
			'DesktopBackgroundCenter',
			'DesktopBackgroundScaled',
			'DesktopBackgroundColor',
			'DesktopBackgroundImage',
			# NEW Stuff - added 1.26.2003 - desktop
			'SupportSemitransparency',
			'DesktopTransparencyColor',
			'DesktopTransparencyImage',
			'GrabRootWindow',
			'MinimizeToDesktop',
			]],
		[_('Key Bindings'),
			[
			'Win95Keys',

			# replaces deprecated 'ModMetaIsCtrlAlt', 6.16.2003, icewm 1.2.8+
			'ModSuperIsCtrlAlt',  

			'KeyWinRaise',
			'KeyWinOccupyAll',
			'KeyWinLower',
			'KeyWinClose',
			'KeyWinRestore',
			'KeyWinPrev',
			'KeyWinNext',
			'KeyWinMove',
			'KeyWinSize',
			'KeyWinMinimize',
			'KeyWinMaximize',
			'KeyWinMaximizeVert',
			'KeyWinHide',
			'KeyWinRollup',
			'KeyWinMenu',
			'KeySysSwitchNext',
			'KeySysSwitchLast',
			'KeySysWinNext',
			'KeySysWinPrev',
			'KeySysWinMenu',
			'KeySysDialog',
			'KeySysMenu',
			#  'KeySysRun', # disabled, not supported in icewm 1.2.8 - 6.16.2003
			'KeySysWindowList',
			'KeySysAddressBar',


			#NEW KEYSTROKES - added 1.26.2003
			'KeyWinFullscreen',
			'KeySysUndoArrange',
			'KeySysTileHorizontal',
			'KeySysTileVertical',
			'KeySysArrange',
			'KeySysArrangeIcons',
			'KeySysMinimizeAll',
			'KeySysWindowList',
			'KeySysWinListMenu',
			'KeySysCascade',
			'KeySysHideAll',
			'KeySysWorkspaceLastTakeWin',
			'KeySysWorkspaceLast',

			'KeySysWorkspacePrev',
			'KeySysWorkspaceNext',
			'KeySysWorkspacePrevTakeWin',
			'KeySysWorkspaceNextTakeWin',
			'KeySysWorkspace1',
			'KeySysWorkspace2',
			'KeySysWorkspace3',
			'KeySysWorkspace4',
			'KeySysWorkspace5',
			'KeySysWorkspace6',
			'KeySysWorkspace7',
			'KeySysWorkspace8',
			'KeySysWorkspace9',
			'KeySysWorkspace10',
			'KeySysWorkspace11',
			'KeySysWorkspace12',
			'KeySysWorkspace1TakeWin',
			'KeySysWorkspace2TakeWin',
			'KeySysWorkspace3TakeWin',
			'KeySysWorkspace4TakeWin',
			'KeySysWorkspace5TakeWin',
			'KeySysWorkspace6TakeWin',
			'KeySysWorkspace7TakeWin',
			'KeySysWorkspace8TakeWin',
			'KeySysWorkspace9TakeWin',
			'KeySysWorkspace10TakeWin',
			'KeySysWorkspace11TakeWin',
			'KeySysWorkspace12TakeWin'
			]],
		[_('Workspaces'),
			[
			'TaskBarShowWorkspaces',
			'TaskBarWorkspacesLeft',
			'WorkspaceNames',
			# added 1.26.2003
			'ColorNormalWorkspaceButtonText',
			'ColorActiveWorkspaceButtonText',
			'ColorNormalWorkspaceButton',
			'ColorActiveWorkspaceButton',
			'NormalWorkspaceFontName',
			'ActiveWorkspaceFontName',
			'ShowWorkspaceStatus',
			'StatusFontName',
			'WorkspaceStatusTime',
			'EdgeSwitchDelay',
			]]
	]

## added 1.27.2003 - a list of tab names
TABS_NAMES=[]
for ii in TABS:
	TABS_NAMES.append(ii[0])

## NEW MORE LOGICAL 'ORDER' mapping for preferences file - added 1.26.2003
for ii in TABS:
	ilist=ii[1]
	for mj in ilist:
		ORDER.append(mj)

#print str(ORDER[0:20])

# added 5.10.2003 - basic search functionality
icepref_search.TABS=TABS
icepref_search.DEFAULTS=DEFAULTS
	
############################################################################
# Classes used in the general IcePref user interface
#
# These are placed at the beginning so that they may be inherited from by
# all other classes
############################################################################

## added 2.23.2003 - break long 'title' strings
def breakTitle(somestr,sstopper=30):
	stopper=sstopper
	if len(somestr)<stopper+1: return somestr
	scut=""
	scutter=0
	while scutter<len(somestr):
		if somestr.find(" ",scutter+stopper)==-1: part=somestr[scutter:len(somestr)].strip()
		else: part=somestr[scutter:somestr.find(" ",scutter+stopper)].strip()
		if len(part)==0: break
		#print str(scutter)
		if len(scut)>0: scut=scut+"\n"+part
		else: scut=part
		if somestr.find(" ",scutter+stopper)==-1: break
		scutter=somestr.find(" ",scutter+stopper)+1
	return scut
		
# This class defines the standard style of labels used in many other classes
# of IcePref

class IceLabel(Label):
	def __init__(self, title,sstopper=30):
		Label.__init__(self, breakTitle(title,sstopper))
		self.set_line_wrap(1)
		self.set_alignment(JUSTIFY_LEFT, 0.5)
		self.set_padding(2,2)
		
# This is a somewhat generic class for dialogs
 
class IceDialog(Window):
	def __init__(self, titlebar, title):
		Window.__init__(self)
		self.set_title(str(titlebar))
		set_basic_window_icon(self)
		self.set_modal(TRUE)
		self.init_widgets(title)
		self.init_buttons()
		self.show()
	
	def init_widgets(self, title):
		vbox = VBox(spacing = SP)
		vbox.set_border_width(BD)
		self.add(vbox)
		vbox.show()

		label = IceLabel(title)
		vbox.pack_start(label)
		label.show()

		self.bbox = HButtonBox()
		vbox.pack_start(self.bbox)
		self.bbox.show()

	def init_buttons(self):
		self.ok_button = Button(_('Ok'))
		self.ok_button.grab_focus()
		self.ok_button.connect('clicked', self.button_cb, 1)
		self.bbox.pack_start(self.ok_button)
		self.ok_button.show()
		
	def button_cb(self, object=None, data=None):
		ret = data
		self.hide()
		self.destroy()

##############################################################################
# The configuration option classes
#
# These classes are designed to implement the configuration user interface in
# generic way.  All of them (at least all of them that are directly used
# by the Application class) have the methods set_value and get_value, the
# function of which should be self evident.  To facilitate interaction with
# the text configuration file, set_value always takes a string argument and
# get_value always returns a string value.
##############################################################################

# The Entry class describes the text entries.
# title = the text of the label
# value = the intial value
		
class IceEntry(VBox):
	def __init__(self, title='', value=''):
		VBox.__init__(self, spacing=SP)
		self.set_border_width(BD)
		self.init_widgets(title)
		self.set_value(value)
		self.show_all()
		
	def init_widgets(self, title):
		label=IceLabel(title)
		label.show()
		self.pack_start(label, FALSE, FALSE)
		self.entry = Entry()
		self.entry.show()
		self.pack_start(self.entry, 0, 0)
		self.pack_start(Label(""),1,1,0)
		
	def set_value(self, value):
		#value = value[1 : len(value) - 1]  # changed 1.27.2003 - was buggy and could cause bad parsing
		value=to_utf8(value.replace("\"",""))
		self.entry.set_text(value)
		
	def get_value(self):
		value = self.entry.get_text()
		value = '"' +remove_utf8( value) + '"'
		return value
		
# The Toggled class describes the check buttons (for boolean options).
# title = text of the label
# value = initial value
		
class IceToggled(VBox):
	def __init__(self, title='', value=''):
		VBox.__init__(self, spacing=SP)
		self.set_border_width(BD)
		self.init_widgets(title)
		self.set_value(value)
		self.show_all()
		
	def init_widgets(self, title):
		self.button = CheckButton()  # changes made here - 1.26.2003
		try: # added 2.23.2003 - cleaner toggle buttons
			pop=IceLabel(title)
			hb=HBox(0,0)
			hb.set_border_width(6)
			hb.pack_start(pop,1,1,0)
			self.button.add(hb)
			hb.show_all()
		except:
			pass
		self.button.show()
		self.pack_start(self.button, FALSE, FALSE, 0)
		self.pack_start(Label(""),1,1,0)
		
	def set_value(self, value):
		self.button.set_active(eval(value))
		
	def get_value(self):
		value = int(self.button.get_active())
		return str(value)

# The Range class describes the range widget.
# Currently, it includes both a GtkAdjustment
# widget and a spinbutton. This could, of
# course, be changed if it is found to be
# unsatisfactory.  title = text of the label
# min = bottom of the allowed range max = top
# of the allowed range value = initial value

class IceRange(VBox):
	def __init__(self, title='', min=0, max=100, value=0):
		VBox.__init__(self, spacing=SP)
		self.set_border_width(BD)
		self.init_widgets(title, min, max)
		self.set_value(value)
		self.show()
		
	def init_widgets(self, title, min, max):
		hbox = HBox(FALSE, SP)
		hbox.set_border_width(BD)
		hbox.show()
		self.pack_start(hbox, FALSE, FALSE, 0)
		label = IceLabel(title)
		label.show()
		hbox.pack_start(label, FALSE, FALSE, 0)
		adj = Adjustment(lower=min, upper=max, step_incr=1)
		self.spin = SpinButton(adj)
		self.spin.set_digits(0)
		self.spin.show()
		hbox.pack_end(self.spin, FALSE, FALSE, 0)
		scale = HScale(adj)
		scale.set_draw_value(FALSE)
		scale.show()
		self.pack_start(scale, FALSE, FALSE, 0)
		
	def set_value(self, value):
		self.spin.set_value(eval(value))
		
	def get_value(self):
		ret = self.spin.get_value_as_int()
		return str(ret)

# The keystroke may not present the best
# possible way to configure key strokes in a
# window manager, but it seems to work--for
# that and only that.

class Keystroke(VBox):
	def __init__(self, title, value):
		VBox.__init__(self)
		self.set_border_width(BD)
		self.init_constants()
		self.init_widgets(title)
		self.set_value(value)
		self.show()
		
	def init_constants(self):
		self.mods=[
					['Alt', 'Alt+'],
					['Ctrl', 'Ctrl+'],
					['Shift', 'Shift+']
					
				]
		
	def init_widgets(self, title):
		label = IceLabel(title)
		self.pack_start(label)
		label.show()
		
		hbox = HBox()
		self.pack_start(hbox)
		hbox.show()
		
		self.mod_buttons = []
		
		for item in self.mods:
			button = ToggleButton(item[0])
			hbox.pack_start(button)
			self.mod_buttons.append(button)
			button.show()
			
		self.entry = Entry()
		hbox.pack_start(self.entry)
		self.entry.show()
		
	def set_value(self, value):
		value = replace(value, '"', '')
		for i in range(len(self.mods)):
			if count(value, self.mods[i][1]) == 1:
				self.mod_buttons[i].set_active(TRUE)
				value = replace(value, self.mods[i][1], '')
			else:
				self.mod_buttons[i].set_active(FALSE)
				value = replace(value, self.mods[i][1], '')
				
		self.entry.set_text(to_utf8(value))
		
	def get_value(self):
		value = ''
		
		for i in range(len(self.mods)):
			if self.mod_buttons[i].get_active():
				value = value + self.mods[i][1]
		
		entry_text = self.entry.get_text()
		value = '"' + value + entry_text + '"'
		
		return remove_utf8(value)


def setDrag(*args): # drag-n-drop support, added 2.23.2003
	drago=args
	if len(drago)<7: 
		args[0].drag_highlight()
		args[0].grab_focus()
	else: 
		#print str(drago[4].data)  # file:/root/something.txt
		try:
			imfile=""+str(drago[4].data).replace("\r\n","").replace("\x00","").replace("file:","")
			#imf=imfile[imfile.rfind(os.sep)+1:len(imfile)].strip()
			#imdir=imfile[0:imfile.rfind(os.sep)+1].strip()
			global im_file_entry
			if not im_file_entry==None: im_file_entry.entry.set_text(imfile)
			global im_file_prev
			if not im_file_prev==None: im_file_prev.update_image(imfile)
		except: 
			pass
		args[0].drag_unhighlight()


## Added 1.27.2003 - a simple image preview for the wallpaper and theme, using GdkPixbuf

class ImagePreviewer:
	def __init__(self,warn_type=0,restart_cmd=None,save_cmd=None):
		self.savec=save_cmd
		self.restartc=restart_cmd
		self.scbox=HBox(0,0)
		self.sc=ScrolledWindow()
		self.gl=Layout()
		self.no_scale=0
		self.sc.set_size_request(240,190)
		self.gl.set_size(400,300)
		self.sc.add(self.gl)
		self.current_image=None
		self.scbox.pack_start(self.sc,0,0,0)
		if warn_type==1:  #Background Image
			self.scbox.set_spacing(4)
			self.scbox.pack_start(Label(_("WARNING:\nNewer IceWM themes often\noverride this wallpaper setting.")),0,0,0)
			addDragSupport(self.sc,setDrag)
		if warn_type==2:  # Theme previewer
			self.scbox.set_spacing(7)
			svert=VBox(0,0)
			bapply=getPixmapButton(None, STOCK_APPLY ,_(" Apply Theme Now! "))
			TIPS.set_tip(bapply,_(" Apply Theme Now! "))
			bgen=getPixmapButton(None, STOCK_NEW , _(" Create Theme Preview... "))
			TIPS.set_tip(bgen,_(" Create Theme Preview... "))
			babout=getPixmapButton(None, STOCK_DIALOG_INFO ,_(" About Theme Previews... "))
			TIPS.set_tip(babout,_(" About Theme Previews... "))
			svert.pack_start(bapply,0,0,0)
			svert.pack_start(Label("  "),1,1,0)
			svert.pack_start(bgen,0,0,0)
			svert.pack_start(Label("  "),1,1,0)
			svert.pack_start(babout,0,0,0)
			if (save_cmd==None) or (restart_cmd==None): bapply.set_sensitive(0)
			else: bapply.connect("clicked",self.applyTheme)
			babout.connect("clicked",self.aboutThemes)
			bgen.connect("clicked",self.generatePreview)
			self.scbox.pack_start(svert,0,0,0)
		#self.scbox.pack_start(Label("          "),1,1,0)
		self.scbox.pack_start(Label("       "),0,0,0)

		# added 2.12.2003 - moved theme author and description to the right of the preview box
		self.entry_box=VBox(0,0)
		self.entry_box.set_spacing(10)
		self.scbox.pack_start(self.entry_box,1,1,0)
		self.scbox.show_all()

	def generatePreview(self,*args):  # added 3.14.2003 - auto generation of theme preview.jpg files 
		try:
			if os.path.exists(self.current_image):
				if not msg_confirm("IcePref2",_("The image")+":\n\n"+self.current_image+"\n\n"+_("already exists.")+"\n"+_("Do you wish to replace it?"))==1: return
		except:
			pass
		self.applyTheme()
		msg_info("IcePref2",_("The theme has been applied,\nand IceWM is quickly restarting.\nWhen it has restarted, click 'OK'.\nThis may take a moment."))
		timeout_add(1500,self.generatePreviewStep2)

	def generatePreviewStep2(self,*args):
		try:
			f=os.popen("import -window root -resize 200x200 "+self.current_image.replace(" ","\\ "))
			f.readlines()
			if not os.path.exists(self.current_image): raise TypeError
			self.update_image(self.current_image)
		except:
			IceDialog("IcePref2",_("A theme preview image could not be created. This features requires the 'import' binary from ImageMagick to be on your path."))	

			# NOTE: We must leave the above message as using 'Dialog' instead of one of the common 
			# dialogs, because we need a Dialog box that doesn't call 'mainloop' while running in a gtk 'timeout'.
			# Using one of the 'common' dialogs will cause a bug where IcePref2 hangs.
		return 0

	def applyTheme(self,*args):
		self.savec("nowarn")
		self.restartc()

	def aboutThemes(self,*args):
		win = commonAbout(_('About Theme Previews'), _("Theme previewing is a new feature of IcePref2 (an updated version of IcePref, improved by Erica Andrews [PhrozenSmoke [at] yahoo.com]).\n\nTheme previewing requires a JPEG image named $preview.jpg$ in each theme's directory. If your theme is in /usr/X11R6/lib/X11/icewm/themes/nice/, then your preview JPEG should be at /usr/X11R6/lib/X11/icewm/themes/nice/preview.jpg (the name MUST be $preview.jpg$). The image should be no larger in size than 200x200 pixels.\n\nThere are three ways to get $preview$ images for your themes:\n[1] Download the package of (some) theme previews from icesoundmanager.sourceforge.net\n[2] Use the theme thumbnails at  http://themes.freshmeat.net/browse/925/?topic_id=925\n[3] Make the preview images yourself with scaled screenshots.\n\nTheme authors are encouraged to add $preview.jpg$ preview files to their distributed theme packages.".replace(" [at] ","@") ).replace("$","\"")   , 0  , "icepref2.png","\n")

	def update_image(self,image_file):
		for ii in self.gl.get_children():
			try:
				self.gl.remove(ii)
				ii.destroy()
				ii.unmap()
			except:
				pass
		try:
			self.current_image=str(image_file).strip()
			if not os.path.exists(self.current_image): return
			if os.path.isdir(self.current_image): return
			pixtemp=loadImage(self.current_image)
			dims=[pixtemp.get_pixbuf().get_width(), pixtemp.get_pixbuf().get_height()]
			aspect=float(dims[0])/float(dims[1])
			sug_x=220
			sug_y=int( math.floor(sug_x/aspect)  )
			if self.no_scale==0:
				if (dims[0]>sug_x) or (dims[1]>sug_y):
					myim_real=loadScaledImage(self.current_image, sug_x,sug_y)		
				else: myim_real=pixtemp
			else: myim_real=pixtemp
			self.gl.put(myim_real,3,2)
			self.gl.set_size_request(myim_real.get_size_request()[0]+15,myim_real.get_size_request()[1]+15)
		except:
			lab=Label(_(" SORRY:\n Image could not\n be previewed."))
			lab.show()
			self.gl.put(lab,0,0)
			self.gl.set_size(220,180)

# The ButtonEntry class is a relatively generic class for metawidgets that
# contain both a text entry and a button to call up a dialog box.  Color,
# Font, and File all inherit from this class.  Path inherits from File.
# title = label text
# value = initial value

class ButtonEntry(VBox):
	def __init__(self, title='', value='',image_previewer=None):
		VBox.__init__(self, FALSE, SP)
		self.set_border_width(BD)
		self.INITVALUE= value[1 : len(value) - 1]
		self.init_widgets(title)
		self.iprev=image_previewer
		self.set_value(value)
		self.show_all()
		
	def init_widgets(self, title):
		label = IceLabel(title)
		label.show()
		self.pack_start(label, FALSE, FALSE, 0)
		
		hbox = HBox(FALSE, SP)
		hbox.show()
		self.pack_start(hbox, FALSE, FALSE, 0)
		
		self.entry = Entry()
		self.entry.show()
		hbox.pack_start(self.entry, TRUE, TRUE, 0)


		## added 2.23.2003 - try to load a prettier select button
		button=getIconButton(None, STOCK_OPEN ,_("Select"))
		TIPS.set_tip(button,_("Select"))
		self.button=button
		button.connect('clicked', self.select)
		button.show_all()
		hbox.pack_start(button, FALSE, FALSE, 0)
		self.hbox=hbox
		
	def set_value(self, value):
		value = value[1 : len(value) - 1]
		self.entry.set_text(to_utf8(value))
		if not self.iprev==None: self.iprev.update_image(value)
		
	def get_value(self):
		value = '"' + self.entry.get_text() + '"'
		return remove_utf8(value)
		
	def cancel(self, data=None):
		self.win.hide()
		self.win.destroy()
		
# The Color class is used for configuring (obviously) options which require
# the rgb value for a color.  It is a derivative of the ButtonEntry class and
# therefore accepts the same options.	
				
class IceColor(ButtonEntry):
	def select(self, data=None):
		value = self.entry.get_text()
		self.win = ColorSelectionDialog(_('Select Color'))
		#self.win.colorsel.set_opacity(FALSE)
		#self.win.colorsel.set_update_policy(UPDATE_CONTINUOUS)
		self.win.set_position(WIN_POS_MOUSE)
		self.win.ok_button.connect('clicked', self.ok)
		self.win.cancel_button.connect('clicked', self.cancel)
		self.win.help_button.destroy()
		if value != '':
			r=g=b=0
			try:
            			r = atoi(value[4:6], 16) << 8
            			g = atoi(value[7:9], 16) << 8
            			b = atoi(value[10:12], 16) << 8
			except:
				pass
            		colour = self.win.get_colormap().alloc_color(r, g, b)
            		self.win.colorsel.set_current_color(colour)
		self.win.set_modal(TRUE)
		self.win.show()

	def init_widgets(self, title):
		label = IceLabel(title)
		label.show()
		self.pack_start(label, FALSE, FALSE, 0)		
		hbox = HBox(FALSE, SP)
		hbox.show()
		self.pack_start(hbox, FALSE, FALSE, 0)		
		self.entry = Entry()
		self.entry.show()
		hbox.pack_start(self.entry, TRUE, TRUE, 0)
		self.hbox=hbox

		button=Button()
		TIPS.set_tip(button,_("Select"))
		self.button=button
		button.set_relief(2)
		button.connect('clicked', self.select)
		self.gc=None
		self.color_i16=[0,0,0]
		value = self.INITVALUE
        	if value != '':
           		r = atoi(value[4:6], 16)
            		g = atoi(value[7:9], 16)
            		b = atoi(value[10:12], 16)
            		self.color_i16=[r,g,b]
		f=Frame()
		f.set_shadow_type(SHADOW_ETCHED_OUT)
		drawing_area = DrawingArea()
		drawing_area.set_size_request(22, 18)
		drawing_area.show() 
		self.drawing_area=drawing_area
		f.add(drawing_area)
		self.drawwin=drawing_area.window
		drawing_area.connect("expose_event", self.setColor)
		drawing_area.set_events(GDK.EXPOSURE_MASK |
		GDK.LEAVE_NOTIFY_MASK |
		GDK.BUTTON_PRESS_MASK )
		button.add(f)
		button.show()
		hbox.pack_start(button, FALSE, FALSE, 1)
		addDragSupportColor(button)  # added 5.16.2003
		button.set_data("colorbutton",self)  # added 5.16.2003
		self.entry.set_data("colorbutton",self)  # added 5.16.2003
		addDragSupportColor(self.entry)  # added 5.16.2003
		self.hbox.show_all()

	def setColor(self,*args):
	  try:
        	if not self.drawwin: self.drawwin=self.drawing_area.window
       		if not self.gc: self.gc=self.drawwin.new_gc()
       		self.gc.foreground=self.drawwin.get_colormap().alloc_color(self.color_i16[0] << 8,
                                                                   self.color_i16[1] << 8,
                                                                   self.color_i16[2] << 8)
        	width, height = self.drawwin.get_size()
        	self.drawwin.draw_rectangle(self.gc,gtk.TRUE,0,0,width,height)
	  except:
		pass

	def set_value(self, value):
		value = value[1 : len(value) - 1]
		self.entry.set_text(to_utf8(value))
        	if value != '':
           		r = atoi(value[4:6], 16)
            		g = atoi(value[7:9], 16)
            		b = atoi(value[10:12], 16)
            		self.color_i16=[r,g,b]
		self.setColor()
        
	def updateColorProperties(self, r, g, b): # new method,functionality separation, 5.16.2003
        	self.color_i16=[r,g,b]
		rstr="%02x" % r
		gstr="%02x" % g
		bstr="%02x" % b
		#print str(self.color_i16)
        	self.entry.set_text("rgb:"+rstr+"/"+gstr+"/"+bstr)
        	self.setColor()
        
	def ok(self, data=None):
	  try:
        	colour = self.win.colorsel.get_current_color()
        	r = colour.red   >> 8
        	g = colour.green >> 8
        	b = colour.blue  >> 8
        	self.win.hide()
        	self.win.destroy()
        	self.updateColorProperties(r,g,b)
	  except:
		pass

# Font class is used (wonder of wonders) to select a font and returns an X
# font descriptor, which coincidentally is just what icewm demands.  It is
# a derivative of the ButtonEntry superclass and takes the same options.
		
class IceFont(ButtonEntry):

	def init_widgets(self, title):
		label = IceLabel(title)
		label.show()
		self.pack_start(label, FALSE, FALSE, 0)
		
		self.sw=ScrolledWindow()
		self.sample = TextView()
		self.sw.add(self.sample)
		self.sample.set_editable(FALSE)
		self.sw.set_size_request(-1,65)
		self.pack_start(self.sw,0,0,0)
		self.sw.show_all()
		self.sample=self.sample.get_buffer()
		
		hbox = HBox(FALSE, SP)
		hbox.show()
		self.pack_start(hbox, FALSE, FALSE, 0)
		self.pack_start(Label(""),1,1,0)
		
		self.entry = Entry()
		#self.entry.connect('changed', self.update)
		self.entry.connect("key-press-event",self.update)
		self.entry.show()
		hbox.pack_start(self.entry, TRUE, TRUE, 0)
		
		## added 2.23.2003 - try to load a prettier select button
		button=getIconButton(None, STOCK_BOLD ,_("Select"))
		TIPS.set_tip(button,_("Select"))
		button.connect('clicked', self.select)
		button.show()
		hbox.pack_start(button, FALSE, FALSE, 0)
		
	def set_value(self, value):
		value = value[1 : len(value) - 1]
		if len(value.split("-"))<9:
			self.entry.set_text(to_utf8(pangoxlfd.pango2XLFD(value)))
		else: 
			self.entry.set_text(to_utf8(value))
		self.set_sample(value)
		
	def set_sample(self, value):
		self.sample.set_text("")
		#self.sample.delete_text(0, length)		
		# The structure catches errors which are caused by invalid
		# font specifications.
		try:
			val=value
			# support legacy fonts like '-adobe-courier-medium-r-*-*-*-140-*-*-*-*-*-*'
			valls=val.split("-")
			if len(valls)>8:
				val=pangoxlfd.XLFD2pango(val)
			# try to create a GdkFont to see if our conversion is valid
			# This catches those stupid pango 'fallback' warnings

			myfontdesc=pango.FontDescription(val)
			if myfontdesc.get_size()> (101 * 1024):
					# Avoid ridiculously huge fonts over 100pts, they can cause crashes
					raise TypeError
			if not GDK.font_from_description(myfontdesc):
					# Avoid fonts that GDK can't even load
					raise TypeError

			text_buffer_insert(self.sample, get_renderable_tab(self.sample,val,COL_BLACK,"iso8859-1"),to_utf8(SAMPLE_TEXT))

		except:
			#print "Invalid: "+val
			#print "Value: "+value
			text_buffer_insert(self.sample, get_renderable_tab(self.sample,"Sans 12",COL_BLACK,"iso8859-1"),to_utf8(ERROR_TEXT))

	def select(self, data=None):
		self.win = FontSelectionDialog(_('Select Font'))
		self.win.set_preview_text(to_utf8(SAMPLE_TEXT))
		self.win.ok_button.connect('clicked', self.ok)
		self.win.cancel_button.connect('clicked', self.cancel)
		value = self.entry.get_text()
		if value !='':
			if len(value.split("-"))>8:
				self.win.fontsel.set_font_name(pangoxlfd.XLFD2pango(value))
			else:
				self.win.fontsel.set_font_name(pangoxlfd.get_valid_pango_font_desc(value))
		self.win.set_modal(TRUE)
		self.win.show()
		
	def ok(self, data=None):
		value = self.win.fontsel.get_font_name()
		self.win.hide()
		self.win.destroy()
		if len(value.split("-"))<9:
			self.entry.set_text(pangoxlfd.pango2XLFD(value))
		else: 
			self.entry.set_text(value)
		self.set_sample(value)
		
	def update(self, widget, event,*args):
		if event.keyval == gtk.keysyms.Return:
			value = self.entry.get_text()
			self.set_sample(value)
		
# The File class is used for options that require a file name and path.  It is
# a derivative of the Button Entry class and takes the same options.
		
class IceFile(ButtonEntry):
		
	def select(self, data=None):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		value = self.entry.get_text()
		if value != '""':
			SET_SELECTED_FILE(value)
		SELECT_A_FILE(self.ok,_("Select a file..."),"icepref","IcePref")
		
	def ok(self, data=None):
		# changed 6.20.2003 -use new common file selection functions in icewmcp_common
		value=GET_SELECTED_FILE()   # from icewmcp_common
		self.entry.set_text(value)
		if not self.iprev==None: self.iprev.update_image(value)


# The class Path is used to configure options that require a path but no file
# name.  It is a derivative of File and accepts the same options.
		
class IcePath(IceFile):
		
	def ok(self, data=None):
		value = self.win.get_filename()
		value = value[: rfind(value, '/') + 1]
		self.win.hide()
		self.win.destroy()
		self.entry.set_text(value)
		
# The Multi class is used to configure options that consist of multiple
# strings in comma seperated lists.  Right now, this is limited to the desktop
# names.
# title = label text
# value = initial value
# num = number of text entries to be displayed
		
class IceMulti(VBox):
	def __init__(self, title, value, num):
		VBox.__init__(self, spacing = SP)
		self.num = num
		self.set_border_width(BD)
		self.init_widgets(title)
		self.set_value(value)
		self.show_all()
		
	def init_widgets(self, title):
		label = IceLabel(title)
		label.show()
		self.pack_start(label,0,0,1)
		self.hb=HBox(0,0)
		self.pack_start(self.hb,1,1,0)
		self.vbox1=VBox(0,0)
		self.hb.pack_start(self.vbox1,1,1,0)
		if self.num>6:
			self.vbox2=VBox(0,0)
			self.hb.set_spacing(8)
			self.hb.pack_start(self.vbox2,1,1,0)
		
		self.entries = []
		vb=self.vbox1
		for i in range(0, self.num):
			entry = Entry()
			entry.show()
			vb.pack_start(entry)
			self.entries.append(entry)
			if self.num>6:
				if i==5:
					vb.pack_start(Label(""),1,1,0)
					vb=self.vbox2
		vb.pack_start(Label(""),1,1,0)
			
	def divide(self, string):
		list = []
		while count(string, '"') > 0:
			f_quote = find(string, '"')
			l_quote = find(string[f_quote + 1 :], '"') + (len(string) - len(string[f_quote + 1:]))
			item = string[f_quote : l_quote + 1]
			string = string[l_quote + 1 :]
			list.append(item)			
		return list
		
	def set_value(self, value):
		for i in range(0, self.num):
			self.entries[i].set_text('')
		values = self.divide(value)
		if len(values) > self.num: values = values[:self.num]
		for i in range(0, len(values)):
			trimmed = values[i][1 : len(values[i]) - 1]
			self.entries[i].set_text(to_utf8(trimmed))
		
	def get_value(self):
		values = []
		for entry in self.entries:
			text = entry.get_text()
			if text != '':
				values.append(text)		
		value = ''	
		for item in values:
			value = value + '"' + item + '"' + ','		
		value = value[:len(value) - 1]
		return remove_utf8(value)

# The ThemeData class, when passed the whole path of a theme, sets its members
# to the values required by the ThemeSel class.

class ThemeData:
	def __init__(self, full_path):
		self.full_path = full_path
		self.init_vars(full_path)

	def init_vars(self, full_path):
		slash_1 = rfind(full_path, '/')
		slash_2 = rfind(full_path[:slash_1], '/')
		self.name = full_path[slash_2 + 1 : slash_1]
		self.theme_file = full_path[slash_1 + 1:]
		self.full_name = self.name + ' (' + self.theme_file + ')'
		self.path = self.name + '/' + self.theme_file
		# added 1.27.2003 - try parsing for theme description and author info
		# default description:  "nice - default"  or "axxrom1.1 - spring", etc
		self.description=""+self.name+" - "+self.theme_file.replace(".theme","").strip()

		# added 2.12.2003 - more descriptive theme names in CLIST
		addon=self.theme_file.replace(".theme","").strip()
		if len(addon)>0:
			if not addon=="default":  self.name=self.name+"  ["+addon+"]"

		self.author="Author Unknown"
		try:
			f=open(full_path)
			flist=f.read().split("\n")[0:15]  # - check the first 15 lines of the theme file for info
			f.close()
			for ii in flist:
				ii=ii.replace("\t"," ")
				if (ii.strip().startswith("ThemeDescription")) and (ii.strip().find("=")>0): 
					td=ii.replace("ThemeDescription","").replace("\"","").replace("\t"," ").replace("\r"," ").replace("=","").strip()
					if len(td)>0: 
						self.description=td
				if (ii.strip().startswith("ThemeAuthor")) and (ii.strip().find("=")>0): 
					td=ii.replace("ThemeAuthor","").replace("\"","").replace("\t"," ").replace("\r"," ").replace("=","").strip()
					if len(td)>0:
						self.author=td
		except:
			pass

# This class creates a CList which can be used to select a theme.  It is quite
# specialized at this point.  Perhaps it could later be generalized to handle
# other options.
		
class ThemeSel(VBox):
	def __init__(self, title='', value='',Image_prev=None):
	    VBox.__init__(self)
	    self.set_border_width(BD)
	    self.fvalue=""
	    self.set_spacing(SP)
	    self.init_theme_list()
	    self.t_map={} # theme name to full path  # added 1.27.2003
	    self.a_map={} # theme name to author # added 1.27.2003
	    self.d_map={}  # theme name to theme description # added 1.27.2003
	    self.author_entry=None # added 1.27.2003
	    self.desc_entry=None # added 1.27.2003
	    self.iprev=Image_prev  # added 1.27.2003
	    self.set_value(value)
	    self.init_widgets(title)
	    self.set_value(value)
	    self.show()
		
	def init_theme_list(self):
	    self.theme_list = []
	    for path in THEME_PATH:
		subdir_list = glob.glob(path)
		self.extract_theme_files(subdir_list)
			
	def extract_theme_files(self, subdir_list):
	    for subdir in subdir_list:
			contents = glob.glob(subdir + '/*.theme')
			if contents != []:
				for file in contents:
					theme = ThemeData(file)
					self.append_theme(theme)
					# self.theme_list.append(theme)
	
	def append_theme(self, theme):
	    in_list = FALSE
	    for entry in self.theme_list:
		if theme.full_name == entry.full_name:
		    in_list = TRUE
	    if not in_list:
		self.theme_list.append(theme)
					
	def set_value(self, value):	    
	    self.value = value[1 : len(value) - 1]
	    if self.value == '':
		self.value = self.theme_list[0].path
	    selval=self.value
	    if self.t_map.has_key(self.value):
		previm=self.t_map[self.value][0:self.t_map[self.value].rfind(os.sep)+1]+"preview.jpg"
	   	if not self.iprev==None: 
			self.iprev.update_image(previm)
	    if self.value.rfind("themes/")>-1:
	    	shortval=self.value[self.value.rfind("themes/")+len("themes/"):]
	    	if self.t_map.has_key(shortval):
			selval=shortval
			previm=self.t_map[shortval][0:self.t_map[shortval].rfind(os.sep)+1]+"preview.jpg"
	   		if not self.iprev==None: 
				self.iprev.update_image(previm)
	    if (self.a_map.has_key(self.value)) :	  
		if not self.author_entry==None:
			self.author_entry.set_value(self.a_map[self.value])
	    if (self.d_map.has_key(self.value)) :	  
		if not self.desc_entry==None:
			self.desc_entry.set_value(self.d_map[self.value])
	    # added 12.2.2003, Erica Andrews - highlight and scroll to the row of the current theme
	    try:
				k=self.t_map.keys()
				k.sort()
				self.CLIST.moveto(k.index(selval),0,0 ,0)
				self.CLIST.select_row(k.index(selval),0)
	    except:
				pass
			
	def get_value(self):
	    if not self.fvalue=='': value = '"' + self.fvalue + '"'
	    else: value = '"' + self.value + '"'
	    return value
	
	def init_widgets(self, title):
		label = Label(_("IceWM Themes"))
		self.pack_start(label)
		label.show()
		
		swin = ScrolledWindow()
		swin.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
		swin.set_size_request(150, 150)
		self.pack_start(swin)
		swin.show()
		
		clist = CList(2, [' '+_('Theme Name')+'               ', ' '+_('File')+'   '])
		clist.set_column_width(0,290)
		clist.connect('select_row', self.clist_cb)
		swin.add(clist)
		clist.show()
		self.CLIST=clist		
		clist.freeze()
		row_count = 0
		for item in self.theme_list:
			row = [item.name, item.full_path]
			clist.append(row)
			clist.set_row_data(row_count, [item.path,item.full_path])
			self.t_map[item.path]=item.full_path
			self.a_map[item.path]=item.author
			self.d_map[item.path]=item.description
			if item.path == self.value:
				clist.select_row(row_count,0)
			row_count = row_count + 1
		clist.sort()
		clist.columns_autosize()
		clist.thaw()
		
	def clist_cb(self, widget, row, col, event):
		self.value = widget.get_row_data(row)[0]
		self.fvalue= widget.get_row_data(row)[1]
		if self.t_map.has_key(self.value):
			previm=self.t_map[self.value][0:self.t_map[self.value].rfind(os.sep)+1]+"preview.jpg"
			#print previm
			if not self.iprev==None: 
				self.iprev.update_image(previm)
		if (self.a_map.has_key(self.value)) :	  
			if not self.author_entry==None:
				self.author_entry.set_value(self.a_map[self.value])
		if (self.d_map.has_key(self.value)) :	  
			if not self.desc_entry==None:
				self.desc_entry.set_value(self.d_map[self.value])

# The OptionMenu class is a generic class for numerically coded options with a small, fixed
# number of possible options.

class IceOptionMenu(VBox):
	def __init__(self, title='', value=''):
		VBox.__init__(self)
		self.set_border_width(BD)
		self.init_widgets(title)
		self.set_value(value)
		self.show()
		
	def init_widgets(self, title):
		label = IceLabel(title)
		self.pack_start(label)
		label.show()
		
		self.option_menu = OptionMenu()
		self.option_menu.set_menu(self.create_menu())
		self.pack_start(self.option_menu)
		self.option_menu.show()
		
	def init_options(self):
		self.options = [['Null', '0']]
		
	def create_menu(self):
		self.init_options()
		menu = Menu()
		group = None
		self.all_items = []			
		for option in self.options:
			menuitem = RadioMenuItem(group, option[0])
			menuitem.connect('activate', self.menu_cb, option[1])
			group = menuitem
			menu.append(menuitem)
			self.all_items.append(menuitem)
			menuitem.show()
			
		return menu
		
	def menu_cb(self, widget, data):
		self.value = str(data)
			
	def set_value(self, value):
		if eval(value) > 7:
			value = str(7)
		if eval(value) < 0:
			value = str(0)
		self.value = value
		for i in range(len(self.options)):
			if value == self.options[i][1]:
				self.all_items[i].set_active(TRUE)
				self.option_menu.set_history(i)
			
	def get_value(self):
		return self.value

# This special class is used to configure options which use a bitmask to control
# the behavior of the three mouse buttons.

class BitMask(IceOptionMenu):   # translations needed!
	def init_options(self):
		self.options = [[_('No mouse buttons'), '0'],
                                [_('First button only'), '1'],
                                [_('Second button only'), '2'],
                                [_('Third button only'), '4'],
                                [_('First and second buttons'), '3'],
                                [_('First and third buttons'), '5'],
                                [_('Second and third buttons'), '6'],
                                [_('All three buttons'), '7']]

# This child of OptionMenu (MouseButton) is used to configure options which call for a particular
# mouse button by number.

class MouseButton(IceOptionMenu):  # translations needed!
	def init_options(self):
		self.options = [[_('No mouse button'), '0'],
					[_('First mouse button'), '1'],
					[_('Second mouse button'), '2'],
					[_('Third mouse button'), '3'],
					[_('Fourth mouse button'), '4'],
					[_('Fifth mouse button'), '5']]

##############################################################################		
# The Application class -- mother of all IcePref classes
#
# The Application class is the main class of this little utility.  It is
# confusing and I don't feel like commenting it right now.
##############################################################################
	
class Application(Window):
	
	def __init__(self, argv):
		Window.__init__(self)
		global APP_WINDOW
		APP_WINDOW=self
		self.set_title('IcePref2')
		set_basic_window_icon(self)
		self.set_position(WIN_POS_CENTER)
		self.set_wmclass("icepref","IcePref")
		self.connect('destroy', mainquit)
		self.determine_os()
		self.init_settings()
		self.find_global_preferences()
		self.find_local_preferences()
		self.get_current_settings()
		
		self.vbox1 = VBox(0,2)
		self.vbox1.set_border_width(0)
		self.vbox = VBox(0,2)
		self.vbox.set_border_width(5)


		#added 1.26.2003
		self.my_tabs={} 

		TABS.sort()
		for tab in TABS:
			if not SHOW_MODULE==None:
				if SHOW_MODULE in TABS_NAMES:
					if str(tab[0])==SHOW_MODULE:
						self.my_tabs[str(tab[0])]=TABS.index(tab)
				else:
					self.my_tabs[str(tab[0])]=TABS.index(tab)
			else:
				self.my_tabs[str(tab[0])]=TABS.index(tab)
		self.init_menu()
		self.widget_dict = {}
		# added 1.27.2003 - try to show a nice logo via GdkPixbuf
		try:
			logoim=loadImage(getBaseDir()+"icepref2.png")
			self.vbox.pack_start(logoim,0,0,1)
		except:
			pass
		self.init_notebook()
		self.init_buttons()
		self.vbox1.pack_start(self.vbox,1,1,0)
		self.add(self.vbox1)
		self.set_default_size(GDK.screen_width()-100, GDK.screen_height()-150)
		self.show_all()
		
	def mainloop(self):
		mainloop()
	
	# The determine_os() method will tell what operating system is running
	# so that calls to the shell, for example, may be issued correctly.
	# This is not currently used very much, and it is implemented in an extremely
	# ugly fashion.  It messes things up for users of recent versions of Redhat
        # and Mandrake.  Also, it will, as it stands, assume that any distribution of
        # linux is Debian (not a terrible thing, but . . .)
		
	def determine_os(self):
	    os_list = { 'freebsd'  : ['FreeBSD',  'BSD'],
	                'pc-linux-gnu': ['Debian',   'Linux'],
			'mandrake' : ['Mandrake', 'Linux'],
			'redhat'   : ['RedHat',   'Linux'],
			'solaris'  : ['Solaris',  'Unix'] }
	    self.os = 'Linux'
	    self.distribution = 'Generic'
	    for os_type in os_list.keys():
		if find( MACHTYPE, os_type ) != -1:
		    self.distribution = os_list[os_type][0]
		    self.os = os_list[os_type][1]

	
	def find_global_preferences(self):
	    
	    # make list of possibilities for various operating systems
	    possibilities = [ '/usr/local/lib/X11/icewm/',
	                      '/usr/X11R6/lib/X11/icewm/',
			      '/etc/X11/icewm/',
			      '/usr/X11R6/share/icewm/',
					'/usr/share/icewm/',
			      '/usr/lib/X11/icewm/' ]
	    
	    # get any additional possibilites from the PATH env variable.
	    path_dirs = re.split(':', PATH)
	    for directory in path_dirs:
		directory = directory + '/lib/X11/icewm/'
		possibilities.append( directory )
		
	    # find the location of the icewm exectuable.  Add an addition
	    # to _possibilities_ based upon this path.
	    
	    # This probably isn't that useful anymore.
	    
	    exec_path = commands.getoutput('whereis icewm')
	    exec_path = split(exec_path) # split output of whereis into tokens at whitespace
	    exec_path = exec_path[1] # get second token (should be executable)
	    
		
	    if find(exec_path, '/bin/icewm') != -1:
		path = exec_path[:-10] + '/X11/lib/icewm/'
		possibilities.append( path )
	    else:
		pass
	    
	    # search through _possibilities_ until a valid file is found.
	    # set self.global_preferences to this value.
	    # if none is found, set self.global_preferences to "".
	    
	    self.global_preferences = ''
	    
	    for location in possibilities:
		location = location + 'preferences'
		if os.path.isfile( location ):
		    self.global_preferences = location

	
	def find_local_preferences(self):
	    # check to see if the directory ~/.icewm exists.  If not, create
	    # it.
	    if not os.path.isdir(getIceWMPrivConfigPath()):
		try:
			os.makedirs(getIceWMPrivConfigPath())
		except:
			win = msg_err(_('Warning'), "WARNING:  Could not create the necessary personal IcePref2 directory:  "+str(getIceWMPrivConfigPath()))

		    
	    # if not, and if the self.global_preferences contains a path,
	    # copy the file at that path to ~/.icewm.
	    elif self.global_preferences != '':
		preferences = ''
		try:
		    f = open( self.global_preferences, 'r')
		    preferences = f.read()
		    f.close()
		except:
			win = msg_err(_('Warning'), 'Cannot read global preferences file: '+str(self.global_preferences))

	
	# Makes a copy of DEFAULTS in self.settings.
		
	def init_settings(self):
		self.settings = {}
		for key in DEFAULTS.keys():
			self.settings[key] = DEFAULTS[key][:]
	
	# Goes through each of the configuration options and forces the widgets
	# to conform to the data in self.settings
	 	
	def update_widgets(self, data=None):
		for widget in ORDER:
			try:
				self.widget_dict[widget].set_value(self.settings[widget][VALUE])
			except:
				pass
	
	# Takes a line from the configuration file and returns the name of the
	# configuration option (name) and its value (value) as a tuple. This whole
	# thing could be dramatically simplified by the use of regex stuff (of which
	# I was ignorant at the time I originally wrote it.  Also, it is possible that
	# options which are commented out should still be read as the new default
	# preferences file for IceWM has _all_ options commented out.
			
	def analyze(self, string):
	    
	    whole_options = string.split("\n")
	    
	    all_options = {}

	    for option in whole_options:
		if option.find("=")==-1: continue
		if option.strip().startswith("#"): continue
		option = re.split('=', option)
		option_name = option[0].strip()
		option_value = option[1]
		
		# added 1.26.2003 - improved preferences file parsing
		if option_value.find("\n")>-1: 
			option_value=option_value[0:option_value.find("\n")]
		if option_value.find("\r")>-1: 
			option_value=option_value[0:option_value.find("\r")]
		if option_value.find("\t")>-1: 
			option_value=option_value[0:option_value.find("\t")]
		if option_value.find("#")>-1: 
			option_value=option_value[0:option_value.find("#")]
		all_options[option_name] = option_value.strip()

	    return all_options
		
	# This is a replacement for the old get current settings.  It is designed to use the self.analyze()
	# method rather than the primitive and clumsy self.trim() method.

	def get_current_settings(self, data=None):
	    
	    # try to open preferences file.  Read whole file into variable and close.
	    
	    try:
		f = open(CONFIG_FILE, 'r')
		contents = f.read()
		f.close()
	    except:
		win = msg_warn(_('Warning'), _('Unable to read local preferences file!'))
		contents = ''
	    # pass contents of preferences file to self.analyze() and store the result
	    # in current.

	    current = self.analyze( contents )

	    # for each of the options in the dictionary current,
	    # check for a matching option in self.settings.  If there
	    # is no matching option, report it and record it.  If there is a matching option,
	    # set that option in self.settings to the value from current.

	    open_errors=""
	    for option in current.keys():
		if self.settings.has_key( option ):
			self.settings[option][VALUE] = current[option]
		else:
		    xxerr='Corrupt preferences file:  %s=%s does not seem to be a valid option' % (option, current[option])
		    open_errors=open_errors+xxerr+"\n\n"
	    if len(open_errors)>0:		
				commonAbout("Errors", open_errors , 0, "icepref2.png","\n")


	def save_current_theme_settings(self, *data):
		if self.widget_dict.has_key('Theme'):
			try:
				f=open(THEME_SET_FILE,"w")
				f.write("Theme="+str(self.widget_dict['Theme'].get_value()))
				f.flush()
				f.close()
			except:
				win = msg_err(_('Warning'), _("There was an ERROR saving your IceWM theme settings file.")+"\n"+str(THEME_SET_FILE))


	# writes the contents of self.settings to the preferences file
			
	def save_current_settings(self, *data):
		# this stuff is to make a backup file
		try: 
			f = open(CONFIG_FILE, 'r')
			old_pref = f.read()
			f.close()
			
			backup = CONFIG_FILE + '.backup-file'
			f = open(backup, 'w')
			f.write(old_pref)
			f.close()
		except:
			if str(data).find("nowarn")==-1: win = msg_warn(_('Warning'), _('There was no preferences file to backup!'))
		# this stuff saves the actual info
		try: 
			f = open(CONFIG_FILE, 'w')
			f.write('# This configuration file automatically generated by IcePref2 %s (updated by PhrozenSmoke, December 2003) -- a Python-based IceWM configuration tool.\n\n' % VERSION)
			for name in ORDER:
				string =''
				# this adds some descriptors depending upon the type of
				# option
				if self.settings[name][TYPE] == TOGGLE:
					string =' # 0 / 1'
				elif self.settings[name][TYPE] == RANGE:
					min = self.settings[name][MIN]
					max = self.settings[name][MAX]
					string = ' # ' + str(min) + '-' + str(max)
				# this sets up the comment descriptor, which is the same
				# as the label text.
				comment = '# ' + self.settings[name][TITLE] + '\n'
				if self.widget_dict.has_key(name):
					line = name + '=' + self.widget_dict[name].get_value() + string + '\n'
				else:
					if self.settings.has_key(name):  # added 5.5.2003, fall back to default
						line = name + '=' + str(self.settings[name][VALUE]) + string + '\n'
				f.write(comment)
				f.write(line)
				f.write('\n')
			f.close()
			if str(data).find("nowarn")==-1: win = msg_info(_('Success'), _("IceWM Preferences successfully saved to: ")+CONFIG_FILE+"\n\nBack-up: "+CONFIG_FILE+".backup-file")
		except:
			win = msg_err(_('Warning'), _("There was an ERROR saving your IceWM 'preferences' file."))
		self.save_current_theme_settings()

	def restart(self, widget=None, data=None):
	    
		# restart icewm.  Note that this is experimental and I have no idea
		# if it will work on all systems.  It definitely doesn't work on FreeBSD--
		# the signal HUP doesn't have the desired effect upon IceWM--but it may
		# work on other non Linux systems.  Under Debian, this function requires
		# the installation of the psmisc package.

		self.save_current_settings("nowarn")
		if self.os=="BSD":
			win = msg_confirm(_('Warning'), _("Restarting IceWM from IcePref is buggy on BSD systems.  You should restart IceWM yourself."))
			if not win==1: return
		#    changed 12.24.2003 - use common Bash shell probing
		#    to fix BUG NUMBER: 1523884
		#    Reported By: david ['-at-'] jetnet.co.uk
		#    Reported At: Fri Oct 31 23:47:12 2003
		fork_process("killall -HUP -q icewm")
		fork_process("killall -HUP -q icewm-gnome")
		# added  8.14.2003, needed by IceWM 1.2.10 and above
		# run icewmbg if it's not already running, restart it if it is
		if not get_pidof("icewmbg"): 
			fork_process("icewmbg")
		else: 
			fork_process("killall -HUP -q icewmbg")
		if not get_pidof("icewmbg"): 
			fork_process("icewmbg")
	

	
	def ok(self, data=None):
		self.save_current_settings()
		mainquit()
		
	# callback for the `about' menu option
		
	def about_cb(self, *data):
		aboutt=_('IcePref %s : a Python-based configuration utility for IceWM.\n\nOriginal Author:  David Mortensen.\nUpdated by: Erica Andrews\nSite: http://icesoundmananger.sourceforge.net\n\nIcePref %s is optimized for use with IceWM %s. This version of IcePref (%s) was updated by Erica Andrews (PhrozenSmoke [at] yahoo.com) in January 2003.  I, Erica Andrews, have modified IcePref in accordance with the GNU GPL under which IcePref is distributed.  I cannot say I have "taken over" the IcePref project, but got tired of it being abandoned and decided to make it more usable with newer versions of IceWM.  The new IcePref includes the new options available in the IceWM preferences file as of IceWM  %s.  The old IcePref site was at:  http://members.xoom.com/SaintChoj/icepref.html - but it appears that David Mortensen has abandoned his project, as he had not updated IcePref since the summer of 2000, and his site no longer exists.\n\nYou can find UPDATED versions of IcePref (for IceWM 1.2 and higher) at  http://icesoundmananger.sourceforge.net.  This updated version of IcePref by Erica Andrews is distributed under the GNU GPL without ANY warranty whatsoever. Use at your own risk! '.replace(' [at] ','@') ) % (VERSION,VERSION,  ICE_VERSION,VERSION,ICE_VERSION) 
		commonAbout(_('About IcePref2'), aboutt , 1, "icepref2.png","\n")
	
	# reloads the preferences file and sets all of the config widgets to
	# corresponding values.
			
	def set_file_settings(self, *data):
		self.init_settings()
		self.get_current_settings()
		self.update_widgets()
		
	# returns self.settings to the default values--doesn't work quite right
			
	def set_default_settings(self, *data):
		self.init_settings()
		self.update_widgets()

	# added 1.27.2003 - 2 methods to launch IceMe and IceSoundManager
	def run_iceme(self, *args):
		# changed 12.24.2003 - use common Bash shell probing
		# to fix BUG NUMBER: 1523884
		# Reported By: david ['-at-'] jetnet.co.uk
		# Reported At: Fri Oct 31 23:47:12 2003
		fork_process("iceme &> /dev/null")
	def run_ism(self, *args):
		# changed 12.24.2003 - use common Bash shell probing
		# to fix BUG NUMBER: 1523884
		# Reported By: david ['-at-'] jetnet.co.uk
		# Reported At: Fri Oct 31 23:47:12 2003
		fork_process("IceSoundManager &> /dev/null")
	def run_icecp(self, *args):
		# changed 12.24.2003 - use common Bash shell probing
		# to fix BUG NUMBER: 1523884
		# Reported By: david ['-at-'] jetnet.co.uk
		# Reported At: Fri Oct 31 23:47:12 2003
		fork_process("IceWMCP &> /dev/null")
	def run_icetd(self, *args):
		# changed 12.24.2003 - use common Bash shell probing
		# to fix BUG NUMBER: 1523884
		# Reported By: david ['-at-'] jetnet.co.uk
		# Reported At: Fri Oct 31 23:47:12 2003
		fork_process("icepref-td &> /dev/null")
	
	# creates the menubar
		
	def init_menu(self):
		menu_items = [
				(_('/_File'), None, None, 0, '<Branch>'),
				# 12.1.2003 - Tearoff disabled due to seg-faults in PyGtk2
				# (_('/File/tearoff1'), None, None, 0, '<Tearoff>'),
				(_('/_File')+'/_'+_('Open IceWM Preferences File')+'...', '<control>O', self.open_preference_file_cb, 0, ''),
				(_('/File/_Reload Preferences File'), '<control>P', self.set_file_settings, 0, ''),
				(_('/File/Reset _Defaults'), '<control>D', self.set_default_settings, 0, ''),
				(_('/File/_Save Preferences'), '<control>S', self.save_current_settings, 0, ''),

				# added 5.10.2003 - basic search functionality
				(_('/_File')+"/"+_('Search')+'...', '<control>B', icepref_search.runSearchDialog, 0, ''),

				(_('/File/sep1'), None, None, 0, '<Separator>'),
				(_('/File/_Apply Changes Now...'), '<control>A', self.restart, 0, ''),
				(_('/File/sep2'), None, None, 0, '<Separator>'),
 				(_("/_File")+"/_"+FILE_RUN,'<control>R', rundlg,421,""),
				(_('/_File')+"/_"+_("Check for newer versions of this program..."), '<control>U',checkSoftUpdate, 420, ''),
				(_('/File/sep2'), None, None, 0, '<Separator>'),
				(_('/File/_Exit IcePref2'), '<control>Q', mainquit, 0, ''),
				(_('/_Category'), None, None, 400, '<Branch>'),
				# 12.1.2003 - Tearoff disabled due to seg-faults in PyGtk2
				# (_('/_Category/tearoff2'), None, None, 401, '<Tearoff>'),
				(_('/_Tools'), None, None, 500, '<Branch>'),
				(_('/_Tools/Theme Designer (requires IcePref2-TD)...'), None, self.run_icetd, 501, ''),
				(_('/_Tools/Edit task bar menus (requires IceMe)...'), None, self.run_iceme, 501, ''),
				(_('/_Tools/Manage sound events (requires IceSoundManager)...'), None, self.run_ism, 503, ''),
				(_('/_Tools/Open Control Panel (requires IceControlPanel)...').replace("IceControlPanel","IceWMCP"), None, self.run_icecp, 502, ''),
				(_('/_Help'), None, None, 0, '<LastBranch>'),
				(_('/Help/_About IcePref2...'), "F2", self.about_cb, 0, ''),
  				(_("/_Help")+"/_"+APP_HELP_STR, "F4", displayHelp,5006, ""),
  				(_("/_Help")+"/_"+CONTRIBUTORS+"...", "F3", show_credits,913, ""),
  				(_("/_Help")+"/_"+BUG_REPORT_MENU+"...", "F5", file_bug_report,5006, ""),
					]
					
		ikeys=self.my_tabs.keys()
		ikeys.sort()
		for ii in ikeys:
			menu_items.append((_('/_Category/')+ii, None, self.switchTab, self.my_tabs[ii], '', ))
		ag = AccelGroup()
		itemf = ItemFactory(MenuBar, '<main>', ag)
		self.ag=ag
		self.itemf=itemf
		self.add_accel_group(ag)
		itemf.create_items(menu_items)
		self.menubar = itemf.get_widget('<main>')

		# added 6.21.2003 - "run as root" menu selector
		self.leftmenu=self.menubar.get_children()[0].get_submenu()
		self.run_root_button=CheckMenuItem(" "+RUN_AS_ROOT)
		self.leftmenu.prepend(self.run_root_button)
		self.run_root_button.connect("toggled",self.run_as_root_cb)

		self.vbox1.pack_start(self.menubar, 0,0,0)
		self.menubar.show()

	# added 1.26.2003 - quick category tab switching - added by PhrozenSmoke
	def switchTab(self,*args):
		try:
			self.mynotebook.set_current_page(args[0])
		except:
			pass
		
	# creates the notebook and its friends.

	def init_notebook(self):
		global im_file_entry
		global im_file_prev
		global PULL_TAB
		im_file_entry=None
		im_file_prev=None
		if PULL_TAB==None:
			notebook = Notebook()
			notebook.set_tab_pos(POS_TOP)
			notebook.set_scrollable(TRUE)
			notebook.show()

			self.vbox.pack_start(notebook,1,1,0)
			sep = HSeparator()
			sep.show()
			self.vbox.pack_start(sep, expand = FALSE)
			# sets up each of the tabs (one for each category of
			# configuration options

			#added 1.26.2003
			self.mynotebook=notebook

		TABS.sort()
		found_tab=0  # added 5.5.2003, try to speed up single-module loading of IcePref2

		for tab in TABS:
			if found_tab==1:  break
			if PULL_TAB==None: label = Label(" "+tab[0]+" ")
			widgets = tab[1]

			if not SHOW_MODULE==None:
				if SHOW_MODULE in TABS_NAMES:
					if not str(tab[0])==SHOW_MODULE:  
						continue   
						# added 5.5.2003 - speed up 'single module' mode by skipping 
						# unnecessary GUI creation, although all preferences are loaded 'invisibly'

			# creates a scrolled window within the notepad page
			# for each tab.
			scroll = ScrolledWindow()

			#scroll.set_size_request(gtk.screen_width()-150, gtk.screen_height()-240)
			scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
			scroll.show()
			if not SHOW_MODULE==None:
				if SHOW_MODULE in TABS_NAMES:
					if str(tab[0])==SHOW_MODULE:
						if PULL_TAB==None: 
							notebook.append_page(scroll, label)
							found_tab=1
						else:  
							self.scroller=scroll  # added 5.5.2003
							found_tab=1
				else:
					if PULL_TAB==None: notebook.append_page(scroll, label)
			else:
				if PULL_TAB==None: notebook.append_page(scroll, label)
			
			vbox = VBox(spacing=SP)
			vbox.show()
			
			# Determines whether to use one column or two.
			# If there are more than 4 widgets, two columns
			# are used.
			
			num_widgets = len( widgets )
			
			if num_widgets > 4:
				rows = ( int( num_widgets / 2 ) + 1)
				cols = 2
			else:
				rows = num_widgets
				cols = 1
			if rows < 2: rows = 2

			if not PULL_TAB==None: cols=1  # added 5.5.2003
			
			# Creates a table for the widgets
			
			table = Table(	 rows, cols, FALSE)
			table.show()
			if cols==2: table.set_col_spacings(25)
			table.set_row_spacings(5)
			vbox.pack_start(table, FALSE, FALSE)
			scroll.add_with_viewport(vbox)
			
			# Add the widgets to the table.
			
			x, y = 0, 0 # x and y counters for the table
			ts=None
			for item in widgets:
				if not item in REQUIRE_PREVIEW: 
					widget = self.widget_chooser(item)
					# added 1.27.2003 - dynamic theme reading support
					if (item=="ThemeAuthor"): 
						if not ts==None: 
							ts.author_entry=widget
							ts.author_entry.entry.set_editable(0)
							if not ts.iprev.entry_box==None:
								ts.iprev.entry_box.pack_start(widget,0,0,0)
								ts.iprev.entry_box.pack_start(Label("  "),1,1,7)
					elif (item=="ThemeDescription"): 
						if not ts==None: 
							ts.desc_entry=widget
							ts.desc_entry.entry.set_editable(0)
							if not ts.iprev.entry_box==None:
								ts.iprev.entry_box.pack_start(widget,0,0,0)
								ts.iprev.entry_box.show_all()
					else:
						table.attach(widget, x,x+1, y,y+1)
				else: 
					if item=="Theme": ipreview=ImagePreviewer(2,self.restart,self.save_current_settings)
					elif item=="DesktopBackgroundImage": 
						ipreview=ImagePreviewer(1, None,None)
						im_file_prev=ipreview
					else: ipreview=ImagePreviewer()
					widget = self.widget_chooser(item,ipreview)
					if item=="DesktopBackgroundImage": 
						im_file_entry=widget
						addDragSupport(widget.entry,setDrag)  # drag-n-drop support, 2.23.2003
						addDragSupport(widget.button,setDrag)  # drag-n-drop support, 2.23.2003
					if item=="Theme": ts=widget
					table.attach(widget, x,x+1, y,y+1)
					y = y + 1
					table.attach(ipreview.scbox, x,x+1, y,y+1)
				self.widget_dict[item] = widget
				# if the y counter is greater than or equal to half
				# the number of widgets in a two column page,
				# move to the second column
				if y >= ((num_widgets / 2.0) - 1) and x == 0 and cols == 2:
					y = 0
					x = x + 1
				else:
					y = y + 1
					
	# accepts a configuration option as its argument and returns the
	# appropriate widget.  If a new type of widget is added, it will have
	# to be added here as well.
					
	def widget_chooser(self, item,Image_prev=None):
		type = self.settings[item][TYPE]
		W_TITLE=_(self.settings[item][TITLE])
		W_VALUE=self.settings[item][VALUE]
		if type == TOGGLE:
			widget = IceToggled(	W_TITLE,
						W_VALUE)
		elif type == RANGE:
			widget = IceRange(		W_TITLE,
						self.settings[item][MIN],
						self.settings[item][MAX],
						W_VALUE)
		elif type == FILE:
			widget = IceFile(		W_TITLE,
						W_VALUE,Image_prev)
		elif type == PATH:
			widget = IcePath(		W_TITLE,
						W_VALUE)
		elif type == COLOR:
			widget = IceColor(		W_TITLE,
						W_VALUE)
		elif type == FONT:
			widget = IceFont(		W_TITLE,
						W_VALUE)
		elif type == ENTRY:
			widget = IceEntry(		W_TITLE,
						W_VALUE)
		elif type == KEYSTROKE:
			widget = Keystroke(	W_TITLE,
						W_VALUE)
		elif type == MULTI:
			widget = IceMulti(		W_TITLE,
						W_VALUE,
						self.settings[item][NUM])
		elif type == THEME:
			widget = ThemeSel(	W_TITLE,
						W_VALUE,Image_prev)
					
		elif type == BITMASK:
			widget = BitMask(	W_TITLE,
						W_VALUE)
							
		elif type == MOUSEBUTTON:
			widget = MouseButton( 	W_TITLE,
						W_VALUE)
		TIPS.set_tip(widget,W_TITLE+"\n["+item+"]")
		for ichild in widget.get_children():
			TIPS.set_tip(ichild,W_TITLE+"\n["+item+"]")
			try:
				for ichildd in ichild.get_children():
					if not ichildd.__class__.__name__=="Button": TIPS.set_tip(ichildd,W_TITLE+"\n["+item+"]")
			except:
				pass		
		return widget


	# creates the buttons at the bottom of the window
	
	def init_buttons(self):	

		buttons = [
					[_('Save'), self.save_current_settings,_('Save settings to your IceWM preferences file'), STOCK_SAVE],
					[_('Defaults'), self.set_default_settings,_('Reset default values'), STOCK_UNDO],
					[_('Reload'), self.set_file_settings,_('Reload the preferences file'), STOCK_REFRESH],
					[_('Apply'), self.restart,_('Apply')+"\n"+_('Restart IceWM (does not work on all systems)'), STOCK_APPLY],
					[_('Exit'), mainquit,_('Exit IcePref2'), STOCK_QUIT]
				]
				
		bbox = HButtonBox()
		bbox.set_layout(BUTTONBOX_SPREAD)
		bbox.show()
		self.vbox.pack_start(bbox, FALSE, FALSE, 0)
		for item in buttons:
			button = getPixmapButton(None, item[3] , item[0])
			button.connect('clicked', item[1])
			TIPS.set_tip(button,item[2])
			button.show()			    
			bbox.pack_start(button, FALSE, FALSE, 0)

	# added 6.21.2003, Erica Andrews, "Run as Root" functionality
	def run_as_root_cb(self,*args):  # callback for the menu
		self.run_as_root(int(self.run_root_button.get_active()))
		if self.run_root_button.get_active(): self.set_title('IcePref2   [ROOT]')
		else: self.set_title('IcePref2')
		self.menubar.deactivate()

	def run_as_root(self,root_bool):	# make available to PullTab sub-class
		global CONFIG_FILE
		if root_bool==1:
			CONFIG_FILE = getIceWMConfigPath()+'preferences'
			self.set_file_settings()
		else:   # turn 'root' OFF
			CONFIG_FILE = getIceWMPrivConfigPath()+'preferences'
			self.set_file_settings()		
		#print "CONFIG: "+CONFIG_FILE
		

	# added 6.22.2003, Erica Andrews, allow opening of random prefs files anywhere on the system
	def open_preference_file_cb(self,*args):
		SET_SELECTED_FILE(CONFIG_FILE)  # from icewmcp_common
		SELECT_A_FILE(self.open_preference_file,_("Select a file..."),"icepref","IcePref")

	def open_preference_file(self,*args):
		conf=GET_SELECTED_FILE()
		if not conf==None:
			if not conf=='':
				global CONFIG_FILE
				CONFIG_FILE=conf
				self.set_file_settings()


##  ADDED 5.5.2003 - PhrozenSmoke - to pull a single 'tab' from the app, kind of a 'plugin'
class PullTab(Application):  # added 5.5.2003 - to be able to pull one 'tab'from the app	
	def __init__(self, pull_tab="Mouse"):
		global APP_WINDOW		
		# this basically equates to an unshown window
		self.scroller=None   # the 'detachable' widget for plugging into other apps
		APP_WINDOW=self
		global SHOW_MODULE
		global PULL_TAB
		PULL_TAB=_(pull_tab)
		SHOW_MODULE=PULL_TAB
		self.widget_dict={}
		self.determine_os()
		self.init_settings()
		self.find_global_preferences()
		self.find_local_preferences()
		self.get_current_settings()
		self.my_tabs={} 
		self.init_notebook()
		self.scroller.show_all()
	def get_tab(self):
		return self.scroller



# makes the whole show run

def run():
	for mm in sys.argv:
		if str(mm).startswith("module="):
			choice_mod=str(mm).replace("module=","").replace("\"","").replace("'","").strip()
			if len(choice_mod)>0: 
				global SHOW_MODULE
				SHOW_MODULE=_(choice_mod)
				if not SHOW_MODULE in TABS_NAMES:
					print "\nWarning: No module named '"+SHOW_MODULE+"' - displaying all modules.\n\nRun icepref with the command-line option '--listmodules' for a list of available modules."
		if str(mm).lower().find("listmodules")>-1:
			print "\nAvailable IcePref modules:\n\n"
			for yy in TABS_NAMES:
				print "\t"+str(yy)
			print "\n"
			sys.exit(0)

	app = Application(sys.argv)
	hideSplash()
	app.mainloop()

if __name__ == '__main__':		
	run()
	hideSplash()
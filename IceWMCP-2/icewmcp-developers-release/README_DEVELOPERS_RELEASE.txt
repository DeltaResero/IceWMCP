
THIS SOFTWARE IS DISTRIBUTED AS OPEN SOURCE UNDER THE TERMS OF THE GNU GENERAL PUBLIC LICENSE (GPL).

Copyright (c) 2003 Erica Andrews
<PhrozenSmoke@yahoo.com>


THIS IS THE DEVELOPER'S RELEASE OF ICEWM CONTROL PANEL (VERSION 3.0)


NO TECHNICAL SUPPORT OF ANY KIND IS PROVIDED FOR THIS RELEASE!!!  DO NOT CONTACT ME WITH QUESTIONS OR REQUESTS FOR HELP REGARDING THIS RELEASE.  IF YOU ARE NOT KNOWLEDGEABLE ABOUT PYTHON PROGRAMMING (AND ARE NOT WILLING TO LEARN ON YOUR OWN), YOU SHOULD *NOT* BE USING THIS RELEASE.


THIS RELEASE PACKAGE IS NOT INTENDED FOR GENERAL USERS. INSTEAD, IT IS INTENDED FOR PROGRAMMERS AND DEVELOPERS INTERESTED IN HAVING A BARE-BONES COPY OF THE ICEWM CONTROL PANEL AS A FRAMEWORK FOR A NEW 'CONTROL PANEL' APPLICATION.


As noted on the IceWM Control Panel home page (http://icesoundmanager.sourceforge.net), the IceWM Control Panel can also be used as a GENERAL PURPOSE 'Control Panel' application for any window manager or desktop environment.  This developer's release is intended to demonstrate how easy it is to build different types of 'Control Panels' based on the modular, stable framework of the IceWM Control Panel.  In fact, that is exactly what this 'developer's release' provides:  A FRAMEWORK for creating your own 'Control Panel' application, without the extra IceWM-specific tools available in the 'users' edition of the IceWM Control Panel.  Have fun with it, build a control panel for any window manager of your choice.

Three sample control panel 'applets' are included.  For more information on developing your own control panel applets, please see the document 'ControlPanel-APPLETS.html' in the 'docs' directory of this distribution.

This software is written in 100% Python.  So, the following are required: Python 2.2, PyGtk 1.9.9 or better (with the GdkPixbuf modules).  

As an added plus, the IceWM Control Panel features foreign language (gettext) support, as well as software update checking and on-demand bug reporting from within IceWM Control Panel to help users send bug reports quickly and easily.  The following languages are currently supported: English, Spanish, Russian, and Traditional Chinese (zh_TW).  An end-user help file is currently available in the following languages:  English, Spanish.


To run the application:  execute  'python IceWMCP.py'  or run the 'run-me.sh' script

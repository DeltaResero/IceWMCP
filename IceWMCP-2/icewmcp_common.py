#############################
#  IceWM Control Panel - Common
#  
#  Copyright 2003 by Erica Andrews
#  PhrozenSmoke ['at'] yahoo.com
#  http://icesoundmanager.sourceforge.net
#  
#  This program is distributed free
#  of charge (open source) under the GNU
#  General Public License
#############################

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



# added 4/28/2003, python-based vs. static binary, for bug reporter
global IS_STATIC_BINARY
IS_STATIC_BINARY="no"

# seems to help some Debian systems
try:
	import pygtk
	pygtk.require("2.0")
except:
	pass



# Some PyGtk2 path settings while we upgrade from PyGtk-1 to PyGtk2
try:
	import sys
	sys.path=["/usr/lib/python2.2/site-packages/gtk-2.0"]+sys.path
	sys.path=["/usr/lib/python2.3/site-packages/gtk-2.0"]+sys.path
	import gtk
	import gtk.gdk 
	GDK=gtk.gdk
	GTK=gtk
	from gtk import *
	import pango
except:
	print "You do not have PyGtk-2 or one of its libraries properly installed."
	print "This application requires PyGtk-2 1.99/2.00 or better."
	sys.exit(0)
	pass



DEFAULT_CHARSET="iso8859-1"  
# added, 12.1.2003- Erica Andrews, Good for English/Spanish, will probe later for Pango


# added, 12.1.2003- Erica Andrews - list of International charsets to help Pango
INTL_CHARSETS={
	"ru":"koi8-r",  # Russian
	"es":"iso8859-1",  # Spanish
	"fr":"iso8859-1",  # French
	"en":"iso8859-1",  # English
	"":"iso8859-1",  # for unknown locales
	"fi":"iso8859-1",  # Finnish, only translation is for IceMe, which needs "iso8859-15"
	"zh_tw":"big5",  # Traditional Chinese
}

LANGUAGE_CODEC=None  
# added 12.1.2003, most languages can use built-in 'unicode', will set later

def to_utf8(somestr):
	try:
		somestr.decode("utf-8")
		return somestr  # already in utf-8
	except:
		pass
	try:
		if LANGUAGE_CODEC==None:
			unistr = unicode(str(somestr),DEFAULT_CHARSET)
		else: unistr=LANGUAGE_CODEC.decode(str(somestr))[0]
		utfstr = unistr.encode("utf-8")
		return utfstr
	except:
		print " "
		print "Your Python installation does not support the character set"
		print "'"+str(DEFAULT_CHARSET)+"' needed to translate this application into your language." 
		print "If you are are attempting to run this application in Chinese,"
		print "Korean, or Japanese, you will need to download and install the"
		print "appropriate Python language codecs from http://cjkpython.berlios.de/"
		print "or get a pre-compiled copy from http://icesoundmanager.sourceforge.net"
		print "You can also simply run this application in English or another supported language."
		print " "
		sys.exit(0)


import gtk
import gettext,sys,os,gtk.gdk,glob,string

TIPS=gtk.Tooltips()  # added 4/27/2003


# added 12.3.2003, two methods for setting basic window icons
# These icons, of course, can be over-ridden by the use if they choose
# using a program like IceWMCP-WinOptions, also a builtin pixmap for icons

# A simple 20x20 builtin pixmap for window icons, we don't want to rely images on the DISK
# for something like an app's window icon...one click of the delete button= No more icons
# WARNING: Editing this pixmap code by hand can produce an invalid pixmap which 
# wil cause PyGtk-2 to seg-fault

icon_icewmcp=[
"20 20 163 2",
"  	c None",
". 	c #46527A",
"+ 	c #7A86B2",
"@ 	c #56628A",
"# 	c #8A8EA6",
"$ 	c #96A2CA",
"% 	c #8A92C2",
"& 	c #525A72",
"* 	c #8A8A96",
"= 	c #929AB2",
"- 	c #9296AA",
"; 	c #929ECA",
"> 	c #C2CAEE",
", 	c #8A92B2",
"' 	c #A2A6B6",
") 	c #DEDEE6",
"! 	c #8E96BA",
"~ 	c #A6AABA",
"{ 	c #929AB6",
"] 	c #9EAAD6",
"^ 	c #E2E6F6",
"/ 	c #BAC2DA",
"( 	c #9A9EB6",
"_ 	c #E6E6EA",
": 	c #AEB6D6",
"< 	c #626A92",
"[ 	c #8E8E96",
"} 	c #B6B6BE",
"| 	c #828EB6",
"1 	c #F2F2F6",
"2 	c #CED2E6",
"3 	c #727A96",
"4 	c #B2B6BE",
"5 	c #DADEE6",
"6 	c #9EA6C6",
"7 	c #525A82",
"8 	c #52525E",
"9 	c #7A82AA",
"0 	c #BAC2E2",
"a 	c #EEF2FA",
"b 	c #DEE2EE",
"c 	c #6E769A",
"d 	c #AEB6CA",
"e 	c #828AB2",
"f 	c #A6AECA",
"g 	c #929ABE",
"h 	c #42465A",
"i 	c #868692",
"j 	c #D6D6DA",
"k 	c #EEEEF6",
"l 	c #7E8AAE",
"m 	c #7E86AA",
"n 	c #8E92B2",
"o 	c #727EAE",
"p 	c #AEB2C2",
"q 	c #C2C6DE",
"r 	c #EAEAEE",
"s 	c #B6BACE",
"t 	c #CACEDE",
"u 	c #C6CEE2",
"v 	c #F6FAF6",
"w 	c #BEC2D2",
"x 	c #8E96AE",
"y 	c #AAB2D6",
"z 	c #828EBA",
"A 	c #6A7AAA",
"B 	c #7E86A2",
"C 	c #D2D6DE",
"D 	c #FAFAFA",
"E 	c #D6DADE",
"F 	c #7A82A2",
"G 	c #9A9AAA",
"H 	c #E2E6EA",
"I 	c #BEC2CE",
"J 	c #DADEEA",
"K 	c #9EA2B2",
"L 	c #E2E2EA",
"M 	c #8A96C2",
"N 	c #F2F2F2",
"O 	c #EAEAEA",
"P 	c #868A9E",
"Q 	c #82869A",
"R 	c #C6CAD2",
"S 	c #E6EAEE",
"T 	c #C6CADA",
"U 	c #868EB2",
"V 	c #A6AAC6",
"W 	c #8A8EA2",
"X 	c #D2D2DA",
"Y 	c #CED2DE",
"Z 	c #C2C6D2",
"` 	c #BEC2DA",
" .	c #D2DAF2",
"..	c #8A92BE",
"+.	c #9AA2B6",
"@.	c #5E6A8E",
"#.	c #B6BAC2",
"$.	c #CACED2",
"%.	c #A2A6C2",
"&.	c #EEF2F6",
"*.	c #B6BEDE",
"=.	c #A2A6BA",
"-.	c #8A92B6",
";.	c #868EAA",
">.	c #B2B6C2",
",.	c #CED2EA",
"'.	c #7E8296",
").	c #D6DAE2",
"!.	c #D6DEFA",
"~.	c #F6F6F6",
"{.	c #E2E2EE",
"].	c #F6F6FA",
"^.	c #82869E",
"/.	c #8A92AE",
"(.	c #727EA2",
"_.	c #AAB2C6",
":.	c #565E82",
"<.	c #868EAE",
"[.	c #56668A",
"}.	c #565E86",
"|.	c #525E8A",
"1.	c #3E4E7E",
"2.	c #46527E",
"3.	c #4A5682",
"4.	c #3E4E86",
"5.	c #364672",
"6.	c #56628E",
"7.	c #767E96",
"8.	c #4E5E8E",
"9.	c #6A769A",
"0.	c #4A5A86",
"a.	c #525E86",
"b.	c #4E5E86",
"c.	c #465682",
"d.	c #4E5E8A",
"e.	c #525E8E",
"f.	c #42528A",
"g.	c #364A82",
"h.	c #3A4E86",
"i.	c #36467A",
"j.	c #3A4A7A",
"k.	c #626E92",
"l.	c #626E96",
"m.	c #4A5A8A",
"n.	c #4A5A82",
"o.	c #465A8A",
"p.	c #465686",
"q.	c #3A4E7E",
"r.	c #324276",
"s.	c #3A4A7E",
"t.	c #424E7E",
"u.	c #465282",
"v.	c #46568A",
"w.	c #425286",
"x.	c #3E4E82",
"y.	c #425282",
"z.	c #3A4E82",
"A.	c #4E5A86",
"B.	c #3E5286",
"C.	c #52628E",
"D.	c #4E5A8A",
"E.	c #32427A",
"F.	c #2E427A",
"                    .                   ",
"                    + @                 ",
"                  # $ % & * =           ",
"                  - ; > , ' ) !         ",
"                ~ { ] ^ / ( _ : <       ",
"              [ } | > 1 2 3 4 5 6 7     ",
"            8 ~ ~ 9 0 a b c c - d e     ",
"      f g h i j ~ $ ; b k = l m n o     ",
"    p b q 3 4 r s t e u v w x y z A     ",
"  B C D E F G H I J K q L b y / M |     ",
"  K ) N O P Q j R S T q } 5 H u U V M   ",
"  ' R E v 4 W X C H Y t Z ` k  ...+.:   ",
"@.#.+.t D O +.} k ^ ^ S $.%.^ &.*.m =.-.",
";.>.U ,.v k %.'.).!.&.~.} g {.].T 9 ^./.",
"x 3 (.*.E _.(.:.4  .k N G <.5 ).x [.}.|.",
"1.2.7 @.[.3.4.5.6.U / I 7.8.9.[.0.a.b.c.",
"0.d.e.e.f.g.h.i.j.a.k.l.[.m.d.2.n.b.b.m.",
"n.c.o.p.q.r.r.g.s.p.a.b.|.|.|.c.t.u.v.w.",
"t.2.x.j.y.0.t.q.z.o.A.t.1.1.c.B.B.4.h.z.",
"j.c.a.d.n.p.C.8.D.6.C.b.p.x.x.f.g.E.E.F."]


def set_special_window_icon(mywindow,my_xpm):
	try:
		mywindow.set_icon(GDK.pixbuf_new_from_xpm_data(my_xpm))
	except:
		pass

def set_basic_window_icon(mywindow):
	try:
		mywindow.set_icon(GDK.pixbuf_new_from_xpm_data(icon_icewmcp))
	except:
		pass



# added 6.8.2003, mainly for developer testing, 
# but may be of use to others: allows IceWMCP
# programs to be 'forced' to run in a certain locale
# without having to set the LANG and LANGUAGE 
# environment variables.  Useful for my personal 
# testing and if you want just one program to run 
# in a certain language.  Examples:  'es' - Spanish, 
# 'ru' - Russian, 'fi' - Finnish, 'en' - English
# String should be the locale 'abbreviation' for the locale 
# to force IceWMCP to run in.  Default is '' - meaning 
# the default behavior is to use the LANG/LANGUAGE 
# environment variables.

# Recommended fonts for ru (Russian) locale in .gtkrc:
# "-microsoft-verdana-bold-r-normal-*-*-130-*-*-p-*-koi8-r"
# "-cronyx-helvetica-medium-r-normal-*-*-140-*-*-p-*-koi8-r"

FORCE_LOCALE=""    # example:  'ru'

def getBaseDir() :
	if sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]=='': return "."+os.sep
	return sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]

locale_dirs=[getBaseDir()+'/locale','/usr/share/locale','/usr/X11R6/share/locale','/usr/locale','/usr/local/share/locale']


# added 6.8.2003 - a method for forcing the loading
# of a particular gettext locale catalog, using FORCE_LOCALE

def getForcedLocale(catalog):  # This fails for chinese zh_tw
	if FORCE_LOCALE=='': return None
	for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			locale_file=os.path.abspath(LOCALE_DIR+"/"+FORCE_LOCALE.lower()+"/LC_MESSAGES/"+catalog)
			#print locale_file
			gettext.install(locale_file)
			#print str(gettext._translations)
			return gettext._translations[locale_file+".mo"]
		except:
			pass
	return None



def getPixDir() :
    return getBaseDir()+os.sep+"pixmaps"+os.sep

def getDocDir() :
    return getBaseDir()+os.sep+"doc"+os.sep


# added 4.25.2003 - centralized method for finding locale-based sub-directories in IceWMCP directory tree
def getLocaleDir():
	if not FORCE_LOCALE=='': return FORCE_LOCALE.lower()+"/"  # added 6.8.2003

	# added 6.19.2003: Some locales are so radically different even if the language 
	# like 'Chinese' is the same, so exceptions for a few: Chinese, Portuguese where 
	# regional differences = total language difference, we will keep the WHOLE locale name 
	#  i.e.  'zh_tw', instead of cutting it to 'zh'

	EXCEPTIONS=['zh_tw','zh_sg','zh_hk','zh_cn','pt_br','pt_pt']
	loc_vars=['LANG', 'LANGUAGE', 'LC_ALL', 'LOCALE', 'LC_MESSAGES']
	# rewritten, 12.19.2003, to probe more than LANG and LANGUAGE, also code cleanup
	for locvar in loc_vars:
		try:
			mylang=os.environ[locvar]  # try $LANG variable first
			if mylang.strip()=='': continue
			for ii in EXCEPTIONS:
				if mylang.strip().lower().startswith(ii): return ii+"/"
			if mylang.find("_")>-1: mylang=mylang[0:mylang.find("_")]  #  es_MX  -> 'es'
			mylang=mylang.strip().lower()+os.sep   # example:  "es/"
			return mylang
		except:
			pass
	return ""  # default to no sub-directory at all


# Set up locale for Pango, 12.1.2003 - Erica Andrews 
ice_locale_check=getLocaleDir().replace("/","").strip()
if INTL_CHARSETS.has_key(ice_locale_check):
	DEFAULT_CHARSET=INTL_CHARSETS[ice_locale_check]

#Setup Chinese language support
if ice_locale_check=="zh_tw":
	try:
		sys.path=["/usr/lib/python2.2/site-packages/cjkcodecs"]+sys.path
		sys.path=["/usr/lib/python2.3/site-packages/cjkcodecs"]+sys.path
		from cjkcodecs import big5
		LANGUAGE_CODEC=big5.codec
	except:
		pass

#print DEFAULT_CHARSET
#print ice_locale_check

# added 4.25.2003 - centralized method for locating the 'Help' sub-directory
def getHelpDir():
    return getBaseDir()+os.sep+"help"+os.sep


# added 4.25.2003 - centralized method for locating locale-specific 'Help' file sub-directory
def getHelpDirLocale():
    return getHelpDir()+getLocaleDir()

def loadImage(picon,windowval=None):
    try:
        p=Image()
	if (picon.startswith("gtk-")) : # a stock icon
		# hmmm, no way to really scale stock icons to a special size
		p.set_from_stock(picon,ICON_SIZE_BUTTON)
	else: p.set_from_file(str(picon).strip())
        p.show_all()
        return p
    except:
        return None

def loadScaledImage(picon,newheight=40,newwidth=40):  # added in version 0.3, gdkpixbup support, load png, xpm, or gif, allow scaling of images
    try:
	if (picon.startswith("gtk-")) : # a stock icon
		# No way to scale stock icons, so just return the default size
		return loadImage(picon)
        img = gtk.gdk.pixbuf_new_from_file(picon)
        img2 = img.scale_simple(newheight,newwidth,gtk.gdk.INTERP_BILINEAR)
        pix,mask = img2.render_pixmap_and_mask()
        icon = gtk.Image()
        icon.set_from_pixmap(pix, mask)
        icon.show()
        return icon
    except:
        return None
    

# Some image/icon enhanced widgets

def getPixmapVBox(iwin,picon,btext):
	# return HBox with icon and label
        try:
	  v=HBox(1,2)
          v.set_homogeneous(0)
	  v.pack_start(loadScaledImage(str(picon),24,24),0,0,1)
          v.pack_start(Label(str(btext)),0,0,1)
          v.show_all()
          return v
        except:
          v=HBox(1,1)
          v.pack_start(Label(str(btext)),0,0,1)
          v.show_all()
          return v

def getPixmapButton (iwin,picon,btext) :  
	  # return a Button with icon and label
	  b=Button()
          b.add(getPixmapVBox(iwin,picon,btext))
          b.show_all()        
          return b

def getIconButton (iwin,picon,lab="?") :  
	# return a Button with just the icon
	b=Button()
	b.add(getImage(str(picon),str(lab) )) 
	b.show_all()
	return b



global MY_ICEWM_PATH
MY_ICEWM_PATH=None

def getIceWMPrivConfigPath():  # implemented in 0.3 - check environ variable, though who really uses this variable?
	if os.environ.has_key("ICEWM_PRVCFG"): 	ppath=os.environ['ICEWM_PRVCFG']
	else: 	ppath=os.environ['HOME']+os.sep+".icewm"+os.sep
	if not ppath.endswith(os.sep): ppath=ppath+os.sep
	return ppath

def getIceWMConfigPath():  # new in version 0.3, search for IceWM global config path in likely locations
	global MY_ICEWM_PATH
	if not MY_ICEWM_PATH==None: return MY_ICEWM_PATH
	for iipath in ["/usr/X11R6/lib/X11/icewm/","/usr/local/lib/X11/icewm/","/etc/X11/icewm/","/etc/icewm/","/usr/local/share/icewm/","/usr/local/lib/icewm/","/usr/share/icewm/","/usr/X11R6/share/icewm/","/usr/lib/icewm/"]:
		try:
			if os.path.exists(iipath) and os.path.isdir(iipath): 
				MY_ICEWM_PATH=iipath
				return iipath
		except:
			pass
	MY_ICEWM_PATH="/usr/X11R6/lib/X11/icewm/"  # we didnt find the path, use a default
	return "/usr/X11R6/lib/X11/icewm/"



## added 2.18.2003 - some suggested consolidation, also  preliminary localization support

# gettext locale support - icewmcp
icewmcp_xtext=gettext.NullTranslations()

try:
	# open icewmcp.mo in /usr/share/locale or whatever
	f_gettext=0
	icewmcp_xtext=getForcedLocale("icewmcp")
	if not icewmcp_xtext==None: f_gettext=1
	else:
	   for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			icewmcp_xtext=gettext.translation("icewmcp",LOCALE_DIR)
			f_gettext=1
			break
		except:
			pass
	if not f_gettext==1: raise TypeError   # couldnt find a gettext catalog, raise exception, use empty catalog
except:
	icewmcp_xtext=gettext.NullTranslations()

translateCP=icewmcp_xtext.gettext


# gettext locale support - icepref2
icewmcp_icepref_xtext=gettext.NullTranslations()

try:
	# open icewmcp-icepref.mo in /usr/share/locale or whatever
	f_gettext=0
	icewmcp_icepref_xtext=getForcedLocale("icewmcp-icepref")
	if not icewmcp_icepref_xtext==None: f_gettext=1
	else:
	   for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			icewmcp_icepref_xtext=gettext.translation("icewmcp-icepref",LOCALE_DIR)
			f_gettext=1
			break
		except:
			pass
	if not f_gettext==1: raise TypeError   # couldnt find a gettext catalog, raise exception, use empty catalog
except:
	icewmcp_icepref_xtext=gettext.NullTranslations()

translateP=icewmcp_icepref_xtext.gettext


# gettext locale support - Ice Sound Manager
icewmcp_ism_xtext=gettext.NullTranslations()

try:
	# open icewmcp-ism.mo in /usr/share/locale or whatever
	f_gettext=0
	icewmcp_ism_xtext=getForcedLocale("icewmcp-ism")
	if not icewmcp_ism_xtext==None: f_gettext=1
	else:
	   for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			icewmcp_ism_xtext=gettext.translation("icewmcp-ism",LOCALE_DIR)
			f_gettext=1
			break
		except:
			pass
	if not f_gettext==1: raise TypeError   # couldnt find a gettext catalog, raise exception, use empty catalog
except:
	icewmcp_ism_xtext=gettext.NullTranslations()

translateISM=icewmcp_ism_xtext.gettext


# gettext locale support - IceMe
icewmcp_iceme_xtext=gettext.NullTranslations()

try:
	# open icewmcp-iceme.mo in /usr/share/locale or whatever
	f_gettext=0
	icewmcp_iceme_xtext=getForcedLocale("icewmcp-iceme")
	if not icewmcp_iceme_xtext==None: f_gettext=1
	else:
	   for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			icewmcp_iceme_xtext=gettext.translation("icewmcp-iceme",LOCALE_DIR)
			f_gettext=1
			break
		except:
			pass
	if not f_gettext==1: raise TypeError   # couldnt find a gettext catalog, raise exception, use empty catalog
except:
	icewmcp_iceme_xtext=gettext.NullTranslations()

translateME=icewmcp_iceme_xtext.gettext


# gettext locale support - HW plugin
icewmcp_hw_xtext=gettext.NullTranslations()

try:
	# open icewmcp-hw.mo in /usr/share/locale or whatever
	f_gettext=0
	icewmcp_hw_xtext=getForcedLocale("icewmcp-hw")
	if not icewmcp_hw_xtext==None: f_gettext=1
	else:
	   for LOCALE_DIR in locale_dirs:  # open the first catalog we find, try ./locale dir first
		try:
			icewmcp_hw_xtext=gettext.translation("icewmcp-hw",LOCALE_DIR)
			f_gettext=1
			break
		except:
			pass
	if not f_gettext==1: raise TypeError   # couldnt find a gettext catalog, raise exception
except:
	icewmcp_hw_xtext=gettext.NullTranslations()

translateHW=icewmcp_hw_xtext.gettext




def _(somestr):
	return to_utf8(translateCP(somestr))

DIALOG_TITLE=_("IceWM Control Panel")
DIALOG_OK=_("OK")
DIALOG_CANCEL=_("CANCEL")
DIALOG_CLOSE=_("Close")
FILE_RUN=_("Run")+"..."
HELP_MENU=_("/_Help")
ABOUT_MENU=_('/Help/_About...')
FILE_MENU=_('/_File')
EXIT_MENU=_('/File/_Exit')
UPDATE_MENU=_("Check for newer versions of this program...")
CONTRIBUTORS=_("Credits")
# added 4/25/2003 - for Help files
APP_HELP_STRR=_("/_Help").replace("/_","").replace("/","").replace("(_H)","")  
# added 4/25/2003 - for Help files
APP_HELP_STR=_("/_Help").replace("/_","").replace("/","").replace("(_H)","")+"..." 
BUG_REPORT_MENU=_("Send A Bug Report")
RUN_AS_ROOT=_("Run As Root")  # added 6.18.2003

def getImage(im_file,lab_err=DIALOG_TITLE) : # GdkImlib Image loading
    try:
	if (im_file.startswith("gtk-")) : # a stock icon
		# No way to scale stock icons, so just return the default size
		return loadImage(im_file)
        myim= Image()
        myim.set_from_file(str(im_file).strip())
        return myim
    except:
        return gtk.Label(str(lab_err))



# added 4.2.2003 - common message dialogs with attractive icons, version 1.2
import IceWMCP_Dialogs
IceWMCP_Dialogs.icon_setter_method=set_special_window_icon
IceWMCP_Dialogs.pix_button_setter=getPixmapButton
def msg_info(wintitle,message):
	IceWMCP_Dialogs.message(wintitle,message.split("\n"),(DIALOG_OK,),2,1, [STOCK_OK])

def msg_warn(wintitle,message):
	IceWMCP_Dialogs.message(wintitle,message.split("\n"),(DIALOG_OK,),1,1, [STOCK_OK])

def msg_err(wintitle,message):
	IceWMCP_Dialogs.message(wintitle,message.split("\n"),(DIALOG_OK,),4,1, [STOCK_OK])

def msg_confirm(wintitle,message,d_ok=DIALOG_OK,d_cancel=DIALOG_CANCEL):
	ret=IceWMCP_Dialogs.message(wintitle,message.split("\n"),(d_ok,d_cancel,),3,1, 
		[STOCK_YES, STOCK_NO])
	if str(ret)==d_ok: return 1
	else: return 0


# new in version 0.3 - let user quickly check for software updates
def closeUpdateWin(*args):
    try:
        args[0].get_data("window").hide()
        args[0].get_data("window").destroy()
        args[0].get_data("window").unmap()
    except:
        pass


#######  VERSION  #######

this_software_version="3.1"     # must match the same variable in IceWMCP_BugReport.py

SOFTWARE_UPDATE_URL= "http://icesoundmanager.sourceforge.net/ICEWMCP_WEB_VERSION"

#######  VERSION  #######



def checkSoftUpdate(*args):
    try:
        import ICEWMCP_URLRead
        up_content=ICEWMCP_URLRead.openUrl(SOFTWARE_UPDATE_URL)
        if up_content.find(",")==-1: raise TypeError  # such as "404 Not Found"
        if len(up_content.split(","))<2: raise TypeError
        new_version=up_content.split(",")[0].replace("\n","").replace("\r","").replace("\t","").strip()
        dl_url=up_content.split(",")[1].replace("\n","").replace("\r","").replace("\t","").strip()

        w=gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.set_wmclass("icewmcontrolpanel","IceWMControlPanel")
	set_basic_window_icon(w)
        w.realize()
        w.set_title(_("IceWM Control Panel"))
        w.set_position(gtk.WIN_POS_CENTER)
        w.set_default_size(430,200)
        v=gtk.VBox(0,0)
        v.set_spacing(4)
        v.set_border_width(7)
        v.pack_start(gtk.Label(_("You are currently using version")+":   "+this_software_version+"  (IceWMCP)"),1,1,0)
        v.pack_start(gtk.Label(_("The newest version available is")+":   "+new_version+"  (IceWMCP)"),1,1,0)
        v.pack_start(gtk.Label("  "),1,1,3)
        v.pack_start(gtk.Label(_("You can download the newest version from")+": "),1,1,0)
        e=gtk.Entry()
        e.set_text(dl_url)
        v.pack_start(e,1,1,2)
        b=getPixmapButton(None, STOCK_YES ,DIALOG_OK)
	TIPS.set_tip(b,DIALOG_OK)
        b.set_data("window",w)
        w.set_data("window",w)
        w.connect("destroy",closeUpdateWin)
        b.connect("clicked",closeUpdateWin)
        v.pack_start(b,0,0,4)
        w.add(v)
        w.set_modal(1)
        w.show_all()
    except:
        msg_err(DIALOG_TITLE,_("Could not check for software update.")+"\n"+_("This feature requires an internet connection.")) 


#  moved from IceWMCP_BugReport, 4/25/2003
# maps file menu callback numbers to real application names, used by Bug-Reported and Help
app_map={
5000:["IceWMCP.py", "IceWMCP"],
# 5001:["IceWMCPCursors.py", "IceWMCP Cursors"], # disabled, 5.5.2003...tool merged
5002:["IceWMCPKeyEdit.py", "IceWMCP KeyEdit"],
5003:["IceWMCPWallpaper.py", "IceWMCP Wallpaper"],
5004:["IceWMCPWinOptions.py", "IceWMCP WinOptions"],
5005:["icesound.py", "Ice Sound Manager"],  # The help function for IceSoundManager not used, ISM has its own help
5006:["icepref.py", "IcePref2"],
5007:["icepref_td.py", "IcePref2 TD"],
5008:["pyspool.py", "PySpool"],
5009:["IceMe.py", "IceMe"],
5010:["phrozenclock.py", "PhrozenClock"],
5011:["IceWMCP_GtkPCCard.py", "GtkPCCard"],
5012:["IceWMCPMouse.py", "IceWMCP Mouse"],
5013:["IceWMCPKeyboard.py", "IceWMCP Keyboard"],
5014:["IceWMCPSystem.py", "IceWMCP System"],
5015:["IceWMCPEnergyStar.py", "IceWMCP Energy Star"],
7777:["template.py","Help Template Test"],  # for testing purposes only
}



# added 4/26/2003...allow some windows to be closed easily by pressing 'Esc' and/or 'Return' on the keyboard
# this is used for Help and About windows, and the Run Dialog, as well as the Bug-Reporter

def keyPressClose(widget, event,*args):
    if event.keyval == gtk.keysyms.Escape:
        widget.hide()
        widget.destroy()
        widget.unmap()
    elif event.keyval == gtk.keysyms.Return:
        if widget.get_data("ignore_return")==None: # some windows shouldn't close on 'Return'
            widget.hide()
            widget.destroy()
            widget.unmap()


# added 4.4.2003 - support for sending e-mail bug reports directly from within the program
# using new ICEWMCP_BugReport module, new in version 1.2

from ICEWMCP_BugReport import *



def calculateSegment(rgb_seg):
    if not rgb_seg: return 0
    if not len(rgb_seg)==2: return 0
    alpha_num_map={"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"a":10,"b":11,"c":12,"d":13,"e":14,"f":15}
    try:
        return (alpha_num_map[str(rgb_seg[0:1])]*16)+alpha_num_map[str(rgb_seg[1:2])]
    except:
        return 0

def getRGBForHex(hexstr):
     if not hexstr: return (0,0,0)
     h=hexstr.replace("#","").strip().lower()
     if not len(h)==6: return None #invalid hex string send
     r_seg=h[0:2]
     g_seg=h[2:4]
     b_seg=h[4:6]
     R=calculateSegment(r_seg)
     G=calculateSegment(g_seg)
     B=calculateSegment(b_seg)
     return (R,G,B)


# Colors and fonts needed for nicely displaying help text files, 4.25.2003
# Changed 12.6.2003, GDK provides us a colormap, no need for hidden window anymore
SOME_BLANK_COLORMAP=GDK.rgb_get_colormap()
COL_BLUE=SOME_BLANK_COLORMAP.alloc_color('SkyBlue3')
COL_PURPLE=SOME_BLANK_COLORMAP.alloc_color('DarkOrchid4')
COL_GRAY=SOME_BLANK_COLORMAP.alloc_color('RoyalBlue3')
COL_BLACK=SOME_BLANK_COLORMAP.alloc_color('black')
COL_RED=SOME_BLANK_COLORMAP.alloc_color('IndianRed3')
COL_WHITE=SOME_BLANK_COLORMAP.alloc_color('white')


# added 6.21.2003 - special fonts for help files in special locales
HELP_FONT1,HELP_FONT2,HELP_FONT3=[None,None,None]

HELP_FONTS={
		"ru":  ["Arial 14" ,   # Russian
				   "Arial 12" , 
				  "Arial Bold 18", "koi8-r"  ]   ,
		"es":  ["Helvetica 14" ,   # Spanish
				   "Helvetica 12" , 
				  "Helvetica Bold 18", "iso8859-1"  ]   ,
		"fr":  ["Helvetica 14" ,   # French
				   "Helvetica 12" , 
				  "Helvetica Bold 18", "iso8859-1"  ]   ,
		"fi":  ["Helvetica 14" ,   # Finnish
				   "Helvetica 12" , 
				  "Helvetica Bold 18", "iso8859-15"  ]   ,

		"zh_tw":  ["fixed 14" ,   # Traditional Chinese
				   "fixed 12" , 
				  "fixed 18", "big5"  ]   ,

		"all":  ["Helvetica 14" ,   # any lang., english
				   "Helvetica 12" , 
				  "Helvetica Bold 18", "iso8859-1"  ]   ,
			   }

# load special fonts if the locale requires it
MY_LANG_LOCALE=getLocaleDir().replace(os.sep,"").lower()

if HELP_FONTS.has_key(MY_LANG_LOCALE):
	my_locale_lang_fonts=HELP_FONTS[MY_LANG_LOCALE]
else : my_locale_lang_fonts=HELP_FONTS["all"]

HELP_FONT1=my_locale_lang_fonts[0]
HELP_FONT2=my_locale_lang_fonts[1]
HELP_FONT3=my_locale_lang_fonts[2]
LANGCODE=my_locale_lang_fonts[3]
global RENDER_TAG
RENDER_TAG=0




# Display help text from text file in a somewhat 'pretty' format, my own small markup language, 4.25.2003



def get_renderable_tab(mybuffer, myfont,mycolor,mylangcode):
	global RENDER_TAG
	RENDER_TAG=RENDER_TAG+1
	tagname="render-tag"+str(RENDER_TAG)
	texttag=mybuffer.create_tag(tagname)
	texttag.set_property("font",myfont)
	texttag.set_property("foreground-gdk",mycolor)
	texttag.set_property("language",mylangcode)
	return tagname

def text_buffer_insert(textbuf, mytag,mytext):
	tags=[mytag]
	textbuf.insert_with_tags_by_name(textbuf.get_end_iter(), to_utf8(mytext), *tags)


def renderHelp(texta,mesg):
	textbuf=texta.get_buffer()
	for ii in mesg:
		mline=ii.strip()
		if mline.find("[PHTITLE]")>-1:
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT3,COL_BLUE,LANGCODE),APP_HELP_STRR)
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT3,COL_BLUE,LANGCODE),":  "+mline.replace("[PHTITLE]","").strip()+"\n\n")
			continue
		elif mline.find("[PHSECTION]")>-1:
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT1,COL_PURPLE,LANGCODE),"\n"+mline.replace("[PHSECTION]","").strip()+":\n")
			continue
		elif mline.find("[PHERROR]")>-1:
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT1,COL_RED,LANGCODE),mline.replace("[PHERROR]","").strip()+"\n")
			continue
		elif mline.find("[PH-HI]")>-1:
			mlist=mline.split("[PH-HI]")
			for yy in mlist:
				if yy.find("[/PH-HI]")>-1: 
					text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT2,COL_GRAY,LANGCODE),yy[0:yy.find("[/PH-HI]")])
					text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT2,COL_BLACK,LANGCODE),yy[yy.find("[/PH-HI]")+8:len(yy)])			
				else:  
					text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT2,COL_BLACK,LANGCODE),yy)
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT2,COL_BLACK,LANGCODE),"\n")
		else:
			text_buffer_insert(textbuf, get_renderable_tab(textbuf,HELP_FONT2,COL_BLACK,LANGCODE),mline.strip()+"\n")



# added 4.1.2003 - common 'about' dialogs with uniform look, version 1.2
# 4/26/2003 - also used for displaying Help topics (displayHelp)
def commonAbout(wintitle, mesg, with_copy=1, logo="icewmcp_short.png",
                new_line=" ", editable=0, is_help=0) :
    if is_help==1:
        with_copy=0
        if str(logo).find("ism_header.png")==-1: 
		if str(logo).find("icepref2.png")==-1: 
			logo="icewmcp_short.png"
        editable=0
        mesg=mesg.replace("\r\n","\n").replace("\r","")
        if mesg.find("[PHERROR]")==-1: 
            mesg=mesg.replace("IceWM Control Panel","IceWMCP"). \
                      replace("IceWMCP","IceWM Control Panel (IceWMCP)")
        mesg=mesg.split("\n")

    if with_copy==1: 
        abouttext = "Copyright (c) 2003 by Erica Andrews\n"+\
                    "PhrozenSmoke@yahoo.com\n"+\
                    "http://icesoundmanager.sourceforge.net\n"+\
                    "License: GNU General Public License (GPL)\n\n"
    else: 
        abouttext=""

    if not is_help==1:
        abouttext=abouttext+mesg.replace("\n\n","[ICEWMCP-BREAK]").\
                                 replace("\n",new_line).\
                                 replace("[ICEWMCP-BREAK]","\n\n")+"\n"

    aboutwin=gtk.Window(gtk.WINDOW_TOPLEVEL)
    set_basic_window_icon(aboutwin)
    aboutwin.set_wmclass("icewmcontrolpanel","IceWMControlPanel")
    aboutwin.realize()
    aboutwin.set_title(wintitle)
    aboutwin.set_position(gtk.WIN_POS_CENTER)
    mainvbox=gtk.VBox(0,1)
    mainvbox.set_spacing(3)
    mainvbox.set_border_width(5)
    if str(logo).find(os.sep)==-1: 
        logo=getBaseDir()+logo
    p=getImage(logo,aboutwin)
    if not p: 
        p=gtk.Label(wintitle)
    mainvbox.pack_start(p,0,0,0)
    if is_help==1: 
        helpbox=gtk.HBox(0,0)
        helpbox.set_spacing(4)
        helpbox.pack_start(gtk.Label(" "),1,1,0)
        helpbox.pack_start(getImage(STOCK_DIALOG_INFO,""),0,0,0)
        helpbox.pack_start(gtk.Label(to_utf8(APP_HELP_STRR.upper())),0,0,0)
        helpbox.pack_start(getImage(STOCK_DIALOG_INFO,""),0,0,0)
        helpbox.pack_start(gtk.Label(" "),1,1,0)
        mainvbox.pack_start(helpbox,0,0,2)
    mainvbox.pack_start(gtk.HSeparator(),0,0,4)
    sc=gtk.ScrolledWindow()
    sctext=gtk.TextView()
    sctext.set_editable(editable)
    sctext.set_wrap_mode(gtk.WRAP_WORD)
    # Force white background, make sure all colors are viewable
    for gg in [STATE_NORMAL, STATE_ACTIVE, STATE_PRELIGHT,
					STATE_SELECTED, STATE_INSENSITIVE]:
					sctext.modify_base(gg,COL_WHITE)
    if is_help==1: 
        renderHelp(sctext,mesg)
    else: 
        sctext.get_buffer().set_text(abouttext)
    sc.add(sctext)
    mainvbox.pack_start(sc,1,1,0)
    b=Button()
    clbox=HBox(0,0)
    clbox.set_spacing(3)
    clbox.set_border_width(2)
    bimage=Image()
    if is_help==1: 
        blab=Label(DIALOG_CLOSE)
        TIPS.set_tip(b,DIALOG_CLOSE)
	bimage.set_from_stock(STOCK_CANCEL,ICON_SIZE_BUTTON)
    else: 
        blab=Label(DIALOG_OK)
        TIPS.set_tip(b,DIALOG_OK)
	bimage.set_from_stock(STOCK_YES,ICON_SIZE_BUTTON)
    clbox.pack_start(bimage,0,0,0)
    clbox.pack_start(Label("  "),0,0,0)
    clbox.pack_start(blab,0,0,0)
    clbox.pack_start(Label(" "),1,1,0)
    b.add(clbox)
    b.set_data("window",aboutwin)
    b.connect("clicked",closeUpdateWin)
    mainvbox.pack_start(b,0,0,4)    
    aboutwin.add(mainvbox)
    if not is_help==1: aboutwin.set_modal(1)
    aboutwin.connect("key-press-event",keyPressClose)
    if is_help==1: aboutwin.set_default_size(385,400)
    else: aboutwin.set_default_size(385,290)
    aboutwin.show_all()


def displayHelp(appnum=7777,*args):
	try:
		htop=app_map[appnum][1]
		fname=app_map[appnum][0].replace(".py","")+".txt"
	except:
		htop="Not Found"
		fname=None
	wtitle=APP_HELP_STRR+":  "+htop
	mesg=""
	if fname==None:
		mesg="[PHERROR]"+_("No such help topic")+" :  "+str(appnum)
	else:
		try:
			mesg=open(getHelpDirLocale()+fname).read()  # try to read locale-specific help first
			if len(mesg)==0: raise TypeError
		except:
			try:  # locale-specific help failed, try standard English
				mesg=open(getHelpDir()+fname).read()
			except:
				mesg="[PHERROR]"+_("Could not open Help file")+" :  "+str(fname)
	if fname=="icesound.txt": # special case for IceSoundManager
		if mesg.find("[PHSECTION]")>-1:
			mesg=mesg[0:mesg.find("[PHSECTION]")]+translateISM("SPANISH HELP IS AVAILABLE IN THE 'icesound-es-help.html'  FILE.")+" ("+"./doc/"+")\n\n"+mesg[mesg.find("[PHSECTION]"):len(mesg)]
	glogo="icewmcp_short.png"
	if str(fname).find("icesound")>-1: glogo=getPixDir()+"ism_header.png"
	if str(fname).find("icepref")>-1: glogo="icepref2.png"
	return commonAbout(wtitle,mesg,0,glogo,"",0,1)
	
    

# added 4.2.2003 - translators/contributors credits dialog
# NOTE: We use '['at']' instead of '@' here because this code is often reposted on the web
# and we don't want to make people's email address easy to collect for spam robots that 
# scour the web collecting email addresses

def show_credits(*args):
	commonAbout(CONTRIBUTORS,"PyGtk-2/Gtk-2 Port Started By:\n"+"David Moore <djm ['at'] e3.net.nz>"+"\n\n"+"PyGtk-2/Gtk-2 Port Completed By:\n"+"Erica Andrews <PhrozenSmoke ['at'] yahoo.com>"+"\n\n"+_("Translators")+"  (ordered by language):\n\nChinese (Traditional): Chao-Hsiung Liao <pesder.liao ['at'] msa.hinet.net>\n\nFinnish: Petteri Aimonen  <jpa ['at'] pyrmio.org> [IceMe only]\n\nFrench: Yves Perraudin  <yploglib ['at'] free.fr> [60% complete]\n\nRussian: Vasya Leushin <basileus ['at'] newmail.ru>  [Main translation, Several help files]\n\nRussian: Roman Shiryaev <mih_val ['at'] mail.ru> [Several help files]\n\nSeveral Spanish Corrections: 'Martintxo' <fundamento ['at'] sindominio.net>\n\nSpanish: Erica Andrews <PhrozenSmoke ['at'] yahoo.com>"+"\n\n_____________\n"+_("If you wish to help us with the translations, please visit the following site on the web")+":\n\nhttp://icesoundmanager.sourceforge.net/translator.php\n\nA big THANKS to all who have contributed."    ,0,"icewmcp_short.png","\n")


# SPLASH SCREEN CODE - added 4/27/2003 - common code for splash 
# screens - used by IceMe, IcePref2, and IcePref2-TD
 

global SPLASH_WIN
global SPLASH_METHOD
global SPLASH_TEXT
global SPLASH_LOGO
SPLASH_WIN=None     # reference to the gtk.Window
SPLASH_METHOD=None      # method to run while Splash is showing
SPLASH_TEXT=None    # text to display in Splash win
SPLASH_LOGO=getBaseDir()+"icewmcp_short.png"    # a default Splash logo

def setSplash(splash_meth,splash_text=to_utf8(translateCP("Loading"))+"..." ,splash_logo=getBaseDir()+"icewmcp_short.png"):
    global SPLASH_METHOD
    global SPLASH_TEXT
    global SPLASH_LOGO
    SPLASH_METHOD=splash_meth  # note: SPLASH_METHOD must make a call to 'hideSplash' when it is done
    SPLASH_TEXT=splash_text
    if not splash_logo==None: SPLASH_LOGO=splash_logo

def hideSplash(*args):
    # close the small Splash screen after loading is complete
    global SPLASH_WIN
    try:
        SPLASH_WIN.hide()
        SPLASH_WIN.destroy()
        SPLASH_WIN.unmap()
    except:
        pass
    return 0

#  This is a hidden/private method, and should not be called directly
def __initSplash(*args):
    global SPLASH_WIN
    global SPLASH_METHOD
    global SPLASH_TEXT
    global SPLASH_LOGO
    # added 4/25/2003 - Erica Andrews, new prettier start-up process, more informative - small Splash screen
    SPLASH_WIN=gtk.Window(gtk.WINDOW_POPUP)
    SPLASH_WIN.set_position(gtk.WIN_POS_CENTER)
    hb=gtk.VBox(0,0)
    hb.set_border_width(10)
    hb.set_spacing(6)
    hb.pack_start(gtk.HSeparator(),1,1,0)
    hb.pack_start(getImage(SPLASH_LOGO ,"IceWMCP") ,1,1,3)
    hb.pack_start(gtk.Label(SPLASH_TEXT) ,1,1,6)
    hb.pack_start(gtk.HSeparator(),1,1,0)
    SPLASH_WIN.add(hb)
    SPLASH_WIN.show_all()
    # added 4/25/2003 - Erica Andrews, call main initiation methods, SPLASH_METHOD
    gtk.timeout_add(50,SPLASH_METHOD)
    return 0

def showSplash(with_time=1,*args):
    if with_time==1: gtk.timeout_add(15,__initSplash)
    else: __initSplash()

#  variable to disable splash window in some apps (i.e. IceWMCPCursors), 4/29/2003
#  import icewmcp_common
#  icewmcp_common.NOSPLASH=1

global NOSPLASH
NOSPLASH=0


# added 6.18.2003 - common file selection functionality
ICEWMCP_FILE_WIN=None
ICEWMCP_LAST_FILE=getIceWMPrivConfigPath()
FILE_SELECTOR_TITLE=_("Select a file...")

def CLOSE_FILE_SELECTOR(*args):
	   try:
		ICEWMCP_FILE_WIN.hide()
		ICEWMCP_FILE_WIN.destroy()
		ICEWMCP_FILE_WIN.unmap()
	   except:
		pass

def GET_SELECTED_FILE(*args):
		gfile=ICEWMCP_FILE_WIN.get_filename()
		global ICEWMCP_LAST_FILE
		if not gfile==None: ICEWMCP_LAST_FILE=gfile
		CLOSE_FILE_SELECTOR()
		return gfile

def SET_SELECTED_FILE(file_name):
		global ICEWMCP_LAST_FILE
		ICEWMCP_LAST_FILE=str(file_name)

def SELECT_A_FILE(file_sel_cb,title=FILE_SELECTOR_TITLE,wm_class="icewmcontrolpanel",wm_name="IceWMControlPanel",widget=None,ok_button_title=None,cancel_button_title=None):
		global ICEWMCP_FILE_WIN
		ICEWMCP_FILE_WIN = FileSelection(title)
		set_basic_window_icon(ICEWMCP_FILE_WIN)
		ICEWMCP_FILE_WIN.set_wmclass(wm_class,wm_name)
		ICEWMCP_FILE_WIN.ok_button.connect('clicked', file_sel_cb)
		value = ICEWMCP_LAST_FILE
		if not widget==None: 
			ICEWMCP_FILE_WIN.ok_button.set_data("cfg_path",widget.get_data("cfg_path"))
			if value=='': value=widget.get_data("cfg_path").get_text()
		if not ok_button_title==None:
			ICEWMCP_FILE_WIN.ok_button.remove(
				ICEWMCP_FILE_WIN.ok_button.get_children()[0])
			ICEWMCP_FILE_WIN.ok_button.add(
				getPixmapButton(None, STOCK_APPLY ,str(ok_button_title))
																)
			TIPS.set_tip(ICEWMCP_FILE_WIN.ok_button, str(ok_button_title))
		if not cancel_button_title==None:
			ICEWMCP_FILE_WIN.cancel_button.remove( 
				ICEWMCP_FILE_WIN.cancel_button.get_children()[0])
			ICEWMCP_FILE_WIN.cancel_button.add(
				getPixmapButton(None, STOCK_CANCEL ,str(cancel_button_title))
																	)
			TIPS.set_tip(ICEWMCP_FILE_WIN.cancel_button,str(cancel_button_title) )
		ICEWMCP_FILE_WIN.cancel_button.connect('clicked', CLOSE_FILE_SELECTOR)
		ICEWMCP_FILE_WIN.connect("destroy",CLOSE_FILE_SELECTOR)

		#     Changed 12.21.2003 to use error-catching AND check for a None value
		#     for 'ICEWMCP_LAST_FILE' to fix BUG NUMBER: 6441772, 
		#     Reported by: Anonymous User, At: Tue Sep 30 20:40:01 2003
		try:
			if value:
				if value != '""':
					ICEWMCP_FILE_WIN.set_filename(value)
		except:
			pass
		#print "Last File:  "+str(value)
		ICEWMCP_FILE_WIN.set_data("ignore_return",1)
		ICEWMCP_FILE_WIN.connect("key-press-event", keyPressClose)
		ICEWMCP_FILE_WIN.set_modal(1)
		ICEWMCP_FILE_WIN.show_all()

# end - common file selection functionality


# added 8.25.20003, common code for getting a process ID
def get_pidof(someapp):
	try:
		fg=os.popen("pidof "+someapp)
		ff=fg.readline().replace("\n","").replace("\t","").replace("\r","").strip()
		fg.close()
		if len(ff)>0: return ff		
		return None
	except:
		return None


# Special fonts for special languages, 12.1.2003, Erica Andrews
special_fonts_map= {
	"ru":["Arial 10","Arial 9"],
	"zh_tw":["fixed 11","fixed 12"],
}


# added 12.19.2003 - Bash shell probing
# to fix BUG NUMBER: 1523884
# Reported By: david ['-at-'] jetnet.co.uk
# Reported At: Fri Oct 31 23:47:12 2003

# we need to look for a bash shell since some 
# users may not be using Bash as the default shell,
# look for a shell named 'bash', usually at /bin/bash.
# This will help ensure proper launching of applets
# and extern applications

BASH_SHELL_EXEC="bash"

for ii in ['/bin/', '/usr/bin/', '/usr/local/bin/']:
	try:
		if os.path.exists(ii+"bash"): 
				BASH_SHELL_EXEC=ii+"bash"
				break
	except:
			pass

# fallback to the Bourne ('sh') shell, if no 'bash' exec was found:
# on most systems the 'sh' shell is now Bash

if BASH_SHELL_EXEC=="bash":
	for ii in ['/bin/', '/usr/bin/', '/usr/local/bin/']:
		try:
			if os.path.exists(ii+"sh"): 
				BASH_SHELL_EXEC=ii+"sh"
				break
		except:
			pass

# added 12.24.2003, common process forking using  BASH_SHELL_EXEC
# To fix several bugs caused when users use the app under a non-Bash shell

def fork_process(some_proc):
	os.popen(BASH_SHELL_EXEC+" -c \""+str(some_proc).strip()+" &\"")


import IceWMCPRun    # THis should always be the last function defined in this module
def rundlg(*args):  # new in versin 1.1, global access to a 'Run...' dialog	
	IceWMCPRun.runwindow()


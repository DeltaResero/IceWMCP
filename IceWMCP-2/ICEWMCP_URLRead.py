######################################
# IceWM Control Panel  2.4
# 
# URL-reading module for checking for software updates via
# HTTP
#  
# Copyright 2003 by Erica Andrews 
# (PhrozenSmoke@yahoo.com)
# http://icesoundmanager.sourceforge.net
# 
# This program is distributed under the GNU General
# Public License (open source).
#######################################

import httplib
import urllib
import string
import urlparse
from threading import RLock

global __monitor
global __content
global __BROWSER
__monitor=RLock() # thread monitor, modest attempt to make URL requests thread safe
__content=""
__BROWSER="IceWMCP/2.4 (IceWMCP; IceWM Control Panel)"


def __parseUrl(my_url):
  if my_url:
    try:
      hdata=[]
      if not urlparse.urlparse(my_url)[0].lower().strip()=="http":
        return None

      hinfo=str(urlparse.urlparse(my_url)[1])
      if hinfo.find(":") == -1:
        hdata.append(hinfo.strip())
        hdata.append(80)
        hdata.append(urlparse.urlparse(my_url)[2])
        hdata.append(urlparse.urlparse(my_url)[4])
      else:  #another port was declared
        hdata.append(hinfo[0:string.find(hinfo,":")].strip())
        hdata.append(string.atoi(hinfo[string.find(hinfo,":")+1:len(hinfo)].strip()))
        hdata.append(urlparse.urlparse(my_url)[2])
        hdata.append(urlparse.urlparse(my_url)[4])
      return hdata
    except:
      return None
  else:
    return None


def openUrl(my_url,user_name=None,doGet=1,_params={},_referer="http://icesoundmanager.sourceforge.net"):
  """This method takes the following parameters: (my_url,user_name=None,doGet=1,_params={},_referer="http://icesoundmanager.sourceforge.net")"""
  global __monitor
  global __content
  __monitor.acquire()

  try:
    stat=302
    __content=""
    msg=""
    hc=None
    nextUrl=my_url
    do_get=doGet
    urlParams=_params
    refer=_referer
    beenHere=0
    base_url=my_url
    try:
      base_url=str(urlparse.urlparse(my_url)[0])+"://"+str(urlparse.urlparse(my_url)[1])
    except:
      pass

    while (stat > 299) and (stat < 400): #continue on 300-codes, break on 200, 400 or 500
      resp=[580,"Code or System Error in readPage",None,None] # standard feedback
      resp=__readPage(nextUrl,user_name,do_get,urlParams,refer)

      stat=resp[0]
      msg=resp[1]
      __content=""+str(stat)+"  "+msg  # create a minimal content text
      try:
        hc.getfile().close()
      except:
        pass
      hc=resp[3]
      urlParams={}
      refer=nextUrl
      do_get=1  # any redirects should be handled as GET
      if stat>499:
        break
      if not nextUrl.lower().startswith("http://"):
        if nextUrl.startswith("/"):
          nextUrl=str(base_url)+str(nextUrl)
        else:
          nextUrl=str(base_url)+"/"+str(nextUrl)
      # print removed
      #print "NextUrl:  "+nextUrl

      if nextUrl==refer:
        beenHere=beenHere+1  # we have been reflected back to the same Url
      if beenHere>3:  # 3 reflections is enough
        break
      # Include something here to look for 302/301 redirects
    
    if (stat>199) and (stat<300):  # we got a 200 code back, read file
      hf=None
      try:
        hf=hc.getfile()
        __content=hf.read()
      except:
        pass
      try:
        hf.close()
      except:
        pass

  finally:
    mi=__monitor.release()
    return __content


def __readPage(my_url,user_name=None,doGet=1,_params={},_referer="http://icesoundmanager.sourceforge.net"):
  global __BROWSER
  hdata=__parseUrl(str(my_url))
  if hdata:
    hc=httplib.HTTP(hdata[0],hdata[1])
    meth="GET"
    if not doGet:
      meth="POST"
    if not hdata[2]:
      hc.putrequest(meth,"/")
    else:
      content=urllib.urlencode(_params)
      if not doGet:  # using post method
        hc.putrequest(meth,hdata[2])
      else:  # using GET method
        _u=hdata[2]
        if hdata[3]:
          _u=_u+"?"+hdata[3]
        if len(_params) > 0:
          if _u.find("?") == -1:
            _u=_u+"?"+content
          else:
            if _u.endswith("&"):
              _u=_u+content
            else:
              _u=_u+"&"+content
        hc.putrequest(meth,_u)

    hc.putheader("Accept-Language","en, sp")
    hc.putheader("Accept","text/html, text/plain, text/xml, image/gif, image/x-bitmap, image/jpeg, image/pjpeg, image/png, */* ")
    hc.putheader("Accept-Charset","iso-8859-1,*,utf-8")
    hc.putheader("Host",hdata[0])
    hc.putheader("Referer",str(_referer))
    hc.putheader("User-Agent",__BROWSER)
    if doGet:
      hc.putheader("Content-length","0")
    else:
      hc.putheader("Content-length",str(len(content)))
      hc.putheader("Content-type", "application/x-www-form-urlencoded")
    hc.endheaders()
    if not doGet:
      ii=hc.send(content)
    reply, msg, hdrs = hc.getreply()
    return [reply,msg,hdrs.headers,hc]
  else: 
    return [580,"URL Parsing Error",None,None]

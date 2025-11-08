#! /usr/bin/env python

#####################
# Simple script to check for      #
# missing and obsolete 			   #
# gettext strings in IceWMCP   #
# programs.						    #
# 									   #
# PhrozenSmoke@yahoo.com  #
# 									   #
##################### 

import gettext

potdir="/Compile/IceWMCP/locale/"
es="/Compile/IceWMCP/locale/es/LC_MESSAGES/"
ru="/Compile/IceWMCP/locale/ru/LC_MESSAGES/"
fin="/Compile/IceWMCP/locale/fi/LC_MESSAGES/"

tocheck=[ru,fin,es]

names= {
  es:"spanish",
  ru:"russian",
  fin:"finnish"
		}

files=['icewmcp','icewmcp-hw','icewmcp-ism','icewmcp-iceme','icewmcp-icepref']
officials={}

alias_pot = {
	"icewmcp":"icewmcp",
	"icewmcp-hw":"icewmcp-hw",
	"icewmcp-ism":"icesound",
	"icewmcp-iceme":"iceme",
	"icewmcp-icepref":"icepref",
		   }

def run():
	for ii in files:  # get official listings
		myfile=potdir+alias_pot[ii]+".pot"
		try:
			f=open(myfile)
			ff=f.read().split("\n")
			f.close()
			d={}
			recon=0
			saved=""
			line_count=-1
			for yy in ff:
				line_count=line_count+1
				word=yy
				if word.strip().startswith("#"): continue
				if word.strip()=='': continue
				if word.strip().startswith("msgid"):
					recon=1
				if word.strip().startswith("msgstr"): recon=0
				if recon==1:
					gprop=word.replace("msgid","").strip()
					#print gprop
					gprop=gprop[1:gprop.rfind("\"")].replace("\\\"","\"").replace("\\n","")
					if not gprop=='':
						if saved=='': saved=gprop
						else: saved=saved+"\n"+gprop
					continue
				if word.strip().startswith("msgstr"):
				  if not saved=='':
					if not d.has_key(saved):
						d[saved]=str(line_count)
					else:
						print "\nWarning: DUPLICATE msgid in .pot ("+myfile+") - line ["+str(line_count)+"] : '"+saved +"'    ALSO found on line ["+d[saved]+"] \n"
				  recon=0
				  saved=""
			officials[ii]=d
			#print str(d.keys()[0:20])
		except:
			print "\nWarning: could not open POT file : "+myfile

	for yy in tocheck:
		print '\n\n____________________________\n\n'
		lname=names[yy].upper()  # country name
		for ii in files:  # get locale-based listings
			myfile=yy+ii
			moname=myfile+'.mo'
			potcomp=officials[ii]
			potname=alias_pot[ii]+".pot"
			try:
				gettext.install(myfile)
			except:
				print "\nGETTEXT CATALOG NOT FOUND: "+moname+" (skipping)\n"
				continue
			g=gettext._translations[moname]
			gcat=g._catalog

			for zz in gcat.keys():
				#if zz.find("a simple")>-1: print "**** HERE1 *** \n"+zz
				if zz=='': continue
				if not potcomp.has_key(zz):
					print "\n"+lname+" - OBSOLETE: ["+moname+"]   has key  ['"+zz+"'] not in ["+potname+"]\n"
					print "#: "+ii
					print "\nmsgid \""+zz.replace("\"","\\\"").replace("\n","\"\n\"")+"\""
					print "msgstr \"\"\n\n"

		for ii in files:  # get locale-based listings
			myfile=yy+ii
			moname=myfile+'.mo'
			potcomp=officials[ii]
			potname=alias_pot[ii]+".pot"
			try:
				gettext.install(myfile)
			except:
				print "\nGETTEXT CATALOG NOT FOUND: "+moname+" (skipping)\n"
				continue
			g=gettext._translations[moname]
			gcat=g._catalog
			for zz in potcomp.keys():
				#if zz.find("a simple")>-1: print "**** HERE *** \n"+zz
				if not gcat.has_key(zz):
					print "\n"+lname+" - MISSING: ["+moname+"]   does not have key  ['"+zz+"'] found in ["+potname+"]\n"
					print "#: "+ii
					print "\nmsgid \""+zz.replace("\"","\\\"").replace("\n","\"\n\"")+"\""
					print "msgstr \"\"\n\n"

		for ii in files:  # get locale-based listings
			myfile=yy+ii
			moname=myfile+'.mo'
			potcomp=officials[ii]
			potname=alias_pot[ii]+".pot"
			try:
				gettext.install(myfile)
			except:
				print "\nGETTEXT CATALOG NOT FOUND: "+moname+" (skipping)\n"
				continue
			g=gettext._translations[moname]
			gcat=g._catalog
			print "\nCATALOGS: "+ii+".mo "+ str(len(gcat))+"  :  "+potname+"  "+str(len(potcomp))


if __name__== "__main__" :
	run()
LOCALEDIR=/usr/share/IceWMCP/locale

all: mo

#create all mo files
mo:
	if test -f  icewmcp-iceme.po; then\
		msgfmt -o `pwd`/LC_MESSAGES/icewmcp-iceme.mo icewmcp-iceme.po ; \
	fi;
	if test -f icewmcp-icepref.po; then\
		msgfmt -o `pwd`/LC_MESSAGES/icewmcp-icepref.mo icewmcp-icepref.po ; \
	fi;
	if test -f icewmcp-ism.po; then\
		msgfmt -o `pwd`/LC_MESSAGES/icewmcp-ism.mo icewmcp-ism.po ; \
	fi;
	if test -f icewmcp.po; then\
		msgfmt -o `pwd`/LC_MESSAGES/icewmcp.mo icewmcp.po ; \
	fi;
	if test -f icewmcp-hw.po; then\
		msgfmt -o `pwd`/LC_MESSAGES/icewmcp-hw.mo icewmcp-hw.po ; \
	fi;





#install mo files
install: mo
	if test -f icewmcp.mo; then\
		install -D --mode=644 icewmcp.mo $(LOCALEDIR)/zh_TW/LC_MESSAGES/icewmcp.mo ; \
	fi;
	if test -f icewmcp-icepref.mo; then\
		install -D --mode=644 icewmcp-icepref.mo $(LOCALEDIR)/zh_TW/LC_MESSAGES/icewmcp-icepref.mo ; \
	fi;
	if test -f icewmcp-ism.mo; then\
		install -D --mode=644 icewmcp-ism.mo $(LOCALEDIR)/zh_TW/LC_MESSAGES/icewmcp-ism.mo ; \
	fi;
	if test -f icewmcp-iceme.mo; then\
		install -D --mode=644 icewmcp-iceme.mo $(LOCALEDIR)/zh_TW/LC_MESSAGES/icewmcp-iceme.mo ; \
	fi;
	if test -f icewmcp-hw.mo; then\
		install -D --mode=644 icewmcp-hw.mo $(LOCALEDIR)/zh_TW/LC_MESSAGES/icewmcp-hw.mo ; \
	fi;

clean:
	rm -f *.mo
	rm -f POTFILES.in
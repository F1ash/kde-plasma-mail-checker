DESTDIR=/
INSTALL=install -D -m 0644 -p
LRELEASE=/usr/bin/lrelease-qt4
REALNAME=plasmaMailChecker
GITVER=`date +%Y%m%d`
PKGNAME=kde-plasma-mail-checker-git$(GITVER)

build: contents/code/ru.qm
	@echo "Nothing build"

install: build
	$(INSTALL) metadata.desktop $(DESTDIR)/usr/share/kde4/services/plasma-applet-plasmaMailChecker.desktop
	$(INSTALL) contents/code/main.py $(DESTDIR)/usr/share/kde4/apps/$(REALNAME)/code/main.py
	$(INSTALL) contents/code/ru.qm $(DESTDIR)/usr/share/kde4/apps/$(REALNAME)/code/ru.qm
	$(INSTALL) contents/icons/mailChecker.png $(DESTDIR)/usr/share/kde4/apps/$(REALNAME)/icons/mailChecker.png
	$(INSTALL) contents/icons/mailChecker_stop.png $(DESTDIR)/usr/share/kde4/apps/$(REALNAME)/icons/mailChecker_stop.png
	$(INSTALL) contents/icons/mailChecker_web.png $(DESTDIR)/usr/share/kde4/apps/$(REALNAME)/icons/mailChecker_web.png

contents/code/ru.qm:
	$(LRELEASE) contents/code/ru.ts -qm contents/code/ru.qm

clean:
	rm -rf $(DESTDIR)/share/kde4/services/plasma-applet-plasmaMailChecker.desktop
	rm -rf $(DESTDIR)/share/kde4/apps/$(REALNAME)

tarboll:
	rm -rf $(PKGNAME)
	mkdir -p $(PKGNAME)/
	cp -r contents $(PKGNAME)/
	cp metadata.desktop $(PKGNAME)/
	cp README* $(PKGNAME)/
	tar cfjv $(PKGNAME).tar.bz2 $(PKGNAME)

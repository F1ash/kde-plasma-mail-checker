DESTDIR=/usr
INSTALL=install -D -m 0644 -p
LRELEASE=/usr/bin/lrelease-qt4
APP_NAME=kde-plasma-mail-checker
PLASMA=plasma/plasmoids

build: contents/code/ru.qm
	@echo "Nothing to build"

install: build
	$(INSTALL) metadata.desktop $(DESTDIR)/share/kde4/services/$(APP_NAME).desktop
	$(INSTALL) contents/code/main.py $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)/code/main.py
	$(INSTALL) contents/code/ru.qm $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)/code/ru.qm
	$(INSTALL) contents/icons/mailChecker.png $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)/icons/mailChecker.png
	$(INSTALL) contents/icons/mailChecker_stop.png $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)/icons/mailChecker_stop.png
	$(INSTALL) contents/icons/mailChecker_web.png $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)/icons/mailChecker_web.png

contents/code/ru.qm:
	$(LRELEASE) contents/code/ru.ts -qm contents/code/ru.qm

clean:
	rm -rf $(DESTDIR)/share/kde4/services/$(APP_NAME).desktop
	rm -rf $(DESTDIR)/share/kde4/apps/$(PLASMA)/$(APP_NAME)

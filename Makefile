DESTDIR=/usr
INSTALL=install -D -m 0644 -p
LRELEASE=/usr/bin/lrelease-qt4
APP_NAME=kde-plasma-mail-checker
KAPPS=share/kde4/apps
KSERV=share/kde4/services
PLASMA=plasma/plasmoids
CODE=contents/code
ICONS=contents/icons

build: contents/code/ru.qm
	@echo "Nothing to build"

install: build
	$(INSTALL) metadata.desktop $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	$(INSTALL) $(CODE)/main.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/main.py
	$(INSTALL) $(CODE)/mail.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/mail.py
	$(INSTALL) $(CODE)/AkonadiMod.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiMod.py
	$(INSTALL) $(CODE)/Functions.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Functions.py
	$(INSTALL) $(CODE)/Examples.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Examples.py
	$(INSTALL) $(CODE)/MailProgExec.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailProgExec.py
	$(INSTALL) $(CODE)/imapUTF7.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/imapUTF7.py
	$(INSTALL) $(CODE)/ru.qm $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ru.qm
	$(INSTALL) $(ICONS)/mailChecker.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png
	$(INSTALL) $(ICONS)/mailChecker_stop.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_stop.png
	$(INSTALL) $(ICONS)/mailChecker_web.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_web.png

contents/code/ru.qm:
	$(LRELEASE) $(CODE)/ru.ts -qm $(CODE)/ru.qm

clean:
	rm -rf $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	rm -rf $(DESTDIR)/v/$(PLASMA)/$(APP_NAME)

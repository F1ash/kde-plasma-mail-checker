DESTDIR=/usr
INSTALL=install -D -m 0644 -p
LRELEASE=/usr/bin/lrelease-qt4
APP_NAME=kde-plasma-mail-checker
KAPPS=share/kde4/apps
KSERV=share/kde4/services
PLASMA=plasma/plasmoids
CODE=contents/code
ICONS=contents/icons
ICON_PATH=/usr/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png

build: contents/code/ru.qm
	@echo "Nothing to build"

install: build
	sed -i 's|Icon=.*|Icon='$(ICON_PATH)'|' metadata.desktop
	$(INSTALL) metadata.desktop $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	$(INSTALL) metadata.desktop $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/metadata.desktop
	$(INSTALL) EXAMPLES $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/EXAMPLES
	$(INSTALL) $(CODE)/main.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/main.py
	$(INSTALL) $(CODE)/mail.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/mail.py
	$(INSTALL) $(CODE)/AkonadiMod.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiMod.py
	$(INSTALL) $(CODE)/Functions.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Functions.py
	$(INSTALL) $(CODE)/MailFunc.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailFunc.py
	$(INSTALL) $(CODE)/Examples.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Examples.py
	$(INSTALL) $(CODE)/MailProgExec.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailProgExec.py
	$(INSTALL) $(CODE)/IdleMailing.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/IdleMailing.py
	$(INSTALL) $(CODE)/imapUTF7.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/imapUTF7.py
	$(INSTALL) $(CODE)/Translator.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Translator.py
	$(INSTALL) $(CODE)/Buttons.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Buttons.py
	$(INSTALL) $(CODE)/Filter.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Filter.py
	$(INSTALL) $(CODE)/ru.qm $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ru.qm
	$(INSTALL) $(CODE)/templates $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/templates
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Proxy.py
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/__init__.py
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Box.py
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Mail.py
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/MainWindow.py
	$(INSTALL) $(ICONS)/mailChecker.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png
	$(INSTALL) $(ICONS)/mailChecker_stop.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_stop.png
	$(INSTALL) $(ICONS)/mailChecker_web.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_web.png

contents/code/ru.qm:
	$(LRELEASE) $(CODE)/ru.ts -qm $(CODE)/ru.qm

clean:
	rm -rf $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	rm -rf $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)

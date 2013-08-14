PREFIX=/usr
INSTALL=install -D -m 0644 -p
LRELEASE=/usr/bin/lrelease-qt4
APP_NAME=kde-plasma-mail-checker
KAPPS=share/kde4/apps
KSERV=share/kde4/services
PLASMA=plasma/plasmoids
CODE=contents/code
ICONS=contents/icons
ICON_PATH=$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png

build: contents/code/ru.qm
	@echo "Nothing to build"

install: build
	sed -i 's|Icon=.*|Icon='$(ICON_PATH)'|' metadata.desktop

	$(INSTALL) metadata.desktop $(DESTDIR)$(PREFIX)/$(KSERV)/$(APP_NAME).desktop
	$(INSTALL) metadata.desktop $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/metadata.desktop
	$(INSTALL) EXAMPLES $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/EXAMPLES

	$(INSTALL) $(CODE)/AkonadiMod.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiMod.py
	$(INSTALL) $(CODE)/AkonadiObjects.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiObjects.py
	$(INSTALL) $(CODE)/AkonadiResources.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiResources.py
	$(INSTALL) $(CODE)/AppletSettings.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AppletSettings.py
	$(INSTALL) $(CODE)/Buttons.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Buttons.py
	$(INSTALL) $(CODE)/CheckMailThread.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/CheckMailThread.py
	$(INSTALL) $(CODE)/ColorSets.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ColorSets.py
	$(INSTALL) $(CODE)/EditAccounts.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditAccounts.py
	$(INSTALL) $(CODE)/EditList.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditList.py
	$(INSTALL) $(CODE)/EditParam.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditParam.py
	$(INSTALL) $(CODE)/EditParamOBJ.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditParamOBJ.py
	$(INSTALL) $(CODE)/Examples.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Examples.py
	$(INSTALL) $(CODE)/Filter.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Filter.py
	$(INSTALL) $(CODE)/FontNColor.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/FontNColor.py
	$(INSTALL) $(CODE)/Functions.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Functions.py
	$(INSTALL) $(CODE)/IdleMailing.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/IdleMailing.py
	$(INSTALL) $(CODE)/imapUTF7.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/imapUTF7.py
	$(INSTALL) $(CODE)/mail.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/mail.py
	$(INSTALL) $(CODE)/main.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/main.py
	$(INSTALL) $(CODE)/MailFunc.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailFunc.py
	$(INSTALL) $(CODE)/MailProgExec.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailProgExec.py
	$(INSTALL) $(CODE)/Passwd.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Passwd.py
	$(INSTALL) $(CODE)/Proxy.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Proxy.py
	$(INSTALL) $(CODE)/ReceiveParams.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ReceiveParams.py
	$(INSTALL) $(CODE)/ru.qm $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ru.qm
	$(INSTALL) $(CODE)/SendParams.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/SendParams.py
	$(INSTALL) $(CODE)/templates $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/templates
	$(INSTALL) $(CODE)/TextFunc.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/TextFunc.py
	$(INSTALL) $(CODE)/Translator.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Translator.py
	$(INSTALL) $(CODE)/WaitIdle.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/WaitIdle.py

	$(INSTALL) $(CODE)/Viewer/__init__.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/__init__.py
	$(INSTALL) $(CODE)/Viewer/Box.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Box.py
	$(INSTALL) $(CODE)/Viewer/Mail.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Mail.py
	$(INSTALL) $(CODE)/Viewer/MainWindow.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/MainWindow.py

	$(INSTALL) $(CODE)/Sender/__init__.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Sender/__init__.py
	$(INSTALL) $(CODE)/Sender/mailSender.py $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Sender/mailSender.py

	$(INSTALL) $(ICONS)/mailChecker.png $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png
	$(INSTALL) $(ICONS)/mailChecker_stop.png $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_stop.png
	$(INSTALL) $(ICONS)/mailChecker_web.png $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_web.png
	# prepared for %doc
	$(INSTALL) $(ICONS)/Licenses ./Licenses

contents/code/ru.qm:
	$(LRELEASE) $(CODE)/ru.ts -qm $(CODE)/ru.qm

clean:
	rm -rf $(DESTDIR)$(PREFIX)/$(KSERV)/$(APP_NAME).desktop
	rm -rf $(DESTDIR)$(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)

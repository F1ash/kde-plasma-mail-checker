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

	$(INSTALL) metadata.desktop $(PREFIX)/$(KSERV)/$(APP_NAME).desktop
	$(INSTALL) metadata.desktop $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/metadata.desktop
	$(INSTALL) EXAMPLES $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/EXAMPLES

	$(INSTALL) $(CODE)/AkonadiMod.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiMod.py
	$(INSTALL) $(CODE)/AkonadiObjects.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiObjects.py
	$(INSTALL) $(CODE)/AkonadiResources.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AkonadiResources.py
	$(INSTALL) $(CODE)/AppletSettings.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/AppletSettings.py
	$(INSTALL) $(CODE)/Buttons.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Buttons.py
	$(INSTALL) $(CODE)/CheckMailThread.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/CheckMailThread.py
	$(INSTALL) $(CODE)/ColorSets.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ColorSets.py
	$(INSTALL) $(CODE)/EditAccounts.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditAccounts.py
	$(INSTALL) $(CODE)/EditList.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditList.py
	$(INSTALL) $(CODE)/EditParam.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditParam.py
	$(INSTALL) $(CODE)/EditParamOBJ.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/EditParamOBJ.py
	$(INSTALL) $(CODE)/Examples.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Examples.py
	$(INSTALL) $(CODE)/Filter.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Filter.py
	$(INSTALL) $(CODE)/FontNColor.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/FontNColor.py
	$(INSTALL) $(CODE)/Functions.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Functions.py
	$(INSTALL) $(CODE)/IdleMailing.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/IdleMailing.py
	$(INSTALL) $(CODE)/imapUTF7.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/imapUTF7.py
	$(INSTALL) $(CODE)/mail.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/mail.py
	$(INSTALL) $(CODE)/main.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/main.py
	$(INSTALL) $(CODE)/MailFunc.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailFunc.py
	$(INSTALL) $(CODE)/MailProgExec.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/MailProgExec.py
	$(INSTALL) $(CODE)/Passwd.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Passwd.py
	$(INSTALL) $(CODE)/Proxy.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Proxy.py
	$(INSTALL) $(CODE)/ReceiveParams.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ReceiveParams.py
	$(INSTALL) $(CODE)/ru.qm $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/ru.qm
	$(INSTALL) $(CODE)/SendParams.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/SendParams.py
	$(INSTALL) $(CODE)/templates $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/templates
	$(INSTALL) $(CODE)/TextFunc.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/TextFunc.py
	$(INSTALL) $(CODE)/Translator.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Translator.py
	$(INSTALL) $(CODE)/WaitIdle.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/WaitIdle.py

	$(INSTALL) $(CODE)/Viewer/__init__.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/__init__.py
	$(INSTALL) $(CODE)/Viewer/Box.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Box.py
	$(INSTALL) $(CODE)/Viewer/Mail.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/Mail.py
	$(INSTALL) $(CODE)/Viewer/MainWindow.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Viewer/MainWindow.py

	$(INSTALL) $(CODE)/Sender/__init__.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Sender/__init__.py
	$(INSTALL) $(CODE)/Sender/mailSender.py $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/Sender/mailSender.py

	$(INSTALL) $(ICONS)/Licenses $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/Licenses
	$(INSTALL) $(ICONS)/mailChecker.png $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker.png
	$(INSTALL) $(ICONS)/mailChecker_stop.png $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_stop.png
	$(INSTALL) $(ICONS)/mailChecker_web.png $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/mailChecker_web.png

contents/code/ru.qm:
	$(LRELEASE) $(CODE)/ru.ts -qm $(CODE)/ru.qm

clean:
	rm -rf $(PREFIX)/$(KSERV)/$(APP_NAME).desktop
	rm -rf $(PREFIX)/$(KAPPS)/$(PLASMA)/$(APP_NAME)

# -*- coding: utf-8 -*-
#  main.py
#  
#  Copyright 2012 Flash <kaperang07@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

try :
	from Functions import *
	from MailProgExec import MailProgExec
	from Filter import Filters
	from Proxy import ProxySettings
	from Examples import Examples
	from Translator import Translator
	from IdleMailing import IdleMailing
	from EditAccounts import EditAccounts
	from WaitIdle import WaitIdle
	from AppletSettings import AppletSettings
	from FontNColor import Font_n_Colour
	from CheckMailThread import ThreadCheckMail
	from Passwd import PasswordManipulate
	from AkonadiResources import AkonadiResources, A
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from PyKDE4.kdecore import KGlobal, KComponentData
	from PyKDE4.kdeui import *
	from PyKDE4.plasma import Plasma
	from PyKDE4 import plasmascript
	import string, time, os.path, sys
	#sys.stderr = open('/dev/shm/errorMailChecker' + str(time.time()) + '.log','w')
	sys.stdout = open('/tmp/outMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
except Exception, err :
	print "Exception: ", err
finally:
	'O`key'
	pass

class plasmaMailChecker(plasmascript.Applet):
	idleThreadMessage = pyqtSignal(dict)
	idleingStopped = pyqtSignal()
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self,parent)

		self.initStat = False
		self.checkResult = []
		self.idleMailingList = []
		self.ErrorMsg = ''

		self.panelIcon = Plasma.IconWidget()
		self.icon = Plasma.IconWidget()
		self.listNewMail = []
		self.connectIconsFlag = False
		self.appletName = 'plasmaMailChecker'
		self.tr = Translator()
		self.Settings = QSettings(self.appletName,self.appletName)
		self.GeneralLOCK = QMutex()
		self.someFunctions = Required(self)
		self.initPrefixAndSuffix()

	def init(self):
		self.setHasConfigurationInterface(True)
		self.T = ThreadCheckMail(self)

		self.Timer = QTimer()
		self.Timer.timeout.connect(self._refreshData)

		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.layout.setSpacing(0)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())

		if not os.path.exists(self.kdehome+"share/apps/kde-plasma-mail-checker/kde-plasma-mail-checker.notifyrc"):
			if os.path.exists(self.kdehome+"share/apps"):
				self.createNotifyrc(self.kdehome)
		self.stopIconPath = self.user_or_sys('contents/icons/mailChecker_stop.png')
		self.webIconPath = self.user_or_sys('contents/icons/mailChecker_web.png')
		self.usualIconPath = self.user_or_sys('contents/icons/mailChecker.png')

		if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
			self.titleLayout = QGraphicsLinearLayout()
			self.titleLayout.setOrientation(Qt.Horizontal)

			self.TitleDialog = Plasma.Label()
			self.initTitle()
			self.titleLayout.addItem(self.TitleDialog)

			self.icon.setIcon(self.stopIconPath)
			self.icon.setMaximumSize(35.0, 35.0)
			self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + self.headerSuff)
			self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			self.titleLayout.addItem(self.icon)

			self.layout.setOrientation(Qt.Vertical)
			self.layout.addItem(self.titleLayout)
			self.createDialogWidget()
		else:
			self.createIconWidget()

		self.setLayout(self.layout)

		self.connect(self.applet, SIGNAL('destroyed()'), self.eventClose)
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.connect(self, SIGNAL('access'), self.processInit)
		self.connect(self, SIGNAL('killThread'), self.killMailCheckerThread)
		self.idleThreadMessage.connect(self.idleMessage)
		self.idleingStopped.connect(self.idleingStoppedEvent)

		self.maxShowedMail = int(self.initValue('MaxShowedMail', '1024'))
		AutoRun = self.initValue('AutoRun')
		if AutoRun != '0' :
			#QApplication.postEvent(self, QEvent(QEvent.User))
			self.Timer1 = QTimer()
			self.Timer1.setSingleShot(True)
			self.Timer1.timeout.connect(self.enterPassword)
			self.Timer1.start(2000)

	def initTitle(self):
		self.VERSION = '~'
		fileName = self.user_or_sys('metadata.desktop')
		if os.path.exists(fileName) :
			with open(fileName) as f :
				str_ = f.read()
			list_ = string.split(str_, '\n')
			for _str in list_ :
				if 'X-KDE-PluginInfo-Version' in _str :
					self.VERSION = string.split(_str, '=')[1]
					break
		#print dateStamp() , "VERSION : ", self.VERSION
		self.version = self.initValue('ShowVersion', '1')
		if int(self.version) > 0 :
			self.title = self.tr._translate('M@il Checker') + '\n' + self.VERSION + ' ' + lang[0][:2]
		else :
			self.title = self.tr._translate('M@il Checker')
		self.TitleDialog.setStyleSheet(self.headerColourStyle)
		self.TitleDialog.setText(self.headerPref + self.title + self.headerSuff)

	def initColourAndFont(self):
		self.headerFontVar = self.initValue('headerFont', ' ')
		self.headerSizeVar = self.initValue('headerSize')
		self.headerBoldVar = self.initValue('headerBold')
		self.headerItalVar = self.initValue('headerItal')
		self.headerColourVar = self.initValue('headerColour')

		self.accountFontVar = self.initValue('accountFont', ' ')
		self.accountSizeVar = self.initValue('accountSize')
		self.accountBoldVar = self.initValue('accountBold')
		self.accountItalVar = self.initValue('accountItal')
		self.accountColourVar = self.initValue('accountColour')
		self.accountSFontVar = self.initValue('accountSFont', ' ')
		self.accountSSizeVar = self.initValue('accountSSize')
		self.accountSBoldVar = self.initValue('accountSBold')
		self.accountSItalVar = self.initValue('accountSItal')
		self.accountSColourVar = self.initValue('accountSColour')

		self.accountToolTipFontVar = self.initValue('accountToolTipFont', ' ')
		self.accountToolTipSizeVar = self.initValue('accountToolTipSize')
		self.accountToolTipBoldVar = self.initValue('accountToolTipBold')
		self.accountToolTipItalVar = self.initValue('accountToolTipItal')
		self.accountToolTipColourVar = self.initValue('accountToolTipColour')
		self.accountToolTipSFontVar = self.initValue('accountToolTipSFont', ' ')
		self.accountToolTipSSizeVar = self.initValue('accountToolTipSSize')
		self.accountToolTipSBoldVar = self.initValue('accountToolTipSBold')
		self.accountToolTipSItalVar = self.initValue('accountToolTipSItal')
		self.accountToolTipSColourVar = self.initValue('accountToolTipSColour')

		self.countFontVar = self.initValue('countFont', ' ')
		self.countSizeVar = self.initValue('countSize')
		self.countBoldVar = self.initValue('countBold')
		self.countItalVar = self.initValue('countItal')
		self.countColourVar = self.initValue('countColour')
		self.countSFontVar = self.initValue('countSFont', ' ')
		self.countSSizeVar = self.initValue('countSSize')
		self.countSBoldVar = self.initValue('countSBold')
		self.countSItalVar = self.initValue('countSItal')
		self.countSColourVar = self.initValue('countSColour')

		self.countToolTipFontVar = self.initValue('countToolTipFont', ' ')
		self.countToolTipSizeVar = self.initValue('countToolTipSize')
		self.countToolTipBoldVar = self.initValue('countToolTipBold')
		self.countToolTipItalVar = self.initValue('countToolTipItal')
		self.countToolTipColourVar = self.initValue('countToolTipColour')
		self.countToolTipSFontVar = self.initValue('countToolTipSFont', ' ')
		self.countToolTipSSizeVar = self.initValue('countToolTipSSize')
		self.countToolTipSBoldVar = self.initValue('countToolTipSBold')
		self.countToolTipSItalVar = self.initValue('countToolTipSItal')
		self.countToolTipSColourVar = self.initValue('countToolTipSColour')

		self.fieldBoxFontVar = self.initValue('fieldBoxFont', ' ')
		self.fieldBoxSizeVar = self.initValue('fieldBoxSize')
		self.fieldBoxBoldVar = self.initValue('fieldBoxBold')
		self.fieldBoxItalVar = self.initValue('fieldBoxItal')
		self.fieldBoxColourVar = self.initValue('fieldBoxColour')

		self.fieldFromFontVar = self.initValue('fieldFromFont', ' ')
		self.fieldFromSizeVar = self.initValue('fieldFromSize')
		self.fieldFromBoldVar = self.initValue('fieldFromBold')
		self.fieldFromItalVar = self.initValue('fieldFromItal')
		self.fieldFromColourVar = self.initValue('fieldFromColour')

		self.fieldSubjFontVar = self.initValue('fieldSubjFont', ' ')
		self.fieldSubjSizeVar = self.initValue('fieldSubjSize')
		self.fieldSubjBoldVar = self.initValue('fieldSubjBold')
		self.fieldSubjItalVar = self.initValue('fieldSubjItal')
		self.fieldSubjColourVar = self.initValue('fieldSubjColour')

		self.fieldDateFontVar = self.initValue('fieldDateFont', ' ')
		self.fieldDateSizeVar = self.initValue('fieldDateSize')
		self.fieldDateBoldVar = self.initValue('fieldDateBold')
		self.fieldDateItalVar = self.initValue('fieldDateItal')
		self.fieldDateColourVar = self.initValue('fieldDateColour')

		self.headerColourStyle = self.getRGBaStyle(QString(self.headerColourVar).toUInt())
		self.accountColourStyle = self.getRGBaStyle(QString(self.accountColourVar).toUInt())
		self.accountSColourStyle = self.getRGBaStyle(QString(self.accountSColourVar).toUInt())
		self.accountToolTipColourStyle = self.getRGBaStyle(QString(self.accountToolTipColourVar).toUInt())
		self.accountToolTipSColourStyle = self.getRGBaStyle(QString(self.accountToolTipSColourVar).toUInt())
		self.countColourStyle = self.getRGBaStyle(QString(self.countColourVar).toUInt())
		self.countSColourStyle = self.getRGBaStyle(QString(self.countSColourVar).toUInt())
		self.countToolTipColourStyle = self.getRGBaStyle(QString(self.countToolTipColourVar).toUInt())
		self.countToolTipSColourStyle = self.getRGBaStyle(QString(self.countToolTipSColourVar).toUInt())

	def getRGBaStyle(self, (colour, yes)):
		if yes :
			style = 'QLabel { color: rgba' + str(QColor().fromRgba(colour).getRgb()) + ';} '
		else :
			style = 'QLabel { color: rgba' + self.getSystemColor() + ';} '
		return style

	def initValue(self, key_, defaultValue = ''):
		if self.Settings.contains(key_) :
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return self.Settings.value(key_).toString()
		else :
			if defaultValue == '' :
				defaultValue = self.getSystemColor('int')
			self.Settings.setValue(key_, QVariant(defaultValue))
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return defaultValue

	def getSystemColor(self, key_ = ''):
		currentBrush = QPalette().windowText()
		colour = currentBrush.color()
		if key_ == 'int' :
			#print dateStamp() ,  colour.rgba()
			return str(colour.rgba())
		else :
			#print dateStamp() ,  str(colour.getRgb())
			return str(colour.getRgb())

	def cursive_n_bold(self, bold, italic):
		pref = ''
		suff = ''
		if bold == '1' :
			pref += '<b>'; suff += '</b>'
		if italic == '1' :
			pref = '<i>' + pref; suff += '</i>'
		return pref, suff

	def getPrefixAndSuffix(self, b, i, font, tooltip = False, colour = 0):
		pref, suff = self.cursive_n_bold(b, i)
		prefix = '<font face="' + font
		if tooltip :
			colourHTML = str( QColor(QString(colour).toUInt()[0]).name() )
			prefix += '" color="' + colourHTML
		prefix += '" >' + pref
		suffix = suff + '</font>'
		return prefix, suffix

	def initPrefixAndSuffix(self):
		self.initColourAndFont()
		self.headerPref, self.headerSuff = self.getPrefixAndSuffix( \
							self.headerBoldVar, self.headerItalVar, \
							self.headerFontVar)
		self.accPref, self.accSuff = self.getPrefixAndSuffix( \
							self.accountBoldVar, self.accountItalVar, \
							self.accountFontVar)
		self.accSPref, self.accSSuff = self.getPrefixAndSuffix( \
							self.accountSBoldVar, self.accountSItalVar, \
							self.accountSFontVar)
		self.accTTPref, self.accTTSuff = self.getPrefixAndSuffix( \
							self.accountToolTipBoldVar, self.accountToolTipItalVar, \
							self.accountToolTipFontVar, True, self.accountToolTipColourVar)
		self.accTTSPref, self.accTTSSuff = self.getPrefixAndSuffix( \
							self.accountToolTipSBoldVar, self.accountToolTipSItalVar, \
							self.accountToolTipSFontVar, True, self.accountToolTipSColourVar)
		self.countPref, self.countSuff = self.getPrefixAndSuffix( \
							self.countBoldVar, self.countItalVar, \
							self.countFontVar)
		self.countSPref, self.countSSuff = self.getPrefixAndSuffix( \
							self.countSBoldVar, self.countSItalVar, \
							self.countFontVar)
		self.countTTPref, self.countTTSuff = self.getPrefixAndSuffix( \
							self.countToolTipBoldVar, self.countToolTipItalVar, \
							self.countToolTipFontVar, True, self.countToolTipColourVar)
		self.countTTSPref, self.countTTSSuff = self.getPrefixAndSuffix( \
							self.countToolTipSBoldVar, self.countToolTipSItalVar, \
							self.countToolTipSFontVar, True, self.countToolTipSColourVar)
		self.fieldBoxPref, self.fieldBoxSuff = self.getPrefixAndSuffix( \
							self.fieldBoxBoldVar, self.fieldBoxItalVar, \
							self.fieldBoxFontVar, True, self.fieldBoxColourVar)
		self.fieldFromPref, self.fieldFromSuff = self.getPrefixAndSuffix( \
							self.fieldFromBoldVar, self.fieldFromItalVar, \
							self.fieldFromFontVar, True, self.fieldFromColourVar)
		self.fieldSubjPref, self.fieldSubjSuff = self.getPrefixAndSuffix( \
							self.fieldSubjBoldVar, self.fieldSubjItalVar, \
							self.fieldSubjFontVar, True, self.fieldSubjColourVar)
		self.fieldDatePref, self.fieldDateSuff = self.getPrefixAndSuffix( \
							self.fieldDateBoldVar, self.fieldDateItalVar, \
							self.fieldDateFontVar, True, self.fieldDateColourVar)
		self.mailAttrColor = ((self.fieldFromPref, self.fieldFromSuff), \
								(self.fieldSubjPref, self.fieldSubjSuff), \
								(self.fieldDatePref, self.fieldDateSuff))

	def customEvent(self, event):
		if event.type() == QEvent.User :
			self.enterPassword()
		elif event.type() == 1011 :
			self._refreshData()
		elif event.type() == 1010 :
			self.emit(SIGNAL('killThread'))

	def user_or_sys(self, path_):
		var1 = os.path.join(self.kdehome, 'share/apps/plasma/plasmoids/kde-plasma-mail-checker/', path_)
		var2 = os.path.join('/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-mail-checker/', path_)
		#print [var1, var2]
		if os.path.exists(var2) :
			return var2
		elif os.path.exists(var1) :
			return var1
		else :
			return os.path.join(os.path.expanduser('~/kde-plasma-mail-checker/'), path_)

	def createDialogWidget(self):
		if hasattr(self, 'Dialog') :
			self.layout.removeItem(self.scroll)
			self.layout.removeItem(self.labelStat)
			del self.label
			del self.countList
			del self.labelStat
			del self.Dialog
			del self.scroll
			#print dateStamp() ,  're-createDialog'
		self.scroll = Plasma.ScrollWidget()
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.scrolled = QGraphicsWidget()
		self.scrolled.setMinimumSize(150.0,75.0)
		self.Dialog = QGraphicsGridLayout()
		i = 0
		self.label = []
		self.countList = []
		for accountName in string.split(self.Settings.value('Accounts').toString(),';') :
			self.label.append(accountName)
			self.countList.append(accountName)

			self.label[i] = Plasma.Label()
			self.countList[i] = Plasma.Label()
			self.label[i].setStyleSheet(self.accountColourStyle)
			self.countList[i].setStyleSheet(self.countColourStyle)
			self.label[i].setToolTip(self.accTTPref + self.tr._translate('Account') + \
													self.accTTSuff + ' ' + accountName)

			self.Dialog.addItem(self.label[i],i,0)
			self.Dialog.addItem(self.countList[i],i,1)
			i += 1

		self.labelStat = Plasma.Label()
		self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
		self.scrolled.setLayout(self.Dialog)
		self.scroll.setWidget(self.scrolled)
		self.layout.addItem(self.scroll)
		self.layout.addItem(self.labelStat)

		self.setLayout(self.layout)

	def processInit(self):
		self.Settings.sync()
		self.accountList = string.split(self.Settings.value('Accounts').toString(),';')
		self.accountCommand = {}
		for accountName in self.accountList :
			self.Settings.beginGroup(accountName)
			self.accountCommand[accountName] = self.initValue('CommandLine', ' ')
			self.Settings.endGroup()
		timeOut = self.initValue('TimeOut', '600')
		self.waitThread = self.initValue('WaitThread', '120')
		self.maxShowedMail = int(self.initValue('MaxShowedMail', '1024'))
		self.mailsInGroup = int(self.initValue('MailsInGroup', '5'))

		self.initStat = True
		self.someFunctions.initPOP3Cache()

		self.Timer.start(int(timeOut) * 1000)
		print dateStamp() ,  'processInit'
		QApplication.postEvent(self, QEvent(1011))
		self.initAkonadi()

	def createNotifyrc(self, kdehome):
		# Output the notifyrc file to the correct location
		print dateStamp() ,  "Outputting notifyrc file"

		dir_ = kdehome+"share/apps/kde-plasma-mail-checker"
		if not os.path.isdir(dir_):
			try:
				os.mkdir(dir_)
			except:
				print dateStamp() ,  "Problem creating directory: " + dir_
				print dateStamp() ,  "Unexpected error:", sys.exc_info()[0]

		# File to create
		fn = kdehome+"share/apps/kde-plasma-mail-checker/kde-plasma-mail-checker.notifyrc"

		# File contents
		c = []
		c.append("[Global]\n")
		c.append("IconName=mailChecker\n")
		c.append("Comment=MailChecker plasmoid\n")
		c.append("Name=M@ilChecker\n")
		c.append("\n")
		c.append("[Event/new-notification-arrived]\n")
		c.append("Name=New Notifications Arrived\n")
		c.append("Sound=KDE-Im-New-Mail.ogg\n")
		c.append("Action=Popup|Sound\n")
		c.append("\n")

		# Write file
		try:
			f = open(fn,"w")
			f.writelines(c)
			f.close()
		except:
			print dateStamp() ,  "Problem writing to file: " + fn
			print dateStamp() ,  "Unexpected error:", sys.exc_info()[0]

	def eventNotification(self, str_ = '', id_of_new_Items = {}, command = ''):
		newMailNotify = KNotification.event("new-notification-arrived", \
						QString(str_), \
						QPixmap(self.usualIconPath), \
						None, \
						KNotification.CloseOnTimeout, \
						KComponentData('kde-plasma-mail-checker','kde-plasma-mail-checker', \
						KComponentData.SkipMainComponentRegistration))
		if len(id_of_new_Items) != 0 :
			newMailNotify.setActions( QStringList() << "View" )
			shell_command = MailProgExec(self, id_of_new_Items, command, self)
			newMailNotify.activated['unsigned int'].connect(shell_command.start)
		newMailNotify.sendEvent()

	def disableIconClick(self):
		if self.connectIconsFlag :
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				if self.initStat :
					self.connectIconsFlag = not ( self.disconnect(self.icon, \
						SIGNAL('clicked()'), self._enterPassword) )
			else :
				if self.initStat :
					self.connectIconsFlag = not ( self.disconnect(self.panelIcon, \
						SIGNAL('clicked()'), self._enterPassword) )

	def _refreshData(self):
		print dateStamp() , '_refresh'
		if self.initStat :
			path_ = self.webIconPath

			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.labelStat.setText("<font color=green><b>" + self.tr._translate('..running..') + "</b></font>")
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.headerPref + self.tr._translate('Mail\nChecking') +  self.headerSuff)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Mail\nChecking') +  self.headerSuff, \
					self.panelIcon.icon() ) )
			self.disableIconClick()
		else:
			path_ = self.stopIconPath
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Click for Start\Stop') +  self.headerSuff, \
					self.panelIcon.icon() ) )
			return None

		if self.checkAccess() :
			if not self.T.isRunning() :
				#print dateStamp() ,  'start'
				accData = []
				for accountName in string.split(self.Settings.value('Accounts').toString(),';') :
					self.Settings.beginGroup(accountName)
					enable = self.Settings.value('Enabled').toString()
					connectMethod = self.Settings.value('connectMethod').toString()
					self.Settings.endGroup()
					#print dateStamp() , accountName.toLocal8Bit().data(), connectMethod, enable
					if str(enable) == '1' :
						data = (accountName, self.wallet.readPassword(accountName)[1])
						if connectMethod == 'imap\idle' :
							exist = False
							for item in self.idleMailingList :
								if accountName == item.name :
									exist = True
									break
							if not exist :
								self.idleMailingList.append(IdleMailing(data, self))
							accData.append(('', ''))
						else :
							accData.append(data)
					else :
						# delete the disabled accounts within idle mode
						exist = False
						for item in self.idleMailingList :
							if accountName == item.name :
								item.stop()
								exist = item
								break
						#print exist, accountName.toLocal8Bit().data()
						if exist : self.idleMailingList.remove(exist)
						accData.append(('', ''))
				self.T = ThreadCheckMail(self, accData, self.waitThread)
				print dateStamp() ,  'time for wait thread : ', self.waitThread
				self.T.start()
				#print dateStamp() , ' starting idles mail:', self.idleMailingList
				for item in self.idleMailingList :
					try :
						if not item.runned :
							item.start()
							state = ' started'
						else :
							state = ' runned'
						#print item.name, state
					except Exception, err :
						print dateStamp(), err, 'in', item.name.toLocal8Bit().data()
					finally : pass
			else :
				#print dateStamp() ,  'isRunning : send signal to kill...'
				#self.emit(SIGNAL('killThread'))
				pass
		else:
			self.emit(SIGNAL('refresh'))
			# print dateStamp() ,  'false start'

	def refreshData(self):
		#print dateStamp() ,  'refresh'
		self.GeneralLOCK.lock()

		if self.initStat :
			noCheck = False
			path_ = self.usualIconPath
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.labelStat.setText("<font color=green><b>" + self.tr._translate('..running..') + "</b></font>")
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + \
																						self.headerSuff)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Click for Start\Stop') +  self.headerSuff, \
					self.panelIcon.icon() ) )
		else :
			noCheck = True
			path_ = self.stopIconPath
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + \
																					self.headerSuff)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Click for Start\Stop') + self.headerSuff, \
					self.panelIcon.icon() ) )

		#print dateStamp() ,  self.checkResult, '  received Result'
		i = 0
		newMailExist = False
		self.listNewMail = ''
		x = ''
		if not hasattr(self, 'accountList') : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList'
		for accountName in self.accountList :
			self.Settings.beginGroup(accountName)
			connectMethod = self.Settings.value('connectMethod').toString()
			self.Settings.endGroup()
			IDLE = True if connectMethod == 'imap\idle' else False
			try :
				if int(self.checkResult[i][2]) > 0 and not IDLE :
					self.listNewMail += '<pre>' + accountName + '&#09;' + \
										 str(self.checkResult[i][2]) + ' | ' + \
										 str(self.checkResult[i][6]) + '</pre>'
					newMailExist = True
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountSColourStyle)
						self.countList[i].setStyleSheet(self.countSColourStyle)
					if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
						accountName_ = self.accSPref + accountName + self.accSSuff
						accountTT = self.accTTSPref + self.tr._translate('Account') + \
													self.accTTSSuff + ' ' + accountName
						text_1 = self.countSPref + str(self.checkResult[i][1]) + ' | ' + \
								 str(self.checkResult[i][6]) + self.countSSuff
						text_2 = self.countTTSPref + '<pre>' + self.tr._translate('New : ') + \
								 str(self.checkResult[i][2]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
								 str(self.checkResult[i][6]) + '</pre>' + self.countTTSSuff
				elif int(self.checkResult[i][2]) < 1 and not IDLE :
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountColourStyle)
						self.countList[i].setStyleSheet(self.countColourStyle)
					if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
						accountName_ = self.accPref + accountName + self.accSuff
						accountTT = self.accTTPref + self.tr._translate('Account') + \
													self.accTTSuff + ' ' + accountName
						text_1 = self.countPref + str(self.checkResult[i][1]) + ' | ' + \
								 str(self.checkResult[i][6]) + self.countSuff
						text_2 = self.countTTPref + '<pre>' + self.tr._translate('New : ') + \
								 str(self.checkResult[i][2]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
								 str(self.checkResult[i][6]) + '</pre>' + self.countTTSuff

				if (self.formFactor() in (Plasma.Planar, Plasma.MediaCenter)) \
												and self.initStat and not IDLE :
					self.label[i].setText(accountName_)
					self.label[i].setToolTip(accountTT)
					self.countList[i].setText(text_1)
					self.countList[i].setToolTip(text_2)

			except Exception, x :
				print dateStamp() ,  x, '  refresh_1'
			finally:
				pass
			i += 1

		#print dateStamp() ,  newMailExist and not noCheck
		countOfNodes = len(self.checkResult)
		matched = True if countOfNodes == len(self.accountList) else False
		if newMailExist and not noCheck and matched :
			''' detect count of new mail '''
			countOfAllNewMail = 0
			overLoad = False
			i = 0
			while i < countOfNodes :
				countOfAllNewMail += int(self.checkResult[i][2])
				i += 1
			if self.maxShowedMail < countOfAllNewMail :
				overLoad = True
				self.eventNotification('<b>' + self.tr._translate('There are more then') + '<br></br>' + \
										'&#09;' + str(self.maxShowedMail) + \
										' (' + str(countOfAllNewMail) + ') ' + \
										self.tr._translate('messages.') + '</b>', \
										{0 : 0}, '' )
			i = 0
			while i < countOfNodes and not overLoad :
				""" collected mail headers for each account """
				str_ = self.checkResult[i][4]
				encoding = self.checkResult[i][5].split('\n')
				STR_ = ''
				numbers = self.checkResult[i][7].split()
				if str_ not in ['', ' ', '0'] :
					#print dateStamp() ,  str_
					j = 0
					k = 0
					groups = 0
					for _str in str_.split('\r\n\r\n') :
						if _str not in ('', ' ', '\n', '\t', '\r', '\r\n') :
							mailAttrStr = self.someFunctions.mailAttrToSTR(_str, encoding[j])
							_str_raw = htmlWrapper(mailAttrStr, self.mailAttrColor)
							## None is means deprecated mail header
							if _str_raw is None :
								j += 1
								continue
							''' grouping mail '''
							STR_ += '<br>' + self.tr._translate('In ') + \
									self.fieldBoxPref + self.accountList[i] + \
									self.fieldBoxSuff + ':</br><br>' + _str_raw
							k += 1
							if k == self.mailsInGroup :
								''' mail group notification '''
								l = groups * k
								m = l + k
								#print [numbers[l:m]], (l, m)
								self.eventNotification('<b><u>' + \
										self.tr._translate('New Mail :') + \
										'</u></b>' + STR_, \
										{self.accountList[i] : string.join(numbers[l:m], ' ')}, \
										self.accountCommand[ self.accountList[i] ])
								k = 0
								groups += 1
								STR_ = ''
						j += 1
				''' tail of mail group notification '''
				if STR_ != '' :
					l = groups * self.mailsInGroup
					#print [numbers[l:]]
					self.eventNotification('<b><u>' + \
										self.tr._translate('New Mail :') + \
										'</u></b>' + STR_, \
										{self.accountList[i] : string.join(numbers[l:], ' ')}, \
										self.accountCommand[ self.accountList[i] ])
				i += 1

		if not ( self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) ) :
			if self.listNewMail == '' :
				self.listNewMail = self.tr._translate("No new mail")
			Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
								self.panelIcon.toolTip(), \
								self.headerPref + self.listNewMail + self.headerSuff, \
								self.panelIcon.icon() ) )

		i = 0
		while i < countOfNodes :
			if self.checkResult[i][3] not in ['', ' ', '0', '\n'] :
				self.ErrorMsg += self.checkResult[i][3]
			i += 1
		if self.ErrorMsg not in ['', ' ', '0', '\n'] :
			if self.Settings.value('ShowError').toString() != '0' and not noCheck :
				self.eventNotification( QString().fromUtf8(self.ErrorMsg) )

		if not self.connectIconsFlag :
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			else :
				self.connectIconsFlag = self.connect(self.panelIcon, SIGNAL('clicked()'), self._enterPassword)
		self.GeneralLOCK.unlock()

	def createIconWidget(self):
		self.panelIcon = Plasma.IconWidget()

		self.panelIcon.setIcon(self.stopIconPath)
		self.panelIcon.setToolTip(self.headerPref + self.tr._translate('M@il Checker') + self.headerSuff)
		Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
			self.panelIcon.toolTip(), \
			self.headerPref + self.tr._translate('Click for Start\Stop') + self.headerSuff, \
			self.panelIcon.icon() ) )
		self.panelIcon.resize(32,32)
		self.panelIcon.show()
		self.connectIconsFlag = self.connect(self.panelIcon, SIGNAL('clicked()'), self._enterPassword)
		self.layout.addItem(self.panelIcon)
		self.labelStat = Plasma.Label()

		self.setLayout(self.layout)

	def createConfigurationInterface(self, parent):
		self.editAccounts = EditAccounts(self, parent)
		parent.addPage(self.editAccounts, self.tr._translate("Accounts"))
		self.appletSettings = AppletSettings(self, parent)
		parent.addPage(self.appletSettings, self.tr._translate("Settings"))
		self.passwordManipulate = PasswordManipulate(self, parent)
		parent.addPage(self.passwordManipulate, self.tr._translate("Password Manipulation"))
		self.fontsNcolour = Font_n_Colour(self, parent)
		parent.addPage(self.fontsNcolour, self.tr._translate("Font and Colour"))
		self.akonadiResources = AkonadiResources(self, parent)
		parent.addPage(self.akonadiResources, self.tr._translate("Akonadi Mail Resources"))
		self.filters = Filters(self, parent)
		parent.addPage(self.filters, self.tr._translate("Filters"))
		self.proxy = ProxySettings(self, parent)
		parent.addPage(self.proxy, self.tr._translate("Proxy"))
		self.examples = Examples(self.user_or_sys('EXAMPLES'), parent)
		parent.addPage(self.examples, self.tr._translate("EXAMPLES"))
		self.akonadiResources.reloadAkonadi.connect(self.reloadAkonadiStuff)
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

	def showConfigurationInterface(self):
		self.dialog = KPageDialog()
		self.dialog.setModal(True)
		self.dialog.setFaceType(KPageDialog.List)
		self.dialog.setButtons( KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel) )
		self.createConfigurationInterface(self.dialog)
		self.dialog.show()
		self.dialog.move(self.popupPosition(self.dialog.sizeHint()))

	def settingsChangeComplete(self):
		if self.editAccounts.StateChanged :
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Accounts'), \
					 self.tr._translate('Changes was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.editAccounts.parameters.saveAccountData()
		self.appletSettings.refreshSettings()
		self.fontsNcolour.refreshSettings()
		if self.filters.StateChanged[0] or self.filters.StateChanged[1] :
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Filters'), \
					 self.tr._translate('Changes was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer :
				if self.filters.subjEditor.isEnabled() :
					self.filters.saveFilter(0)
				if self.filters.fromEditor.isEnabled() :
					self.filters.saveFilter(1)
		if self.akonadiResources.StateChanged :
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate("Akonadi Mail Resources"), \
					 self.tr._translate('Changes was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.akonadiResources.saveData()
		if self.proxy.StateChanged :
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Proxy'), \
					 self.tr._translate('Changes was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.proxy.saveData()
		self.Settings.setValue('UseProxy', 'True' if self.proxy.enableProxy.checkState()==Qt.Checked else 'False')

	def checkAccess(self):
		self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.wallet is None :
			self.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return False
		if not self.wallet.hasFolder(self.appletName) :
			self.wallet.createFolder(self.appletName)
		self.wallet.setFolder(self.appletName)
		return True

	def configAccepted(self):
		self.disconnect(self, SIGNAL('refresh'), self.refreshData)
		if not self.checkAccess() : return None
		self.settingsChangeComplete()
		#print dateStamp() ,  self.formFactor(), '---'
		self.disableIconClick()
		x = ''
		try:
			self.Timer.stop()
		except Exception, x :
			print dateStamp() ,  x, '  acceptConf_1'
		finally : pass
		# refresh color & font Variables
		self.initPrefixAndSuffix()
		if hasattr(self, 'dialog') : del self.dialog
		# refresh plasmoid Header
		if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
			self.initTitle()
			self.createDialogWidget()
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.emit(SIGNAL('killThread'))

	def configDenied(self):
		if hasattr(self, 'dialog') : del self.dialog

	def _enterPassword(self):
		if not self.initStat :
			if self.checkAccess() :
				#print dateStamp() ,  '_eP'
				self.enterPassword()
			else :
				#print dateStamp() ,  '_eP_1'
				return None
		else :
			self.disableIconClick()
			x = ''
			try:
				self.Timer.stop()
			except Exception, x :
				print dateStamp() ,  x, '  _entP'
			finally:
				pass
			self.emit(SIGNAL('killThread'))
			print dateStamp() ,  'stop_eP'

	def enterPassword(self):
		if self.checkAccess() :
			#print dateStamp() ,  'eP'
			self.importAccPasswords()
			self.emit(SIGNAL('access'))
		else :
			#print dateStamp() ,  'eP_1'
			self.initStat = False

	def eventClose(self):
		print dateStamp() ,  '  eventCloseMethod'
		self.initStat = False
		self.disconnect(self, SIGNAL('refresh'), self.refreshData)
		self.disconnect(self, SIGNAL('access'), self.processInit)
		self.disconnect(self, SIGNAL('destroyed()'), self.eventClose)
		self.disconnect(self, SIGNAL('killThread'), self.killMailCheckerThread)
		self.idleThreadMessage.disconnect(self.idleMessage)
		self.idleingStopped.disconnect(self.idleingStoppedEvent)
		self.disableIconClick()
		self.deleteAkonadiMonitor()
		x = ''
		try :
			self.Timer.stop()
			if not(self.wallet is None) :
				self.wallet.closeWallet(self.appletName, True)
				print dateStamp() ,  ' wallet closed'
		except Exception, x :
			print dateStamp() , x, '  eventClose_1'
		finally : pass
		try :
			self.someFunctions.savePOP3Cache()
		except IOError, x :
			print dateStamp() ,x, '  eventClose_2'
		finally : pass
		self.killMailCheckerThread()
		self.GeneralLOCK.unlock()
		count = self.initValue('stayDebLog', '5')
		cleanDebugOutputLogFiles(int(count))
		print dateStamp() , "MailChecker destroyed manually."
		#sys.stderr.close()
		sys.stdout.close()

	def killMailCheckerThread(self):
		if hasattr(self, 'T') :
			#print dateStamp() ,'   killMetod Up'
			if self.T.isRunning() : self.T._terminate()
		# stopping idles mail
		for item in self.idleMailingList :
			try :
				item.stop()
			except Exception, err :
				print dateStamp(), err
			finally : pass
		''' wait for idle terminate '''
		i = WaitIdle(self)
		i.start()

	def idleingStoppedEvent(self):
		print dateStamp() , 'idleingStoppedEvent'
		self.someFunctions.savePOP3Cache()
		self.monitor_isnt_exist()
		self.initStat = False
		self.emit(SIGNAL('refresh'))

	def mouseDoubleClickEvent(self, ev):
		if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
			self.showConfigurationInterface()

	def importAccPasswords(self):
		if self.appletName in self.wallet.walletList() :
			self.old_wallet = KWallet.Wallet.openWallet(self.appletName, 0)
			if not (self.old_wallet is None) :
				entryList = self.old_wallet.entryList()
				for item in entryList :
					self.wallet.writePassword( item, self.old_wallet.readPassword(item)[1] )
				self.wallet.deleteWallet(self.appletName)

	def initAkonadi(self):
		if not A.AkonadiModuleExist or A.Akonadi.ServerManager.state() == A.Akonadi.ServerManager.State(4) :
			print dateStamp(), A.AkonadiModuleExist , 'Module PyKDE4.akonadi or Akonadi server are not available.'
			return None
		else :
			print dateStamp(), A.AkonadiModuleExist , 'Module PyKDE4.akonadi is available.'
		if self.monitor_isnt_exist() :
			print dateStamp(), 'Module PyKDE4.akonadi && Akonadi server are available.'
			timeout = self.initValue('TimeOutGroup', '3')
			self.monitor = A.AkonadiMonitor(timeout, self)
			self.monitorTimer = QTimer()
			self.monitorTimer.timeout.connect(self.monitor.syncCollection)
			self.monitor.initAccounts()
			self.monitorTimer.start(60 * 1000)

	def akonadiAccountList(self):
		self.Settings.beginGroup('Akonadi account')
		accList = self.Settings.allKeys()
		self.Settings.endGroup()
		return accList

	def monitor_isnt_exist(self):
		if A.AkonadiModuleExist and self.akonadiAccountList().count() != 0 \
				and A.Akonadi.ServerManager.state() == A.Akonadi.ServerManager.State(2) :
			self.deleteAkonadiMonitor()
			return True
		else :
			return False

	def deleteAkonadiMonitor(self):
		if 'monitorTimer' in dir(self) :
			self.monitorTimer.timeout.disconnect(self.monitor.syncCollection)
			self.monitorTimer.stop()
			del self.monitorTimer
		if 'monitor' in dir(self) :
			self.monitor.__del__()
			del self.monitor
			print dateStamp(), ' monitor delete.'

	def reloadAkonadiStuff(self):
		self.deleteAkonadiMonitor()
		reload(A)
		self.initAkonadi()
		self.akonadiResources.restartAkonadi()

	def __del__(self): self.eventClose()

	def idleMessage(self, d):
		# print d
		# stopping emitted idle mail
		if d['state'] == SIGNSTOP :
			itm = None
			for item in self.idleMailingList :
				if item.name == d['acc'] : itm = item
			#print self.idleMailingList, '<--|'
			i = 0
			if 'accountList' not in dir(self) : self.accountList = QStringList()
			#for item in self.accountList : print item.toLocal8Bit().data(), 'accList_IDLE'
			for accountName in self.accountList :
				try :
					if d['acc'] == accountName :
						if hasattr(self, 'label') :
							self.label[i].setStyleSheet(self.accountColourStyle)
							self.countList[i].setStyleSheet(self.countColourStyle)
						if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
							accountName_ = self.accPref + accountName + self.accSuff
							accountTT = self.accTTPref + self.tr._translate('Account') + \
										self.accTTSuff + ' ' + accountName + '<br>(IDLE stopped)'

						if (self.formFactor() in (Plasma.Planar, Plasma.MediaCenter)) :
							self.label[i].setText(accountName_)
							self.label[i].setToolTip(accountTT)
						break
					i += 1
				except Exception, err :
					print dateStamp(), err, 'idle_stop'
				finally : pass
			if itm is not None :
				self.eventNotification( itm.name + self.tr._translate(' is not active.' ))
				self.idleMailingList.remove(itm)
			#print self.idleMailingList, '<--'
			return None
		#
		# show error notify from emitted idle mail
		if d['state'] == SIGNERRO :
			self.eventNotification( "In %s error: %s"%(d['acc'], \
									str([QString(s).toLocal8Bit().data() for s in d['msg']])) )
			return None
		#
		# show init or new mail data and notify
		i = 0
		self.listNewMail = ''
		if not hasattr(self, 'accountList') : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList_IDLE1'
		for accountName in self.accountList :
			try :
				if d['acc'] == accountName :
					self.listNewMail += '<pre>' + accountName + '(IDLE)&#09;' + \
											str(d['msg'][1]) + ' | ' + \
											str(d['msg'][2]) + '</pre>'
					newMailExist = True
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountSColourStyle)
						self.countList[i].setStyleSheet(self.countSColourStyle)
					if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
						accountName_ = self.accSPref + accountName + self.accSSuff
						accountTT = self.accTTSPref + self.tr._translate('Account') + \
									self.accTTSSuff + ' ' + accountName + '<br>(IDLE)'
						text_1 = self.countSPref + str(d['msg'][0]) + ' | ' + \
								str(d['msg'][2]) + self.countSSuff
						text_2 = self.countTTSPref + '<pre>' + self.tr._translate('New : ') + \
								str(d['msg'][1]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
								str(d['msg'][2]) + '</pre>' + self.countTTSSuff

					if (self.formFactor() in (Plasma.Planar, Plasma.MediaCenter)) :
						self.label[i].setText(accountName_)
						self.label[i].setToolTip(accountTT)
						self.countList[i].setText(text_1)
						self.countList[i].setToolTip(text_2)
				i += 1
			except Exception, err :
				print dateStamp(), err, 'idle_newMail'
			finally : pass
		if d['state'] == SIGNDATA :
			if not ( self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) ) :
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
								self.panelIcon.toolTip(), \
								self.headerPref + self.listNewMail + self.headerSuff, \
								self.panelIcon.icon() ) )
			''' detect count of new mail '''
			countOfAllNewMail = d['msg'][1]
			overLoad = False
			if self.maxShowedMail < countOfAllNewMail :
				overLoad = True
				self.eventNotification('<b>' + self.tr._translate('There are more then') + '<br></br>' + \
										'&#09;' + str(self.maxShowedMail) + \
										' (' + str(countOfAllNewMail) + ') ' + \
										self.tr._translate('messages.') + '</b>', \
										{0 : 0}, '' )
			if not overLoad :
				j = 0
				STR_ = ''
				k = 0
				groups = 0
				numbers = d['msg'][4].split()
				for _str in string.split(d['msg'][3], '\r\n\r\n') :
					if _str not in ('', ' ', '\n', '\t', '\r', '\r\n') :
						mailAttrStr = self.someFunctions.mailAttrToSTR(_str)
						_str_raw = htmlWrapper(mailAttrStr, self.mailAttrColor)
						## None is means deprecated mail header
						if _str_raw is None :
							j += 1
							continue
						STR_ += '<br>' + self.tr._translate('In ') + \
								self.fieldBoxPref + d['acc'] + self.fieldBoxSuff + ':</br><br>' + \
								_str_raw
						k += 1
						if k == self.mailsInGroup :
							''' mail group notification '''
							l = groups * k
							m = l + k
							self.eventNotification('<b><u>' + \
									self.tr._translate('New Mail :') + \
									'</u></b>' + STR_, \
									{d['acc'] : string.join(numbers[l:m], ' ')}, \
									self.accountCommand[ d['acc'] ])
							k = 0
							groups += 1
							STR_ = ''
					j += 1
				if STR_ != '' :
					l = groups * self.mailsInGroup
					msg = '<b><u>' + self.tr._translate('New Mail :') + '</u></b>' + STR_
					self.eventNotification( msg, \
											{d['acc'] : string.join(numbers[l:], ' ')}, \
											self.accountCommand[ d['acc'] ])

def CreateApplet(parent):
	return plasmaMailChecker(parent)

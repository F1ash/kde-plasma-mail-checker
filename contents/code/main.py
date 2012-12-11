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
	global warningMsg
	global Settings
	global RESULT
	global ErrorMsg
	global WAIT
	global VERSION
	from Functions import *
	from MailProgExec import MailProgExec
	from Filter import Filters
	from Proxy import ProxySettings
	from Examples import Examples
	from Translator import Translator
	from IdleMailing import IdleMailing
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from PyKDE4.kdecore import *
	from PyKDE4.kdeui import *
	from PyKDE4.plasma import Plasma
	from PyKDE4 import plasmascript
	import string, time, os.path, sys, signal
	try :
		ModuleExist = True
		from PyKDE4.akonadi import Akonadi
		from AkonadiMod import *
	except Exception, err:
		ModuleExist = False
		print err
	finally :
		pass
	RESULT = []
	Settings = QSettings('plasmaMailChecker','plasmaMailChecker')
	ErrorMsg = ''
	warningMsg = ''
	#sys.stderr = open('/dev/shm/errorMailChecker' + str(time.time()) + '.log','w')
	sys.stdout = open('/tmp/outMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
except ImportError, warningMsg :
	print "ImportError", warningMsg
finally:
	'O`key'
	pass

GeneralLOCK = QMutex()
LOCK = QReadWriteLock()

class WaitIdle(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self, parent)

		self.Parent = parent
		self.key = False

	def run(self):
		while not self.key and len(self.Parent.idleMailingList) :
			self.msleep(500)
			if getExternalIP() == '' :
				print dateStamp(), 'Internet not available'
				for item in self.Parent.idleMailingList :
					item.__del__()
				break
		self.Parent.idleingStopped.emit()

	def __del__(self):
		self.key = True
		self.quit()

class ThreadCheckMail(QThread):
	def __init__(self, obj = None, accountData = [('', '')], timeout = 120, parent = None):
		QThread.__init__(self, parent)

		self.Parent = obj
		self.setTerminationEnabled(False)
		self.Timer = QTimer()
		self.Timer.setSingleShot(True)
		self.Timer.timeout.connect(self.signalToKillSelf)
		self.timeout = int(timeout) * 1000
		self.accData = accountData
		self.accountThread = []
		self.dataList = []
		global ErrorMsg
		ErrorMsg = ''
		global WAIT
		WAIT = True

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/' + path_
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/' + path_
		if os.path.exists(var2) :
			return var2
		elif os.path.exists(var1) :
			return var1
		else :
			return os.path.expanduser('~/kde-plasma-mail-checker/contents/' + path_)

	def readResult(self):
		global RESULT
		RESULT = []
		for i in xrange(len(self.accountThread)) :
			RESULT += [readDataFiles(self.dataList[i][1])]
		#print dateStamp() ,  RESULT

	def run(self):
		try:
			x = ''
			self.Timer.start(self.timeout)
			path = self.user_or_sys('code/mail.py')
			i = 0
			for accountData in self.accData :
				if WAIT :
					str_ = str(randomString(24))
					with open('/dev/shm/' + str_, 'wb') as f:
						if isinstance(accountData[1], basestring) :
							_str = accountData[1]
						else :
							_str = accountData[1].toLocal8Bit().data()
						f.write(_str)
					Data = QStringList()
					Data.append(path)
					Data.append(accountData[0])
					Data.append(str_)
					self.accountThread += ['']
					self.accountThread[i] = QProcess()
					start, pid = self.accountThread[i].startDetached('/usr/bin/python', Data, os.getcwd())
					self.dataList += [(pid, str_, start)]
					print dateStamp() ,  start, pid, Data.join(' ').toUtf8().data()
				else :
					break
				i += 1

			# waiting mailcheckig processes
			key_ = True
			while key_ and WAIT :
				time.sleep(0.1)
				key_ = False
				for node in self.dataList :
					if bool(node[2]) and node[0] != 0 :
						#print bool(node[2]), node[0], ' ????'
						key_ = key_ or pid_exists(node[0], 0)

		except Exception, x :
			self.Timer.stop()
			print dateStamp() ,  x, '  thread'
		finally :
			self.Timer.stop()
			if WAIT :
				self.readResult()
				self.Parent.emit(SIGNAL('refresh'))
				self.quit()
		return

	def signalToKillSelf(self):
		global WAIT
		global ErrorMsg
		LOCK.lockForRead()
		WAIT = False
		LOCK.unlock()
		print dateStamp() ,  WAIT, '  changed WAIT'
		ErrorMsg += 'Timeout thread error\n'
		print dateStamp() ,  'Mail thread timeout terminating...'
		#QApplication.postEvent(self.Parent, QEvent(1010))
		self._terminate()

	def _terminate(self):
		self.Timer.stop()
		global WAIT
		LOCK.lockForRead()
		WAIT = False
		LOCK.unlock()
		for i in xrange(len(self.dataList)) :
			if bool(self.dataList[i][2]) and pid_exists(self.dataList[i][0], signal.SIGKILL) :
				#print dateStamp() ,  self.dataList[i][0], '  killed'
				pass
			else :
				#print dateStamp() ,  self.dataList[i][0], '  not exist'
				pass
		print dateStamp() ,  'recive signal to kill...'
		self.readResult()
		self.Parent.emit(SIGNAL('refresh'))
		self.quit()

class plasmaMailChecker(plasmascript.Applet):
	idleThreadMessage = pyqtSignal(dict)
	idleingStopped = pyqtSignal()
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self,parent)

		self.initStat = False
		self.checkResult = []
		self.idleMailingList = []

		self.panelIcon = Plasma.IconWidget()
		self.icon = Plasma.IconWidget()
		self.listNewMail = []
		self.connectIconsFlag = False
		self.tr = Translator('plasmaMailChecker')
		self.initPrefixAndSuffix()

	def init(self):
		global Settings
		self.setHasConfigurationInterface(True)
		self.T = ThreadCheckMail(self)
		#self.loop = QEventLoop()

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
			self.TitleDialog.setStyleSheet(self.headerColourStyle)
			self.initTitle()
			self.TitleDialog.setText(self.headerPref + self.title + self.headerSuff)
			self.titleLayout.addItem(self.TitleDialog)

			self.icon.setIcon(self.stopIconPath)
			self.icon.setMaximumSize(35.0, 35.0)
			self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + self.headerSuff)
			self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			self.titleLayout.addItem(self.icon)

			self.layout.setOrientation(Qt.Vertical)
			self.layout.addItem(self.titleLayout)
			self.setMinimumSize(150.0,75.0)
			self.createDialogWidget()
		else:
			self.createIconWidget()

		self.setLayout(self.layout)

		self.connect(self.applet, SIGNAL('destroyed()'), self.eventClose)
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.connect(self, SIGNAL('access'), self.processInit)
		self.connect(self, SIGNAL('killThread'), self.killMailCheckerThread)
		#self.connect(self, SIGNAL('finished()'), self.loop , SLOT(self.T._terminate()))
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
		global VERSION
		fileName = self.user_or_sys('metadata.desktop')
		if os.path.exists(fileName) :
			with open(fileName) as f :
				str_ = f.read()
			list_ = string.split(str_, '\n')
			for _str in list_ :
				if 'X-KDE-PluginInfo-Version' in _str :
					VERSION = string.split(_str, '=')[1]
					break
		else :
			VERSION = '~'
		#print dateStamp() , "VERSION : ", VERSION
		self.version = self.initValue('ShowVersion', '1')
		if int(self.version) > 0 :
			self.title = self.tr._translate('M@il Checker') + '\n' + VERSION + ' ' + lang[0][:2]
		else :
			self.title = self.tr._translate('M@il Checker')
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
		global Settings
		if Settings.contains(key_) :
			#print dateStamp() ,  key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			if defaultValue == '' :
				defaultValue = self.getSystemColor('int')
			Settings.setValue(key_, QVariant(defaultValue))
			#print dateStamp() ,  key_, Settings.value(key_).toString()
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
		global Settings
		if 'Dialog' in dir(self) :
			self.layout.removeItem(self.Dialog)
			del self.label
			del self.countList
			del self.labelStat
			del self.Dialog
			#print dateStamp() ,  're-createDialog'
		self.Dialog = QGraphicsGridLayout()
		i = 0
		self.label = []
		self.countList = []
		for accountName in string.split(Settings.value('Accounts').toString(),';') :
			self.label += [accountName]
			self.countList += [accountName]

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
		self.Dialog.addItem(self.labelStat, i, 0)

		self.Dialog.updateGeometry()
		self.layout.addItem(self.Dialog)

		self.setLayout(self.layout)

	def processInit(self):
		global Settings
		Settings.sync()
		self.accountList = string.split(Settings.value('Accounts').toString(),';')
		self.accountCommand = {}
		for accountName in self.accountList :
			Settings.beginGroup(accountName)
			self.accountCommand[accountName] = self.initValue('CommandLine', ' ')
			Settings.endGroup()
		timeOut = self.initValue('TimeOut', '600')
		self.waitThread = self.initValue('WaitThread', '120')
		self.maxShowedMail = int(self.initValue('MaxShowedMail', '1024'))
		self.mailsInGroup = int(self.initValue('MailsInGroup', '5'))

		self.initStat = True
		initPOP3Cache()

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

		self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if not (self.wallet is None) :
			self.wallet.setFolder('plasmaMailChecker')
			if not self.T.isRunning() :
				#print dateStamp() ,  'start'
				accData = []
				for accountName in string.split(Settings.value('Accounts').toString(),';') :
					Settings.beginGroup(accountName)
					enable = Settings.value('Enabled').toString()
					connectMethod = Settings.value('connectMethod').toString()
					Settings.endGroup()
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
		GeneralLOCK.lock()
		global ErrorMsg
		global RESULT
		global Settings

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

		self.checkResult = RESULT
		#print dateStamp() ,  self.checkResult, '  received Result'
		i = 0
		newMailExist = False
		self.listNewMail = ''
		x = ''
		if 'accountList' not in dir(self) : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList'
		for accountName in self.accountList :
			Settings.beginGroup(accountName)
			connectMethod = Settings.value('connectMethod').toString()
			Settings.endGroup()
			IDLE = True if connectMethod == 'imap\idle' else False
			try :
				if int(self.checkResult[i][2]) > 0 and not IDLE :
					self.listNewMail += '<pre>' + accountName + '&#09;' + \
										 str(self.checkResult[i][2]) + ' | ' + \
										 str(self.checkResult[i][6]) + '</pre>'
					newMailExist = True
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

			except IndexError, x :
				print dateStamp() ,  x, '  refresh_1'
			except x :
				print dateStamp() ,  x, '  refresh_2'
			except AttributeError, x:
				#print dateStamp() ,  x, '  refresh_3'
				pass
			except UnboundLocalError, x :
				print dateStamp() ,  x, '  refresh_4'
				pass
			except x :
				print dateStamp() ,  x, '  refresh_5'
				pass
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
						if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
							_str_raw = htmlWrapper(mailAttrToSTR(_str, encoding[j]), self.mailAttrColor)
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
				ErrorMsg += self.checkResult[i][3]
			i += 1
		if ErrorMsg not in ['', ' ', '0', '\n'] :
			if Settings.value('ShowError').toString() != '0' and not noCheck :
				self.eventNotification( QString().fromUtf8(ErrorMsg) )

		if not self.connectIconsFlag :
			if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
				self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			else :
				self.connectIconsFlag = self.connect(self.panelIcon, SIGNAL('clicked()'), self._enterPassword)
		GeneralLOCK.unlock()

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
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

	def showConfigurationInterface(self):
		self.dialog = KPageDialog()
		self.dialog.setModal(True)
		self.dialog.setFaceType(KPageDialog.List)
		self.dialog.setButtons( KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel) )
		self.createConfigurationInterface(self.dialog)
		self.dialog.move(self.popupPosition(self.dialog.sizeHint()))
		self.dialog.exec_()

	def configAccepted(self):
		self.disconnect(self, SIGNAL('refresh'), self.refreshData)
		self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.wallet is None :
			self.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.appletSettings.refreshSettings(self)
		self.fontsNcolour.refreshSettings(self)
		Settings.setValue('UseProxy', 'True' if self.proxy.enableProxy.checkState()==Qt.Checked else 'False')
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
		if 'dialog' in dir(self) : del self.dialog
		# refresh plasmoid Header
		if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
			self.TitleDialog.setStyleSheet(self.headerColourStyle)
			self.initTitle()
			self.TitleDialog.setText(self.headerPref + self.title + self.headerSuff)
			self.createDialogWidget()
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.emit(SIGNAL('killThread'))

	def configDenied(self):
		del self.dialog

	def _enterPassword(self):
		if not self.initStat :
			self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
			if not (self.wallet is None) :
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
		self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if not (self.wallet is None) :
			if not self.wallet.hasFolder('plasmaMailChecker') : self.wallet.createFolder('plasmaMailChecker')
			#print dateStamp() ,  'eP'
			self.wallet.setFolder('plasmaMailChecker')
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
		if 'monitor' in dir(self) :
			self.monitorTimer.timeout.disconnect(self.monitor.syncCollection)
			del self.monitorTimer
			del self.monitor
		x = ''
		try :
			self.Timer.stop()
			if not (self.wallet is None) :
				self.wallet.closeWallet('plasmaMailChecker', True)
				print dateStamp() ,  ' wallet closed'
		except AttributeError, x :
			print dateStamp() , x, '  eventClose_1'
		except x :
			print dateStamp() , x, '  eventClose_2'
			pass
		finally :
			pass
		try :
			savePOP3Cache()
		except IOError, x :
			print dateStamp() ,x, '  eventClose_3'
		finally :
			pass
		self.killMailCheckerThread()
		GeneralLOCK.unlock()
		count = self.initValue('stayDebLog', '5')
		cleanDebugOutputLogFiles(int(count))
		print dateStamp() , "MailChecker destroyed manually."
		#sys.stderr.close()
		sys.stdout.close()

	def killMailCheckerThread(self):
		#self.loop.quit()
		if 'T' in dir(self):
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
		savePOP3Cache()
		self.monitor_isnt_exist()
		self.initStat = False
		self.emit(SIGNAL('refresh'))

	def mouseDoubleClickEvent(self, ev):
		if self.formFactor() in (Plasma.Planar, Plasma.MediaCenter) :
			self.showConfigurationInterface()

	def importAccPasswords(self):
		if 'plasmaMailChecker' in self.wallet.walletList() :
			self.old_wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
			if not (self.old_wallet is None) :
				entryList = self.old_wallet.entryList()
				for item in entryList :
					self.wallet.writePassword( item, self.old_wallet.readPassword(item)[1] )
				self.wallet.deleteWallet('plasmaMailChecker')

	def initAkonadi(self):
		global ModuleExist
		if not ModuleExist or Akonadi.ServerManager.state() == Akonadi.ServerManager.State(4) :
			print dateStamp(), ModuleExist , 'Module PyKDE4.akonadi or Akonadi server are not available.'
			return None
		else :
			print dateStamp(), ModuleExist , 'Module PyKDE4.akonadi is available.'
		if self.monitor_isnt_exist() :
			print dateStamp(), 'Module PyKDE4.akonadi && Akonadi server are available.'
			timeout = self.initValue('TimeOutGroup', '3')
			self.monitor = AkonadiMonitor(timeout, self)
			self.monitorTimer = QTimer()
			self.monitorTimer.timeout.connect(self.monitor.syncCollection)
			self.monitor.initAccounts()
			self.monitorTimer.start(60 * 1000)

	def monitor_isnt_exist(self):
		global ModuleExist
		if ModuleExist and akonadiAccountList().count() != 0 \
				and Akonadi.ServerManager.state() == Akonadi.ServerManager.State(2) :
			if 'monitorTimer' in dir(self) :
				self.monitorTimer.timeout.disconnect(self.monitor.syncCollection)
				self.monitorTimer.stop()
				del self.monitorTimer
			if 'monitor' in dir(self) :
				self.monitor.__del__()
				del self.monitor
				print dateStamp(), ' monitor delete.'
			return True
		else :
			return False

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
					print dateStamp(), err
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
		if 'accountList' not in dir(self) : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList_IDLE1'
		for accountName in self.accountList :
			try :
				if d['acc'] == accountName :
					self.listNewMail += '<pre>' + accountName + '(IDLE)&#09;' + \
											str(d['msg'][1]) + ' | ' + \
											str(d['msg'][2]) + '</pre>'
					newMailExist = True
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
				print dateStamp(), err
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
					if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
						_str_raw = htmlWrapper(mailAttrToSTR(_str), self.mailAttrColor)
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

class EditAccounts(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self, parent)

		self.Status = 'FREE'
		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('EditAccounts')
		self.connectFlag = False
		global Settings

		self.VBLayout = QVBoxLayout()

		self.layout = QGridLayout()

		self.accountListBox = KListWidget()
		i = 0
		self.accountList = []
		while i < Settings.childGroups().count() :
			#print dateStamp() ,  str(Settings.childGroups().__getitem__(i)), '-'
			accountName = Settings.childGroups().__getitem__(i)
			if accountName != 'Akonadi account' :
				self.accountListBox.addItem(accountName)
				self.accountList += [accountName]
			i += 1
		#print dateStamp() ,  self.accountList
		self.accountListBox.itemClicked.connect(self.enable_Del_n_Edit)
		self.layout.addWidget(self.accountListBox,0,0,2,3)

		self.stringEditor = KLineEdit()
		self.stringEditor.setToolTip(self.tr._translate("Deprecated char : '<b>;</b>'"))
		self.stringEditor.setContextMenuEnabled(True)
		self.layout.addWidget(self.stringEditor,3,0)

		self.addAccountItem = QPushButton('&Add')
		self.addAccountItem.setToolTip(self.tr._translate("Add new Account"))
		self.addAccountItem.clicked.connect(self.addNewAccount)
		self.layout.addWidget(self.addAccountItem,3,4)

		self.editAccountItem = QPushButton('&Edit')
		self.editAccountItem.setEnabled(False)
		self.editAccountItem.setToolTip(self.tr._translate("Edit current Account"))
		self.editAccountItem.clicked.connect(self.editCurrentAccount)
		self.layout.addWidget(self.editAccountItem,1,4)

		self.delAccountItem = QPushButton('&Del')
		self.delAccountItem.setEnabled(False)
		self.delAccountItem.setToolTip(self.tr._translate("Delete current Account"))
		self.delAccountItem.clicked.connect(self.delCurrentAccount)
		self.layout.addWidget(self.delAccountItem,0,4)

		self.VBLayout.addLayout(self.layout)

		self.HB1Layout = QGridLayout()

		self.HB1Layout.addWidget(QLabel(self.tr._translate("Server : ")),0,0)
		self.HB1Layout.addWidget(QLabel(self.tr._translate("Port : ")),0,1)
		self.HB1Layout.addWidget(QLabel(self.tr._translate("Enable : ")),0,2)

		self.serverLineEdit = KLineEdit()
		self.serverLineEdit.setContextMenuEnabled(True)
		self.serverLineEdit.setToolTip(self.tr._translate("Example : imap.gmail.com, pop.mail.ru"))
		self.HB1Layout.addWidget(self.serverLineEdit,1,0)

		self.portBox = KIntSpinBox(0, 65535, 1, 0, self)
		self.HB1Layout.addWidget(self.portBox, 1, 1)

		self.enabledBox = QCheckBox()
		Enabled = AppletSettings().initValue('Enabled', '1')
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.HB1Layout.addWidget(self.enabledBox,1,2, Qt.AlignHCenter)

		self.VBLayout.addLayout(self.HB1Layout)

		self.HB2Layout = QGridLayout()

		self.HB2Layout.addWidget(QLabel(self.tr._translate("AuthMethod : ")),0,0)

		self.connectMethodBox = KComboBox()
		self.connectMethodBox.addItem('POP3',QVariant('pop'))
		self.connectMethodBox.addItem('IMAP4',QVariant('imap'))
		self.connectMethodBox.addItem('IMAP4\IDLE',QVariant('imap\idle'))
		self.connect(self.connectMethodBox, SIGNAL("currentIndexChanged(const QString&)"), self.showCatalogChoice)
		self.connect(self.connectMethodBox, SIGNAL("currentIndexChanged(const QString&)"), self.changePort)
		self.HB2Layout.addWidget(self.connectMethodBox,1,0)

		self.HB2Layout.addWidget(QLabel(self.tr._translate("Encrypt : ")),0,1)

		self.cryptBox = KComboBox()
		self.cryptBox.addItem('None',QVariant('None'))
		self.cryptBox.addItem('SSL',QVariant('SSL'))
		#self.cryptBox.addItem('TLS',QVariant('TLS'))
		self.connect(self.cryptBox, SIGNAL("currentIndexChanged(const QString&)"), self.changePort)
		self.HB2Layout.addWidget(self.cryptBox,1,1)

		self.HB2Layout.addWidget(QLabel(self.tr._translate("Changes : ")),0,2)

		self.saveChanges = QPushButton('&Save')
		self.saveChanges.setEnabled(False)
		self.saveChanges.clicked.connect(self.saveChangedAccount)
		self.HB2Layout.addWidget(self.saveChanges,1,2)

		self.clearChanges = QPushButton('&Clear')
		self.clearChanges.clicked.connect(self.clearChangedAccount)
		self.HB2Layout.addWidget(self.clearChanges,1,3)

		self.accountCommandLabel = QLabel()
		self.accountCommandLabel.setText(self.tr._translate('Account Command:'))
		self.accountCommandLabel.setToolTip(self.tr._translate("Exec command activated in notification.\nSee for : EXAMPLES."))
		self.HB2Layout.addWidget(self.accountCommandLabel, 2, 0)

		self.accountCommand = QComboBox()
		self.accountCommand.setToolTip(self.tr._translate("Exec command activated in notification.\nSee for : EXAMPLES."))
		self.accountCommand.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
		self.accountCommand.setEditable(True)
		templates = self.Parent.user_or_sys('contents/code/templates')
		if os.path.isfile(templates) :
			with open(templates, 'rb') as f :
				texts = f.read().split('\n')
				texts.remove('')
		else : texts = []
		#print texts, os.getcwd(), templates
		self.accountCommand.addItems(QStringList() << '' << texts)
		self.HB2Layout.addWidget(self.accountCommand, 2, 1, 2, 4)

		self.VBLayout.addLayout(self.HB2Layout)

		self.HB3Layout = QGridLayout()

		self.HB3Layout.addWidget(QLabel(self.tr._translate("Username : ")),0,0)

		self.HB3Layout.addWidget(QLabel(self.tr._translate("Password : ")),0,1)

		self.userNameLineEdit = KLineEdit()
		self.userNameLineEdit.setContextMenuEnabled(True)
		self.HB3Layout.addWidget(self.userNameLineEdit,1,0)

		self.passwordLineEdit = KLineEdit()
		self.passwordLineEdit.setContextMenuEnabled(True)
		self.passwordLineEdit.setPasswordMode(True)
		self.HB3Layout.addWidget(self.passwordLineEdit,1,1)

		self.VBLayout.addLayout(self.HB3Layout)

		self.setLayout(self.VBLayout)

	def disable_Del_n_Edit(self):
		self.accountListBox.itemClicked.connect(self.enable_Del_n_Edit)
		self.editAccountItem.setEnabled(False)
		self.delAccountItem.setEnabled(False)

	def enable_Del_n_Edit(self):
		self.accountListBox.itemClicked.disconnect(self.enable_Del_n_Edit)
		self.editAccountItem.setEnabled(True)
		self.delAccountItem.setEnabled(True)

	def changePort(self, str_):
		port = [POP3_PORT, POP3_SSL_PORT, IMAP4_PORT, IMAP4_SSL_PORT]
		connectMethod = self.connectMethodBox.itemData(self.connectMethodBox.currentIndex()).toString()
		cryptMethod = self.cryptBox.itemData(self.cryptBox.currentIndex()).toString()
		if str(connectMethod) in ('imap', 'imap\idle') :
			if POP3_PORT in port : port.remove(POP3_PORT)
			if POP3_SSL_PORT in port : port.remove(POP3_SSL_PORT)
		else :
			if IMAP4_PORT in port : port.remove(IMAP4_PORT)
			if IMAP4_SSL_PORT in port : port.remove(IMAP4_SSL_PORT)
		if str(cryptMethod) == 'None' :
			if IMAP4_SSL_PORT in port : port.remove(IMAP4_SSL_PORT)
			if POP3_SSL_PORT in port : port.remove(POP3_SSL_PORT)
		else :
			if IMAP4_PORT in port : port.remove(IMAP4_PORT)
			if POP3_PORT in port : port.remove(POP3_PORT)
		self.portBox.setValue(port[0] if len(port) else 0)

	def showCatalogChoice(self, str_):
		#print dateStamp() , 'signal received'
		if str_ in ('IMAP4', 'IMAP4\IDLE') :
			if 'resultString' not in dir(self) :
				self.resultString = 'INBOX'
			catalog = EnterMailBox(self.resultString, self)
			catalog.move(self.Parent.popupPosition(catalog.sizeHint()))
			catalog.exec_()
			#print dateStamp() , QString.fromUtf8(self.resultString)

	def changePasswFlag(self):
		self.passwordLineEdit.userTextChanged.disconnect(self.changePasswFlag)
		self.passwordLineEdit.setPasswordMode(True)
		self.passwordLineEdit.clear()
		self.passwordChanged = True
		self.connectFlag = False

	def clearChangedAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		if self.Status == 'BUSY' :
			return None
		self.clearFields()
		self.Status = 'FREE'

	def saveChangedAccount(self):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		if self.Status == 'READY' :
			accountName, authData = self.parsingValues()
			if accountName == '' :
				self.clearChangedAccount()
				self.Parent.eventNotification(self.tr._translate("Warning :\nSet Account Name!"))
				return None
			self.Status = 'CLEAR'
			self.delCurrentAccount(self.oldAccountName)
			self.accountListBox.addItem(accountName)
			if self.passwordChanged :
				self.Parent.wallet.writePassword(accountName, authData[3])
				authData[3] = ''
			addAccount(accountName, authData)

			self.accountList += [accountName]
			i = 0
			str_ = ''
			while i < len(self.accountList) :
				str_ += self.accountList[i] + ';'
				i += 1
			Settings.setValue('Accounts', str_)
			self.clearFields()
			self.saveChanges.setEnabled(False)
			self.Status = 'FREE'

	def clearFields(self):
		self.stringEditor.clear()
		self.userNameLineEdit.clear()
		self.passwordLineEdit.clear()
		if self.connectFlag :
			self.passwordLineEdit.userTextChanged.disconnect(self.changePasswFlag)
			self.connectFlag = False
		self.passwordLineEdit.setPasswordMode(True)
		self.serverLineEdit.clear()
		self.portBox.setValue(0)
		self.connectMethodBox.setCurrentIndex(0)
		self.cryptBox.setCurrentIndex(0)
		self.enabledBox.setCheckState(Qt.Unchecked)
		if 'resultString' in dir(self) :
			del self.resultString
		self.accountCommand.clearEditText()
		self.disable_Del_n_Edit()

	def editCurrentAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		self.Status = 'BUSY'
		accountName = self.accountListBox.currentItem().text()
		self.oldAccountName = accountName
		parameterList = readAccountData(accountName)
		self.stringEditor.setText(accountName)
		self.serverLineEdit.setText(str(parameterList[0]))
		if str(parameterList[7]) == '1' :
			self.enabledBox.setCheckState(Qt.Checked)
		i = 0
		count_ = int(self.connectMethodBox.count())
		self.resultString = parameterList[8]
		while i < count_ :
			str_ = self.connectMethodBox.itemData(i).toString()
			#print dateStamp() ,  str_, '-', str(parameterList[5]), '-', i
			if str_ == str(parameterList[5]) :
				self.connectMethodBox.setCurrentIndex(i)
			i += 1
		i = 0
		count_ = int(self.cryptBox.count())
		while i < count_ :
			str_ = self.cryptBox.itemData(i).toString()
			#print dateStamp() ,  str_, '-', str(parameterList[4]), '-', i
			if str_ == str(parameterList[4]) :
				self.cryptBox.setCurrentIndex(i)
			i += 1
		#print dateStamp() ,  parameterList[1]
		self.portBox.setValue(int(parameterList[1]))
		self.accountCommand.setEditText(parameterList[9])
		self.userNameLineEdit.setText(parameterList[2])
		self.passwordChanged = False
		self.passwordLineEdit.setPasswordMode(False)
		if self.Parent.wallet.hasEntry(self.oldAccountName) :
			self.passwordLineEdit.setText( '***EncriptedPassWord***' )
		else:
			self.passwordLineEdit.setText( '***EncriptedKey_not_created***' )
		self.connectFlag = self.passwordLineEdit.userTextChanged.connect(self.changePasswFlag)
		self.saveChanges.setEnabled(True)
		self.Status = 'READY'

	def addNewAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			self.Parent.configDenied()
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		if self.Status != 'FREE' :
			return None
		self.passwordLineEdit.setPasswordMode(True)
		str_ = self.stringEditor.userText()
		if to_unicode(str_) != '' :
			self.accountListBox.addItem(str_)
			accountName, authData = self.parsingValues()
			self.Parent.wallet.writePassword(accountName, authData[3])
			authData[3] = ''
			addAccount(accountName, authData)
			self.clearFields()

	def parsingValues(self):
		global Settings
		accountName = self.stringEditor.userText()
		accountServer = self.serverLineEdit.userText()
		connectMethod = self.connectMethodBox.itemData(self.connectMethodBox.currentIndex()).toString()
		cryptMethod = self.cryptBox.itemData(self.cryptBox.currentIndex()).toString()
		port_ = self.portBox.value()
		command = self.accountCommand.currentText()
		userName = self.userNameLineEdit.userText()
		userPassword = self.passwordLineEdit.userText()
		if self.enabledBox.isChecked() :
			enable = '1'
		else:
			enable = '0'
		if str(connectMethod) in ('imap', 'imap\idle') :
			inbox = self.resultString
		else :
			inbox = None
		# print dateStamp() ,  (accountName,accountServer,port_,connectMethod,cryptMethod, \
		#												userName,userPassword, 'parsingVal')
		return accountName,\
				[ accountServer, port_, userName, userPassword, \
				cryptMethod, connectMethod, '0', enable, inbox, command]

	def delCurrentAccount(self, accountName = ''):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		if self.Status == 'FREE' :
			item_ = self.accountListBox.currentRow()
			#accountGroup = self.accountListBox.currentItem()
			if item_ == -1 :
				return None
			accountName = (self.accountListBox.takeItem(item_)).text()
			# print dateStamp() ,  accountName.text(), str(accountName.text())
		elif self.Status != 'CLEAR' :
			return None
		else:
			i = 0
			while i < self.accountListBox.count() :
				if accountName == self.accountListBox.item(i).text() :
					self.accountListBox.takeItem(i)
					break
				i += 1
			pass

		Settings.remove(accountName)
		if self.Status != 'CLEAR' : self.Parent.wallet.removeEntry(accountName)
		try:
			self.accountList.remove(accountName)
		except ValueError, x :
			print dateStamp() ,  x, '  delAcc'
			pass
		finally:
			pass
		i = 0
		str_ = ''
		while i < len(self.accountList) :
			str_ += self.accountList[i] + ';'
			i += 1
		Settings.setValue('Accounts', str_)

	def eventClose(self, event):
		self.prnt.done(0)

class AppletSettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('AppletSettings')
		global Settings
		global ModuleExist

		timeOut = self.initValue('TimeOut', '600')
		AutoRun = self.initValue('AutoRun', '0')
		countProbe = self.initValue('CountProbe', '3')
		showError = self.initValue('ShowError', '1')
		waitThread = self.initValue('WaitThread', '120')
		stayDebLog = self.initValue('stayDebLog', '5')
		showVersion = self.initValue('ShowVersion', '1')
		timeOutGroup = self.initValue('TimeOutGroup', '3')
		maxShowedMail = self.initValue('MaxShowedMail', '1024')
		mailsInGroup = self.initValue('MailsInGroup', '5')

		self.layout = QGridLayout()

		self.timeOutLabel = QLabel(self.tr._translate("Timeout checking (sec.):"))
		self.layout.addWidget(self.timeOutLabel,0,0)
		self.timeOutBox = KIntSpinBox(10, 7200, 1, int(timeOut), self)
		self.timeOutBox.setMaximumWidth(75)
		self.layout.addWidget(self.timeOutBox, 0, 5)

		self.autoRunLabel = QLabel(self.tr._translate("Autorun mail checking :"))
		self.layout.addWidget(self.autoRunLabel,1,0)
		self.AutoRunBox = QCheckBox()
		if int(AutoRun) > 0 :
			self.AutoRunBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.AutoRunBox,1,5)

		self.countProbe = QLabel(self.tr._translate("Count of connect probe\nto mail server:"))
		self.layout.addWidget(self.countProbe,2,0)
		self.countProbeBox = KIntSpinBox(1, 10, 1, int(countProbe), self)
		self.layout.addWidget(self.countProbeBox, 2, 5)

		self.showError = QLabel(self.tr._translate("Show error messages :"))
		self.layout.addWidget(self.showError,3,0)
		self.showErrorBox = QCheckBox()
		if int(showError) > 0 :
			self.showErrorBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.showErrorBox,3,5)

		self.waitThreadLabel = QLabel(self.tr._translate("Autoexit of connect (sec.):"))
		self.layout.addWidget(self.waitThreadLabel,4,0)
		self.waitThreadBox = KIntSpinBox(3, 7200, 1, int(waitThread), self)
		self.layout.addWidget(self.waitThreadBox, 4, 5)

		self.stayDebLogLabel = QLabel(self.tr._translate("Stay Debug output Log :"))
		self.layout.addWidget(self.stayDebLogLabel,5,0)
		self.stayDebLogBox = KIntSpinBox(1, 50, 1, int(stayDebLog), self)
		self.stayDebLogBox.setMaximumWidth(75)
		self.layout.addWidget(self.stayDebLogBox, 5, 5)

		self.showVersion = QLabel(self.tr._translate("Show Version :"))
		self.layout.addWidget(self.showVersion,6,0)
		self.showVersionBox = QCheckBox()
		if int(showVersion) > 0 :
			self.showVersionBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.showVersionBox,6,5)

		self.timeOutGroupLabel = QLabel(self.tr._translate("Group Akonadi events timeout (sec.):"))
		self.timeOutGroupLabel.setEnabled(ModuleExist)
		self.layout.addWidget(self.timeOutGroupLabel, 7, 0)
		self.timeOutGroupBox = KIntSpinBox(1, 200, 1, int(timeOutGroup), self)
		self.timeOutGroupBox.setMaximumWidth(75)
		self.timeOutGroupBox.setEnabled(ModuleExist)
		self.layout.addWidget(self.timeOutGroupBox, 7, 5)

		self.maxMailLabel = QLabel(self.tr._translate("Max Count of Showed Mail :"))
		self.layout.addWidget(self.maxMailLabel, 8, 0)
		self.maxMailBox = KIntSpinBox(1, 1024, 1, int(maxShowedMail), self)
		self.maxMailBox.setMaximumWidth(75)
		self.maxMailBox.valueChanged[int].connect(self.showMailGroupping)
		self.layout.addWidget(self.maxMailBox, 8, 5)

		self.mailInGroupLabel = QLabel('\t' + self.tr._translate("Count of Mail in Group for account:"))
		self.mailInGroupLabel.setEnabled(False)
		self.layout.addWidget(self.mailInGroupLabel, 9, 0)
		self.mailInGroupBox = KIntSpinBox(1, 10, 1, int(mailsInGroup), self)
		self.mailInGroupBox.setMaximumWidth(75)
		self.mailInGroupBox.setEnabled(False)
		self.layout.addWidget(self.mailInGroupBox, 9, 5)

		self.setLayout(self.layout)
		self.maxMailBox.valueChanged.emit(int(maxShowedMail))

	def initValue(self, key_, default = '0'):
		global Settings
		if Settings.contains(key_) :
			#print dateStamp() ,  key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			Settings.setValue(key_, QVariant(default))
			#print dateStamp() ,  key_, Settings.value(key_).toString()
			return default

	def stateChanged(self, state):
		self.mailInGroupLabel.setEnabled(state)
		self.mailInGroupBox.setEnabled(state)

	def showMailGroupping(self, i):
		if i > self.mailInGroupBox.value() :
			self.stateChanged(True)
		else :
			self.stateChanged(False)

	def refreshSettings(self, parent = None):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')
		Settings.setValue('TimeOut', str(self.timeOutBox.value()))
		Settings.setValue('CountProbe', str(self.countProbeBox.value()))
		Settings.setValue('WaitThread', str(self.waitThreadBox.value()))
		Settings.setValue('stayDebLog', str(self.stayDebLogBox.value()))
		Settings.setValue('TimeOutGroup', str(self.timeOutGroupBox.value()))
		Settings.setValue('MaxShowedMail', str(self.maxMailBox.value()))
		Settings.setValue('MailsInGroup', str(self.mailInGroupBox.value()))
		if self.AutoRunBox.isChecked() :
			Settings.setValue('AutoRun', '1')
		else:
			Settings.setValue('AutoRun', '0')
		if self.showErrorBox.isChecked() :
			Settings.setValue('ShowError', '1')
		else:
			Settings.setValue('ShowError', '0')
		if self.showVersionBox.isChecked() :
			Settings.setValue('ShowVersion', '1')
		else:
			Settings.setValue('ShowVersion', '0')

		Settings.sync()

	def eventClose(self, event):
		self.prnt.done(0)

class PasswordManipulate(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('PasswordManipulate')

		self.VBLayout = QVBoxLayout()

		self.addAccountItem = QPushButton('&New')
		self.addAccountItem.setToolTip(self.tr._translate("Create new Password"))
		self.addAccountItem.clicked.connect(self.createNewKey)
		self.VBLayout.addWidget(self.addAccountItem)

		self.setLayout(self.VBLayout)

	def createNewKey(self):
		self.Parent.wallet.requestChangePassword(0)

	def eventClose(self, event):
		self.prnt.done(0)

class Font_n_Colour(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('Font_n_Colour')
		global Settings

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
		self.fieldBoxColourStyle = self.getRGBaStyle(QString(self.fieldBoxColourVar).toUInt())
		self.fieldFromColourStyle = self.getRGBaStyle(QString(self.fieldFromColourVar).toUInt())
		self.fieldSubjColourStyle = self.getRGBaStyle(QString(self.fieldSubjColourVar).toUInt())
		self.fieldDateColourStyle = self.getRGBaStyle(QString(self.fieldDateColourVar).toUInt())

		self.fontIcon = QIcon().fromTheme("font")
		self.colourIcon = QIcon().fromTheme("color")

		self.init()

	def init(self):
		self.layout = QGridLayout()

		self.label1 = QLabel(self.tr._translate("Normal"))
		self.label2 = QLabel(self.tr._translate("Select"))
		self.label1.setMaximumHeight(30)
		self.label2.setMaximumHeight(30)
		self.layout.addWidget(self.label1, 0, 0)
		self.layout.addWidget(self.label2, 0, 5)

		prefix, suffix = self.cursive_n_bold(self.headerBoldVar, self.headerItalVar)
		self.headerFontLabel = QLabel('<font face="' + self.headerFontVar + \
											'">' + prefix + self.tr._translate('Header :') + suffix + '</font>')
		self.headerFontLabel.setStyleSheet(self.headerColourStyle)
		self.layout.addWidget(self.headerFontLabel, 1, 0)

		self.headerFontButton = QPushButton(self.fontIcon, '')
		self.headerFontButton.setToolTip('Font')
		self.headerFontButton.clicked.connect(self.headerFont)
		self.layout.addWidget(self.headerFontButton, 1, 1)

		self.headerColourButton = QPushButton(self.colourIcon, '')
		self.headerColourButton.setToolTip('Color')
		self.connect(self.headerColourButton, SIGNAL('clicked()'), self.headerColour)
		self.layout.addWidget(self.headerColourButton, 1, 2)

		prefix, suffix = self.cursive_n_bold(self.accountBoldVar, self.accountItalVar)
		self.accountFontLabel = QLabel('<font face="' + \
						self.accountFontVar + '">' + prefix + self.tr._translate('Account :') + suffix + '</font>')
		self.accountFontLabel.setStyleSheet(self.accountColourStyle)
		self.layout.addWidget(self.accountFontLabel, 2, 0)
		prefix, suffix = self.cursive_n_bold(self.accountSBoldVar, self.accountSItalVar)
		self.accountSFontLabel = QLabel('<font face="' + self.accountSFontVar + \
												'">' + prefix + self.tr._translate('Account :') + suffix + '</font>')
		self.accountSFontLabel.setStyleSheet(self.accountSColourStyle)
		self.layout.addWidget(self.accountSFontLabel, 2, 5)

		self.accountFontButton = QPushButton(self.fontIcon, '')
		self.accountFontButton.setToolTip('Font')
		self.connect(self.accountFontButton, SIGNAL('clicked()'), self.accountFont)
		self.layout.addWidget(self.accountFontButton, 2, 1)

		self.accountColourButton = QPushButton(self.colourIcon, '')
		self.accountColourButton.setToolTip('Color')
		self.connect(self.accountColourButton, SIGNAL('clicked()'), self.accountColour)
		self.layout.addWidget(self.accountColourButton, 2, 2)

		self.accountSFontButton = QPushButton(self.fontIcon, '')
		self.accountSFontButton.setToolTip('Font')
		self.connect(self.accountSFontButton, SIGNAL('clicked()'), self.accountSFont)
		self.layout.addWidget(self.accountSFontButton, 2, 3)

		self.accountSColourButton = QPushButton(self.colourIcon, '')
		self.accountSColourButton.setToolTip('Color')
		self.connect(self.accountSColourButton, SIGNAL('clicked()'), self.accountSColour)
		self.layout.addWidget(self.accountSColourButton, 2, 4)

		prefix, suffix = self.cursive_n_bold(self.accountToolTipBoldVar, self.accountToolTipItalVar)
		self.accountToolTipFontLabel = QLabel('<font face="' + self.accountToolTipFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')
		self.accountToolTipFontLabel.setStyleSheet(self.accountToolTipColourStyle)
		self.layout.addWidget(self.accountToolTipFontLabel, 3, 0)
		prefix, suffix = self.cursive_n_bold(self.accountToolTipSBoldVar, self.accountToolTipSItalVar)
		self.accountToolTipSFontLabel = QLabel('<font face="' + self.accountToolTipSFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')
		self.accountToolTipSFontLabel.setStyleSheet(self.accountToolTipSColourStyle)
		self.layout.addWidget(self.accountToolTipSFontLabel, 3, 5)

		self.accountToolTipFontButton = QPushButton(self.fontIcon, '')
		self.accountToolTipFontButton.setToolTip('Font')
		self.connect(self.accountToolTipFontButton, SIGNAL('clicked()'), self.accountToolTipFont)
		self.layout.addWidget(self.accountToolTipFontButton, 3, 1)

		self.accountToolTipColourButton = QPushButton(self.colourIcon, '')
		self.accountToolTipColourButton.setToolTip('Color')
		self.connect(self.accountToolTipColourButton, SIGNAL('clicked()'), self.accountToolTipColour)
		self.layout.addWidget(self.accountToolTipColourButton, 3, 2)

		self.accountToolTipSFontButton = QPushButton(self.fontIcon, '')
		self.accountToolTipSFontButton.setToolTip('Font')
		self.connect(self.accountToolTipSFontButton, SIGNAL('clicked()'), self.accountToolTipSFont)
		self.layout.addWidget(self.accountToolTipSFontButton, 3, 3)

		self.accountToolTipSColourButton = QPushButton(self.colourIcon, '')
		self.accountToolTipSColourButton.setToolTip('Color')
		self.connect(self.accountToolTipSColourButton, SIGNAL('clicked()'), self.accountToolTipSColour)
		self.layout.addWidget(self.accountToolTipSColourButton, 3, 4)

		prefix, suffix = self.cursive_n_bold(self.countBoldVar, self.countItalVar)
		self.countFontLabel = QLabel('<font face="' + self.countFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')
		self.countFontLabel.setStyleSheet(self.countColourStyle)
		self.layout.addWidget(self.countFontLabel, 4, 0)
		prefix, suffix = self.cursive_n_bold(self.countSBoldVar, self.countSItalVar)
		self.countSFontLabel = QLabel('<font face="' + self.countSFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')
		self.countSFontLabel.setStyleSheet(self.countSColourStyle)
		self.layout.addWidget(self.countSFontLabel, 4, 5)

		self.countFontButton = QPushButton(self.fontIcon, '')
		self.countFontButton.setToolTip('Font')
		self.connect(self.countFontButton, SIGNAL('clicked()'), self.countFont)
		self.layout.addWidget(self.countFontButton, 4, 1)

		self.countColourButton = QPushButton(self.colourIcon, '')
		self.countColourButton.setToolTip('Color')
		self.connect(self.countColourButton, SIGNAL('clicked()'), self.countColour)
		self.layout.addWidget(self.countColourButton, 4, 2)

		self.countSFontButton = QPushButton(self.fontIcon, '')
		self.countSFontButton.setToolTip('Font')
		self.connect(self.countSFontButton, SIGNAL('clicked()'), self.countSFont)
		self.layout.addWidget(self.countSFontButton, 4, 3)

		self.countSColourButton = QPushButton(self.colourIcon, '')
		self.countSColourButton.setToolTip('Color')
		self.connect(self.countSColourButton, SIGNAL('clicked()'), self.countSColour)
		self.layout.addWidget(self.countSColourButton, 4, 4)

		prefix, suffix = self.cursive_n_bold(self.countToolTipBoldVar, self.countToolTipItalVar)
		self.countToolTipFontLabel = QLabel('<font face="' + self.countToolTipFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')
		self.countToolTipFontLabel.setStyleSheet(self.countToolTipColourStyle)
		self.layout.addWidget(self.countToolTipFontLabel, 5, 0)
		prefix, suffix = self.cursive_n_bold(self.countToolTipSBoldVar, self.countToolTipSItalVar)
		self.countToolTipSFontLabel = QLabel('<font face="' + self.countToolTipSFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')
		self.countToolTipSFontLabel.setStyleSheet(self.countToolTipSColourStyle)
		self.layout.addWidget(self.countToolTipSFontLabel, 5, 5)

		self.countToolTipFontButton = QPushButton(self.fontIcon, '')
		self.countToolTipFontButton.setToolTip('Font')
		self.connect(self.countToolTipFontButton, SIGNAL('clicked()'), self.countToolTipFont)
		self.layout.addWidget(self.countToolTipFontButton, 5, 1)

		self.countToolTipColourButton = QPushButton(self.colourIcon, '')
		self.countToolTipColourButton.setToolTip('Color')
		self.connect(self.countToolTipColourButton, SIGNAL('clicked()'), self.countToolTipColour)
		self.layout.addWidget(self.countToolTipColourButton, 5, 2)

		self.countToolTipSFontButton = QPushButton(self.fontIcon, '')
		self.countToolTipSFontButton.setToolTip('Font')
		self.connect(self.countToolTipSFontButton, SIGNAL('clicked()'), self.countToolTipSFont)
		self.layout.addWidget(self.countToolTipSFontButton, 5, 3)

		self.countToolTipSColourButton = QPushButton(self.colourIcon, '')
		self.countToolTipSColourButton.setToolTip('Color')
		self.connect(self.countToolTipSColourButton, SIGNAL('clicked()'), self.countToolTipSColour)
		self.layout.addWidget(self.countToolTipSColourButton, 5, 4)

		prefix, suffix = self.cursive_n_bold(self.fieldBoxBoldVar, self.fieldBoxItalVar)
		self.fieldBoxFontLabel = QLabel('<font face="' + self.fieldBoxFontVar + \
											'">' + prefix + self.tr._translate('field Box :') + suffix + '</font>')
		self.fieldBoxFontLabel.setStyleSheet(self.fieldBoxColourStyle)
		self.layout.addWidget(self.fieldBoxFontLabel, 6, 0)

		self.fieldBoxFontButton = QPushButton(self.fontIcon, '')
		self.fieldBoxFontButton.setToolTip('Font')
		self.fieldBoxFontButton.clicked.connect(self.fieldBoxFont)
		self.layout.addWidget(self.fieldBoxFontButton, 6, 1)

		self.fieldBoxColourButton = QPushButton(self.colourIcon, '')
		self.fieldBoxColourButton.setToolTip('Color')
		self.connect(self.fieldBoxColourButton, SIGNAL('clicked()'), self.fieldBoxColour)
		self.layout.addWidget(self.fieldBoxColourButton, 6, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldFromBoldVar, self.fieldFromItalVar)
		self.fieldFromFontLabel = QLabel('<font face="' + self.fieldFromFontVar + \
											'">' + prefix + self.tr._translate('field From :') + suffix + '</font>')
		self.fieldFromFontLabel.setStyleSheet(self.fieldFromColourStyle)
		self.layout.addWidget(self.fieldFromFontLabel, 7, 0)

		self.fieldFromFontButton = QPushButton(self.fontIcon, '')
		self.fieldFromFontButton.setToolTip('Font')
		self.fieldFromFontButton.clicked.connect(self.fieldFromFont)
		self.layout.addWidget(self.fieldFromFontButton, 7, 1)

		self.fieldFromColourButton = QPushButton(self.colourIcon, '')
		self.fieldFromColourButton.setToolTip('Color')
		self.connect(self.fieldFromColourButton, SIGNAL('clicked()'), self.fieldFromColour)
		self.layout.addWidget(self.fieldFromColourButton, 7, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldSubjBoldVar, self.fieldSubjItalVar)
		self.fieldSubjFontLabel = QLabel('<font face="' + self.fieldSubjFontVar + \
											'">' + prefix + self.tr._translate('field Subj :') + suffix + '</font>')
		self.fieldSubjFontLabel.setStyleSheet(self.fieldSubjColourStyle)
		self.layout.addWidget(self.fieldSubjFontLabel, 8, 0)

		self.fieldSubjFontButton = QPushButton(self.fontIcon, '')
		self.fieldSubjFontButton.setToolTip('Font')
		self.fieldSubjFontButton.clicked.connect(self.fieldSubjFont)
		self.layout.addWidget(self.fieldSubjFontButton, 8, 1)

		self.fieldSubjColourButton = QPushButton(self.colourIcon, '')
		self.fieldSubjColourButton.setToolTip('Color')
		self.connect(self.fieldSubjColourButton, SIGNAL('clicked()'), self.fieldSubjColour)
		self.layout.addWidget(self.fieldSubjColourButton, 8, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldDateBoldVar, self.fieldDateItalVar)
		self.fieldDateFontLabel = QLabel('<font face="' + self.fieldDateFontVar + \
											'">' + prefix + self.tr._translate('field Date :') + suffix + '</font>')
		self.fieldDateFontLabel.setStyleSheet(self.fieldDateColourStyle)
		self.layout.addWidget(self.fieldDateFontLabel, 9, 0)

		self.fieldDateFontButton = QPushButton(self.fontIcon, '')
		self.fieldDateFontButton.setToolTip('Font')
		self.fieldDateFontButton.clicked.connect(self.fieldDateFont)
		self.layout.addWidget(self.fieldDateFontButton, 9, 1)

		self.fieldDateColourButton = QPushButton(self.colourIcon, '')
		self.fieldDateColourButton.setToolTip('Color')
		self.connect(self.fieldDateColourButton, SIGNAL('clicked()'), self.fieldDateColour)
		self.layout.addWidget(self.fieldDateColourButton, 9, 2)

		self.setLayout(self.layout)

	def initValue(self, key_, defaultValue = ''):
		global Settings
		if Settings.contains(key_) :
			#print dateStamp() ,  key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			if defaultValue == '' :
				defaultValue = self.getSystemColor('int')
			Settings.setValue(key_, QVariant(defaultValue))
			#print dateStamp() ,  key_, Settings.value(key_).toString()
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

	def getFont(self, currentFont):
		font = QFontDialog()
		selectFont, yes = font.getFont(currentFont)
		str_ = string.split(selectFont.key(), ',')
		b = '0'; i = '0'
		if selectFont.bold() : b = '1'
		if selectFont.italic() : i = '1'
		font.done(0)
		return str_[0], str_[1], b, i, yes

	def getRGBaStyle(self, (colour, yes)):
		if yes :
			style = 'QLabel { color: rgba' + str(QColor().fromRgba(colour).getRgb()) + ';} '
		else :
			style = 'QLabel { color: rgba' + self.getSystemColor() + ';} '
		return style

	def getColour(self, (currentColour, yes)):
		colour = QColorDialog()
		selectColour, _yes = colour.getRgba(currentColour)
		colour.done(0)
		return str(selectColour), _yes, self.getRGBaStyle((selectColour, _yes))

	def headerFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.headerFontVar))
		if yes :
			self.headerFontVar, self.headerSizeVar, self.headerBoldVar, self.headerItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.headerBoldVar, self.headerItalVar)
			self.headerFontLabel.clear()
			self.headerFontLabel.setStyleSheet(self.headerColourStyle)
			self.headerFontLabel.setText('<font face="' + self.headerFontVar + \
									'">' + prefix + self.tr._translate('Header :') + suffix + '</font>')

	def headerColour(self):
		#print dateStamp() ,  self.headerColourVar, type(self.headerColourVar), QString(self.headerColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.headerColourVar).toUInt())
		if yes :
			self.headerColourVar = colour
			#print dateStamp() ,  self.headerColourVar, type(self.headerColourVar)
			self.headerColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.headerBoldVar, self.headerItalVar)
			self.headerFontLabel.clear()
			self.headerFontLabel.setStyleSheet(style)
			self.headerFontLabel.setText('<font face="' + self.headerFontVar + \
							'">' + prefix + self.tr._translate('Header :') + suffix + '</font>')

	def fieldBoxFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.fieldBoxFontVar))
		if yes :
			self.fieldBoxFontVar, self.fieldBoxSizeVar, self.fieldBoxBoldVar, self.fieldBoxItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.fieldBoxBoldVar, self.fieldBoxItalVar)
			self.fieldBoxFontLabel.clear()
			self.fieldBoxFontLabel.setStyleSheet(self.fieldBoxColourStyle)
			self.fieldBoxFontLabel.setText('<font face="' + self.fieldBoxFontVar + \
									'">' + prefix + self.tr._translate('field Box :') + suffix + '</font>')

	def fieldBoxColour(self):
		#print dateStamp() ,  self.fieldBoxColourVar, type(self.fieldBoxColourVar), QString(self.fieldBoxColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.fieldBoxColourVar).toUInt())
		if yes :
			self.fieldBoxColourVar = colour
			#print dateStamp() ,  self.fieldBoxColourVar, type(self.fieldBoxColourVar)
			self.fieldBoxColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.fieldBoxBoldVar, self.fieldBoxItalVar)
			self.fieldBoxFontLabel.clear()
			self.fieldBoxFontLabel.setStyleSheet(style)
			self.fieldBoxFontLabel.setText('<font face="' + self.fieldBoxFontVar + \
							'">' + prefix + self.tr._translate('field Box :') + suffix + '</font>')

	def fieldFromFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.fieldFromFontVar))
		if yes :
			self.fieldFromFontVar, self.fieldFromSizeVar, self.fieldFromBoldVar, self.fieldFromItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.fieldFromBoldVar, self.fieldFromItalVar)
			self.fieldFromFontLabel.clear()
			self.fieldFromFontLabel.setStyleSheet(self.fieldFromColourStyle)
			self.fieldFromFontLabel.setText('<font face="' + self.fieldFromFontVar + \
									'">' + prefix + self.tr._translate('field From :') + suffix + '</font>')

	def fieldFromColour(self):
		#print dateStamp() ,  self.fieldFromColourVar, type(self.fieldFromColourVar), QString(self.fieldFromColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.fieldFromColourVar).toUInt())
		if yes :
			self.fieldFromColourVar = colour
			#print dateStamp() ,  self.fieldFromColourVar, type(self.fieldFromColourVar)
			self.fieldFromColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.fieldFromBoldVar, self.fieldFromItalVar)
			self.fieldFromFontLabel.clear()
			self.fieldFromFontLabel.setStyleSheet(style)
			self.fieldFromFontLabel.setText('<font face="' + self.fieldFromFontVar + \
							'">' + prefix + self.tr._translate('field From :') + suffix + '</font>')

	def fieldSubjFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.fieldSubjFontVar))
		if yes :
			self.fieldSubjFontVar, self.fieldSubjSizeVar, self.fieldSubjBoldVar, self.fieldSubjItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.fieldSubjBoldVar, self.fieldSubjItalVar)
			self.fieldSubjFontLabel.clear()
			self.fieldSubjFontLabel.setStyleSheet(self.fieldSubjColourStyle)
			self.fieldSubjFontLabel.setText('<font face="' + self.fieldSubjFontVar + \
									'">' + prefix + self.tr._translate('field Subj :') + suffix + '</font>')

	def fieldSubjColour(self):
		#print dateStamp() ,  self.fieldSubjColourVar, type(self.fieldSubjColourVar), QString(self.fieldSubjColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.fieldSubjColourVar).toUInt())
		if yes :
			self.fieldSubjColourVar = colour
			#print dateStamp() ,  self.fieldSubjColourVar, type(self.fieldSubjColourVar)
			self.fieldSubjColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.fieldSubjBoldVar, self.fieldSubjItalVar)
			self.fieldSubjFontLabel.clear()
			self.fieldSubjFontLabel.setStyleSheet(style)
			self.fieldSubjFontLabel.setText('<font face="' + self.fieldSubjFontVar + \
							'">' + prefix + self.tr._translate('field Subj :') + suffix + '</font>')

	def fieldDateFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.fieldDateFontVar))
		if yes :
			self.fieldDateFontVar, self.fieldDateSizeVar, self.fieldDateBoldVar, self.fieldDateItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.fieldDateBoldVar, self.fieldDateItalVar)
			self.fieldDateFontLabel.clear()
			self.fieldDateFontLabel.setStyleSheet(self.fieldDateColourStyle)
			self.fieldDateFontLabel.setText('<font face="' + self.fieldDateFontVar + \
									'">' + prefix + self.tr._translate('field Date :') + suffix + '</font>')

	def fieldDateColour(self):
		#print dateStamp() ,  self.fieldDateColourVar, type(self.fieldDateColourVar), QString(self.fieldDateColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.fieldDateColourVar).toUInt())
		if yes :
			self.fieldDateColourVar = colour
			#print dateStamp() ,  self.fieldDateColourVar, type(self.fieldDateColourVar)
			self.fieldDateColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.fieldDateBoldVar, self.fieldDateItalVar)
			self.fieldDateFontLabel.clear()
			self.fieldDateFontLabel.setStyleSheet(style)
			self.fieldDateFontLabel.setText('<font face="' + self.fieldDateFontVar + \
							'">' + prefix + self.tr._translate('field Date :') + suffix + '</font>')

	def accountFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.accountFontVar))
		if yes :
			self.accountFontVar, self.accountSizeVar, \
									self.accountBoldVar, self.accountItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.accountBoldVar, self.accountItalVar)
			self.accountFontLabel.clear()
			self.accountFontLabel.setStyleSheet(self.accountColourStyle)
			self.accountFontLabel.setText('<font face="' + self.accountFontVar + \
									'">' + prefix + self.tr._translate('Account :') + suffix + '</font>')

	def accountColour(self):
		colour, yes, style = self.getColour(QString(self.accountColourVar).toUInt())
		if yes :
			self.accountColourVar = colour
			self.accountColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.accountBoldVar, self.headerItalVar)
			self.accountFontLabel.clear()
			self.accountFontLabel.setStyleSheet(style)
			self.accountFontLabel.setText('<font face="' + \
						self.accountFontVar + '">' + prefix + self.tr._translate('Account :') + suffix + '</font>')

	def accountSFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.accountSFontVar))
		if yes :
			self.accountSFontVar, self.accountSSizeVar, \
									self.accountSBoldVar, self.accountSItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.accountSBoldVar, self.accountSItalVar)
			self.accountSFontLabel.clear()
			self.accountSFontLabel.setStyleSheet(self.accountSColourStyle)
			self.accountSFontLabel.setText('<font face="' + self.accountSFontVar + '">' + \
									prefix + self.tr._translate('Account :') + suffix + '</font>')

	def accountSColour(self):
		colour, yes, style = self.getColour(QString(self.accountSColourVar).toUInt())
		if yes :
			self.accountSColourVar = colour
			self.accountSColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.accountSBoldVar, self.accountSItalVar)
			self.accountSFontLabel.clear()
			self.accountSFontLabel.setStyleSheet(style)
			self.accountSFontLabel.setText('<font face="' + self.accountSFontVar + \
												'">' + prefix + self.tr._translate('Account :') + suffix + '</font>')

	def accountToolTipFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.accountToolTipFontVar))
		if yes :
			self.accountToolTipFontVar, self.accountToolTipSizeVar, self.accountToolTipBoldVar, \
										self.accountToolTipItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.accountToolTipBoldVar, self.accountToolTipItalVar)
			self.accountToolTipFontLabel.clear()
			self.accountToolTipFontLabel.setStyleSheet(self.accountToolTipColourStyle)
			self.accountToolTipFontLabel.setText('<font face="' + self.accountToolTipFontVar + '">' + \
									prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')

	def accountToolTipColour(self):
		colour, yes, style = self.getColour(QString(self.accountToolTipColourVar).toUInt())
		if yes :
			self.accountToolTipColourVar = colour
			self.accountToolTipColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.accountToolTipBoldVar, self.accountToolTipItalVar)
			self.accountToolTipFontLabel.clear()
			self.accountToolTipFontLabel.setStyleSheet(style)
			self.accountToolTipFontLabel.setText('<font face="' + self.accountToolTipFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')

	def accountToolTipSFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.accountToolTipSFontVar))
		if yes :
			self.accountToolTipSFontVar, self.accountToolTipSSizeVar, self.accountToolTipSBoldVar, \
										self.accountToolTipSItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.accountToolTipSBoldVar, self.accountToolTipSItalVar)
			self.accountToolTipSFontLabel.clear()
			self.accountToolTipSFontLabel.setStyleSheet(self.accountToolTipSColourStyle)
			self.accountToolTipSFontLabel.setText('<font face="' + self.accountToolTipSFontVar + '">' + \
									prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')

	def accountToolTipSColour(self):
		colour, yes, style = self.getColour(QString(self.accountToolTipSColourVar).toUInt())
		if yes :
			self.accountToolTipSColourVar = colour
			self.accountToolTipSColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.accountToolTipSBoldVar, self.accountToolTipSItalVar)
			self.accountToolTipSFontLabel.clear()
			self.accountToolTipSFontLabel.setStyleSheet(style)
			self.accountToolTipSFontLabel.setText('<font face="' + self.accountToolTipSFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')

	def countFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.countFontVar))
		if yes :
			self.countFontVar, self.countSizeVar, self.countBoldVar, self.countItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.countBoldVar, self.countItalVar)
			self.countFontLabel.clear()
			self.countFontLabel.setStyleSheet(self.countColourStyle)
			self.countFontLabel.setText('<font face="' + self.countFontVar + \
									'">' + prefix + self.tr._translate('count :') + suffix + '</font>')

	def countColour(self):
		colour, yes, style = self.getColour(QString(self.countColourVar).toUInt())
		if yes :
			self.countColourVar = colour
			self.countColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.countBoldVar, self.countItalVar)
			self.countFontLabel.clear()
			self.countFontLabel.setStyleSheet(style)
			self.countFontLabel.setText('<font face="' + self.countFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')

	def countSFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.countSFontVar))
		if yes :
			self.countSFontVar, self.countSSizeVar, self.countSBoldVar, self.countSItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.countSBoldVar, self.countSItalVar)
			self.countSFontLabel.clear()
			self.countSFontLabel.setStyleSheet(self.countSColourStyle)
			self.countSFontLabel.setText('<font face="' + self.countSFontVar + \
									'">' + prefix + self.tr._translate('count :') + suffix + '</font>')

	def countSColour(self):
		colour, yes, style = self.getColour(QString(self.countSColourVar).toUInt())
		if yes :
			self.countSColourVar = colour
			self.countSColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.countSBoldVar, self.countSItalVar)
			self.countSFontLabel.clear()
			self.countSFontLabel.setStyleSheet(style)
			self.countSFontLabel.setText('<font face="' + self.countSFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')

	def countToolTipFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.countToolTipFontVar))
		if yes :
			self.countToolTipFontVar, self.countToolTipSizeVar, \
									self.countToolTipBoldVar, self.countToolTipItalVar = font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.countToolTipBoldVar, self.countToolTipItalVar)
			self.countToolTipFontLabel.clear()
			self.countToolTipFontLabel.setStyleSheet(self.countToolTipColourStyle)
			self.countToolTipFontLabel.setText('<font face="' + self.countToolTipFontVar + '">' + \
									prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')

	def countToolTipColour(self):
		colour, yes, style = self.getColour(QString(self.countToolTipColourVar).toUInt())
		if yes :
			self.countToolTipColourVar = colour
			self.countToolTipColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.countToolTipBoldVar, self.countToolTipItalVar)
			self.countToolTipFontLabel.clear()
			self.countToolTipFontLabel.setStyleSheet(style)
			self.countToolTipFontLabel.setText('<font face="' + self.countToolTipFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')

	def countToolTipSFont(self):
		font, size, bold, ital, yes = self.getFont(QFont(self.countToolTipSFontVar))
		if yes :
			self.countToolTipSFontVar, self.countToolTipSSizeVar, \
									self.countToolTipSBoldVar, self.countToolTipSItalVar =  font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(self.countToolTipSBoldVar, self.countToolTipSItalVar)
			self.countToolTipSFontLabel.clear()
			self.countToolTipSFontLabel.setStyleSheet(self.countToolTipSColourStyle)
			self.countToolTipSFontLabel.setText('<font face="' + self.countToolTipSFontVar + '">' + \
									prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')

	def countToolTipSColour(self):
		colour, yes, style = self.getColour(QString(self.countToolTipSColourVar).toUInt())
		if yes :
			self.countToolTipSColourVar = colour
			self.countToolTipSColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.countToolTipSBoldVar, self.countToolTipSItalVar)
			self.countToolTipSFontLabel.clear()
			self.countToolTipSFontLabel.setStyleSheet(style)
			self.countToolTipSFontLabel.setText('<font face="' + self.countToolTipSFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')

	def refreshSettings(self, parent = None):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Parent.wallet.setFolder('plasmaMailChecker')

		Settings.setValue('headerFont', self.headerFontVar)
		Settings.setValue('headerSize', self.headerSizeVar)
		Settings.setValue('headerBold', self.headerBoldVar)
		Settings.setValue('headerItal', self.headerItalVar)
		Settings.setValue('headerColour', self.headerColourVar)

		Settings.setValue('countFont', self.countFontVar)
		Settings.setValue('countSize', self.countSizeVar)
		Settings.setValue('countBold', self.countBoldVar)
		Settings.setValue('countItal', self.countItalVar)
		Settings.setValue('countColour', self.countColourVar)
		Settings.setValue('countSFont', self.countSFontVar)
		Settings.setValue('countSSize', self.countSSizeVar)
		Settings.setValue('countSBold', self.countSBoldVar)
		Settings.setValue('countSItal', self.countSItalVar)
		Settings.setValue('countSColour', self.countSColourVar)

		Settings.setValue('accountFont', self.accountFontVar)
		Settings.setValue('accountSize', self.accountSizeVar)
		Settings.setValue('accountBold', self.accountBoldVar)
		Settings.setValue('accountItal', self.accountItalVar)
		Settings.setValue('accountColour', self.accountColourVar)
		Settings.setValue('accountSFont', self.accountSFontVar)
		Settings.setValue('accountSSize', self.accountSSizeVar)
		Settings.setValue('accountSBold', self.accountSBoldVar)
		Settings.setValue('accountSItal', self.accountSItalVar)
		Settings.setValue('accountSColour', self.accountSColourVar)

		Settings.setValue('accountToolTipFont', self.accountToolTipFontVar)
		Settings.setValue('accountToolTipSize', self.accountToolTipSizeVar)
		Settings.setValue('accountToolTipBold', self.accountToolTipBoldVar)
		Settings.setValue('accountToolTipItal', self.accountToolTipItalVar)
		Settings.setValue('accountToolTipColour', self.accountToolTipColourVar)
		Settings.setValue('accountToolTipSFont', self.accountToolTipSFontVar)
		Settings.setValue('accountToolTipSSize', self.accountToolTipSSizeVar)
		Settings.setValue('accountToolTipSBold', self.accountToolTipSBoldVar)
		Settings.setValue('accountToolTipSItal', self.accountToolTipSItalVar)
		Settings.setValue('accountToolTipSColour', self.accountToolTipSColourVar)

		Settings.setValue('countToolTipFont', self.countToolTipFontVar)
		Settings.setValue('countToolTipSize', self.countToolTipSizeVar)
		Settings.setValue('countToolTipBold', self.countToolTipBoldVar)
		Settings.setValue('countToolTipItal', self.countToolTipItalVar)
		Settings.setValue('countToolTipColour', self.countToolTipColourVar)
		Settings.setValue('countToolTipSFont', self.countToolTipSFontVar)
		Settings.setValue('countToolTipSSize', self.countToolTipSSizeVar)
		Settings.setValue('countToolTipSBold', self.countToolTipSBoldVar)
		Settings.setValue('countToolTipSItal', self.countToolTipSItalVar)
		Settings.setValue('countToolTipSColour', self.countToolTipSColourVar)

		Settings.setValue('fieldBoxFont', self.fieldBoxFontVar)
		Settings.setValue('fieldBoxSize', self.fieldBoxSizeVar)
		Settings.setValue('fieldBoxBold', self.fieldBoxBoldVar)
		Settings.setValue('fieldBoxItal', self.fieldBoxItalVar)
		Settings.setValue('fieldBoxColour', self.fieldBoxColourVar)

		Settings.setValue('fieldFromFont', self.fieldFromFontVar)
		Settings.setValue('fieldFromSize', self.fieldFromSizeVar)
		Settings.setValue('fieldFromBold', self.fieldFromBoldVar)
		Settings.setValue('fieldFromItal', self.fieldFromItalVar)
		Settings.setValue('fieldFromColour', self.fieldFromColourVar)

		Settings.setValue('fieldSubjFont', self.fieldSubjFontVar)
		Settings.setValue('fieldSubjSize', self.fieldSubjSizeVar)
		Settings.setValue('fieldSubjBold', self.fieldSubjBoldVar)
		Settings.setValue('fieldSubjItal', self.fieldSubjItalVar)
		Settings.setValue('fieldSubjColour', self.fieldSubjColourVar)

		Settings.setValue('fieldDateFont', self.fieldDateFontVar)
		Settings.setValue('fieldDateSize', self.fieldDateSizeVar)
		Settings.setValue('fieldDateBold', self.fieldDateBoldVar)
		Settings.setValue('fieldDateItal', self.fieldDateItalVar)
		Settings.setValue('fieldDateColour', self.fieldDateColourVar)

		Settings.sync()

	def eventClose(self, event):
		self.prnt.done(0)

class EnterMailBox(KDialog):
	def __init__(self, text_, parent = None):
		KDialog.__init__(self, parent)
		self.prnt = parent
		self.text = text_

		self.setWindowTitle('Choice of MailBox')
		self.setButtons( KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel) )
		self.connect(self, SIGNAL("okClicked()"), self.ok)
		self.connect(self, SIGNAL("cancelClicked()"), self.cancel)

		self.browseText = KLineEdit()
		self.browseText.setToolTip(u'Defailt MailBox : Inbox\nFor example, GMail specified mailbox :\n[Gmail]/All\nor\n[Gmail]/Вся почта')
		self.browseText.setText(self.text)
		self.setMainWidget(self.browseText)

	def ok(self):
		self.prnt.resultString = self.browseText.userText()
		self.done(0)

	def cancel(self):
		self.prnt.resultString = self.text
		self.done(0)

	def closeEvent(self, event):
		event.ignore()

class AkonadiResources(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('EditAccounts')

		global ModuleExist
		print dateStamp(), 'Module PyKDE4.akonadi is'
		if not ModuleExist :
			print '\tnot'
		print '\tavailable.'
		self.init()

	def init(self):

		self.Status = 'FREE'
		self.connectFlag = False
		global Settings
		global ModuleExist
		self.layout = QGridLayout()

		self.VBLayout = QVBoxLayout()

		self.akonadiServer = QPushButton('&Restart')
		self.akonadiServer.hide()
		#self.akonadiServer.setMaximumWidth(50)
		self.akonadiServer.setToolTip(self.tr._translate("Restart Akonadi Server"))
		self.akonadiServer.clicked.connect(self.restartAkonadi)
		self.layout.addWidget(self.akonadiServer, 0, 4)

		self.akonadiState = QLabel()
		if not ModuleExist :
			self.akonadiState.setText(self.tr._translate("Module PyKDE4.akonadi isn`t available."))
			akonadiAccList = []
		else :
			self.akonadiState.setText( self.tr._translate("Akonadi Server is : ") + \
										StateSTR[Akonadi.ServerManager.state()] )
			akonadiAccList = akonadiAccountList()
		self.layout.addWidget(self.akonadiState, 0, 0)

		self.accountListBox = KListWidget()
		self.accountListBox.hide()
		self.accountList = []
		for accountName in akonadiAccList:
			self.accountListBox.addItem(accountName)
			self.accountList += [accountName]
		#print dateStamp() ,  self.accountList
		self.layout.addWidget(self.accountListBox,1,0,2,3)

		self.stringEditor = KLineEdit()
		self.stringEditor.hide()
		self.stringEditor.setToolTip(self.tr._translate("Deprecated char : '<b>;</b>'"))
		self.stringEditor.setContextMenuEnabled(True)
		self.layout.addWidget(self.stringEditor,3,0)

		self.addAccountItem = QPushButton('&Add')
		self.addAccountItem.hide()
		self.addAccountItem.setToolTip(self.tr._translate("Add new Account"))
		self.addAccountItem.clicked.connect(self.addNewAccount)
		self.layout.addWidget(self.addAccountItem,3,4)

		self.editAccountItem = QPushButton('&Edit')
		self.editAccountItem.hide()
		self.editAccountItem.setToolTip(self.tr._translate("Edit current Account"))
		self.editAccountItem.clicked.connect(self.editCurrentAccount)
		self.layout.addWidget(self.editAccountItem,2,4)

		self.delAccountItem = QPushButton('&Del')
		self.delAccountItem.hide()
		self.delAccountItem.setToolTip(self.tr._translate("Delete current Account"))
		self.delAccountItem.clicked.connect(self.delCurrentAccount)
		self.layout.addWidget(self.delAccountItem,1,4)

		self.VBLayout.addLayout(self.layout)

		self.HB1Layout = QGridLayout()

		self.collectionIDLabel = QLabel()
		self.collectionIDLabel.hide()
		self.collectionIDLabel.setText('Collection :')
		self.HB1Layout.addWidget(self.collectionIDLabel, 0, 0)

		self.collectionID = QLabel()
		self.collectionID.hide()
		self.collectionID.setText('-- "" --')
		self.HB1Layout.addWidget(self.collectionID, 0, 1)

		self.collectionResource = QLabel()
		self.collectionResource.hide()
		self.collectionResource.setText('-- "" --')
		self.HB1Layout.addWidget(self.collectionResource, 0, 2)

		self.enableLabel = QLabel(self.tr._translate("Enable : "))
		self.enableLabel.hide()
		self.HB1Layout.addWidget(self.enableLabel, 0, 3)

		self.enabledBox = QCheckBox()
		Enabled = AppletSettings().initValue('Enabled', '1')
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.enabledBox.hide()
		self.HB1Layout.addWidget(self.enabledBox, 0, 4, Qt.AlignHCenter)

		self.VBLayout.addLayout(self.HB1Layout)

		self.HB2Layout = QGridLayout()

		self.collectionChoice = QLabel()
		self.collectionChoice.hide()
		self.collectionChoice.setText('Search:')
		self.HB2Layout.addWidget(self.collectionChoice, 0, 0)

		self.searchColl = QPushButton('...')
		self.searchColl.hide()
		self.searchColl.clicked.connect(self.collectionSearch)
		self.HB2Layout.addWidget(self.searchColl, 0, 1)

		self.saveChanges = QPushButton('&Save')
		self.saveChanges.hide()
		self.saveChanges.clicked.connect(self.saveChangedAccount)
		self.HB2Layout.addWidget(self.saveChanges, 0, 2)

		self.clearChanges = QPushButton('&Clear')
		self.clearChanges.hide()
		self.clearChanges.clicked.connect(self.clearChangedAccount)
		self.HB2Layout.addWidget(self.clearChanges, 0, 3)

		self.accountCommandLabel = QLabel()
		self.accountCommandLabel.hide()
		self.accountCommandLabel.setText(self.tr._translate('Account Command:'))
		self.accountCommandLabel.setToolTip('Exec command activated in notification.\nExample: \n' + \
						'qdbus org.kde.kmail /KMail org.kde.kmail.kmail.showMail %mail_id %mail_id\n' + \
						'qdbus org.kde.kmail /KMail org.kde.kmail.kmail.selectFolder %dir_id')
		self.HB2Layout.addWidget(self.accountCommandLabel, 1, 0)

		self.accountCommand = KLineEdit()
		self.accountCommand.hide()
		self.accountCommand.setContextMenuEnabled(True)
		self.HB2Layout.addWidget(self.accountCommand, 1, 1, 1, 4)

		self.VBLayout.addLayout(self.HB2Layout)

		self.setLayout(self.VBLayout)

		if ModuleExist and Akonadi.ServerManager.state() != Akonadi.ServerManager.State(4) :
			self.initAkonadiAccountManager()

	def initAkonadiAccountManager(self):
		self.akonadiServer.show()
		self.enableLabel.show()
		self.enabledBox.show()
		self.accountListBox.show()
		self.stringEditor.show()
		self.addAccountItem.show()
		self.clearChanges.show()
		self.saveChanges.show()
		self.collectionChoice.show()
		self.collectionResource.show()
		self.collectionID.show()
		self.collectionIDLabel.show()
		self.searchColl.show()
		self.delAccountItem.show()
		self.editAccountItem.show()
		self.accountCommandLabel.show()
		self.accountCommand.show()

	def collectionSearch(self):
		self.Control = ControlWidget()
		self.Control.move(self.Parent.popupPosition(self.Control.size()))
		if self.Control.exec_() :
			col = self.Control.selectedCollection()
			## print dateStamp(), col.name().toUtf8(), col.id(), col.resource()
			self.collectionID.setText(str(col.id()))
			self.nameColl = col.name()
			self.stringEditor.setText(self.nameColl)
			self.collectionResource.setText(col.resource())

	def clearChangedAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'BUSY' :
			return None
		self.clearFields()
		self.Status = 'FREE'

	def saveChangedAccount(self):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'READY' :
			accountName = self.stringEditor.userText()
			if accountName == '' :
				self.clearChangedAccount()
				self.Parent.eventNotification(self.tr._translate("Warning :\nSet Account Name!"))
				return None
			self.Status = 'CLEAR'
			self.delCurrentAccount(self.oldAccountName)
			self.accountListBox.addItem(accountName)
			if self.enabledBox.isChecked() :
				enable = '1'
			else:
				enable = '0'
			Settings.beginGroup('Akonadi account')
			Settings.setValue(accountName, self.collectionID.text() + _0_ + enable + _0_ + \
								self.collectionResource.text() + _0_ + self.nameColl + \
								_0_ + self.accountCommand.text())
			Settings.endGroup()

			self.accountList += [accountName]
			self.clearFields()
			self.Status = 'FREE'

	def clearFields(self):
		self.stringEditor.clear()
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.collectionResource.clear()
		self.collectionID.clear()
		self.accountCommand.clear()

	def editCurrentAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Status = 'BUSY'
		accountName = self.accountListBox.currentItem().text()
		self.oldAccountName = accountName
		Settings.beginGroup('Akonadi account')
		data = Settings.value(accountName).toString()
		Settings.endGroup()
		parameterList = string.split(data, _0_)
		self.stringEditor.setText(accountName)
		self.collectionID.setText(parameterList[0])
		if parameterList.count() > 1 and str(parameterList[1]) == '1' :
			self.enabledBox.setCheckState(Qt.Checked)
		if parameterList.count() > 2 :
			self.collectionResource.setText(parameterList[2])
		if parameterList.count() > 3 :
			self.nameColl = parameterList[3]
		if parameterList.count() > 4 :
			self.accountCommand.setText( parameterList[4] )
		self.Status = 'READY'

	def addNewAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			self.Parent.configDenied()
			return None
		if self.Status != 'FREE' :
			return None
		str_ = self.stringEditor.userText()
		if str_ != '' :
			self.accountList += [str_]
			self.accountListBox.addItem(str_)
			if self.enabledBox.isChecked() :
				enable = '1'
			else:
				enable = '0'
			Settings.beginGroup('Akonadi account')
			Settings.setValue(str_, self.collectionID.text() + _0_ + enable + _0_ + \
								self.collectionResource.text() + _0_ + self.nameColl + \
								_0_ + self.accountCommand.text())
			Settings.endGroup()
			self.clearFields()

	def delCurrentAccount(self, accountName = ''):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'FREE' :
			item_ = self.accountListBox.currentRow()
			#accountGroup = self.accountListBox.currentItem()
			if item_ == -1 :
				return None
			accountName = (self.accountListBox.takeItem(item_)).text()
			# print dateStamp() ,  accountName.text(), str(accountName.text())
		elif self.Status != 'CLEAR' :
			return None
		else:
			i = 0
			while i < self.accountListBox.count() :
				if accountName == self.accountListBox.item(i).text() :
					self.accountListBox.takeItem(i)
					break
				i += 1
			pass

		Settings.beginGroup('Akonadi account')
		Settings.remove(accountName)
		Settings.endGroup()
		try:
			self.accountList.remove(accountName)
		except ValueError, x :
			print dateStamp() ,  x, '  delAcc'
			pass
		finally:
			pass

	def restartAkonadi(self):
		server = Akonadi.Control()
		#server.widgetNeedsAkonadi(self)
		if Akonadi.ServerManager.isRunning() :
			if not server.restart(self) :
				print dateStamp(), 'Unable to start Akonadi Server '
		else :
			if not server.start(self) :
				print dateStamp(), 'Unable to start Akonadi Server '
		self.akonadiState.setText( self.tr._translate("Akonadi Server is : ") + \
										StateSTR[Akonadi.ServerManager.state()] )

	def eventClose(self, event):
		self.prnt.done(0)

def CreateApplet(parent):
	return plasmaMailChecker(parent)

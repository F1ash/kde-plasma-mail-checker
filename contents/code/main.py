# -*- coding: utf-8 -*-

try :
	global warningMsg
	global Settings
	global RESULT
	global NewMailAttributes
	global ErrorMsg
	global g
	global LOG_FILENAME
	LOG_FILENAME = 'mailChecker.log'
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from PyKDE4.kdecore import *
	from PyKDE4.kdeui import *
	from PyKDE4.plasma import Plasma
	from PyKDE4 import plasmascript
	import poplib, imaplib, string, socket, time, os.path, logging, random, sys, email.header, pdb, gc, locale
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', \
											datefmt='%Y-%m-%d %H:%M:%S', filename=LOG_FILENAME)
	RESULT = []
	Settings = QSettings('mailChecker','mailChecker')
	NewMailAttributes = []
	ErrorMsg = ''
	warningMsg = ''
	#sys.stderr = open('/dev/shm/errorMailChecker' + str(time.time()) + '.log','w')
	sys.stdout = open('/tmp/outMailChecker' + \
						time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
except ImportError, warningMsg :
	print "ImportError", warningMsg
	logging.debug(warningMsg)
finally:
	'O`key'

GeneralLOCK = QMutex()
LOCK = QReadWriteLock()

def addAccount(account, data_ = ['']):
	LOCK.lockForWrite()
	global Settings
	accounts_ = Settings.value('Accounts').toString()
	Settings.setValue('Accounts', accounts_ + ';' + str(account))
	Settings.beginGroup(str(account))
	Settings.setValue('server', str(data_[0]))
	Settings.setValue('port', str(data_[1]))
	Settings.setValue('login', str(data_[2]))
	Settings.setValue('authentificationMethod', str(data_[4]))
	Settings.setValue('connectMethod', str(data_[5]))
	if str(data_[6]) != '0' :
		Settings.setValue('lastElemValue', str(data_[6]))
	Settings.endGroup()
	Settings.sync()
	LOCK.unlock()
	pass

def readAccountData(account = ''):
	LOCK.lockForRead()
	global Settings
	Settings.beginGroup(account)
	serv_ = Settings.value('server').toString()
	port_ = Settings.value('port').toString()
	login_ = Settings.value('login').toString()
	authMethod_ = Settings.value('authentificationMethod').toString()
	connMethod_ = Settings.value('connectMethod').toString()
	last_ = Settings.value('lastElemValue').toString()
	Settings.endGroup()
	LOCK.unlock()
	return [str(serv_), str(port_), str(login_), '', str(authMethod_), str(connMethod_), str(last_)]

def initPOP3Cache():
	LOCK.lockForWrite()
	global Settings
	dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
	if  not os.path.isdir(dir_) :
		os.mkdir(dir_)
	for accountName in string.split( Settings.value('Accounts').toString(), ';' ):
		Settings.beginGroup(str(accountName))
		if Settings.value('connectMethod').toString() == 'pop' :
			if not os.path.isfile(dir_ + '/' + str(accountName) + '.cache') :
				f = open(dir_ + '/' + str(accountName) + '.cache', 'w')
				f.close()
			f = open(dir_ +  '/' + str(accountName) + '.cache', 'r')
			c = open('/dev/shm/' + str(accountName) + '.cache', 'w')
			c.writelines(f.readlines())
			f.close()
			c.close()
		Settings.endGroup()
	LOCK.unlock()

def savePOP3Cache():
	LOCK.lockForWrite()
	global Settings
	dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
	for accountName in string.split( Settings.value('Accounts').toString(), ';' ):
		Settings.beginGroup(str(accountName))
		if Settings.value('connectMethod').toString() == 'pop' :
			f = open(dir_ + '/' + str(accountName) + '.cache', 'w')
			if os.path.isfile('/dev/shm/' + str(accountName) + '.cache') :
				c = open('/dev/shm/' + str(accountName) + '.cache', 'r')
				f.writelines(c.readlines())
				c.close()
			f.close()
		Settings.endGroup()
	LOCK.unlock()

def defineUIDL(accountName = '', str_ = ''):
	Result = True
	# print accountName
	x = ''
	STR = []
	try :
		f = open('/dev/shm/' + str(accountName) + '.cache', 'r')
		STR = f.readlines()
		# print STR
	except x :
		print x, '  defUidl'
	finally :
		for uid_ in STR :
			# print string.split(uid_, '\n')[0] , '--- ', str_
			if str_ == string.split(uid_, '\n')[0] :
				Result = False
				break
		f.close()
	return Result

def checkNewMailPOP3(accountData = ['', '']):
	global ErrorMsg
	x = ''
	try:
		global NewMailAttributes
		newMailExist = False
		probeError = True
		authentificationData = readAccountData(accountData[0])
		lastElemUid = authentificationData[6]

		if authentificationData[4] == 'SSL' :
			m = poplib.POP3_SSL(authentificationData[0], authentificationData[1])
		else:
			m = poplib.POP3(authentificationData[0], authentificationData[1])

		auth_login = m.user(authentificationData[2])
		auth_passw = m.pass_( accountData[1] )

		countAll = int(m.stat()[0])
		countNew = 0
		mailUidls = []
		for uidl_ in m.uidl()[1] :
			currentElemUid = string.split(uidl_,' ')[1]
			mailUidls += [currentElemUid + '\n']
			if defineUIDL(accountData[0], currentElemUid) :
				Result =''
				for str_ in m.top( int(string.split(uidl_,' ')[0]) , 0)[1] :
					if str_[:5] == 'From:' :
						Result += unicode(str_, 'UTF-8') + ' '
					if str_[:5] == 'Subje' :
						# print str_, email.header.decode_header(str_)
						if len(email.header.decode_header(str_)) == 1 :
							Result += unicode(str_, 'UTF-8') + ' '
						else :
							Result += 'Subject: ' + email.header.decode_header(str_)[1][0].\
														decode(email.header.decode_header(str_)[1][1]) + ' '
				# print Result
				NewMailAttributes += [Result]
				newMailExist = newMailExist or True
				countNew += 1

		m.quit()

		c = open('/dev/shm/' + str(accountData[0]) + '.cache', 'w')
		# print mailUidls
		c.writelines( mailUidls )
		c.close()

	except poplib.error_proto, x :
		print x, '  POP3_1'
		ErrorMsg += '\n' + unicode(x[0],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		print x, '  POP3_2'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		print x, '  POP3_3'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except x:
		print x, '  POP3_4'
		ErrorMsg += 'Unknown Error\n'
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew

def checkNewMailIMAP4(accountData = ['', '']):
	global ErrorMsg
	global Settings
	x = ''
	try:
		global NewMailAttributes
		newMailExist = False
		probeError = True
		authentificationData = readAccountData(accountData[0])
		lastElemTime = authentificationData[6]

		if authentificationData[4] == 'SSL' :
			m = imaplib.IMAP4_SSL(authentificationData[0], authentificationData[1])
		else:
			m = imaplib.IMAP4(authentificationData[0], authentificationData[1])

		if m.login( authentificationData[2], accountData[1] )[0] == 'OK' :
			answer = m.select()
			if answer[0] == 'OK' :
				countAll = int(answer[1][0])
				countNew = 0
				i = countAll
				while i > 0 :
					currentElemTime_raw = string.split(m.fetch(i,"INTERNALDATE")[1][0],' ')
					currentElemTime_Internal = currentElemTime_raw[1] + ' ' \
												+ currentElemTime_raw[2] + ' ' \
												+ currentElemTime_raw[3] + ' ' \
												+ currentElemTime_raw[4]
					# print currentElemTime_Internal
					date_ = imaplib.Internaldate2tuple(currentElemTime_Internal)
					currentElemTime = str(time.mktime(date_))
					# print currentElemTime
					if currentElemTime > lastElemTime :
						Result =''
						for str_ in string.split(m.fetch(i,"(BODY[HEADER])")[1][0][1],'\r\n') :
							if str_[:5] == 'From:' :
								Result += unicode(str_, 'UTF-8') + ' '
							if str_[:5] == 'Subje' :
								# print str_, email.header.decode_header(str_)
								if len(email.header.decode_header(str_)) == 1 :
									Result += unicode(str_, 'UTF-8') + ' '
								else :
									Result += 'Subject: ' + email.header.decode_header(str_)[1][0].\
														decode(email.header.decode_header(str_)[1][1]) + ' '
						# print Result
						NewMailAttributes += [Result]
						newMailExist = newMailExist or True
						countNew += 1
					else:
						break
					i += -1
			else:
				#print 'selectDirError'
				logging.debug('selectDirError')
				probeError, countAll, countNew = False, 0, 0
		else:
			#print 'AuthError'
			logging.debug('AuthError')
			probeError, countAll, countNew = False, 0, 0
			pass

		if newMailExist :
			lastElemTime_raw = string.split(m.fetch(countAll,"INTERNALDATE")[1][0],' ')
			lastElemTime_Internal = lastElemTime_raw[1] + ' ' \
									+ lastElemTime_raw[2] + ' ' \
									+ lastElemTime_raw[3] + ' ' \
									+ lastElemTime_raw[4]
			# print lastElemTime_Internal
			date_ = imaplib.Internaldate2tuple(lastElemTime_Internal)
			lastElemTime = str(time.mktime(date_))
			# print lastElemTime
			Settings.beginGroup(accountData[0])
			Settings.setValue('lastElemValue', lastElemTime)
			Settings.endGroup()
		else:
			# print 'New message(s) not found.'
			if countAll == 0 :
				Settings.beginGroup(accountData[0])
				Settings.setValue('lastElemValue', '0')
				Settings.endGroup()

		m.close()
		m.logout()

		Settings.sync()

	except imaplib.IMAP4.error, x :
		print x, '  IMAP4_1'
		ErrorMsg += '\n' + unicode(x[0],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		print x, '  IMAP4_2'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		print x, '  IMAP4_3'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except x:
		print x, '  IMAP4_5'
		ErrorMsg += 'Unknown Error\n'
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew

def connectProbe(probe_ = 3, checkNewMail = None, authentificationData = ['', '']):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	i = 0
	while i < probe_ :
		# print 'Probe ', i + 1
		test_, all_, new_ = checkNewMail(authentificationData)
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + authentificationData[0] +'\n'
	return Result, all_, new_, ''

def checkMail(accountData = ['', '']):
	global Settings
	Msg = ''
	if accountData[0] != '' :
		# print accountName
		countProbe_raw = Settings.value('CountProbe')
		# print countProbe_raw.toString()
		Settings.beginGroup(accountData[0])
		connectMethod = Settings.value('connectMethod')
		Settings.endGroup()
		try:
			countProbe = int(countProbe_raw.toString())
		except ValueError:
			print x, '  checkMail'
			countProbe = 3
		finally:
			pass
		# print str(connectMethod.toString()),'---'
		# print countProbe
		if str(connectMethod.toString()) == 'pop' :
			return  connectProbe(countProbe, checkNewMailPOP3, accountData)
		elif str(connectMethod.toString()) == 'imap' :
			return connectProbe(countProbe, checkNewMailIMAP4, accountData)
		else:
			Msg = 'connectMethod Error\n'
	else:
		Msg = 'accountName Error\n'
	return False, None, None, Msg

class Translator(QTranslator):
	def __init__(self, context = '', parent=None):
		QTranslator.__init__(self, parent)

		lang = locale.getdefaultlocale()[0][:2]
		#print lang
		kdehome = unicode(KGlobal.dirs().localkdedir())
		_Path = kdehome + "share/apps/plasma/plasmoids/plasmaMailChecker/contents/code/"
		self.load(QString(lang), QString(_Path), QString('qm'))
		self.context = context

	def _translate(self, sourceText):
		res = QTranslator.translate(self, self.context, sourceText)
		if len(res) == 0:
			res = QString(sourceText)
		return res

class ThreadCheckMail(QThread):
	def __init__(self, obj = None, accountData = [('', '')], timeout = 120, parent = None):
		QThread.__init__(self, parent)

		self.Parent = obj
		self.setTerminationEnabled(False)
		self.Timer = QTimer()
		self.Timer.setSingleShot(True)
		self.Timer.timeout.connect(self._terminate)
		self.timeout = int(timeout) * 1000
		self.accData = accountData

	def run(self):
		try:
			GeneralLOCK.lock()

			global ErrorMsg
			global NewMailAttributes
			global Settings
			global RESULT
			NewMailAttributes = []
			newMailExist = False
			ErrorMsg = ''
			x = ''
			RESULT = []
			self.Timer.start(self.timeout)
			for accountData in self.accData :
				RESULT += [checkMail(accountData)]

		except x :
			print x, '  thread'
			#tb = sys.exc_info()[2]
			#pdb.post_mortem(tb)
			logging.debug(x)
		finally :
			self.Timer.stop()
			GeneralLOCK.unlock()
			#QApplication.postEvent(self.Parent, QEvent(1010))
			self.Parent.emit(SIGNAL('refresh'))
			pass
		return

	def _terminate(self):
		global ErrorMsg
		ErrorMsg += 'Timeout thread error'
		print 'Mail thread timeout terminating...'
		self.Timer.stop()
		GeneralLOCK.unlock()
		self.Parent.emit(SIGNAL('refresh'))
		self.terminate()

class plasmaMailChecker(plasmascript.Applet):
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self,parent)

		self.initStat = False
		self.checkResult = []

		self.panelIcon = Plasma.IconWidget()
		self.icon = Plasma.IconWidget()
		self.listNewMail = []
		self.connectIconsFlag = False
		self.tr = Translator('plasmaMailChecker')

	def init(self):
		global Settings
		self.setHasConfigurationInterface(True)

		self.Timer = QTimer()
		self.Timer.timeout.connect(self._refreshData)

		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.layout.setSpacing(0)
		self.connect(self.applet, SIGNAL('destroyed()'), self.eventClose)
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.connect(self, SIGNAL('access'), self.processInit)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())

		if not os.path.exists(self.kdehome+"share/apps/plasmaMailChecker/plasmaMailChecker.notifyrc"):
			if os.path.exists(self.kdehome+"share/apps"):
				self.createNotifyrc(self.kdehome)
		iconPath = self.kdehome + \
				"share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png"

		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.titleLayout = QGraphicsLinearLayout()
			self.titleLayout.setOrientation(Qt.Horizontal)

			self.TitleDialog = Plasma.Label()
			self.TitleDialog.setText(self.tr._translate("<font color=blue><b>M@il Checker</b></font>"))
			self.titleLayout.addItem(self.TitleDialog)

			self.icon.setIcon(iconPath)
			self.icon.setMaximumSize(35.0, 35.0)
			self.icon.setToolTip(self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"))
			self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			self.titleLayout.addItem(self.icon)

			self.layout.setOrientation(Qt.Vertical)
			self.layout.addItem(self.titleLayout)
			self.setMinimumSize(150.0,75.0)
			self.createDialogWidget()
		else:
			self.createIconWidget()

		self.setLayout(self.layout)

		AutoRun = Settings.value('AutoRun').toString()
		try:
			int(AutoRun)
		except ValueError, x:
			print x, '  AutoRun'
			#logging.debug(x)
			AutoRun = '0'
		finally:
			pass
		if AutoRun != '0' :
			QApplication.postEvent(self, QEvent(QEvent.User))

	def customEvent(self, event):
		if event.type() == QEvent.User :
			self.enterPassword()
		elif event.type() == 1011 :
			self._refreshData()
		pass

	def createDialogWidget(self):
		global Settings
		if 'Dialog' in dir(self) :
			self.layout.removeItem(self.Dialog)
			del self.label
			del self.countList
			del self.labelStat
			del self.Dialog
			#print 're-createDialog'
		self.Dialog = QGraphicsGridLayout()
		i = 0
		self.label = []
		self.countList = []
		for accountName in string.split(Settings.value('Accounts').toString(),';') :
			self.label += [accountName]
			self.countList += [accountName]

			self.label[i] = Plasma.Label()
			self.countList[i] = Plasma.Label()
			self.label[i].setToolTip('Account ' + accountName)

			self.Dialog.addItem(self.label[i],i,0)
			self.Dialog.addItem(self.countList[i],i,1)
			i += 1

		self.labelStat = Plasma.Label()
		self.labelStat.setText(self.tr._translate("<font color=red><b>..stopped..</b></font>"))
		self.Dialog.addItem(self.labelStat, i, 0)

		self.Dialog.updateGeometry()
		self.layout.addItem(self.Dialog)

		self.setLayout(self.layout)

	def processInit(self):
		global Settings
		Settings.sync()
		timeOut = Settings.value('TimeOut').toString()
		self.waitThread = Settings.value('WaitThread').toString()
		try:
			int(timeOut)
		except ValueError, x:
			print x, '  processInit'
			#logging.debug(x)
			timeOut = '600'
		finally:
			pass
		try:
			int(self.waitThread)
		except ValueError, x:
			print x, '  processInit_1'
			#logging.debug(x)
			self.waitThread = '120'
		finally:
			pass

		self.initStat = True
		initPOP3Cache()

		self.Timer.start(int(timeOut) * 1000)
		logging.debug('Timer started.')
		print 'processInit'
		QApplication.postEvent(self, QEvent(1011))

	def createNotifyrc(self, kdehome):
		# Output the notifyrc file to the correct location
		print "Outputting notifyrc file"

		dir_ = kdehome+"share/apps/plasmaMailChecker"
		if not os.path.isdir(dir_):
			try:
				os.mkdir(dir_)
			except:
				print "Problem creating directory: " + dir_
				print "Unexpected error:", sys.exc_info()[0]

		# File to create
		fn = kdehome+"share/apps/plasmaMailChecker/plasmaMailChecker.notifyrc"

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
			print "Problem writing to file: " + fn
			print "Unexpected error:", sys.exc_info()[0]

	def eventNotification(self, str_ = ''):
		KNotification.event("new-notification-arrived",\
		str_,
		QPixmap(),
		None,
		KNotification.CloseOnTimeout,
		KComponentData('plasmaMailChecker','plasmaMailChecker',\
		KComponentData.SkipMainComponentRegistration))

	def _refreshData(self):
		#print '_refresh'
		if self.initStat :
			path_ = self.kdehome + \
					'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_web.png'

			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText(self.tr._translate("<font color=green><b>..running..</b></font>"))
				self.icon.setIcon(path_)
				if self.connectIconsFlag :
					self.connectIconsFlag = not ( self.disconnect(self.icon, SIGNAL('clicked()'), \
																				self._enterPassword) )
				self.icon.setToolTip(self.tr._translate("<font color=blue><b>Mail\nChecking</b></font>"))
			else :
				self.panelIcon.setIcon(path_)
				if self.connectIconsFlag :
					self.connectIconsFlag = not ( self.disconnect(self.panelIcon, SIGNAL('clicked()'), \
																				self._enterPassword) )
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.tr._translate("<font color=blue><b>Mail\nChecking</b></font>"), \
					self.panelIcon.icon() ) )
		else:
			path_ = self.kdehome + \
				'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText(self.tr._translate("<font color=red><b>..stopped..</b></font>"))
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"), \
					self.panelIcon.icon() ) )
			return None

		global g
		self.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if not (self.wallet is None) :
			if not g.isRunning() :
				# print 'start'
				accData = []
				for accountName in string.split(Settings.value('Accounts').toString(),';') :
					accData += [(accountName, self.wallet.readPassword(accountName)[1])]
				g = ThreadCheckMail(self, accData, self.waitThread)
				#_res = pdb.runcall(g.start)
				#logging.debug(_res)
				g.start()
			else :
				# print 'isRunning'
				pass
		else:
			self.emit(SIGNAL('refresh'))
			# print 'false start'

	def refreshData(self):
		#print 'refresh'
		GeneralLOCK.lock()
		global ErrorMsg
		global NewMailAttributes
		global RESULT
		global Settings

		if self.initStat :
			noCheck = False
			path_ = self.kdehome + \
					'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText(self.tr._translate("<font color=green><b>..running..</b></font>"))
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"))
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"), \
					self.panelIcon.icon() ) )
		else:
			noCheck = True
			path_ = self.kdehome + \
				'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText(self.tr._translate("<font color=red><b>..stopped..</b></font>"))
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"))
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"), \
					self.panelIcon.icon() ) )

		self.checkResult = RESULT
		#print self.checkResult
		i = 0
		newMailExist = False
		self.listNewMail = ''
		x = ''
		for accountName in string.split(Settings.value('Accounts').toString(),';') :
			try :
				if int(self.checkResult[i][2]) > 0 :
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						accountName_ = "<font color=red><b>" + accountName + "</b></font>"
						text_1 = "<font color=red><b>" + str(self.checkResult[i][1]) + "</b></font>"
						text_2 = "<font color=red><b>" + \
									'New : ' + str(self.checkResult[i][2]) + "</b></font>"
					self.listNewMail += '<pre>' + accountName + '&#09;' + str(self.checkResult[i][2]) + '</pre>'
					newMailExist = True
				else:
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						accountName_ = "<font color=lime><b>" + accountName + "</b></font>"
						text_1 = "<font color=lime><b>" + \
									str(self.checkResult[i][1]) + "</b></font>"
						text_2 = "<font color=lime><b>" + \
									'New : ' + str(self.checkResult[i][2]) + "</b></font>"

				if (self.formFactor() in [Plasma.Planar, Plasma.MediaCenter]) and self.initStat :
					self.label[i].setText(accountName_)
					self.countList[i].setText(text_1)
					self.countList[i].setToolTip(text_2)

			except IndexError, x :
				print x, '  refresh_1'
			except x :
				print x, '  refresh_2'
			except AttributeError, x:
				#print x, '  refresh_3'
				#logging.debug(x)
				pass
			except UnboundLocalError, x :
				print x, '  refresh_4'
				pass
			except x :
				print x, '  refresh_5'
				pass
			finally:
				pass
			i += 1

		if newMailExist and not noCheck :
			STR_ = ''
			i = 0
			while i < len(NewMailAttributes) :
				STR_ += '\n' + NewMailAttributes[i]
				i += 1
			# print 'newM@ilExist'
			# KNotification.beep()
			# KNotification.StandardEvent(KNotification.Notification)
			self.eventNotification('New Massage(s) :' + STR_)

		if not ( self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] ) :
			if self.listNewMail == '' :
				self.listNewMail = self.tr._translate("No new mail")
			Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
								self.panelIcon.toolTip(), \
								"<font color=lime><b>" + self.listNewMail + "</b></font>", \
								self.panelIcon.icon() ) )

		try :
			ErrorMsg += self.checkResult[i - 1][3]
		except IndexError, x :
			print x, '  refresh_5'
		except x :
			print x, '  refresh_6'
		finally :
			if ErrorMsg != '' :
				if Settings.value('ShowError').toString() != '0' and not noCheck :
					self.eventNotification( ErrorMsg )

		if not self.connectIconsFlag :
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
			else :
				self.connectIconsFlag = self.connect(self.panelIcon, SIGNAL('clicked()'), self._enterPassword)

		GeneralLOCK.unlock()

	def createIconWidget(self):
		self.panelIcon = Plasma.IconWidget()

		path_1 = self.kdehome + "share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png"
		path_ = os.path.expanduser(path_1)
		path_2 = '/usr/share/icons/mailChecker_stop.png'
		if os.path.exists(path_):
			self.panelIcon.setIcon(path_)
		else:
			self.panelIcon.setIcon(path_2)
		self.panelIcon.setToolTip(self.tr._translate("<font color=blue><b>M@il Checker</b></font>"))
		Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
			self.panelIcon.toolTip(), \
			self.tr._translate("<font color=blue><b>Click for Start\Stop</b></font>"), \
			self.panelIcon.icon() ) )
		self.panelIcon.resize(32,32)
		self.panelIcon.show()
		self.connectIconsFlag = self.connect(self.panelIcon, SIGNAL('clicked()'), self._enterPassword)
		self.layout.addItem(self.panelIcon)
		self.labelStat = Plasma.Label()

		self.setLayout(self.layout)

	def createConfigurationInterface(self, parent):
		self.editAccounts = EditAccounts(self)
		parent.addPage(self.editAccounts,self.tr._translate("Accounts"))
		self.appletSettings = AppletSettings(self)
		parent.addPage(self.appletSettings, self.tr._translate("Settings"))
		self.passwordManipulate = PasswordManipulate(self)
		parent.addPage(self.passwordManipulate, self.tr._translate("Password Manipulation"))
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
		self.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.wallet is None :
			self.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.appletSettings.refreshSettings(self)
		#print self.formFactor(), '---'
		global g
		x = ''
		try:
			self.Timer.stop()
			# останов потока проверки почты перед изменением GUI
			g.exit()
			while not g.wait() :
				time.sleep(0.5)
		except AttributeError, x:
			print x, '  acceptConf_1'
			#logging.debug(x)
			pass
		except x :
			print x, '  acceptConf_2'
		finally:
			pass
		savePOP3Cache()
		del self.dialog
		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.createDialogWidget()
		logging.debug('Settings refreshed. Timer stopped.')
		self.initStat = False
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.emit(SIGNAL('refresh'))

	def configDenied(self):
		del self.dialog
		pass

	def _enterPassword(self):
		if not self.initStat :
			self.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
			if not (self.wallet is None) :
				#print '_eP'
				self.enterPassword()
			else :
				#print '_eP_1'
				return None
		else :
			x = ''
			try:
				self.Timer.stop()
				g.quit()
				while not g.wait() :
					time.sleep(0.5)
			except AttributeError, x :
				print x, '  _entP_1'
				pass
			except x :
				print x, '  _entP_2'
			finally:
				pass
			savePOP3Cache()
			logging.debug('No enter password. Timer stopped.')
			self.initStat = False
			print 'stop_eP'
			self.emit(SIGNAL('refresh'))

	def enterPassword(self):
		self.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if not (self.wallet is None) :
			#print 'eP'
			self.wallet.setFolder('Passwords')
			self.emit(SIGNAL('access'))
		else :
			#print 'eP_1'
			self.initStat = False

	def eventClose(self):
		global g
		self.disconnect(self, SIGNAL('refresh'), self.refreshData)
		self.disconnect(self, SIGNAL('access'), self.processInit)
		x = ''
		try :
			self.Timer.stop()
			if not (self.wallet is None) :
				self.wallet.closeWallet('plasmaMailChecker', True)
		except AttributeError, x :
			print x, '  eventClose_1'
		except x :
			print x, '  eventClose_2'
			pass
		finally :
			pass
		g.terminate()
		while not g.wait() :
			time.sleep(0.5)
		GeneralLOCK.unlock()
		try :
			savePOP3Cache()
		except IOError, x :
			print x, '  eventClose_3'
		finally :
			pass
		logging.debug("MailChecker destroyed manually.")
		print "MailChecker destroyed manually."
		#sys.stderr.close()
		sys.stdout.close()

	def mouseDoubleClickEvent(self, ev):
		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.showConfigurationInterface()

class EditAccounts(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self, parent)

		self.Status = 'FREE'
		self.Parent = obj
		self.tr = Translator('EditAccounts')
		global Settings

		self.VBLayout = QVBoxLayout()

		self.layout = QGridLayout()

		self.accountListBox = KListWidget()
		i = 0
		self.accountList = []
		while i < Settings.childGroups().count() :
			#print str(Settings.childGroups().__getitem__(i)), '-'
			accountName = Settings.childGroups().__getitem__(i)
			self.accountListBox.addItem(accountName)
			self.accountList += [accountName]
			i += 1
		#print self.accountList
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
		self.editAccountItem.setToolTip(self.tr._translate("Edit current Account"))
		self.editAccountItem.clicked.connect(self.editCurrentAccount)
		self.layout.addWidget(self.editAccountItem,1,4)

		self.delAccountItem = QPushButton('&Del')
		self.delAccountItem.setToolTip(self.tr._translate("Delete current Account"))
		self.delAccountItem.clicked.connect(self.delCurrentAccount)
		self.layout.addWidget(self.delAccountItem,0,4)

		self.VBLayout.addLayout(self.layout)

		self.HB1Layout = QGridLayout()

		self.HB1Layout.addWidget(QLabel(self.tr._translate("Server : ")),0,0)

		self.HB1Layout.addWidget(QLabel(self.tr._translate("Port : ")),0,1)

		self.serverLineEdit = KLineEdit()
		self.serverLineEdit.setContextMenuEnabled(True)
		self.serverLineEdit.setToolTip(self.tr._translate("Example : imap.gmail.com, pop.mail.ru"))
		self.HB1Layout.addWidget(self.serverLineEdit,1,0)

		self.portBox = KIntSpinBox(0, 65000, 1, 0, self)
		self.HB1Layout.addWidget(self.portBox, 1, 1)

		self.VBLayout.addLayout(self.HB1Layout)

		self.HB2Layout = QGridLayout()

		self.HB2Layout.addWidget(QLabel(self.tr._translate("AuthMethod : ")),0,0)

		self.connectMethodBox = KComboBox()
		self.connectMethodBox.addItem('POP3',QVariant('pop'))
		self.connectMethodBox.addItem('IMAP4',QVariant('imap'))
		self.HB2Layout.addWidget(self.connectMethodBox,1,0)

		self.HB2Layout.addWidget(QLabel(self.tr._translate("Encrypt : ")),0,1)

		self.cryptBox = KComboBox()
		self.cryptBox.addItem('None',QVariant('None'))
		self.cryptBox.addItem('SSL',QVariant('SSL'))
		self.HB2Layout.addWidget(self.cryptBox,1,1)

		self.HB2Layout.addWidget(QLabel(self.tr._translate("Changes : ")),0,2)

		self.saveChanges = QPushButton('&Save')
		self.saveChanges.clicked.connect(self.saveChangedAccount)
		self.HB2Layout.addWidget(self.saveChanges,1,2)

		self.clearChanges = QPushButton('&Clear')
		self.clearChanges.clicked.connect(self.clearChangedAccount)
		self.HB2Layout.addWidget(self.clearChanges,1,3)

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

	def clearChangedAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'BUSY' :
			return None
		self.clearFields()
		self.Status = 'FREE'

	def saveChangedAccount(self):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'READY' :
			accountName, authData = self.parsingValues()
			if accountName == '' :
				self.clearChangedAccount()
				self.Parent.eventNotification(self.tr._translate("Warning :\nSet Account Name!"))
				return None
			self.Status = 'CLEAR'
			self.delCurrentAccount(self.oldAccountName)
			self.accountListBox.addItem(accountName)
			self.Parent.wallet.writePassword(accountName, authData[3])
			authData[3] = ''
			addAccount(accountName, authData)

			self.accountList += [accountName]
			i = 0
			str_ = ''
			while i < len(self.accountList) :
				str_ += str(self.accountList[i]) + ';'
				i += 1
			Settings.setValue('Accounts', str_)
			self.clearFields()
			self.Status = 'FREE'

	def clearFields(self):
		self.stringEditor.clear()
		self.userNameLineEdit.clear()
		self.passwordLineEdit.clear()
		self.serverLineEdit.clear()
		self.portBox.setValue(0)
		self.connectMethodBox.setCurrentIndex(0)
		self.cryptBox.setCurrentIndex(0)

	def editCurrentAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		self.Status = 'BUSY'
		accountName = self.accountListBox.currentItem().text()
		self.oldAccountName = accountName
		parameterList = readAccountData(str(accountName))
		self.stringEditor.setText(accountName)
		self.serverLineEdit.setText(str(parameterList[0]))
		i = 0
		count_ = int(self.connectMethodBox.count())
		while i < count_ :
			str_ = self.connectMethodBox.itemData(i).toString()
			#print str_, '-', str(parameterList[5]), '-', i
			if str_ == str(parameterList[5]) :
				self.connectMethodBox.setCurrentIndex(i)
			elif i == count_ - 1 :
				self.connectMethodBox.setCurrentIndex(0)
			i += 1
		i = 0
		count_ = int(self.cryptBox.count())
		while i < count_ :
			str_ = self.cryptBox.itemData(i).toString()
			#print str_, '-', str(parameterList[4]), '-', i
			if str_ == str(parameterList[4]) :
				self.cryptBox.setCurrentIndex(i)
			elif i == count_ - 1 :
				self.cryptBox.setCurrentIndex(0)
			i += 1
		#print parameterList[1]
		self.portBox.setValue(int(parameterList[1]))
		self.userNameLineEdit.setText(str(parameterList[2]))
		if self.Parent.wallet.hasEntry(self.oldAccountName) :
			self.passwordLineEdit.setText( '***EncriptedPassWord***' )
		else:
			self.passwordLineEdit.setText( '***EncriptedKey_not_created***' )
		self.Status = 'READY'
		pass

	def addNewAccount(self):
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			self.Parent.configDenied()
			return None
		if self.Status != 'FREE' :
			return None
		str_ = self.stringEditor.userText()
		if str(str_) != '' :
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
		userName = self.userNameLineEdit.userText()
		userPassword = self.passwordLineEdit.userText()
		# print accountName,accountServer,port_,connectMethod,cryptMethod, userName,userPassword, 'parsingVal'
		return accountName,\
				[ accountServer, port_, userName, userPassword, cryptMethod, connectMethod, '0' ]

	def delCurrentAccount(self, accountName = ''):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		if self.Status == 'FREE' :
			item_ = self.accountListBox.currentRow()
			#accountGroup = self.accountListBox.currentItem()
			if item_ == -1 :
				return None
			accountName = (self.accountListBox.takeItem(item_)).text()
			# print accountName.text(), str(accountName.text())
		elif self.Status != 'CLEAR' :
			return None
		else:
			i = 0
			while i < self.accountListBox.count() :
				if accountName == str(self.accountListBox.item(i).text()) :
					self.accountListBox.takeItem(i)
					break
				i += 1
			pass

		Settings.remove(accountName)
		self.Parent.wallet.removeEntry(accountName)
		try:
			self.accountList.remove(accountName)
		except ValueError, x :
			print x, '  delAcc'
			#logging.debug(x)
			pass
		finally:
			pass
		i = 0
		str_ = ''
		while i < len(self.accountList) :
			str_ += str(self.accountList[i]) + ';'
			i += 1
		Settings.setValue('Accounts', str_)

class AppletSettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.tr = Translator('AppletSettings')
		global Settings

		timeOut = Settings.value('TimeOut').toString()
		AutoRun = Settings.value('AutoRun').toString()
		countProbe = Settings.value('CountProbe').toString()
		showError = Settings.value('ShowError').toString()
		waitThread = Settings.value('WaitThread').toString()
		try:
			int(timeOut)
		except ValueError, x:
			#logging.debug(x)
			timeOut = '600'
		finally:
			pass
		try:
			int(AutoRun)
		except ValueError, x:
			print x, '  AppletSettings_1'
			#logging.debug(x)
			AutoRun = '0'
		finally:
			pass
		try:
			int(countProbe)
		except ValueError, x:
			print x, '  AppletSettings_2'
			#logging.debug(x)
			countProbe = 3
		finally:
			pass
		try:
			int(showError)
		except ValueError, x:
			print x, '  AppletSettings_3'
			#logging.debug(x)
			showError = 1
		finally:
			pass
		try:
			int(waitThread)
		except ValueError, x:
			print x, '  processInit_1'
			#logging.debug(x)
			waitThread = '120'
		finally:
			pass

		self.layout = QGridLayout()

		self.timeOutLabel = QLabel(self.tr._translate("Timeout checking (sec.):"))
		self.layout.addWidget(self.timeOutLabel,0,0)
		self.timeOutBox = KIntSpinBox(10, 7200, 1, int(timeOut), self)
		self.layout.addWidget(self.timeOutBox, 0, 1)

		self.autoRunLabel = QLabel(self.tr._translate("Autorun mail checking :"))
		self.layout.addWidget(self.autoRunLabel,1,0)
		self.AutoRunBox = QCheckBox()
		if int(AutoRun) > 0 :
			self.AutoRunBox.setCheckState(2)
		self.layout.addWidget(self.AutoRunBox,1,1)

		self.countProbe = QLabel(self.tr._translate("Count of connect probe\nto mail server:"))
		self.layout.addWidget(self.countProbe,2,0)
		self.countProbeBox = KIntSpinBox(1, 10, 1, int(countProbe), self)
		self.layout.addWidget(self.countProbeBox, 2, 1)

		self.showError = QLabel(self.tr._translate("Show error messages :"))
		self.layout.addWidget(self.showError,3,0)
		self.showErrorBox = QCheckBox()
		if int(showError) > 0 :
			self.showErrorBox.setCheckState(2)
		self.layout.addWidget(self.showErrorBox,3,1)

		self.waitThreadLabel = QLabel(self.tr._translate("Autoexit connect (sec.):"))
		self.layout.addWidget(self.waitThreadLabel,4,0)
		self.waitThreadBox = KIntSpinBox(10, 7200, 1, int(waitThread), self)
		self.layout.addWidget(self.waitThreadBox, 4, 1)

		self.setLayout(self.layout)

	def refreshSettings(self, parent = None):
		global Settings
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None
		Settings.setValue('TimeOut', str(self.timeOutBox.value()))
		Settings.setValue('CountProbe', str(self.countProbeBox.value()))
		Settings.setValue('WaitThread', str(self.waitThreadBox.value()))
		if self.AutoRunBox.isChecked() :
			Settings.setValue('AutoRun', '1')
		else:
			Settings.setValue('AutoRun', '0')
		if self.showErrorBox.isChecked() :
			Settings.setValue('ShowError', '1')
		else:
			Settings.setValue('ShowError', '0')

		Settings.sync()

class PasswordManipulate(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.tr = Translator('PasswordManipulate')

		self.VBLayout = QVBoxLayout()

		self.addAccountItem = QPushButton('&New')
		self.addAccountItem.setToolTip(self.tr._translate("Create new Password"))
		self.addAccountItem.clicked.connect(self.createNewKey)
		self.VBLayout.addWidget(self.addAccountItem)

		self.setLayout(self.VBLayout)

	def createNewKey(self):
		self.Parent.wallet.requestChangePassword(0)

try:
	def CreateApplet(parent):
		return plasmaMailChecker(parent)
	x = ''
	g = ThreadCheckMail()
	#gc.set_debug(gc.DEBUG_LEAK)
except x :
	print x, '  main method'
	#tb = sys.exc_info()[2]
	#pdb.post_mortem(tb)
finally :
	pass

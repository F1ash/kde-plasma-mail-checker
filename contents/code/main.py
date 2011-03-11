# -*- coding: utf-8 -*-

try :
	global warningMsg
	global Settings
	global RESULT
	global NewMailAttributes
	global ErrorMsg
	global LOG_FILENAME
	global WAIT
	LOG_FILENAME = 'mailChecker.log'
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from PyKDE4.kdecore import *
	from PyKDE4.kdeui import *
	from PyKDE4.plasma import Plasma
	from PyKDE4 import plasmascript
	import poplib, imaplib, string, socket, time, os.path, logging, random, sys, email.header, gc, locale
	#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', \
	#										datefmt='%Y-%m-%d %H:%M:%S', filename=LOG_FILENAME)
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

def dataToSTR(path_ = ''):
	if os.path.isfile(path_) :
		f = open(path_, 'rb')
		l = f.read()
		f.close()
		os.remove(path_)
		return l
	else :
		return 0

def readDataFiles(fileName):
	path_ = '/dev/shm/' + fileName
	return bool(dataToSTR(path_ + '.Result')), int(dataToSTR(path_ + '.all')), \
						int(dataToSTR(path_ + '.new')), str(dataToSTR(path_ + '.msg')), \
						dataToSTR(path_ + '.content')

def randomString(j = 1):
	return "".join( [random.choice(string.letters) for i in xrange(j)] )

def to_unicode(_str):
	str_ = '<=junk_string=>'
	try:
		#print _str, '---'
		str_ = unicode(_str, 'UTF-8')
	except TypeError:
		str_ = _str
	#except UnicodeEncodeError:
	#	str_ = str(_str)
	finally:
		return str_

def addAccount(account, data_ = ['']):
	LOCK.lockForWrite()
	global Settings
	accounts_ = Settings.value('Accounts').toString()
	Settings.setValue('Accounts', accounts_ + ';' + account)
	Settings.beginGroup(account)
	Settings.setValue('server', str(data_[0]))
	Settings.setValue('port', str(data_[1]))
	Settings.setValue('login', data_[2])
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
	if port_ == '' : port_ =  '0'
	login_ = Settings.value('login').toString()
	authMethod_ = Settings.value('authentificationMethod').toString()
	connMethod_ = Settings.value('connectMethod').toString()
	last_ = Settings.value('lastElemValue').toString()
	Settings.endGroup()
	LOCK.unlock()
	return [str(serv_), str(port_), login_, '', str(authMethod_), str(connMethod_), str(last_)]

def initPOP3Cache():
	LOCK.lockForWrite()
	global Settings
	dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
	if  not os.path.isdir(dir_) :
		os.mkdir(dir_)
	for accountName in string.split( Settings.value('Accounts').toString(), ';' ):
		Settings.beginGroup(accountName)
		if Settings.value('connectMethod').toString() == 'pop' :
			if not os.path.isfile(dir_ + '/' + accountName + '.cache') :
				f = open(dir_ + '/' + accountName + '.cache', 'w')
				f.close()
			f = open(dir_ +  '/' + accountName + '.cache', 'r')
			c = open('/dev/shm/' + accountName + '.cache', 'w')
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
		Settings.beginGroup(accountName)
		if Settings.value('connectMethod').toString() == 'pop' :
			f = open(dir_ + '/' + accountName + '.cache', 'w')
			if os.path.isfile('/dev/shm/' + accountName + '.cache') :
				c = open('/dev/shm/' + accountName + '.cache', 'r')
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
		f = open('/dev/shm/' + accountName + '.cache', 'r')
		STR = f.readlines()
		f.close()
		# print STR
	except x :
		print x, '  defUidl'
	finally :
		for uid_ in STR :
			# print string.split(uid_, '\n')[0] , '--- ', str_
			if str_ == string.split(uid_, '\n')[0] :
				Result = False
				break
	return Result

def checkNewMailPOP3(accountData = ['', '']):
	global ErrorMsg
	#global WAIT
	WAIT = True
	x = ''
	try:
		#global NewMailAttributes
		NewMailAttributes = ''
		newMailExist = False
		probeError = True
		countNew = 0
		mailUidls = []
		countAll = 0
		authentificationData = readAccountData(accountData[0])
		lastElemUid = authentificationData[6]

		if WAIT :
			if authentificationData[4] == 'SSL' :
				#print to_unicode(accountData[0]), '  connect server', WAIT
				m = poplib.POP3_SSL(authentificationData[0], authentificationData[1])
			else:
				#print to_unicode(accountData[0]), '  connect server', WAIT
				m = poplib.POP3(authentificationData[0], authentificationData[1])
		else :
			#print to_unicode(accountData[0]), '  thread don`t WAIT', WAIT
			return probeError, countAll, countNew

		#auth_login = m.user(authentificationData[2])
		if WAIT and m.user(authentificationData[2])[:3] == '+OK' :
			#print to_unicode(accountData[0]), '  login to server', WAIT
			#auth_passw = m.pass_( accountData[1] )
			if WAIT and m.pass_( accountData[1] )[:3] == '+OK' :
				#print to_unicode(accountData[0]), '  passw_ to server', WAIT

				countAll = int(m.stat()[0])
				#print to_unicode(accountData[0]), '  reqwest UIDLs from server', WAIT
				for uidl_ in m.uidl()[1] :
					currentElemUid = string.split(uidl_,' ')[1]
					mailUidls += [currentElemUid + '\n']
					if WAIT and defineUIDL(accountData[0], currentElemUid) :
						From = ''
						Subj = ''
						#print to_unicode(accountData[0]), '  reqwest TOP from server', WAIT
						for str_ in m.top( int(string.split(uidl_,' ')[0]) , 0)[1] :
							if str_[:5] == 'From:' :
								_str = string.replace(str_, '"', '')  ## for using email.header.decode_header
								for part_str in email.header.decode_header(_str) :
									if part_str[1] is None :
										From += part_str[0] + ' '
									else :
										From += part_str[0].decode(part_str[1]) + ' '
								#print From
							if str_[:5] == 'Subje' :
								_str = string.replace(str_, '"', '')
								for part_str in email.header.decode_header(_str) :
									if part_str[1] is None :
										Subj += part_str[0] + ' '
									else :
										Subj += part_str[0].decode(part_str[1]) + ' '
								#print Subj
						# print Result, WAIT
						NewMailAttributes += to_unicode(From) + '\n' + to_unicode(Subj) + '\n'
						#print NewMailAttributes, '   ------'
						newMailExist = newMailExist or True
						countNew += 1
					elif not WAIT :
						m.quit()
						#print to_unicode(accountData[0]), '  close connect', WAIT
						return probeError, countAll, countNew

				c = open('/dev/shm/' + accountData[0] + '.cache', 'w')
				# print mailUidls, WAIT
				c.writelines( mailUidls )
				c.close()

			elif not WAIT :
				m.quit()
				#print to_unicode(accountData[0]), '  close connect', WAIT
				return probeError, countAll, countNew

		m.quit()
		#print to_unicode(accountData[0]), '  close connect', WAIT

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
	except UnicodeDecodeError, x :
		print x, '  POP3_4'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except x:
		print x, '  POP3_5'
		ErrorMsg += 'Unknown Error\n'
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew, NewMailAttributes

def checkNewMailIMAP4(accountData = ['', '']):
	global ErrorMsg
	global Settings
	#global WAIT
	WAIT = True
	x = ''
	try:
		#global NewMailAttributes
		NewMailAttributes = ''
		newMailExist = False
		probeError = True
		countNew = 0
		countAll = 0
		authentificationData = readAccountData(accountData[0])
		lastElemTime = authentificationData[6]

		if WAIT :
			if authentificationData[4] == 'SSL' :
				#print to_unicode(accountData[0]), '  connect server', WAIT
				m = imaplib.IMAP4_SSL(authentificationData[0], authentificationData[1])
			else:
				#print to_unicode(accountData[0]), '  connect server', WAIT
				m = imaplib.IMAP4(authentificationData[0], authentificationData[1])
		else :
			#print to_unicode(accountData[0]), '  thread don`t WAIT', WAIT
			return probeError, countAll, countNew

		if WAIT and m.login( authentificationData[2], accountData[1] )[0] == 'OK' :
			#print to_unicode(accountData[0]), '  login to server', WAIT
			answer = m.select()
			if WAIT and answer[0] == 'OK':
				#print to_unicode(accountData[0]), '  passw_ to server', WAIT
				countAll = int(answer[1][0])
				i = countAll
				while i > 0 and WAIT :
					currentElemTime_raw = string.split(m.fetch(i,"INTERNALDATE")[1][0],' ')
					#print to_unicode(accountData[0]), '  fetch DATA from server', WAIT
					currentElemTime_Internal = currentElemTime_raw[1] + ' ' \
												+ currentElemTime_raw[2] + ' ' \
												+ currentElemTime_raw[3] + ' ' \
												+ currentElemTime_raw[4]
					# print currentElemTime_Internal
					date_ = imaplib.Internaldate2tuple(currentElemTime_Internal)
					currentElemTime = str(time.mktime(date_))
					# print currentElemTime
					if currentElemTime > lastElemTime :
						From = ''
						Subj = ''
						#print to_unicode(accountData[0]), '  reqwest TOP from server', WAIT
						for str_ in string.split(m.fetch(i,"(BODY[HEADER])")[1][0][1],'\r\n') :
							if str_[:5] == 'From:' :
								_str = string.replace(str_, '"', '')  ## for using email.header.decode_header
								for part_str in email.header.decode_header(_str) :
									if part_str[1] is None :
										From += part_str[0] + ' '
									else :
										From += part_str[0].decode(part_str[1]) + ' '
								#print From
							if str_[:5] == 'Subje' :
								_str = string.replace(str_, '"', '')
								for part_str in email.header.decode_header(_str) :
									if part_str[1] is None :
										Subj += part_str[0] + ' '
									else :
										Subj += part_str[0].decode(part_str[1]) + ' '
								#print Subj
						#  print Result, WAIT
						NewMailAttributes += to_unicode(From) + '\n' + to_unicode(Subj) + '\n'
						#print NewMailAttributes, '   ----==------'
						newMailExist = newMailExist or True
						countNew += 1
					else:
						break
					i += -1
			else:
				#print 'selectDirError', WAIT
				logging.debug('selectDirError')
				probeError, countAll, countNew = False, 0, 0
		else:
			#print 'AuthError', WAIT
			logging.debug('AuthError')
			probeError, countAll, countNew = False, 0, 0
			pass

		if newMailExist :
			#print to_unicode(accountData[0]), '  reqwest fetchDATA from server', WAIT
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
		#print to_unicode(accountData[0]), '  close', WAIT

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
	except UnicodeDecodeError, x :
		print x, '  IMAP4_4'
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

	return probeError, countAll, countNew, NewMailAttributes

def connectProbe(probe_ = 3, checkNewMail = None, authData = ['', '']):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	i = 0
	while i < probe_ :
		#GeneralLOCK.lock()
		#print 'Probe ', i + 1, to_unicode(authData[0])
		test_, all_, new_, content = checkNewMail(authData)
		#GeneralLOCK.unlock()
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + to_unicode(authData[0]) +'\n'
	return Result, all_, new_, '', QString(content).toUtf8()

def checkMail(accountData = ['', '']):
	#global NewMailAttributes
	global Settings
	Msg = ''
	if accountData[0] != '' :
		#print accountData[0]
		countProbe_raw = Settings.value('CountProbe')
		#print countProbe_raw.toString()
		account = QString().fromUtf8(accountData[0])
		Settings.beginGroup(account)
		connectMethod = Settings.value('connectMethod').toString()
		Settings.endGroup()
		try:
			countProbe = int(countProbe_raw.toString())
		except ValueError:
			print x, '  checkMail'
			countProbe = 3
		finally:
			pass
		#print str(connectMethod),'---'
		#print countProbe
		if str(connectMethod) == 'pop' :
			return  connectProbe(countProbe, checkNewMailPOP3, [account, accountData[1]])
		elif str(connectMethod) == 'imap' :
			return connectProbe(countProbe, checkNewMailIMAP4, [account, accountData[1]])
		else:
			Msg = 'connectMethod Error\n'
	else:
		Msg = 'accountName Error\n'
	return False, 0, 0, Msg, ''

class Translator(QTranslator):
	def __init__(self, context = '', parent=None):
		QTranslator.__init__(self, parent)

		lang = locale.getdefaultlocale()[0][:2]
		#print lang
		_Path = self.user_or_sys(lang + '.qm')
		self.load(QString(lang), QString(_Path), QString('qm'))
		self.context = context

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/plasmaMailChecker/contents/code/'
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/plasmaMailChecker/contents/code/'
		if os.path.exists(var1 + path_) :
			return var1
		elif os.path.exists(var2 + path_) :
			return var2
		else :
			return kdehome

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
		self.Timer.timeout.connect(self.signalToKillSelf)
		self.timeout = int(timeout) * 1000
		self.accData = accountData
		global WAIT
		WAIT = True

	def __del__(self):
		self.timeout = None
		self.Timer = None
		self.accData = None
		self.Parent = None

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		if os.path.exists(var1) :
			return var1
		elif os.path.exists(var2) :
			return var2
		else :
			return kdehome

	def run(self):
		try:

			global ErrorMsg
			global RESULT
			NewMailAttributes = []
			newMailExist = False
			ErrorMsg = ''
			x = ''
			RESULT = []
			self.dataList = []
			self.Timer.start(self.timeout)
			path = self.user_or_sys('code/mail.py')
			for accountData in self.accData :
				#RESULT += [checkMail(accountData)]
				if WAIT :
					str_ = str(randomString(24))
				#Data = QStringList()
				#Data.append(path); Data.append(accountData[0])
				#Data.append(accountData[1]); Data.append(str_)
					accountThread = KProcess()
					accountThread.setShellCommand('/usr/bin/python '+ path + ' \'' + accountData[0] + \
												'\' \'' + accountData[1] + '\' \'' + str_ + '\'')
				#thread = accountThread.execute(QString('/usr/bin/python '+ path), Data, self.timeout)
				#accountThread.setProgram(QString('/usr/bin/python '), Data)
				#accountThread.setShellCommand('echo 1')
				#print accountThread.pid(), str_
					accountThread.execute(self.timeout)
				#accountThread.start()
					self.dataList += [(accountThread.pid(), str_)]

			#for i in xrange(len(self.accData)) :
			#	try :
			#		os.wait(dataList[i][0], 0)
			#	except OSError:
			#		pass
			for i in xrange(len(self.dataList)) :
				RESULT += [readDataFiles(self.dataList[i][1])]

		except x :

			self.Timer.stop()
			print x, '  thread'
			#tb = sys.exc_info()[2]
			#pdb.post_mortem(tb)
			logging.debug(x)
		finally :
			self.Timer.stop()
			#print RESULT
			self.Parent.emit(SIGNAL('refresh'))
			#self.Parent.emit(SIGNAL('killThread'))
			print ' send "killThread" to mainThread'
			QApplication.postEvent(self.Parent, QEvent(1010))
			pass
		return

	def signalToKillSelf(self):
		global WAIT
		global ErrorMsg
		LOCK.lockForRead()
		WAIT = False
		LOCK.unlock()
		print WAIT, '  changed WAIT'
		ErrorMsg += 'Timeout thread error'
		print 'Mail thread timeout terminating...'
		self.Timer.stop()

	def _terminate(self):
		global WAIT
		LOCK.lockForRead()
		WAIT = False
		LOCK.unlock()
		print 'recive signal to kill...'
		self.Parent.emit(SIGNAL('refresh'))
		self.__del__()
		self.exit()

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
		self.initPrefixAndSuffix()

	def init(self):
		global Settings
		self.setHasConfigurationInterface(True)
		self.T = ThreadCheckMail(obj = self)
		self.loop = QEventLoop()

		self.Timer = QTimer()
		self.Timer.timeout.connect(self._refreshData)

		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.layout.setSpacing(0)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())

		if not os.path.exists(self.kdehome+"share/apps/plasmaMailChecker/plasmaMailChecker.notifyrc"):
			if os.path.exists(self.kdehome+"share/apps"):
				self.createNotifyrc(self.kdehome)
		self.stopIconPath = self.user_or_sys('icons/mailChecker_stop.png')
		self.webIconPath = self.user_or_sys('icons/mailChecker_web.png')
		self.usualIconPath = self.user_or_sys('icons/mailChecker.png')

		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.titleLayout = QGraphicsLinearLayout()
			self.titleLayout.setOrientation(Qt.Horizontal)

			self.TitleDialog = Plasma.Label()
			self.TitleDialog.setStyleSheet(self.headerColourStyle)
			self.TitleDialog.setText(self.headerPref + self.tr._translate('M@il Checker') + self.headerSuff)
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
		self.connect(self, SIGNAL('finished()'), self.loop , SLOT(self.T._terminate()))

		AutoRun = self.initValue('AutoRun')
		if AutoRun != '0' :
			#QApplication.postEvent(self, QEvent(QEvent.User))
			self.Timer1 = QTimer()
			self.Timer1.setSingleShot(True)
			self.Timer1.timeout.connect(self.enterPassword)
			self.Timer1.start(2000)

	def initColourAndFont(self):
		self.headerFontVar = self.initValue('headerFont')
		self.headerSizeVar = self.initValue('headerSize')
		self.headerBoldVar = self.initValue('headerBold')
		self.headerItalVar = self.initValue('headerItal')
		self.headerColourVar = self.initValue('headerColour')

		self.accountFontVar = self.initValue('accountFont')
		self.accountSizeVar = self.initValue('accountSize')
		self.accountBoldVar = self.initValue('accountBold')
		self.accountItalVar = self.initValue('accountItal')
		self.accountColourVar = self.initValue('accountColour')
		self.accountSFontVar = self.initValue('accountSFont')
		self.accountSSizeVar = self.initValue('accountSSize')
		self.accountSBoldVar = self.initValue('accountSBold')
		self.accountSItalVar = self.initValue('accountSItal')
		self.accountSColourVar = self.initValue('accountSColour')

		self.accountToolTipFontVar = self.initValue('accountToolTipFont')
		self.accountToolTipSizeVar = self.initValue('accountToolTipSize')
		self.accountToolTipBoldVar = self.initValue('accountToolTipBold')
		self.accountToolTipItalVar = self.initValue('accountToolTipItal')
		self.accountToolTipColourVar = self.initValue('accountToolTipColour')
		self.accountToolTipSFontVar = self.initValue('accountToolTipSFont')
		self.accountToolTipSSizeVar = self.initValue('accountToolTipSSize')
		self.accountToolTipSBoldVar = self.initValue('accountToolTipSBold')
		self.accountToolTipSItalVar = self.initValue('accountToolTipSItal')
		self.accountToolTipSColourVar = self.initValue('accountToolTipSColour')

		self.countFontVar = self.initValue('countFont')
		self.countSizeVar = self.initValue('countSize')
		self.countBoldVar = self.initValue('countBold')
		self.countItalVar = self.initValue('countItal')
		self.countColourVar = self.initValue('countColour')
		self.countSFontVar = self.initValue('countSFont')
		self.countSSizeVar = self.initValue('countSSize')
		self.countSBoldVar = self.initValue('countSBold')
		self.countSItalVar = self.initValue('countSItal')
		self.countSColourVar = self.initValue('countSColour')

		self.countToolTipFontVar = self.initValue('countToolTipFont')
		self.countToolTipSizeVar = self.initValue('countToolTipSize')
		self.countToolTipBoldVar = self.initValue('countToolTipBold')
		self.countToolTipItalVar = self.initValue('countToolTipItal')
		self.countToolTipColourVar = self.initValue('countToolTipColour')
		self.countToolTipSFontVar = self.initValue('countToolTipSFont')
		self.countToolTipSSizeVar = self.initValue('countToolTipSSize')
		self.countToolTipSBoldVar = self.initValue('countToolTipSBold')
		self.countToolTipSItalVar = self.initValue('countToolTipSItal')
		self.countToolTipSColourVar = self.initValue('countToolTipSColour')

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
			style = 'QLabel { color: rgba(0, 0, 0, 125);} '
		return style

	def initValue(self, key_, default = '0'):
		global Settings
		if Settings.contains(key_) :
			#print key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			Settings.setValue(key_, QVariant(default))
			#print key_, Settings.value(key_).toString()
			return default

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

	def customEvent(self, event):
		if event.type() == QEvent.User :
			self.enterPassword()
		elif event.type() == 1011 :
			self._refreshData()
		elif event.type() == 1010 :
			self.emit(SIGNAL('killThread'))
		pass

	def user_or_sys(self, path_):
		var1 = self.kdehome + 'share/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		if os.path.exists(var1) :
			return var1
		elif os.path.exists(var2) :
			return var2
		else :
			return self.kdehome

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
		timeOut = self.initValue('TimeOut', '600')
		self.waitThread = self.initValue('WaitThread', '120')

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
		QPixmap(self.usualIconPath),
		None,
		KNotification.CloseOnTimeout,
		KComponentData('plasmaMailChecker','plasmaMailChecker',\
		KComponentData.SkipMainComponentRegistration))

	def _refreshData(self):
		#print '_refresh'
		if self.initStat :
			path_ = self.webIconPath

			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=green><b>" + self.tr._translate('..running..') + "</b></font>")
				self.icon.setIcon(path_)
				if self.connectIconsFlag :
					self.connectIconsFlag = not ( self.disconnect(self.icon, SIGNAL('clicked()'), \
																				self._enterPassword) )
				self.icon.setToolTip(self.headerPref + self.tr._translate('Mail\nChecking') +  self.headerSuff)
			else :
				self.panelIcon.setIcon(path_)
				if self.connectIconsFlag :
					self.connectIconsFlag = not ( self.disconnect(self.panelIcon, SIGNAL('clicked()'), \
																				self._enterPassword) )
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Mail\nChecking') +  self.headerSuff, \
					self.panelIcon.icon() ) )
		else:
			path_ = self.stopIconPath
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Click for Start\Stop') +  self.headerSuff, \
					self.panelIcon.icon() ) )
			return None

		self.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if not (self.wallet is None) :
			if not self.T.isRunning() :
				# print 'start'
				self.T.__del__()
				accData = []
				for accountName in string.split(Settings.value('Accounts').toString(),';') :
					accData += [(accountName, self.wallet.readPassword(accountName)[1])]
				self.T = ThreadCheckMail(self, accData, self.waitThread, self)
				print 'time for wait thread : ', self.waitThread
				self.T.start()
			else :
				print 'isRunning : send signal to kill...'
				self.emit(SIGNAL('killThread'))
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
			path_ = self.usualIconPath
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
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
		else:
			noCheck = True
			path_ = self.stopIconPath
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
				self.icon.setIcon(path_)
				self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + \
																					self.headerSuff)
			else :
				self.panelIcon.setIcon(path_)
				Plasma.ToolTipManager.self().setContent( self.panelIcon, Plasma.ToolTipContent( \
					self.panelIcon.toolTip(), \
					self.headerPref + self.tr._translate('Click for Start\Stop') +  self.headerSuff, \
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
					self.label[i].setStyleSheet(self.accountSColourStyle)
					self.countList[i].setStyleSheet(self.countSColourStyle)
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						accountName_ = self.accSPref + accountName + self.accSSuff
						accountTT = self.accTTSPref + self.tr._translate('Account') + \
													self.accTTSSuff + ' ' + accountName
						text_1 = self.countSPref + str(self.checkResult[i][1]) + self.countSSuff
						text_2 = self.countTTSPref + self.tr._translate('New : ') + \
													str(self.checkResult[i][2]) + self.countTTSSuff
					self.listNewMail += '<pre>' + accountName + '&#09;' + str(self.checkResult[i][2]) + '</pre>'
					newMailExist = True
				else:
					self.label[i].setStyleSheet(self.accountColourStyle)
					self.countList[i].setStyleSheet(self.countColourStyle)
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						accountName_ = self.accPref + accountName + self.accSuff
						accountTT = self.accTTPref + self.tr._translate('Account') + \
													self.accTTSuff + ' ' + accountName
						text_1 = self.countPref + str(self.checkResult[i][1]) + self.countSuff
						text_2 = self.countTTPref + self.tr._translate('New : ') + \
													str(self.checkResult[i][2]) + self.countTTSuff

				if (self.formFactor() in [Plasma.Planar, Plasma.MediaCenter]) and self.initStat :
					self.label[i].setText(accountName_)
					self.label[i].setToolTip(accountTT)
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
			while i < len(self.checkResult) :
				str_ = self.checkResult[i][4]
				if str_ not in ['', ' '] :
					#print str_
					STR_ += '\n' + to_unicode(str_)
				i += 1
			# print 'newM@ilExist'
			# KNotification.beep()
			# KNotification.StandardEvent(KNotification.Notification)
			self.eventNotification(self.tr._translate('New Massage(s) :') + STR_)

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
			if ErrorMsg not in ['', ' ', '0'] :
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
		parent.addPage(self.editAccounts,self.tr._translate("Accounts"))
		self.appletSettings = AppletSettings(self, parent)
		parent.addPage(self.appletSettings, self.tr._translate("Settings"))
		self.passwordManipulate = PasswordManipulate(self, parent)
		parent.addPage(self.passwordManipulate, self.tr._translate("Password Manipulation"))
		self.fontsNcolour = Font_n_Colour(self, parent)
		parent.addPage(self.fontsNcolour, self.tr._translate("Font and Colour"))
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
		self.fontsNcolour.refreshSettings(self)
		#print self.formFactor(), '---'
		x = ''
		try:
			self.Timer.stop()
			# останов потока проверки почты перед изменением GUI
			self.emit(SIGNAL('killThread'))
		except AttributeError, x:
			print x, '  acceptConf_1'
			#logging.debug(x)
			pass
		except x :
			print x, '  acceptConf_2'
		finally:
			pass
		savePOP3Cache()
		# refresh color & font Variables
		self.initPrefixAndSuffix()
		del self.dialog
		# refresh plasmoid Header
		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.TitleDialog.setText(self.headerPref + self.tr._translate('M@il Checker') + self.headerSuff)
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
				if self.T.isRunning() :
					self.emit(SIGNAL('killThread'))
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
		self.killMailCheckerThread()
		GeneralLOCK.unlock()
		try :
			savePOP3Cache()
		except IOError, x :
			print x, '  eventClose_3'
		finally :
			pass
		logging.debug("MailChecker destroyed manually.")
		print "MailChecker destroyed manually."
		sys.stderr.close()
		sys.stdout.close()

	def killMailCheckerThread(self):
		self.loop.exit()

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
				str_ += self.accountList[i] + ';'
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
		parameterList = readAccountData(accountName)
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
		self.userNameLineEdit.setText(parameterList[2])
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
		userName = self.userNameLineEdit.userText()
		userPassword = self.passwordLineEdit.userText()
		# print (accountName,accountServer,port_,connectMethod,cryptMethod, userName,userPassword, 'parsingVal')
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
				if accountName == self.accountListBox.item(i).text() :
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
			str_ += self.accountList[i] + ';'
			i += 1
		Settings.setValue('Accounts', str_)

	def eventClose(self, event):
		self.Parent.done(0)

class AppletSettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.tr = Translator('AppletSettings')
		global Settings

		timeOut = self.initValue('TimeOut', '600')
		AutoRun = self.initValue('AutoRun', '0')
		countProbe = self.initValue('CountProbe', '3')
		showError = self.initValue('ShowError', '1')
		waitThread = self.initValue('WaitThread', '120')

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
		self.waitThreadBox = KIntSpinBox(3, 7200, 1, int(waitThread), self)
		self.layout.addWidget(self.waitThreadBox, 4, 1)

		self.setLayout(self.layout)

	def initValue(self, key_, default = '0'):
		global Settings
		if Settings.contains(key_) :
			#print key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			Settings.setValue(key_, QVariant(default))
			#print key_, Settings.value(key_).toString()
			return default

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

	def eventClose(self, event):
		self.Parent.done(0)

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

	def eventClose(self, event):
		self.Parent.done(0)

class Font_n_Colour(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.tr = Translator('Font_n_Colour')
		global Settings

		self.headerFontVar = self.initValue('headerFont')
		self.headerSizeVar = self.initValue('headerSize')
		self.headerBoldVar = self.initValue('headerBold')
		self.headerItalVar = self.initValue('headerItal')
		self.headerColourVar = self.initValue('headerColour')

		self.accountFontVar = self.initValue('accountFont')
		self.accountSizeVar = self.initValue('accountSize')
		self.accountBoldVar = self.initValue('accountBold')
		self.accountItalVar = self.initValue('accountItal')
		self.accountColourVar = self.initValue('accountColour')
		self.accountSFontVar = self.initValue('accountSFont')
		self.accountSSizeVar = self.initValue('accountSSize')
		self.accountSBoldVar = self.initValue('accountSBold')
		self.accountSItalVar = self.initValue('accountSItal')
		self.accountSColourVar = self.initValue('accountSColour')

		self.accountToolTipFontVar = self.initValue('accountToolTipFont')
		self.accountToolTipSizeVar = self.initValue('accountToolTipSize')
		self.accountToolTipBoldVar = self.initValue('accountToolTipBold')
		self.accountToolTipItalVar = self.initValue('accountToolTipItal')
		self.accountToolTipColourVar = self.initValue('accountToolTipColour')
		self.accountToolTipSFontVar = self.initValue('accountToolTipSFont')
		self.accountToolTipSSizeVar = self.initValue('accountToolTipSSize')
		self.accountToolTipSBoldVar = self.initValue('accountToolTipSBold')
		self.accountToolTipSItalVar = self.initValue('accountToolTipSItal')
		self.accountToolTipSColourVar = self.initValue('accountToolTipSColour')

		self.countFontVar = self.initValue('countFont')
		self.countSizeVar = self.initValue('countSize')
		self.countBoldVar = self.initValue('countBold')
		self.countItalVar = self.initValue('countItal')
		self.countColourVar = self.initValue('countColour')
		self.countSFontVar = self.initValue('countSFont')
		self.countSSizeVar = self.initValue('countSSize')
		self.countSBoldVar = self.initValue('countSBold')
		self.countSItalVar = self.initValue('countSItal')
		self.countSColourVar = self.initValue('countSColour')

		self.countToolTipFontVar = self.initValue('countToolTipFont')
		self.countToolTipSizeVar = self.initValue('countToolTipSize')
		self.countToolTipBoldVar = self.initValue('countToolTipBold')
		self.countToolTipItalVar = self.initValue('countToolTipItal')
		self.countToolTipColourVar = self.initValue('countToolTipColour')
		self.countToolTipSFontVar = self.initValue('countToolTipSFont')
		self.countToolTipSSizeVar = self.initValue('countToolTipSSize')
		self.countToolTipSBoldVar = self.initValue('countToolTipSBold')
		self.countToolTipSItalVar = self.initValue('countToolTipSItal')
		self.countToolTipSColourVar = self.initValue('countToolTipSColour')

		self.headerColourStyle = self.getRGBaStyle(QString(self.headerColourVar).toUInt())
		self.accountColourStyle = self.getRGBaStyle(QString(self.accountColourVar).toUInt())
		self.accountSColourStyle = self.getRGBaStyle(QString(self.accountSColourVar).toUInt())
		self.accountToolTipColourStyle = self.getRGBaStyle(QString(self.accountToolTipColourVar).toUInt())
		self.accountToolTipSColourStyle = self.getRGBaStyle(QString(self.accountToolTipSColourVar).toUInt())
		self.countColourStyle = self.getRGBaStyle(QString(self.countColourVar).toUInt())
		self.countSColourStyle = self.getRGBaStyle(QString(self.countSColourVar).toUInt())
		self.countToolTipColourStyle = self.getRGBaStyle(QString(self.countToolTipColourVar).toUInt())
		self.countToolTipSColourStyle = self.getRGBaStyle(QString(self.countToolTipSColourVar).toUInt())

		self.fontIconPath = self.user_or_sys('icons/font.png')
		self.colourIconPath = self.user_or_sys('icons/color.png')
		self.fontIcon = QIcon(self.fontIconPath)
		self.colourIcon = QIcon(self.colourIconPath)

		self.init()

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/plasmaMailChecker/contents/' + path_
		if os.path.exists(var1) :
			return var1
		elif os.path.exists(var2) :
			return var2
		else :
			return kdehome

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

		self.accountFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.accountFontButton.setToolTip('Font')
		self.connect(self.accountFontButton, SIGNAL('clicked()'), self.accountFont)
		self.layout.addWidget(self.accountFontButton, 2, 1)

		self.accountColourButton = QPushButton(QIcon(self.colourIconPath), '')
		self.accountColourButton.setToolTip('Color')
		self.connect(self.accountColourButton, SIGNAL('clicked()'), self.accountColour)
		self.layout.addWidget(self.accountColourButton, 2, 2)

		self.accountSFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.accountSFontButton.setToolTip('Font')
		self.connect(self.accountSFontButton, SIGNAL('clicked()'), self.accountSFont)
		self.layout.addWidget(self.accountSFontButton, 2, 3)

		self.accountSColourButton = QPushButton(QIcon(self.colourIconPath), '')
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

		self.accountToolTipFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.accountToolTipFontButton.setToolTip('Font')
		self.connect(self.accountToolTipFontButton, SIGNAL('clicked()'), self.accountToolTipFont)
		self.layout.addWidget(self.accountToolTipFontButton, 3, 1)

		self.accountToolTipColourButton = QPushButton(QIcon(self.colourIconPath), '')
		self.accountToolTipColourButton.setToolTip('Color')
		self.connect(self.accountToolTipColourButton, SIGNAL('clicked()'), self.accountToolTipColour)
		self.layout.addWidget(self.accountToolTipColourButton, 3, 2)

		self.accountToolTipSFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.accountToolTipSFontButton.setToolTip('Font')
		self.connect(self.accountToolTipSFontButton, SIGNAL('clicked()'), self.accountToolTipSFont)
		self.layout.addWidget(self.accountToolTipSFontButton, 3, 3)

		self.accountToolTipSColourButton = QPushButton(QIcon(self.colourIconPath), '')
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

		self.countFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.countFontButton.setToolTip('Font')
		self.connect(self.countFontButton, SIGNAL('clicked()'), self.countFont)
		self.layout.addWidget(self.countFontButton, 4, 1)

		self.countColourButton = QPushButton(QIcon(self.colourIconPath), '')
		self.countColourButton.setToolTip('Color')
		self.connect(self.countColourButton, SIGNAL('clicked()'), self.countColour)
		self.layout.addWidget(self.countColourButton, 4, 2)

		self.countSFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.countSFontButton.setToolTip('Font')
		self.connect(self.countSFontButton, SIGNAL('clicked()'), self.countSFont)
		self.layout.addWidget(self.countSFontButton, 4, 3)

		self.countSColourButton = QPushButton(QIcon(self.colourIconPath), '')
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

		self.countToolTipFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.countToolTipFontButton.setToolTip('Font')
		self.connect(self.countToolTipFontButton, SIGNAL('clicked()'), self.countToolTipFont)
		self.layout.addWidget(self.countToolTipFontButton, 5, 1)

		self.countToolTipColourButton = QPushButton(QIcon(self.colourIconPath), '')
		self.countToolTipColourButton.setToolTip('Color')
		self.connect(self.countToolTipColourButton, SIGNAL('clicked()'), self.countToolTipColour)
		self.layout.addWidget(self.countToolTipColourButton, 5, 2)

		self.countToolTipSFontButton = QPushButton(QIcon(self.fontIconPath), '')
		self.countToolTipSFontButton.setToolTip('Font')
		self.connect(self.countToolTipSFontButton, SIGNAL('clicked()'), self.countToolTipSFont)
		self.layout.addWidget(self.countToolTipSFontButton, 5, 3)

		self.countToolTipSColourButton = QPushButton(QIcon(self.colourIconPath), '')
		self.countToolTipSColourButton.setToolTip('Color')
		self.connect(self.countToolTipSColourButton, SIGNAL('clicked()'), self.countToolTipSColour)
		self.layout.addWidget(self.countToolTipSColourButton, 5, 4)

		self.setLayout(self.layout)

	def initValue(self, key_, defaultValue = ''):
		global Settings
		if Settings.contains(key_) :
			#print key_, Settings.value(key_).toString()
			return Settings.value(key_).toString()
		else :
			Settings.setValue(key_, QVariant(defaultValue))
			#print key_, Settings.value(key_).toString()
			return defaultValue

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
			style = 'QLabel { color: rgba(0, 0, 0, 125);} '
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
		#print self.headerColourVar, type(self.headerColourVar), QString(self.headerColourVar).toUInt()
		colour, yes, style = self.getColour(QString(self.headerColourVar).toUInt())
		if yes :
			self.headerColourVar = colour
			#print self.headerColourVar, type(self.headerColourVar)
			self.headerColourStyle = style
			prefix, suffix = self.cursive_n_bold(self.headerBoldVar, self.headerItalVar)
			self.headerFontLabel.clear()
			self.headerFontLabel.setStyleSheet(style)
			self.headerFontLabel.setText('<font face="' + self.headerFontVar + \
							'">' + prefix + self.tr._translate('Header :') + suffix + '</font>')

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
		self.Parent.wallet = KWallet.Wallet.openWallet('plasmaMailChecker', 0)
		if self.Parent.wallet is None :
			self.Parent.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
			return None

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

		Settings.sync()

	def eventClose(self, event):
		self.Parent.done(0)

def CreateApplet(parent):
	return plasmaMailChecker(parent)

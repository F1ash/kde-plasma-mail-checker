# -*- coding: utf-8 -*-

try :
	global warningMsg
	global Settings
	global PasswObj
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
	from Crypto.Cipher import Blowfish
	import poplib, imaplib, string, socket, time, os.path, logging, random, hashlib, sys
	logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
	RESULT = []
	Settings = QSettings('mailChecker','mailChecker')
	NewMailAttributes = []
	ErrorMsg = ''
	warningMsg = ''
	sys.stderr = open('/dev/shm/errorMailChecker' + str(time.time()) + '.log','w')
	sys.stdout = open('/dev/shm/outMailChecker' + str(time.time()) + '.log','w')
except ImportError, warningMsg :
	print "ImportError", warningMsg
	logging.debug(warningMsg)
finally:
	'O`key'

GeneralLOCK = QMutex()
WriteLOCK = QReadWriteLock()

class PassWord():
	def __init__(self, key = ''):

		if key == '' :
			key = '**This_bad_or_empty**_' + '16'
		self.key_ = key
		#print key, 'passw 1'
		global Settings
		self.Key = Blowfish.new(self.key_, Blowfish.MODE_ECB)
		if str(Settings.value('Hash').toString()) == \
								hashlib.sha512(self.key_).hexdigest() :
			self.access = True
		else:
			self.access = False

	def randomString(self, j = 1):
		return "".join( [random.choice(string.letters) for i in xrange(j)] )

	def encode(self, str_):
		STR = str_
		diff = int( len(STR)/16 + 1 )*16 - len(STR)
		Result = self.Key.encrypt( \
					str( STR + self.randomString(14 + diff) + str(16 + diff) ) \
									)
		STR = self.randomString( len(STR) )
		return Result

	def decode(self, str_ = ''):
		#print str_, 'decoding 1'
		if str_ == '' :
			str_ = '**This_bad_or_empty**_' + '16'
		try:
			str_raw = self.Key.decrypt(str_)
			#print str_raw, 'decoding 2'
			str_raw[:len(str_raw) - int(str_raw[-2:])]
		except ValueError, x:
			str_raw = '**This_bad_or_empty**_' + '16'
			logging.debug(unicode(x[0],'UTF-8'))
			#print x, 'passw 3'
		finally:
			pass
		return str_raw[:len(str_raw) - int(str_raw[-2:])]

	def createKeyHash(self):
		global Settings
		Settings.setValue('Hash', hashlib.sha512(self.key_).hexdigest())
		self.access = True

def addAccount(account, data_ = ['']):
	WriteLOCK.lockForWrite()
	global Settings
	accounts_ = Settings.value('Accounts').toString()
	Settings.setValue('Accounts', accounts_ + ';' + str(account))
	Settings.beginGroup(str(account))
	Settings.setValue('server', str(data_[0]))
	Settings.setValue('port', str(data_[1]))
	Settings.setValue('login', str(data_[2]))
	if str(data_[3]) != '***EncriptedPassWord***' :
		Settings.setValue('password', str(data_[3]))
	Settings.setValue('authentificationMethod', str(data_[4]))
	Settings.setValue('connectMethod', str(data_[5]))
	Settings.setValue('lastElemValue', str(data_[6]))
	Settings.endGroup()
	Settings.sync()
	WriteLOCK.unlock()
	pass

def readAccountData(account = ''):
	global Settings
	Settings.beginGroup(account)
	serv_ = Settings.value('server').toString()
	port_ = Settings.value('port').toString()
	login_ = Settings.value('login').toString()
	passw_ = Settings.value('password').toByteArray()
	authMethod_ = Settings.value('authentificationMethod').toString()
	connMethod_ = Settings.value('connectMethod').toString()
	last_ = Settings.value('lastElemValue').toString()
	Settings.endGroup()
	return [str(serv_), str(port_), str(login_), \
			passw_.data(), str(authMethod_), str(connMethod_), str(last_)]

def checkNewMailPOP3(accountName = '', parent = None):
	global ErrorMsg
	global PasswOBJ
	global Settings
	try:
		global NewMailAttributes
		newMailExist = False
		probeError = True
		authentificationData = readAccountData(accountName)
		#print accountName
		#logging.debug(accountName)
		lastElemUid = authentificationData[6]

		#print authentificationData[0],authentificationData[1],authentificationData[2],\
		#parent.passwObj.decode(authentificationData[3]),\
		#authentificationData[4],authentificationData[5],\
		#authentificationData[6] , 'читабельный вид у значений?'

		if authentificationData[4] == 'SSL' :
			m = poplib.POP3_SSL(authentificationData[0], authentificationData[1])
		else:
			m = poplib.POP3(authentificationData[0], authentificationData[1])

		auth_login = m.user(authentificationData[2])
		auth_passw = m.pass_( PasswOBJ.decode(authentificationData[3]) )
		#print auth_login, auth_passw, "дол быть о`кеи вроде бы"
		#logging.debug(auth_login+ auth_passw+ "дол быть о`кеи вроде бы")

		countAll = int(m.stat()[0])
		countNew = 0
		i = countAll
		while i > 0 :
			currentElemUid_raw = string.split(m.uidl(i),' ')
			currentElemUid = currentElemUid_raw[2]
			if currentElemUid > lastElemUid:
				Result =''
				for str_ in m.top(i,0)[1] :
					if str_[:5] in ['From:','Subje'] :
						Result += str_ + ' '
				# print Result
				NewMailAttributes += [Result]
				newMailExist = newMailExist or True
				countNew += 1
			else:
				break
			i += -1

		if newMailExist :
			lastElemUid_raw = string.split(m.uidl(countAll),' ')
			lastElemUid = lastElemUid_raw[2]
			Settings.beginGroup(accountName)
			Settings.setValue('lastElemValue', lastElemUid)
			Settings.endGroup()
		else:
			# print 'New message(s) not found.'
			if countAll == 0 :
				Settings.beginGroup(accountName)
				Settings.setValue('lastElemValue', '0')
				Settings.endGroup()

		m.quit()

		Settings.sync()

	except poplib.error_proto, x :
		ErrorMsg += '\n' + unicode(x[0],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew

def checkNewMailIMAP4(accountName = '', parent = None):
	global ErrorMsg
	global PasswOBJ
	global Settings
	try:
		global NewMailAttributes
		newMailExist = False
		probeError = True
		authentificationData = readAccountData(accountName)
		# print accountName
		lastElemTime = authentificationData[6]

		#print authentificationData[0],authentificationData[1],authentificationData[2],\
		#parent.passwObj.decode(authentificationData[3]),authentificationData[4],\
		#authentificationData[5],\
		#authentificationData[6], 'читабельный вид у значений?'

		#logging.debug(authentificationData[0]+authentificationData[1]+authentificationData[2]+\
		#authentificationData[3]+authentificationData[4]+authentificationData[5]+\
		#authentificationData[6]+ 'читабельный вид у значений?')

		if authentificationData[4] == 'SSL' :
			m = imaplib.IMAP4_SSL(authentificationData[0], authentificationData[1])
		else:
			m = imaplib.IMAP4(authentificationData[0], authentificationData[1])

		if m.login( authentificationData[2], \
					PasswOBJ.decode(authentificationData[3]) )[0] == 'OK' :
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
							if str_[:5] in ['From:','Subje'] :
								Result += str_ + ' '
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
		else:
			#print 'AuthError'
			logging.debug('AuthError')
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
			Settings.beginGroup(accountName)
			Settings.setValue('lastElemValue', lastElemTime)
			Settings.endGroup()
		else:
			# print 'New message(s) not found.'
			if countAll == 0 :
				Settings.beginGroup(accountName)
				Settings.setValue('lastElemValue', '0')
				Settings.endGroup()

		m.close()
		m.logout()

		Settings.sync()

	except imaplib.IMAP4.error, x :
		ErrorMsg += '\n' + unicode(x[0],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew

def connectProbe(probe_ = 3, checkNewMail = None, authentificationData = '', parent = None):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	i = 0
	while i < probe_ :
		# print 'Probe ', i + 1
		test_, all_, new_ = checkNewMail(authentificationData, parent)
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + authentificationData +'\n'
	return Result, all_, new_, ''

#def checkMail(accountName = '', parent = None):
def checkMail(args):
	global Settings
	accountName = args
	Msg = ''
	if accountName != '' :
		# print accountName
		countProbe_raw = Settings.value('CountProbe')
		# print countProbe_raw.toString()
		Settings.beginGroup(accountName)
		connectMethod = Settings.value('connectMethod')
		Settings.endGroup()
		try:
			countProbe = int(countProbe_raw.toString())
		except ValueError:
			countProbe = 3
		finally:
			pass
		# print str(connectMethod.toString()),'---'
		# print countProbe
		if str(connectMethod.toString()) == 'pop' :
			return  connectProbe(countProbe, checkNewMailPOP3, accountName)
		elif str(connectMethod.toString()) == 'imap' :
			return connectProbe(countProbe, checkNewMailIMAP4, accountName)
		else:
			Msg = 'connectMethod Error\n'
	else:
		Msg = 'accountName Error\n'
	return False, None, None, Msg

class ThreadCheckMail(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self, parent)

		#self.i = 0
		self.setTerminationEnabled(True)

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
			i = 0
			RESULT = []
			for accountName in string.split(Settings.value('Accounts').toString(),';') :
				RESULT += [checkMail(accountName)]
				i += 1

			GeneralLOCK.unlock()
		except x :
			print x
			logging.debug(x)
		finally :
			#print self.i
			#self.i += 1
			pass
		return

class plasmaMailChecker(plasmascript.Applet):
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self,parent)

		self.initStat = False
		self.checkResult = []

		self.panelIcon = Plasma.IconWidget()
		self.icon = Plasma.IconWidget()

	def init(self):
		global Settings
		self.setHasConfigurationInterface(True)

		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.layout.setSpacing(0)
		self.connect(self.applet, SIGNAL('destroyed()'), self.eventClose)
		self.connect(g, SIGNAL('finished()'), self.refreshData)

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
			self.TitleDialog.setText("<font color=blue><b>M@il Checker</b></font>")
			self.titleLayout.addItem(self.TitleDialog)

			self.icon = Plasma.IconWidget()
			self.icon.setIcon(iconPath)
			self.icon.setMaximumSize(35.0, 35.0)
			self.icon.setToolTip("<font color=blue><b>Click for Start\Stop</b></font>")
			self.connect(self.icon,SIGNAL('clicked()'), self._enterPassword)
			self.titleLayout.addItem(self.icon)

			self.layout.setOrientation(Qt.Vertical)
			self.layout.addItem(self.titleLayout)
			self.setMinimumSize(150.0,75.0)
			self.createDialogWidget()
		else:
			self.createIconWidget()

		self.applet.setLayout(self.layout)
		self.resize(self.size())

	def createDialogWidget(self):
		global Settings
		self.Dialog = QGraphicsGridLayout()
		i = 0
		self.label = []
		self.countList = []
		for accountName in string.split(Settings.value('Accounts').toString(),';') :
			#print accountName_
			self.label += accountName
			self.countList += accountName

			self.label[i] = Plasma.Label()
			self.countList[i] = Plasma.Label()
			self.label[i].setToolTip('Account ' + accountName)

			self.Dialog.addItem(self.label[i],i,0)
			self.Dialog.addItem(self.countList[i],i,1)
			i += 1

		self.labelStat = Plasma.Label()
		self.labelStat.setText("<font color=red><b>..stopped..</b></font>")
		self.Dialog.addItem(self.labelStat, i, 0)

		self.Dialog.updateGeometry()
		self.layout.addItem(self.Dialog)

		self.applet.setLayout(self.layout)

	def processInit(self):
		global Settings
		timeOut = Settings.value('TimeOut').toString()
		checkAfterRun = Settings.value('CheckAfterRun').toString()
		try:
			int(timeOut)
		except ValueError, x:
			#logging.debug(x)
			timeOut = '600'
		finally:
			pass
		try:
			int(checkAfterRun)
		except ValueError, x:
			#logging.debug(x)
			checkAfterRun = '0'
		finally:
			pass

		self.initStat = True
		self.Timer = QTimer()
		self.Timer.timeout.connect(self._refreshData)
		self.Timer.start(int(timeOut) * 1000)
		logging.debug('Timer started.')
		if checkAfterRun != '0' :
			self.Timer.singleShot(7000, self._refreshData)

		self.labelStat.setText("<font color=green><b>..running..</b></font>")

	def createNotifyrc(self, kdehome):
		# Output the notifyrc file to the correct location
		print "Outputting notifyrc file"

		# Create fbnotifier-plasmoid directory if required
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
		if self.initStat :
			path_ = self.kdehome + \
					'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=green><b>..running..</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)
		else:
			path_ = self.kdehome + \
				'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=red><b>..stopped..</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)

		global g
		g.start()

	def refreshData(self):
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
				self.labelStat.setText("<font color=green><b>..running..</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)
		else:
			noCheck = True
			path_ = self.kdehome + \
				'share/apps/plasma/plasmoids/plasmaMailChecker/contents/icons/mailChecker_stop.png'
			if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
				self.labelStat.setText("<font color=red><b>..stopped..</b></font>")
				self.icon.setIcon(path_)
			else :
				self.panelIcon.setIcon(path_)

		self.checkResult = RESULT
		i = 0
		newMailExist = False
		#print self.checkResult
		for accountName in string.split(Settings.value('Accounts').toString(),';') :
			try :
				if int(self.checkResult[i][2]) > 0 :
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						text_1 = "<font color=red><b>" + str(self.checkResult[i][1]) + "</b></font>"
						accountName_ = "<font color=red><b>" + accountName + "</b></font>"
						text_2 = "<font color=red><b>" + \
									'New : ' + str(self.checkResult[i][2]) + "</b></font>"
					newMailExist = True
				else:
					if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
						text_1 = "<font color=lime><b>" + \
									str(self.checkResult[i][1]) + "</b></font>"
						accountName_ = "<font color=lime><b>" + accountName + "</b></font>"
						text_2 = "<font color=lime><b>" + \
									'New : ' + str(self.checkResult[i][2]) + "</b></font>"
			except IndexError, x :
				print x
			finally :
				pass

			try:
				if self.initStat :
					self.label[i].setText(accountName_)
					self.countList[i].setText(text_1)
					self.countList[i].setToolTip(text_2)
			except AttributeError, x:
				#logging.debug(x)
				pass
			finally:
				pass
			i += 1

		self.applet.setLayout(self.layout)

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

		try :
			if ErrorMsg != '' or self.checkResult[i - 1][3] != '' :
				if Settings.value('ShowError').toString() != '0' and not noCheck :
					self.eventNotification(ErrorMsg + self.checkResult[i - 1][3])
		except IndexError, x :
			print x
		finally :
			pass

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
		self.panelIcon.setToolTip('M@ilChecker\nClick for Start\Stop')
		self.panelIcon.resize(32,32)
		self.panelIcon.show()
		self.connect(self.panelIcon,SIGNAL('clicked()'), self._enterPassword)
		self.layout.addItem(self.panelIcon)
		self.labelStat = Plasma.Label()

		self.setLayout(self.layout)

	def createConfigurationInterface(self, parent):
		self.editAccounts = EditAccounts(self)
		parent.addPage(self.editAccounts,"Accounts")
		self.appletSettings = AppletSettings(self)
		parent.addPage(self.appletSettings, 'Settings')
		self.passwordManipulate = PasswordManipulate(self)
		parent.addPage(self.passwordManipulate, 'Password Manipulation')
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
		global PasswOBJ
		if not PasswOBJ.access :
			self.eventNotification('Warning :\nAccess denied!')
			return None
		self.appletSettings.refreshSettings(self)
		#print self.formFactor(), '---'
		try:
			self.Timer.stop()
			# останов потока проверки почты перед изменением GUI
			global g
			while g.isRunning() :
				g.exit()
				time.sleep(0.05)
		except AttributeError, x:
			#logging.debug(x)
			pass
		except x :
			print x
		finally:
			pass
		if self.formFactor() in [Plasma.Planar, Plasma.MediaCenter] :
			self.createDialogWidget()
		logging.debug('Settings refreshed. Timer stopped.')
		self.initStat = False
		self.refreshData()

	def configDenied(self):
		pass

	def _enterPassword(self):
		if not self.initStat :
			self.enterPassword()
		else:
			try:
				if g.isRunning :
					g.quit()
				self.Timer.stop()
			except AttributeError, x :
				print
				pass
			except x :
				print x
			finally:
				pass
			logging.debug('No enter password. Timer stopped.')
			self.initStat = False
			self.refreshData()

	def enterPassword(self):
		self.initStat = True
		self.dialog = KeyDialog(self)
		self.dialog.move(self.popupPosition(self.dialog.sizeHint()))

	def eventClose(self):
		global g
		self.disconnect(g, SIGNAL('finished()'), self.refreshData)
		self.Timer.stop()
		g.quit()
		while g.isRunning() :
			g.exit()
			time.sleep(0.05)
		GeneralLOCK.unlock()
		print "MailChecker destroyed manually."
		logging.debug("MailChecker destroyed manually.")
		sys.stderr.close()
		sys.stdout.close()
		self.exit()

class KeyDialog(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self)

		global Settings
		self.Parent = parent
		self.setWindowTitle('Enter Encrypting Key')
		self.setMaximumSize(250.0, 120.0)
		self.layout = QGridLayout()

		self.existHash = len(str(Settings.value('Hash').toString()))
		if self.existHash == 0 :
			self.layout.addWidget(QLabel('<font color=red><b>Create Encrypting Key : </b></font>'), 0, 0)
		else:
			self.layout.addWidget(QLabel('<font color=blue><b>Encrypting Key : </b></font>'), 0, 0)

		self.keyLineEdit = KLineEdit()
		self.keyLineEdit.setContextMenuEnabled(True)
		self.keyLineEdit.setPasswordMode(True)
		self.layout.addWidget(self.keyLineEdit, 1, 0, 1, 2)
		self.ok = QPushButton('&Ok')
		self.cancel = QPushButton('&Cancel')
		self.layout.addWidget(self.ok, 2, 0)
		self.layout.addWidget(self.cancel, 2, 1)
		self.setLayout(self.layout)
		self.connect(self.ok,SIGNAL('clicked()'), self.initPassWord)
		self.connect(self.cancel,SIGNAL('clicked()'), self.eventClose)
		self.keyLineEdit.returnPressed.connect(self.initPassWord)
		self.show()

	def initPassWord(self):
		if str(self.keyLineEdit.userText()) == '' :
			self.eventClose()
			return None
		global PasswOBJ
		PasswOBJ = PassWord(str(self.keyLineEdit.userText()))
		if self.existHash == 0 :
			PasswOBJ.createKeyHash()
		#elif str(Settings.value('Hash').toString()) != \
		#						hashlib.sha512(str(self.keyLineEdit.userText())).hexdigest() :
		elif not PasswOBJ.access :
			self.eventClose()
			return None
		self.keyLineEdit.setText( PassWord().randomString(24) )
		self.Parent.processInit()
		self.close()

	def eventClose(self):
		self.Parent.initStat = False
		self.close()

class EditAccounts(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self, parent)

		self.Status = 'FREE'
		self.Parent = obj
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
		self.stringEditor.setToolTip("Deprecated char : '<b>;</b>'")
		self.stringEditor.setContextMenuEnabled(True)
		self.layout.addWidget(self.stringEditor,3,0)

		self.addAccountItem = QPushButton('&Add')
		self.addAccountItem.setToolTip('Add new Account')
		self.addAccountItem.clicked.connect(self.addNewAccount)
		self.layout.addWidget(self.addAccountItem,3,4)

		self.editAccountItem = QPushButton('&Edit')
		self.editAccountItem.setToolTip('Edit current Account')
		self.editAccountItem.clicked.connect(self.editCurrentAccount)
		self.layout.addWidget(self.editAccountItem,1,4)

		self.delAccountItem = QPushButton('&Del')
		self.delAccountItem.setToolTip('Delete current Account')
		self.delAccountItem.clicked.connect(self.delCurrentAccount)
		self.layout.addWidget(self.delAccountItem,0,4)

		self.VBLayout.addLayout(self.layout)

		self.HB1Layout = QGridLayout()

		self.HB1Layout.addWidget(QLabel('Server : '),0,0)

		self.HB1Layout.addWidget(QLabel('Port : '),0,1)

		self.serverLineEdit = KLineEdit()
		self.serverLineEdit.setContextMenuEnabled(True)
		self.serverLineEdit.setToolTip('Example : imap.gmail.com, pop.mail.ru')
		self.HB1Layout.addWidget(self.serverLineEdit,1,0)

		self.portBox = KIntSpinBox(0, 65000, 1, 0, self)
		self.HB1Layout.addWidget(self.portBox, 1, 1)

		self.VBLayout.addLayout(self.HB1Layout)

		self.HB2Layout = QGridLayout()

		self.HB2Layout.addWidget(QLabel('AuthMethod : '),0,0)

		self.connectMethodBox = KComboBox()
		self.connectMethodBox.addItem('POP3',QVariant('pop'))
		self.connectMethodBox.addItem('IMAP4',QVariant('imap'))
		self.HB2Layout.addWidget(self.connectMethodBox,1,0)

		self.HB2Layout.addWidget(QLabel('Encrypt : '),0,1)

		self.cryptBox = KComboBox()
		self.cryptBox.addItem('None',QVariant('None'))
		self.cryptBox.addItem('SSL',QVariant('SSL'))
		self.HB2Layout.addWidget(self.cryptBox,1,1)

		self.HB2Layout.addWidget(QLabel('Changes : '),0,2)

		self.saveChanges = QPushButton('&Save')
		self.saveChanges.clicked.connect(self.saveChangedAccount)
		self.HB2Layout.addWidget(self.saveChanges,1,2)

		self.clearChanges = QPushButton('&Clear')
		self.clearChanges.clicked.connect(self.clearChangedAccount)
		self.HB2Layout.addWidget(self.clearChanges,1,3)

		self.VBLayout.addLayout(self.HB2Layout)

		self.HB3Layout = QGridLayout()

		self.HB3Layout.addWidget(QLabel('Username : '),0,0)

		self.HB3Layout.addWidget(QLabel('Password : '),0,1)

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
		global PasswOBJ
		if not PasswOBJ.access :
			self.Parent.eventNotification('Warning :\nAccess denied!')
			return None
		if self.Status == 'BUSY' :
			return None
		self.clearFields()
		self.Status = 'FREE'

	def saveChangedAccount(self):
		global PasswOBJ
		global Settings
		if not PasswOBJ.access :
			self.Parent.eventNotification('Warning :\nAccess denied!')
			return None
		if self.Status == 'READY' :
			accountName, authData = self.parsingValues()
			if accountName == '' :
				self.clearChangedAccount()
				self.Parent.eventNotification('Warning :\nSet Account Name!')
				return None
			self.Status = 'CLEAR'
			self.delCurrentAccount(self.oldAccountName)
			self.accountListBox.addItem(accountName)
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
		global PasswOBJ
		if not PasswOBJ.access :
			self.Parent.eventNotification('Warning :\nAccess denied!')
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
		if parameterList[3] != '***EncriptedKey_not_created***' :
			self.passwordLineEdit.setText('***EncriptedPassWord***')
		else:
			self.passwordLineEdit.setText(str(parameterList[3]))
		self.Status = 'READY'
		pass

	def addNewAccount(self):
		global PasswOBJ
		if not PasswOBJ.access :
			self.eventNotification('Warning :\nAccess denied!')
			self.configDenied()
			return None
		if self.Status != 'FREE' :
			return None
		str_ = self.stringEditor.userText()
		if str(str_) != '' :
			self.accountListBox.addItem(str_)
			accountName, authData = self.parsingValues()
			addAccount(accountName, authData)
			self.clearFields()

	def parsingValues(self):
		global PasswOBJ
		global Settings
		accountName = self.stringEditor.userText()
		accountServer = self.serverLineEdit.userText()
		connectMethod = self.connectMethodBox.itemData(self.connectMethodBox.currentIndex()).toString()
		cryptMethod = self.cryptBox.itemData(self.cryptBox.currentIndex()).toString()
		port_ = self.portBox.value()
		userName = self.userNameLineEdit.userText()
		if len(str(Settings.value('Hash').toString())) == 0 :
			userPassword = '***EncriptedKey_not_created***'
			self.Parent.eventNotification('Warning :\nPassword non-encrypted!')
		elif str(self.passwordLineEdit.userText()) != '***EncriptedPassWord***' :
			# print str(self.passwordLineEdit.userText())
			userPassword = PasswOBJ.encode( str(self.passwordLineEdit.userText()) )
		else:
			userPassword = '***EncriptedPassWord***'
		# print accountName,accountServer,port_,connectMethod,cryptMethod, userName,userPassword, 'parsingVal'
		return accountName,\
				[ accountServer, port_, userName,\
				 userPassword, cryptMethod, connectMethod, '0' ]

	def delCurrentAccount(self, accountName = ''):
		global PasswOBJ
		global Settings
		if not PasswOBJ.access :
			self.Parent.eventNotification('Warning :\nAccess denied!')
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
		try:
			self.accountList.remove(accountName)
		except ValueError, x :
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
		global Settings

		timeOut = Settings.value('TimeOut').toString()
		checkAfterRun = Settings.value('CheckAfterRun').toString()
		countProbe = Settings.value('CountProbe').toString()
		showError = Settings.value('ShowError').toString()
		try:
			int(timeOut)
		except ValueError, x:
			#logging.debug(x)
			timeOut = '600'
		finally:
			pass
		try:
			int(checkAfterRun)
		except ValueError, x:
			#logging.debug(x)
			checkAfterRun = '0'
		finally:
			pass
		try:
			int(countProbe)
		except ValueError, x:
			#logging.debug(x)
			countProbe = 3
		finally:
			pass
		try:
			int(showError)
		except ValueError, x:
			#logging.debug(x)
			showError = 1
		finally:
			pass

		self.layout = QGridLayout()

		self.timeOutLabel = QLabel("Timeout checking (sec.):")
		self.layout.addWidget(self.timeOutLabel,0,0)

		self.timeOutBox = KIntSpinBox(1, 7200, 1, int(timeOut), self)
		self.layout.addWidget(self.timeOutBox, 0, 1)

		self.timeOutLabel = QLabel("Check mail after\nrun applet:")
		self.layout.addWidget(self.timeOutLabel,1,0)

		self.checkAfterRun = QCheckBox()
		if int(checkAfterRun) > 0 :
			self.checkAfterRun.setCheckState(2)
		self.layout.addWidget(self.checkAfterRun,1,1)

		self.countProbe = QLabel("Count of connect probe\nto mail server:")
		self.layout.addWidget(self.countProbe,2,0)

		self.countProbeBox = KIntSpinBox(1, 10, 1, int(countProbe), self)
		self.layout.addWidget(self.countProbeBox, 2, 1)

		self.showError = QLabel("Show error messages :")
		self.layout.addWidget(self.showError,3,0)

		self.showErrorBox = QCheckBox()
		if int(showError) > 0 :
			self.showErrorBox.setCheckState(2)
		self.layout.addWidget(self.showErrorBox,3,1)

		self.setLayout(self.layout)

	def refreshSettings(self, parent = None):
		global Settings
		if not PasswOBJ.access :
			self.Parent.eventNotification('Warning :\nAccess denied!')
			return None
		Settings.setValue('TimeOut', str(self.timeOutBox.value()))
		Settings.setValue('CountProbe', str(self.countProbeBox.value()))
		if self.checkAfterRun.isChecked() :
			Settings.setValue('CheckAfterRun', '1')
		else:
			Settings.setValue('CheckAfterRun', '0')
		if self.showErrorBox.isChecked() :
			Settings.setValue('ShowError', '1')
		else:
			Settings.setValue('ShowError', '0')

		Settings.sync()

class PasswordManipulate(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj

		self.VBLayout = QVBoxLayout()

		self.layout = QGridLayout()

		self.existHash = len(str(Settings.value('Hash').toString()))
		if self.existHash == 0 :
			self.layout.addWidget(QLabel('<font color=red><b>Create Encrypting Key : </b></font>'), 0, 0)
		else:
			self.layout.addWidget(QLabel('<font color=blue><b>Encrypting Key : </b></font>'), 0, 0)

			self.layout.addWidget(QLabel('Old key : '),4,0)

			self.oldKey = KLineEdit()
			self.oldKey.setContextMenuEnabled(True)
			self.oldKey.setPasswordMode(True)
			self.layout.addWidget(self.oldKey,5,0)

		self.inputKey = KLineEdit()
		self.inputKey.setPasswordMode(True)
		self.inputKey.setContextMenuEnabled(True)
		self.layout.addWidget(self.inputKey,1,0)

		self.layout.addWidget(QLabel('Confirm key : '),2,0)

		self.confirmKey = KLineEdit()
		self.confirmKey.setContextMenuEnabled(True)
		self.confirmKey.setPasswordMode(True)
		self.layout.addWidget(self.confirmKey,3,0)

		self.addAccountItem = QPushButton('&New')
		self.addAccountItem.setToolTip('Create new Password')
		self.addAccountItem.clicked.connect(self.createNewKey)
		self.layout.addWidget(self.addAccountItem,3,4)

		self.VBLayout.addLayout(self.layout)

		self.setLayout(self.VBLayout)

	def createNewKey(self):
		global PasswOBJ
		global Settings
		if str(self.inputKey.userText()) == '' :
			self.clearFields()
			self.Parent.eventNotification('Warning :\nThis password must die!')
			return None
		elif str(self.inputKey.userText()) != str(self.confirmKey.userText()) :
			self.clearFields()
			self.Parent.eventNotification('Warning :\nConfirmation false!')
			return None
		if self.existHash == 0 :
			PasswOBJ = PassWord(str(self.inputKey.userText()))
			PasswOBJ.createKeyHash()
		elif str(Settings.value('Hash').toString()) != \
										hashlib.sha512(str(self.oldKey.userText())).hexdigest() :
			self.clearFields()
			self.Parent.eventNotification('Warning :\nAccess denied!')
			return None
		else:
			# расшифровать пароль каждой учётки
			# и сразу перешифровать; по окончании --
			# -- пересоздать объект PasswOBJ
			i = 0
			self.accountList = []
			while i < Settings.childGroups().count() :
				accountName = Settings.childGroups().__getitem__(i)
				self.accountList += [accountName]
				i += 1
			_error = False
			for account in self.accountList :
				Settings.beginGroup(str(account))
				# порверка перешифровки
				str_ = Settings.value('password').toByteArray()
				try:
					PassWord(str(self.inputKey.userText())).\
							encode(str(PasswOBJ.decode(str_.data())))
				except UnicodeEncodeError, x:
					logging.debug(x)
					# print x, '----'
					_error = True
				finally:
					Settings.endGroup()
					pass
			if not _error :
				for account in self.accountList :
					Settings.beginGroup(str(account))
					# перешифровка
					str_ = Settings.value('password').toByteArray()
					Settings.setValue('password', \
	PassWord(str(self.inputKey.userText())).encode(str(PasswOBJ.decode(str_.data()))))
					Settings.endGroup()

				PasswOBJ = PassWord(str(self.inputKey.userText()))
				PasswOBJ.createKeyHash()
				self.Parent.eventNotification('Information :\nPassword changed successfull!')
			else:
				self.Parent.eventNotification('Warning :\nEncode\decode error...\nMay be config destructed.\nClear config manually.')

			self.clearFields()
		pass

	def clearFields(self):
		self.inputKey.clear()
		self.confirmKey.clear()
		self.oldKey.clear()

try:
	def CreateApplet(parent):
		return plasmaMailChecker(parent)
except x :
	print x
finally :
	#sys.stderr.close()
	#sys.stdout.close()
	pass

PasswOBJ = PassWord()
g = ThreadCheckMail()

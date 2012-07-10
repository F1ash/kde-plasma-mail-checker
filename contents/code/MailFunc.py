# -*- coding: utf-8 -*-

from imapUTF7 import imapUTF7Encode
from PyQt4.QtCore import QString, QSettings, QMutex
import poplib, imaplib, time, datetime, locale, socket

global ErrorMsg
ErrorMsg = ''
LOCK = QMutex()
Settings = QSettings('plasmaMailChecker','plasmaMailChecker')

def readProxySettings(socks):
	def take_value(arg):
		return None if arg == 'None' or arg.isEmpty() else QString().fromUtf8(arg)
	_type = Settings.value('ProxyType', 'None').toString()
	if   _type is None : proxytype = None
	elif _type == 'HTTP' : proxytype = socks.PROXY_TYPE_HTTP
	elif _type == 'SOCKS4' : proxytype = socks.PROXY_TYPE_SOCKS4
	elif _type == 'SOCKS5' : proxytype = socks.PROXY_TYPE_SOCKS5
	else : proxytype = None
	_addr = Settings.value('ProxyAddr', 'None').toString()
	addr = take_value(_addr)
	_port = take_value(Settings.value('ProxyPort', 'None').toString())
	port = int(_port) if _port else None
	rdns = True if Settings.value('ProxyRDNS', 'True').toString()=='True' else False
	_name = Settings.value('ProxyUSER', 'None').toString()
	username = take_value(_name)
	_pass = Settings.value('ProxyPASS', 'None').toString()
	password = take_value(_pass)
	return proxytype, addr, port, rdns, username, password

def loadSocketModule(loadModule = None):
	proxyLoad = False
	reload(socket)
	if ( loadModule is None and Settings.value('UseProxy', 'False')=='True' ) or loadModule :
		## http://sourceforge.net/projects/socksipy/
		## or install the Fedora liked python-SocksiPy package
		try :
			import socks
			proxyLoad = True
		except : pass #proxyLoad = False
		finally :
			if proxyLoad :
				"""setdefaultproxy(proxytype, addr[, port[, rdns[, username[, password]]]])"""
				proxytype, addr, port, rdns, username, password = readProxySettings(socks)
				#print proxytype, addr, port, rdns, username, password
				socks.setdefaultproxy(proxytype, addr, port, rdns, username, password)
				socket.socket = socks.socksocket
	reload(poplib)
	reload(imaplib)
	return proxyLoad

def losedBlank(str_raw):
	""" рассчёт на то, что в строке может быть не одна закодированная фраза
		поэтому добавляем пробел в конце обработанной фразы
	"""
	STR_ = ''
	for str_ in str_raw.split(' ') :
		_str = str_.rpartition('?=')
		if _str[1] != '' and _str[2] != '' :
			STR_ += ''.join([ _str[0], '?= ', losedBlank( _str[2] )]) + ' '
		else :
			STR_ += str_ + ' '
	return STR_

def codeDetect(str_):
	charSetExist = False
	_str = ''
	for _diff in ['charset = ', 'charset =', 'charset= ', 'charset='] :
		_str = str_.partition(_diff)
		if _str[1] != '' :
			charSetExist = charSetExist or True
			break
	if not charSetExist or _str[2] == '' : return ''
	STR = [_str[2]]
	for symbol in ['\r\n', '\n', ';'] :
		_str_raw = STR[0].partition(symbol)
		STR = _str_raw
	headerCode = STR[0].replace('"','').lower()
	## print headerCode, ' <--  header Code'
	return headerCode

def dateStamp():
	return time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime()) + ' : '

def to_unicode(txt, encoding = 'utf-8'):
	if isinstance(txt, basestring) :
		if not isinstance(txt, unicode) :
			txt = unicode(txt, encoding, errors = 'replace')
	return txt

def defineUIDL(accountName = '', str_ = ''):
	Result = True
	# print dateStamp(), accountName
	x = ''
	STR = []
	try :
		f = open('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache', 'r')
		STR = f.readlines()
		f.close()
		# print dateStamp(), STR
	except x :
		print dateStamp(), x, '  defUidl'
	finally :
		for uid_ in STR :
			# print dateStamp(), uid_.split('\n')[0] , '--- ', str_
			if str_ == uid_.split('\n')[0] :
				Result = False
				break
	return Result

def readAccountData(account = ''):
	LOCK.lock()
	global Settings
	Settings.beginGroup(account)
	serv_ = Settings.value('server').toString()
	port_ = Settings.value('port').toString()
	if port_ == '' : port_ =  '0'
	login_ = Settings.value('login').toString()
	authMethod_ = Settings.value('authentificationMethod').toString()
	connMethod_ = Settings.value('connectMethod').toString()
	last_ = Settings.value('lastElemValue').toString()
	enable = Settings.value('Enabled').toString()
	if str(connMethod_) == 'imap' :
		inbox = Settings.value('Inbox').toString()
	else :
		inbox = ''
	if Settings.contains('CommandLine') :
		command = Settings.value('CommandLine').toString()
	else :
		command = ''
	Settings.endGroup()
	LOCK.unlock()
	return [str(serv_), str(port_), login_, '', \
			str(authMethod_), str(connMethod_), str(last_), str(enable), inbox, command]

def checkNewMailPOP3(accountData = ['', '']):
	global ErrorMsg
	encoding = ''
	x = ''
	try:
		NewMailAttributes = ''
		newMailExist = False
		probeError = True
		countNew = 0
		mailUidls = []
		countAll = 0
		authentificationData = readAccountData(accountData[0])
		lastElemUid = authentificationData[6]

		if authentificationData[4] == 'SSL' :
			m = poplib.POP3_SSL(authentificationData[0], authentificationData[1])
		else :
			m = poplib.POP3(authentificationData[0], authentificationData[1])

		#auth_login = m.user(authentificationData[2])
		if m.user(authentificationData[2])[:3] == '+OK' :
			#auth_passw = m.pass_( accountData[1] )
			if m.pass_( accountData[1] )[:3] == '+OK' :

				countAll = int(m.stat()[0])
				for uidl_ in m.uidl()[1] :
					currentElemUid = uidl_.split(' ')[1]
					mailUidls += [currentElemUid + '\n']
					if defineUIDL(accountData[0], currentElemUid) :
						From = ''
						Subj = ''
						Date = ''
						Code = ''
						Next = ''
						for str_ in m.top( int(uidl_.split(' ')[0]) , 0)[1] :
							if str_[:5] == 'From:' or (Next == 'From' and str_[:1] == ' ') :
								Next = 'From'
								From += losedBlank(str_) + ' '
								#print dateStamp(), From
							elif str_[:5] == 'Subje' or (Next == 'Subj' and str_[:1] == ' ') :
								Next = 'Subj'
								Subj += losedBlank(str_) + ' '
								#print dateStamp(), Subj
							elif str_[:13].lower() == 'content-type:' \
								 and str_.lower().find('text/plain') > -1 \
								 or (Next == 'Code' and str_[:1] == ' ') :
								Next = 'Code'
								Code += codeDetect(str_)
							elif str_[:5] == 'Date:' :
								Date += str_
								#print dateStamp(), Date
							else : Next = ''
						NewMailAttributes += Date + '\r\n' + From + '\r\n' + Subj + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ------'
						encoding += Code + '\n'
						#print encoding, '  encoding POP3'
						newMailExist = newMailExist or True
						countNew += 1

				c = open('/dev/shm/' + QString(accountData[0]).toUtf8().data() + '.cache', 'w')
				c.writelines( mailUidls )
				c.close()

		m.quit()

	except poplib.error_proto, x :
		print dateStamp(), x, '  POP3_1'
		ErrorMsg += '\n' + unicode(x[0],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		print dateStamp(), x, '  POP3_2'
		ErrorMsg += '\n' + unicode(str(x),'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		print dateStamp(), x, '  POP3_3'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except UnicodeDecodeError, x :
		print dateStamp(), x, '  POP3_4'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except x:
		print dateStamp(), x, '  POP3_5'
		ErrorMsg += 'Unknown Error\n'
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew, NewMailAttributes, encoding, '-'

def getCurrentElemTime(m, i):
	currentElemTime_raw = m.fetch(i,"INTERNALDATE")[1][0].split(' ')
	currentElemTime_Internal = currentElemTime_raw[1] + ' ' \
							 + currentElemTime_raw[2] + ' ' \
							 + currentElemTime_raw[3] + ' ' \
							 + currentElemTime_raw[4]
	# print dateStamp(), currentElemTime_Internal
	date_ = imaplib.Internaldate2tuple(currentElemTime_Internal)
	return str(time.mktime(date_))

def getMailAttributes(m, i):
	Date = ''
	From = ''
	Subj = ''
	Date = m.fetch(i,"(BODY.PEEK[HEADER.FIELDS (date)])")[1][0][1].replace('\r\n\r\n', '')
	From = m.fetch(i,"(BODY.PEEK[HEADER.FIELDS (from)])")[1][0][1].replace('\r\n\r\n', '')
	Subj = m.fetch(i,"(BODY.PEEK[HEADER.FIELDS (subject)])")[1][0][1].replace('\r\n\r\n', '')
	# NewMailAttributes += m.fetch(i,"(BODY.PEEK[HEADER.FIELDS (date from subject)])")[1][0][1]
	return Date, From, Subj

def checkNewMailIMAP4(accountData = ['', '']):
	global Settings
	global ErrorMsg
	encoding = ''
	x = ''
	try:
		NewMailAttributes = ''
		newMailExist = False
		probeError = True
		countNew = 0
		countAll = 0
		unSeen = 0
		authentificationData = readAccountData(accountData[0])
		lastElemTime = authentificationData[6]

		if authentificationData[4] == 'SSL' :
			m = imaplib.IMAP4_SSL(authentificationData[0], authentificationData[1])
		else :
			m = imaplib.IMAP4(authentificationData[0], authentificationData[1])

		if m.login( authentificationData[2], accountData[1] )[0] == 'OK' :
			if authentificationData[8] == '' :
				mailBox = 'INBOX'
			else :
				mailBox = unicode(QString(authentificationData[8]).toUtf8().data(), 'utf-8')
			#print dateStamp(), mailBox, imapUTF7Encode(mailBox)
			answer = m.select(imapUTF7Encode(mailBox))
			if answer[0] == 'OK':
				unSeen = len(m.search(None, 'UnSeen')[1][0].split())
				countAll = int(answer[1][0])
				i = countAll
				while i > 0 :
					currentElemTime = getCurrentElemTime(m, i)
					# print dateStamp(), currentElemTime
					if currentElemTime > lastElemTime :
						Date, From, Subj = getMailAttributes(m, i)
						NewMailAttributes += Date + '\r\n' + From + '\r\n' + Subj + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ----==------'
						encoding += '\n'
						newMailExist = newMailExist or True
						countNew += 1
					else:
						break
					i += -1
			else:
				#print dateStamp(), 'selectDirError'
				probeError, countAll, countNew = False, 0, 0
		else:
			#print dateStamp(), 'AuthError'
			probeError, countAll, countNew = False, 0, 0

		if newMailExist :
			lastElemTime = getCurrentElemTime(m, countAll)
			# print dateStamp(), lastElemTime
			Settings.beginGroup(accountData[0])
			Settings.setValue('lastElemValue', lastElemTime)
			Settings.endGroup()
		else:
			# print dateStamp(), 'New message(s) not found.'
			if countAll == 0 :
				Settings.beginGroup(accountData[0])
				Settings.setValue('lastElemValue', '0')
				Settings.endGroup()

		if answer[0] == 'OK' :
			m.close()
		m.logout()

		Settings.sync()

	except imaplib.IMAP4.error, x :
		print dateStamp(), x, '  IMAP4_1'
		ErrorMsg += '\n' + unicode(str(x),'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.error, x :
		print dateStamp(), x, '  IMAP4_2'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except socket.gaierror, x :
		print dateStamp(), x, '  IMAP4_3'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except UnicodeDecodeError, x :
		print dateStamp(), x, '  IMAP4_4'
		ErrorMsg += '\n' + unicode(x[1],'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	except x:
		print dateStamp(), x, '  IMAP4_5'
		ErrorMsg += 'Unknown Error\n'
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew, NewMailAttributes, encoding, unSeen

def connectProbe(probe_ = 3, checkNewMail = None, authData = ['', ''], acc = ''):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	encoding = ''
	unSeen = '-'
	i = 0
	while i < probe_ :
		#print dateStamp(), 'Probe ', i + 1, to_unicode(authData[0])
		test_, all_, new_, content, encoding, unSeen = checkNewMail(authData)
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + to_unicode(acc) + '\n'
	#print dateStamp(), ErrorMsg, '  errors'
	return Result, all_, new_, ErrorMsg, QString(content).toUtf8(), encoding, str(unSeen)

def checkMail(accountData = ['', '']):
	global Settings
	Msg = ''
	if accountData[0] != '' :
		#print dateStamp(), accountData[0]
		countProbe_raw = Settings.value('CountProbe')
		#print dateStamp(), countProbe_raw.toString()
		account = QString().fromUtf8(accountData[0])
		Settings.beginGroup(account)
		connectMethod = Settings.value('connectMethod').toString()
		Settings.endGroup()
		try:
			countProbe = int(countProbe_raw.toString())
		except ValueError:
			print dateStamp(), '  checkMail'
			countProbe = 3
		finally:
			pass
		#print dateStamp(), str(connectMethod),'---'
		#print dateStamp(), countProbe
		if str(connectMethod) == 'pop' :
			return  connectProbe(countProbe, checkNewMailPOP3, [account, accountData[1]], accountData[0])
		elif str(connectMethod) == 'imap' :
			return connectProbe(countProbe, checkNewMailIMAP4, [account, accountData[1]], accountData[0])
		else:
			Msg = 'ConnectMethod Error\n'
	else:
		Msg = 'AccountName Error\n'
	return False, 0, 0, Msg, '', '', '-'


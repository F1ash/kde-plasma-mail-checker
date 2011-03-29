# -*- coding: utf-8 -*-

from imapUTF7 import imapUTF7Decode, imapUTF7Encode
from PyQt4.QtCore import QString, QSettings, QReadWriteLock
import poplib, imaplib, os, string, socket, time, os.path, random, sys, email.header, datetime, locale

global ErrorMsg
ErrorMsg = ''
LOCK = QReadWriteLock()
Settings = QSettings('plasmaMailChecker','plasmaMailChecker')

dltHours = time.localtime().tm_hour - time.gmtime().tm_hour
dltMinutes = time.localtime().tm_min - time.gmtime().tm_min
dltLocal = datetime.timedelta(hours = dltHours, minutes = dltMinutes)

lang = locale.getdefaultlocale()

def utcDelta(str_):
	hours_ = int(str_[:3])
	minutes_ = int(str_[:1] + str_[-2:])
	return datetime.timedelta(hours = hours_, minutes = minutes_)

def dateFormat(str_):
	print str_
	locale.setlocale(locale.LC_ALL, 'C')
	localTime = datetime.datetime.strptime( str_[6:-6], "%a, %d %b %Y %H:%M:%S" ) - utcDelta(str_[-5:]) + dltLocal
	data_ = localTime.timetuple()
	#return time.ctime(time.mktime(localTime.timetuple()))
	locale.setlocale(locale.LC_ALL, lang)
	dateSTR = time.strftime("%a, %d.%m.%Y %H:%M:%S", time.localtime(time.mktime(data_)))
	print dateSTR
	return 'Date: ' + QString().fromUtf8(dateSTR)

def mailAttrToSTR(_str):
	From = ''
	Subj = ''
	Date = ''
	for str_ in string.split(_str, '\r\n') :
		if str_[:5] == 'From:' :
			From = decodeMailSTR(str_) + ' '
			#print dateStamp(), From
		if str_[:5] == 'Subje' :
			Subj = decodeMailSTR(str_) + ' '
			#print dateStamp(), Subj
		if str_[:5] == 'Date:' :
			Date = str_
			#print dateStamp(), Date
	return From + '\n' + Subj + '\n' + dateFormat(Date) + '\n'

def decodeMailSTR(str_):
	obj = ''
	for part_str in email.header.decode_header(str_) :
		if part_str[1] is None :
			obj += part_str[0] + ' '
		else :
			obj += part_str[0].decode(part_str[1]) + ' '
	return obj

def dateStamp():
	return time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime()) + ' : '

def cleanDebugOutputLogFiles(stay = 1):
	LIST = []
	uid = os.geteuid()
	for name_ in os.listdir('/tmp') :
		name = '/tmp/' + name_
		if os.path.isfile(name) and name[:19] == '/tmp/outMailChecker' and os.stat(name).st_uid == uid :
				LIST += [name]
	while len(LIST) > stay :
		try :
			minItem = min(LIST)
			os.remove(minItem)
			LIST.remove(minItem)
		except OSError:
			pass

def pid_exists(pid, sig):
	try:
		os.kill(pid, sig)
		return True
	except OSError, err:
		return False

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
						str(dataToSTR(path_ + '.content'))

def randomString(j = 1):
	return "".join( [random.choice(string.letters) for i in xrange(j)] )

def to_unicode(_str):
	str_ = '<=junk_string=>'
	try:
		#print dateStamp(), _str, '---'
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
	Settings.setValue('Enabled', str(data_[7]))
	if str(data_[5]) == 'imap' :
		Settings.setValue('Inbox', data_[8])
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
	enable = Settings.value('Enabled').toString()
	if str(connMethod_) == 'imap' :
		inbox = Settings.value('Inbox').toString()
	else :
		inbox = ''
	Settings.endGroup()
	LOCK.unlock()
	return [str(serv_), str(port_), login_, '', \
			str(authMethod_), str(connMethod_), str(last_), str(enable), inbox]

def initPOP3Cache():
	LOCK.lockForWrite()
	global Settings
	dir_cache = os.path.expanduser('~/.cache')
	if  not os.path.isdir(dir_cache) :
		os.mkdir(dir_cache)
	dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
	if  not os.path.isdir(dir_) :
		os.mkdir(dir_)
	for accountName in string.split( Settings.value('Accounts').toString(), ';' ):
		Settings.beginGroup(accountName)
		if Settings.value('connectMethod').toString() == 'pop' :
			if not os.path.isfile(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache') :
				f = open(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache', 'w')
				f.close()
			f = open(dir_ +  '/' + QString(accountName).toUtf8().data() + '.cache', 'r')
			c = open('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache', 'w')
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
			f = open(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache', 'w')
			if os.path.isfile('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache') :
				c = open('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache', 'r')
				f.writelines(c.readlines())
				c.close()
			f.close()
		Settings.endGroup()
	LOCK.unlock()

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
			# print dateStamp(), string.split(uid_, '\n')[0] , '--- ', str_
			if str_ == string.split(uid_, '\n')[0] :
				Result = False
				break
	return Result

def checkNewMailPOP3(accountData = ['', '']):
	global ErrorMsg
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
		else:
			m = poplib.POP3(authentificationData[0], authentificationData[1])

		#auth_login = m.user(authentificationData[2])
		if m.user(authentificationData[2])[:3] == '+OK' :
			#auth_passw = m.pass_( accountData[1] )
			if m.pass_( accountData[1] )[:3] == '+OK' :

				countAll = int(m.stat()[0])
				for uidl_ in m.uidl()[1] :
					currentElemUid = string.split(uidl_,' ')[1]
					mailUidls += [currentElemUid + '\n']
					if defineUIDL(accountData[0], currentElemUid) :
						From = ''
						Subj = ''
						Date = ''
						for str_ in m.top( int(string.split(uidl_,' ')[0]) , 0)[1] :
							if str_[:5] == 'From:' :
								From += str_
								#print dateStamp(), From
							if str_[:5] == 'Subje' :
								Subj += str_
								#print dateStamp(), Subj
							if str_[:5] == 'Date:' :
								Date += str_
								#print dateStamp(), Date
						NewMailAttributes += From + '\r\n' + Subj + '\r\n' + Date + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ------'
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

	return probeError, countAll, countNew, NewMailAttributes

def checkNewMailIMAP4(accountData = ['', '']):
	global Settings
	global ErrorMsg
	x = ''
	try:
		NewMailAttributes = ''
		newMailExist = False
		probeError = True
		countNew = 0
		countAll = 0
		authentificationData = readAccountData(accountData[0])
		lastElemTime = authentificationData[6]

		if authentificationData[4] == 'SSL' :
			m = imaplib.IMAP4_SSL(authentificationData[0], authentificationData[1])
		else:
			m = imaplib.IMAP4(authentificationData[0], authentificationData[1])

		if m.login( authentificationData[2], '\'' + accountData[1] + '\'' )[0] == 'OK' :
			if authentificationData[8] == '' :
				mailBox = 'INBOX'
			else :
				mailBox = unicode(QString(authentificationData[8]).toUtf8().data(), 'utf-8')
			#print dateStamp(), mailBox
			answer = m.select(imapUTF7Encode(mailBox))
			if answer[0] == 'OK':
				countAll = int(answer[1][0])
				i = countAll
				while i > 0 :
					currentElemTime_raw = string.split(m.fetch(i,"INTERNALDATE")[1][0],' ')
					currentElemTime_Internal = currentElemTime_raw[1] + ' ' \
												+ currentElemTime_raw[2] + ' ' \
												+ currentElemTime_raw[3] + ' ' \
												+ currentElemTime_raw[4]
					# print dateStamp(), currentElemTime_Internal
					date_ = imaplib.Internaldate2tuple(currentElemTime_Internal)
					currentElemTime = str(time.mktime(date_))
					# print dateStamp(), currentElemTime
					if currentElemTime > lastElemTime :
						NewMailAttributes += m.fetch(i,"(BODY.PEEK[HEADER.FIELDS (date from subject)])")[1][0][1]
						#print dateStamp(), NewMailAttributes, '   ----==------'
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
			lastElemTime_raw = string.split(m.fetch(countAll,"INTERNALDATE")[1][0],' ')
			lastElemTime_Internal = lastElemTime_raw[1] + ' ' \
									+ lastElemTime_raw[2] + ' ' \
									+ lastElemTime_raw[3] + ' ' \
									+ lastElemTime_raw[4]
			# print dateStamp(), lastElemTime_Internal
			date_ = imaplib.Internaldate2tuple(lastElemTime_Internal)
			lastElemTime = str(time.mktime(date_))
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

	return probeError, countAll, countNew, NewMailAttributes

def connectProbe(probe_ = 3, checkNewMail = None, authData = ['', ''], acc = ''):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	i = 0
	while i < probe_ :
		#print dateStamp(), 'Probe ', i + 1, to_unicode(authData[0])
		test_, all_, new_, content = checkNewMail(authData)
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + to_unicode(acc) + '\n'
	#print dateStamp(), ErrorMsg, '  errors'
	return Result, all_, new_, ErrorMsg, QString(content).toUtf8()

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
	return False, 0, 0, Msg, ''

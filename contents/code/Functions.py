# -*- coding: utf-8 -*-

from PyQt4.QtCore import QString, QSettings, QReadWriteLock
import poplib, imaplib, string, socket, time, os.path, random, sys, email.header

LOCK = QReadWriteLock()
Settings = QSettings('mailChecker','mailChecker')

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
			return probeError, countAll, countNew, NewMailAttributes

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
						return probeError, countAll, countNew, NewMailAttributes

				c = open('/dev/shm/' + accountData[0] + '.cache', 'w')
				# print mailUidls, WAIT
				c.writelines( mailUidls )
				c.close()

			elif not WAIT :
				m.quit()
				#print to_unicode(accountData[0]), '  close connect', WAIT
				return probeError, countAll, countNew, NewMailAttributes

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
			return probeError, countAll, countNew, NewMailAttributes

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
				probeError, countAll, countNew = False, 0, 0
		else:
			#print 'AuthError', WAIT
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
			Msg = 'ConnectMethod Error\n'
	else:
		Msg = 'AccountName Error\n'
	return False, 0, 0, Msg, ''

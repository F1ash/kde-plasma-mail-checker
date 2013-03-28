# -*- coding: utf-8 -*-
#  MailFunc.py
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

from imapUTF7 import imapUTF7Encode
from PyQt4.QtCore import QString, QSettings, QMutex
import poplib, imaplib, time, socket
from string import join
import re, urllib2

global ErrorMsg
ErrorMsg = ''
ModuleType = type(time)
LOCK = QMutex()
Settings = QSettings('plasmaMailChecker','plasmaMailChecker')
TIMEOUT = Settings.value('timeoutSocks', 45).toUInt()[0]
USE_PROXY = Settings.value('UseProxy', 'False').toString()

pattern = "[1-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?"
ip_re = re.compile(pattern)
CHECK_SERVICES = ('http://www.viewmyipaddress.com/', 'http://api.wipmania.com/', 'http://checkip.dyndns.org')

def getExternalIP():
	ip = ''
	reload(urllib2)
	for addr in CHECK_SERVICES :
		try :
			f = urllib2.urlopen(urllib2.Request(addr))
			response = f.read()
			f.close()
			ip_ = ip_re.findall(response)
			if ip_ == [] : continue
			ip = ip_[0]
			break
		except Exception, err:
			print '[MailFunc in getExternalIP] Error: ', str(err)
		finally : pass
	return ip

########################################################################
# see for: https://raw.github.com/athoune/imapidle/master/src/imapidle.py
def idle(connection):
	tag = connection._new_tag()
	#print dateStamp(), "%s IDLE\r\n" % tag
	connection.send("%s IDLE\r\n" % tag)
	response = connection.readline()
	#print dateStamp(), [response]
	if response == '+ idling\r\n':
		resp = connection.readline()
		#print dateStamp(), [resp]
		if resp != '' :
			uid, message = resp[2:-2].split(' ')
			return uid, message
	raise Exception("IDLE not handled? : %s." % response)

def done(connection):
	connection.send("DONE\r\n")

def setIdleMethods():
	imaplib.IMAP4.idle = idle
	imaplib.IMAP4.done = done
########################################################################

def readProxySettings(socks):
	def take_value(arg):
		return None if arg == 'None' or arg.isEmpty() else QString().fromUtf8(arg)
	_type = Settings.value('ProxyType', 'None').toString()
	if   _type == 'HTTP'   : proxytype = socks.PROXY_TYPE_HTTP
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

def loadSocketModule(loadModule = None, module = None):
	proxyLoad = False
	reload(socket)
	setattr(socket, '__reloaded__', False)
	if ( loadModule is None and USE_PROXY == 'True' ) or loadModule :
		## http://sourceforge.net/projects/socksipy/
		## or install the Fedora liked python-SocksiPy package
		try :
			import socks
			proxyLoad = True
		except : pass
		finally :
			if proxyLoad :
				socks._socket.setdefaulttimeout(TIMEOUT)
				"""setdefaultproxy(proxytype, addr[, port[, rdns[, username[, password]]]])"""
				proxytype, addr, port, rdns, username, password = readProxySettings(socks)
				#print proxytype, addr, port, rdns, username, password
				socks.setdefaultproxy(proxytype, addr, port, rdns, username, password)
				socket.socket = socks.socksocket
				setattr(socket, '__reloaded__', True)
	if type(module) == ModuleType :
		reload(module)
		setattr(module, '__reloaded__', getattr(socket, '__reloaded__'))
	# for checking proxy availability or external IP uncomment below
	#ip = getExternalIP()
	#print "External IP: %s ; Reloaded: %s" % (ip, getattr(socket, '__reloaded__'))

	return proxyLoad

def losedBlank(str_raw):
	""" append the gap to end phrase due to the fact
		that the phrase may be a composite
	"""
	STR_ = ''
	for str_ in str_raw.split(' ') :
		_str = str_.rpartition('?=')
		if _str[1] != '' and _str[2] != '' :
			STR_ += join([ _str[0], '?= ', losedBlank( _str[2] )], '') + ' '
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

def clearBlank(s):
	while s.startswith('\r') or s.startswith('\n') : s = s[1:]
	while s.endswith('\r') or s.endswith('\n') : s = s[:-1]
	return ' ' if s == '' else s

def popAuth(serv, port, login, passw, authMthd):
	go = False
	loadSocketModule(module = poplib)
	#print getattr(poplib, '__reloaded__', None), '<< -- POP3 reloaded'
	popMail = poplib.POP3_SSL if authMthd == 'SSL' else poplib.POP3
	m = popMail(serv, port)
	if m.user(login)[:3] == '+OK' :
		if m.pass_(passw)[:3] == '+OK' :
			go = True
	return m, go

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
		newMailIds = []
		m, go = popAuth(authentificationData[0], \
						authentificationData[1], \
						authentificationData[2], \
						accountData[1], \
						authentificationData[4])
		if go :
				countAll = int(m.stat()[0])
				for uidl_ in m.uidl()[1] :
					currentMailId, currentElemUid = uidl_.split()
					mailUidls.append(currentElemUid + '\n')
					if defineUIDL(accountData[0], currentElemUid) :
						newMailIds.append(currentMailId)
						From = ''
						Subj = ''
						Date = ''
						Code = ''
						Next = ''
						for str_ in m.top( int(currentMailId) , 0)[1] :
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
						NewMailAttributes += clearBlank(Date) + '\r\n' + \
											 clearBlank(From) + '\r\n' + \
											 clearBlank(Subj) + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ------'
						encoding += Code + '\n'
						#print encoding, '  encoding POP3'
						newMailExist = newMailExist or True
						countNew += 1

				c = open('/dev/shm/' + QString(accountData[0]).toUtf8().data() + '.cache', 'w')
				c.writelines( mailUidls )
				c.close()

		m.quit()

	except Exception, x:
		print dateStamp(), x, '  POP3'
		ErrorMsg += '\n' + unicode(str(x),'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew, NewMailAttributes, encoding, '-', newMailIds

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

def imapAuth(serv, port, login, passw, authMthd, inbox, idle = False):
	answer = [None, None]
	m = None
	loadSocketModule(module = imaplib)
	if idle : setIdleMethods()
	#print getattr(imaplib, '__reloaded__', None), '<< -- IMAP4 reloaded'
	try :
		if authMthd == 'SSL' :
			m = imaplib.IMAP4_SSL(serv, port)
		else :
			m = imaplib.IMAP4(serv, port)
	except Exception :
		return ('', None), m, False
	tag = m._new_tag()
	m.send("%s CAPABILITY\r\n" % tag)
	#print dateStamp(), "%s CAPABILITY\r\n" % tag
	resp = m.readline()
	serves = resp.lower().split()
	resp = m.readline()
	#print dateStamp(), serves
	#print dateStamp(), resp
	idleable = True if 'idle' in serves else False

	if m.login(login, passw)[0] == 'OK' :
		if inbox == '' :
			mailBox = 'INBOX'
		else :
			mailBox = unicode(QString(inbox).toUtf8().data(), 'utf-8')
		#print dateStamp(), mailBox, imapUTF7Encode(mailBox)
		answer = m.select(imapUTF7Encode(mailBox))
	return answer, m, idleable

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
		newMailIds = []

		answer, m, idleable = imapAuth(authentificationData[0], authentificationData[1], \
				authentificationData[2], accountData[1], \
				authentificationData[4], authentificationData[8])
		if answer[0] == 'OK' :
				countAll = int(answer[1][0])
				unSeen = countAll - len(m.search(None, 'Seen')[1][0].split())
				i = countAll
				while i > 0 :
					currentElemTime = getCurrentElemTime(m, i)
					# print dateStamp(), currentElemTime
					if currentElemTime > lastElemTime :
						newMailIds.append(str(i))
						Date, From, Subj = getMailAttributes(m, i)
						NewMailAttributes += clearBlank(Date) + '\r\n' + \
											 clearBlank(From) + '\r\n' + \
											 clearBlank(Subj) + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ----==------'
						encoding += '\n'
						newMailExist = newMailExist or True
						countNew += 1
					else:
						break
					i += -1
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
		if not (m is None) : m.logout()

		Settings.sync()

	except Exception, x :
		print dateStamp(), x, '  IMAP4'
		ErrorMsg += '\n' + unicode(str(x),'UTF-8')
		probeError = False
		countAll = 0
		countNew = 0
	finally:
		pass

	return probeError, countAll, countNew, NewMailAttributes, encoding, unSeen, newMailIds

def connectProbe(probe_ = 3, checkNewMail = None, authData = ['', ''], acc = ''):
	global ErrorMsg
	Result = False
	all_ = 0
	new_ = 0
	encoding = ''
	unSeen = '-'
	newMailIds = None
	i = 0
	while i < probe_ :
		#print dateStamp(), 'Probe ', i + 1, to_unicode(authData[0])
		test_, all_, new_, content, encoding, unSeen, newMailIds = checkNewMail(authData)
		if test_ :
			Result = True
			break
		i += 1
		if i == probe_ :
			ErrorMsg += "\nCan`t connect to server\non Account : " + to_unicode(acc) + '\n'
	#print dateStamp(), ErrorMsg, '  errors'
	ids = '' if newMailIds is None else join(newMailIds, ' ')
	return Result, all_, new_, ErrorMsg, QString(content).toUtf8(), encoding, str(unSeen), ids

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
	return False, 0, 0, Msg, '', '', '-', ''

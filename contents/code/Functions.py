# -*- coding: utf-8 -*-
#  Functions.py
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

from PyQt4.QtCore import QString, QMutex
import os, string, time, os.path, random, email.header, datetime, locale

# idle thread states
SIGNERRO = -2
SIGNSTOP = -1
SIGNINIT = 0
SIGNDATA = 1

# ports
POP3_PORT = 110
POP3_SSL_PORT = 995
IMAP4_PORT = 143
IMAP4_SSL_PORT = 993

dltHours = time.localtime().tm_hour - time.gmtime().tm_hour
dltMinutes = time.localtime().tm_min - time.gmtime().tm_min
dltLocal = datetime.timedelta(hours = dltHours, minutes = dltMinutes)

lang = locale.getdefaultlocale()
char_set = string.ascii_letters + string.digits

dlm = ' <||> '

def dataToList(path_ = ''):
	if os.path.isfile(path_) :
		with open(path_, 'rb') as f :
			l_ = f.read()
			raw_l = l_.split('\n')
			if raw_l.count('') : raw_l.remove('')
			l = []
			for item in raw_l :
				l.append(QString().fromUtf8(item))
		return l
	else :
		return []

FROM_filter = dataToList(os.path.expanduser('~/.config/plasmaMailChecker/filter.from'))
SUBJ_filter = dataToList(os.path.expanduser('~/.config/plasmaMailChecker/filter.subj'))

def Filter(text, deprecated):
	res = True
	for item in deprecated :
		#print [text, item]
		if QString(text).contains(item) :
			res = False
			break
	return res

def htmlWrapper((From_, Subj_, Date_) = ('', '', ''),
				((pref1, suff1), (pref2, suff2), (pref3, suff3)) \
				= (('', ''), ('', ''), ('', ''))) :
	if From_ is None or Subj_ is None : return None
	From_ = From_.replace('<', '&lt;')
	From_ = From_.replace('>', '&gt;')
	Subj_ = Subj_.replace('<', '&lt;')
	Subj_ = Subj_.replace('>', '&gt;')
	From = pref1 + From_ + suff1
	Subj = pref2 + Subj_ + suff2
	Date = pref3 + Date_ + suff3
	return 'From: ' + From + '<br></br>' + 'Subj: ' + Subj + '<br></br>' + 'Date: ' + Date + '<br></br>'

def utcDelta(str_):
	hours_ = int(str_[:3])
	minutes_ = int(str_[:1] + str_[-2:])
	return datetime.timedelta(hours = hours_, minutes = minutes_)

def dateFormat(str_):
	# print str_, '???'
	locale.setlocale(locale.LC_ALL, 'C')
	try:
		localTime = datetime.datetime.strptime( str_[6:30], "%a, %d %b %Y %H:%M:%S" ) - \
														utcDelta(str_[32:37]) + dltLocal
		data_ = localTime.timetuple()
		#return time.ctime(time.mktime(localTime.timetuple()))
		locale.setlocale(locale.LC_ALL, lang)
		dateSTR = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(time.mktime(data_)))
	except ValueError:
		dateSTR = 'get Date error'
	finally :
		locale.setlocale(locale.LC_ALL, lang)
	#print dateSTR
	return QString().fromUtf8(dateSTR)

def decodeMailSTR(str_, headerCode = ''):
	obj = ''
	_str = '' if str_ is None else str_.replace('"', ' &quot; ')
	for part_str in email.header.decode_header(_str) :
		try :
			if part_str[1] is None :
				_headerCode = headerCode
				if headerCode != '':
					if headerCode[:3].lower() == 'win' or headerCode[:2].lower() == 'cp' :
						_headerCode = 'cp' + headerCode[-4:]
					obj += part_str[0].decode(_headerCode) + ' '
				else :
					obj += unicode(part_str[0]) + ' '
				## print dateStamp(), ' charset=', _headerCode, ' <--- None'	##, '::', obj, '<--', part_str[0]
			else :
				_headerCode = part_str[1]
				if part_str[1][:3].lower() == 'win' or part_str[1][:2].lower() == 'cp' :
					_headerCode = 'cp' + part_str[1][-4:]
				obj += part_str[0].decode(_headerCode) + ' '
				## print dateStamp(), ' charset=', part_str[1], ' : ', _headerCode	##, '::', obj, '<--', part_str[0]
		except LookupError, err:
			print dateStamp(), err, ' : ', headerCode, '<>', part_str[1], ' <---> ', QString(part_str[0]).toUtf8().data()
			obj += part_str[0] + ' '
		except UnicodeDecodeError, err:
			print dateStamp(), err, ' : ', headerCode, '<>', part_str[1], ' <---> ', QString(part_str[0]).toUtf8().data()
			obj += QString().fromUtf8(part_str[0]) + ' '
		finally :
			pass
	return obj

def dateStamp():
	return time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime()) + ' : '

def cleanDebugOutputLogFiles(stay = 1):
	LIST = []
	uid = os.geteuid()
	for name_ in os.listdir('/tmp') :
		name = os.path.join('/tmp', name_)
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
		   str(dataToSTR(path_ + '.content')), str(dataToSTR(path_ + '.encoding')), \
		   str(dataToSTR(path_ + '.unRead')), str(dataToSTR(path_ + '.Ids'))

def randomString(j = 1):
	#return "".join( [random.choice(string.letters) for i in xrange(j)] )
	return ''.join(random.sample(char_set, j))

def to_unicode(txt, encoding = 'utf-8'):
	if isinstance(txt, basestring) :
		if not isinstance(txt, unicode) :
			txt = unicode(txt, encoding, errors = 'replace')
	return txt

class Required():
	def __init__(self, parent = None):
		self.parent = parent
		self.Settings = parent.Settings
		self.LOCK = QMutex()

	def loadSocksModule(self, loadModule = None):
		proxyLoad = False
		if ( loadModule is None and self.Settings.value('UseProxy', 'False')=='True' ) or loadModule :
			## http://sourceforge.net/projects/socksipy/
			## or install the Fedora liked python-SocksiPy package
			try :
				import socks
				proxyLoad = True
			except : pass #proxyLoad = False
			finally : pass
		return proxyLoad

	def Allowed(self, FROM = '', SUBJ = ''):
		A = Filter(FROM, FROM_filter) if self.Settings.value('FROMFilter', 'False')=='True' else True
		B = Filter(SUBJ, SUBJ_filter) if self.Settings.value('SUBJFilter', 'False')=='True' else True
		return A and B

	def readAccountData(self, account = ''):
		self.LOCK.lock()
		self.Settings.beginGroup(account)
		serv_ = self.Settings.value('server').toString()
		port_ = self.Settings.value('port').toString()
		if port_ == '' : port_ =  '0'
		login_ = self.Settings.value('login').toString()
		authMethod_ = self.Settings.value('authentificationMethod').toString()
		connMethod_ = self.Settings.value('connectMethod').toString()
		last_ = self.Settings.value('lastElemValue').toString()
		enable = self.Settings.value('Enabled').toString()
		if str(connMethod_) == 'imap' :
			inbox = self.Settings.value('Inbox').toString()
		else :
			inbox = ''
		if self.Settings.contains('CommandLine') :
			command = self.Settings.value('CommandLine').toString()
		else :
			command = ''
		self.Settings.endGroup()
		self.LOCK.unlock()
		return [str(serv_), str(port_), login_, '', \
				str(authMethod_), str(connMethod_), str(last_), str(enable), inbox, command]

	def initPOP3Cache(self):
		self.LOCK.lock()
		dir_cache = os.path.expanduser('~/.cache')
		if  not os.path.isdir(dir_cache) :
			os.mkdir(dir_cache)
		dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
		if  not os.path.isdir(dir_) :
			os.mkdir(dir_)
		for accountName in string.split( self.Settings.value('Accounts').toString(), ';' ):
			self.Settings.beginGroup(accountName)
			if self.Settings.value('connectMethod').toString() == 'pop' :
				if not os.path.isfile(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache') :
					f = open(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache', 'w')
					f.close()
				f = open(dir_ +  '/' + QString(accountName).toUtf8().data() + '.cache', 'r')
				c = open('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache', 'w')
				c.writelines(f.readlines())
				f.close()
				c.close()
			self.Settings.endGroup()
		self.LOCK.unlock()

	def savePOP3Cache(self):
		self.LOCK.lock()
		dir_ = os.path.expanduser('~/.cache/plasmaMailChecker')
		for accountName in string.split( self.Settings.value('Accounts').toString(), ';' ):
			self.Settings.beginGroup(accountName)
			if self.Settings.value('connectMethod').toString() == 'pop' :
				f = open(dir_ + '/' + QString(accountName).toUtf8().data() + '.cache', 'w')
				if os.path.isfile('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache') :
					c = open('/dev/shm/' + QString(accountName).toUtf8().data() + '.cache', 'r')
					f.writelines(c.readlines())
					c.close()
				f.close()
			self.Settings.endGroup()
		self.LOCK.unlock()

	def mailAttrToSTR(self, str_, headerCode = ''):
		From = ''
		Subj = ''
		Date = ''
		STR_= str_
		#print STR_, '\n'
		for different in ['\r\nFrom', '\r\nSubject: ', ''] :
			if different != '' :
				raw_str = string.split(STR_, different)[0]
			else :
				raw_str = STR_
			#print dateStamp(), raw_str, 'raw_str'
			_str = raw_str.replace('\r\n', '')
			if _str[:5] == 'From:' :
				From = decodeMailSTR(_str[6:], headerCode) + ' '
				#print dateStamp(), From, 'From'
			elif _str[:5] == 'Subje' :
				Subj = decodeMailSTR(_str[9:], headerCode) + ' '
				#print dateStamp(), Subj, 'Subj'
			elif _str[:5] == 'Date:' :
				Date = _str
				#print dateStamp(), Date, 'Date'
			STR_ = STR_.replace( raw_str + '\r\n', '' )
		if self.Allowed(From, Subj) : return From, Subj, dateFormat(Date)
		else : return None, None, None

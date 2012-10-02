# -*- coding: utf-8 -*-
#  MailProgExec.py
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

from Functions import dateStamp, randomString, Settings, _0_
from PyQt4.QtCore import *
import string

class MailProgExec(QThread):
	def __init__(self, obj = None, param = {}, command = '', parent = None):
		QThread.__init__(self, parent)
		if isinstance(param.keys()[0], int) :
			__str = ''
		else :
			__str = param.keys()[0]
		if command.count('integrated mail Viewer') :
			""" prepeare file with parameters """
			accName = __str
			accIds = str(param.values()[0])
			Settings.beginGroup(accName)
			serv_ = Settings.value('server').toString().toLocal8Bit().data()
			port_ = Settings.value('port').toString().toLocal8Bit().data()
			if port_ == '' : port_ =  '0'
			login_ = Settings.value('login').toString().toLocal8Bit().data()
			authMethod_ = Settings.value('authentificationMethod').toString().toLocal8Bit().data()
			connMethod_ = Settings.value('connectMethod').toString().toLocal8Bit().data()
			if str(connMethod_) == 'imap' :
				inbox = Settings.value('Inbox').toString().toLocal8Bit().data()
			else :
				inbox = ''
			Settings.endGroup()
			accPswd = parent.wallet.readPassword(accName)[1]
			if not isinstance(accPswd, basestring) :
				accPswd = accPswd.toLocal8Bit().data()
			## accName decode after accPswd for getting correct account password
			if not isinstance(accName, basestring) :
				accName = accName.toLocal8Bit().data()
			pathToViewer = parent.pathToViewer
			print dateStamp() , (accName, serv_, port_, login_, authMethod_, \
								connMethod_, inbox, accPswd, accIds)
			str_ = str(randomString(24))
			with open('/dev/shm/' + str_, 'wb') as f:
				f.write(string.join((accName, serv_, port_, login_, authMethod_, \
								connMethod_, inbox, accPswd), _0_))
			''' prepare command for integrated viewer '''
			self.command = string.join(('/usr/bin/python', pathToViewer, str_, accIds), ' ')
			print accName, accIds, command, self.command
		else :
			''' prepare command '''
			if not isinstance(__str, basestring) :
				collId = __str.toLocal8Bit().data()
			else :
				collId = __str
			itemId = str(param.values()[0])
			_command = command.replace('%dir_id', collId).replace('%mail_id', itemId)
			self.command = '' if _command == '' else '/bin/bash -c "%s"' % _command
			print collId, itemId, command, self.command

	def run(self):
		accountThread = QProcess()
		if self.command not in ['', ' ', '  ', '\n'] :
			start = accountThread.startDetached(self.command)
			print dateStamp(), QString().fromUtf8(self.command), ' start is ', start
		else :
			print dateStamp(), 'Empty command is not start'

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

from Functions import dateStamp
from PyQt4.QtCore import *

class MailProgExec(QThread):
	def __init__(self, obj = None, param = {}, command = '', parent = None):
		QThread.__init__(self, parent)
		self.collId = str(param.keys()[0])
		self.itemId = str(param.values()[0])
		self.command = command.replace('%dir_id', self.collId).replace('%mail_id', self.itemId)
		#print self.collId, self.itemId, command, self.command

	def run(self):
		accountThread = QProcess()
		if self.command not in ['', ' ', '  ', '\n'] :
			start = accountThread.startDetached('/bin/bash -c "' + self.command + '"')
			print dateStamp(), QString().fromUtf8(self.command), ' start is ', start
		else :
			print dateStamp(), 'Empty command is not start'

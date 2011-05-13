# -*- coding: utf-8 -*-

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
		if self.command not in ['', ' ', '  '] :
			start = accountThread.startDetached('/bin/bash -c "' + self.command + '"')
			print dateStamp(), QString().fromUtf8(self.command), ' start is ', start
		else :
			print dateStamp(), 'Empty command is not start'

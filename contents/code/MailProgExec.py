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
		start = accountThread.startDetached(self.command)
		print dateStamp(), self.command, ' start is ', start


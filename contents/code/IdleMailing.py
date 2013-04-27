# -*- coding: utf-8 -*-
#  IdleMailing.py
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

from PyQt4.QtCore import QThread, QTimer
from imapUTF7 import imapUTF7Encode
from MailFunc import dateStamp, getMailAttributes, getCurrentElemTime, clearBlank, imapAuth
from Functions import SIGNERRO, SIGNSTOP, SIGNINIT, SIGNDATA
from string import join
from random import randint

class IdleMailing(QThread):
	def __init__(self, data = (), parent = None):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.name = data[0]
		self.passw = data[1]
		self.runned = False
		self.timer = QTimer()
		self.Settings = self.prnt.Settings
		self.countProbe = int(self.Settings.value('CountProbe').toString())
		self.TIMEOUT = self.Settings.value('timeoutSocks', 45).toUInt()[0]
		self.readAccountData = parent.someFunctions.readAccountData

	def runIdle(self):
		self.restarting = False
		errorCount = 0
		while self.key :
			# random deviation [0-12] sec
			delay = self.TIMEOUT*1000 - randint(1, 11999)
			self.timer.setInterval(delay)
			self.timer.start()
			#print "+idle: %s <-- R; %s <-- E; %s <-- D"%(self.restarting, errorCount, delay)
			try :
				uid, msg = (None, '')
				if self.key : uid, msg = self.mail.idle()
			except Exception, err :
				if not self.restarting : errorCount += 1
				uid, msg = (None, err)
			finally : pass
			if self.timer.isActive() : self.timer.stop()
			#print dateStamp(), uid, msg, 'uid, msg'
			if msg == "EXISTS" and self.key :
				try :
					self.mail.done()
					NewMailAttributes = ''
					currentElemTime = getCurrentElemTime(self.mail, uid)
					# print dateStamp(), currentElemTime
					countAll = len(self.mail.search(None, 'All')[1][0].split())
					unSeen = countAll - len(self.mail.search(None, 'Seen')[1][0].split())
					if currentElemTime > self.lastElemTime :
						Date, From, Subj = getMailAttributes(self.mail, uid)
						NewMailAttributes += clearBlank(Date) + '\r\n' + \
											 clearBlank(From) + '\r\n' + \
											 clearBlank(Subj) + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ----==------', unSeen, countAll
						self.lastElemTime = currentElemTime
						self.Settings.beginGroup(self.name)
						self.Settings.setValue('lastElemValue', self.lastElemTime)
						self.Settings.endGroup()
						self.Settings.sync()
						# send data to main thread for change mail data & notify
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNDATA, \
														'msg': [countAll, 1, unSeen, NewMailAttributes, \
																str(uid)]})
					else :
						# send data to main thread for change mail data
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNINIT, \
														'msg': [countAll, 0, unSeen, '']})
				except Exception, err :
					# send error messasge to main thread
					self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNERRO, 'msg': err})
				finally :
					# successfull probe is clear the errorCount
					errorCount = 0
			elif self.key and not self.restarting :
				# send error messasge to main thread
				self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNERRO, 'msg': msg})
			elif self.key and self.restarting :
				self.setRestartingState(False)
				new = 0
				unSeen = 0
				countAll = 0
				try :
					new = len(self.mail.search(None, 'New')[1][0].split())
					countAll = len(self.mail.search(None, 'All')[1][0].split())
					unSeen = countAll - len(self.mail.search(None, 'Seen')[1][0].split())
					# send data to main thread for change mail data
					self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNINIT, \
													'msg': [countAll, new, unSeen, '']})
				except Exception, err : print dateStamp(), err
				finally : pass
			elif not self.key :
				print dateStamp(), 'key off'
				self.mail.done()
			# limit of errors shutdown idle thread
			if errorCount == self.countProbe :
				self.key = False
				print dateStamp(), 'errors limit '
		#
		# idle out
		self.timer.timeout.disconnect(self.restartIdle)
		print dateStamp(), self.name.toLocal8Bit().data(), 'timer stopped & disconnected'

	def setRestartingState(self, state):
		self.restarting = state

	def restartIdle(self):
		try :
			self.mail.done()
			self.setRestartingState(True)
			#print 'restart IDLE'
		except Exception, err : print dateStamp(), err
		finally : pass

	def run(self):
		self.key = True
		self.answer = []
		self.timer.timeout.connect(self.restartIdle)
		self.authentificationData = self.readAccountData(self.name)
		self.lastElemTime = self.authentificationData[6]
		newMailIds = []

		for j in xrange(self.countProbe) :
			try :
				#print 'probe', j+1
				self.answer, self.mail, idleable = imapAuth(\
						self.authentificationData[0], self.authentificationData[1], \
						self.authentificationData[2], self.passw, \
						self.authentificationData[4], self.authentificationData[8], \
						True)
				#print self.answer, self.mail, idleable
				if idleable :
					msg = "IDLE mode is available"
				else :
					msg = "IDLE mode isn`t available"
				print dateStamp(), "%s for %s" % (msg, self.name.toLocal8Bit().data())
				if not idleable :
					self.key = False
					# send unavailable notify
					self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNERRO, \
													'msg': [msg]})
					break

				if self.answer[0] == 'OK' and self.key :
						self.runned = True
						countAll = int(self.answer[1][0])
						unSeen = countAll - len(self.mail.search(None, 'Seen')[1][0].split())
						# send signal with countAll & unSeen for show init data to main thread
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNINIT, \
														'msg': [countAll, 0, unSeen, '']})
						i = countAll
						NewMailAttributes = ''
						newMailExist = False
						countNew = 0
						while i > 0 and self.key :
							currentElemTime = getCurrentElemTime(self.mail, i)
							# print dateStamp(), currentElemTime
							if currentElemTime > self.lastElemTime :
								newMailIds.append(str(i))
								Date, From, Subj = getMailAttributes(self.mail, i)
								NewMailAttributes += clearBlank(Date) + '\r\n' + \
													 clearBlank(From) + '\r\n' + \
													 clearBlank(Subj) + '\r\n\r\n'
								#print dateStamp(), NewMailAttributes, '   ----==------'
								newMailExist = newMailExist or True
								countNew += 1
							else:
								break
							i += -1
						if self.key :
							self.lastElemTime = getCurrentElemTime(self.mail, countAll)
							# print dateStamp(), self.lastElemTime
							self.Settings.beginGroup(self.name)
							self.Settings.setValue('lastElemValue', self.lastElemTime)
							self.Settings.endGroup()
							if newMailExist :
								# send data to main thread for change mail data & notify
								self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNDATA, \
																'msg': [countAll, countNew, \
																		unSeen, NewMailAttributes, \
																		join(newMailIds, ' ')]})
						break
			except Exception, err :
				print dateStamp(), err
			finally : pass

		print dateStamp(), self.name.toLocal8Bit().data(), 'is runned:', self.runned, '; crypted:', self.authentificationData[4]
		if self.key and self.runned : self.runIdle()
		self.key = False
		self._shutdown()

	def stop(self):
		self.key = False
		#print self.key, '<-- key off'
		try : self.mail.done()
		except Exception, err : print dateStamp(), err
		finally : pass

	def _shutdown(self):
		if self.answer != [] and self.answer[0] == 'OK' :
			try : self.mail.close()
			except Exception, err : print dateStamp(), err
			finally : pass
		print dateStamp(), self.name.toLocal8Bit().data(), 'dir close'
		try: self.mail.logout()
		except Exception, err : print dateStamp(), err
		finally : pass
		print dateStamp(), self.name.toLocal8Bit().data(), 'logout'
		print dateStamp(), self.name.toLocal8Bit().data(), 'thread stopped'
		self.emitStoppedSignal()

	def emitStoppedSignal(self):
		# send signal about shutdown to main thread
		self.runned = False
		self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNSTOP, 'msg': ''})

	def __del__(self):
		self.stop()
		if hasattr(self, 'm') : del self.m
		self.emitStoppedSignal()

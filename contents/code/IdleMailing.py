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

from PyQt4.QtCore import QThread, QSettings, QTimer
from imapUTF7 import imapUTF7Encode
from MailFunc import readAccountData, dateStamp, getMailAttributes, getCurrentElemTime, clearBlank
from Functions import SIGNERRO, SIGNSTOP, SIGNINIT, SIGNDATA, LOCK
import imaplib, string
from random import randint

Settings = QSettings('plasmaMailChecker','plasmaMailChecker')

#####
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

def idled(connection):
	tag = connection._new_tag()
	connection.send("%s CAPABILITY\r\n" % tag)
	#print dateStamp(), "%s CAPABILITY\r\n" % tag
	resp = connection.readline()
	serves = resp.lower().split()
	resp = connection.readline()
	#print dateStamp(), serves
	#print dateStamp(), resp
	return 'idle' in serves

imaplib.IMAP4.idle = idle
imaplib.IMAP4.done = done
imaplib.IMAP4.idled = idled
#####

TIMEOUT = 30

class IdleMailing(QThread):
	def __init__(self, data = (), parent = None):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.name = data[0]
		self.passw = data[1]
		self.runned = False
		self.timer = QTimer()
		self.countProbe = int(Settings.value('CountProbe').toString())

	def runIdle(self):
		self.restarting = False
		errorCount = 0
		while self.key :
			# random deviation [0-12] sec
			delay = TIMEOUT*1000 + randint(1, 11999)
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
						Settings.beginGroup(self.name)
						Settings.setValue('lastElemValue', self.lastElemTime)
						Settings.endGroup()
						Settings.sync()
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
		self.authentificationData = readAccountData(self.name)
		if self.authentificationData[8] == '' :
			mailBox = 'INBOX'
		else :
			mailBox = unicode(QString(self.authentificationData[8]).toUtf8().data(), 'utf-8')
		#print dateStamp(), mailBox, imapUTF7Encode(mailBox), self.countProbe
		self.lastElemTime = self.authentificationData[6]
		newMailIds = []

		for j in xrange(self.countProbe) :
			try :
				#print 'probe', j+1
				if self.authentificationData[4] == 'SSL' :
					self.mail = imaplib.IMAP4_SSL(self.authentificationData[0], self.authentificationData[1])
				else :
					self.mail = imaplib.IMAP4(self.authentificationData[0], self.authentificationData[1])
				idled = self.mail.idled()
				if idled :
					msg = "IDLE mode is available"
				else :
					msg = "IDLE mode isn`t available"
				print dateStamp(), "%s for %s" % (msg, self.name.toLocal8Bit().data())
				if not idled :
					self.key = False
					# send unavailable notify
					self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNERRO, \
													'msg': [msg]})
					break

				if self.mail.login( self.authentificationData[2], self.passw )[0] == 'OK' :
					self.answer = self.mail.select(imapUTF7Encode(mailBox))
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
							Settings.beginGroup(self.name)
							Settings.setValue('lastElemValue', self.lastElemTime)
							Settings.endGroup()
							if newMailExist :
								# send data to main thread for change mail data & notify
								self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNDATA, \
																'msg': [countAll, countNew, \
																		unSeen, NewMailAttributes, \
																		string.join(newMailIds, ' ')]})
						break
			except Exception, err :
				print dateStamp(), err
			finally : pass

		print dateStamp(), self.name.toLocal8Bit().data(), 'is runned:', self.runned, 'crypted:', self.authentificationData[4]
		if self.key and self.runned : self.runIdle()
		self.runned = False
		self.key = False
		self._shutdown()

	def stop(self):
		LOCK.lock()
		self.key = False
		#print self.key, '<-- key off'
		self.mail.done()
		LOCK.unlock()

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
		# send signal about shutdown to main thread
		self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': SIGNSTOP, 'msg': ''})

	def __del__(self):
		self.stop()

# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, QSettings
from imapUTF7 import imapUTF7Encode
from MailFunc import readAccountData, dateStamp, getMailAttributes, getCurrentElemTime
import imaplib
import time

Settings = QSettings('plasmaMailChecker','plasmaMailChecker')

#####
# see for: https://raw.github.com/athoune/imapidle/master/src/imapidle.py
def idle(connection):
	tag = connection._new_tag()
	connection.send("%s IDLE\r\n" % tag)
	response = connection.readline()
	connection.loop = True
	if response == '+ idling\r\n':
		while connection.loop:
			resp = connection.readline()
			uid, message = resp[2:-2].split(' ')
			#yield uid, message
			return uid, message
	else:
		raise Exception("IDLE not handled? : %s." % response)

def done(connection):
	connection.send("DONE\r\n")
	connection.loop = False

imaplib.IMAP4.idle = idle
imaplib.IMAP4.done = done
#####

class IdleMailing(QThread):
	def __init__(self, data = (), parent = None):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.name = data[0]
		self.passw = data[1]
		self.runned = False

	def run(self):
		self.key = True
		self.authentificationData = readAccountData(self.name)
		if self.authentificationData[8] == '' :
			mailBox = 'INBOX'
		else :
			mailBox = unicode(QString(self.authentificationData[8]).toUtf8().data(), 'utf-8')
		self.msleep(500)
		countProbe = int(Settings.value('CountProbe').toString())
		print dateStamp(), mailBox, imapUTF7Encode(mailBox), countProbe
		lastElemTime = self.authentificationData[6]
		self.msleep(500)

		for i in xrange(countProbe) :
			try :
				#print 'probe', i+1
				self.msleep(500)
				if self.authentificationData[4] == 'SSL' :
					self.mail = imaplib.IMAP4_SSL(self.authentificationData[0], self.authentificationData[1])
				else :
					self.mail = imaplib.IMAP4(self.authentificationData[0], self.authentificationData[1])

				if self.mail.login( self.authentificationData[2], self.passw )[0] == 'OK' :
					answer = self.mail.select(imapUTF7Encode(mailBox))
					if answer[0] == 'OK':
						self.runned = True
						countAll = int(answer[1][0])
						unSeen = len(self.mail.search(None, 'UnSeen')[1][0].split())
						# send signal with countAll & unSeen for show init data to main thread
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': 0, \
														'msg': [countAll, 0, unSeen, '']})
						i = countAll
						NewMailAttributes = ''
						newMailExist = False
						countNew = 0
						while i > 0 :
							currentElemTime = getCurrentElemTime(self.mail, i)
							# print dateStamp(), currentElemTime
							if currentElemTime > lastElemTime :
								Date, From, Subj = getMailAttributes(self.mail, i)
								NewMailAttributes += Date + '\r\n' + From + '\r\n' + Subj + '\r\n\r\n'
								#print dateStamp(), NewMailAttributes, '   ----==------'
								newMailExist = newMailExist or True
								countNew += 1
							else:
								break
							i += -1
						lastElemTime = getCurrentElemTime(self.mail, countAll)
						# print dateStamp(), lastElemTime
						Settings.beginGroup(self.name)
						Settings.setValue('lastElemValue', lastElemTime)
						Settings.endGroup()
						if newMailExist :
							# send data to main thread for change mail data & notify
							self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': 1, \
															'msg': [countAll, countNew, \
																	unSeen, NewMailAttributes]})
						break
			except Exception, _ :
				print dateStamp(), _
			finally : pass
		self.msleep(500)
		print dateStamp(), self.name, 'is runned && ', self.runned, 'connected', self.authentificationData[4]
		count = 0
		while self.key and self.runned and count < countProbe :
			#for uid, msg in self.mail.idle():
			try :
				uid, msg = self.mail.idle()
			except Exception, _ :
				print dateStamp(), _
				count += 1
				uid, msg = (None, _)
			finally : pass
			print dateStamp(), uid, msg, 'uid, msg'
			if msg == "EXISTS":
				try :
					self.mail.done()
					NewMailAttributes = ''
					currentElemTime = getCurrentElemTime(self.mail, uid)
					# print dateStamp(), currentElemTime
					unSeen = len(self.mail.search(None, 'UnSeen')[1][0].split())
					countAll = len(self.mail.search(None, 'All')[1][0].split())
					if currentElemTime > lastElemTime :
						Date, From, Subj = getMailAttributes(self.mail, uid)
						NewMailAttributes += Date + '\r\n' + From + '\r\n' + Subj + '\r\n\r\n'
						#print dateStamp(), NewMailAttributes, '   ----==------', unSeen, countAll
						lastElemTime = currentElemTime
						Settings.beginGroup(self.name)
						Settings.setValue('lastElemValue', lastElemTime)
						Settings.endGroup()
						Settings.sync()
						# send data to main thread for change mail data & notify
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': 1, \
														'msg': [countAll, 1, unSeen, NewMailAttributes]})
					else :
						# send data to main thread for change mail data & notify
						self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': 0, \
														'msg': [countAll, 0, unSeen, '']})
				except Exception, _ :
					# send error messasge to main thread
					self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': -2, 'msg': _})
			else :
				# send error messasge to main thread
				self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': -2, 'msg': msg})
		try :
			self.mail.done()
			if answer[0] == 'OK': self.mail.close()
		except Exception, _ :
			print dateStamp(), _
		finally : pass
		try :
			self.mail.logout()
		except Exception, _ :
			print dateStamp(), _
		finally : pass
		self.runned = False
		print dateStamp(), self.name, 'stopped'
		# send signal about shutdown to main thread
		self.prnt.idleThreadMessage.emit({'acc': self.name, 'state': -1, 'msg': ''})

	def stop(self):
		self.key = False
		self.mail.done()
		self.mail.close()
		self.mail.logout()

	def __del__(self):
		self.stop()


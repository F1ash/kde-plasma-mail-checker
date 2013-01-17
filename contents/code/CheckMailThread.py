#  CheckMailThread.py
#  
#  Copyright 2013 Flash <kaperang07@gmail.com>
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

from PyQt4.QtCore import *
from PyKDE4.kdecore import KGlobal
from Functions import randomString, pid_exists, dateStamp, readDataFiles
import os.path, signal, os

class ThreadCheckMail(QThread):
	def __init__(self, obj = None, accountData = [('', '')], timeout = 120, parent = None):
		QThread.__init__(self, parent)

		self.Parent = obj
		self.setTerminationEnabled(False)
		self.LOCK = QReadWriteLock()
		self.Timer = QTimer()
		self.Timer.setSingleShot(True)
		self.Timer.timeout.connect(self.signalToKillSelf)
		self.timeout = int(timeout) * 1000
		self.accData = accountData
		self.accountThread = []
		self.dataList = []
		self.Parent.ErrorMsg = ''
		self.WAIT = True

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/' + path_
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/' + path_
		if os.path.exists(var2) :
			return var2
		elif os.path.exists(var1) :
			return var1
		else :
			return os.path.expanduser('~/kde-plasma-mail-checker/contents/' + path_)

	def readResult(self):
		self.Parent.checkResult = []
		for i in xrange(len(self.accountThread)) :
			self.Parent.checkResult.append(readDataFiles(self.dataList[i][1]))
		#print dateStamp() ,  RESULT

	def run(self):
		try:
			x = ''
			self.Timer.start(self.timeout)
			path = self.user_or_sys('code/mail.py')
			i = 0
			for accountData in self.accData :
				if self.WAIT :
					str_ = str(randomString(24))
					with open('/dev/shm/' + str_, 'wb') as f :
						if isinstance(accountData[1], basestring) :
							_str = accountData[1]
						else :
							_str = accountData[1].toLocal8Bit().data()
						f.write(_str)
					Data = QStringList()
					Data.append(path)
					Data.append(accountData[0])
					Data.append(str_)
					self.accountThread.append('')
					self.accountThread[i] = QProcess()
					start, pid = self.accountThread[i].startDetached('/usr/bin/python', Data, os.getcwd())
					self.dataList.append((pid, str_, start))
					#print dateStamp() ,  start, pid, Data.join(' ').toUtf8().data()
				else :
					break
				i += 1

			# waiting mailcheckig processes
			key_ = True
			while key_ and self.WAIT :
				self.msleep(100)
				key_ = False
				for node in self.dataList :
					if bool(node[2]) and node[0] != 0 :
						key_ = key_ or pid_exists(node[0], 0)
						#print node[2], node[0], ' ????', key_

		except Exception, x :
			self.Timer.stop()
			print dateStamp() ,  x, '  thread'
		finally :
			self.Timer.stop()
			if self.WAIT :
				self.readResult()
				self.Parent.emit(SIGNAL('refresh'))
				self.quit()
		return

	def signalToKillSelf(self):
		self.LOCK.lockForRead()
		self.WAIT = False
		self.LOCK.unlock()
		print dateStamp() ,  self.WAIT, '  changed WAIT'
		self.Parent.ErrorMsg += 'Timeout thread error\n'
		print dateStamp() ,  'Mail thread timeout terminating...'
		#QApplication.postEvent(self.Parent, QEvent(1010))
		self._terminate()

	def _terminate(self):
		self.Timer.stop()
		self.LOCK.lockForRead()
		self.WAIT = False
		self.LOCK.unlock()
		for i in xrange(len(self.dataList)) :
			if bool(self.dataList[i][2]) and pid_exists(self.dataList[i][0], signal.SIGKILL) :
				#print dateStamp() ,  self.dataList[i][0], '  killed'
				pass
			else :
				#print dateStamp() ,  self.dataList[i][0], '  not exist'
				pass
		print dateStamp() ,  'recive signal to kill...'
		self.readResult()
		self.Parent.emit(SIGNAL('refresh'))
		self.quit()

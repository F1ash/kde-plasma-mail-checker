#  mailViewer.py
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

from MailFunc import *
from Functions import _0_
import sys, os, os.path
#from PyQt4 import QtCore
#from MailBox import MainWindow

if __name__ == '__main__':
	fileName = sys.argv[1]
	accIds = sys.argv[2:]
	if os.path.isfile('/dev/shm/' + fileName) :
		with open('/dev/shm/' + fileName, 'rb') as f: l = f.read()
		print (l), ' file'
		with open('/dev/shm/' + fileName, 'wb') as f: f.write(''.join(['' for i in xrange(len(l))]))
		os.remove('/dev/shm/' + fileName)
		while l.endswith('\n') : l.remove('\n')
		''' (accName, serv_, port_, login_, authMethod_, connMethod_, inbox, accPaswd) '''
		accName, serv_, port_, login_, authMethod_, connMethod_, inbox, accPaswd = \
			l.split(_0_)
	else :
		accName, serv_, port_, login_, authMethod_, connMethod_, inbox, accPaswd = \
			['' for i in xrange(8)]
	#print dateStamp(), (accName, serv_, port_, login_, authMethod_, connMethod_, inbox, accPaswd), '  viewer:'
	#print dateStamp(), accIds, ' uids'
	

	#app = QtGui.QApplication(sys.argv)
	#main = MainWindow()
	#sys.exit(app.exec_())

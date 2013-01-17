#  Passwd.py
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

from PyQt4.QtGui import *
from Translator import Translator

class PasswordManipulate(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('PasswordManipulate')
		self.checkAccess = self.Parent.checkAccess

		self.VBLayout = QVBoxLayout()

		self.addAccountItem = QPushButton('&New')
		self.addAccountItem.setToolTip(self.tr._translate("Create new Password"))
		self.addAccountItem.clicked.connect(self.createNewKey)
		self.VBLayout.addWidget(self.addAccountItem)

		self.setLayout(self.VBLayout)

	def createNewKey(self):
		if self.checkAccess() : self.Parent.wallet.requestChangePassword(0)

	def eventClose(self, event):
		self.prnt.done(0)

#  EditAccounts.py
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Translator import Translator
from EditList import EditList
from EditParam import EditParam

class EditAccounts(QWidget):
	edit = pyqtSignal(QListWidgetItem)
	edited = pyqtSignal()
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('EditAccounts')
		self.Settings = self.Parent.Settings
		self.checkAccess = self.Parent.checkAccess
		self.accounts  = EditList(obj, self)
		self.parameters = EditParam(self)
		self.parameters.changeSelfActivity(False)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.accounts)
		self.layout.addWidget(self.parameters)
		self.setLayout(self.layout)
		self.edit.connect(self.editEvent)
		self.edited.connect(self.editedEvent)
		self.StateChanged = False

	def editEvent(self, item):
		self.StateChanged = True
		self.accounts.changeSelfActivity(False)
		self.parameters.changeSelfActivity(True)
		self.parameters.initWidgets(item)

	def editedEvent(self):
		self.parameters.changeSelfActivity(False)
		self.accounts.changeSelfActivity(True)
		self.StateChanged = False

	def __del__(self):
		self.close()

#  SendParams.py
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

class SendParams(QWidget):
	def __init__(self, item, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings
		self.item = item
		self.setToolTip(self.tr._translate("Send mail"))

		self.layout = QVBoxLayout()
		self.layout.addWidget(QLabel('These options don`t implemented.'))

		self.setLayout(self.layout)

	def saveData(self):
		#self.Settings.beginGroup(self.item.text())
		#self.Settings.endGroup()
		pass

	def __del__(self):
		self.close()

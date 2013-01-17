#  EditParam.py
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
from ReceiveParams import ReceiveParams
from SendParams import SendParams

class EditParam(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings
		self.checkAccess = parent.checkAccess

		self.save_ = QPushButton()
		self.save_.setToolTip(self.tr._translate("Save"))
		self.save_.setFixedHeight(10)
		self.save_.clicked.connect(self.saveAccountData)

		self.cancel_ = QPushButton()
		self.cancel_.setToolTip(self.tr._translate("Cancel"))
		self.cancel_.setFixedHeight(10)
		self.cancel_.clicked.connect(self.cancel)

		self.buttons = QHBoxLayout()
		self.buttons.addWidget(self.save_)
		self.buttons.addWidget(self.cancel_)

		self.layout = QVBoxLayout()
		self.layout.addLayout(self.buttons)
		self.setLayout(self.layout)

	def changeSelfActivity(self, state = True):
		self.setEnabled(state)

	def initWidgets(self, item):
		self.split = QSplitter()
		self.receiveParams = ReceiveParams(item, self)
		self.sendParams = SendParams(item, self)
		self.split.addWidget(self.receiveParams)
		self.split.addWidget(self.sendParams)
		self.layout.insertWidget(0, self.split)
		self.setLayout(self.layout)

	def clearParamArea(self):
		self.split.setVisible(False)
		self.layout.takeAt(0)
		self.setLayout(self.layout)
		del self.receiveParams
		del self.sendParams
		del self.split
		self.receiveParams = None
		self.sendParams = None
		self.split = None

	def cancel(self):
		self.clearParamArea()
		self.Parent.edited.emit()

	def saveAccountData(self):
		if hasattr(self, 'receiveParams') : self.receiveParams.saveData()
		if hasattr(self, 'sendParams')    : self.sendParams.saveData()
		# data saved
		self.clearParamArea()
		self.Parent.edited.emit()

	def __del__(self):
		self.close()

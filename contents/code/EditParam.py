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
from ColorSets import ColorButton
from EditParamOBJ import EditParamOBJ

class EditParam(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings

		self.save_ = QPushButton()
		self.save_.setToolTip(self.tr._translate("Save"))
		self.save_.setFixedHeight(10)
		self.save_.clicked.connect(self.saveAccountData)

		self.saveColor = ColorButton('Save')
		self.saveColor.setToolTip(self.tr._translate("Save Color Set"))
		self.saveColor.setFixedSize(24, 10)

		self.cancelColor = ColorButton('Cancel')
		self.cancelColor.setToolTip(self.tr._translate("Cancel Color Set"))
		self.cancelColor.setFixedSize(24, 10)

		self.cancel_ = QPushButton()
		self.cancel_.setToolTip(self.tr._translate("Cancel"))
		self.cancel_.setFixedHeight(10)
		self.cancel_.clicked.connect(self.cancel)

		self.buttons = QHBoxLayout()
		self.buttons.addWidget(self.save_)
		self.buttons.addWidget(self.saveColor)
		self.buttons.addWidget(self.cancelColor)
		self.buttons.addWidget(self.cancel_)

		self.layout = QVBoxLayout()
		self.layout.addLayout(self.buttons)
		self.setLayout(self.layout)

		# init OBJ-methods
		OBJ = EditParamOBJ(self)
		self.initColor = OBJ.initColor
		self.setButtonColor = OBJ.setButtonColor
		self.blink = OBJ.blink
		self.emitEditedSignal = OBJ.emitEditedSignal
		self.changeSelfActivity = OBJ.changeSelfActivity

		# connect SLOTs after OBJ-init
		self.saveColor.colorSettings.connect(self.setButtonColor)
		self.cancelColor.colorSettings.connect(self.setButtonColor)
		self.initColor()

	def initWidgets(self, item):
		self.split = QSplitter()
		self.receiveParams = ReceiveParams(item, self)
		self.sendParams = SendParams(item, self)
		self.split.addWidget(self.receiveParams)
		self.split.addWidget(self.sendParams)
		self.layout.insertWidget(0, self.split)
		self.setLayout(self.layout)

	def clearParamArea(self):
		if hasattr(self, 'split') :
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
		self.blink(False, True)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def saveAccountData(self):
		if hasattr(self, 'receiveParams') : self.receiveParams.saveData()
		if hasattr(self, 'sendParams')    : self.sendParams.saveData()
		# data saved
		self.blink(True, False)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def __del__(self):
		self.close()

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
	blinked = pyqtSignal()
	saveStyle = pyqtSignal(tuple)
	cancelStyle = pyqtSignal(tuple)
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
		self.saveStyle.connect(self.setSaveStyle)
		self.cancelStyle.connect(self.setCancelStyle)
		self.blinked.connect(self.emitEditedSignal)

	def blink(self, i = 0, left = True, right = True):
		self.da = float(33-189)/200
		self.db = float(239-255)/200
		self.dc = float(68-21)/200
		self.dd = float(i-255)/200
		self.de = float(232-255)/200
		self.df = float(51-168)/200
		self.dg = float(25-5)/200
		self.dh = float(i-255)/200
		self.k = 0
		self.both = (left, right)
		self.newParams()

	def newParams(self):
		if self.k<200 :
			if self.both[0] :
				seq1 = (189 + int(self.k*self.da), \
						255 + int(self.k*self.db), \
						21 + int(self.k*self.dc), \
						255 + int(self.k*self.dd))
			if self.both[1] :
				seq2 = (255 + int(self.k*self.de), \
						168 + int(self.k*self.df), \
						5 + int(self.k*self.dg), \
						255 + int(self.k*self.dh))

			if self.both[0] : self.saveStyle.emit(seq1)
			if self.both[1] : self.cancelStyle.emit(seq2)
			self.k += 1
			QTimer.singleShot(1, self.newParams)
		else :
			self.blinked.emit()

	def emitEditedSignal(self):
		if not( self.both[0] and self.both[1] ) :
			self.clearParamArea()
			self.Parent.edited.emit()

	def changeSelfActivity(self, state = True):
		self.setEnabled(state)
		if state :
			brightness = 128
		else :
			brightness = 32
		self.blink(brightness)

	def setSaveStyle(self, param):
		self.save_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % param)

	def setCancelStyle(self, param):
		self.cancel_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % param)

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
		self.blink(32, False, True)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def saveAccountData(self):
		if hasattr(self, 'receiveParams') : self.receiveParams.saveData()
		if hasattr(self, 'sendParams')    : self.sendParams.saveData()
		# data saved
		self.blink(32, True, False)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def __del__(self):
		self.close()

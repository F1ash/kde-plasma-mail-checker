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
from ColorSets import ColorSets, ColorButton

class EditParam(QWidget):
	blinked = pyqtSignal()
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
		self.saveColor.colorSettings.connect(self.setButtonColor)

		self.cancelColor = ColorButton('Cancel')
		self.cancelColor.setToolTip(self.tr._translate("Cancel Color Set"))
		self.cancelColor.setFixedSize(24, 10)
		self.cancelColor.colorSettings.connect(self.setButtonColor)

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
		self.blinked.connect(self.editComplete)
		self.initColor()

	def initColor(self):
		self.startColorSave = self.Settings.value(self.saveColor.name+'StartColor', 0).toUInt()[0]
		self.endColorSave = self.Settings.value(self.saveColor.name+'EndColor', 0).toUInt()[0]
		self.startColorCancel = self.Settings.value(self.cancelColor.name+'StartColor', 0).toUInt()[0]
		self.endColorCancel = self.Settings.value(self.cancelColor.name+'EndColor', 0).toUInt()[0]

	def setButtonColor(self, button):
		print 'Colors of ', button.name, button.styleSheet()
		setColor = ColorSets(button.name, self)
		setColor.exec_()
		self.initColor()
		self.blink()

	def blink(self, left = True, right = True):
		self.rgba1 = QColor().fromRgba(self.startColorSave).getRgb()
		self.rgba2 = QColor().fromRgba(self.endColorSave).getRgb()
		self.rgba3 = QColor().fromRgba(self.startColorCancel).getRgb()
		self.rgba4 = QColor().fromRgba(self.endColorCancel).getRgb()
		# end value - start value
		self.da = float(self.rgba2[0]-self.rgba1[0])/200
		self.db = float(self.rgba2[1]-self.rgba1[1])/200
		self.dc = float(self.rgba2[2]-self.rgba1[2])/200
		self.dd = float(self.rgba2[3]-self.rgba1[3])/200
		self.de = float(self.rgba4[0]-self.rgba3[0])/200
		self.df = float(self.rgba4[1]-self.rgba3[1])/200
		self.dg = float(self.rgba4[2]-self.rgba3[2])/200
		self.dh = float(self.rgba4[3]-self.rgba3[3])/200
		self.k = 0
		self.both = (left, right)
		self.nextParams()

	def nextParams(self):
		if self.k<200 :
			if self.both[0] :
				# start value + iteration * different
				seq1 = (self.rgba1[0] + int(self.k*self.da), \
						self.rgba1[1] + int(self.k*self.db), \
						self.rgba1[2] + int(self.k*self.dc), \
						self.rgba1[3] + int(self.k*self.dd))
			if self.both[1] :
				# start value + iteration * different
				seq2 = (self.rgba3[0] + int(self.k*self.de), \
						self.rgba3[1] + int(self.k*self.df), \
						self.rgba3[2] + int(self.k*self.dg), \
						self.rgba3[3] + int(self.k*self.dh))

			if self.both[0] :
				self.save_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq1)
			if self.both[1] :
				self.cancel_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq2)
			self.k += 1
			QTimer.singleShot(2, self.nextParams)
		else :
			self.blinked.emit()

	def editComplete(self):
		if not( self.both[0] and self.both[1] ) :
			QTimer.singleShot(250, self.emitEditedSignal)
	def emitEditedSignal(self):
		self.clearParamArea()
		self.Parent.edited.emit()

	def changeSelfActivity(self, state = True):
		self.setEnabled(state)
		if state : brightness = 128
		else : brightness = 32
		self.blink()
		style = 'QPushButton { background: rgba(128, 128, 128, %s); }' % brightness
		self.saveColor.setStyleSheet(style)
		self.cancelColor.setStyleSheet(style)
		rbga2_3 = self.rgba2[3] if state else self.rgba2[3]/4
		rbga4_3 = self.rgba4[3] if state else self.rgba4[3]/4
		seq1 = (self.rgba2[0], self.rgba2[1], self.rgba2[2], rbga2_3)
		seq2 = (self.rgba4[0], self.rgba4[1], self.rgba4[2], rbga4_3)
		self.save_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq1)
		self.cancel_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq2)

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

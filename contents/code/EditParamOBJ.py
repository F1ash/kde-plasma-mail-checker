#  EditParamOBJ.py
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

from ColorSets import ColorSets, COLOR
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QObject, QTimer, pyqtSignal

class EditParamOBJ(QObject):
	blinked = pyqtSignal()
	def __init__(self, parent):
		QObject.__init__(self, parent)
		self.Parent = parent
		self.Parent.setMinimumWidth(48)
		self.Settings = parent.Settings
		self.saveColor = parent.saveColor
		self.cancelColor = parent.cancelColor
		self.blinked.connect(self.editComplete)

	def initColor(self):
		self.startColorSave = self.Settings.value(self.saveColor.name+'StartColor', COLOR[21]).toUInt()[0]
		self.endColorSave = self.Settings.value(self.saveColor.name+'EndColor', COLOR[20]).toUInt()[0]
		self.startColorCancel = self.Settings.value(self.cancelColor.name+'StartColor', COLOR[11]).toUInt()[0]
		self.endColorCancel = self.Settings.value(self.cancelColor.name+'EndColor', COLOR[10]).toUInt()[0]

	def setButtonColor(self, button):
		#print 'Colors of ', button.name, button.styleSheet()
		setColor = ColorSets(button.name, self.Parent)
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
				self.Parent.save_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq1)
			if self.both[1] :
				self.Parent.cancel_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq2)
			self.k += 1
			QTimer.singleShot(2, self.nextParams)
		else :
			self.blinked.emit()

	def editComplete(self):
		if not( self.both[0] and self.both[1] ) :
			QTimer.singleShot(250, self.emitEditedSignal)
	def emitEditedSignal(self):
		self.Parent.clearParamArea()
		self.Parent.Parent.edited.emit()

	def changeSelfActivity(self, state = True):
		self.Parent.setEnabled(state)
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
		self.Parent.save_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq1)
		self.Parent.cancel_.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq2)

#  ColorSets.py
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
from PyQt4.QtCore import *

COLOR = {11:3774864640, 10:2180972544, 21:3741315843, 20:2483092480}

class ColorButton(QPushButton):
	colorSettings = pyqtSignal(object)
	def __init__(self, name, parent = None):
		QPushButton.__init__(self, parent)
		self.name = name
		self.setAutoDefault(False)
		self.clicked.connect(self.emitClickedSignal)

	def emitClickedSignal(self):
		self.colorSettings.emit(self)

class ColorSets(QDialog):
	def __init__(self, name, parent = None):
		QDialog.__init__(self, parent)
		self.Parent = parent
		self.name = name
		self.Settings = parent.Settings
		startDefault = COLOR[11] if name == 'Cancel' else COLOR[21]
		endDefault = COLOR[10] if name == 'Cancel' else COLOR[20]
		self.startColorValue = self.Settings.value(name+'StartColor', startDefault).toUInt()[0]
		self.endColorValue = self.Settings.value(name+'EndColor', endDefault).toUInt()[0]
		#print [self.startColorValue, self.endColorValue, name, self.Settings.value(name+'StartColor', 0)]
		self.layout = QGridLayout()

		self.startColor = ColorButton(self.name + 'StartColor')
		self.endColor   = ColorButton(self.name + 'EndColor')
		self.startColor.setToolTip(self.Parent.tr._translate("Start Color"))
		self.endColor.setToolTip(self.Parent.tr._translate("End Color"))
		self.initDifference(self.startColor, self.startColorValue)
		self.initDifference(self.endColor, self.endColorValue)
		self.startColor.colorSettings.connect(self.getColor)
		self.endColor.colorSettings.connect(self.getColor)

		self.save = QPushButton()
		self.save.setToolTip(self.Parent.tr._translate("Save"))
		self.save.setFixedWidth(10)
		self.save.clicked.connect(self.saveColor)

		self.probe = QPushButton(self.Parent.tr._translate("Probe"))
		self.probe.clicked.connect(self.blink)

		self.layout.addWidget(self.startColor, 0, 0)
		self.layout.addWidget(self.endColor, 1, 0)
		self.layout.addWidget(self.save, 0, 1, 3, 2)
		self.layout.addWidget(self.probe, 2, 0)

		self.setLayout(self.layout)

	def getColor(self, button):
		colour = QColorDialog()
		if button.name.endswith('StartColor') :
			selectColour = colour.getRgba(self.startColorValue)
		else :
			selectColour = colour.getRgba(self.endColorValue)
		colour.done(0)
		if not selectColour[1] : return None
		#print selectColour[0], button.name
		self.initDifference(button, selectColour[0])

	def initDifference(self, button, colorValue):
		rgba = QColor().fromRgba(colorValue).getRgb()
		button.setStyleSheet('QPushButton {background: rgba' + str(rgba) + ';}')
		if button.name.endswith('StartColor') :
			self.startColorValue = colorValue
			self.sR = rgba[0]
			self.sG = rgba[1]
			self.sB = rgba[2]
			self.sA = rgba[3]
		else :
			self.endColorValue = colorValue
			self.eR = rgba[0]
			self.eG = rgba[1]
			self.eB = rgba[2]
			self.eA = rgba[3]

	def blink(self):
		try :
			# end value - start value
			self.dR = float(self.eR - self.sR)/200
			self.dG = float(self.eG - self.sG)/200
			self.dB = float(self.eB - self.sB)/200
			self.dA = float(self.eA - self.sA)/200
			self.k = 0
			self.nextParams()
		except Exception : return
		finally : pass

	def nextParams(self):
		if self.k<200 :
			# start value + iteration * different
			seq  = (self.sR + int(self.k*self.dR), \
					self.sG + int(self.k*self.dG), \
					self.sB + int(self.k*self.dB), \
					self.sA + int(self.k*self.dA))

			self.probe.setStyleSheet('QPushButton { background: rgba(%s, %s, %s, %s); }' % seq)
			self.k += 1
			QTimer.singleShot(2, self.nextParams)

	def saveColor(self):
		self.Settings.setValue(self.name+'StartColor', self.startColorValue)
		self.Settings.setValue(self.name+'EndColor', self.endColorValue)

	def __del__(self): self.close()

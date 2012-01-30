# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Functions import Settings

class ButtonPanel(QWidget):
	def __init__(self, id_, parent = None):
		QWidget.__init__(self, parent)

		self.prnt = parent
		self.tr = self.prnt.tr
		self.id_ = id_
		self.Settings = Settings
		self.layout = QVBoxLayout()

		self.enabledBox = QCheckBox()
		self.enabledBox.setToolTip(self.tr._translate("Enable\Disable the Filter"))
		value = 'SUBJFilter' if self.id_ else 'FROMFilter'
		self.Enabled = self.Settings.value(value, 'False').toBool()
		if self.Enabled : self.enabledBox.setCheckState(Qt.Checked)
		else : self.enabledBox.setCheckState(Qt.Unchecked)
		self.enabledBox.stateChanged.connect(self.activate)
		self.layout.addWidget(self.enabledBox, 0, Qt.AlignHCenter)

		self.addButton = QPushButton(('&Add'))
		self.addButton.setMaximumWidth(40)
		self.addButton.setToolTip(self.tr._translate("Add to Filter"))
		self.addButton.clicked.connect(self.addItem)
		self.layout.addWidget(self.addButton, 0,  Qt.AlignHCenter)

		self.delButton = QPushButton(('&Del'))
		self.delButton.setMaximumWidth(40)
		self.delButton.setToolTip(self.tr._translate("Delete from Filter"))
		self.delButton.clicked.connect(self.delItem)
		self.layout.addWidget(self.delButton, 0, Qt.AlignHCenter)

		self.saveButton = QPushButton(('&Save'))
		self.saveButton.setMaximumWidth(40)
		self.saveButton.setToolTip(self.tr._translate("Save the filters"))
		self.saveButton.clicked.connect(self.saveFilter)
		self.layout.addWidget(self.saveButton, 0, Qt.AlignHCenter)

		self.setLayout(self.layout)

	def addItem(self):
		self.prnt.addItem(self.id_)

	def delItem(self):
		self.prnt.delItem(self.id_)

	def saveFilter(self):
		self.prnt.saveFilter(self.id_)

	def activate(self, state):
		value = 'SUBJFilter' if self.id_ else 'FROMFilter'
		self.Settings.setValue(value, 'True' if state else 'False')
		if state : self.prnt.enableSide(self.id_)
		else : self.prnt.disableSide(self.id_)

	def setCurrentState(self):
		if self.Enabled : self.activate(True)
		else : self.activate(False)

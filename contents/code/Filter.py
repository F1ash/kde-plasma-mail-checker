# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Buttons import ButtonPanel
from Translator import Translator
from Functions import dataToList, FROM_filter, SUBJ_filter
import os.path, string

def saveListToFile(l, path):
	with open(path, 'wb') as f :
		f.write(string.join(l, '\n'))

class Filters(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('Filters')
		dir_ = os.path.expanduser('~/.config/plasmaMailChecker')

		self.filterFROM = os.path.join(dir_, 'filter.from')
		self.filterSUBJ = os.path.join(dir_, 'filter.subj')
		i = 0
		for path in (self.filterFROM, self.filterSUBJ) :
			if not os.path.isfile(path) :
				name = self.filterSUBJ if i else self.filterFROM
				with open(name, 'wb') as f : pass
				#print path, 'not exist'
			i += 1

		self.listFROM = dataToList(self.filterFROM)
		self.listSUBJ = dataToList(self.filterSUBJ)

		self.layout = QGridLayout()
		self.layout.setSpacing(0)

		self.labelFROM = QLabel(self.tr._translate("FROM field"))
		self.labelSUBJ = QLabel(self.tr._translate("SUBJ field"))
		self.layout.addWidget(self.labelFROM, 0, 1,  Qt.AlignHCenter)
		self.layout.addWidget(self.labelSUBJ, 0, 2,  Qt.AlignHCenter)

		self.fromEditor = QLineEdit()
		self.subjEditor = QLineEdit()
		self.fromListBox = QListWidget()
		self.fromListBox.setSortingEnabled(True)
		self.fromListBox.setToolTip(self.tr._translate("Filter`s strings"))
		self.fromListBox.addItems(self.listFROM)
		self.subjListBox = QListWidget()
		self.subjListBox.setSortingEnabled(True)
		self.subjListBox.setToolTip(self.tr._translate("Filter`s strings"))
		self.subjListBox.addItems(self.listSUBJ)

		self.layout.addWidget(self.fromEditor, 1, 1)
		self.layout.addWidget(self.subjEditor, 1, 2)
		self.layout.addWidget(self.fromListBox, 2, 1)
		self.layout.addWidget(self.subjListBox, 2, 2)

		self.buttonFROM = ButtonPanel(0, self)
		self.buttonSUBJ = ButtonPanel(1, self)
		self.layout.addWidget(self.buttonFROM, 2, 0)
		self.layout.addWidget(self.buttonSUBJ, 2, 3)
		self.setLayout(self.layout)
		self.buttonFROM.setCurrentState()
		self.buttonSUBJ.setCurrentState()

	def addItem(self, id_):
		if id_ :
			text = self.subjEditor.text()
			text_ = unicode(QString().fromUtf8(text)).split()
			if len(text_) : self.subjListBox.addItem(text)
			self.subjEditor.clear()
		else :
			text = self.fromEditor.text()
			text_ = unicode(QString().fromUtf8(text)).split()
			if len(text_) : self.fromListBox.addItem(text)
			self.fromEditor.clear()

	def delItem(self, id_):
		if id_ :
			item_ = self.subjListBox.currentRow()
			self.subjListBox.takeItem(item_)
		else :
			item_ = self.fromListBox.currentRow()
			self.fromListBox.takeItem(item_)

	def saveFilter(self, id_):
		if id_ :
			i = 0
			filter_ = []
			while i < self.subjListBox.count() :
				filter_.append(self.subjListBox.item(i).text().toUtf8().data())
				#print unicode(QString().fromUtf8(self.subjListBox.item(i).text()))
				i += 1
			saveListToFile(filter_, self.filterSUBJ)
			SUBJ_filter = dataToList(self.filterSUBJ)
		else :
			i = 0
			filter_ = []
			while i < self.fromListBox.count() :
				filter_.append(self.fromListBox.item(i).text().toUtf8().data())
				#print unicode(QString().fromUtf8(self.fromListBox.item(i).text()))
				i += 1
			saveListToFile(filter_, self.filterFROM)
			FROM_filter = dataToList(self.filterFROM)

	def activateSide(self, id_, state = False):
		if id_ :
			self.buttonSUBJ.addButton.setEnabled(state)
			self.buttonSUBJ.delButton.setEnabled(state)
			self.buttonSUBJ.saveButton.setEnabled(state)
			self.subjEditor.setEnabled(state)
			self.subjListBox.setEnabled(state)
		else :
			self.buttonFROM.addButton.setEnabled(state)
			self.buttonFROM.delButton.setEnabled(state)
			self.buttonFROM.saveButton.setEnabled(state)
			self.fromEditor.setEnabled(state)
			self.fromListBox.setEnabled(state)

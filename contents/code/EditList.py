#  EditList.py
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

class EditList(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = parent.tr
		self.Settings = parent.Settings
		self.checkAccess = self.Parent.checkAccess
		self.accountList = QStringList()
		self.renamedItem = None

		self.layout = QGridLayout()
		self.layout.setSpacing(0)

		self.stringEditor = QLineEdit()
		self.stringEditor.setToolTip(self.tr._translate("Account name"))
		self.stringEditor.setPlaceholderText(self.tr._translate("Enter Account Name for Add to List"))
		self.accountListBox = QListWidget()
		self.accountListBox.setSortingEnabled(True)
		self.accountListBox.itemDoubleClicked.connect(self.renameItem)
		self.accountListBox.setToolTip(self.tr._translate("Accounts"))
		for accountName in self.Settings.childGroups() :
			if accountName != 'Akonadi account' :
				item = QListWidgetItem(accountName)
				item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
				self.accountListBox.addItem(item)
				self.accountList.append(accountName)

		self.addAccountItem = QPushButton(QIcon().fromTheme('list-add'), '&Add')
		self.addAccountItem.setToolTip(self.tr._translate("Add new Account"))
		self.addAccountItem.clicked.connect(self.addItem)

		self.editAccountItem = QPushButton(QIcon().fromTheme('document-edit'), '&Edit')
		self.editAccountItem.setToolTip(self.tr._translate("Edit current Account"))
		self.editAccountItem.clicked.connect(self.editItem)

		self.delAccountItem = QPushButton(QIcon().fromTheme('list-remove'), '&Del')
		self.delAccountItem.setToolTip(self.tr._translate("Delete current Account"))
		self.delAccountItem.clicked.connect(self.delItem)

		self.VBLayout = QVBoxLayout()
		self.VBLayout.addWidget(self.addAccountItem)
		self.VBLayout.addWidget(self.editAccountItem)
		self.VBLayout.addWidget(self.delAccountItem)

		self.layout.addWidget(self.stringEditor, 0, 0)
		self.layout.addWidget(self.accountListBox, 1, 0)
		self.layout.addLayout(self.VBLayout, 1, 1, 1, 2)
		self.setLayout(self.layout)

	def addItem(self):
		if self.checkAccess() :
			text = self.stringEditor.text()
			if not text.isEmpty() :
				exist = False
				for i in xrange(self.accountListBox.count()) :
					if text == self.accountListBox.item(i).text() :
						exist = True
						break
				if exist :
					QMessageBox.information(self, "ADD NAME",
						self.tr._translate('Name exist already.'))
					return None
				item = QListWidgetItem(text)
				item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
				self.accountListBox.addItem(item)
				self.Settings.beginGroup(text)
				self.Settings.setValue('server', '')
				self.Settings.endGroup()
				accList = self.Settings.value('Accounts').toString()
				accList_ = accList.split(';')
				accList_.removeAll('')
				accList_.append(text)
				accList = accList_.join(';')
				self.Settings.setValue('Accounts', accList)
				# edit new account
				self.accountListBox.setCurrentItem(item)
				self.editItem()
			else :
				# blink string Editor
				self.blinked = self.stringEditor
				self.currentStyle = self.stringEditor.styleSheet()
				self.counter = 0
				self.timer = self.startTimer(40)
				QMessageBox.information(self, "ADD NAME",
					self.tr._translate('Name is empty.'))
			self.stringEditor.clear()

	def timerEvent(self, ev):
		if self.timer == ev.timerId() :
			self.counter += 25
			if self.counter <= 512 :
				i = self.counter - 256 if self.counter>255 else self.counter
				self.blinked.setStyleSheet("QWidget {background: rgba(%s,%s,%s,128);}"%(i, i, i))
			else :
				self.killTimer(self.timer)
				self.blinked.setStyleSheet(self.currentStyle)
				self.counter = 0
				self.blinked = None

	def renameItem(self, item):
		if not self.checkAccess() : return None
		count = self.accountListBox.count()
		if item is not None :
			if self.renamedItem is None :
				self.prnt.StateChanged = True
				self.renamedItem = item.text()
				self.buttonState(False)
				i = 0
				while i < count :
					item_ = self.accountListBox.item(i)
					if item_ != item : item_.setFlags(Qt.NoItemFlags)
					i += 1
				self.accountListBox.openPersistentEditor(item)
			else :
				self.accountListBox.closePersistentEditor(item)
				if self.renamedItem in self.Settings.childGroups() :
					# swapping data for rename
					self.Settings.beginGroup(self.renamedItem)
					Keys = self.Settings.allKeys()
					self.Settings.endGroup()
					for key in Keys :
						self.Settings.beginGroup(self.renamedItem)
						value = self.Settings.value(key)
						self.Settings.endGroup()
						self.Settings.beginGroup(item.text())
						self.Settings.setValue(key, value)
						self.Settings.endGroup()
					# uncomment below for remove available
					self.Settings.remove(self.renamedItem)
					self.accountList.append(self.renamedItem)
					self.accountList.append(item.text())
					accList = self.Settings.value('Accounts').toString()
					accList.replace(self.renamedItem, item.text())
					self.Settings.setValue('Accounts', accList)
					QMessageBox.information(self, "RENAME", self.renamedItem)
					print self.renamedItem.toLocal8Bit().data()
				else :
					QMessageBox.information(self, "RENAME", \
						self.tr._translate('Rename is fail.'))
				self.renamedItem = None
				i = 0
				while i < count :
					item_ = self.accountListBox.item(i)
					if item_ != item :
						item_.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
					i += 1
				self.buttonState(True)
				self.prnt.StateChanged = False

	def delItem(self):
		if not self.checkAccess() : return None
		item = self.accountListBox.currentItem()
		if item is None :
			text = self.tr._translate('Account not selected.')
			# blink Account List Widget
			self.blinked = self.accountListBox
			self.currentStyle = self.accountListBox.styleSheet()
			self.counter = 0
			self.timer = self.startTimer(40)
		else :
			answer = QMessageBox.question (self, \
					 "DELETE", \
					 self.tr._translate('You sure?'), \
					 self.tr._translate('Yes'), \
					 self.tr._translate('Reject'))
			if answer : return None
			text = item.text()
			# uncomment below for remove available
			self.Settings.remove(item.text())
			row = self.accountListBox.row(item)
			self.accountListBox.takeItem(row)
			accList = self.Settings.value('Accounts').toString()
			accList_ = accList.split(';')
			accList_.removeAll('')
			accList_.removeAll(text)
			accList = accList_.join(';')
			self.Settings.setValue('Accounts', accList)
			text += self.tr._translate(" deleted.")
		QMessageBox.information(self, "DELETE", text)

	def editItem(self):
		if self.checkAccess() :
			item = self.accountListBox.currentItem()
			if item is None :
				text = self.tr._translate('Account not selected.')
				# blink Account List Widget
				self.blinked = self.accountListBox
				self.currentStyle = self.accountListBox.styleSheet()
				self.counter = 0
				self.timer = self.startTimer(40)
				QMessageBox.information(self, "EDIT", text)
			else :
				#text = item.text()
				self.prnt.edit.emit(item)

	def changeSelfActivity(self, state = True):
		self.setEnabled(state)

	def buttonState(self, state):
		self.addAccountItem.setEnabled(state)
		self.editAccountItem.setEnabled(state)
		self.delAccountItem.setEnabled(state)

	def __del__(self):
		self.close()

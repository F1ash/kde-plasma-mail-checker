#  AkonadiResources.py
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

from Functions import dateStamp, dlm
from PyQt4.QtGui import *
from PyQt4.QtCore import QStringList, Qt, pyqtSignal
import AkonadiMod as A
from Translator import Translator
from ColorSets import ColorButton
from EditParamOBJ import EditParamOBJ

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
		self.accountListBox = QListWidget()
		self.accountListBox.setSortingEnabled(True)
		self.accountListBox.itemDoubleClicked.connect(self.renameItem)
		self.accountListBox.setToolTip(self.tr._translate("Accounts"))
		self.Settings.beginGroup('Akonadi account')
		for accountName in self.Settings.allKeys() :
			item = QListWidgetItem(accountName)
			item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.accountListBox.addItem(item)
			self.accountList.append(accountName)
		self.Settings.endGroup()

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

		self.layout.addWidget(self.accountListBox, 0, 0)
		self.layout.addWidget(self.stringEditor, 1, 0)
		self.layout.addLayout(self.VBLayout, 0, 1, 1, 2)
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
				self.Settings.beginGroup('Akonadi account')
				self.Settings.setValue(text, '')
				self.Settings.endGroup()
			self.stringEditor.clear()

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
				self.Settings.beginGroup('Akonadi account')
				if self.renamedItem in self.Settings.allKeys() :
					# swapping data for rename
					value = self.Settings.value(self.renamedItem)
					self.Settings.setValue(item.text(), value)
					# uncomment below for remove available
					self.Settings.remove(self.renamedItem)
					QMessageBox.information(self, "RENAME", self.renamedItem)
					print self.renamedItem.toLocal8Bit().data()
				else :
					QMessageBox.information(self, "RENAME", \
						self.tr._translate('Rename is fail.'))
				self.Settings.endGroup()
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
		else :
			text = item.text() + self.tr._translate(" deleted.")
			# uncomment below for remove available
			self.Settings.beginGroup('Akonadi account')
			self.Settings.remove(item.text())
			self.Settings.endGroup()
			row = self.accountListBox.row(item)
			self.accountListBox.takeItem(row)
		QMessageBox.information(self, "DELETE", text)

	def editItem(self):
		if self.checkAccess() :
			item = self.accountListBox.currentItem()
			if item is None :
				text = self.tr._translate('Account not selected.')
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

class EditParam(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings

		self.layout = QGridLayout()

		self.collectionIDLabel = QLabel()
		self.collectionIDLabel.setText(self.tr._translate('Collection :'))
		self.layout.addWidget(self.collectionIDLabel, 0, 0)

		self.collectionID = QLabel()
		self.collectionID.setText('-- "" --')
		self.layout.addWidget(self.collectionID, 0, 1)

		self.collectionResource = QLabel()
		self.collectionResource.setText('-- "" --')
		self.layout.addWidget(self.collectionResource, 0, 2)

		self.accountCommand = QLineEdit()
		self.layout.addWidget(self.accountCommand, 2, 1, 2, 4)

		self.collectionChoice = QLabel()
		self.collectionChoice.setText(self.tr._translate('Search:'))
		self.layout.addWidget(self.collectionChoice, 1, 0)

		self.searchColl = QPushButton('...')
		self.searchColl.clicked.connect(self.Parent.collectionSearch)
		self.layout.addWidget(self.searchColl, 1, 1)

		self.enableLabel = QLabel(self.tr._translate("Enable : "))
		self.layout.addWidget(self.enableLabel, 0, 4)

		self.enabledBox = QCheckBox()
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.layout.addWidget(self.enabledBox, 1, 4, Qt.AlignHCenter)

		self.accountCommandLabel = QLabel()
		self.accountCommandLabel.setText(self.tr._translate('Account Command:'))
		self.accountCommandLabel.setToolTip('Exec command activated in notification.\nExample: \n' + \
						'qdbus org.kde.kmail /KMail org.kde.kmail.kmail.showMail %mail_id %mail_id\n' + \
						'qdbus org.kde.kmail /KMail org.kde.kmail.kmail.selectFolder %dir_id')
		self.layout.addWidget(self.accountCommandLabel, 2, 0)

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
		self.layout.addLayout(self.buttons, 4, 0, 4, 5)
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
		self.blink()

	def initWidgets(self, item):
		self.Settings.beginGroup('Akonadi account')
		data = self.Settings.value(item.text()).toString()
		self.Settings.endGroup()
		parameterList = data.split(dlm)
		self.collectionID.setText(parameterList[0])
		if parameterList.count() > 1 and str(parameterList[1]) == '1' :
			self.enabledBox.setCheckState(Qt.Checked)
		if parameterList.count() > 2 :
			self.collectionResource.setText(parameterList[2])
		else :
			self.collectionResource.setText('-- "" --')
		if parameterList.count() > 3 :
			self.nameColl = parameterList[3]
		else :
			self.nameColl = '-- "" --'
		if parameterList.count() > 4 :
			self.accountCommand.setText( parameterList[4] )
		else :
			self.accountCommand.setText('')

	def clearParamArea(self):
		self.collectionID.setText('-- "" --')
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.collectionResource.setText('-- "" --')
		self.nameColl = ''
		self.accountCommand.clear()

	def changeSelfActivity(self, state = True):
		self.setEnabled(state)

	def cancel(self):
		self.blink(False, True)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def saveAccountData(self):
		collId = self.collectionID.text()
		if self.enabledBox.checkState() == Qt.Checked :
			enable = '1'
		else :
			enable = '0'
		collRes = self.collectionResource.text()
		accCommand = self.accountCommand.text()
		params = QStringList() << collId << enable << \
			collRes << self.nameColl << accCommand
		data = params.join(dlm)
		item = self.Parent.editList.accountListBox.currentItem()
		self.Settings.beginGroup('Akonadi account')
		data = self.Settings.setValue(item.text(), data)
		self.Settings.endGroup()
		# data saved
		self.blink(True, False)
		# after blink auto clear and emit edited-signal
		# in emitEditedSignal()

	def __del__(self):
		self.close()

class AkonadiResources(QWidget):
	edit = pyqtSignal(QListWidgetItem)
	edited = pyqtSignal()
	reloadAkonadi = pyqtSignal()
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.Settings = self.Parent.Settings
		self.checkAccess = self.Parent.checkAccess
		self.tr = Translator('EditAccounts')

		print dateStamp(), 'Module PyKDE4.akonadi is'
		if not A.AkonadiModuleExist :
			print '\tnot'
		print '\tavailable.'
		self.init()

	def init(self):
		self.layout = QGridLayout()
		self.VBLayout = QVBoxLayout()

		self.akonadiServer = QPushButton('&Restart')
		self.akonadiServer.setToolTip(self.tr._translate("Restart Akonadi Server"))
		self.akonadiServer.clicked.connect(self.reloadAkonadiStuff)
		self.layout.addWidget(self.akonadiServer, 0, 4)

		self.akonadiState = QLabel()
		if not A.AkonadiModuleExist :
			self.akonadiState.setText(self.tr._translate("Module PyKDE4.akonadi isn`t available."))
			akonadiAccList = []
		else :
			self.akonadiState.setText( self.tr._translate("Akonadi Server is : ") + \
										A.StateSTR[A.Akonadi.ServerManager.state()] )
			akonadiAccList = self.Parent.akonadiAccountList()
		self.layout.addWidget(self.akonadiState, 0, 0)

		self.VBLayout.addLayout(self.layout)

		self.editList = EditList(self.Parent, self)
		self.editParams = EditParam(self)

		self.VBLayout.addWidget(self.editList)
		self.VBLayout.addWidget(self.editParams)

		self.setLayout(self.VBLayout)

		self.edit.connect(self.editEvent)
		self.edited.connect(self.editedEvent)
		self.StateChanged = False
		self.setEditWidgetsState()

	def setEditWidgetsState(self):
		if A.AkonadiModuleExist and A.Akonadi.ServerManager.state() != A.Akonadi.ServerManager.State(4) :
			#self.editParams.changeSelfActivity(False)
			self.editList.changeSelfActivity(True)
		else :
			self.editList.changeSelfActivity(False)
		self.editParams.changeSelfActivity(False)

	def editEvent(self, item):
		self.StateChanged = True
		self.editList.changeSelfActivity(False)
		self.editParams.changeSelfActivity(True)
		self.editParams.initWidgets(item)

	def editedEvent(self):
		self.editParams.changeSelfActivity(False)
		self.editList.changeSelfActivity(True)
		self.StateChanged = False

	def collectionSearch(self):
		if not A.AkonadiModuleExist : return None
		self.Control = A.ControlWidget()
		if self.Control.exec_() :
			self.Control.move(self.Parent.popupPosition(self.Control.size()))
			col = self.Control.selectedCollection()
			## print dateStamp(), col.name().toUtf8(), col.id(), col.resource()
			self.editParams.collectionID.setText(str(col.id()))
			self.editParams.nameColl = col.name()
			#self.editList.stringEditor.setText(self.editParams.nameColl)
			self.editParams.collectionResource.setText(col.resource())

	def restartAkonadi(self):
		if not A.AkonadiModuleExist :
			self.akonadiState.setText(self.tr._translate("Module PyKDE4.akonadi isn`t available."))
			akonadiAccList = []
		else :
			server = A.Akonadi.Control()
			#server.widgetNeedsAkonadi(self)
			if A.Akonadi.ServerManager.isRunning() :
				if not server.restart(self) :
					print dateStamp(), 'Unable to start Akonadi Server '
			else :
				if not server.start(self) :
					print dateStamp(), 'Unable to start Akonadi Server '
			self.akonadiState.setText( self.tr._translate("Akonadi Server is : ") + \
											A.StateSTR[A.Akonadi.ServerManager.state()] )
		self.setEditWidgetsState()

	def reloadAkonadiStuff(self):
		self.reloadAkonadi.emit()

	def saveData(self):
		self.editParams.saveAccountData()

	def eventClose(self, event):
		self.prnt.done(0)

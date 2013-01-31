#  SendParams.py
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
SEND_PORT = 25
SEND_SSL_PORT = 465
SEND_TLS_PORT = 587

class SendParams(QWidget):
	def __init__(self, item, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings
		self.item = item
		self.appletName = self.Parent.Parent.Parent.appletName
		self.setToolTip(self.tr._translate("Send mail"))
		self.setMinimumWidth(48)

		self.VBLayout = QVBoxLayout()
		self.VBLayout.setContentsMargins(0, 0, 0, 0)
		self.HB1Layout = QGridLayout()

		self.HB1Layout.addWidget(QLabel(self.tr._translate(": Mail")), 0, 1)
		self.mailLineEdit = QLineEdit()
		self.mailLineEdit.setToolTip(self.tr._translate("Mail Address"))
		self.HB1Layout.addWidget(self.mailLineEdit, 0, 0)

		self.HB1Layout.addWidget(QLabel(self.tr._translate("Server : ")), 1, 0)
		self.HB1Layout.addWidget(QLabel(self.tr._translate("Port : ")), 1, 1)

		self.serverLineEdit = QLineEdit()
		self.serverLineEdit.setToolTip(self.tr._translate("Example : smtp.gmail.com, smtp.mail.ru or other"))
		self.HB1Layout.addWidget(self.serverLineEdit, 2, 0)

		self.portBox = QSpinBox()
		self.portBox.setMinimum(0)
		self.portBox.setMaximum(65535)
		self.portBox.setSingleStep(1)
		self.HB1Layout.addWidget(self.portBox, 2, 1)

		self.cryptBox = QComboBox()
		self.cryptBox.addItem('None', QVariant('None'))
		self.cryptBox.addItem('SSL', QVariant('SSL'))
		self.cryptBox.addItem('TLS', QVariant('TLS'))
		self.connect(self.cryptBox, SIGNAL("currentIndexChanged(const QString&)"), self.changePort)
		self.HB1Layout.addWidget(self.cryptBox, 2, 2)

		self.HB2Layout = QGridLayout()

		self.enabledBox = QCheckBox()
		remark = 'Use another data for authentification at send mail'
		self.enabledBox.setToolTip(self.tr._translate(remark))
		self.enabledBox.stateChanged.connect(self.changeAuthFieldState)
		self.HB2Layout.addWidget(self.enabledBox, 0, 0, Qt.AlignRight)
		self.HB2Layout.addWidget(QLabel(self.tr._translate(remark)[:16]), 0, 1, Qt.AlignLeft)

		self.userNameLineEdit = QLineEdit()
		self.userNameLineEdit.setToolTip(self.tr._translate("Username"))
		self.HB2Layout.addWidget(self.userNameLineEdit, 1, 0)

		self.passwordLineEdit = QLineEdit()
		self.passwordLineEdit.setToolTip(self.tr._translate("Password"))
		self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
		self.HB2Layout.addWidget(self.passwordLineEdit, 1, 1)

		self.VBLayout.addLayout(self.HB1Layout)
		self.VBLayout.addLayout(self.HB2Layout)
		self.setLayout(self.VBLayout)
		self.initData()
		self.passwordChanged = False

	def initData(self):
		self.Settings.beginGroup(self.item.text())

		self.mailLineEdit.setText(self.Settings.value('mailAddr').toString())

		if self.Settings.value('anotherAuthData', '0').toString() == '1' :
			self.enabledBox.setCheckState(Qt.Checked)
		else :
			self.enabledBox.setCheckState(Qt.Unchecked)
		self.changeAuthFieldState()

		self.serverLineEdit.setText(self.Settings.value('sendServer').toString())

		i = self.cryptBox.findData(self.Settings.value('sendAuthMethod', ''), flags = Qt.MatchFixedString)
		if i>=0 : self.cryptBox.setCurrentIndex(i)

		self.portBox.setValue(int(self.Settings.value('sendPort', '25').toString()))

		self.userNameLineEdit.setText(self.Settings.value('sendLogin', '').toString())

		if self.Parent.Parent.Parent.wallet.hasEntry(self.item.text()) and \
			self.Parent.Parent.Parent.wallet.hasFolder(self.appletName+'_SEND') :
			self.passwordLineEdit.setText( '***EncriptedPassWord***' )
		else:
			self.passwordLineEdit.setText( '***EncriptedKey_not_created***' )
		self.passwordLineEdit.textChanged.connect(self.changePasswd)

		self.Settings.endGroup()

	def changePasswd(self):
		self.passwordLineEdit.textChanged.disconnect(self.changePasswd)
		self.passwordLineEdit.setEchoMode(QLineEdit.Password)
		self.passwordLineEdit.clear()
		self.passwordChanged = True

	def changePort(self, str_):
		cryptMethod = self.cryptBox.itemData(self.cryptBox.currentIndex()).toString()
		if str(cryptMethod) == 'None' : self.portBox.setValue(SEND_PORT)
		elif str(cryptMethod) == 'SSL' : self.portBox.setValue(SEND_SSL_PORT)
		elif str(cryptMethod) == 'TLS' : self.portBox.setValue(SEND_TLS_PORT)

	def changeAuthFieldState(self):
		state = self.enabledBox.checkState()
		self.userNameLineEdit.setEnabled(state)
		self.passwordLineEdit.setEnabled(state)

	def saveData(self):
		self.Settings.beginGroup(self.item.text())

		self.Settings.setValue('mailAddr', self.mailLineEdit.text())

		if self.enabledBox.checkState() : value = '1'
		else : value = '0'
		self.Settings.setValue('anotherAuthData', value)

		self.Settings.setValue('sendServer', self.serverLineEdit.text())

		self.Settings.setValue('sendAuthMethod', self.cryptBox.itemData(self.cryptBox.currentIndex()))

		self.Settings.setValue('sendPort', self.portBox.value())

		if self.enabledBox.checkState() :
			self.Settings.setValue('sendLogin', self.userNameLineEdit.text())

			if self.passwordChanged :
				if not self.Parent.Parent.Parent.wallet.hasFolder(self.appletName+'_SEND') :
					self.Parent.Parent.Parent.wallet.createFolder(self.appletName+'_SEND')
				self.Parent.Parent.Parent.wallet.setFolder(self.appletName+'_SEND')
				self.Parent.Parent.Parent.wallet.writePassword(self.item.text(), self.passwordLineEdit.text())
				self.passwordLineEdit.setText( '***EncriptedPassWord***' )

		self.Settings.endGroup()

	def __del__(self):
		self.close()

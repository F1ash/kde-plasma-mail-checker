# -*- coding: utf-8 -*-
#  ReceiveParams.py
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
from Functions import *
import os.path

class ReceiveParams(QWidget):
	def __init__(self, item, parent = None):
		QWidget.__init__(self, parent)

		self.Parent = parent
		self.tr = parent.tr
		self.Settings = parent.Settings
		self.item = item
		self.setToolTip(self.tr._translate("Receive mail"))

		self.VBLayout = QVBoxLayout()
		self.VBLayout.setContentsMargins(0, 0, 0, 0)
		self.HB1Layout = QGridLayout()

		self.HB1Layout.addWidget(QLabel(self.tr._translate("Server : ")), 0, 0)
		self.HB1Layout.addWidget(QLabel(self.tr._translate("Port : ")), 0, 1)
		self.HB1Layout.addWidget(QLabel(self.tr._translate("Enable : ")), 0, 2)

		self.serverLineEdit = QLineEdit()
		self.serverLineEdit.setToolTip(self.tr._translate("Example : imap.gmail.com, pop.mail.ru"))
		self.HB1Layout.addWidget(self.serverLineEdit, 1, 0)

		self.portBox = QSpinBox()
		self.portBox.setMinimum(0)
		self.portBox.setMaximum(65535)
		self.portBox.setSingleStep(1)
		self.HB1Layout.addWidget(self.portBox, 1, 1)

		self.enabledBox = QCheckBox()
		self.enabledBox.setCheckState(Qt.Unchecked)
		self.HB1Layout.addWidget(self.enabledBox, 1, 2, Qt.AlignHCenter)

		self.HB2Layout = QGridLayout()

		self.connectMethodBox = QComboBox()
		self.connectMethodBox.addItem('POP3',QVariant('pop'))
		self.connectMethodBox.addItem('IMAP4',QVariant('imap'))
		self.connectMethodBox.addItem('IMAP4\IDLE',QVariant('imap\idle'))
		self.connect(self.connectMethodBox, SIGNAL("currentIndexChanged(const QString&)"), self.showCatalogChoice)
		self.connect(self.connectMethodBox, SIGNAL("currentIndexChanged(const QString&)"), self.changePort)
		self.HB2Layout.addWidget(self.connectMethodBox, 0, 0)

		self.cryptBox = QComboBox()
		self.cryptBox.addItem('None',QVariant('None'))
		self.cryptBox.addItem('SSL',QVariant('SSL'))
		#self.cryptBox.addItem('TLS',QVariant('TLS'))
		self.connect(self.cryptBox, SIGNAL("currentIndexChanged(const QString&)"), self.changePort)
		self.HB2Layout.addWidget(self.cryptBox, 0, 1)

		self.mailboxLineEdit = QLineEdit()
		self.mailboxLineEdit.setVisible(False)
		self.mailboxLineEdit.setToolTip(u'Defailt MailBox : Inbox\nFor example, GMail specified mailbox :\n[Gmail]/All\nor\n[Gmail]/Вся почта')
		self.HB2Layout.addWidget(self.mailboxLineEdit, 0, 2)

		self.accountCommand = QComboBox()
		self.accountCommand.setToolTip(self.tr._translate("Exec command activated in notification.\nSee for : EXAMPLES."))
		self.accountCommand.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
		self.accountCommand.setEditable(True)
		templates = self.Parent.Parent.Parent.user_or_sys('contents/code/templates')
		if os.path.isfile(templates) :
			with open(templates, 'rb') as f :
				texts = f.read().split('\n')
				texts.remove('')
		else : texts = []
		#print texts, os.getcwd(), templates
		self.accountCommand.addItems(QStringList() << '' << texts)
		self.HB2Layout.addWidget(self.accountCommand, 2, 0, 2, 4)

		self.HB3Layout = QGridLayout()

		self.HB3Layout.addWidget(QLabel(self.tr._translate("Username : ")), 0, 0)

		self.HB3Layout.addWidget(QLabel(self.tr._translate("Password : ")), 0, 1)

		self.userNameLineEdit = QLineEdit()
		self.HB3Layout.addWidget(self.userNameLineEdit, 1, 0)

		self.passwordLineEdit = QLineEdit()
		self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
		self.HB3Layout.addWidget(self.passwordLineEdit, 1, 1)

		self.VBLayout.addLayout(self.HB1Layout)
		self.VBLayout.addLayout(self.HB2Layout)
		self.VBLayout.addLayout(self.HB3Layout)
		self.setLayout(self.VBLayout)
		self.initData()
		self.passwordChanged = False

	def changePort(self, str_):
		ports = [POP3_PORT, POP3_SSL_PORT, IMAP4_PORT, IMAP4_SSL_PORT]
		connectMethod = self.connectMethodBox.itemData(self.connectMethodBox.currentIndex()).toString()
		cryptMethod = self.cryptBox.itemData(self.cryptBox.currentIndex()).toString()
		if str(connectMethod) in ('imap', 'imap\idle') :
			if POP3_PORT in ports : ports.remove(POP3_PORT)
			if POP3_SSL_PORT in ports : ports.remove(POP3_SSL_PORT)
		else :
			if IMAP4_PORT in ports : ports.remove(IMAP4_PORT)
			if IMAP4_SSL_PORT in ports : ports.remove(IMAP4_SSL_PORT)
		if str(cryptMethod) == 'None' :
			if IMAP4_SSL_PORT in ports : ports.remove(IMAP4_SSL_PORT)
			if POP3_SSL_PORT in ports : ports.remove(POP3_SSL_PORT)
		else :
			if IMAP4_PORT in ports : ports.remove(IMAP4_PORT)
			if POP3_PORT in ports : ports.remove(POP3_PORT)
		self.portBox.setValue(ports[0] if len(ports) else 0)

	def showCatalogChoice(self, str_):
		if str_ in ('IMAP4', 'IMAP4\IDLE') : state = True
		else : state = False
		self.mailboxLineEdit.setVisible(state)

	def initData(self):
		self.Settings.beginGroup(self.item.text())

		self.serverLineEdit.setText(self.Settings.value('server').toString())

		if self.Settings.value('Enabled', '0').toString() == '1' :
			self.enabledBox.setCheckState(Qt.Checked)

		i = self.connectMethodBox.findData(self.Settings.value('connectMethod', ''), flags = Qt.MatchFixedString)
		if i>=0 : self.connectMethodBox.setCurrentIndex(i)

		i = self.cryptBox.findData(self.Settings.value('authentificationMethod', ''), flags = Qt.MatchFixedString)
		if i>=0 : self.cryptBox.setCurrentIndex(i)

		self.portBox.setValue(int(self.Settings.value('port', '0').toString()))

		self.mailboxLineEdit.setText(self.Settings.value('Inbox', '').toString())

		i = self.accountCommand.findText(self.Settings.value('CommandLine', '').toString(), Qt.MatchFixedString)
		if i>=0 : self.accountCommand.setCurrentIndex(i)

		self.userNameLineEdit.setText(self.Settings.value('login', '').toString())

		if self.Parent.Parent.Parent.wallet.hasEntry(self.item.text()) :
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

	def saveData(self):
		self.Settings.beginGroup(self.item.text())

		self.Settings.setValue('server', self.serverLineEdit.text())

		if self.enabledBox.checkState() : value = '1'
		else : value = '0'
		self.Settings.setValue('Enabled', value)

		self.Settings.setValue('connectMethod', self.connectMethodBox.itemData(self.connectMethodBox.currentIndex()).toString())

		self.Settings.setValue('authentificationMethod', self.cryptBox.itemData(self.cryptBox.currentIndex()))

		self.Settings.setValue('port', self.portBox.value())

		if self.mailboxLineEdit.isVisible() :
			self.Settings.setValue('Inbox', self.mailboxLineEdit.text())

		self.Settings.setValue('CommandLine', self.accountCommand.currentText())

		self.Settings.setValue('login', self.userNameLineEdit.text())

		if self.passwordChanged :
			self.Parent.Parent.Parent.wallet.writePassword(self.item.text(), self.passwordLineEdit.text())
			self.passwordLineEdit.setText( '***EncriptedPassWord***' )

		self.Settings.endGroup()

	def __del__(self):
		self.close()

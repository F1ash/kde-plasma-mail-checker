# -*- coding: utf-8 -*-
#  Proxy.py
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
from Translator import Translator

class ProxySettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('Proxy')
		self.Settings = obj.Settings
		self.loadSocksModule = obj.someFunctions.loadSocksModule

		self.layout = QGridLayout()
		self.layout.setSpacing(0)

		self.enableProxy = QCheckBox()
		self.enableProxy.setToolTip(self.tr._translate("Enable\Disable the Proxy"))
		self.Enabled = True if self.Settings.value('UseProxy', 'False')=='True' else False
		if self.Enabled : self.enableProxy.setCheckState(Qt.Checked)
		else : self.enableProxy.setCheckState(Qt.Unchecked)
		self.enableProxy.stateChanged.connect(self.activateProxy)
		self.layout.addWidget(self.enableProxy, 0, 0, Qt.AlignLeft)

		self.saveButton = QPushButton('&Save')
		#self.saveButton.setMaximumWidth(40)
		self.saveButton.clicked.connect(self.saveData)
		self.saveButton.setToolTip(self.tr._translate("Save"))

		self.layout.addWidget(self.saveButton, 0, 1,  Qt.AlignLeft)

		self.proxyTypeBox = QComboBox()
		#self.proxyTypeBox.addItem('HTTP', QVariant('HTTP'))
		self.proxyTypeBox.addItem('SOCKS4', QVariant('SOCKS4'))
		self.proxyTypeBox.addItem('SOCKS5', QVariant('SOCKS5'))
		self.proxyTypeBox.setToolTip(self.tr._translate("Proxy type"))
		data = self.Settings.value('ProxyType', 'SOCKS5')
		self.proxyTypeBox.setCurrentIndex(self.proxyTypeBox.findData(data))
		self.proxyTypeBox.currentIndexChanged.connect(self.stateChangedEvent)
		self.layout.addWidget(self.proxyTypeBox, 1, 0)

		self.Hlayout = QHBoxLayout()
		self.addrEditor = QLineEdit()
		self.addrEditor.setText(self.Settings.value('ProxyAddr', '').toString())
		self.addrEditor.setToolTip(self.tr._translate("Proxy address"))
		self.addrEditor.textChanged.connect(self.stateChangedEvent)
		self.Hlayout.addWidget(self.addrEditor, 0)

		self.portBox = QSpinBox()
		self.portBox.setMinimum(0)
		self.portBox.setMaximum(65535)
		value = self.Settings.value('ProxyPort', '3128' )
		self.portBox.setValue(int(str(value.toString())))
		self.portBox.setSingleStep(1)
		self.portBox.setToolTip(self.tr._translate('Proxy Port'))
		self.portBox.valueChanged.connect(self.stateChangedEvent)
		self.Hlayout.addWidget(self.portBox, 0,  Qt.AlignRight)

		self.layout.addItem(self.Hlayout, 1, 1)

		self.userLabel = QLabel(self.tr._translate("UserName :"))
		self.passwLabel = QLabel(self.tr._translate("Password :"))
		self.layout.addWidget(self.userLabel, 2, 0,  Qt.AlignLeft)
		self.layout.addWidget(self.passwLabel, 3, 0,  Qt.AlignLeft)

		self.userEditor = QLineEdit()
		self.userEditor.setText(self.Settings.value('ProxyUSER', '').toString())
		self.userEditor.textChanged.connect(self.stateChangedEvent)
		self.passwEditor = QLineEdit()
		self.passwEditor.setText(self.Settings.value('ProxyPASS', '').toString())
		self.passwEditor.textChanged.connect(self.stateChangedEvent)
		self.layout.addWidget(self.userEditor, 2, 1)
		self.layout.addWidget(self.passwEditor, 3, 1)

		self.timeoutLabel = QLabel(self.tr._translate("Timeout Socks"))
		a, b, c = "If error: ['The read operation timed out']", \
				"in IMAP/IDLE connect is often,", \
				"then you should increase the timeout"
		description = QString('%1\n%2\n%3').arg(a).arg(b).arg(c)
		self.timeoutLabel.setToolTip(self.tr._translate(description))
		self.layout.addWidget(self.timeoutLabel, 4, 0)
		self.layout.addWidget(self.passwEditor, 3, 1)
		self.timeoutBox = QSpinBox()
		self.timeoutBox.setMinimum(30)
		self.timeoutBox.setMaximum(300)
		value = self.Settings.value('timeoutSocks', 45).toUInt()[0]
		self.timeoutBox.setValue(value)
		self.timeoutBox.setSingleStep(1)
		self.timeoutBox.setToolTip(self.tr._translate('Proxy TimeOut'))
		self.timeoutBox.valueChanged.connect(self.stateChangedEvent)
		self.layout.addWidget(self.timeoutBox, 4, 1, Qt.AlignRight)

		if self.loadSocksModule() : available = self.tr._translate("SocksiPy module loaded")
		else : available = self.tr._translate("SocksiPy module not loaded")
		self.proxyModuleLabel = QLabel(available)
		self.layout.addWidget(self.proxyModuleLabel, 0, 1, Qt.AlignRight)

		self.setLayout(self.layout)
		self.StateChanged = False
		self.activateProxy()

	def stateChangedEvent(self):
		self.StateChanged = True

	def saveData(self):
		self.Settings.setValue('ProxyType', self.proxyTypeBox.currentText())
		self.Settings.setValue('ProxyAddr', self.addrEditor.text())
		self.Settings.setValue('ProxyPort', self.portBox.value())
		self.Settings.setValue('ProxyUSER', self.userEditor.text())
		self.Settings.setValue('ProxyPASS', self.passwEditor.text())
		self.Settings.setValue('timeoutSocks', self.timeoutBox.value())
		self.StateChanged = False

	def activateProxy(self):
		state = True if self.enableProxy.checkState()==Qt.Checked else False
		if state : PROXY_Module = self.loadSocksModule(True)
		else : PROXY_Module = self.loadSocksModule(False)
		if PROXY_Module : available = self.tr._translate("SocksiPy module loaded")
		else : available = self.tr._translate("SocksiPy module not loaded")
		self.proxyModuleLabel.setText(available)
		if PROXY_Module and state : self.enableWidgets(True)
		else : self.enableWidgets(False)

	def enableWidgets(self, state):
		self.saveButton.setEnabled(state)
		self.addrEditor.setEnabled(state)
		self.portBox.setEnabled(state)
		self.userLabel.setEnabled(state)
		self.passwLabel.setEnabled(state)
		self.userEditor.setEnabled(state)
		self.passwEditor.setEnabled(state)
		self.proxyTypeBox.setEnabled(state)
		self.timeoutBox.setEnabled(state)
		self.timeoutLabel.setEnabled(state)
		self.layout.setEnabled(state)

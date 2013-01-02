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
from Functions import *
from Translator import Translator

class ProxySettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('Proxy')

		self.layout = QGridLayout()
		self.layout.setSpacing(0)

		self.enableProxy = QCheckBox()
		self.enableProxy.setToolTip(self.tr._translate("Enable\Disable the Proxy"))
		self.Enabled = True if Settings.value('UseProxy', 'False')=='True' else False
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
		self.proxyTypeBox.addItem('HTTP', QVariant('HTTP'))
		self.proxyTypeBox.addItem('SOCKS4', QVariant('SOCKS4'))
		self.proxyTypeBox.addItem('SOCKS5', QVariant('SOCKS5'))
		self.proxyTypeBox.setToolTip(self.tr._translate("Proxy type"))
		data = Settings.value('ProxyType', 'SOCKS5')
		self.proxyTypeBox.setCurrentIndex(self.proxyTypeBox.findData(data))
		self.proxyTypeBox.currentIndexChanged.connect(self.stateChangedEvent)
		self.layout.addWidget(self.proxyTypeBox, 1, 0)

		self.Hlayout = QHBoxLayout()
		self.addrEditor = QLineEdit()
		self.addrEditor.setText(Settings.value('ProxyAddr', '').toString())
		self.addrEditor.setToolTip(self.tr._translate("Proxy address"))
		self.addrEditor.textChanged.connect(self.stateChangedEvent)
		self.Hlayout.addWidget(self.addrEditor, 0)

		self.portBox = QSpinBox()
		self.portBox.setMinimum(0)
		self.portBox.setMaximum(65535)
		value = Settings.value('ProxyPort', '3128' )
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
		self.userEditor.setText(Settings.value('ProxyUSER', '').toString())
		self.userEditor.textChanged.connect(self.stateChangedEvent)
		self.passwEditor = QLineEdit()
		self.passwEditor.setText(Settings.value('ProxyPASS', '').toString())
		self.passwEditor.textChanged.connect(self.stateChangedEvent)
		self.layout.addWidget(self.userEditor, 2, 1)
		self.layout.addWidget(self.passwEditor, 3, 1)

		if loadSocksModule() : available = self.tr._translate("SocksiPy module loaded")
		else : available = self.tr._translate("SocksiPy module not loaded")
		self.proxyModuleLabel = QLabel(available)
		self.layout.addWidget(self.proxyModuleLabel, 0, 1,  Qt.AlignRight)

		self.setLayout(self.layout)
		self.StateChanged = False
		self.activateProxy()

	def stateChangedEvent(self):
		self.StateChanged = True

	def saveData(self):
		Settings.setValue('ProxyType', self.proxyTypeBox.currentText())
		Settings.setValue('ProxyAddr', self.addrEditor.text())
		Settings.setValue('ProxyPort', self.portBox.value())
		Settings.setValue('ProxyUSER', self.userEditor.text())
		Settings.setValue('ProxyPASS', self.passwEditor.text())
		self.StateChanged = False

	def activateProxy(self):
		state = True if self.enableProxy.checkState()==Qt.Checked else False
		if state : PROXY_Module = loadSocksModule(True)
		else : PROXY_Module = loadSocksModule(False)
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

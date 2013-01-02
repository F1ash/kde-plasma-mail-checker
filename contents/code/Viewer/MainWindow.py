# -*- coding: utf-8 -*-
#  MainWindow.py
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
from PyQt4.QtWebKit import QWebSettings
from Box import Box
from Translator import Translator

class MainWindow(QMainWindow):
	def __init__(self, data = {}, parent = None):
		QMainWindow.__init__(self, parent)
		self.runned = False
		self.tr = Translator('mailViewer')
		self.autoLoadImage = False
		self.privateEnable = False

		self.setWindowTitle(self.tr._translate('Mail Viewer'))
		self.setWindowIcon(QIcon().fromTheme("mail"))

		self.exit_ = QAction(QIcon().fromTheme("application-exit"), '&'+self.tr._translate('Exit'), self)
		self.exit_.setShortcut('Ctrl+Q')
		self.connect(self.exit_, SIGNAL('triggered()'), self._close)

		self.image_ = QAction(self.tr._translate('Image AutoLoad'), self)
		self.image_.setShortcut('Ctrl+I')
		self.image_.setCheckable(True)
		self.image_.setChecked(self.autoLoadImage)
		#self.image_.setIcon(QIcon().fromTheme("arrow-down-double"))
		self.connect(self.image_, SIGNAL('triggered()'), self._image)

		self.priv_ = QAction(self.tr._translate('Private Browsing'), self)
		self.priv_.setShortcut('Ctrl+P')
		self.priv_.setCheckable(True)
		self.priv_.setChecked(self.privateEnable)
		#self.priv_.setIcon(QIcon().fromTheme("user-group-delete"))
		self.connect(self.priv_, SIGNAL('triggered()'), self._private)

		self.menubar = self.menuBar()

		file_ = self.menubar.addMenu('&'+self.tr._translate('File'))
		file_.addAction(self.exit_)

		sett_ = self.menubar.addMenu('&'+self.tr._translate('Settings'))
		sett_.addAction(self.image_)
		sett_.addAction(self.priv_)

		self.statusBar = QStatusBar(self)
		self.setStatusBar(self.statusBar)

		self.menuTab = Box(data, self)
		self.setCentralWidget(self.menuTab)

	def _image(self): self.regimeChange('image', self.image_.isChecked())

	def _private(self): self.regimeChange('private', self.priv_.isChecked())

	def regimeChange(self, parameter, state):
		if parameter == 'image' :
			attr = QWebSettings.AutoLoadImages
		else :
			attr = QWebSettings.PrivateBrowsingEnabled
		for wdg in self.menuTab.webViewWDGs :
			wdg.settings().setAttribute(attr, state)
			wdg.reload()

	def _close(self): self.eventClose()

	def closeEvent(self, ev):
		self.menuTab.__del__()

	def eventClose(self):
		self.close()

#  Mail.py
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

class Mail(QWidget):
	def __init__(self, idx = None, parent = None):
		QWidget.__init__(self, parent)
		self.idx = idx
		self.tr = Translator('mailViewer')
		self.fromField = QLabel(self.tr._translate('From:'))
		self.subjField = QLabel(self.tr._translate('Subj:'))
		self.dateField = QLabel(self.tr._translate('Date:'))
		self.mailField = QSplitter()
		self.mailField.setChildrenCollapsible(True)
		self.mailField.setOrientation(Qt.Vertical)
		self.mailField.setStretchFactor(1, 1)
		self.mailField.setHandleWidth(5)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.fromField)
		self.layout.addWidget(self.subjField)
		self.layout.addWidget(self.dateField)
		self.layout.addWidget(self.mailField)
		self.setLayout(self.layout)

	def __del__(self): self.close()

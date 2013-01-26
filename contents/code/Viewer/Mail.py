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
from Sender.mailSender import MailSender

class Mail(QWidget):
	def __init__(self, idx = None, parent = None):
		QWidget.__init__(self, parent)
		self.idx = idx
		self.Parent = parent
		self.tr = Translator('mailViewer')
		self.reply_to = None
		self._from_subj = None
		self.fromField = QLabel(self.tr._translate('From:'))
		self.fromField.setOpenExternalLinks(True)
		self.fromField.linkHovered.connect(self.linkDisplay)
		self.subjField = QLabel(self.tr._translate('Subj:'))
		self.dateField = QLabel(self.tr._translate('Date:'))

		self.sendRe = QPushButton(QIcon.fromTheme('mail-reply-custom'), '')
		self.sendRe.setToolTip(self.tr._translate('Quick Answer'))
		self.sendRe.setFixedWidth(self.Parent.iconSize().width())
		self.sendRe.setMinimumHeight(self.Parent.iconSize().height())
		self.sendRe.setContentsMargins(0, 0, 0, 0)
		self.sendRe.clicked.connect(self.sendReMail)
		self.sendFw = QPushButton(QIcon.fromTheme('mail-forward'), '')
		self.sendFw.setToolTip(self.tr._translate('Quick Forward'))
		self.sendFw.setFixedWidth(self.Parent.iconSize().width())
		self.sendFw.setMinimumHeight(self.Parent.iconSize().height())
		self.sendFw.setContentsMargins(0, 0, 0, 0)
		self.sendFw.clicked.connect(self.sendFwMail)

		self.mailField = QSplitter()
		self.mailField.setChildrenCollapsible(True)
		self.mailField.setOrientation(Qt.Vertical)
		self.mailField.setStretchFactor(1, 1)
		self.mailField.setHandleWidth(5)

		self.panel = QHBoxLayout()
		self.mailInfo = QVBoxLayout()
		self.mailInfo.addWidget(self.fromField)
		self.mailInfo.addWidget(self.subjField)
		self.mailInfo.addWidget(self.dateField)
		self.buttons = QVBoxLayout()
		self.buttons.addWidget(self.sendRe)
		self.buttons.addWidget(self.sendFw)
		self.panel.addItem(self.mailInfo)
		self.panel.addItem(self.buttons)

		self.layout = QVBoxLayout()
		self.layout.addItem(self.panel)
		self.layout.addWidget(self.mailField)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setSpacing(0)
		self.setLayout(self.layout)

	def linkDisplay(self, s):
		self.Parent.Parent.statusBar.showMessage(s)

	def sendReMail(self):
		self.sendMail('Re: ')
	def sendFwMail(self):
		self.sendMail('Fw: ')
	def sendMail(self, prefix):
		splt = self.mailField.widget(0)
		wdg = splt.widget(splt.count() - 1)
		if hasattr(wdg, 'toPlainText') : text = wdg.toPlainText()
		elif hasattr(wdg, 'title') : text = wdg.title()
		else : text = QString('<UNKNOWN_ERROR>')
		to_ = self._from_subj[0] if self.reply_to is None else self.reply_to
		self.sender = MailSender(to_, prefix, self._from_subj[1], text, self)
		self.sender.exec_()

	def __del__(self): self.close()

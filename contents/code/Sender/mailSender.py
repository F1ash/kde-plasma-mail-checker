#  mailSender.py
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

class MailSender(QDialog):
	def __init__(self, from_, to_, prefix, subj_, text, parent = None):
		QDialog.__init__(self, parent)
		self.Parent = parent
		self.tr = Translator('mailSender')
		self.setWindowTitle(self.tr._translate('Mail Sender'))
		
		self.toField = QLabel(self.tr._translate('To:'))
		self.copyField = QLabel(self.tr._translate('Copy:'))
		self.subjField = QLabel(self.tr._translate('Subj:'))
		
		self.toLine  = QLineEdit()
		self.toLine.setText(to_ if prefix=='Re: ' else '')
		self.copyLine  = QLineEdit()
		self.copyLine.setText('')
		self.subjLine  = QLineEdit()
		self.subjLine.setText(prefix + subj_.remove('Subj: '))

		self.reg_ = QComboBox()
		self.reg_.setToolTip(self.tr._translate('Connection Type'))
		self.reg_.addItem('', QVariant(None))
		self.reg_.addItem('SSL', QVariant('ssl'))
		self.reg_.addItem('TLS', QVariant('tls'))
		self.reg_.setVisible(False)
		
		self.servLine  = QLineEdit()
		self.servLine.setVisible(False)
		self.servLine.setReadOnly(False)
		self.servLine.setText('' if len(from_.split('@'))<=1 else 'smtp.'+from_.split('@')[1])
		self.portLine  = QLineEdit()
		self.portLine.setVisible(False)
		self.portLine.setReadOnly(False)
		self.portLine.setMaximumWidth(2*self.Parent.Parent.iconSize().width())
		self.portLine.setText(str(self.Parent.Parent.getMail.data['port']))
		self.passwLine = QLineEdit()
		self.passwLine.setVisible(False)
		self.passwLine.setReadOnly(False)
		self.passwLine.setEchoMode(QLineEdit.Password)
		self.passwLine.setText(self.Parent.Parent.getMail.data['password'])
		
		self.send = QPushButton(QIcon.fromTheme('mail-reply-sender'), '')
		self.send.setToolTip(self.tr._translate('Send mail'))
		self.send.setMinimumWidth(self.Parent.Parent.iconSize().width())
		self.send.setMinimumHeight(self.Parent.Parent.iconSize().height())
		self.send.setContentsMargins(0, 0, 0, 0)
		self.send.clicked.connect(self.sendMail)

		self.edit = QPushButton('>>')
		self.edit.setToolTip(self.tr._translate('Show settings'))
		self.edit.clicked.connect(self.showServerSettings)
		
		self.mailField = QTextEdit()
		self.mailField.setText(text)

		self.layout = QGridLayout()
		self.layout.addWidget(self.toField, 0, 0)
		self.layout.addWidget(self.copyField, 1, 0)
		self.layout.addWidget(self.subjField, 2, 0)
		self.layout.addWidget(self.toLine, 0, 1)
		self.layout.addWidget(self.copyLine, 1, 1)
		self.layout.addWidget(self.subjLine, 2, 1)
		self.layout.addWidget(self.send, 0, 2, 2, 2)
		self.layout.addWidget(self.edit, 1, 2, 2, 2)
		self.layout.addWidget(self.mailField, 5, 0, 6, 3)
		self.setLayout(self.layout)
		
		self.setModal(False)
		self.setWindowModality(Qt.NonModal)

	def sendMail(self):
		print self.toLine.text().toLocal8Bit().data(), self.copyLine.text().toLocal8Bit().data()
		print self.subjLine.text().toLocal8Bit().data()
		print self.servLine.text().toLocal8Bit().data()
		print self.portLine.text().toLocal8Bit().data()
		print self.passwLine.text().toLocal8Bit().data()
		#print self.mailField.toPlainText().toLocal8Bit().data()
		#print self.mailField.toHtml().toLocal8Bit().data()
		QMessageBox.information(self, self.tr._translate('Mail Sender'), \
					'This function not implemented.')

	def showServerSettings(self):
		state = not self.servLine.isVisible()
		if state : self.edit.setText('<<')
		else : self.edit.setText('>>')
		self.reg_.setVisible(state)
		self.servLine.setVisible(state)
		self.portLine.setVisible(state)
		self.passwLine.setVisible(state)

		if state :
			self.layout.addWidget(self.reg_, 3 , 0)
			self.layout.addWidget(self.servLine, 3, 1)
			self.layout.addWidget(self.portLine, 3, 2)
			self.layout.addWidget(self.passwLine, 4, 1)
		else :
			self.layout.removeWidget(self.reg_)
			self.layout.removeWidget(self.servLine)
			self.layout.removeWidget(self.portLine)
			self.layout.removeWidget(self.passwLine)
		self.setLayout(self.layout)

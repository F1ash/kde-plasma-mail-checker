# -*- coding: utf-8 -*-
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
from TextFunc import MAILTO_REGEXP
from MailFunc import loadSocketModule
from re import findall

global ModuleExist
ModuleExist = False
try :
	import smtplib
	import mailer
	ModuleExist = True
except Exception : pass
finally : pass

BLOCK = '<blockquote class="gmail_quote" style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">'
BLOCK_END = '</blockquote><br>'

def _difference(chunks):
	mark = True
	for chunk in chunks :
		if chunk[:1] in ('', ' ', '\n', '\t', '\r') : mark = mark and True
		else : mark = mark and False
	dlm = ' >' if mark else '>'
	pos = len(dlm)
	summ = QStringList()
	_block = QStringList()
	mark = False
	for chunk in chunks :
		_mark = True if chunk.startsWith(dlm) else False
		if _mark > mark :
			summ.append(chunk[pos:].prepend(BLOCK))
			mark = True
		elif _mark < mark :
			for item in _difference(_block) : summ.append(item)
			_chunk = summ.takeLast()
			_chunk.append(BLOCK_END)
			summ.append(_chunk)
			summ.append(chunk)
			_block = QStringList()
			mark = False
		elif mark == _mark == True :
			_block.append(chunk[pos:])
		elif mark == _mark == False :
			summ.append(chunk)
	return summ

def makeHtml(text):
	chunks =  text.split('\n')
	data = _difference(chunks)
	return data.join('<br>')

class SendThread(QThread):
	def __init__(self, sender, msg, parent = None):
		QThread.__init__(self, parent)
		self.Parent = parent
		self.sender = sender
		self.msg = msg

	def run(self):
		try :
			_result = (False, -1, '')
			self.sender.send(self.msg)
			_result = (True, 0, '')
		except Exception as e:
			args = e.args
			if len(args) < 2:
				args = (-1, e.args[0])
			_result = (False, args[0], args[1])
		finally :
			self.Parent.msgSent.emit({'result' : _result})

class DelButton(QPushButton):
	def __init__(self, i = 0, parent = None):
		QPushButton.__init__(self, QIcon().fromTheme('list-remove'), '', parent)
		self.Parent = parent
		self.i = i
		self.setToolTip(self.Parent.tr._translate('Delete attachment'))
		self.clicked.connect(self.buttonClicked)

	def buttonClicked(self):
		self.Parent.delAttach.emit(self.i)

class MailSender(QDialog):
	delAttach = pyqtSignal(int)
	msgSent   = pyqtSignal(dict)
	def __init__(self, to_, prefix, subj_, text, parent = None):
		QDialog.__init__(self, parent)
		self.Parent = parent
		self.tr = Translator('mailSender')
		self.text = text
		self.setWindowTitle(self.tr._translate('Mail Sender'))
		self.attachList = {}
		self.Re_Fw = prefix=='Re: '

		self.fromField = QLabel(self.tr._translate('From:'))
		self.toField   = QLabel(self.tr._translate('To:'  ))
		self.copyField = QLabel(self.tr._translate('Copy:'))
		self.subjField = QLabel(self.tr._translate('Subj:'))

		self.fromLine = QLineEdit()
		accName = self.Parent.Parent.getMail.data['mailBox']
		self.Parent.Parent.Settings.beginGroup(accName)
		from_ = self.Parent.Parent.Settings.value('mailAddr').toString()
		self.Parent.Parent.Settings.endGroup()
		self.fromLine.setText(from_)
		self.toLine = QLineEdit()
		self.toLine.setText(to_ if self.Re_Fw else '')
		self.copyLine = QLineEdit()
		self.copyLine.setText('')
		self.subjLine = QLineEdit()
		self.subjLine.setText(prefix + subj_)

		self.send = QPushButton(QIcon.fromTheme('mail-reply-sender'), '')
		self.send.setToolTip(self.tr._translate('Send mail'))
		self.send.setMinimumWidth(self.Parent.Parent.iconSize().width())
		self.send.setMinimumHeight(self.Parent.Parent.iconSize().height())
		self.send.clicked.connect(self.sendMail)

		self.save = QPushButton(QIcon().fromTheme('document-save'), '')
		self.save.setToolTip(self.tr._translate('Save message as file'))
		self.save.clicked.connect(self.saveAsFile)

		self.attach = QPushButton(QIcon().fromTheme('list-add'), '')
		self.attach.setToolTip(self.tr._translate('Add attachment'))
		self.attach.clicked.connect(self.addAttachment)

		self.mailField = QTextEdit()
		self.mailField.setAcceptRichText(True)
		self.mailField.setUndoRedoEnabled(True)
		self.mailField.setAutoFormatting(QTextEdit.AutoAll)
		self.mailField.setReadOnly(not self.Re_Fw)
		if self.Re_Fw :
			chunks = text.split('\n')
			data = chunks.join('\n> ').append('\n').prepend('> ')
		else :
			data = self.text
		self.mailField.setText(data)

		self.layout = QGridLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(self.fromField, 0, 0)
		self.layout.addWidget(self.toField, 1, 0)
		self.layout.addWidget(self.copyField, 2, 0)
		self.layout.addWidget(self.subjField, 3, 0)
		self.layout.addWidget(self.fromLine, 0, 1)
		self.layout.addWidget(self.toLine, 1, 1)
		self.layout.addWidget(self.copyLine, 2, 1)
		self.layout.addWidget(self.subjLine, 3, 1)
		self.layout.addWidget(self.send, 0, 2)
		self.layout.addWidget(self.save, 1, 2)
		self.layout.addWidget(self.attach, 2, 2)
		self.layout.addWidget(self.mailField, 4, 0, 5, 3)
		self.setLayout(self.layout)

		self.setModal(False)
		self.setWindowModality(Qt.NonModal)
		self.delAttach.connect(self.delAttachment)
		self.msgSent.connect(self.sendResult)

	def makeMessage(self):
		if ModuleExist :
			''' see for -- mailer.Message
			__init__(self, To=None, From=None, CC=None, BCC=None,
					Subject=None, Body=None, Html=None,
					Date=None, attachments=None, charset=None)
			'''
			_To = self.toLine.text().toLocal8Bit().data()
			To = findall(MAILTO_REGEXP, _To)[0]
			_From = self.fromLine.text().toLocal8Bit().data()
			From = findall(MAILTO_REGEXP, _From)[0]
			CC = self.copyLine.text().toLocal8Bit().data()
			BCC = None
			Subj = self.subjLine.text().toLocal8Bit().data()
			Body = self.mailField.toPlainText().toLocal8Bit().data()
			_Html = makeHtml(self.mailField.toPlainText())
			Html = _Html.toLocal8Bit().data()
			Date = None
			attachments = []
			for key in self.attachList :
				attachments.append(self.attachList[key])
			loadSocketModule(module = smtplib)
			reload(mailer)
			#print getattr(smtplib, '__reloaded__', None), '<< -- MAILER reloaded'
			message = mailer.Message(To, From, CC, BCC, Subj, \
					Body, Html, Date, attachments, 'utf-8')
			return message
		else :
			QMessageBox.information(self, self.tr._translate('Mail Sender'), \
					'Mailer module not available.')
			return None

	def sendMail(self):
		msg = self.makeMessage()
		if msg is None :
			QMessageBox.information(self, self.tr._translate('Mail Sender'), \
					'Message isn`t sended.')
		else :
			accName = self.Parent.Parent.getMail.data['mailBox']
			self.Parent.Parent.Settings.sync()
			self.Parent.Parent.Settings.beginGroup(accName)
			another = False
			if self.Parent.Parent.Settings.value('anotherAuthData', '0').toString() == '1' :
				another = True
			#print 'Use special authentificate data for send mail: %s' % str(another)
			if another :
				usr = self.Parent.Parent.Settings.value('sendLogin').toString().toLocal8Bit().data()
			else :
				usr = self.Parent.Parent.Settings.value('login').toString().toLocal8Bit().data()
			_host = self.Parent.Parent.Settings.value('sendServer').toString()
			_port, dig = self.Parent.Parent.Settings.value('sendPort').toString().toInt()
			authMthd = self.Parent.Parent.Settings.value('sendAuthMethod').toString().toLocal8Bit().data()
			self.Parent.Parent.Settings.endGroup()
			''' ∇∇∇            SSL&TLS don`t use both            ∇∇∇ '''
			ssl = False; tls = False;
			if authMthd.lower() == 'ssl' : ssl = True
			elif authMthd.lower() == 'tls' : tls = True
			''' ∆∆∆            SSL&TLS don`t use both            ∆∆∆ '''
			host = 'localhost' if _host.isEmpty() else _host.toLocal8Bit().data()
			port = _port if dig else 25
			if another :
				passwd = self.Parent.Parent.getMail.data['sendPass']
			else :
				passwd = self.Parent.Parent.getMail.data['password']
			#print another, usr, passwd
			answer = QMessageBox.question(self, self.tr._translate('Mail Sender'), \
					'Send to: %s\nUse: %s:%s\nMethod: %s' % \
					(msg.To, host, port, authMthd), \
					QMessageBox.Ok, QMessageBox.No)
			if answer == QMessageBox.Ok :
				self.send.setEnabled(False)
				''' see for -- mailer.Mailer
				__init__(self, host="localhost", port=0, use_tls=False,
						usr=None, pwd=None, use_ssl=False)
				'''
				sender = mailer.Mailer(host, port, tls, usr, passwd, ssl)
				self.sender = SendThread(sender, msg, self)
				self.sender.start()

	def sendResult(self, result = {}):
		if 'result' in result :
			sent = result['result'][0]
			echo = result['result'][1]
			comm = result['result'][2]
			if sent :
				QMessageBox.information(self, self.tr._translate('Mail Sender'), \
						'Message is sent.')
			else :
				QMessageBox.information(self, self.tr._translate('Mail Sender'), \
						'Message isn`t sent:\nCode:%s\n%s' % (echo, comm))
		else :
			QMessageBox.information(self, self.tr._translate('Mail Sender'), \
						'Unknown error.')
		self.send.setEnabled(True)

	def addAttachment(self):
		fileName = QFileDialog.getOpenFileName(self, 'Path_to_', '~')
		#print fileName.toLocal8Bit().data()
		i = self.layout.rowCount()
		self.attachList[i] = fileName.toLocal8Bit().data()
		self.layout.addWidget(QLabel(fileName), i, 1)
		self.layout.addWidget(DelButton(i, self), i, 2)
		self.setLayout(self.layout)

	def delAttachment(self, i):
		item1 = self.layout.itemAtPosition(i, 1)
		item1.widget().setVisible(False)
		self.layout.removeItem(item1)
		item2 = self.layout.itemAtPosition(i, 2)
		item2.widget().setVisible(False)
		self.layout.removeItem(item2)
		if i in self.attachList : del self.attachList[i]
		self.setLayout(self.layout)

	def saveAsFile(self):
		self.save.setEnabled(False)
		msg = self.makeMessage()
		if msg is None :
			QMessageBox.information(self, self.tr._translate('Mail Sender'), \
					'Message not saved.')
		else :
			#print msg.as_string()
			fileName = QFileDialog.getSaveFileName(self, 'Path_to_', '~')
			#print fileName.toLocal8Bit().data()
			if not fileName.isEmpty() :
				try :
					_name = fileName.toLocal8Bit().data()
					with open(_name, 'wb') as f :
						f.write(msg.as_string())
					QMessageBox.information(self, self.tr._translate('Mail Sender'), \
							'Message is saved in\n%s .' % _name)
				except Exception, err :
					QMessageBox.information(self, self.tr._translate('Mail Sender'), \
							'Message isn`t saved.\n%s' % str(err))
				finally : pass
		self.save.setEnabled(True)

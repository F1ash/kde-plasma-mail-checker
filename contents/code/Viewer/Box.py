# -*- coding: utf-8 -*-
#  Box.py
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
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from TextFunc import *
from Translator import Translator
from Mail import Mail
from MailFunc import imapAuth, popAuth, Settings
from Functions import dateFormat, randomString, dateStamp
from email import message_from_string
import os.path, os, shutil

SIZE=32

def emitInfo(obj, idx, cont_type, ll, data, fileName, nesting_level, boundary):
	obj.Parent.mailData.emit({\
		'number'	: idx, \
		'type'		: cont_type, \
		'data'		: (ll, data, fileName), \
		'level'		: nesting_level , \
		'boundary'	: str(boundary)})

def displayMailText(obj, msg, idx, parent_type = None, nesting_level = 0, \
					boundary = None):
	fileName = ''
	if msg.is_multipart() :
		cont_type = msg.get_content_type()
		boundary_ = msg.get_boundary()
		_boundary = boundary_ if boundary_ is None else boundary_.replace('/', '')
		if cont_type == 'message/rfc822' :
			msg = msg.get_payload()[0]
			#print msg.items()
			boundary_ = msg.get_boundary()
			_boundary = boundary_ if boundary_ is None else boundary_.replace('/', '')
			ll = '<pre><font color="red" style="background-color:yellow"><b>Type:%s<br>Level:%s<br>Boundary:%s</b></font></pre>' \
					 % (cont_type, str(nesting_level + 1), _boundary)
			Date = msg.get('Date')
			From = 'From: ' + textChain(msg.get('From'))
			Subj = 'Subj: ' + textChain(msg.get('Subject'))
			if Date is None : Date = ''
			Date = 'Date: ' + dateFormat('Date: ' + Date)
			#print Date, From, Subj, '\n'
			data = mailToString(From) + '\r\n' + Subj + '\r\n' + Date
			emitInfo(obj, idx, 'header', ll, data, fileName, nesting_level + 1, _boundary)
			_payload = msg.get_payload()
			if type(_payload) not in (list, tuple) :
				emitInfo(obj, idx, 'plain', ll, _payload, fileName, nesting_level + 1, _boundary)
				return None
		for _msg in msg.get_payload() :
			displayMailText(obj, _msg, idx, cont_type, \
							nesting_level + 1, \
							_boundary)
	else :
		main_type = msg.get_content_maintype()
		cont_type = msg.get_content_subtype()
		ll = '<pre><font color="red" style="background-color:yellow"><b>Type:%s<br>Level:%s<br>Boundary:%s</b></font></pre>' \
			  % (parent_type, str(nesting_level), boundary)
		_contCharSet = msg.get_content_charset()
		contCharSet = '' if _contCharSet is None else _contCharSet
		_content = msg.get_payload(decode=True)
		content = _content if contCharSet == '' else _content.decode(contCharSet)
		if main_type == 'text' and cont_type in ('plain', 'html') :
			data = content.replace('&quot;', '"')
		else :
			data = content
			name_ = msg.get_param('name')
			_name = '' if name_ is None else name_
			_res = msg.get('Content-ID')
			itemName = _name if _res is None else _res
			fileName = boundary + '_' + itemName.replace('<', '').replace('>', '')
			cont_type = msg.get_content_type()
		emitInfo(obj, idx, cont_type, ll, data, fileName, nesting_level, boundary)

def getMail(obj, m, protocol):
	data = obj.data
	for idx in data['ids'] :
		if not obj.key :  break
		try :
			if protocol == 'imap' :
				_Mail = m.fetch(idx,"(RFC822)")[1][0][1]
			else :
				_Mail = m.retr(idx)[1]
		except Exception, err :
			print dateStamp(), err
			_Mail = 'From: %s' % err
		finally : pass
		msg = message_from_string(_Mail)
		#print msg.items()
		Date		= msg.get('Date')
		_From		= msg.get('From')
		From		= mailToString(textChain(_From))
		_Subj		= msg.get('Subject')
		Subj		= textChain(_Subj)
		_From_Subj	= (_From, _Subj)
		ReplyTo		= msg.get('Reply-To')
		# for checking Received address uncomment below
		#Received	= msg.get('Received')
		#print Received, ' <--- received from'
		if Date is None : Date = ''
		Date = dateFormat('Date: ' + Date)
		obj.Parent.mailAttr.emit({\
			'number'	: idx, \
			'from'		: obj.Parent.tr._translate('From:') + ' ' + From, \
			'subj'		: obj.Parent.tr._translate('Subj:') + ' ' + Subj, \
			'date'		: obj.Parent.tr._translate('Date:') + ' ' + Date, \
			'ReplyTo'	: ReplyTo, \
			'_F_S'		: _From_Subj})
		displayMailText(obj, msg, idx)

def recImap4Mail(obj):
	res = True
	data = obj.data
	answer, m, idleable = imapAuth(\
			data['server'], data['port'], \
			data['login'], data['password'], \
			data['authMthd'], data['inbox'])
	if answer[0] == 'OK' :
		getMail(obj, m, 'imap')
		m.close()
	else : res = False
	if not (m is None) : m.logout()
	return res

def recPop3Mail(obj):
	res = True
	data = obj.data
	m, go = popAuth(\
			data['server'], data['port'], \
			data['login'], data['password'], \
			data['authMthd'])
	if go :
		getMail(obj, m, 'pop3')
	else : res = False
	m.quit()
	return res

def changeImagePath(data, boundary):
	''' <img src=" cid:imageName "> '''
	b = boundary + '_'
	if data.count('src=" cid:') :
		data = data.replace('src=" cid:', 'src=" %s' % b)
	if data.count('src="cid:') :
		data = data.replace('src="cid:', 'src=" %s' % b)
	if data.count('src= " cid:') :
		data = data.replace('src= " cid:', 'src=" %s' % b)
	return data

class GetMail(QThread):
	def __init__(self, data = {}, parent = None):
		QThread.__init__(self, parent)
		self.key = True
		self.data = data
		self.Parent = parent

	def run(self):
		if self.data['connMthd'].count('imap') :
			receiveMail = recImap4Mail
		else :
			receiveMail = recPop3Mail
		res = receiveMail(self)
		if res :
			self.Parent.Parent.statusBar.showMessage(self.Parent.tr._translate('Job completed.'))
		else :
			self.Parent.Parent.statusBar.showMessage(self.Parent.tr._translate('Job completed with error.'))

	def stop(self):
		self.key = False

	def __del__(self): self.stop

class Box(QTabWidget):
	mailAttr = pyqtSignal(dict)
	mailData = pyqtSignal(dict)
	def __init__(self, data = {}, parent = None):
		QTabWidget.__init__(self, parent)
		self.Parent = parent
		self.tr = Translator('mailViewer')
		self.mails = []
		self.webViewWDGs = []
		self.iconDatabasePath = os.path.join('/tmp', randomString(24))
		os.mkdir(self.iconDatabasePath)
		self.Settings = Settings

		self.setMovable(True)
		self.setIconSize(QSize(SIZE, SIZE))

		if 'ids' in data and len(data['ids']) :
			i = 0
			for idx in data['ids'] :
				self.mails.append(Mail(idx, self))

				self.addTab(self.mails[i], QIcon().fromTheme("mail"), QString(self.tr._translate('Mail') + ' ' + idx))
				self.setTabToolTip(i, self.tr._translate('Mail') + ' #' + idx)
				i += 1
			self.Parent.statusBar.showMessage(self.tr._translate('Getting mail...'))
			self.mailAttr.connect(self.setMailAttr)
			self.mailData.connect(self.setMailData)
			self.getMail = GetMail(data, self)
			self.getMail.start()
		else :
			self.Parent.statusBar.showMessage(self.tr._translate('Empty Job.'))

	def setMailAttr(self, d):
		i = 0
		for m in self.mails :
			if m.idx == d['number'] : break
			else : i += 1
		self.mails[i].fromField.setText(d['from'])
		self.mails[i].subjField.setText(d['subj'])
		self.mails[i].dateField.setText(d['date'])
		self.mails[i].reply_to = d['ReplyTo']
		self.mails[i]._from_subj = d['_F_S']

	def setMailData(self, d):
		ll = d['data'][0]
		data = d['data'][1]
		i = 0
		for m in self.mails :
			if m.idx == d['number'] : break
			else : i += 1
		fileName = None
		if d['type'] == 'html' :
			_data = changeImagePath(data, d['boundary'])
			''' create temporary html-file '''
			fileName = os.path.join(self.iconDatabasePath, randomString(24) + '.html')
			with open(fileName, 'w') as f : f.write(_data.encode('utf-32'))
			wdg = QWebView()
			wdg.triggerPageAction(QWebPage.Reload, True)
			wdg.triggerPageAction(QWebPage.Stop, True)
			wdg.triggerPageAction(QWebPage.Back, True)
			wdg.triggerPageAction(QWebPage.Forward, True)
			wdg.settings().setAttribute(QWebSettings.AutoLoadImages, \
										self.Parent.autoLoadImage)
			wdg.settings().setAttribute(QWebSettings.PrivateBrowsingEnabled, \
										self.Parent.privateEnable)
			if wdg.settings().iconDatabasePath().isEmpty() :
				wdg.settings().setIconDatabasePath(self.iconDatabasePath)
			wdg.load(QUrl('file://' + fileName))
			#print dateStamp(), QUrl('file://' + fileName), '  created'
			wdg.show()
			self.webViewWDGs.append(wdg)
		elif d['type'] in ('plain') :
			wdg = QTextBrowser()
			wdg.setAcceptRichText(True)
			wdg.setOpenExternalLinks(True)
			wdg.setOpenLinks(True)
			data = data.replace('<', '&lt; ')
			data = data.replace('>', ' &gt;')
			wdg.setHtml(changeLink(data))
		elif d['type'] == 'header' :
			wdg = QLabel()
			wdg.setText(data)
			wdg.linkHovered.connect(self.linkDisplay)
			wdg.setAlignment(Qt.AlignLeft)
		else :
			''' create temporary file '''
			fileName = os.path.join(self.iconDatabasePath, d['data'][2])
			with open(fileName, 'wb') as f : f.write(data)
			wdg = QLabel()
			wdg.setOpenExternalLinks(True)
			ins = self.tr._translate('Inserted:')
			wdg.setText(QString('<a href="%1">%2 %3</a>').arg(fileName).arg(ins).arg(d['type']))
			wdg.linkHovered.connect(self.linkDisplay)
			wdg.setAlignment(Qt.AlignLeft)
		wdg.setToolTip(ll)
		splt = QSplitter()
		splt.setOrientation(Qt.Horizontal)
		splt.setChildrenCollapsible(True)
		if d['level'] :
			blank = QLabel()
			blank.setFixedWidth(d['level']*SIZE)
			splt.addWidget(blank)
		splt.addWidget(wdg)
		self.mails[i].mailField.addWidget(splt)
		self.mails[i].setLayout(self.mails[i].layout)

	def linkDisplay(self, s):
		self.Parent.statusBar.showMessage(s)

	def __del__(self):
		shutil.rmtree(self.iconDatabasePath)

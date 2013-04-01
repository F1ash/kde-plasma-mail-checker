# -*- coding: utf-8 -*-
#  AkonadiObjects.py
#  
#  Copyright 2013 Flash <kaperang07@gmail.com>
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

from PyQt4.QtCore import *
from Functions import dateStamp, htmlWrapper
from MailFunc import losedBlank, codeDetect
from AkonadiMod import Akonadi
import string

StateSTR = { 0 : 'NotRunning', 1 : 'Starting', 2 : 'Running', 3 : 'Stopping', 4 : 'Broken' }

class ItemFetchJob(Akonadi.ItemFetchJob):
	def __init__(self, col, id_ = 0, parent = None):
		Akonadi.ItemFetchJob.__init__(self, col, parent)

		self.prnt = parent
		self.id_ = id_
		self.nameKey = str(col.id())
		self.result['KJob*'].connect( self.jobFinished )
		self.fetchScope().fetchPayloadPart(QByteArray('HEAD'), True)

	def jobFinished(self, job):
		## print self.id_, '  ID search :\n'
		data = []
		for item in job.items() :
			if item.id() == self.id_ :
				## print item.payloadData().data(), '  common enter data'
				data = string.split(item.payloadData().data(), '\n')
				## delete whitelines
				for str_ in ['', ' ', '\t', '\r', '\n'] :
					for i in xrange(data.count(str_)) :
						data.remove(str_)
				i = 0
				for str_ in data :
					l = len(str_)
					if str_.endswith('\r') : data[i] = str_[:(l-1)]
					i += 1
				## for str_ in data : print str_ , ' ==='
				break
		""" self.nameKey -- collection id, self.id_ -- item id """
		self.prnt.jobFinished( data, self.nameKey, self.id_ )

class AkonadiMonitor(QObject):
	def __init__(self, timeout = '3', parent = None):
		QObject.__init__(self, parent)
		self.Parent = parent
		self.timeout = int(str(timeout)) * 1000
		self.Settings = self.Parent.Settings
		self.mailAttrToSTR = self.Parent.someFunctions.mailAttrToSTR

		self.monitor = Akonadi.Monitor()
		self.monitor.fetchCollection(True)
		self.monitor.fetchCollectionStatistics(True)
		if not self.connect(self.monitor, \
				SIGNAL("itemAdded(const Akonadi::Item&, const Akonadi::Collection&)"), \
				self.printItemAttr) :
			print dateStamp(), ' Signal "itemAdded" not connected'
		#self.initAccounts()
		self.Timer = QTimer()
		self.Timer.setSingleShot(True)
		self.Timer.timeout.connect(self.popupShow)

	@pyqtSlot('const Akonadi::Item&', 'const Akonadi::Collection&', name = 'printItemAttr')
	def printItemAttr(self, item, col):
		#print dateStamp(), '\n\tadded in ', col.name().toUtf8(), \
		#		' with ID : ', col.id(), '<- col : item ->',  item.id(), '\tRes: ', col.resource()

		job = ItemFetchJob( col, item.id(), self )

	def jobFinished(self, data, nameKey, id_):
		if self.Timer.isActive() :
			#print '  stop Timer'
			self.Timer.stop()
		else :
			#print '  Timer not Active'
			self.pointers_to_new_Items = {}
			self.count = 0
		i = 0
		dataString = ['', '', '']; count = len(data); headerCode = ''
		for str_ in data :
			if str_[:5] == 'Date:' :
				dataString[0] += str_ + '\r\n'
			elif str_[:5] == 'From:' :
				dataString[1] += losedBlank(str_) + ' \r\n'
				From = True
				j = i
				while From and j < (count - 1) :
					next_str = data[j+1]
					if next_str[:1] in ['\t', ' ', '\n'] :
						dataString[1] += losedBlank(next_str) + ' \r\n'
					else :
						From = False
					j += 1
			elif str_[:8] == 'Subject:' :
				dataString[2] += losedBlank(str_) + ' \r\n'
				Subj = True
				j = i
				while Subj and j < (count - 1) :
					next_str = data[j+1]
					if next_str[:1] in ['\t', ' ', '\n'] :
						dataString[2] += losedBlank(next_str) + ' \r\n'
					else :
						Subj = False
					j += 1
			elif (str_[:13].lower() == 'content-type:') and (string.find(str_.lower(), 'text/plain') > -1) :
				Code = True
				headerCode = codeDetect(str_)
				if headerCode == '' :
					j = i
					while Code and j < (count - 1) :
						next_str = data[j+1]
						if next_str[:1] in ['\t', ' ', '\n'] :
							headerCode = codeDetect(next_str)
							if headerCode != '' : break
						else :
							Code = False
						j += 1
			i += 1
		## add "\r\n" once, because dataString[2] contain "\r\n" already
		str_ = string.join(dataString, '') + '\r\n'

		self.count += 1
		STR_ = ''
		""" nameKey -- collection id, id_ -- item id
			distinction by source
		"""
		for _str in string.split(str_, '\r\n\r\n') :
			if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
				STR_ += htmlWrapper(self.mailAttrToSTR(_str, headerCode), self.Parent.mailAttrColor) + '\n'
		var = self.pointers_to_new_Items.pop(nameKey, {})
		var[ id_ ] = STR_
		self.pointers_to_new_Items[ nameKey ] = var
		self.Timer.start( self.timeout )

	def popupShow(self):
		for name_ in self.pointers_to_new_Items.keys() :
			STR_ = ''; id_ = []
			for _id in self.pointers_to_new_Items[name_].keys() :
				STR_ += self.pointers_to_new_Items[name_][_id]
				id_ += [_id]
			self.Parent.eventNotification('<b><u>' + self.Parent.tr._translate('New Message(s) :') + '</u></b>' + \
						'\n' + self.Parent.tr._translate('In ') + \
						self.Parent.fieldBoxPref + self.nameList[name_][0] + self.Parent.fieldBoxSuff + ':\n' + \
						STR_, {name_ : min(id_)}, self.nameList[name_][1])

	def initAccounts(self):
		self.accList = self.Parent.akonadiAccountList()
		self.collResourceList = QStringList()
		self.collNameList = QStringList()
		self.collCommList = QStringList()
		self.collIdList = QStringList()
		self.collEnableList = []
		self.Settings.beginGroup('Akonadi account')
		for str_ in self.accList :
			data = string.split( self.Settings.value(str_).toString(), ' <||> ' )
			if data.count() < 1 :
				data += ['', '0', '', '', '']
			elif data.count() < 2 :
				data += ['0', '', '', '']
			elif data.count() < 3 :
				data += ['', '', '']
			elif data.count() < 4 :
				data += ['', '']
			elif data.count() < 5 :
				data += ['%dir_id %mail_id']
			##print dateStamp(), str_.toUtf8(), data[0], data[1]
			self.collIdList.append(data[0])
			self.collEnableList += [ data[1] ]
			self.collResourceList.append(data[2])
			self.collNameList.append(data[3])
			self.collCommList.append(data[4])
		#for i in xrange(self.accList.count()) :
		#	print self.collResourceList[i], self.collEnableList[i]
		self.Settings.endGroup()
		""" Get all collections and that matched for id, name,
			and resource of the collection transmit to the monitor.
			If there were changes, print a warning about reinitialization
			of specific accounts.
		"""
		self.job = \
				Akonadi.CollectionFetchJob( Akonadi.Collection.root(), Akonadi.CollectionFetchJob.Recursive, self)
		self.connect( self.job, SIGNAL('result(KJob*)'), self.collectionsFetched )

	def collectionsFetched(self, job):
		self.nameList = {}
		brokenItemList = QStringList()
		listJobColl = job.collections()
		j = 0
		for i in xrange( self.accList.count() ) :
			itemBroken = True
			for col in listJobColl :
				if self.collResourceList[i] == col.resource() and \
							self.collNameList[i] == col.name() :
					if self.collIdList[i] == str(col.id()) :
						itemBroken = False
						if self.collEnableList[ i ] == '1' :
							self.monitor.setCollectionMonitored(col)
							self.nameList[ str( col.id() ) ] = (self.accList[i], self.collCommList[i])
						j += 1
						break
			if itemBroken :
				brokenItemList.append(self.accList[i])
		if j == 0 and self.accList.count() != 0 :
			self.errorMessage()
		elif not brokenItemList.isEmpty() :
			self.errorMessage(brokenItemList)
		#for col in self.monitor.collectionsMonitored() :
		#	print dateStamp(), col.resource(), '\t', col.id(), '\t', col.name().toUtf8() + '\t', '  monitored'

	def __del__(self):
		for col in self.monitor.collectionsMonitored() :
			self.monitor.setCollectionMonitored(col, False)
			## print dateStamp(), col.resource(), '\t', col.name().toUtf8() + '\t', ' not monitored'
		self.monitor.session().clear()
		del self.monitor
		del self.job
		del self.Timer

	def errorMessage(self, something = 0):
		if type(something) is int :
			#print dateStamp(), 'Your accounts are invalid. You must reinit them.'
			self.Parent.eventNotification('Your accounts are invalid.\nYou must reinit them.')
		else :
			STR = ''
			for str_ in something :
				STR += str_ + '\nThis account is invalid.\n'
				#print dateStamp(), str_.toUtf8(), '\t is involid.'
			self.Parent.eventNotification(STR)

	def syncCollection(self):
		agentManager = Akonadi.AgentManager.self()
		for col in self.monitor.collectionsMonitored() :
			agentManager.synchronizeCollection(col)
		#self.Parent.eventNotification('')

class ControlWidget(Akonadi.CollectionDialog):
	def __init__(self, parent = None):
		Akonadi.CollectionDialog.__init__(self, parent)
		self.setMimeTypeFilter( QStringList() << QString("message/rfc822") )
		self.setAccessRightsFilter( Akonadi.Collection.CanCreateItem )

	def eventClose(self):
		self.done(0)

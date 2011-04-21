# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from Functions import dateStamp, htmlWrapper, mailAttrToSTR
from main import Settings
import os.path, time, string
try :
	ModuleExist = True
	from PyKDE4.akonadi import Akonadi
except :
	print 'PyKDE4.akonadi module not available.'
	ModuleExist = False
finally :
	pass

StateSTR = { 0 : 'NotRunning', 1 : 'Starting', 2 : 'Running', 3 : 'Stopping', 4 : 'Broken' }

def akonadiAccountList():
	Settings.beginGroup('Akonadi account')
	accList = Settings.allKeys()
	Settings.endGroup()
	return accList

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
				## print item.payloadData().data()
				data += string.split(item.payloadData().data(), '\n')
				break
		self.prnt.jobFinished( data, self.nameKey )

class AkonadiMonitor(QObject):
	def __init__(self, parent = None):
		QObject.__init__(self, parent)
		self.Parent = parent
		self.monitoredCollection = []

		self.monitor = Akonadi.Monitor()
		self.monitor.fetchCollection(True)
		self.monitor.fetchCollectionStatistics(True)
		if not self.connect(self.monitor, \
				SIGNAL("itemAdded(const Akonadi::Item&, const Akonadi::Collection&)"), \
				self.printItemAttr) :
			print dateStamp(), ' Signal "itemAdded" not connected'
		#self.initAccounts()

	@pyqtSlot('const Akonadi::Item&', 'const Akonadi::Collection&', name = 'printItemAttr')
	def printItemAttr(self, item, col):
		print dateStamp(), '\n\tadded in ', col.name().toUtf8(), \
				' with ID : ', col.id(), '<- col : item ->',  item.id()

		job = ItemFetchJob( col, item.id(), self )

	def jobFinished(self, data, id_):
		i = 0
		dataString = ''
		for str_ in data :
			if str_[:5] == 'Date:' :
				dataString += str_ + '\r\n'
			elif str_[:5] == 'From:' :
				dataString += str_ + '\r\n'
			elif str_[:8] == 'Subject:' :
				dataString += str_
				Subj = True
				j = i
				while Subj :
					next_str = data[j+1]
					if next_str[:1] in ['\t', ' ', '\r\n'] :
						dataString += next_str + ' \r\n '
					else :
						Subj = False
					j += 1
			i += 1
		str_ = dataString + '\r\n\r\n'
		STR_ = ''
		for _str in string.split(str_, '\r\n\r\n') :
			if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
				STR_ += '\n' + self.Parent.tr._translate('In ') + \
						self.Parent.fieldBoxPref + self.nameList[id_] + self.Parent.fieldBoxSuff + ':\n' + \
						htmlWrapper(mailAttrToSTR(_str), self.Parent.mailAttrColor) + '\n'
		self.Parent.eventNotification('<b><u>' + self.Parent.tr._translate('New Massage(s) :') + '</u></b>' + STR_)

	def initAccounts(self):
		global Settings
		self.accList = akonadiAccountList()
		self.collResourceList = QStringList()
		self.collEnableList = []
		Settings.beginGroup('Akonadi account')
		for str_ in self.accList :
			data = string.split( Settings.value(str_).toString(), ' <||> ' )
			if data.count() < 2 :
				data += ['0']
			##print dateStamp(), str_.toUtf8(), data[0], data[1]
			self.collResourceList.append(data[0])
			self.collEnableList += [ data[1] ]
		#for i in xrange(accList.count()) :
		#	print self.collResourceList[i], self.collEnableList[i]
		Settings.endGroup()
		""" получить все коллекции и, совпадающие по id, запустить
		"""
		self.job = \
				Akonadi.CollectionFetchJob( Akonadi.Collection.root(), Akonadi.CollectionFetchJob.Recursive, self)
		self.connect( self.job, SIGNAL('result(KJob*)'), self.collectionsFetched )

	def collectionsFetched(self, job):
		self.nameList = {}
		for col in job.collections() :
			i = self.collResourceList.indexOf( str(col.id()) )
			#print str(col.id()), i
			if self.collResourceList.contains(str(col.id())) and self.collEnableList[ i ] == '1' :
				self.monitor.setCollectionMonitored(col)
				self.nameList[ str( col.id() ) ] = self.accList[i]
		for col in self.monitor.collectionsMonitored() :
			##print dateStamp(), col.resource(), '\t', col.name().toUtf8() + '\t', '  monitored'
			self.monitoredCollection += [col]

	def __del__(self):
		for col in self.monitor.collectionsMonitored() :
			self.monitor.setCollectionMonitored(col, False)
			## print dateStamp(), col.resource(), '\t', col.name().toUtf8() + '\t', ' not monitored'
		del self.monitor
		del self.job

	def syncCollection(self):
		agentManager = Akonadi.AgentManager.self()
		for col in self.monitoredCollection :
			agentManager.synchronizeCollection(col)

class ControlWidget(Akonadi.CollectionDialog):
	def __init__(self, parent = None):
		Akonadi.CollectionDialog.__init__(self, parent)
		self.setMimeTypeFilter( QStringList() << QString("message/rfc822") )
		self.setAccessRightsFilter( Akonadi.Collection.CanCreateItem )

	def eventClose(self):
		self.done(0)

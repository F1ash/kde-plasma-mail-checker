# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from PyKDE4.kdecore import *
import locale, os.path

class Translator(QTranslator):
	def __init__(self, context = '', parent=None):
		QTranslator.__init__(self, parent)

		lang = locale.getdefaultlocale()[0][:2]
		_Path = self.user_or_sys(lang + '.qm')
		#print 'Tr:' ,  lang, _Path
		self.load(QString(lang), QString(_Path), QString('qm'))
		self.context = context

	def user_or_sys(self, path_):
		kdehome = unicode(KGlobal.dirs().localkdedir())
		var1 = kdehome + 'share/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/code/'
		var2 = '/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-mail-checker/contents/code/'
		if os.path.exists(var2 + path_) :
			return var2
		elif os.path.exists(var1 + path_) :
			return var1
		else :
			return kdehome

	def _translate(self, sourceText):
		res = self.translate(self.context, sourceText)
		#print res, 'tr:', self.context, sourceText
		if len(res) == 0:
			res = QString(sourceText)
		return res

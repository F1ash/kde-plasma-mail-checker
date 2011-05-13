# -*- coding: utf-8 -*-

from PyQt4.QtCore import QString
from PyQt4.QtGui import QWidget, QTextEdit, QGridLayout
import string

class Examples(QWidget):
	def __init__(self, path_ = '', parent = None):
		QWidget.__init__(self, parent)

		browseText = QTextEdit()
		browseText.setReadOnly(True)

		with open(path_,'rU') as f :
			data_ = f.readlines()
		raw_data = string.join(data_)
		megadata = QString.fromUtf8(raw_data)
		browseText.setText(megadata)

		form = QGridLayout()
		form.addWidget(browseText,0,0)
		self.setLayout(form)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

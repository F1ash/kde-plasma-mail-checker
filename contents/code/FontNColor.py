#  FontNColor.py
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
from PyQt4.QtGui import *
from Translator import Translator
import string

class Font_n_Colour(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		self.prnt = parent
		self.Settings = self.Parent.Settings
		self.checkAccess = self.Parent.checkAccess
		self.tr = Translator('Font_n_Colour')

		self.headerFontVar = self.initValue('headerFont', ' ')
		self.headerSizeVar = self.initValue('headerSize')
		self.headerBoldVar = self.initValue('headerBold')
		self.headerItalVar = self.initValue('headerItal')
		self.headerColourVar = self.initValue('headerColour')

		self.accountFontVar = self.initValue('accountFont', ' ')
		self.accountSizeVar = self.initValue('accountSize')
		self.accountBoldVar = self.initValue('accountBold')
		self.accountItalVar = self.initValue('accountItal')
		self.accountColourVar = self.initValue('accountColour')
		self.accountSFontVar = self.initValue('accountSFont', ' ')
		self.accountSSizeVar = self.initValue('accountSSize')
		self.accountSBoldVar = self.initValue('accountSBold')
		self.accountSItalVar = self.initValue('accountSItal')
		self.accountSColourVar = self.initValue('accountSColour')

		self.accountToolTipFontVar = self.initValue('accountToolTipFont', ' ')
		self.accountToolTipSizeVar = self.initValue('accountToolTipSize')
		self.accountToolTipBoldVar = self.initValue('accountToolTipBold')
		self.accountToolTipItalVar = self.initValue('accountToolTipItal')
		self.accountToolTipColourVar = self.initValue('accountToolTipColour')
		self.accountToolTipSFontVar = self.initValue('accountToolTipSFont', ' ')
		self.accountToolTipSSizeVar = self.initValue('accountToolTipSSize')
		self.accountToolTipSBoldVar = self.initValue('accountToolTipSBold')
		self.accountToolTipSItalVar = self.initValue('accountToolTipSItal')
		self.accountToolTipSColourVar = self.initValue('accountToolTipSColour')

		self.countFontVar = self.initValue('countFont', ' ')
		self.countSizeVar = self.initValue('countSize')
		self.countBoldVar = self.initValue('countBold')
		self.countItalVar = self.initValue('countItal')
		self.countColourVar = self.initValue('countColour')
		self.countSFontVar = self.initValue('countSFont', ' ')
		self.countSSizeVar = self.initValue('countSSize')
		self.countSBoldVar = self.initValue('countSBold')
		self.countSItalVar = self.initValue('countSItal')
		self.countSColourVar = self.initValue('countSColour')

		self.countToolTipFontVar = self.initValue('countToolTipFont', ' ')
		self.countToolTipSizeVar = self.initValue('countToolTipSize')
		self.countToolTipBoldVar = self.initValue('countToolTipBold')
		self.countToolTipItalVar = self.initValue('countToolTipItal')
		self.countToolTipColourVar = self.initValue('countToolTipColour')
		self.countToolTipSFontVar = self.initValue('countToolTipSFont', ' ')
		self.countToolTipSSizeVar = self.initValue('countToolTipSSize')
		self.countToolTipSBoldVar = self.initValue('countToolTipSBold')
		self.countToolTipSItalVar = self.initValue('countToolTipSItal')
		self.countToolTipSColourVar = self.initValue('countToolTipSColour')

		self.fieldBoxFontVar = self.initValue('fieldBoxFont', ' ')
		self.fieldBoxSizeVar = self.initValue('fieldBoxSize')
		self.fieldBoxBoldVar = self.initValue('fieldBoxBold')
		self.fieldBoxItalVar = self.initValue('fieldBoxItal')
		self.fieldBoxColourVar = self.initValue('fieldBoxColour')

		self.fieldFromFontVar = self.initValue('fieldFromFont', ' ')
		self.fieldFromSizeVar = self.initValue('fieldFromSize')
		self.fieldFromBoldVar = self.initValue('fieldFromBold')
		self.fieldFromItalVar = self.initValue('fieldFromItal')
		self.fieldFromColourVar = self.initValue('fieldFromColour')

		self.fieldSubjFontVar = self.initValue('fieldSubjFont', ' ')
		self.fieldSubjSizeVar = self.initValue('fieldSubjSize')
		self.fieldSubjBoldVar = self.initValue('fieldSubjBold')
		self.fieldSubjItalVar = self.initValue('fieldSubjItal')
		self.fieldSubjColourVar = self.initValue('fieldSubjColour')

		self.fieldDateFontVar = self.initValue('fieldDateFont', ' ')
		self.fieldDateSizeVar = self.initValue('fieldDateSize')
		self.fieldDateBoldVar = self.initValue('fieldDateBold')
		self.fieldDateItalVar = self.initValue('fieldDateItal')
		self.fieldDateColourVar = self.initValue('fieldDateColour')

		self.headerColourStyle = self.getRGBaStyle(QString(self.headerColourVar).toUInt())
		self.accountColourStyle = self.getRGBaStyle(QString(self.accountColourVar).toUInt())
		self.accountSColourStyle = self.getRGBaStyle(QString(self.accountSColourVar).toUInt())
		self.accountToolTipColourStyle = self.getRGBaStyle(QString(self.accountToolTipColourVar).toUInt())
		self.accountToolTipSColourStyle = self.getRGBaStyle(QString(self.accountToolTipSColourVar).toUInt())
		self.countColourStyle = self.getRGBaStyle(QString(self.countColourVar).toUInt())
		self.countSColourStyle = self.getRGBaStyle(QString(self.countSColourVar).toUInt())
		self.countToolTipColourStyle = self.getRGBaStyle(QString(self.countToolTipColourVar).toUInt())
		self.countToolTipSColourStyle = self.getRGBaStyle(QString(self.countToolTipSColourVar).toUInt())
		self.fieldBoxColourStyle = self.getRGBaStyle(QString(self.fieldBoxColourVar).toUInt())
		self.fieldFromColourStyle = self.getRGBaStyle(QString(self.fieldFromColourVar).toUInt())
		self.fieldSubjColourStyle = self.getRGBaStyle(QString(self.fieldSubjColourVar).toUInt())
		self.fieldDateColourStyle = self.getRGBaStyle(QString(self.fieldDateColourVar).toUInt())

		self.fontIcon = QIcon().fromTheme("font")
		self.colourIcon = QIcon().fromTheme("color")

		self.init()

	def init(self):
		self.layout = QGridLayout()

		self.label1 = QLabel(self.tr._translate("Normal"))
		self.label2 = QLabel(self.tr._translate("Select"))
		self.label1.setMaximumHeight(30)
		self.label2.setMaximumHeight(30)
		self.layout.addWidget(self.label1, 0, 0)
		self.layout.addWidget(self.label2, 0, 5)

		prefix, suffix = self.cursive_n_bold(self.headerBoldVar, self.headerItalVar)
		self.headerFontLabel = QLabel('<font face="' + self.headerFontVar + \
											'">' + prefix + self.tr._translate('Header :') + suffix + '</font>')
		self.headerFontLabel.setStyleSheet(self.headerColourStyle)
		self.layout.addWidget(self.headerFontLabel, 1, 0)

		self.headerFontButton = QPushButton(self.fontIcon, '')
		self.headerFontButton.setToolTip('Font')
		self.headerFontButton.clicked.connect(self.headerFont)
		self.layout.addWidget(self.headerFontButton, 1, 1)

		self.headerColourButton = QPushButton(self.colourIcon, '')
		self.headerColourButton.setToolTip('Color')
		self.connect(self.headerColourButton, SIGNAL('clicked()'), self.headerColour)
		self.layout.addWidget(self.headerColourButton, 1, 2)

		prefix, suffix = self.cursive_n_bold(self.accountBoldVar, self.accountItalVar)
		self.accountFontLabel = QLabel('<font face="' + \
						self.accountFontVar + '">' + prefix + self.tr._translate('Account :') + suffix + '</font>')
		self.accountFontLabel.setStyleSheet(self.accountColourStyle)
		self.layout.addWidget(self.accountFontLabel, 2, 0)
		prefix, suffix = self.cursive_n_bold(self.accountSBoldVar, self.accountSItalVar)
		self.accountSFontLabel = QLabel('<font face="' + self.accountSFontVar + \
												'">' + prefix + self.tr._translate('Account :') + suffix + '</font>')
		self.accountSFontLabel.setStyleSheet(self.accountSColourStyle)
		self.layout.addWidget(self.accountSFontLabel, 2, 5)

		self.accountFontButton = QPushButton(self.fontIcon, '')
		self.accountFontButton.setToolTip('Font')
		self.connect(self.accountFontButton, SIGNAL('clicked()'), self.accountFont)
		self.layout.addWidget(self.accountFontButton, 2, 1)

		self.accountColourButton = QPushButton(self.colourIcon, '')
		self.accountColourButton.setToolTip('Color')
		self.connect(self.accountColourButton, SIGNAL('clicked()'), self.accountColour)
		self.layout.addWidget(self.accountColourButton, 2, 2)

		self.accountSFontButton = QPushButton(self.fontIcon, '')
		self.accountSFontButton.setToolTip('Font')
		self.connect(self.accountSFontButton, SIGNAL('clicked()'), self.accountSFont)
		self.layout.addWidget(self.accountSFontButton, 2, 3)

		self.accountSColourButton = QPushButton(self.colourIcon, '')
		self.accountSColourButton.setToolTip('Color')
		self.connect(self.accountSColourButton, SIGNAL('clicked()'), self.accountSColour)
		self.layout.addWidget(self.accountSColourButton, 2, 4)

		prefix, suffix = self.cursive_n_bold(self.accountToolTipBoldVar, self.accountToolTipItalVar)
		self.accountToolTipFontLabel = QLabel('<font face="' + self.accountToolTipFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')
		self.accountToolTipFontLabel.setStyleSheet(self.accountToolTipColourStyle)
		self.layout.addWidget(self.accountToolTipFontLabel, 3, 0)
		prefix, suffix = self.cursive_n_bold(self.accountToolTipSBoldVar, self.accountToolTipSItalVar)
		self.accountToolTipSFontLabel = QLabel('<font face="' + self.accountToolTipSFontVar + '">' + \
											prefix + self.tr._translate('Account\nToolTip :') + suffix + '</font>')
		self.accountToolTipSFontLabel.setStyleSheet(self.accountToolTipSColourStyle)
		self.layout.addWidget(self.accountToolTipSFontLabel, 3, 5)

		self.accountToolTipFontButton = QPushButton(self.fontIcon, '')
		self.accountToolTipFontButton.setToolTip('Font')
		self.connect(self.accountToolTipFontButton, SIGNAL('clicked()'), self.accountToolTipFont)
		self.layout.addWidget(self.accountToolTipFontButton, 3, 1)

		self.accountToolTipColourButton = QPushButton(self.colourIcon, '')
		self.accountToolTipColourButton.setToolTip('Color')
		self.connect(self.accountToolTipColourButton, SIGNAL('clicked()'), self.accountToolTipColour)
		self.layout.addWidget(self.accountToolTipColourButton, 3, 2)

		self.accountToolTipSFontButton = QPushButton(self.fontIcon, '')
		self.accountToolTipSFontButton.setToolTip('Font')
		self.connect(self.accountToolTipSFontButton, SIGNAL('clicked()'), self.accountToolTipSFont)
		self.layout.addWidget(self.accountToolTipSFontButton, 3, 3)

		self.accountToolTipSColourButton = QPushButton(self.colourIcon, '')
		self.accountToolTipSColourButton.setToolTip('Color')
		self.connect(self.accountToolTipSColourButton, SIGNAL('clicked()'), self.accountToolTipSColour)
		self.layout.addWidget(self.accountToolTipSColourButton, 3, 4)

		prefix, suffix = self.cursive_n_bold(self.countBoldVar, self.countItalVar)
		self.countFontLabel = QLabel('<font face="' + self.countFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')
		self.countFontLabel.setStyleSheet(self.countColourStyle)
		self.layout.addWidget(self.countFontLabel, 4, 0)
		prefix, suffix = self.cursive_n_bold(self.countSBoldVar, self.countSItalVar)
		self.countSFontLabel = QLabel('<font face="' + self.countSFontVar + \
											'">' + prefix + self.tr._translate('count :') + suffix + '</font>')
		self.countSFontLabel.setStyleSheet(self.countSColourStyle)
		self.layout.addWidget(self.countSFontLabel, 4, 5)

		self.countFontButton = QPushButton(self.fontIcon, '')
		self.countFontButton.setToolTip('Font')
		self.connect(self.countFontButton, SIGNAL('clicked()'), self.countFont)
		self.layout.addWidget(self.countFontButton, 4, 1)

		self.countColourButton = QPushButton(self.colourIcon, '')
		self.countColourButton.setToolTip('Color')
		self.connect(self.countColourButton, SIGNAL('clicked()'), self.countColour)
		self.layout.addWidget(self.countColourButton, 4, 2)

		self.countSFontButton = QPushButton(self.fontIcon, '')
		self.countSFontButton.setToolTip('Font')
		self.connect(self.countSFontButton, SIGNAL('clicked()'), self.countSFont)
		self.layout.addWidget(self.countSFontButton, 4, 3)

		self.countSColourButton = QPushButton(self.colourIcon, '')
		self.countSColourButton.setToolTip('Color')
		self.connect(self.countSColourButton, SIGNAL('clicked()'), self.countSColour)
		self.layout.addWidget(self.countSColourButton, 4, 4)

		prefix, suffix = self.cursive_n_bold(self.countToolTipBoldVar, self.countToolTipItalVar)
		self.countToolTipFontLabel = QLabel('<font face="' + self.countToolTipFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')
		self.countToolTipFontLabel.setStyleSheet(self.countToolTipColourStyle)
		self.layout.addWidget(self.countToolTipFontLabel, 5, 0)
		prefix, suffix = self.cursive_n_bold(self.countToolTipSBoldVar, self.countToolTipSItalVar)
		self.countToolTipSFontLabel = QLabel('<font face="' + self.countToolTipSFontVar + '">' + \
											prefix + self.tr._translate('count\nToolTip :') + suffix + '</font>')
		self.countToolTipSFontLabel.setStyleSheet(self.countToolTipSColourStyle)
		self.layout.addWidget(self.countToolTipSFontLabel, 5, 5)

		self.countToolTipFontButton = QPushButton(self.fontIcon, '')
		self.countToolTipFontButton.setToolTip('Font')
		self.connect(self.countToolTipFontButton, SIGNAL('clicked()'), self.countToolTipFont)
		self.layout.addWidget(self.countToolTipFontButton, 5, 1)

		self.countToolTipColourButton = QPushButton(self.colourIcon, '')
		self.countToolTipColourButton.setToolTip('Color')
		self.connect(self.countToolTipColourButton, SIGNAL('clicked()'), self.countToolTipColour)
		self.layout.addWidget(self.countToolTipColourButton, 5, 2)

		self.countToolTipSFontButton = QPushButton(self.fontIcon, '')
		self.countToolTipSFontButton.setToolTip('Font')
		self.connect(self.countToolTipSFontButton, SIGNAL('clicked()'), self.countToolTipSFont)
		self.layout.addWidget(self.countToolTipSFontButton, 5, 3)

		self.countToolTipSColourButton = QPushButton(self.colourIcon, '')
		self.countToolTipSColourButton.setToolTip('Color')
		self.connect(self.countToolTipSColourButton, SIGNAL('clicked()'), self.countToolTipSColour)
		self.layout.addWidget(self.countToolTipSColourButton, 5, 4)

		prefix, suffix = self.cursive_n_bold(self.fieldBoxBoldVar, self.fieldBoxItalVar)
		self.fieldBoxFontLabel = QLabel('<font face="' + self.fieldBoxFontVar + \
											'">' + prefix + self.tr._translate('field Box :') + suffix + '</font>')
		self.fieldBoxFontLabel.setStyleSheet(self.fieldBoxColourStyle)
		self.layout.addWidget(self.fieldBoxFontLabel, 6, 0)

		self.fieldBoxFontButton = QPushButton(self.fontIcon, '')
		self.fieldBoxFontButton.setToolTip('Font')
		self.fieldBoxFontButton.clicked.connect(self.fieldBoxFont)
		self.layout.addWidget(self.fieldBoxFontButton, 6, 1)

		self.fieldBoxColourButton = QPushButton(self.colourIcon, '')
		self.fieldBoxColourButton.setToolTip('Color')
		self.connect(self.fieldBoxColourButton, SIGNAL('clicked()'), self.fieldBoxColour)
		self.layout.addWidget(self.fieldBoxColourButton, 6, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldFromBoldVar, self.fieldFromItalVar)
		self.fieldFromFontLabel = QLabel('<font face="' + self.fieldFromFontVar + \
											'">' + prefix + self.tr._translate('field From :') + suffix + '</font>')
		self.fieldFromFontLabel.setStyleSheet(self.fieldFromColourStyle)
		self.layout.addWidget(self.fieldFromFontLabel, 7, 0)

		self.fieldFromFontButton = QPushButton(self.fontIcon, '')
		self.fieldFromFontButton.setToolTip('Font')
		self.fieldFromFontButton.clicked.connect(self.fieldFromFont)
		self.layout.addWidget(self.fieldFromFontButton, 7, 1)

		self.fieldFromColourButton = QPushButton(self.colourIcon, '')
		self.fieldFromColourButton.setToolTip('Color')
		self.connect(self.fieldFromColourButton, SIGNAL('clicked()'), self.fieldFromColour)
		self.layout.addWidget(self.fieldFromColourButton, 7, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldSubjBoldVar, self.fieldSubjItalVar)
		self.fieldSubjFontLabel = QLabel('<font face="' + self.fieldSubjFontVar + \
											'">' + prefix + self.tr._translate('field Subj :') + suffix + '</font>')
		self.fieldSubjFontLabel.setStyleSheet(self.fieldSubjColourStyle)
		self.layout.addWidget(self.fieldSubjFontLabel, 8, 0)

		self.fieldSubjFontButton = QPushButton(self.fontIcon, '')
		self.fieldSubjFontButton.setToolTip('Font')
		self.fieldSubjFontButton.clicked.connect(self.fieldSubjFont)
		self.layout.addWidget(self.fieldSubjFontButton, 8, 1)

		self.fieldSubjColourButton = QPushButton(self.colourIcon, '')
		self.fieldSubjColourButton.setToolTip('Color')
		self.connect(self.fieldSubjColourButton, SIGNAL('clicked()'), self.fieldSubjColour)
		self.layout.addWidget(self.fieldSubjColourButton, 8, 2)

		prefix, suffix = self.cursive_n_bold(self.fieldDateBoldVar, self.fieldDateItalVar)
		self.fieldDateFontLabel = QLabel('<font face="' + self.fieldDateFontVar + \
											'">' + prefix + self.tr._translate('field Date :') + suffix + '</font>')
		self.fieldDateFontLabel.setStyleSheet(self.fieldDateColourStyle)
		self.layout.addWidget(self.fieldDateFontLabel, 9, 0)

		self.fieldDateFontButton = QPushButton(self.fontIcon, '')
		self.fieldDateFontButton.setToolTip('Font')
		self.fieldDateFontButton.clicked.connect(self.fieldDateFont)
		self.layout.addWidget(self.fieldDateFontButton, 9, 1)

		self.fieldDateColourButton = QPushButton(self.colourIcon, '')
		self.fieldDateColourButton.setToolTip('Color')
		self.connect(self.fieldDateColourButton, SIGNAL('clicked()'), self.fieldDateColour)
		self.layout.addWidget(self.fieldDateColourButton, 9, 2)

		self.setLayout(self.layout)

	def initValue(self, key_, defaultValue = ''):
		if self.Settings.contains(key_) :
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return self.Settings.value(key_).toString()
		else :
			if defaultValue == '' :
				defaultValue = self.getSystemColor('int')
			self.Settings.setValue(key_, QVariant(defaultValue))
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return defaultValue

	def getSystemColor(self, key_ = ''):
		currentBrush = QPalette().windowText()
		colour = currentBrush.color()
		if key_ == 'int' :
			#print dateStamp() ,  colour.rgba()
			return str(colour.rgba())
		else :
			#print dateStamp() ,  str(colour.getRgb())
			return str(colour.getRgb())

	def cursive_n_bold(self, bold, italic):
		pref = ''
		suff = ''
		if bold == '1' :
			pref += '<b>'; suff += '</b>'
		if italic == '1' :
			pref = '<i>' + pref; suff += '</i>'
		return pref, suff

	def getFont(self, currentFont):
		font = QFontDialog()
		selectFont, yes = font.getFont(currentFont)
		str_ = string.split(selectFont.key(), ',')
		b = '0'; i = '0'
		if selectFont.bold() : b = '1'
		if selectFont.italic() : i = '1'
		font.done(0)
		return str_[0], str_[1], b, i, yes

	def getRGBaStyle(self, (colour, yes)):
		if yes :
			style = 'QLabel { color: rgba' + str(QColor().fromRgba(colour).getRgb()) + ';} '
		else :
			style = 'QLabel { color: rgba' + self.getSystemColor() + ';} '
		return style

	def getColour(self, (currentColour, yes)):
		colour = QColorDialog()
		selectColour, _yes = colour.getRgba(currentColour)
		colour.done(0)
		return str(selectColour), _yes, self.getRGBaStyle((selectColour, _yes))

	def headerFont(self):
		self.headerSizeVar, \
			self.headerColourStyle, \
			self.headerBoldVar, \
			self.headerItalVar, \
			self.headerFontLabel, \
			self.headerFontVar = \
		self.templateMethodForFont( \
			self.headerSizeVar, \
			self.headerColourStyle, \
			self.headerBoldVar, \
			self.headerItalVar, \
			self.headerFontLabel, \
			self.headerFontVar, \
			'Header :')

	def headerColour(self):
			self.headerColourVar, \
			self.headerColourStyle, \
			self.headerBoldVar, \
			self.headerItalVar, \
			self.headerFontLabel, \
			self.headerFontVar = \
		self.templateMethodForColor( \
			self.headerColourVar, \
			self.headerColourStyle, \
			self.headerBoldVar, \
			self.headerItalVar, \
			self.headerFontLabel, \
			self.headerFontVar, \
			'Header :')

	def fieldBoxFont(self):
		self.fieldBoxSizeVar, \
			self.fieldBoxColourStyle, \
			self.fieldBoxBoldVar, \
			self.fieldBoxItalVar, \
			self.fieldBoxFontLabel, \
			self.fieldBoxFontVar = \
		self.templateMethodForFont( \
			self.fieldBoxSizeVar, \
			self.fieldBoxColourStyle, \
			self.fieldBoxBoldVar, \
			self.fieldBoxItalVar, \
			self.fieldBoxFontLabel, \
			self.fieldBoxFontVar, \
			'field Box :')

	def fieldBoxColour(self):
		self.fieldBoxColourVar, \
			self.fieldBoxColourStyle, \
			self.fieldBoxBoldVar, \
			self.fieldBoxItalVar, \
			self.fieldBoxFontLabel, \
			self.fieldBoxFontVar = \
		self.templateMethodForColor( \
			self.fieldBoxColourVar, \
			self.fieldBoxColourStyle, \
			self.fieldBoxBoldVar, \
			self.fieldBoxItalVar, \
			self.fieldBoxFontLabel, \
			self.fieldBoxFontVar, \
			'field Box :')

	def fieldFromFont(self):
		self.fieldFromSizeVar, \
			self.fieldFromColourStyle, \
			self.fieldFromBoldVar, \
			self.fieldFromItalVar, \
			self.fieldFromFontLabel, \
			self.fieldFromFontVar = \
		self.templateMethodForFont( \
			self.fieldFromSizeVar, \
			self.fieldFromColourStyle, \
			self.fieldFromBoldVar, \
			self.fieldFromItalVar, \
			self.fieldFromFontLabel, \
			self.fieldFromFontVar, \
			'field From :')

	def fieldFromColour(self):
		self.fieldFromColourVar, \
			self.fieldFromColourStyle, \
			self.fieldFromBoldVar, \
			self.fieldFromItalVar, \
			self.fieldFromFontLabel, \
			self.fieldFromFontVar = \
		self.templateMethodForColor( \
			self.fieldFromColourVar, \
			self.fieldFromColourStyle, \
			self.fieldFromBoldVar, \
			self.fieldFromItalVar, \
			self.fieldFromFontLabel, \
			self.fieldFromFontVar, \
			'field From :')

	def fieldSubjFont(self):
		self.fieldSubjSizeVar, \
			self.fieldSubjColourStyle, \
			self.fieldSubjBoldVar, \
			self.fieldSubjItalVar, \
			self.fieldSubjFontLabel, \
			self.fieldSubjFontVar = \
		self.templateMethodForFont( \
			self.fieldSubjSizeVar, \
			self.fieldSubjColourStyle, \
			self.fieldSubjBoldVar, \
			self.fieldSubjItalVar, \
			self.fieldSubjFontLabel, \
			self.fieldSubjFontVar, \
			'field Subj :')

	def fieldSubjColour(self):
		self.fieldSubjColourVar, \
			self.fieldSubjColourStyle, \
			self.fieldSubjBoldVar, \
			self.fieldSubjItalVar, \
			self.fieldSubjFontLabel, \
			self.fieldSubjFontVar = \
		self.templateMethodForColor( \
			self.fieldSubjColourVar, \
			self.fieldSubjColourStyle, \
			self.fieldSubjBoldVar, \
			self.fieldSubjItalVar, \
			self.fieldSubjFontLabel, \
			self.fieldSubjFontVar, \
			'field Subj :')

	def fieldDateFont(self):
		self.fieldDateSizeVar, \
			self.fieldDateColourStyle, \
			self.fieldDateBoldVar, \
			self.fieldDateItalVar, \
			self.fieldDateFontLabel, \
			self.fieldDateFontVar = \
		self.templateMethodForFont( \
			self.fieldDateSizeVar, \
			self.fieldDateColourStyle, \
			self.fieldDateBoldVar, \
			self.fieldDateItalVar, \
			self.fieldDateFontLabel, \
			self.fieldDateFontVar, \
			'field Date :')

	def fieldDateColour(self):
		self.fieldDateColourVar, \
			self.fieldDateColourStyle, \
			self.fieldDateBoldVar, \
			self.fieldDateItalVar, \
			self.fieldDateFontLabel, \
			self.fieldDateFontVar = \
		self.templateMethodForColor( \
			self.fieldDateColourVar, \
			self.fieldDateColourStyle, \
			self.fieldDateBoldVar, \
			self.fieldDateItalVar, \
			self.fieldDateFontLabel, \
			self.fieldDateFontVar, \
			'field Date :')

	def accountFont(self):
		self.accountSizeVar, \
			self.accountColourStyle, \
			self.accountBoldVar, \
			self.accountItalVar, \
			self.accountFontLabel, \
			self.accountFontVar = \
		self.templateMethodForFont( \
			self.accountSizeVar, \
			self.accountColourStyle, \
			self.accountBoldVar, \
			self.accountItalVar, \
			self.accountFontLabel, \
			self.accountFontVar, \
			'Account :')

	def accountColour(self):
		self.accountColourVar, \
			self.accountColourStyle, \
			self.accountBoldVar, \
			self.accountItalVar, \
			self.accountFontLabel, \
			self.accountFontVar = \
		self.templateMethodForColor( \
			self.accountColourVar, \
			self.accountColourStyle, \
			self.accountBoldVar, \
			self.accountItalVar, \
			self.accountFontLabel, \
			self.accountFontVar, \
			'Account :')

	def accountSFont(self):
		self.accountSSizeVar, \
			self.accountSColourStyle, \
			self.accountSBoldVar, \
			self.accountSItalVar, \
			self.accountSFontLabel, \
			self.accountSFontVar = \
		self.templateMethodForFont( \
			self.accountSSizeVar, \
			self.accountSColourStyle, \
			self.accountSBoldVar, \
			self.accountSItalVar, \
			self.accountSFontLabel, \
			self.accountSFontVar, \
			'Account :')

	def accountSColour(self):
		self.accountSColourVar, \
			self.accountSColourStyle, \
			self.accountSBoldVar, \
			self.accountSItalVar, \
			self.accountSFontLabel, \
			self.accountSFontVar = \
		self.templateMethodForColor( \
			self.accountSColourVar, \
			self.accountSColourStyle, \
			self.accountSBoldVar, \
			self.accountSItalVar, \
			self.accountSFontLabel, \
			self.accountSFontVar, \
			'Account :')

	def accountToolTipFont(self):
		self.accountToolTipSizeVar, \
			self.accountToolTipColourStyle, \
			self.accountToolTipBoldVar, \
			self.accountToolTipItalVar, \
			self.accountToolTipFontLabel, \
			self.accountToolTipFontVar = \
		self.templateMethodForFont( \
			self.accountToolTipSizeVar, \
			self.accountToolTipColourStyle, \
			self.accountToolTipBoldVar, \
			self.accountToolTipItalVar, \
			self.accountToolTipFontLabel, \
			self.accountToolTipFontVar, \
			'Account\nToolTip :')

	def accountToolTipColour(self):
		self.accountToolTipColourVar, \
			self.accountToolTipColourStyle, \
			self.accountToolTipBoldVar, \
			self.accountToolTipItalVar, \
			self.accountToolTipFontLabel, \
			self.accountToolTipFontVar = \
		self.templateMethodForColor( \
			self.accountToolTipColourVar, \
			self.accountToolTipColourStyle, \
			self.accountToolTipBoldVar, \
			self.accountToolTipItalVar, \
			self.accountToolTipFontLabel, \
			self.accountToolTipFontVar, \
			'Account\nToolTip :')

	def accountToolTipSFont(self):
		self.accountToolTipSSizeVar, \
			self.accountToolTipSColourStyle, \
			self.accountToolTipSBoldVar, \
			self.accountToolTipSItalVar, \
			self.accountToolTipSFontLabel, \
			self.accountToolTipSFontVar = \
		self.templateMethodForFont( \
			self.accountToolTipSSizeVar, \
			self.accountToolTipSColourStyle, \
			self.accountToolTipSBoldVar, \
			self.accountToolTipSItalVar, \
			self.accountToolTipSFontLabel, \
			self.accountToolTipSFontVar, \
			'Account\nToolTip :')

	def accountToolTipSColour(self):
		self.accountToolTipSColourVar, \
			self.accountToolTipSColourStyle, \
			self.accountToolTipSBoldVar, \
			self.accountToolTipSItalVar, \
			self.accountToolTipSFontLabel, \
			self.accountToolTipSFontVar = \
		self.templateMethodForColor( \
			self.accountToolTipSColourVar, \
			self.accountToolTipSColourStyle, \
			self.accountToolTipSBoldVar, \
			self.accountToolTipSItalVar, \
			self.accountToolTipSFontLabel, \
			self.accountToolTipSFontVar, \
			'Account\nToolTip :')

	def countFont(self):
		self.countSizeVar, \
			self.countColourStyle, \
			self.countBoldVar, \
			self.countItalVar, \
			self.countFontLabel, \
			self.countFontVar = \
		self.templateMethodForFont( \
			self.countSizeVar, \
			self.countColourStyle, \
			self.countBoldVar, \
			self.countItalVar, \
			self.countFontLabel, \
			self.countFontVar, \
			'count :')

	def countColour(self):
		self.countColourVar, \
			self.countColourStyle, \
			self.countBoldVar, \
			self.countItalVar, \
			self.countFontLabel, \
			self.countFontVar = \
		self.templateMethodForColor( \
			self.countColourVar, \
			self.countColourStyle, \
			self.countBoldVar, \
			self.countItalVar, \
			self.countFontLabel, \
			self.countFontVar, \
			'count :')

	def countSFont(self):
		self.countSSizeVar, \
			self.countSColourStyle, \
			self.countSBoldVar, \
			self.countSItalVar, \
			self.countSFontLabel, \
			self.countSFontVar = \
		self.templateMethodForFont( \
			self.countSSizeVar, \
			self.countSColourStyle, \
			self.countSBoldVar, \
			self.countSItalVar, \
			self.countSFontLabel, \
			self.countSFontVar, \
			'count :')

	def countSColour(self):
		self.countSColourVar, \
			self.countSColourStyle, \
			self.countSBoldVar, \
			self.countSItalVar, \
			self.countSFontLabel, \
			self.countSFontVar = \
		self.templateMethodForColor( \
			self.countSColourVar, \
			self.countSColourStyle, \
			self.countSBoldVar, \
			self.countSItalVar, \
			self.countSFontLabel, \
			self.countSFontVar, \
			'count :')

	def countToolTipFont(self):
		self.countToolTipSizeVar, \
			self.countToolTipColourStyle, \
			self.countToolTipBoldVar, \
			self.countToolTipItalVar, \
			self.countToolTipFontLabel, \
			self.countToolTipFontVar = \
		self.templateMethodForFont( \
			self.countToolTipSizeVar, \
			self.countToolTipColourStyle, \
			self.countToolTipBoldVar, \
			self.countToolTipItalVar, \
			self.countToolTipFontLabel, \
			self.countToolTipFontVar, \
			'count\nToolTip :')

	def countToolTipColour(self):
		self.countToolTipColourVar, \
			self.countToolTipColourStyle, \
			self.countToolTipBoldVar, \
			self.countToolTipItalVar, \
			self.countToolTipFontLabel, \
			self.countToolTipFontVar = \
		self.templateMethodForColor( \
			self.countToolTipColourVar, \
			self.countToolTipColourStyle, \
			self.countToolTipBoldVar, \
			self.countToolTipItalVar, \
			self.countToolTipFontLabel, \
			self.countToolTipFontVar, \
			'count\nToolTip :')

	def countToolTipSFont(self):
		self.countToolTipSSizeVar, \
			self.countToolTipSColourStyle, \
			self.countToolTipSBoldVar, \
			self.countToolTipSItalVar, \
			self.countToolTipSFontLabel, \
			self.countToolTipSFontVar = \
		self.templateMethodForFont( \
			self.countToolTipSSizeVar, \
			self.countToolTipSColourStyle, \
			self.countToolTipSBoldVar, \
			self.countToolTipSItalVar, \
			self.countToolTipSFontLabel, \
			self.countToolTipSFontVar, \
			'count\nToolTip :')

	def countToolTipSColour(self):
		self.countToolTipSColourVar, \
			self.countToolTipSColourStyle, \
			self.countToolTipSBoldVar, \
			self.countToolTipSItalVar, \
			self.countToolTipSFontLabel, \
			self.countToolTipSFontVar = \
		self.templateMethodForColor( \
			self.countToolTipSColourVar, \
			self.countToolTipSColourStyle, \
			self.countToolTipSBoldVar, \
			self.countToolTipSItalVar, \
			self.countToolTipSFontLabel, \
			self.countToolTipSFontVar, \
			'count\nToolTip :')

	def templateMethodForFont(self, SizeVar, ColourStyle, BoldVar, \
									 ItalVar, FontLabel, FontVar, _template):
		font, size, bold, ital, yes = self.getFont(QFont(FontVar))
		if yes :
			FontVar, SizeVar, BoldVar, ItalVar =  font, size, bold, ital
			prefix, suffix = self.cursive_n_bold(BoldVar, ItalVar)
			FontLabel.clear()
			FontLabel.setStyleSheet(ColourStyle)
			FontLabel.setText('<font face="' + FontVar + '">' + \
							  prefix + self.tr._translate(_template) + \
							  suffix + '</font>')
		return SizeVar, ColourStyle, BoldVar, ItalVar, FontLabel, FontVar

	def templateMethodForColor(self, ColourVar, ColourStyle, BoldVar, \
									 ItalVar, FontLabel, FontVar, _template):
		colour, yes, style = self.getColour(QString(ColourVar).toUInt())
		if yes :
			ColourVar = colour
			ColourStyle = style
			prefix, suffix = self.cursive_n_bold(BoldVar, ItalVar)
			FontLabel.clear()
			FontLabel.setStyleSheet(style)
			FontLabel.setText('<font face="' + FontVar + '">' + \
							  prefix + self.tr._translate(_template) + \
							  suffix + '</font>')
		return ColourVar, ColourStyle, BoldVar, ItalVar, FontLabel, FontVar

	def refreshSettings(self):
		if not self.checkAccess() : return None

		self.Settings.setValue('headerFont', self.headerFontVar)
		self.Settings.setValue('headerSize', self.headerSizeVar)
		self.Settings.setValue('headerBold', self.headerBoldVar)
		self.Settings.setValue('headerItal', self.headerItalVar)
		self.Settings.setValue('headerColour', self.headerColourVar)

		self.Settings.setValue('countFont', self.countFontVar)
		self.Settings.setValue('countSize', self.countSizeVar)
		self.Settings.setValue('countBold', self.countBoldVar)
		self.Settings.setValue('countItal', self.countItalVar)
		self.Settings.setValue('countColour', self.countColourVar)
		self.Settings.setValue('countSFont', self.countSFontVar)
		self.Settings.setValue('countSSize', self.countSSizeVar)
		self.Settings.setValue('countSBold', self.countSBoldVar)
		self.Settings.setValue('countSItal', self.countSItalVar)
		self.Settings.setValue('countSColour', self.countSColourVar)

		self.Settings.setValue('accountFont', self.accountFontVar)
		self.Settings.setValue('accountSize', self.accountSizeVar)
		self.Settings.setValue('accountBold', self.accountBoldVar)
		self.Settings.setValue('accountItal', self.accountItalVar)
		self.Settings.setValue('accountColour', self.accountColourVar)
		self.Settings.setValue('accountSFont', self.accountSFontVar)
		self.Settings.setValue('accountSSize', self.accountSSizeVar)
		self.Settings.setValue('accountSBold', self.accountSBoldVar)
		self.Settings.setValue('accountSItal', self.accountSItalVar)
		self.Settings.setValue('accountSColour', self.accountSColourVar)

		self.Settings.setValue('accountToolTipFont', self.accountToolTipFontVar)
		self.Settings.setValue('accountToolTipSize', self.accountToolTipSizeVar)
		self.Settings.setValue('accountToolTipBold', self.accountToolTipBoldVar)
		self.Settings.setValue('accountToolTipItal', self.accountToolTipItalVar)
		self.Settings.setValue('accountToolTipColour', self.accountToolTipColourVar)
		self.Settings.setValue('accountToolTipSFont', self.accountToolTipSFontVar)
		self.Settings.setValue('accountToolTipSSize', self.accountToolTipSSizeVar)
		self.Settings.setValue('accountToolTipSBold', self.accountToolTipSBoldVar)
		self.Settings.setValue('accountToolTipSItal', self.accountToolTipSItalVar)
		self.Settings.setValue('accountToolTipSColour', self.accountToolTipSColourVar)

		self.Settings.setValue('countToolTipFont', self.countToolTipFontVar)
		self.Settings.setValue('countToolTipSize', self.countToolTipSizeVar)
		self.Settings.setValue('countToolTipBold', self.countToolTipBoldVar)
		self.Settings.setValue('countToolTipItal', self.countToolTipItalVar)
		self.Settings.setValue('countToolTipColour', self.countToolTipColourVar)
		self.Settings.setValue('countToolTipSFont', self.countToolTipSFontVar)
		self.Settings.setValue('countToolTipSSize', self.countToolTipSSizeVar)
		self.Settings.setValue('countToolTipSBold', self.countToolTipSBoldVar)
		self.Settings.setValue('countToolTipSItal', self.countToolTipSItalVar)
		self.Settings.setValue('countToolTipSColour', self.countToolTipSColourVar)

		self.Settings.setValue('fieldBoxFont', self.fieldBoxFontVar)
		self.Settings.setValue('fieldBoxSize', self.fieldBoxSizeVar)
		self.Settings.setValue('fieldBoxBold', self.fieldBoxBoldVar)
		self.Settings.setValue('fieldBoxItal', self.fieldBoxItalVar)
		self.Settings.setValue('fieldBoxColour', self.fieldBoxColourVar)

		self.Settings.setValue('fieldFromFont', self.fieldFromFontVar)
		self.Settings.setValue('fieldFromSize', self.fieldFromSizeVar)
		self.Settings.setValue('fieldFromBold', self.fieldFromBoldVar)
		self.Settings.setValue('fieldFromItal', self.fieldFromItalVar)
		self.Settings.setValue('fieldFromColour', self.fieldFromColourVar)

		self.Settings.setValue('fieldSubjFont', self.fieldSubjFontVar)
		self.Settings.setValue('fieldSubjSize', self.fieldSubjSizeVar)
		self.Settings.setValue('fieldSubjBold', self.fieldSubjBoldVar)
		self.Settings.setValue('fieldSubjItal', self.fieldSubjItalVar)
		self.Settings.setValue('fieldSubjColour', self.fieldSubjColourVar)

		self.Settings.setValue('fieldDateFont', self.fieldDateFontVar)
		self.Settings.setValue('fieldDateSize', self.fieldDateSizeVar)
		self.Settings.setValue('fieldDateBold', self.fieldDateBoldVar)
		self.Settings.setValue('fieldDateItal', self.fieldDateItalVar)
		self.Settings.setValue('fieldDateColour', self.fieldDateColourVar)

		self.Settings.sync()

	def eventClose(self, event):
		self.prnt.done(0)

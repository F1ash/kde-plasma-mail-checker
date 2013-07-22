#  TextFunc.py
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
# -*- coding: utf-8 -*-

import string
from re import findall
from Functions import decodeMailSTR

SINTAX_SIGN = ('.',',',':',';','<','>','?','\\','[',']','(',')','\'','^','@','%','+','-','=','*','$','#','~','`', '"')
URL_REGEXP = r'[abefghilnmpstvw]*://+[\S]*'
#r'[abefghilnmpstvw]*://(?:[a-zA-Z]|[0-9]|[$-_@.&+?=:#~]|[!*\(\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
MAILTO_REGEXP = r'[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*[a-zA-Z]'

def textChain(text, contCharSet = ''):
	if len(text.split('\r\n')) : d = '\r\n'
	elif len(text.split('\n')) : d = '\n'
	else : d = ''
	chains = []
	for chain in text.split(d) :
		_chain = decodeMailSTR(chain, contCharSet).replace('&quot;', '"')
		if type(_chain) not in (str, unicode) : _chain = chain
		chains.append(_chain)
	return string.join(chains, d)

def mailToString(str_):
	items = []
	for item in findall(MAILTO_REGEXP, str_) :
		if item not in items : items.append(item)
	if len(items) : str_ = '<a href="mailto: %s">%s</a>' % (items[0], str_)
	return str_

def maximize(l):
	_l = []
	while len(l) :
		i = max(l)
		if i not in _l : _l.append(i)
		l.remove(i)
	return _l

def cleanUrlItem(t):
	while t[-1:] in SINTAX_SIGN :
		_t = t[:-1]
		t = _t
	return t

def worker(_REGEXP, data, _template):
	items = []
	for item in findall(_REGEXP, data) :
		if item not in items :
			if _REGEXP == URL_REGEXP :
				item = cleanUrlItem(item)
			items.append(item)
	items = maximize(items)
	for item in items :
		#print item, _template % (item, item)
		""" search same items """
		same = []
		for _item in items :
			if _item != item and _item.startswith(item) :
				same.append(_item)
		same = maximize(same)
		if len(same) :
			for _item in same :
				data = data.replace(_item, '<||%s||>' % items.index(_item))
		data = data.replace(item, _template % (item, item))
		if len(same) :
			for _item in same :
				data = data.replace('<||%s||>' % items.index(_item), _item)
	return data

def changeLink(data):
	data = worker(URL_REGEXP, data, '<a href="%s">%s</a>')
	data = worker(MAILTO_REGEXP, data, '<a href="mailto: %s">%s</a>')
	data = data.replace('\r\n', '<br>')
	data = data.replace('\n', '<br>')
	data = data.replace('\t', '&#09;')
	return data

def insertMetaData(data):
	res = None
	insert_after = 0
	meta = "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />\n"
	if not len(data) :
		return data
	while data[0] in string.whitespace :
		data = data[1:]
	if data.startswith("<!DOCTYPE") :
		insert_after = data.find(">") + 1
	if data.startswith("<html") :
		insert_after = data.find(">", insert_after) + 1
	if data.startswith("<head") :
		insert_after = data.find(">", insert_after) + 1
	if data.count(meta[:-12]) :
		res = data
	else :
		head = data[:insert_after]
		tail = data[insert_after:]
		res = ''.join((head, meta, tail))
	return res

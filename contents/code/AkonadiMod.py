# -*- coding: utf-8 -*-
#  AkonadiMod.py
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

import os.path
import PyKDE4

def reloadAkonadiModule():
	res = False
	try :
		reload (PyKDE4)
		fn = os.path.join(PyKDE4.__path__[0], 'akonadi.so')
		res = os.path.isfile(fn)
	except Exception, err:
		print "[in AkonadiMod error]: %s" % err
	finally : pass
	return res

AkonadiModuleExist = reloadAkonadiModule()
if AkonadiModuleExist :
	from PyKDE4.akonadi import Akonadi
	from AkonadiObjects import *

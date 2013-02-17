#  WaitIdle.py
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

from PyQt4.QtCore import QThread

class WaitIdle(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self, parent)

		self.Parent = parent
		self.key = False

	def run(self):
		while not self.key and len(self.Parent.idleMailingList) :
			for item in self.Parent.idleMailingList :
				if not item.runned : item.__del__()
			self.msleep(200)
		self.Parent.idleingStopped.emit()

	def __del__(self):
		self.key = True
		self.quit()

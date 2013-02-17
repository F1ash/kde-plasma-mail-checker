# -*- coding: utf-8 -*-
#  mail.py
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

from MailFunc import checkMail, QString
import sys, os, os.path

if __name__ == '__main__':
	#sys.stdout = open('/tmp/threadMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
	account, fileName = sys.argv[1], sys.argv[2]
	if os.path.isfile('/dev/shm/' + fileName) :
		with open('/dev/shm/' + fileName, 'rb') as f: l = f.read()
		with open('/dev/shm/' + fileName, 'wb') as f: f.write(''.join(['' for i in xrange(len(l))]))
		os.remove('/dev/shm/' + fileName)
		while l.endswith('\n') : l.remove('\n')
		passw = l
	else : passw = ''
	#print dateStamp(), (account, passw, fileName), '  thread'
	if (account, passw) == ('','') :
		Result = (False, 0, 0, '', '', '', '-', '')
	else :
		Result = ( checkMail( [account, passw] ) )
	suff = ['.Result', '.all', '.new', '.msg', '.content', '.encoding', '.unRead', '.Ids']
	#print Result, ' -- Result in mail.py'
	for i in xrange(len(suff)) :
		f = open('/dev/shm/' + fileName + suff[i], 'w')
		if type(Result[i]) is bool or type(Result[i]) is int :
			res_ = str(Result[i])
		elif type(Result[i]) is str :
			res_ = Result[i]
		else :
			res_ = QString(Result[i]).toUtf8().data()
		f.write(res_)
		f.close()
	#sys.stdout.close()

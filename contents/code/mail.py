# -*- coding: utf-8 -*-

from MailFunc import *
from Functions import randomString
import sys, os, os.path

if __name__ == '__main__':
	#sys.stdout = open('/tmp/threadMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
	account, fileName = sys.argv[1], sys.argv[2]
	if os.path.isfile('/dev/shm/' + fileName) :
		with open('/dev/shm/' + fileName, 'rb') as f: l = f.read()
		with open('/dev/shm/' + fileName, 'wb') as f: f.write(randomString(48))
		os.remove('/dev/shm/' + fileName)
		while l.endswith('\n') : l.remove('\n')
		passw = l
	else : passw = ''
	#print dateStamp(), (account, passw, fileName), '  thread'
	if (account, passw) == ('','') :
		Result = (False, 0, 0, '', '', '', '-')
	else :
		loadSocketModule()
		Result = ( checkMail( [account, passw] ) )
	suff = ['.Result', '.all', '.new', '.msg', '.content', '.encoding', '.unRead']
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

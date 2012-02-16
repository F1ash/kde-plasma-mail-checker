# -*- coding: utf-8 -*-

from MailFunc import *
import sys

if __name__ == '__main__':
	#sys.stdout = open('/tmp/threadMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
	account, passw, fileName = sys.argv[1], sys.argv[2], sys.argv[3]
	#print dateStamp(), account, passw, fileName, '  thread'
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

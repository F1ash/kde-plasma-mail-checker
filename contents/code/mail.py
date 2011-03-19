# -*- coding: utf-8 -*-

from Functions import *

if __name__ == '__main__':
	account, passw, fileName = sys.argv[1], sys.argv[2], sys.argv[3]
	#print account, passw, fileName, '  thread'
	Result = ( checkMail( [account, passw] ) )
	suff = ['.Result', '.all', '.new', '.msg', '.content']
	for i in xrange(5) :
		f = open('/dev/shm/' + fileName + suff[i], 'w')
		if type(Result[i]) is bool or type(Result[i]) is int :
			res_ = str(Result[i])
		else :
			res_ = Result[i]
		f.write(res_)
		f.close

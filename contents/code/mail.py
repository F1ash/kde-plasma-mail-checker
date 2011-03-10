# -*- coding: utf-8 -*-

from main import *

if __name__ == '__main__':
	account, passw, fileName = sys.argv[1], sys.argv[2], sys.argv[3]
	#print account, passw, fileName, '  thread'
	Result = ( checkMail( [account, passw] ) )
	suff = ['.Result', '.all', '.new', '.msg']
	for i in xrange(4) :
		f = open('/dev/shm/' + fileName + suff[i], 'wb')
		f.write(str(Result[i]))
		f.close

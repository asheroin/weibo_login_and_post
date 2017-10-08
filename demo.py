# -*- coding: utf-8 -*-
import re
import json
import base64
import binascii
import itertools
import os
import json
import datetime
import sys
import time

from weibo import WeiboClient as wb
from operator import itemgetter

ISOTIMEFORMAT='%Y-%m-%d %X'



def loop(weibo_client):
	second = sleeptime(0,0,1)
	for index,value in enumerate(pipes):
		if index < 175:
			continue
		while True:
			try:
				time.sleep(second)
				second = sleeptime(0,0,30)
			except KeyboardInterrupt,e:
				print "[{}]ctrl-c.".format(ss)
				sys.exit()
			except Exception,e:
				ss = time.strftime( ISOTIMEFORMAT, time.localtime() )
				print "[{}]Unkonw error occured.".format(ss)
				print Exception,":",e
				sys.exit()

			try:
				now = datetime.datetime.now()
				if(now.minute%5 == 0):
					# do something
					weibo_client.postText('some text',[])
					ss = time.strftime( ISOTIMEFORMAT, time.localtime() )
					print "[{}]successfully post {}.".format(ss,index)
					second = sleeptime(0,1,0)
					break
			except KeyboardInterrupt,e:
				print "[{}]ctrl-c.".format(ss)
				sys.exit()
			except Exception,e:
				ss = time.strftime( ISOTIMEFORMAT, time.localtime() )
				print "[{}]Unkonw error occured.".format(ss)
				print Exception,":",e
			else:
				ss = time.strftime( ISOTIMEFORMAT, time.localtime() )
				print "[{}]Wake up once.".format(ss)



if __name__ == '__main__':
	weibo_client = wb()
	weibo_client.wblogin(YOUR_ACCOUNT, PASS_WORD)
	weibo_client.postText('pure text',[])
	weibo_client.postText('imgs',['img1.jpg','img2.jpg'])
  # or a Weibo timer
  # loop(weibo_client)

# -*- coding: utf-8 -*-
import re
import json
import base64
import binascii

import rsa
import requests

import logging
import time
import urllib
import urllib2
import urlparse 
import datetime


class WeiboClient(object):
	def __init__(self):
		# general variable
		self.WBCLIENT = 'ssologin.js(v1.4.15)'
		self.user_agent = (
		    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
		    'Chrome/20.0.1132.57 Safari/536.11'
		)
		# create session
		self.session = requests.session()
		self.session.headers['User-Agent'] = self.user_agent


		ISOTIMEFORMAT='%Y-%m-%d %X'

		TIMEFORMAT2 = '%X'

		self.picHeader = self.session.headers
		self.textHeader = self.session.headers


	def encrypt_passwd(self,passwd, pubkey, servertime, nonce):
	    key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
	    message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
	    passwd = rsa.encrypt(message.encode('utf-8'), key)
	    return binascii.b2a_hex(passwd)


	def wblogin(self,username, password):
	    resp = self.session.get(
	        'http://login.sina.com.cn/sso/prelogin.php?'
	        'entry=sso&callback=sinaSSOController.preloginCallBack&'
	        'su=%s&rsakt=mod&client=%s' %
	        (base64.b64encode(username.encode('utf-8')), self.WBCLIENT)
	    )

	    pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)
	    pre_login = json.loads(pre_login_str)

	    pre_login = json.loads(pre_login_str)
	    data = {
	        'entry': 'weibo',
	        'gateway': 1,
	        'from': '',
	        'savestate': 7,
	        'userticket': 1,
	        'ssosimplelogin': 1,
	        'su': base64.b64encode(requests.utils.quote(username).encode('utf-8')),
	        'service': 'miniblog',
	        'servertime': pre_login['servertime'],
	        'nonce': pre_login['nonce'],
	        'vsnf': 1,
	        'vsnval': '',
	        'pwencode': 'rsa2',
	        'sp': self.encrypt_passwd(password, pre_login['pubkey'],
	                             pre_login['servertime'], pre_login['nonce']),
	        'rsakv' : pre_login['rsakv'],
	        'encoding': 'UTF-8',
	        'prelt': '115',
	        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.si'
	               'naSSOController.feedBackUrlCallBack',
	        'returntype': 'META'
	    }
	    resp = self.session.post(
	        'http://login.sina.com.cn/sso/login.php?client=%s' % self.WBCLIENT,
	        data=data
	    )

	    login_url = re.search(r'replace\([\"\']([^\'\"]+)[\"\']',\
	                          resp.text).group(1)
	    resp = self.session.get(login_url)
	    re_pattern = re.compile(r'\((.*?)\)')
	    re_result = re_pattern.findall(resp.text)
	    rsp = json.loads(re_result[0])
	    uid = rsp['userinfo']['uniqueid']

	    # FIXME: uid
	    self.session.headers["Referer"] = "http://weibo.com/u/{}/home?topnav=1&wvr=6".format(uid)
	    self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
	    self.session.headers['Connection'] = 'keep-alive'
	    # save headers
	    self.picHeader = self.session.headers
	    self.textHeader = self.session.headers

	    self.picHeader['Host'] = 'picupload.weibo.com'
	    self.picHeader['Upgrade-Insecure-Requests'] = '1'

	    self.textHeader['Host'] ='weibo.com'
	    return
	    # return json.loads(login_str)


	def uploadPic(self,file):
		with open(file, "rb") as image_file:
			encoded_image = base64.b64encode(image_file.read())

		params = urllib.urlencode({'app': 'miniblog',
			'cb': 'http://weibo.com/aj/static/upimgback.html?_wv=5&callback=STK_ijax_'+str(int(time.time()*1000)),
			'data':'base64',
			'logo':'',
			'markpos':'1',
			'marks': '0',
			'mime': 'image/jpeg',
			'nick': '0',
			's': 'rdxt',
			'url': '0'})
		uploadPicUrl = "http://picupload.weibo.com/interface/pic_upload.php?%s" % params

		picPostData = {
		'b64_data':encoded_image
		}
		self.session.header = self.picHeader
		rp = self.session.post(uploadPicUrl,data = picPostData,allow_redirects=False)

		return dict(urlparse.parse_qsl(urlparse.urlsplit(rp.headers['Location']).query))['pid']

	def postText(self,text,pids):
		if type(pids)!=list:
			pids = [pids]
		if len(pids)!=0:
			pid_line = reduce(lambda x,y:x+'|'+y,pids)
		else:
			pid_line = ''
		postData={
			'_t':'0',
			'appkey':'',
			'location':'v6_content_home',
			'module':'stissue',
			'pdetail':'',
			'pic_id':pid_line,
			'pub_source':'main_',
			'pub_type':'dialog',
			'rank':'0',
			'rankid':'',
			'style_type':'1',
			'text':text,
			'tid':'',
			'updata_img_num':str(len(pids))}
		
		postUrl = 'http://weibo.com/aj/mblog/add?ajwvr=6&__rnd='+str(int(time.time()*1000))
		self.session.header = self.textHeader
		self.session.post(postUrl,data = postData)

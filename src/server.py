#!/usr/bin/python
# coding=utf-8

"""
server.py

Simple server to return quality assessment for a given image.

Created by Xu Kaifeng on 2017.09.12
Particle Holding Inc. All rights reserved.
"""

import SimpleHTTPServer
import SocketServer
import sys,time,json
import urlparse
from iqa import IQA

def when():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

def info(msg):
	sys.stdout.write('(%s) INFO: %s\n' % (when(), msg))
	sys.stdout.flush()

def err(msg):
	sys.stderr.write('(%s) ERROR: %s\n' % (when(), msg))

if len(sys.argv) < 2:
	info('Usage: python server.py')
	sys.exit()

def detect(image):
	try:
		iqa = IQA(image)
		ret = {'sharpness':iqa.sharpness(),'colorfulness':iqa.colorfulness(),'entropy':iqa.entropy(),'shape':iqa.shape()}
		return ret
	except:
		err('%s not in database' % ip)
		return {'error':'%s not in database' % ip}

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	
	def do_GET(self):
		query = dict(urlparse.parse_qsl(urlparse.urlsplit(self.path).query))
		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.end_headers()
		if 'image' in query:
			self.wfile.write(json.dumps(detect(query['image'])))
		else:
			self.wfile.write(json.dumps({'error':'missing parameter image'}))
		self.finish()
		self.connection.close()

info('Server listening on port 8000')
httpd = SocketServer.ThreadingTCPServer(('0.0.0.0', 8000), Handler, False)
httpd.allow_reuse_address = True
httpd.server_bind()
httpd.server_activate()
httpd.serve_forever()

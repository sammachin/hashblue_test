#!/usr/bin/env python

################################################################################
# Hashblue Test Client to do the oAuth Dance then get your messages
# Sam Machin Telefonica UK February 2012
# Use this for testing only its not production quality :-)
################################################################################

import json
import webbrowser
import BaseHTTPServer
import urlparse
import os
import thread
import time
import urllib
import urllib2

def getAccessToken(code):
	data = {}
	data['client_id'] = identifier
	data['client_secret'] = secret
	data['grant_type'] = "authorization_code"
	data['redirect_uri'] = "http://localhost:8000/return"
	data['code'] = code
	params = urllib.urlencode(data)
	url = "https://hashblue.com/oauth/access_token"
	req = urllib2.Request(url, params)
	resp = urllib2.urlopen(req)
	rdata = json.loads(resp.read())
	accesstoken = rdata["access_token"]
	return accesstoken


def getMessages(token):
	authhead = "OAuth " + token
	req = urllib2.Request('https://api.hashblue.com/messages')
	req.add_header('Authorization', authhead)
	req.add_header('Accept', 'application/json')
	resp = urllib2.urlopen(req)
	data = json.loads(resp.read())
	for msg in data['messages']:
		print msg['contact']['msisdn'] + " : " + msg['content']        


def webserver():
	server = BaseHTTPServer.HTTPServer(("127.0.0.1", 8000), Handler)
	server.pages = {}
	server.serve_forever()

def main():
	global identifier
	global secret
	global hburl
	identifier = raw_input('Enter client_id: ')
	secret = raw_input('Enter client_secret: ')
	hburl = "https://hashblue.com/oauth/authorize?client_id=" + identifier +"&redirect_uri=http://localhost:8000/return"
	print "Starting the oAuth dance, look at your web browser."
	pid = thread.start_new_thread(webserver, ())
	webbrowser.open("http://localhost:8000/start")
	time.sleep(300)



class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

		def do_GET(self):
			parsed_path = urlparse.urlparse(self.path)
			if self.path == "/start":
	   			self.send_response(301)
				self.send_header("Location", hburl)
				self.end_headers()
			elif self.path.split("?")[0] == "/return":
				code = parsed_path.query.split("=")[1]
				accesstoken = getAccessToken(code)
				self.send_response(200)
				self.send_header("content-type", "text/plain;charset=utf-8")
				self.end_headers()
				self.wfile.write("Authorised,(%s) please return to terminal to see your messages" % accesstoken)
				getMessages(accesstoken)
			else:
				self.send_response(404)
				self.end_headers()

if __name__ == '__main__':
	main()
	
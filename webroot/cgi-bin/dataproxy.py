#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()
import os
import urllib2
from config import *

#target = "http://addama-csacr.appspot.com" + os.environ.get("REQUEST_URI").split("proxy.py",1)[1]
target = proxyhost + os.environ.get("REQUEST_URI").split("proxy.py",1)[1]

req = urllib2.Request(target, None, { "API_KEY":"952975ec-93c3-44c0-b32a-e68dbafea5ce"})
response = urllib2.urlopen(req)

print "Content-type: text/html"
print
print response.read()


	

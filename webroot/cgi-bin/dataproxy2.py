#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()
import os
import urllib

target = "http://drake:9081" + os.environ.get("REQUEST_URI").split("proxy.py",1)[1]
response = urllib.urlopen(target)

print "Content-type: text/html"
print
print response.read()


	

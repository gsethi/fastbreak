#!/local/bin/python2.6.5/python
import time

startclock = time.clock()
starttime = time.time()

import os, glob
import cgi
import cgitb
cgitb.enable()
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
try: import cPickle as pickle
except ImportError: import pickle
import sys
import math
import urllib2
#import bisect

from config import *





def log(msg):
	if debugmode:
		logf = open(logfile,"a")
		logf.write("%s:\t%s\n"%(time.strftime("%c"), msg))
		logf.close()

log("Script called with uri: \"%s\""%(os.environ.get("REQUEST_URI")))
form=cgi.FieldStorage()

for field in form:
	log("paramater %s is \"%s\""%(field,form.getvalue(field)))

chrm = str(form.getvalue("chr"))	#the chromosone the start region is located on
start = int(form.getvalue("start")) #the start of the start region
end = int(form.getvalue("end"))	#the end of the start region
searchdepth = int(form.getvalue("depth"))	#the depth of transversals to follow
searchradius = int(form.getvalue("radius"))  #the size of leaves
bdoutfile = str(form.getvalue("file"))  #the breakdancer output
filters = form.getvalue("filters")
key = str(form.getvalue("key"))

if filters == None:
	filters = False
else:
	filters = json.loads(str(filters)) 

##### google datasource code; could be refactored
reqId=0
responseHandler="google.visualization.Query.setResponse"
tqx=str(form.getvalue("tqx")) #the google query
for param in tqx.split(";"):
	pair = param.split(":")
	if pair[0] == "reqId":
		reqId = int(pair[1])
	if pair[0] == "responseHandler":
		responseHandler = int(pair[1])
		

def googleDataTable(cols,rows):
	out = {"cols":[],"rows":[]}
	
	for col in cols:
		out["cols"].append({"id":col,"type":"string"})
	for row in rows:
		rowout = []
		for val in row:
			rowout.append({"v":val})
		out["rows"].append({"c":rowout})
	return out
##### end google datasource code

#TODO: Binary search out which edges are in a range for a given chromosone
def filter(index,chrm,start,end):
 	out = []
	if chrm in index:
		for edge in index[chrm]:
			if edge["Pos1"] < start:
				continue
			if edge["Pos1"] > end:
				break
				
			includeme = False
			if filters != False:
				for filter in filters:
					if	edge["Type"]==filter["type"] and int(edge["Score"])>=int(filter["minscore"]) :
						includeme = True
						break
			else:
				includeme = True
			if includeme==True:
				out.append(edge)
	return out
#  	if chrm in index:
#  		leftbound = bisect.bisect_left(index[chrm],start)
#  		rightbound = bisect.bisect_right(index[chrm],end)
#  		return index[chrm][leftbound:rightbound]
#  	else:
#  		return []
		
	
#grow the tree in a method similar to a depth first search
def growDepthFirst(chrm,start,end,index,curdepth, maxdepth,radius,adjList,visited):
	curdepth+=1
	if curdepth >= maxdepth:
		return
	
	for edge in filter(index,chrm,start,end):
		if edge["line"] in visited:
			continue
		adjList.append([edge["line"],edge["Chr1"],edge["Chr2"],"%i"%(edge["Pos1"]),"%i"%(edge["Pos2"]),"%i"%(edge["num_Reads"]),edge["Type"],edge["Score"]])
		visited[edge["line"]]=True
		growDepthFirst(edge["Chr2"],edge["Pos2"]-radius,edge["Pos2"]+radius,index,curdepth, maxdepth,radius,adjList,visited)



#Variable to hold an adjacancy list of the directed acyclic(?) graph representing the tree
#each row should have  elements:
outcols = ["edge_id", "source_chr", "target_chr", "source_pos", "target_pos", "num_reads","type","score"]

adjList = []

#variable to hold the regions that have allready been searched
visited = {}

index = {}

loadstart = time.time()

if(loadPickleFromUri==True):	
	target = picklehost + bdoutfile
	log("Loading %s from jcr"%(target))
	req = urllib2.Request(target, None, { "API_KEY":key})
	response = urllib2.urlopen(req)	
	index = pickle.loads(response.read())
else:
	log("Loading %s from filesystem"%(bdoutfile))
	indexfile = open(os.path.join(datapath,bdoutfile.lstrip("\/")),"r")
	index = pickle.load(indexfile)
	indexfile.close()

log("Loading took %s real seconds."%(time.time()-loadstart))	
log("Index has chrs: %s"%(", ".join(index.keys())))

#growDepthFirst(chrm,start,end,index,0,searchdepth,searchradius,adjList,visited)
log("Starting depth first search")
contigs = [[{"chr":chrm,"start":start,"end":end}]]
for depth in range(searchdepth):
	newcontigs = []
	for contig in contigs[depth]:
		for edge in filter(index, contig["chr"],contig["start"],contig["end"]):
			if edge["line"] in visited:
				continue
			adjList.append([edge["line"],edge["Chr1"],edge["Chr2"],"%i"%(edge["Pos1"]),"%i"%(edge["Pos2"]),"%i"%(edge["num_Reads"]),edge["Type"],edge["Score"]])
			visited[edge["line"]]=True
			addcontig = True
			chr2 = edge["Chr2"]
			s = edge["Pos2"]-searchradius
			e = edge["Pos2"]+searchradius
			for c in newcontigs:			
				if (chr2 == c["chr"] and ( (s >= c["start"] and s <= c["end"]) or (e >= c["start"] and e <= c["end"]) or (s <= c["start"] and e >= c["end"]))):
					addcontig = False
					if (s < c["start"]):
						c["start"] = s
					if (e > c["end"]):
						c["end"] = e
					break
	
			if addcontig==True:
				newcontigs.append({"chr":chr2,"start":s,"end":e})

			
		
	contigs.append(newcontigs);
	
log("Printing output")
##### google datasource code; could be refactored
print "Content-type: text/html"
print
print "%(responseHandler)s({status:'ok',table:%(table)s,reqId:'%(reqId)i'})"%{'table':json.dumps(googleDataTable(outcols,adjList)),'reqId':reqId,'responseHandler':responseHandler}

log("Done. Request took %s real time %s system time. Exiting Now."%(time.time()-starttime,time.clock()-startclock))


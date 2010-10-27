#!/usr/bin/python
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

datapath = "../data/tranche_09/"
form=cgi.FieldStorage()

chrm = str(form.getvalue("chr"))	#the chromosone the start region is located on
start = int(form.getvalue("start")) #the start of the start region
end = int(form.getvalue("end"))	#the end of the start region
searchdepth = int(form.getvalue("depth"))	#the depth of transversals to follow
searchradius = int(form.getvalue("radius"))  #the size of leaves
bdoutfile = datapath+str(form.getvalue("file"))  #the breakdancer output

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
			if edge["Pos1"] > start and edge["Pos1"] < end:
				out.append(edge)
	return out
		
	
#grow the tree in a method similar to a depth first search
def growDepthFirst(chrm,start,end,index,curdepth, maxdepth,radius,adjList,visited):
	curdepth+=1
	if curdepth >= maxdepth:
		return
	
	for edge in filter(index,chrm,start,end):
		if edge["line"] in visited:
			continue
		adjList.append([edge["line"],edge["Chr1"],edge["Chr2"],"%i"%(edge["Pos1"]),"%i"%(edge["Pos2"]),"%i"%(edge["Size"]),"%i"%(edge["num_Reads"]),edge["Type"],edge["Score"]])
		visited[edge["line"]]=True;
		growDepthFirst(edge["Chr2"],edge["Pos2"]-radius,edge["Pos2"]+radius,index,curdepth, maxdepth,radius,adjList,visited)



#Variable to hold an adjacancy list of the directed acyclic(?) graph representing the tree
#each row should have  elements:
outcols = ["edge_id", "source_chr", "target_chr", "source_pos", "target_pos", "size", "num_reads","type","score"]

adjList = []

#variable to hold the regions that have allready been searched
visited = {}

indexfile = open(bdoutfile+".pickle")
index = pickle.load(indexfile)
indexfile.close()

growDepthFirst(chrm,start,end,index,0,searchdepth,searchradius,adjList,visited)

##### google datasource code; could be refactored
print "Content-type: text/html"
print
print "%(responseHandler)s({status:'ok',table:%(table)s,reqId:'%(reqId)i'})"%{'table':json.dumps(googleDataTable(outcols,adjList)),'reqId':reqId,'responseHandler':responseHandler}
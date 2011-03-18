#!/usr/bin/python
#
# 
#     Copyright (C) 2003-2010 Institute for Systems Biology
#                             Seattle, Washington, USA.
# 
#     This library is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 2.1 of the License, or (at your option) any later version.
# 
#     This library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public
#     License along with this library; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
# 

"""
This is the data service for use with the transplant visaulization
there is a cgi python version floating arount to but
this version you call by passing in the query string
python transplantdata.py querystring
see below for the expected params.

Python >= 2.5 required
"""

__author__ = "Ryan Bressler"




import os
import glob
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
try: import cPickle as pickle
except ImportError: import pickle
import sys
import math




querystring = sys.argv[1].replace("\"","")

print querystring

params = {}
for param in querystring.split("&"):
	pair = param.split("=")
	params[pair[0]]=pair[1]

chrm = str(params["chr"])	#the chromosone the start region is located on
start = int(params["start"]) #the start of the start region
end = int(params["end"])	#the end of the start region
searchdepth = int(params["depth"])	#the depth of transversals to follow
searchradius = int(params["radius"])  #the size of leaves
bdoutfile = str(params["file"])  #the breakdancer output

##### google datasource code; could be refactored
reqId=0
responseHandler="google.visualization.Query.setResponse"
tqx=str(params["tqx"]) #the google query
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

indexfile = open(bdoutfile)
index = pickle.load(indexfile)
indexfile.close()

growDepthFirst(chrm,start,end,index,0,searchdepth,searchradius,adjList,visited)

##### google datasource code; could be refactored
print "%(responseHandler)s({status:'ok',table:%(table)s,reqId:'%(reqId)i'})"%{'table':json.dumps(googleDataTable(outcols,adjList)),'reqId':reqId,'responseHandler':responseHandler}
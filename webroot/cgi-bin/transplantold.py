#!/usr/bin/python
import os, glob
import cgi
import cgitb
cgitb.enable()
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
import sys

datapath = "../data/"
form=cgi.FieldStorage()

chrm = str(form.getvalue("chr"))	#the chromosone the start region is located on
start = int(form.getvalue("start")) #the start of the start region
end = int(form.getvalue("end"))	#the end of the start region
searchdepth = int(form.getvalue("depth"))	#the depth of transversals to follow
searchradius = int(form.getvalue("radius"))  #the size of leaves
bdoutfile = datapath+str(form.getvalue("file"))  #the breakdancer output
reqId=0
responseHandler="google.visualization.Query.setResponse"
tqx=str(form.getvalue("tqx")) #the google query
for param in tqx.split(";"):
	pair = param.split(":")
	if pair[0] == "reqId":
		reqId = int(pair[1])
	if pair[0] == "responseHandler":
		reqId = int(pair[1])
		

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
		




#this describe the breakdancer.out file format and the tranlation to our needed fields
#I do it like this incase it changes
inputcols = ["Chr1","Pos1","Orientation1","Chr2","Pos2","Orientation2","Type","Size","Score","num_Reads","num_Reads_lib","Allele_frequency","Version","Run_Param"]
deliminator = "\t"

typei = inputcols.index("Type")
chr1i = inputcols.index("Chr1")
chr2i = inputcols.index("Chr2")
pos2i = inputcols.index("Pos2")
pos1i = inputcols.index("Pos1")
sizei = inputcols.index("Size")
valuei = inputcols.index("num_Reads")

#Variable to hold an adjacancy list of the directed acyclic(?) graph representing the tree
#each row should have  elements:
outcols = ["edge_id", "source_chr", "target_chr", "source_pos", "target_pos", "size", "num_reads","type"]

adjList = []

#variable to keep track of which branches to grow
oldBranchesEnd = 0

#variable to hold current search regions
#ie the growing leaves of the branches
leaves = []



#the breakdancer ouput is essentially an adj list so we just loop over it searchdepth times
#growing branches
#TODO: create spatial data structure from breakdancer output to speed up deeper searching
for curdepth in range(searchdepth):
	input = open(bdoutfile, 'r')
	if curdepth == 0:
		leaves =[[chrm,int(start),int(end)]]
	else:
		leaves = []
		if oldBranchesEnd == len(adjList):
			#no branches to grow so we stop trying
			break
		for leaf in range(oldBranchesEnd,len(adjList)):
			row = adjList[leaf]
			#TODO: what is the actual size of leaf region 
			leaves.append([row[outcols.index("target_chr")],int(row[outcols.index("target_pos")])-searchradius,int(row[outcols.index("target_pos")])+searchradius])
	
	oldBranchedEnd = len(adjList)
	for line in input:
		if line.find("#")>-1:
			line = line.split("#")[0]
			if line == '':
				continue
		values = line.split()
		if(len(values)>7):
			#is a valid row
			#check to see if its start position is on one of the leaves
			#TODO: check end position as well?
			Sprout = False
			for leaf in leaves:
				if values[chr1i] == leaf[0] and int(values[pos1i]) > leaf[1] and int(values[pos1i]) < leaf[2]:
					Sprout = True
			if Sprout == False:
				#do not need to grow
				continue
			#grow the leaf
			#TODO: handle events besides translocations
			if values [typei] == "ITX" or values [typei] == "CTX":
				#output line format. Mush match the array above.
				adjList.append(["",values[chr1i],values[chr2i],values[pos1i],values[pos2i],values[sizei],values[valuei]])
			
	input.close()
	
#Dump output

#print "%s"%(json.dumps(googleDataTable(outcols,adjList)))

print "Content-type: text/html"
print
print "%(responseHandler)s({status:'ok',table:%(table)s,reqId:'%(reqId)i'})"%{'table':json.dumps(googleDataTable(outcols,adjList)),'reqId':reqId,'responseHandler':responseHandler}
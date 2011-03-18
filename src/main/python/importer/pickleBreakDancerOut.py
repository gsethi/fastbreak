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
"""

__author__ = "Ryan Bressler"

import cPickle as pickle
import os
import glob
import errno
import sys
import shutil

import genelist



def addrow (index, line, Chr1,Pos1, Chr2, Pos2, Type, Score, num_Reads):
	if not Chr1 in index:
		index[Chr1] = []
	index[Chr1].append({"line":line, "Chr1":Chr1, "Pos1": int(Pos1), "Chr2": Chr2, "Pos2": int(Pos2), "Type": Type, "Score": float(Score), "num_Reads":int(num_Reads)})
	

def doPickle(input,inf,genelistfn,picklepath):
	#this describe the breakdancer.out file format and the tranlation to our needed fields
	#I do it like this incase it changes
	
	deliminator = "\t"
	
	type = []
	
	#firstline = 
	#define vars indicating what pos in the tsv diffrent values take
	#check to see if it is our inhouse format
	if inf.find(".listcalled")>-1:
		typei = 7
		chr1i = 0
		chr2i = 2
		pos2i = 3
		pos1i = 1
		scorei = 6
		valuei = 5
		types = ["small","other"]
	
	#if not assume breakdancer
	else:
		input.next() #skip the header for
		inputcols = ["Chr1","Pos1","Orientation1","Chr2","Pos2","Orientation2","Type","Size","Score","num_Reads","num_Reads_lib","Allele_frequency","Version","Run_Param"]
		
		typei = inputcols.index("Type")
		chr1i = inputcols.index("Chr1")
		chr2i = inputcols.index("Chr2")
		pos2i = inputcols.index("Pos2")
		pos1i = inputcols.index("Pos1")
		scorei = inputcols.index("Score")
		sizei = inputcols.index("Size")
		valuei = inputcols.index("num_Reads")
		types = ["ITX","CTX"]
	
	genes=genelist.loadGenes(genelistfn,types)

	
	
	
	index = {}
	
	
	for i, line in enumerate(input):
		if line.find("#")>-1:
			line = line.split("#")[0]
			if line == '':
				continue
		values = line.split()
		#make sure its a valid interaction
		if(len(values)>7):
			if values [typei] in types:
				#add both lines
				chr1 = values[chr1i]
				chr2 = values[chr2i]
				if not chr1.startswith("chr"):
					chr1 = "chr"+chr1
				if not chr2.startswith("chr"):
					chr2 = "chr"+chr2
				#add it both from->to and to->from
				addrow(index,i,chr1,values[pos1i],chr2,values[pos2i],values[typei],values[scorei],values[valuei])
				addrow(index,i,chr2,values[pos2i],chr1,values[pos1i],values[typei],values[scorei],values[valuei])
				
				for pos in [{"c":chr1,"p":int(values[pos1i])}, {"c":chr2,"p":int(values[pos2i])}]:
					p = pos["p"]
					c = pos["c"]
					if c in genes:
						for j, gene in enumerate(genes[c]):
							if p > gene["start"] and p < gene["end"]:
								genes[c][j][values [typei]] +=1
					
				
	
	#sort by pos
	for key in index:
		index[key].sort(key = lambda row: row["Pos1"])
	
	outf=os.path.basename(inf+".pickle")
	print("Attempting to make dir "+os.path.dirname(picklepath))
	try:
		os.makedirs(picklepath)
	except OSError, exc: # Python 2.5 was "except OSError as exc"
		if exc.errno == errno.EEXIST:
			pass
		else: raise
	
	#produce the pickle file
	print "Pickling index to %s \n"%(outf)
	output = open(outf,"w")
	pickle.dump(index,output)
	output.close()
	if os.path.dirname(os.path.abspath(outf)) != os.path.abspath(picklepath):
		shutil.copy(outf,picklepath)
	
	#write the scores out
	genelistoutf=inf+".t.per.gene"
	genelistout = open(genelistoutf,"w")
	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(types)+"\n")
	for chr in genes:
		for gene in genes[chr]:
			vals = "\t".join([ str(gene[type]) for type in types ])
			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
	genelistout.close()

#for us as script	
if __name__ == "__main__":
	print "Finding %s \n"%(sys.argv[1])
	files = glob.glob(sys.argv[1])
	print "%i files: %s  \n"%(len(files),", ".join(files) )
	for inf in files:
		print "processing %s \n"%(inf)	
		input = open(inf, 'r')
		doPickle(input,inf,"genelist.txt","./")
		input.close()

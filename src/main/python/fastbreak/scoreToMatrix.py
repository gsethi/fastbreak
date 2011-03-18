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

import os
import glob
import errno

def score():
	files = glob.glob("./*.t.per.gene")
	print "%i files\n"%(len(files))
	cols = ["gene_symbol"]
	fileobjs = []
	for inf in files:
		cols.append(os.path.basename(inf).split(".")[0])
		fileobjs.append(open(inf,"r"))
	
	
	
	itxf = open("itxmatrix.tsv","w")
	ctxf = open("ctxmatrix.tsv","w")
	
	
	itxf.write("\t".join(cols)+"\n")
	ctxf.write("\t".join(cols)+"\n")
	
	loop = True
	while loop==True:
		
		firstpass=True
		itxvs = []
		ctxvs = []
		for file in fileobjs:
			try:
				line = file.next()
			except StopIteration:
				loop=False
			if loop == True:
				linevs = line.rstrip().split("\t")
				if linevs[0] == "gene_symbol":
					continue
				if firstpass==True:
					itxvs.append(linevs[0])
					ctxvs.append(linevs[0])
					firstpass = False
				itxvs.append(linevs[4])
				ctxvs.append(linevs[5])

				
		if loop==True and len(linevs) > 1:
			itxf.write("\t".join(itxvs)+"\n")
			ctxf.write("\t".join(ctxvs)+"\n")
			
	for file in fileobjs:
		file.close()
	
	itxf.close()
	ctxf.close()


if __name__ == "__main__":
	score()
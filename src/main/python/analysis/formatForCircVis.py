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

import sys
import glob

from fastbreak import genelist

def formatMatrix(matrixfilen, gl):
    fo = open(matrixfilen,"r")
    fout = open(matrixfilen+".for.circvis.txt","w")
    fout.write("chr1\tstart1\tend1\toptions1\tchr2\tstart2\tend2\toptions2\tlinkValue\n")
    columns = fo.next().lstrip().rstrip().replace('"','').split()
    for j,line in enumerate(fo):
    	vals = line.rstrip().replace('"','').split()
    	gene = vals[0]
    	for i,val in enumerate(vals[1:]):
    		if columns[i]!=gene and val != "NA" and i>j:
				go1 = gl[gene]
				go2 = gl[columns[i]]
				fout.write("\t".join(["%s"%(i) for i in [go1["chr"],go1["start"],go1["end"],"label="+go1["name"],go2["chr"],go2["start"],go2["end"],"label="+go2["name"],val]])+"\n")
    fout.close()
    fo.close()
    			

def formatList(listfilen,gl):
	fo = open(listfilen,"r")
	fout = open(listfilen+".for.circvis.txt","w")
	fout.write("chr\tstart\tend\tvalue\toptions\n")
	columns = fo.next()
	for line in fo:
		vals = line.rstrip().replace('"','').split()
		gene = vals[0]
		if gene in gl:
			go1=gl[gene]
			fout.write("\t".join(["%s"%(i) for i in [go1["chr"],go1["start"],go1["end"],vals[1],"label="+go1["name"]]])+"\n")
	fout.close()
	fo.close()



if __name__ == "__main__":

	gl = genelist.loadGenesByName(sys.argv[1])
	#formatMatrix("Fastbreak_tumor_cutoff_3_by_gene_MIdist.txt",gl)
	#formatList("Fastbreak_tumor_cutoff_3_by_gene_Counts.txt",gl)
	
	for filename in glob.glob("*_by_gene_Counts.txt"):
		formatList(filename,gl)
	
	for filename in glob.glob("*.distmatrix.txt"):
		formatMatrix(filename,gl)

    
    

  
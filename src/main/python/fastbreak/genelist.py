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

def loadGenes(filen,types):
	genes={}
	genelist = open (filen,"r")
	for gene in genelist:
		vs = gene.rstrip().split("\t")
		if not vs[2] in genes:
			genes[vs[2]]=[]
		vdict = {"name":vs[0],"start":int(vs[4]),"end":int(vs[5]),"or":vs[3]}
		for type in types:
			vdict[type]=0
		genes[vs[2]].append(vdict)
	genelist.close()
	return genes

def loadGenesByName(filen):
	genes={}
	genelist = open (filen,"r")
	for gene in genelist:
		vs = gene.strip().split("\t")
		if not vs[0] in genes:
		    vdict = {"name":vs[0],"chr":vs[2], "start":int(vs[4]),"end":int(vs[5]),"or":vs[3]}
		    genes[vs[0]]=vdict
	genelist.close()
	return genes
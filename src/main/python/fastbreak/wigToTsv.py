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

def parseEqList(ins):
	retDic = {}
	for term in ins.rstrip().split():
		term = term.split("=")
		if len(term)==2:
			retDic[term[0]]=term[1]
	return retDic

def wigToTsv(wig,sample,outf):
	vStep = True
	chr = ""
	start = 1
	span = 1
	step = 0
	#outf = open(outfn,"w")
	for line in wig:
		
		if line.startswith("track"):
			continue
		if line.startswith("variableStep"):
			vStep = True
			params = parseEqList(line)
			chr = params["chrom"]			
			span = params["span"] or 1
			continue
		if line.startswith("fixedStep"):
			vStep = False
			params = parseEqList(line)
			chr = params["chrom"]			
			span = params["span"] or 1
			start = int(params["start"])
			step = params["step"]
			continue
		value = 0
		if vStep == True:
			values = line.rstrip().split()
			start = values[0]
			value = values[1]
		else:
			value = line.rstrip()
		
		outf.write("\t".join([sample,chr,start,span,value+"\n"]))
			
		if vStep == False:
			start = int(start)+int(step)
	#outf.close()
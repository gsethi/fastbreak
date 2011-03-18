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

import glob 
import os 
import sys

from fastbreak import makeCalls

import scoreCalls
import smallSMatrixByGene 


def main():
	wigfiles = glob.glob("./*.tile.wig")
	coveredregions  = {}
	firstpass = True
	coveragecutoff = 1
	
	
	print "Finding Covered Regions"
	for wigfn in wigfiles:		
		print "Loading " + wigfn
		wig =  makeCalls.loadWigHash(wigfn)
		fitleredcount = 0
		passedCount = 0
		for chr in wig:
			if not chr in coveredregions:
				coveredregions[chr] = {}
			for tile in wig[chr]:
				if int(wig[chr][tile]) >= int(coveragecutoff):
					passedCount +=1
					if firstpass == True:
						coveredregions[chr][tile] = True
									
				else:
					coveredregions[chr][tile] = False
					fitleredcount += 1
		print "Found %i tiles covered over cutoff and %i tiles covered but below cutoff"%(passedCount,fitleredcount)
					
		firstpass = False
			
	for minscore in [0,30,50,70,90,99]:
		for infile in glob.glob(os.path.join(os.getcwd(),'TCGA*.breakdancer.out')):
			print "Processing " + infile
			scoreCalls.scoreBreakDancer(infile,infile,sys.argv[1],coveredregions,minscore)
			
		print "Combining per gene breakdancer files"
		smallSMatrixByGene.scoreFiles("./*.breakdancer.out.t.per.gene",4,"minscore.%i.breakdancer.per.gene.score"%(minscore))
		
if __name__ == "__main__":
	main()
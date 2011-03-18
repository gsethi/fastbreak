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
import sys

from fastbreak import makeCalls
from fastbreak import genelist

import scoreCalls

resolution = 1000
padby = 1000
includeAllGenes = True
restricttoCoveredBins = True
coveragecutoff = 1

def score(genelistfn):
	wigfiles = glob.glob("./*.tile.wig")
	coveredregions  = {}
	firstpass = True
	
	print "Loading " + genelistfn
	genes=genelist.loadGenes(genelistfn,wigfiles)
	
	coveredregions  = {}
	firstpass = True
	
	if restricttoCoveredBins == True:
		print "Finding Covered Regions"
		for wigfn in wigfiles:		
			print "Loading " + wigfn
			wig =  makeCalls.loadWigHash(wigfn)
			fitleredcount = 0
			passedCount = 0
			for chr in wig:
				chrNorm = scoreCalls.addChr(chr)
				if not chrNorm in coveredregions:
					coveredregions[chrNorm] = {}
				for tile in wig[chr]:
					if int(wig[chr][tile]) >= int(coveragecutoff):
						passedCount +=1
						if firstpass == True:
							coveredregions[chrNorm][tile] = True
										
					else:
						coveredregions[chrNorm][tile] = False
						fitleredcount += 1
			print "Found %i tiles covered over cutoff and %i tiles covered but below cutoff"%(passedCount,fitleredcount)
						
			firstpass = False
	
	
	for wigfn in wigfiles:		
		print "Loading " + wigfn
		wig =  makeCalls.loadWigHash(wigfn)
		
		print "Bining by gene"
		for chr in genes:
			for j, gene in enumerate(genes[chr]):
				for tile in xrange(makeCalls.getTile(int(gene["start"])-int(padby)),makeCalls.getTile(int(gene["end"])+int(padby))):
					if restricttoCoveredBins == False or ( chr in coveredregions and tile in coveredregions[chr] and coveredregions[chr][tile] == True):
						wigchr=chr
						
						if not wigchr in wig:
							wigchr = wigchr.replace("chr","")
						if wigchr in wig and tile in wig[wigchr]:
							if includeAllGenes == False:
								if int(wig[wigchr][tile])>10:
									genes[chr][j][wigfn] = 1
							else:
								if int(wig[wigchr][tile])>0:
									if not wigfn in genes[chr][j]:
										genes[chr][j][wigfn] = 0
									genes[chr][j][wigfn]+=int(wig[wigchr][tile])
		
								
	
	
	genelistoutf="coverage.per.gene.per.sample.tsv"
	print "Writing " + genelistoutf
	genelistout = open(genelistoutf,"w")
	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(wigfiles)+"\n")
	for chr in genes:
		for gene in genes[chr]:
			vals = "\t".join([ str(gene[type]) for type in wigfiles ])
			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
	genelistout.close()
	


if __name__ == "__main__":
	score(sys.argv[1])
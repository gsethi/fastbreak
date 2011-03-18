import glob 
import os 
import sys

from fastbreak import scoreCalls
from fastbreak import smallSMatrixByGene 
from fastbreak import makeCalls

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
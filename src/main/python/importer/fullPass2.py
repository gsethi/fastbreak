#example usage (in the directory with jakes output)
#python fullPass2.py TCGA-25-1328 TCGA-25-1319 TCGA-25-1314

import sys,os
import plotL
import makeCalls
import glob
do1stplots = False
makecalls = True
do2ndplots = False


def fullPass2(patient,dir):
	global do1stplots,makecalls,do2ndplots
	if do1stplots:
		plotL.plotL(patient,dir)
	if makecalls:
		filenbase = os.path.join(dir,patient)+"*oddreads.list"
		print "Looking for odd read files matching " + filenbase
		for filename in glob.glob(filenbase):
			print "Making calls for file " + filename
			makeCalls.makeCalls(open(filename,"r"),open(filename+"called","w"),filename+"distances")
	if do2ndplots:
		plotL.plotLcalled(patient,dir)
	
	
if __name__ == "__main__":
	for patient in sys.argv[1:]:
		fullPass2(patient,"./")
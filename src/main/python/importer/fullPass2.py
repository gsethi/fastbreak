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
	patients=[]
	if len(sys.argv)==1:
		wigfiles = glob.glob("./*.tile.wig")
		patientdic = {}
		for filen in wigfiles:
			patientdic[os.path.basename(filen)[0:12]] = 1
			patients = patientdic.keys()
	else:
		patients = sys.argv[1:]
	
	for patient in patients:
		fullPass2(patient,"./")
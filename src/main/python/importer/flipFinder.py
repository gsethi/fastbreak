import makeCalls, tsvparser
import os, glob

calledHeaders = ["fromC","fromP","toC","toP","ori","count","score","type"]

def outputFlip():

def findFlips(10wigfn,coverageWigfn,calledFn,step=1000):
	# load index of inverted sections
	invertedSections = makeCalls.loadWigHash(10wigfn)
	
	# and coverage data for use in cutoffs
	coveredSections = makeCalls.loadWigHash(coverageWigfn)
	
	calledFO = open(calledFn,"r")
	
	otherDict={"11":{},"00":{}}
	
	
	#index "edges" by type and position
	for line in calledFO:
		vs = tsvparser.parseLine(line,calledHeaders)
		if vs["type"]=="other":
			
			if vs["ori"] = "00":
				if not vs["toC"] in otherDict["00"]:
					otherDict["00"][vs["toC"]]={}
				if not vs["toP"] in otherDict["00"][vs["toC"]]
					otherDict["00"][vs["toC"]][vs["toP"]] = []
				otherDict["00"][vs["toC"]][vs["toP"]].append(vs)
				
			elif vs["ori"] == "11":
				if not vs["fromC"] in otherDict["11"]:
					otherDict["11"][vs["fromC"]]={}
				if not vs["fromP"] in otherDict["11"][vs["fromC"]]
					otherDict["11"][vs["fromC"]][vs["fromP"]] = []
				otherDict["11"][vs["fromC"]][vs["fromP"]].append(vs)
	
	calledFO.close()
	
	
	for flipChr in invertedSections:
		
		flipStart = -1 
		lastPos = -1
		
		for flipPos in invertedSections[flipChr]:
			if flipStart == -1:
				flipStart = int(flipPos)
				lastPos = int(flipPos) - 1
			if int(flipPos) - lastPost > 1:
				outputFlip()
				flipStart = int(flipPos)
				lastPos = int(flipPos)
			else:
				lastPos = int(flipPos)
				
				
				
			
				
		
	
		
	
	
	
	






if __name__ == "__main__":
	samples = {}
	for infile in glob.glob(os.path.join(os.getcwd(),'TCGA*')):
		samples[os.path.basename(infile)[0:15]] = 1
	
	for sample in samples.keys():
		callFN = glob.glob("./"+sample + ".listcalled")
		10wigfn = glob.glob("./"+sample + ".tile10.wig")
		coverageFn = glob.glob("./"+sample + ".tile.wig")
		findFlips(10wigfn,coverageFn,callFN)
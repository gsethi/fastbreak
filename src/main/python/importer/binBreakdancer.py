import sys
import math
import time
import tsvparser
import glob

tileWidth=1000
minNReads = 0
minSameBinReads=0
minRatio=0.0
maxBinDistance = sys.maxint
minMapQ = 0
minScore = 0
headers = []
debug = False
writeDistance = False
types = ["10","01","00","11"]
distanceCutoffs = [0,2,4,8]
coverageCutoffs = [0,.1,.2,.3]
distanceFiles = {}
coverageFiles = {}

coverage = {}


def loadWigHash(filename):
	curchrm = "chr1"
	returnval = {}
	fo = open(filename,"r")
	for line in fo:
		if line.startswith("variableStep"):
	
			for term in line.rstrip().split():
				terms = term.split("=")
				if len(terms)==2 and terms[0]=="chrom":
					curchrm=terms[1]

					if not curchrm in returnval:
						returnval[curchrm]={}
		else:
			vals = line.rstrip().split()
			if len(vals)==2:
				returnval[curchrm][getTile(int(vals[0]))] = int(vals[1])
	fo.close()
	return returnval
			

def log(msg):
	global debug
	if debug==True:
		print msg
		# logf = open("log.txt","w")
# 		logf.write("%s:\t%s\n"%(time.strftime("%c"), msg))
# 		logf.close()

def smart_bool(s):
	if s is True or s is False:
		return s
	s = str(s).strip().lower()
	return not s in ['false','f','n','0','']
		
def bTo01s(s):
	return str(int(smart_bool(s)))
		

	
def outputTile(cout,acum,curChrm,tileStart):
	global tileWidth, minNReads, minScore, minRatio
	global writeDistance, distanceCutoffs,coverageCutoffs, distanceFiles,coverageFiles,coverage
	curBin = getTile(tileStart)
	for chr in acum:
		log("chr is %s"%chr)
		for type in acum[chr]:
			log("type is %s"%type)
			for bin in acum[chr][type]:
				log("bin is %s"%bin)
				count = int(acum[chr][type][bin]["count"])
				score = (1.0-acum[chr][type][bin]["score"])*100
				log("count %s score %s"%(count,score))
				currentCov = 0
				

				cout.write("\t".join(["%s"%el for el in[curChrm,tileStart,chr,int(bin)*tileWidth,type,count,score]])+"\tother\n")

def getTile(pos):
	return int(math.floor(float(pos)/float(tileWidth)))
	
def makeCalls(fo,cout,fn):
	global headers
	global tileWidth
	global writeDistance, distanceCutoffs, coverageCutoffs, distanceFiles,coverageFiles, types, coverage

	firstline = True
	#curChrm = ""
	#tileStart = 0
	acum = {}
	
	for line in fo:
		
		headers = tsvparser.splitLine("#Chr1	Pos1	Orientation1	Chr2	Pos2	Orientation2	Type	Size	Score	num_Reads	num_Reads_lib	Allele_frequency	Version	Run_Param".replace("#Chr1","FromChr").replace("Chr2","ToChr").replace("Pos1","FromPos").replace("Pos2","ToPos").replace("Score","MapQ"))

		if firstline:
			if line.startswith("#") and not line.startswith("#Chr1"):
				continue
			line = line.replace("#Chr1","FromChr").replace("Chr2","ToChr").replace("Pos1","FromPos").replace("Pos2","ToPos").replace("Score","MapQ")
			
			headers = tsvparser.splitLine(line)
			firstline=False
			continue
		
		vs = tsvparser.parseLine(line,headers)
		chr = vs["FromChr"]
		tchr = vs["ToChr"]
		if tchr == "=":
			tchr = chr
		fpos = float(vs["FromPos"])
		tpos = float(vs["ToPos"])
		mapQ = float(vs["MapQ"])
		if mapQ < minMapQ or fpos == tpos:
			continue
		#if curChrm != chr or fpos - tileStart > tileWidth:
		#	log("Doing bin %s %i"%(chr,tileStart))
		#	outputTile(cout,acum,curChrm,tileStart)
		#	acum = {}
		#	curChrm = chr
		#	tileStart = getTile(fpos)*tileWidth
		
		if not chr in acum:
			acum[chr] ={}
		fbin = getTile(fpos)
		if not fbin in acum[chr]:
			acum[chr][fbin] ={}
		if not tchr in acum[chr][fbin]:
			acum[chr][fbin][tchr]={}
		type = vs["Type"]
		if "StrandQ" in vs and "StrandM" in vs:
			if int(fpos) > int(tpos) and tchr == chr:
				type = bTo01s()+bTo01s(vs["StrandM"])
			else:
				type = bTo01s(vs["StrandM"])+bTo01s(vs["StrandQ"])
		
		if not type in acum[chr][fbin][tchr]:
			acum[chr][fbin][tchr][type]={}
		
		tobin = getTile(tpos)
		
		if not tobin in acum[chr][fbin][tchr][type]:
			acum[chr][fbin][tchr][type][tobin]={"count":1,"score":1.0-float(vs["MapQ"])/100.0}
		else:
			log("bin exsists")
			acum[chr][fbin][tchr][type][tobin]["count"]=int(acum[chr][fbin][tchr][type][tobin]["count"])+1
			acum[chr][fbin][tchr][type][tobin]["score"]=float(acum[chr][fbin][tchr][type][tobin]["score"])*(1.0-mapQ/100.0)
	
	
	for curChrm in acum:
		for bin in acum[curChrm]:
			outputTile(cout,acum[curChrm][bin],curChrm,bin*tileWidth)
		
	if writeDistance:
		for t in types:
			for d in distanceCutoffs:
				distanceFiles[t][d].close()
			for d in coverageCutoffs:
				coverageFiles[t][d].close()
			
if __name__ == "__main__":

	filename = sys.argv[1]
	if filename.endswith(".bam.breakdancer.out"):
		writeDistance = False
		minNReads = 0
		minSameBinReads=0
		minRatio=0
		maxBinDistance = sys.maxint
		distancefn = "./"+filename[0:28]+"*.tile.wig"

		distancefn = glob.glob(distancefn)[0]
		#distancefn = distancefn.replace(".tile.wig","oddreads.list")
		
		makeCalls(open(filename,"r"),open(filename+".binned","w"),distancefn)
	else:
		makeCalls(open(filename,"r"),open(filename+"called","w"),filename+"distances")
	#makeCalls(sys.stdin,sys.stdout)
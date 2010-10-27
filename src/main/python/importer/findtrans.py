#findtrans.py
#usage nice samtools view somefile.bam | nice python findtrans.py cancertype[ov,gbm,mix] patientLabel prognosis tileWindow transRange1 transRange2 reportOrientationAndDistance[0,1] generateFastQ[0,1] reportMappingMetrics[0,1] DoReadGroup[0,1]
#ie nice ../bin/samtools-0.1.7_x86_64-linux/samtools view  /titan/cancerregulome1/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1/tranche_07/TCGA-25-1328-10A-01W-0492-08.sorted.bam | nice /tools/bin/python findtrans.py ov TCGA-25-1328-10A-01W-0492-08-medium-0630 medium 1000 50 1000 1 0 1 1 > TCGA-25-1328-10A-01W-0492-08-medium-0630.log

##commenting courtesy of Sheila Reynold
## the SAM format is tab-delimited with 12 columns expected:
##       1      query (pair) name
##       2      bit flags
##       3      reference sequence name
##       4      1-based leftmost position/coordinate of sequence
##       5      mapping quality (phred-scaled)
##       6      extended "cigar" string
##       7      mate reference sequence name ('=' if same as column 3)
##       8      1-based mate position
##       9      inferred insert size
##      10      mapped query sequence
##      11      query quality (ASCII-33 gives Phred base quality)
##      12      variable optional fields ... (may actually be tab-delimited
##              and divided into multiple columns)
##
## there are 11 bits that can be set in the "bit flags" integer:
##      0x0001 : the read is paired in sequencing
##      0x0002 : the read is mapped in a proper pair
##      0x0004 : the query sequence itself is unmapped
##      0x0008 : the mate is unmapped
##      0x0010 : strand of the query (1 for reverse)
##      0x0020 : strand of the mate (1 for reverse)
##      0x0040 : the read is the first read in a pair
##      0x0080 : the read is the second read in a pair
##      0x0100 : the alignment is not primary
##      0x0200 : the read fails platform / vendor quality checks
##      0x0400 : the read is a duplicate
##
## a correct pair of reads should look like this :
##
##                |--------->
## ---------------|-------------------------------|--------------------------
##                                                |<--------
##
## where the vertical bars show the positions that are stored in the SAM
## file (the 1-based leftmost positions) -- the "insert size", however
## goes from the left-edge of the top-strand read to the right-edge of
## the bottom-strand read
##
## the insert size for "good" pairs has a mode at approx 142bp, with a much
## longer tail to the right than to the left ...
##      at ~10% of mode height : 91 - 303
##      at  ~1% of mode height : 78 - 435
## --> we'll probably need to check this for all input files to be sure
##     that they are consistent ...
##
## -------------------------------------------------------------------------- ##

import sys
import string
import time
from time import gmtime, strftime, localtime
import math
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json

#take in class parameters
cancerType = sys.argv[1]
patientLabel = sys.argv[2]
prognosis = sys.argv[3]
tileWindow = 1000
if len(sys.argv) == 5:
	tileWindow = sys.argv[4]
transRange1 = int(sys.argv[5])
transRange2 = int(sys.argv[6])
reportOrientationAndDistance = int(sys.argv[7])
generateFastQ = int(sys.argv[8])	
reportMappingMetrics = int(sys.argv[9])
doReadGroups = int(sys.argv[10])
if doReadGroups == 0:
	print "ignore readgroups as one file\n"
	doReadGroups = False
else:
	print "do each readgroup as separate files\n"
	doReadGroups = True
saveSkippedInfo = False
if len(sys.argv) == 12:
        if int(sys.argv[11]) == 1:
		saveSkippedInfo = True
initialized = False
outhash = {}
rghash = {}
rpthash = {}

timenow = time.strftime("%c")
print 'FindTrans Execution begins: %s for patient %s prognosis %s tileWindow %s transRange1 %i transRange2 %i reportOD %s genFastq %s reportMapping %s' % (timenow, patientLabel, prognosis, tileWindow, transRange1, transRange2, str(reportOrientationAndDistance), str(generateFastQ), str(reportMappingMetrics))
i = 1
beginRangePos = 0

currentRangeChrom = "chrM"
currentTileChrom = "chrM"
currentTile10Chrom = "chrM"

rangeWidth = int(tileWindow)
samcolumns = ["qname","flag","rname","pos","mapq","ciagr","mrnm","mpos","isize","seq","qual","opt"]
samcolumnslen = len(samcolumns)

tileStart = 0
tileWidth = int(tileWindow)


def initialize():
	global outhash, rghash, rpthash, patientLabel, doReadGroups
	if not doReadGroups:
		rghash["rg_all"] = "rg_all"
	relativePath = "/titan/cancerregulome2/synthetic_cancer/trans_out_patient/" + cancerType + "/"	

	for rid in rghash:
		plr = patientLabel + rid		
		#outhash["bucket" + rid] = open(relativePath + prognosis + "/" + plr + "_AllBinsSameChrom_500K", 'w')
		if generateFastQ == 1:
			outhash["fastq" + rid] = open(relativePath + prognosis + "/" + plr + ".fastq", 'w')		
		outhash["tilecov" + rid] = open(relativePath + prognosis + "/" + plr + ".tile.cov", 'w')		
		outhash["tile10" + rid] = open(relativePath + prognosis + "/" + plr + ".tile10.wig", 'w')		
		outhash["tile10" + rid].write('variableStep\tchrom=chrM\tspan=%s\n' % tileWindow)		
		outhash["tile" + rid] = open(relativePath + prognosis + "/" + plr + ".tile.wig", 'w')		
		outhash["tile" + rid].write('variableStep\tchrom=chrM\tspan=%s\n' % tileWindow)
		outhash["oddreadbed" + rid] = open(relativePath + prognosis + "/" + plr+"oddreads.bed", 'w')		
		outhash["oddreadbed" + rid].write('\t'.join(["Chromosome","Start","End","Feature","Translocations\n"]))
		outhash["oddreadlist" + rid] = open(relativePath + prognosis + "/" + plr+"oddreads.list", 'w')
		outhash["oddreadlist" + rid].write('\t'.join(["FromChr","FromPos","ToChr","ToPos","MapQ","Distance","StrandQ","StrandM\n"]))
		outhash["wigsame" + rid] = open(relativePath + prognosis + "/" + plr + ".same.wig", 'w')		
		outhash["wigsame" + rid].write('variableStep\tchrom=chrM\tspan=%s\n' % tileWindow)
		outhash["wigdiff" + rid] = open(relativePath + prognosis + "/" + plr + ".diff.wig", 'w')
		outhash["wigdiff" + rid].write('variableStep\tchrom=chrM\tspan=%s\n' % tileWindow)
		outhash["alldistance" + rid] = open(relativePath + prognosis + "/" + plr + "_distanceAll", 'w')
		outhash["alldistanceMapQ" + rid] = open(relativePath + prognosis + "/" + plr + "_distanceAllMapQ", 'w')
		outhash["distance11" + rid] = open(relativePath + prognosis + "/" + plr + "_distance11", 'w')
		outhash["distance11MapQ" + rid] = open(relativePath + prognosis + "/" + plr + "_distance11MapQ", 'w')
		outhash["distance10" + rid] = open(relativePath + prognosis + "/" + plr + "_distance10", 'w')
		outhash["distance10MapQ" + rid] = open(relativePath + prognosis + "/" + plr + "_distance10MapQ", 'w')
		outhash["distance01" + rid] = open(relativePath + prognosis + "/" + plr + "_distance01", 'w')
		outhash["distance01MapQ" + rid] = open(relativePath + prognosis + "/" + plr + "_distance01MapQ", 'w')
		outhash["distance00" + rid] = open(relativePath + prognosis + "/" + plr + "_distance00", 'w')
		outhash["distance00MapQ" + rid] = open(relativePath + prognosis + "/" + plr + "_distance00MapQ", 'w')
		outhash["outlier" + rid] = open(relativePath + prognosis + "/" + plr + "_outlierReadings", 'w')
		outhash["outlier" + rid].write('read pos chromosome qname seq score distance\n')
        	if saveSkippedInfo:
			outhash["skipped" + rid] = open(relativePath + prognosis + "/" + plr + "_skipped", 'w')
                	outhash["skipped" + rid].write('rname\tmPos\tmapQScore\tdupeFlag\tfailedQC\trandomIndex\n')
		outhash["summary" + rid] = open(relativePath + "/" + prognosis + "/" + plr + "_summary", 'w')
        
		rpthash["nreads" + rid] = 0
		rpthash["rangeReads"+rid] = 0				
		rpthash["tilereads" + rid] = 0
		rpthash["tilereads10" + rid] = 0
		rpthash["ntrans" + rid] = 0
		rpthash["pairs" + rid] = 0
		rpthash["pairsGT0" + rid] = 0
		rpthash["cumulativeAvg" + rid] = 0
		rpthash["cumulativeRangedAvg" + rid] = 0
		rpthash["nsamechromtrans" + rid] = 0
		rpthash["ndiffchromtrans" + rid] = 0	
		rpthash["pairsRangedGT0"+rid] = 0
		rpthash["numNotSamechrom"+rid] = 0
		rpthash["numSamechrom"+rid] = 0
		rpthash["num11"+rid] = 0
		rpthash["num10"+rid] = 0
		rpthash["num01"+rid] = 0
		rpthash["num00"+rid] = 0
		rpthash["zeroDistance"+rid] = 0
		rpthash["numSkipped"+rid] = 0
		rpthash["numPairedUnmapped"+rid] = 0
		rpthash["numUnmappedFirst"+rid] = 0
		rpthash["numQueryUnmapped"+rid] = 0
		rpthash["numMateUnmapped"+rid] = 0
		rpthash["nontrandistance"+rid] = 0
		rpthash["nontranpairs"+rid] = 0
		rpthash["numTransNotStrand"+rid] = 0
		rpthash["rangeSameChrTransCount"+rid] = 0
		rpthash["rangeDiffChrTransCount"+rid] = 0

def reportSummary():
	#Summary Reporting
	global rghash, outhash, rpthash
	for rgid in rghash:
		print("summarizing readgroup:" + rgid + "\n")
		cumRptFile = outhash["summary" + rgid]
		cumRptFile.write("Patient %s rg %s\n"%(patientLabel, rgid))
		cumRptFile.write("Total BAM Reads %i\n"%(rpthash["nreads"+rgid]))
		if reportOrientationAndDistance == 1:
			cumRptFile.write("numTranslocations %i\n"%(rpthash["ntrans"+rgid]))
			cumRptFile.write("abs(pairs>0) %i\n"%(rpthash["pairsGT0"+rgid]))
			if rpthash["ntrans"+rgid] > 0: 
				cumRptFile.write("numTranslocations Same Chr %i pct %f\n"%(rpthash["nsamechromtrans"+rgid], (rpthash["nsamechromtrans"+rgid]/rpthash["ntrans"+rgid])))
				cumRptFile.write("numTranslocations Diff Chr %i pct %f\n"%(rpthash["ndiffchromtrans"+rgid], (rpthash["ndiffchromtrans"+rgid]/rpthash["ntrans"+rgid])))
				cumRptFile.write("numTranslocations Independent of Strand 01_10 %i pct %f\n"%(rpthash["numTransNotStrand"+rgid], (rpthash["numTransNotStrand"+rgid]/rpthash["ntrans"+rgid])))
	
		cumRptFile.write("pairsRangedGT0 %i\n"%(rpthash["pairsRangedGT0"+rgid]))
		cumRptFile.write("notSameChromCount %i\n"%(rpthash["numNotSamechrom"+rgid]))
		cumRptFile.write("num11 %i\n"%(rpthash["num11"+rgid]))
		cumRptFile.write("num10 %i\n"%(rpthash["num10"+rgid]))
		cumRptFile.write("num01 %i\n"%(rpthash["num01"+rgid]))
		cumRptFile.write("num00 %i\n"%(rpthash["num00"+rgid]))
		cumRptFile.write("zeroDistance %i\n"%(rpthash["zeroDistance"+rgid]))
		cumRptFile.write("numSkipped %i\n"%(rpthash["numSkipped"+rgid]))
		cumRptFile.write("cumulativeAvg %f\n"%(rpthash["cumulativeAvg"+rgid]))
		cumRptFile.write("cumulativeRangedAvg %f\n"%(rpthash["cumulativeRangedAvg"+rgid]))
		
		if reportMappingMetrics == 1:
			cumRptFile.write("numPairedUnmapped %i numUnmappedFirst %i numQueryUnmapped %i numMateUnmapped %i\n"%(rpthash["numPairedUnmapped"+rgid], rpthash["numUnmappedFirst"+rgid], rpthash["numQueryUnmapped"+rgid], rpthash["numMateUnmapped"+rgid]))

		#rptJson = {"bamTotalReads":str(nreads),"numTranslocations":str(foundntrans),"cumulativeAvg":str(cumulativeAvg),"pairsGT0":str(pairsGT0),"cumulativeRangedAvg":str(cumulativeRangedAvg),"numTranslocationsSamChrom":str(nsamechromtrans),"numTranslocationsDiffChrom":str(ndiffchromtrans),"numTransNotStrand":str(numTransNotStrand),"pairsRangedGT0":str(pairsRangedGT0),"num11":str(num11),"num10":str(num10),"num01":str(num01),"num00":str(num00),"zeroDistance":str(zeroDistance),"numSkipped":str(numSkipped), "numPairedUnmapped":str(numPairedUnmapped), "numQueryUnmapped":str(numQueryUnmapped), "numMateUnmapped":str(numMateUnmapped), "numUnmappedFirst":str(numUnmappedFirst)}
		#cumRptFile.write("\n" + json.dumps(rptJson) + "\n")


def cleanup():
	global outhash
	for o in outhash:
		outhash[o].close()
	print("Program completed: Done cleaning up:" + str(time.strftime("%c")))

#list of functions to check filter flag to find information about read/strand info
def getQueryUnmapped(fval):
        return ((fval & 0x0004) > 0)

#dec 8 bin 2^3
def getMateUnmapped(fval):
        return ((fval & 0x0008) > 0)

#dec 16 bin 2^4
def getStrandQ(fval):
        return ((fval & 0x0010) > 0)

#dec 32 bin 2^5
def getStrandM(fval):
        return ((fval & 0x0020) > 0)

#dec 64 bin 2^6
def isFirstRead(fval):
        return ((fval & 0x0040) > 0)

#dec 128 bin 2^7
def isSecondRead(fval):
        return ((fval & 0x0080) > 0)

#dec 512 bin 2^9
def isFailedQC(fval):
        return ((fval & 0x0200) > 0)

#dec 1024 bin 2^10
def isDuplicate(fval):
        return ((fval & 0x0400) > 0)


#print out some statistics about what has been found
#hopefully enough to figure out if it is in fact an illumina faile with
#mate pairs
#usage : summarize(pairs,trans,sumedlength/(i+1),sumeddistance/(i+1))
#cumulativeAvg = float(0.0)
def updateCumulativeAvg(rgid, i,val):
	global rpthash
	i = float(i)
	val = float(val)
	rpthash["cumulativeAvg"+rgid] = (val + (i-1)*rpthash["cumulativeAvg"+rgid])/i

#cumulativeRangedAvg = float(0.0)
def updateCumulativeRangedAvg(rgid, i,val):
	global rpthash
	i = float(i)
	val = float(val)
	rpthash["cumulativeRangedAvg"+rgid] = (val + (i-1)*rpthash["cumulativeRangedAvg"+rgid])/i

#capture distance and mapQScore by strand orientation
def reportOrientationAndDistanceQS(rgid, strandQ, strandM, myDistance, mapQScore, readPos, matePos):
	global rpthash, outhash
	trans = False
	if strandQ:
		if strandM:
			rpthash["num11"+rgid]+=1
			trans = True
			outhash["distance11"+rgid].write('%s,' % str(myDistance))
        		outhash["distance11MapQ"+rgid].write('%s,' % str(mapQScore))
		else: #10, not trans only if  
			if matePos > readPos:
				rpthash["num10"+rgid]+=1
				trans = True
				outhash["distance10"+rgid].write('%s,' % str(myDistance))
                		outhash["distance10MapQ"+rgid].write('%s,' % str(mapQScore))
			else:
				# --> <-- good case mPos > rPos 
				rpthash["num01"+rgid]+=1
				trans = False
				outhash["distance01"+rgid].write('%s,' % str(myDistance))
                		outhash["distance01MapQ"+rgid].write('%s,' % str(mapQScore))
	else:
		if strandM:
			if matePos > readPos:
				rpthash["num01"+rgid]+=1
				trans = False
				outhash["distance01"+rgid].write('%s,' % str(myDistance))
                		outhash["distance01MapQ"+rgid].write('%s,' % str(mapQScore))
			else: 
				rpthash["num10"+rgid]+=1
				trans = True
				outhash["distance10"+rgid].write('%s,' % str(myDistance))
                		outhash["distance10MapQ"+rgid].write('%s,' % str(mapQScore))
		else:
			rpthash["num00"+rgid]+=1
			trans = True
			outhash["distance00"+rgid].write('%s,' % str(myDistance))
            		outhash["distance00MapQ"+rgid].write('%s,' % str(mapQScore))
	return trans

		

def putInAllBuckets(rgid, myDistance, read, chrom, pos, qname, seq, mapQScore):
	global outhash
	outhash["alldistance" + rgid].write('%s,' % str(myDistance))
	outhash["alldistanceMapQ" + rgid].write('%s,' % str(mapQScore))
	if myDistance > 500000:
		#bucketArray[499999]+=1
		outhash["outlier" + rgid].write('%s,%s,%s,%s,%s,%s,%s\n' % (str(read), chrom, str(pos), qname, seq, str(mapQScore), str(myDistance)))
	#else:
	#	bucketArray[int(math.floor(myDistance/10))]+=1

def getTile(pos):
        return int(math.floor(float(pos)/float(tileWidth)))
		
def writeWig(chr,pos):
	global beginRangePos,currentRangeChrom,outhash,rghash,rpthash
	for rgid in rghash:
		sameRangeProb = 0.0
		diffRangeProb = 0.0
		if rpthash["rangeReads"+rgid] > 0:
			sameRangeProb = float(rpthash["rangeSameChrTransCount"+rgid])/float(rpthash["rangeReads"+rgid])
			diffRangeProb = float(rpthash["rangeDiffChrTransCount"+rgid])/float(rpthash["rangeReads"+rgid])
		outhash["wigsame"+rgid].write('%s\t%f\n' % (beginRangePos,sameRangeProb))			
		outhash["wigdiff"+rgid].write('%s\t%f\n' % (beginRangePos,diffRangeProb))
		if currentRangeChrom != chr:
			timenow = time.strftime("%c")
			print 'FindTrans Executing finishing chromosome %s and beginning %s at time %s' % (currentRangeChrom, chr, timenow)
			outhash["wigsame"+rgid].write('variableStep chrom=%s span=%s\n' % (chr, tileWindow))
			outhash["wigdiff"+rgid].write('variableStep chrom=%s span=%s\n' % (chr, tileWindow))
			currentRangeChrom = chr
		rpthash["rangeSameChrTransCount"+rgid] = 0
		rpthash["rangeDiffChrTransCount"+rgid] = 0
		rpthash["rangeReads"+rgid] = 0
		beginRangePos = int(pos)

def writeTile(chr,pos):
        global tileStart, outhash, rpthash, rghash, currentTileChrom
	binStart = tileStart
	#bin1 will hold the tileReads, tileReads - 1 to account for the pos read outside this bin
	for rgid in rghash:
		if (pos - tileStart > int(tileWindow)):
			rpthash["tilereads"+rgid] = rpthash["tilereads"+rgid] - 1
		outhash["tilecov"+rgid].write('%s,' % str(rpthash["tilereads"+rgid]))
		if rpthash["tilereads"+rgid] > 0:
			outhash["tile"+rgid].write('%s\t%i\n' % (binStart, rpthash["tilereads"+rgid]))
		rpthash["tilereads"+rgid] = 1 
        
		if currentTileChrom != chr:
        		outhash["tile"+rgid].write('variableStep chrom=%s span=%s\n' % (chr, tileWindow))                     
			currentTileChrom = chr
			rpthash["tilereads"+rgid] = 0

# tiling orientation 10 and distance of less than tileWindow (default to be 1000) 
def writeTile10(chr,pos,currentReadIs10):
        global tileStart, outhash, rpthash, rghash, currentTile10Chrom
        binStart = tileStart
       	for rgid in rghash:
        	#bin1 will hold the tileReads, tileReads - 1 if the current read counted and is outside the bin range
        	if (rpthash["tilereads10"+rgid] > 1 and currentReadIs10 == True and (pos - tileStart > int(tileWindow))):
            		rpthash["tilereads10"+rgid] = rpthash["tilereads10"+rgid] - 1
        	if rpthash["tilereads10"+rgid] > 0:
			outhash["tile10"+rgid].write('%s\t%i\n' % (binStart, rpthash["tilereads10"+rgid]))
        	rpthash["tilereads10"+rgid] = 0
			
		if currentReadIs10 == True:
			rpthash["tilereads10"+rgid] = 1

        	if currentTile10Chrom != chr:
            		outhash["tile10"+rgid].write('variableStep chrom=%s span=%s\n' % (chr, tileWindow))
                	currentTile10Chrom = chr
                	rpthash["tilereads10"+rgid] = 0

# FastQ format
# @header
# seq
# +
# qual
def writeBam2Fastq(rgid, qname,seq,qual):
        global outhash
        outhash["fastq"+rgid].write('@%s\n%s\n+\n%s\n' % (qname, seq, qual))

def reportMappingMetrics(rgid, queryUnmapped,mateUnmapped,isFirstR):
	global rpthash
        if queryUnmapped or mateUnmapped:
                if not queryUnmapped:
                        rpthash["numMateUnmapped"+rgid] += 1
                if not mateUnmapped:
                        #numQueryUnmapped +=1
                        rpthash["numQueryUnmapped"+rgid] += 1	
                if isFirstR:
                        #numUnmappedFirst += 1
                        rpthash["numUnmappedFirst"+rgid] += 1	
                if queryUnmapped and mateUnmapped:
                        #numPairedUnmapped +=1
                        rpthash["numPairedUnmapped"+rgid] += 1	
                        

#begin main 
rgid = "rg_all"
currentPos = 0
for line in sys.stdin:
	#this section splits the line into terns and checks to make sure it is in the readGroups if provided
	read = {}
	if line.startswith("@"):
		if doReadGroups and line.startswith("@RG"):		
			rgterm = line.split("\t")[1]			
			rgid = "rg" + rgterm.split(":")[1]
			print "Doing readgroupids %s\n" % (rgid)
			rghash[rgid] = rgid
			continue
		else:			
			continue
	else:
		if not initialized:
			print "Initializing"
			initialize()
			initialized = True
	
	for j,term in enumerate(line.split("\t")):
		if doReadGroups:
			if term.startswith("RG:Z:"):
				rgid = "rg" + term.split(":")[2].rstrip()
		#else:
		#	rgid = "rg_all"
		if j<samcolumnslen:
			read[samcolumns[j]]=term
				
	rpthash["nreads"+rgid] +=1
	rpthash["rangeReads"+rgid] +=1	
	rpthash["tilereads"+rgid] +=1
	
	trans = False	
	qname = read["qname"]
	rname = read["rname"]
	randomIndex = string.find(rname, "random")
	myFlag = int(read["flag"])
	queryUnmapped = getQueryUnmapped(myFlag)
	mateUnmapped = getMateUnmapped(myFlag)
	isFirstR = isFirstRead(myFlag)
	isSecondR = isSecondRead(myFlag)	
	strandQ = getStrandQ(myFlag)
	strandM = getStrandM(myFlag)
	dupeFlag = isDuplicate(myFlag)
	failedQC = isFailedQC(myFlag)
	mPos = int(read["mpos"])
	rPos = int(read["pos"])
	mapQScore = int(read["mapq"])
	isize = int(read["isize"])
	seq = read["seq"]
	length = len(seq)
	qual = read["qual"]
	#sumedlength += length
	#tiling for strand 10 between 50 and 1000
	currentReadIs10 = False
	if strandQ == True and strandM == False and (isize > transRange1 and isize < transRange2):
		rpthash["tilereads10"+rgid] +=1
		currentReadIs10 = True
	#generate fastQ file
	if generateFastQ == 1:
		writeBam2Fastq(rgid, qname, seq, qual)

	#report Mapping metrics
	if reportMappingMetrics == 1:
		reportMappingMetrics(rgid, queryUnmapped, mateUnmapped, isFirstR)

	#wig coverage tile
        if ((rPos - tileStart) >  tileWidth or currentTileChrom != rname) and (rname != "*" or randomIndex == -1):
		writeTile(rname, rPos)
		writeTile10(rname, rPos, currentReadIs10)
		tileStart = getTile(rPos)*tileWidth
		currentPos = rPos
	#wig probability		
	if ((rPos - beginRangePos) >  rangeWidth or currentRangeChrom != rname) and (rname != "*" or randomIndex == -1):
		writeWig(rname,rPos)

	if reportOrientationAndDistance == 1:
		if rname == "chrM" or mPos == 0 or mapQScore == 0 or dupeFlag or failedQC or randomIndex > 0:
			rpthash["numSkipped"+rgid] +=1
			if saveSkippedInfo:
				outhash["skipped"+rgid].write('\t'.join([rname, str(mPos), str(mapQScore), str(dupeFlag), str(failedQC), str(randomIndex) + '\n']))
		else:	
			rpthash["pairs"+rgid]+=1		
			#consider using ISIZE column
			#distance = abs(rPos - mPos)
			distance = abs(isize)
			if distance > 0:
				rpthash["pairsGT0"+rgid] += 1
				updateCumulativeAvg(rgid, rpthash["pairsGT0"+rgid],distance)
				if distance < 500000:
					rpthash["pairsRangedGT0"+rgid] += 1
					updateCumulativeRangedAvg(rgid, rpthash["pairsRangedGT0"+rgid],distance)			
			else:
				rpthash["zeroDistance"+rgid] +=1
				
			#place distance within range(except for < 50 case) of nontrans in bins 0 .. 18
			same_chrom= (rname == read["mrnm"] or read["mrnm"] == "=")
		
			trans = reportOrientationAndDistanceQS(rgid, strandQ, strandM, distance, mapQScore, rPos, mPos)
			#place below into function	
			if trans == False:
				if not(same_chrom):
					trans = True
				elif distance > 1000:
					trans = True
					rpthash["numTransNotStrand"+rgid] += 1
					
			if same_chrom:
				#sumeddistance += distance
				putInAllBuckets(rgid, distance, i, rname, rPos, qname, seq, mapQScore)
				rpthash["numSamechrom"+rgid] += 1
				if not trans:
					#nontrandistance += distance
					rpthash["nontranpairs"+rgid] +=1
			else:	
				rpthash["numNotSamechrom"+rgid] += 1
			
			if trans == True and same_chrom:
				rpthash["nsamechromtrans"+rgid]+=1
				rpthash["rangeSameChrTransCount"+rgid]+=1			
			elif trans == False:
				rpthash["rangeDiffChrTransCount"+rgid]+=1
				rpthash["ndiffchromtrans"+rgid]+=1
				
			if trans == True:
				rpthash["ntrans"+rgid]+=1			
				outhash["oddreadbed"+rgid].write('\t'.join([rname,read["pos"],str(rPos+length),"na",'1\n']))
				outhash["oddreadlist"+rgid].write('\t'.join([rname,read["pos"],read["mrnm"],read["mpos"],read["mapq"],str(distance),str(strandQ),str(strandM)])+"\n")
						 
			#if i%timefirstn==0:
			#	avgdistance = 0
			#	avgnontrandistance=0
			#	if numSamechrom>0:
			#		avgdistance= sumeddistance/numSamechrom
			#	if nontranpairs > 0:
			#		avgnontrandistance = nontrandistance/nontranpairs			
		i+=1
#end of for loop
#remaining reads
writeWig(currentRangeChrom,"-1")
writeTile(currentTileChrom, currentPos)			
writeTile10(currentTileChrom, currentPos, False)
reportSummary()
cleanup()

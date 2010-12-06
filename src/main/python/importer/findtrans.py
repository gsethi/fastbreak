__author__ = 'RyanBressler_JakeLin'
#findtrans.py - fastbreak pass1
#Usage with config file samtools view -h XXX.sorted.bam | python findtrans.py sample-label myConfig.config   
#ie nice /titan/cancerregulome2/bin/samtools-0.1.7_x86_64-linux/samtools view -h /titan/cancerregulome8/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/coad/wugsc/exchange/TCGA_phs000178/TCGA-AA-A02J-01A-01W-A00E-09_IlluminaGA-DNASeq_exome.sorted.bam | nice /tools/bin/python /titan/cancerregulome2/synthetic_cancer/python/findtrans.py TCGA-AA-A02J-01A-01W_refactored /titan/cancerregulome2/synthetic_cancer/python/configs/pass1.config	 	 	 

#Alternative usage with inline arguments ie 

detailedText = """nice /path/samtools-0.1.7_x86_64-linux/samtools view -h /bamPath/myBam.sorted.bam | nice /tools/bin/python /path/findtrans.py BAMLabel resultsDir 1000 1000 50 1000 500000 1 0 1 0 0
resultsDir = output directory 
1000 = calledTransSize
1000 = tileWindow
50 = transRangeStart
1000 = transRangeEnd
500000 = outlierDistance
1 = reportOrientationAndDistance 
0 = generateFastQ (uses lots of disk space)
1 = reportMappingMetrics
0 = readGroups (Group outputs by readGroupID for QA purposes, see SAM Format Manual)
0 = savedDiscarded Reads (uses lots of disk space)
"""
#Email jlin or rbressler@systemsbiology.org if you need more help or have questions

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
import os
import errno
import string
import ConfigParser
import optparse
import time
from time import gmtime, strftime, localtime
import math
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json

usage = "usage: Fastbreak Pass1 module is used to collect reads with odd distances and orientations. See Readme for more information. This script is designed to use samtools view -h with paired end bam files sorted by chromosome position. \nsamtools view -h XXX.sorted.bam | python findtrans.py sample-bam-label myConfig.config(see ./configs/pass1.config for template) \n[In-line Parameters mode ie\n %s]" % detailedText
parser = optparse.OptionParser(usage=usage)

args = parser.parse_args()
argsLen = len(sys.argv)
print argsLen

if argsLen < 2:
	parser.error("BAMLabel is required")
if argsLen > 3 and argsLen != 13:
	parser.error("Tried running inline mode, missing required arguments, follow this example %s\n" %(detailedText))
sampleBamLabel = sys.argv[1]
if argsLen == 3:
	configFile = sys.argv[2]
	if not os.path.exists(configFile):
		parser.error("Config file %s does not exist" % configFile)

#Read in Fastbreak Pass 1 configurations or In-line parameters
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	transLowerBound = config.getint("Fastbreak_Called_Parameters", "CalledTransSize")
	tileWindow = config.getint("Fastbreak_QA_Parameters", "TileWindow")
	transRange1 = config.getint("Fastbreak_QA_Parameters", "TransRange1")
	transRange2 = config.getint("Fastbreak_QA_Parameters", "TransRange2")
	outlierDistance = config.getint("Fastbreak_QA_Parameters", "OutlierDistance")
	resultsRelativePath = config.get("Fastbreak_Output_Parameters", "ResultsRelativePath")
	reportOrientationAndDistance = config.getint("Fastbreak_Output_Parameters", "ReportOrientationAndDistance")
	generateFastQ = config.getint("Fastbreak_Output_Parameters", "GenerateFastQ")
	doReportMappingMetrics = config.getint("Fastbreak_Output_Parameters", "ReportMappingMetrics")
	doReadGroups = config.getint("Fastbreak_Output_Parameters", "DoReadGroups")
	saveSkippedInfo = config.getint("Fastbreak_Output_Parameters", "SaveSkippedInfo")
else:
	resultsRelativePath = sys.argv[2]
	transLowerBound = int(sys.argv[3])
	tileWindow = int(sys.argv[4])
	transRange1 = int(sys.argv[5])
	transRange2 = int(sys.argv[6])
	outlierDistance = int(sys.argv[7])
	reportOrientationAndDistance = int(sys.argv[8])
	generateFastQ = int(sys.argv[9])
	doReportMappingMetrics = int(sys.argv[10])
	doReadGroups = int(sys.argv[11])
	saveSkippedInfo = int(sys.argv[12])

initialized = False

#Create results path if necessary
try:
	os.makedirs(resultsRelativePath)
except OSError, exc:
	if exc.errno == errno.EEXIST: pass
	else: raise

outhash = {}
rghash = {}
rpthash = {}

timenow = time.strftime("%c")
print 'FindTrans Execution begins: %s for sampleBam  %s calledTransSize %i tileWindow %i transRange1 %i transRange2 %i outLierSize %i reportOrientationAndDistance %s genFastq %s reportMapping %s results path %s' % (timenow, sampleBamLabel, transLowerBound, tileWindow, transRange1, transRange2, outlierDistance, str(reportOrientationAndDistance), str(generateFastQ), str(doReportMappingMetrics), resultsRelativePath)
i = 1
beginRangePos = 0
#sorted bams are sorted by chromosome and position, chrM are the initial chromosome and we disregard these reads 
currentRangeChrom = "chrM"
currentTileChrom = "chrM"
currentTile10Chrom = "chrM"
samcolumns = ["qname","flag","rname","pos","mapq","ciagr","mrnm","mpos","isize","seq","qual","opt"]
samcolumnslen = len(samcolumns)
tileStart = 0

# Function that inits a set of filenames to capture results and qa and store them inside a class hash 
def initialize():
	global outhash, rghash, rpthash, sampleBamLabel, doReadGroups
	if doReadGroups == 0:
		rghash["rg_all"] = "rg_all"

	for rid in rghash:
		plr = sampleBamLabel + rid		
		#outhash["bucket" + rid] = open(resultsRelativePath + "/" + plr + "_AllBinsSameChrom_500K", 'w')
		if generateFastQ == 1:
			outhash["fastq" + rid] = open(resultsRelativePath + "/" + plr + ".fastq", 'w')		
		outhash["tilecov" + rid] = open(resultsRelativePath + "/" + plr + ".tile.cov", 'w')		
		outhash["tile10" + rid] = open(resultsRelativePath + "/" + plr + ".tile10.wig", 'w')		
		outhash["tile10" + rid].write('variableStep\tchrom=chrM\tspan=%i\n' % tileWindow)		
		outhash["tile" + rid] = open(resultsRelativePath + "/" + plr + ".tile.wig", 'w')		
		outhash["tile" + rid].write('variableStep\tchrom=chrM\tspan=%i\n' % tileWindow)
		outhash["oddreadbed" + rid] = open(resultsRelativePath + "/" + plr+"oddreads.bed", 'w')		
		outhash["oddreadbed" + rid].write('\t'.join(["Chromosome","Start","End","Feature","Translocations\n"]))
		outhash["oddreadlist" + rid] = open(resultsRelativePath + "/" + plr+"oddreads.list", 'w')
		outhash["oddreadlist" + rid].write('\t'.join(["FromChr","FromPos","ToChr","ToPos","MapQ","Distance","StrandQ","StrandM","QName\n"]))
		outhash["wigsame" + rid] = open(resultsRelativePath + "/" + plr + ".same.wig", 'w')		
		outhash["wigsame" + rid].write('variableStep\tchrom=chrM\tspan=%i\n' % tileWindow)
		outhash["wigdiff" + rid] = open(resultsRelativePath + "/" + plr + ".diff.wig", 'w')
		outhash["wigdiff" + rid].write('variableStep\tchrom=chrM\tspan=%i\n' % tileWindow)
		outhash["alldistance" + rid] = open(resultsRelativePath + "/" + plr + "_distanceAll", 'w')
		outhash["alldistanceMapQ" + rid] = open(resultsRelativePath + "/" + plr + "_distanceAllMapQ", 'w')
		outhash["distance11" + rid] = open(resultsRelativePath + "/" + plr + "_distance11", 'w')
		outhash["distance11MapQ" + rid] = open(resultsRelativePath + "/" + plr + "_distance11MapQ", 'w')
		outhash["distance10" + rid] = open(resultsRelativePath + "/" + plr + "_distance10", 'w')
		outhash["distance10MapQ" + rid] = open(resultsRelativePath + "/" + plr + "_distance10MapQ", 'w')
		outhash["distance01" + rid] = open(resultsRelativePath + "/" + plr + "_distance01", 'w')
		outhash["distance01MapQ" + rid] = open(resultsRelativePath + "/" + plr + "_distance01MapQ", 'w')
		outhash["distance00" + rid] = open(resultsRelativePath + "/" + plr + "_distance00", 'w')
		outhash["distance00MapQ" + rid] = open(resultsRelativePath + "/" + plr + "_distance00MapQ", 'w')
		outhash["outlier" + rid] = open(resultsRelativePath + "/" + plr + "_outlierReadings", 'w')
		outhash["outlier" + rid].write('read pos chromosome qname seq score distance\n')
        	if saveSkippedInfo == 1:
			outhash["skipped" + rid] = open(resultsRelativePath + "/" + plr + "_skipped", 'w')
                	outhash["skipped" + rid].write('rname\tmPos\tmapQScore\tdupeFlag\tfailedQC\trandomIndex\n')
		outhash["summary" + rid] = open(resultsRelativePath  + "/" + plr + "_summary", 'w')
        
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
		rpthash["numNotPaired"+rid] = 0
		rpthash["numNotProperPair"+rid] = 0
		rpthash["numPairedUnmapped"+rid] = 0
		rpthash["numUnmappedFirst"+rid] = 0
		rpthash["numQueryUnmapped"+rid] = 0
		rpthash["numMateUnmapped"+rid] = 0
		rpthash["nontrandistance"+rid] = 0
		rpthash["nontranpairs"+rid] = 0
		rpthash["numTransNotStrand"+rid] = 0
		rpthash["rangeSameChrTransCount"+rid] = 0
		rpthash["rangeDiffChrTransCount"+rid] = 0

#Metrics Summary reporting, called at the end of processing bam file
def reportSummary():
	global rghash, outhash, rpthash, doReportMappingMetrics
	for rgid in rghash:
		print("summarizing readgroup:" + rgid + "\n")
		cumRptFile = outhash["summary" + rgid]
		cumRptFile.write("Patient %s rg %s\n"%(sampleBamLabel, rgid))
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
		
		if doReportMappingMetrics == 1:
			cumRptFile.write("numNotReadPaired %i \nnumNotProperPaired %i \nnumPairedUnmapped %i \nnumUnmappedFirst %i \nnumQueryUnmapped %i \nnumMateUnmapped %i\n"%(%(rpthash["numNotPaired"+rgid], rpthash["numNotProperPair"+rgid], rpthash["numPairedUnmapped"+rgid], rpthash["numUnmappedFirst"+rgid], rpthash["numQueryUnmapped"+rgid], rpthash["numMateUnmapped"+rgid]))

#Cleanup
def cleanup():
	global outhash
	for o in outhash:
		outhash[o].close()
	print("Program completed: Done cleaning up:" + str(time.strftime("%c")))

#list of functions to check filter flag to find information about read/strand info
#dec 1 2^0 - depends on protocol and inferred during alignment
def gePaired(fval):
	return ((fval & 0x0001) > 0)

#dec 2 2^1 - depends on protocol and inferred during alignment
def getProperPair(fval):
	return ((fval & 0x0002) > 0)

#dec 4 2^2
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


#updates cumulative average
def updateCumulativeAvg(rgid, i, val):
	global rpthash
	i = float(i)
	val = float(val)
	rpthash["cumulativeAvg"+rgid] = (val + (i-1)*rpthash["cumulativeAvg"+rgid])/i

#updates cumulative ranged average
def updateCumulativeRangedAvg(rgid, i, val):
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

		
#Captures Distance for all reads
def putInAllBuckets(rgid, myDistance, read, chrom, pos, qname, seq, mapQScore):
	global outhash
	outhash["alldistance" + rgid].write('%s,' % str(myDistance))
	outhash["alldistanceMapQ" + rgid].write('%s,' % str(mapQScore))
	if myDistance > outlierDistance:
		#bucketArray[499999]+=1
		outhash["outlier" + rgid].write('%s,%s,%s,%s,%s,%s,%s\n' % (str(read), chrom, str(pos), qname, seq, str(mapQScore), str(myDistance)))
	#else:
	#	bucketArray[int(math.floor(myDistance/10))]+=1

#returns tile hash of read position
def getTile(pos):
        return int(math.floor(float(pos)/float(tileWindow)))

#Persisting wig (covereage)		
def writeWig(chr,pos):
	global beginRangePos,currentRangeChrom,outhash,rghash,rpthash
	if beginRangePos >= tileWindow:
		#to account for span nature of wig format
		beginRangePos = beginRangePos - tileWindow + 1
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
			outhash["wigsame"+rgid].write('variableStep chrom=%s span=%i\n' % (chr, tileWindow))
			outhash["wigdiff"+rgid].write('variableStep chrom=%s span=%i\n' % (chr, tileWindow))
			currentRangeChrom = chr
		rpthash["rangeSameChrTransCount"+rgid] = 0
		rpthash["rangeDiffChrTransCount"+rgid] = 0
		rpthash["rangeReads"+rgid] = 0
		beginRangePos = int(pos)

# writing tiles for 01 read strands
def writeTile(chr,pos):
        global tileStart, outhash, rpthash, rghash, currentTileChrom
	binStart = tileStart
	#bin1 will hold the tileReads, tileReads - 1 to account for the pos read outside this bin
	for rgid in rghash:
		if ((pos - tileStart) > tileWindow):
			rpthash["tilereads"+rgid] = rpthash["tilereads"+rgid] - 1
		outhash["tilecov"+rgid].write('%s,' % str(rpthash["tilereads"+rgid]))
		if rpthash["tilereads"+rgid] > 0:
			outhash["tile"+rgid].write('%s\t%i\n' % (binStart, rpthash["tilereads"+rgid]))
		rpthash["tilereads"+rgid] = 1 
        
		if currentTileChrom != chr:
        		outhash["tile"+rgid].write('variableStep chrom=%s span=%i\n' % (chr, tileWindow))                     
			currentTileChrom = chr
			rpthash["tilereads"+rgid] = 0

# tiling orientation 10 and distance of less than tileWindow (default to be 1000) 
def writeTile10(chr,pos,currentReadIs10):
        global tileStart, outhash, rpthash, rghash, currentTile10Chrom
        binStart = tileStart
       	for rgid in rghash:
        	#bin1 will hold the tileReads, tileReads - 1 if the current read counted and is outside the bin range
        	if (rpthash["tilereads10"+rgid] > 1 and currentReadIs10 == True and ((pos - tileStart) > tileWindow)):
            		rpthash["tilereads10"+rgid] = rpthash["tilereads10"+rgid] - 1
        	if rpthash["tilereads10"+rgid] > 0:
			outhash["tile10"+rgid].write('%s\t%i\n' % (binStart, rpthash["tilereads10"+rgid]))
        	rpthash["tilereads10"+rgid] = 0
			
		if currentReadIs10 == True:
			rpthash["tilereads10"+rgid] = 1

        	if currentTile10Chrom != chr:
            		outhash["tile10"+rgid].write('variableStep chrom=%s span=%i\n' % (chr, tileWindow))
                	currentTile10Chrom = chr
                	rpthash["tilereads10"+rgid] = 0

# FastQ format
# @header
# seq
# +
# qual
# Outputs huge file, use with caution
def writeBam2Fastq(rgid,qname,seq,qual):
        global outhash
        outhash["fastq"+rgid].write('@%s\n%s\n+\n%s\n' % (qname, seq, qual))

# Calculates read totals for different strands 
def reportMappingMetrics(rgid,paired,properPair,queryUnmapped,mateUnmapped,isFirstR):
	global rpthash
	if not paired:
		rpthash["numNotPaired"+rgid] += 1
	if not properPair:
		rpthash["numNotProperPair"+rgid] += 1
        if queryUnmapped or mateUnmapped:	
                if not queryUnmapped:
                        rpthash["numMateUnmapped"+rgid] += 1
                if not mateUnmapped:
                        rpthash["numQueryUnmapped"+rgid] += 1	
                if isFirstR:
                        rpthash["numUnmappedFirst"+rgid] += 1	
                if queryUnmapped and mateUnmapped:
                        rpthash["numPairedUnmapped"+rgid] += 1	
                        

#begin main - receives IO from samtools -view 
rgid = "rg_all"
currentPos = 0
for line in sys.stdin:
	#this section splits the line into terns and checks to make sure it is in the readGroups if provided
	read = {}
	if line.startswith("@"):
		if doReadGroups == 1 and line.startswith("@RG"):		
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
		if doReadGroups == 1:
			if term.startswith("RG:Z:"):
				rgid = "rg" + term.split(":")[2].rstrip()
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
	paired = getPaired(myFlag)
	properPair = getProperPair(myFlag)
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
	if doReportMappingMetrics == 1:
		reportMappingMetrics(rgid, paired, properPair, queryUnmapped, mateUnmapped, isFirstR)

	#wig coverage tile
        if ((rPos - tileStart) >  tileWindow or currentTileChrom != rname) and (rname != "*" or randomIndex == -1):
		writeTile(rname, rPos)
		writeTile10(rname, rPos, currentReadIs10)
		tileStart = getTile(rPos)*tileWindow
		currentPos = rPos
	#wig probability		
	if ((rPos - beginRangePos) >  tileWindow or currentRangeChrom != rname) and (rname != "*" or randomIndex == -1):
		writeWig(rname,rPos)

	if reportOrientationAndDistance == 1:
		if paired == False or rname == "chrM" or mPos == 0 or mapQScore == 0 or dupeFlag or failedQC or randomIndex > 0:
			rpthash["numSkipped"+rgid] +=1
			if saveSkippedInfo == 1:
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
			if trans == False:
				if not(same_chrom):
					trans = True
				elif distance > transLowerBound:
					trans = True
					rpthash["numTransNotStrand"+rgid] += 1
					
			if same_chrom:
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
			elif trans == True:
				rpthash["rangeDiffChrTransCount"+rgid]+=1
				rpthash["ndiffchromtrans"+rgid]+=1
				
			if trans == True:
				rpthash["ntrans"+rgid]+=1			
				outhash["oddreadbed"+rgid].write('\t'.join([rname,read["pos"],str(rPos+length),"na",'1\n']))
				outhash["oddreadlist"+rgid].write('\t'.join([rname,read["pos"],read["mrnm"],read["mpos"],read["mapq"],str(distance),str(strandQ),str(strandM),qname])+"\n")
						 
		i+=1
#end of for loop
#remaining reads
writeWig(currentRangeChrom,"-1")
writeTile(currentTileChrom, currentPos)			
writeTile10(currentTileChrom, currentPos, False)
reportSummary()
cleanup()

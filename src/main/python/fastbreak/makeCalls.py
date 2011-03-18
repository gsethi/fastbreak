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

import sys
import math

import tsvparser

tileWidth=1000
minNReads = 2
minSameBinReads=4
minRatio=.05
maxBinDistance = 7
minMapQ = 0
minScore = 0
headers = []
debug = False
writeDistance = True
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
	if debug:
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
				if curChrm in coverage and curBin in coverage[curChrm]:
					currentCov = float(coverage[curChrm][curBin])
				if writeDistance:
					if curChrm == chr:
						for d in distanceCutoffs:
							if count >= int(d):
								distanceFiles[type][d].write(str(1000*math.fabs(int(bin)-int(curBin)))+",")
						for c in coverageCutoffs:
							
							if currentCov != 0:
								if float(count)/currentCov >= c:
									coverageFiles[type][c].write(str(1000*math.fabs(int(bin)-int(curBin)))+",")
							else:
								print "WARNING READS FOUND IN BIN WITH 0 COVERAGE"						
								
						
				if currentCov != 0:
					if count >= minNReads and float(count)/currentCov >= minRatio and ( (curChrm == chr and curBin != bin and type == "01" and math.fabs(int(curBin)-int(bin))<maxBinDistance)):
						cout.write("\t".join(["%s"%el for el in[curChrm,tileStart,chr,int(bin)*tileWidth,type,count,score]])+"\tsmall\n")
					elif count >= minNReads and float(count)/currentCov >= minRatio:
						cout.write("\t".join(["%s"%el for el in[curChrm,tileStart,chr,int(bin)*tileWidth,type,count,score]])+"\tother\n")

def getTile(pos):
	return int(math.floor(float(pos)/float(tileWidth)))
	
def makeCalls(fo,cout,fn):
	global headers
	global tileWidth
	global writeDistance, distanceCutoffs, coverageCutoffs, distanceFiles,coverageFiles, types, coverage
	if writeDistance:
		coverage = loadWigHash(fn.replace("oddreads.listdistances",".tile.wig"))
		
		for t in types:
			distanceFiles[t]={}
			coverageFiles[t]={}
			for d in distanceCutoffs:
				distanceFiles[t][d]=open(str(fn)+"distance"+str(t)+"cutoff"+str(d),"w")
			for c in coverageCutoffs:
				coverageFiles[t][c]=open(str(fn)+"distance"+str(t)+"coveragecutoff"+str(c),"w")
	firstline = True
	curChrm = ""
	tileStart = 0
	acum = {}
	
	for line in fo:
		if firstline:
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
		if curChrm != chr or fpos - tileStart > tileWidth:
			log("Doing bin %s %i"%(chr,tileStart))
			outputTile(cout,acum,curChrm,tileStart)
			acum = {}
			curChrm = chr
			tileStart = getTile(fpos)*tileWidth
		if not tchr in acum:
			acum[tchr]={}
		type = ""
		
		if int(fpos) > int(tpos) and tchr == chr:
			type = bTo01s(vs["StrandQ"])+bTo01s(vs["StrandM"])
		else:
			type = bTo01s(vs["StrandM"])+bTo01s(vs["StrandQ"])
		
		if not type in acum[tchr]:
			acum[tchr][type]={}
		
		tobin = getTile(tpos)
		
		if not tobin in acum[tchr][type]:
			acum[tchr][type][tobin]={"count":1,"score":1.0-float(vs["MapQ"])/100.0}
		else:
			log("bin exsists")
			acum[tchr][type][tobin]["count"]=int(acum[tchr][type][tobin]["count"])+1
			acum[tchr][type][tobin]["score"]=float(acum[tchr][type][tobin]["score"])*(1.0-mapQ/100.0)
	
	outputTile(cout,acum,curChrm,tileStart)
	if writeDistance:
		for t in types:
			for d in distanceCutoffs:
				distanceFiles[t][d].close()
			for d in coverageCutoffs:
				coverageFiles[t][d].close()
			
if __name__ == "__main__":
	filename = sys.argv[1]
	makeCalls(open(filename,"r"),open(filename+"called","w"),filename+"distances")
	#makeCalls(sys.stdin,sys.stdout)
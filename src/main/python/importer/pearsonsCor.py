import makeCalls
import math
import glob
import averageCorelations


def doCor(breakfn,covfn,breakFilter,breakTileCount):
    minCov=1
    minBreaks=0
    breakf = open(breakfn)


    breakDic  = {}

    for line in breakf:
        chr1, pos1, chr2, pos2 = line.split("\t")[0:4]

        for cp in [[chr1, makeCalls.getTile(pos1)],[chr1,makeCalls.getTile(pos1)]]:
            if cp[0] not in breakDic:
                breakDic[cp[0]]={}
            if cp[1] not in breakDic[cp[0]]:
                breakDic[cp[0]][cp[1]] = 1
            else:
                breakDic[cp[0]][cp[1]]+=1

    totalCount = 0
    totalCov = 0
    totalBreaks = 0

    coverage = makeCalls.loadWigHash(covfn)

    for chr in coverage:
        for tile in coverage[chr]:
            if coverage[chr][tile] >= minCov and chr in breakFilter and tile in breakFilter[chr]:
                breakCount = 0
                if chr in breakDic and tile in breakDic[chr]:
                     breakCount = breakDic[chr][tile]
                if breakCount >= minBreaks:
                    totalCount += 1
                    totalCov += coverage[chr][tile]
                    totalBreaks += breakCount


    covMean = totalCov/totalCount
    breakMean = totalBreaks/totalCount

    covarSum = 0.0
    covSDSum = 0.0
    breakSDSum = 0.0

    for chr in coverage:
        for tile in coverage[chr]:
            if coverage[chr][tile] >= minCov:
                breakCount = 0
                if chr in breakDic and tile in breakDic[chr]:
                     breakCount = breakDic[chr][tile]
                if chr in breakFilter and tile in breakFilter[chr]:
                    covDif = (coverage[chr][tile]-covMean)
                    breakDif = float(breakCount) - breakMean

                    covarSum += covDif*breakDif
                    covSDSum += covDif*covDif
                    breakSDSum += breakDif*breakDif

    covSD = math.sqrt(covSDSum/totalCount)
    breakSD = math.sqrt(breakSDSum/totalCount)

    denom1 = totalCount*covSD*breakSD
    denom2 = breakTileCount*covSD*breakSD

    return ["%s"%(e) for e in [covarSum/denom1 if denom1 != 0 else "NA", covarSum/denom2 if denom2 != 0 else "NA"]]


def findCovFileAndDoCor(filename,breakFilter,breakCount):
    distancefnglob = filename[0:28]+"*.tile.wig"
    fns = glob.glob(distancefnglob)
    if len(fns)>0:
        return doCor(filename,fns[0],breakFilter,breakCount)
    else:
        return ["NA","NA"]


def getLine(filen,breakFilter,breakCount):
	line = "%s\t%s\n"%(filen,"\t".join(findCovFileAndDoCor(filen,breakFilter,breakCount)))
	#print line
	return line

def getBreakFilter(patterns,minBreak):
    returnBreakDic = {}
    breakCount = 0
    for pattern in patterns:
        for filen in glob.glob(pattern):
			print "Loading "+filen
			breakf = open(filen)
			
			
			breakDic  = {}
			
			
			for line in breakf:
				chr1, pos1, chr2, pos2 = line.split("\t")[0:4]
			
				for chr,pos in [[chr1, makeCalls.getTile(pos1)],[chr2,makeCalls.getTile(pos2)]]:
					if chr not in breakDic:
						breakDic[chr]={}
					if pos not in breakDic[chr]:
						breakDic[chr][pos] = 1
					else:
						breakDic[chr][pos]+=1
			
					if breakDic[chr][pos] >= minBreak:
						if chr not in returnBreakDic:
							returnBreakDic[chr]={}
						if pos not in returnBreakDic[chr]:
							breakCount+=1
							returnBreakDic[chr][pos] = 1
			breakf.close()

    print "%i tiles have at least one break"%(breakCount)
    return returnBreakDic,breakCount

def getFilesAndDoCorAndAvgWooo(fn, pattern,breakFilter,breakCount):

    fo = open(fn,"w")

    for filen in glob.glob(pattern):
        fo.write(getLine(filen,breakFilter,breakCount))
    fo.close()

    print fn
    fo = open(fn)
    averageCorelations.doAvg(fo)
    fo.close()

if __name__ == "__main__":

    coverageCutoffs = [1,10,100,100]
    breakCutoffs =[0,1,2,4]
    for minBreaks in breakCutoffs:
        pattern1 = "*.bam.breakdancer.out.binned"
        pattern2 = "*oddreads.listcalled"

        breakFilter,breakCount = getBreakFilter([pattern1,pattern2],minBreaks)


        fn = "breakdancerCoverageCorelations_breakMin_%i.txt"%(minBreaks)

        getFilesAndDoCorAndAvgWooo(fn, pattern1,breakFilter,breakCount)


        fn = "fastbreakCoverageCorelations_breakMin_%i.txt"%(minBreaks)

        getFilesAndDoCorAndAvgWooo(fn, pattern2,breakFilter,breakCount)




















import os, glob, errno
import makeCalls
import scoreCalls

def scoreFilesByTile(inFilePattern,scorecolid,filenamebase):
	outf = open(filenamebase+".matrix.tsv","w")
	
	files = glob.glob(inFilePattern)
	print "%i files matching %s\n"%(len(files),inFilePattern)
	if len(files) == 0:
		return
		
	cols = ["chrom","pos"]
	chrList = []
	chrMax = {}
	scoresByFileChrPos = {}
	
	for file in files:
		cols.append(file)
		scoresByFileChrPos[file]={}
		fileobj = open(file,"r")
		#discard header
		fileobj.next()
		for line in fileobj:
			linevs = line.rstrip().split("\t")
			c = linevs[0]
			p = linevs[1]
			v = linevs[scorecolid]
			if not c in chrList:
				chrList.append(c)
			if not c in chrMax:
				chrMax[c]=int(p)
			elif int(p) > int(chrMax[c]):
				chrMax[c]=int(p)
				
			if not c in scoresByFileChrPos[file]:
				scoresByFileChrPos[file][c]={}
			scoresByFileChrPos[file][c][p]=v
		fileobj.close()
	
	
	
	# wigfiles = glob.glob("./*.tile.wig")
# 	coveragedic = {}
# 
# 	print "Finding Covered Regions"
# 	for wigfn in wigfiles:		
# 		print "Loading " + wigfn
# 		coveragedic[wigfn] =  makeCalls.loadWigHash(wigfn)
# 		
# 	coverageByTile = open("coverage.per.gene.per.tile.tsv", "w")
# 	coverageByTile.write("chr\tstart\t"+"\t".join(wigfiles))

		
	
	outf.write("\t".join(cols).rstrip()+"\n")		
	for chr in chrList:
		print "Checking bins for chr: %s %i to %i"%(chr,0,int(chrMax[chr]))
		for pos in xrange(0,int(chrMax[chr]),1000):
#			coverageByTile.write(chr+"\t"+pos+"\t"+"\t".join([ coveragedic[wigfn][chr][pos] if chr in coveragedic[wigfn] and pos in coveragedic[wigfn][chr] else 0 for wigfn in wigfiles]))
			includeBin = False
			colvs = [chr,str(pos)]
			for file in files:
				v = 0
				if chr in scoresByFileChrPos[file] and str(pos) in scoresByFileChrPos[file][chr]:
					
					v = scoresByFileChrPos[file][chr][str(pos)]
					includeBin = True
				colvs.append(str(v))
			if includeBin == True:
				outf.write("\t".join(colvs)+"\n")
	outf.close()
	
	wigfiles = glob.glob("./*.tile.wig")
	tiledic={}

	print "Finding Covered Bins"
	
	for wigfn in wigfiles:		
		print "Loading " + wigfn
		wigf =  makeCalls.loadWigHash(wigfn)
		outfn = wigfn+".tiled"
		outf = open(outfn,"w")
		for chr in chrList:
			for pos in xrange(0,int(chrMax[chr]),1000):
				outf.write( "%i\n"%(wigf[chr][pos] if chr in wigf and pos in wigf[chr] else 0))
		outf.close()
		tiledic[wigfn] = open(outfn,"r")
	
	coverageByTile = open("coverage.per.tile.per.sample.tsv", "w")
 	coverageByTile.write("chr\tstart\t"+"\t".join(wigfiles)+"\n")
 	
	
	for chr in chrList:
		print "Outputing coverage for chr: %s %i to %i"%(chr,0,int(chrMax[chr]))
		for pos in xrange(0,int(chrMax[chr]),1000):
			coverageByTile.write(str(chr)+"\t"+str(pos)+"\t"+"\t".join([ str(tiledic[wigfn].next().rstrip()) for wigfn in wigfiles])+"\n")

		


				
				
			
	
	
def scoreFiles(inFilePattern,scorecolid1,scorecolid2,filenamebase):
	outf1 = open(filenamebase+".col."+str(scorecolid1)+".matrix.tsv","w")
	outf2 = open(filenamebase+".col."+str(scorecolid2)+".matrix.tsv","w")
	
	files = glob.glob(inFilePattern)
	print "%i files matching %s\n"%(len(files),inFilePattern)
	if len(files) == 0:
		return
	cols = ["gene_symbol"]
	fileobjs = []
	for inf in files:
		cols.append(os.path.basename(inf).split(".")[0])
		fileobjs.append(open(inf,"r"))
	
	
	outf1.write("\t".join(cols)+"\n")
	outf2.write("\t".join(cols)+"\n")
	
	loop = True
	while loop==True:
		
		firstpass=True
		outvs1 = []
		outvs2 = []
		linevs = []
		for file in fileobjs:
			try:
				line = file.next()
			except StopIteration:
				loop=False
			if loop == True:
				linevs = line.rstrip().split("\t")
				if linevs[0] == "gene_symbol":
					continue
				if firstpass==True:
					outvs1.append(linevs[0])
					outvs2.append(linevs[0])
					firstpass = False
				outvs1.append(linevs[scorecolid1])
				outvs2.append(linevs[scorecolid2])

				
		if loop==True and len(linevs) > 1:
			outf1.write("\t".join(outvs1)+"\n")
			outf2.write("\t".join(outvs2)+"\n")
			
	outf1.close()
	outf2.close()
	for file in fileobjs:
		file.close()

def score():
	for scoreCutoff in [0,25,50,75,90,94,96,98,99]:
		print "Combining per gene fastbreak files"
		scoreFiles("./*listcalled.minScore."+str(scoreCutoff)+".pergene.tsv",4,5,"fastbreak.per.gene.score.minscore."+str(scoreCutoff))
	
	#print "Combining per gene breakdancer files"
	#scoreFiles("./*.breakdancer.out.t.per.gene",4,"breakdancer.per.gene.score")
	
	#print "Combining per tile fastbreak files"
	#scoreFilesByTile("./*.listcalled.bined.tsv",2,"fastbreak.per.tile.score")
	
	
	
	
	
	
	


if __name__ == "__main__":
	score()
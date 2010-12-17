import tsvparser
import genelist
import sys
import os, glob
import makeCalls

coveragecutoff = 1

calledHeaders = ["fromC","fromP","toC","toP","ori","count","score","type"]
chrMax = {}
globaldict={}
padby=1000
includeAllGenes = True


def addEvent(chr,pos,vs,type):
	global chrMax, globaldict
	
	if not chr in chrMax:
		chrMax[chr] = pos
	elif int(pos) > int(chrMax[chr]):
		chrMax[chr] = pos
		
	if not chr in globaldict:
		globaldict[chr]={}
	if not pos in globaldict[chr]:
		globaldict[chr][pos] = {}
	if not type in globaldict[chr][pos]:
		globaldict[chr][pos][type]=[]
	globaldict[chr][pos][type].append(vs)
		
def addChr(chr):
	chr=str(chr)
	if not chr.startswith("chr"):
		chr = "chr"+chr
	return chr
	

def loadCalledFile(fname,type):
	global globaldict

	fo = open(fname,"r")
	for line in fo:
		vs = tsvparser.parseLine(line,calledHeaders)
		
		
		addEvent(addChr(vs["fromC"]),vs["fromP"],vs,type)
		addEvent(addChr(vs["toC"]),vs["toP"],vs,type)
	fo.close()

		
def getCountSmall(Li,scoreCutoff):
	count = 0
	for vs in Li:
		if vs["type"].find("small")!=-1 and float(vs["score"]) >= scoreCutoff:
			count+=1
	return count
		
	
	
def getCountEdge(Li,scoreCutoff):
	count = 0
	for vs in Li:
		if vs["type"].find("other")!=-1 and float(vs["score"]) >= scoreCutoff:
			count+=1
	return count
	
	
# def scoreCalls(outfn,tumorFN,controlFN,genelistfn):
# 	global globaldict
# 	globaldict = {}
# 	loadCalledFile(	tumorFN,"t" )
# 	loadCalledFile( controlFN,"c" )
# 	
# 	types = ["small","other"]
# 	
# 	genes=genelist.loadGenes(genelistfn,types)
# 	
# 	binedout = open(outfn+".bined.tsv","w")
# 	binedout.write("chrom\tpos\tsmall\tother\n")
# 	
# 	
# 	for chr in globaldict:
# 		for bin in globaldict[chr]:
# 			pos = int(bin)
# 			tsmallcount = 0 
# 			csmallcount = 0
# 			tothercount = 0 
# 			cothercount = 0
# 			
# 			if "t" in globaldict[chr][bin]:
# 				 tsmallcount = getCountSmall(globaldict[chr][bin]["t"])
# 				 tothercount = getCountEdge(globaldict[chr][bin]["t"])
# 				 if chr in genes:
# 					for j, gene in enumerate(genes[chr]):
# 						if pos > gene["start"]-padby and pos < gene["end"]+padby:
# 							genes[chr][j]["small"] += tsmallcount
# 							genes[chr][j]["other"] += tothercount
# 							
# 			if "c" in globaldict[chr][bin]:
# 				 csmallcount = getCountSmall(globaldict[chr][bin]["c"])
# 				 cothercount = getCountEdge(globaldict[chr][bin]["c"])
# 				 if chr in genes:
# 					for j, gene in enumerate(genes[chr]):
# 						if pos > gene["start"]-padby and pos < gene["end"]+padby:
# 							genes[chr][j]["small"] -= csmallcount
# 							genes[chr][j]["other"] -= cothercount
# 			
# 			smallscore = str(tsmallcount - csmallcount)
# 			edgescore = str(tsmallcount - csmallcount)
# 			binedout.write("\t".join([chr,str(pos),smallscore,edgescore])+"\n")
# 			
# 	
# 	binedout.close()
# 	
# 	genelistoutf=outfn+".pergene.tsv"
# 	genelistout = open(genelistoutf,"w")
# 	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(types)+"\n")
# 	for chr in genes:
# 		for gene in genes[chr]:
# 			vals = "\t".join([ str(gene[type]) for type in types ])
# 			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
# 	genelistout.close()
	
def scoreBreakDancer(outfn,infn,genelistfn,coveredregions,minscore=0):
	global includeAllGenes
	input = open(infn,"r")
	inputcols = ["Chr1","Pos1","Orientation1","Chr2","Pos2","Orientation2","Type","Size","Score","num_Reads","num_Reads_lib","Allele_frequency","Version","Run_Param"]
	
	typei = inputcols.index("Type")
	chr1i = inputcols.index("Chr1")
	chr2i = inputcols.index("Chr2")
	pos2i = inputcols.index("Pos2")
	pos1i = inputcols.index("Pos1")
	scorei = inputcols.index("Score")
	sizei = inputcols.index("Size")
	valuei = inputcols.index("num_Reads")
	
	types = ["ITX","CTX"]
	
	genes=genelist.loadGenes(genelistfn,types)
	
	for chr in genes:
		filtered = []
		if chr in coveredregions:	
			for gene in genes[chr]:
				covered = includeAllGenes
				if includeAllGenes == False:				
					for tile in xrange(makeCalls.getTile(int(gene["start"])-int(padby)),makeCalls.getTile(int(gene["end"])+int(padby))):
						if tile in coveredregions[chr] and coveredregions[chr][tile] == True:
							covered = True
							break
				if covered == True:
					filtered.append(gene)
		genes[chr] = filtered
	
	
	
	
	
	
	for i, line in enumerate(input):
		if line.find("#")>-1:
			line = line.split("#")[0]
			if line == '':
				continue
		values = line.split()
		if(len(values)>7):
			if values[typei] in types and int(values[scorei])>=minscore:
				#add both lines
				chr1 = addChr(values[chr1i])
				chr2 = addChr(values[chr2i])
				
				
				for pos in [{"c":chr1,"p":int(values[pos1i])}, {"c":chr2,"p":int(values[pos2i])}]:
					p = pos["p"]
					c = pos["c"]
					tile=makeCalls.getTile(p)
					if tile in coveredregions[c] and coveredregions[c][tile] == True and c in genes:
						for j, gene in enumerate(genes[c]):
							if p > int(gene["start"])-int(padby) and p < int(gene["end"])+int(padby):
								genes[c][j][values [typei]] +=1
	
	input.close()
	genelistoutf=outfn+".t.per.gene"
	genelistout = open(genelistoutf,"w")
	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(types)+"\n")
	for chr in genes:
		for gene in genes[chr]:
			vals = "\t".join([ str(gene[type]) for type in types ])
			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
	genelistout.close()

def scoreCallsNoSubtract(outfn,oneFN,genelistfn,coveredregions,scoreCutoff):
	global includeAllGenes
	global globaldict
	globaldict = {}
	loadCalledFile(	oneFN,"t" )
	#loadCalledFile( controlFN,"c" )
	
	types = ["small","other"]
	
	genes=genelist.loadGenes(genelistfn,types)
	
	#TODO: do this once for all
	for chr in genes:
		filtered = []
		if chr in coveredregions:	
			for gene in genes[chr]:
				covered = includeAllGenes
				if includeAllGenes == False:				
					for tile in xrange(makeCalls.getTile(int(gene["start"])-int(padby)),makeCalls.getTile(int(gene["end"])+int(padby))):
						if tile in coveredregions[chr] and coveredregions[chr][tile] == True:
							covered = True
							break
				if covered == True:
					filtered.append(gene)
		genes[chr] = filtered
	
	binedout = open(outfn+".bined.tsv","w")
	binedout.write("chrom\tpos\tsmall\tother\n")
	
	
	for chr in globaldict:
		#print "chr is " + chr
		for pos in globaldict[chr]:
			#print "bin is " + bin
			
			bin = makeCalls.getTile(int(pos))
			if bin in coveredregions[chr] and coveredregions[chr][bin] == True:					
				
				tsmallcount = 0 
				
				tothercount = 0 
				
				
				if "t" in globaldict[chr][pos]:
					 
					 tsmallcount = getCountSmall(globaldict[chr][pos]["t"],scoreCutoff)
					 #print "small count is %i"%( tsmallcount)
					 tothercount = getCountEdge(globaldict[chr][pos]["t"],scoreCutoff)
					 if chr in genes:
						for j, gene in enumerate(genes[chr]):
							if int(pos) > (int(gene["start"])-int(padby)) and int(pos) < (int(gene["end"])+int(padby)):
								#print "%i found in gene "%(tsmallcount) + gene["name"]
								genes[chr][j]["small"] += tsmallcount
								genes[chr][j]["other"] += tothercount
								
				
				
				smallscore = str(tsmallcount)
				edgescore = str(tothercount)
				binedout.write("\t".join([chr,str(pos),smallscore,edgescore])+"\n")
			
	
	binedout.close()
	
	genelistoutf=outfn+".minScore."+str(scoreCutoff)+".pergene.tsv"
	genelistout = open(genelistoutf,"w")
	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(types)+"\n")
	for chr in genes:
		for gene in genes[chr]:
			vals = "\t".join([ str(gene[type]) for type in types ])
			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
	genelistout.close()

def getFileName(filenbase,type):

	filepatern = filenbase+"-"+type+"*called"
	print "lookinf for files matching " + filepatern
	return glob.glob(filepatern)[0]			
			
if __name__ == "__main__":
	# patients = {}
# 	for infile in glob.glob(os.path.join(os.getcwd(),'TCGA*')):
# 		patients[os.path.basename(infile)[0:12]] = 1
# 	
# 	for patient in patients.keys():
# 		tfilen = getFileName("./"+patient,"01")
# 		cfilen = getFileName("./"+patient,"10")
# 		scoreCalls(patient+".breakscores",tfilen,cfilen,sys.argv[1])
	
	wigfiles = glob.glob("./*.tile.wig")
	coveredregions  = {}
	firstpass = True
	

	print "Finding Covered Regions"
	for wigfn in wigfiles:		
		print "Loading " + wigfn
		wig =  makeCalls.loadWigHash(wigfn)
		fitleredcount = 0
		passedCount = 0
		for chr in wig:
			chrNorm = addChr(chr)
			if not chrNorm in coveredregions:
				coveredregions[chrNorm] = {}
			for tile in wig[chr]:
				if int(wig[chr][tile]) >= int(coveragecutoff):
					passedCount +=1
					if firstpass == True:
						coveredregions[chrNorm][tile] = True
									
				else:
					coveredregions[chrNorm][tile] = False
					fitleredcount += 1
		print "Found %i tiles covered over cutoff and %i tiles covered but below cutoff"%(passedCount,fitleredcount)
					
		firstpass = False
# 	for infile in glob.glob(os.path.join(os.getcwd(),'TCGA*.breakdancer.out')):
# 		print "Processing " + infile
# 		scoreBreakDancer(infile,infile,sys.argv[1],coveredregions)
		
	for scoreCutoff in [0,25,50,75,90,94,96,98,99]:
		for infile in glob.glob(os.path.join(os.getcwd(),'TCGA*called')):
			print "Processing " + infile
			scoreCallsNoSubtract(infile,infile,sys.argv[1],coveredregions,scoreCutoff)
		
				
			
	
	
	
	
	
import os, glob, errno, sys
import makeCalls, genelist
resolution = 1000
padby = 1000
includeAllGenes = True

def score(genelistfn):
	wigfiles = glob.glob("./*.tile.wig")
	coveredregions  = {}
	firstpass = True
	
	print "Loading " + genelistfn
	genes=genelist.loadGenes(genelistfn,wigfiles)
	
	for wigfn in wigfiles:		
		print "Loading " + wigfn
		wig =  makeCalls.loadWigHash(wigfn)
		
		print "Bining by gene"
		for chr in genes:
			for j, gene in enumerate(genes[chr]):
				for tile in xrange(makeCalls.getTile(int(gene["start"])-int(padby)),makeCalls.getTile(int(gene["end"])+int(padby))):
					if not chr in wig:
						chr = chr.replace("chr","")
					if chr in wig and tile in wig[chr]:
						if includeAllGenes == False:
							if int(wig[chr][tile])>10:
								genes[chr][j][wigfn] = 1
						else:
							if int(wig[chr][tile])>0:
								if not wigfn in genes[chr][j]:
									genes[chr][j][wigfn] = 0
								genes[chr][j][wigfn]+=int(wig[chr][tile])
		
								
	
	
	genelistoutf="coverage.per.gene.per.sample.tsv"
	print "Writing " + genelistoutf
	genelistout = open(genelistoutf,"w")
	genelistout.write("gene_symbol\tchr\tstart\tend\t"+"\t".join(wigfiles)+"\n")
	for chr in genes:
		for gene in genes[chr]:
			vals = "\t".join([ str(gene[type]) for type in wigfiles ])
			genelistout.write("\t".join([gene["name"],chr,str(gene["start"]),str(gene["end"]),vals])+"\n")
	genelistout.close()
	


if __name__ == "__main__":
	score(sys.argv[1])
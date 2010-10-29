def loadGenes(filen,types):
	genes={}
	genelist = open (filen,"r")
	for gene in genelist:
		vs = gene.rstrip().split("\t")
		if not vs[2] in genes:
			genes[vs[2]]=[]
		vdict = {"name":vs[0],"start":int(vs[4]),"end":int(vs[5]),"or":vs[3]}
		for type in types:
			vdict[type]=0
		genes[vs[2]].append(vdict)
	genelist.close()
	return genes

def loadGenesByName(filen):
	genes={}
	genelist = open (filen,"r")
	for gene in genelist:
		vs = gene.strip().split("\t")
		if not vs[0] in genes:
		    vdict = {"name":vs[0],"chr":vs[2], "start":int(vs[4]),"end":int(vs[5]),"or":vs[3]}
		    genes[vs[0]]=vdict
	genelist.close()
	return genes
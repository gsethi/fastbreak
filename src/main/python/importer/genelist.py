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
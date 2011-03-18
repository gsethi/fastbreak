import os
import glob
import errno

def score():
	files = glob.glob("./*.t.per.gene")
	print "%i files\n"%(len(files))
	cols = ["gene_symbol"]
	fileobjs = []
	for inf in files:
		cols.append(os.path.basename(inf).split(".")[0])
		fileobjs.append(open(inf,"r"))
	
	
	
	itxf = open("itxmatrix.tsv","w")
	ctxf = open("ctxmatrix.tsv","w")
	
	
	itxf.write("\t".join(cols)+"\n")
	ctxf.write("\t".join(cols)+"\n")
	
	loop = True
	while loop==True:
		
		firstpass=True
		itxvs = []
		ctxvs = []
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
					itxvs.append(linevs[0])
					ctxvs.append(linevs[0])
					firstpass = False
				itxvs.append(linevs[4])
				ctxvs.append(linevs[5])

				
		if loop==True and len(linevs) > 1:
			itxf.write("\t".join(itxvs)+"\n")
			ctxf.write("\t".join(ctxvs)+"\n")
			
	for file in fileobjs:
		file.close()
	
	itxf.close()
	ctxf.close()


if __name__ == "__main__":
	score()
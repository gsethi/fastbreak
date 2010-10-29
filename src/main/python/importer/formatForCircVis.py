__author__ = 'rbressle'
import genelist
import sys


def formatMatrix(matrixfilen, gl):
    fo = open(matrixfilen,"r")
    fout = open(matrixfilen+".for.circvis.txt","w")
    fout.write("chr1\tstart1\tend1\toptions1\tchr2\tstart2\tend2\toptions2\tlinkValue\n")
    columns = fo.next().lstrip().rstrip().replace('"','').split()
    for line in fo:
    	vals = line.rstrip().replace('"','').split()
    	gene = vals[0]
    	for i,val in enumerate(vals[1:]):
    		if columns[i]!=gene and val != "NA" and float(val)<1.0:
				go1 = gl[gene]
				go2 = gl[columns[i]]
				fout.write("\t".join(["%s"%(i) for i in [go1["chr"],go1["start"],go1["end"],"label="+go1["name"],go2["chr"],go2["start"],go2["end"],"label="+go2["name"],val]])+"\n")
    fout.close()
    fo.close()
    			

def formatList(listfilen,gl):
	fo = open(listfilen,"r")
	fout = open(listfilen+".for.circvis.txt","w")
	fout.write("chr\tstart\tend\tvalue\toptions\n")
	columns = fo.next()
	for line in fo:
		vals = line.rstrip().replace('"','').split()
		gene = vals[0]
		go1=gl[gene]
		fout.write("\t".join(["%s"%(i) for i in [go1["chr"],go1["start"],go1["end"],vals[1],"label="+go1["name"]]])+"\n")
	fout.close()
	fo.close()



if __name__ == "__main__":

    gl = genelist.loadGenesByName(sys.argv[1])
    formatMatrix("Fastbreak_tumor_cutoff_3_by_gene_MIdist.txt",gl)
    formatList("Fastbreak_tumor_cutoff_3_by_gene_Counts.txt",gl)
    
    

  
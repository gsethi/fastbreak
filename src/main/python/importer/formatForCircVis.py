__author__ = 'rbressle'
import genelist
import sys


def formatMatrix(matrixfilen, gl):
    fo = open(mstrixfilen,"r")
    fout = open(mstrixfilen+".for.circvis.txt","w")
    fout.write("chr1\tstart1\tend1\toptions1\tchr2\tstart2\tend2\toptions2\tlinkValue\n")
    columns = fo.next().lstrip().rstrip().replace('"','').split("\t")
    for line in fo:
    	vals = line.rstrip().replace('"','').split("\t")
    	gene = vals[0]
    	for i,val in enumerate(vals[1:]):
    		if columns[i]!=gene and float(val)<1.0:
				go1 = gl[gene]
				go2 = gl[columns[i]]
				fout.write("\t".join([go1["chr"],go1["start"],go1["end"],"label="+go1["name"],go2["chr"],go2["start"],go2["end"],"label="+go2["name"],val])+"\n")
    fout.close()
    fo.close()
    			

def formatList(listfilen,gl):
    fo = open(listfilen,"r")
    fout = open(mstrixfilen+".for.circvis.txt","w")



if __name__ == "__main__":

    gl = genelist.loadGenesByName(sys.argv[1])
    formatMatrix("Fastbreak_tumor_cutoff_3_by_gene_MIdist.txt",gl) 
    
    

  
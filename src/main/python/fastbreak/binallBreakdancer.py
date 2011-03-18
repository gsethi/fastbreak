import glob
from fastbreak import binBreakdancer

for filename in glob.glob("*.bam.breakdancer.out"):
	distancefnglob = "./"+filename[0:28]+"*.tile.wig"
	fns = glob.glob(distancefnglob)
	if len(fns)>0:
		distancefn = fns[0]
		#distancefn = distancefn.replace(".tile.wig","oddreads.list")
		
		binBreakdancer.makeCalls(open(filename,"r"),open(filename+".binned","w"),distancefn)
	else:
		print("No match found for "+distancefnglob)
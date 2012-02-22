"""Alternative fastbreak pass one for complete genomics data.

Takes a cg map file:

flags, chromosome, offseINChr(zero based), gap1, gap2, gap3, weight, mateRec
"""
__author__ = 'RyanBressler'

import sys
import glob

#bitise flag checking
#1== 1<<0 == 001, 2 == 1<<1 == 010, 4 == 1 << 2 == 100
def isLast(flag):
	return int(flag)&1

def isRight(flag):
	return int(flag)&2>0

def getStrand(flag):
	return int(flag)&4>0


def ParseScore(score):
	return 100-ord(score)


def WriteOddRead(fo,lvs,matelvs):
	strands=["+","-"]
	fo.write('\t'.join([lvs[1],lvs[2],matelvs[1],matelvs[2],str(1-ord(lvs[-2])*ord(matelvs[-2])/10000.0),str(abs(int(lvs[2])-int(matelvs[2]))),strands[getStrand(lvs[0])],strands[getStrand(matelvs[0])],"\n"]))

def WritePair(outfiles,lvs,matelvs):
	#same chrm
	if lvs[1]==matelvs[1]:
		d = abs(int(lvs[2])-int(matelvs[2]))
		sc = ord(lvs[-2])*ord(matelvs[-2])/10000
		orstring = "%i%i"%(getStrand(lvs[0]),getStrand(matelvs[0]))
		outfiles["distanceAll"].write("%i,"%(d))
		outfiles["distance"+orstring].write("%i,"%(d))
		outfiles["distanceAllMapQ"].write("%i,"%(sc))
		outfiles["distance"+orstring+"MapQ"].write("%i,"%(sc))
		if d > 1000:
			WriteOddRead(outfiles["oddreadlist"],lvs,matelvs)
	else:
		WriteOddRead(outfiles["oddreadlist"],lvs,matelvs)

def main():
	fn = sys.argv[1]
	

	independentoutfiles={
	"distanceAll":open(fn+"ind_distanceAll","w"),
	"distance00":open(fn+"ind_distance00","w"),
	"distance01":open(fn+"ind_distance01","w"),
	"distance10":open(fn+"ind_distance10","w"),
	"distance11":open(fn+"ind_distance11","w"),
	"distanceAllMapQ":open(fn+"ind_distanceAllMapQ","w"),
	"distance00MapQ":open(fn+"ind_distance00MapQ","w"),
	"distance01MapQ":open(fn+"ind_distance01MapQ","w"),
	"distance10MapQ":open(fn+"ind_distance10MapQ","w"),
	"distance11MapQ":open(fn+"ind_distance11MapQ","w"),
	"oddreadlist":open(fn+"ind.oddreads.list", 'w')		
	}
	independentoutfiles["oddreadlist"].write('\t'.join(["FromChr","FromPos","ToChr","ToPos","MapQ","Distance","StrandQ","StrandM","QName\n"]))

	bestpairoutfiles={
	"distanceAll":open(fn+"_distanceAll","w"),
	"distance00":open(fn+"_distance00","w"),
	"distance01":open(fn+"_distance01","w"),
	"distance10":open(fn+"_distance10","w"),
	"distance11":open(fn+"_distance11","w"),
	"distanceAllMapQ":open(fn+"_distanceAllMapQ","w"),
	"distance00MapQ":open(fn+"_distance00MapQ","w"),
	"distance01MapQ":open(fn+"_distance01MapQ","w"),
	"distance10MapQ":open(fn+"_distance10MapQ","w"),
	"distance11MapQ":open(fn+"_distance11MapQ","w"),
	"oddreadlist":open(fn+"oddreads.list", 'w')		
	}

	bestpairoutfiles["oddreadlist"].write('\t'.join(["FromChr","FromPos","ToChr","ToPos","MapQ","Distance","StrandQ","StrandM","QName\n"]))
		
	for filen in glob.glob(fn+"*.tsv"):
		print "Reading %s.0\n"%(filen)
		fo = open(filen)
		lines = []
		bestleftscore = 100
		bestleft = -1
		bestrightscore = 100
		bestright = -1


		for line in fo:
			if line[0]=="#" or line[0]==">":
				continue
			vs = line.rstrip().split()
			if len(vs) < 8:
				continue
			
			if (not isRight(vs[0])) and ord(vs[-2])<bestleftscore:
				bestleft = len(lines)
			if isRight(vs[0]) and ord(vs[-2])< bestrightscore:
				bestright = len(lines)	
			lines.append(vs)
			
			if isLast(vs[0]):
				if bestleft != -1 and bestright != -1:
					WritePair(independentoutfiles,lines[bestleft],lines[bestright])
				#output
				for i,lvs in enumerate(lines):
					matei=lvs[-1]
					matelvs = lines[int(matei)]
					WritePair(bestpairoutfiles,lvs,matelvs)
					
					

				bestleftscore = 100
				bestleft = -1
				bestrightscore = 100
				bestright = -1		
				lines=[]
		fo.close()

	for i in independentoutfiles:
		independentoutfiles[i].close()
	for i in bestpairoutfiles:
		bestpairoutfiles[i].close()


			


if __name__ == '__main__':
	main()

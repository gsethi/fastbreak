"""Alternative fastbreak pass one for complete genomics data.

Takes a cg map file:

flags, chromosome, offseINChr(zero based), gap1, gap2, gap3, weight, mateRec
"""
__author__ = 'RyanBressler'

#bitise flag checking
#1== 1<<0 == 001, 2 == 1<<1 == 010, 4 == 1 << 2 == 100
def isLast(flag):
	return flag&1

def isRight(flag):
	return flag&2>0

def getStrand(flag):
	return flag&4>0


def ParseScore(score):
	return 100-ord(score)


def WriteOddRead(fo,lvs,matelvs):
	strands=["+","-"]
	fo.write('\t'.join([lvs[1],lvs[2],matelvs[1],matelvs[2],str(1-ord(lvs[-2])*ord(matelvs[-2])/10000.0),str(abs(lvs[2]-matelvs[2])),strands[getStrand(lvs[0])],strands[getStrand(lvs[1])],""))

def main():
	fn = sys.argv(1)
	fo = open(fn)

	outfiles={
	"distanceAll":open(fn+"_distanceAll","w")
	"distance00":open(fn+"_distance00","w")
	"distance01":open(fn+"_distance01","w")
	"distance10":open(fn+"_distance10","w")
	"distance10":open(fn+"_distance10","w")
	"distanceAllMapQ":open(fn+"_distanceAllMapQ","w")
	"distance00MapQ":open(fn+"_distance00MapQ","w")
	"distance01MapQ":open(fn+"_distance01MapQ","w")
	"distance10MapQ":open(fn+"_distance10MapQ","w")
	"distance10MapQ":open(fn+"_distance10MapQ","w")
	"oddreadlist":open(fn+"oddreads.list", 'w')		
	}

	outfiles["oddreadlist"].write('\t'.join(["FromChr","FromPos","ToChr","ToPos","MapQ","Distance","StrandQ","StrandM","QName\n"]))
		
	
	lines = []

	for line in fo:
		vs = line.rstrip().split()
		flags = ParseFlag(vs[0])
		
		lines.append(vs)
		
		if isLast(vs[0]):
			#output
			for i,lvs in enumerate(lines):
				matei=lvs[-1]
				if i == matei:
					matelvs = lines[matei]
					#same chrm
					if lvs[1]==matelvs[1]:
						d = abs(lvs[2]-matelvs[2])
						sc = ord(lvs[-2])*ord(matelvs[-2])/10000.0
						orstring = "%i%i"%(getStrand(vs[0]),getStrand(matelvs[0]))
						outfiles["distanceAll"].write(d)
						outfiles["distance"+orstring+"MapQ"].write(d)
						outfiles["distanceAll"].write(d)
						outfiles["distance"+orstring+"MapQ"].write(d)
						if orstring == "01" or d > 1000:
							WriteOddRead(outfiles["oddreadlist"],lvs,matelvs)
					else:
						WriteOddRead(outfiles["oddreadlist"],lvs,matelvs)
					

					
			lines=[]
	for i in outfiles:
		i.close()


			


if __name__ == '__main__':
	main()

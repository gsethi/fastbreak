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


def main():
	fn = sys.argv(1)
	fo = open(fn)

	outfiles={
	"distanceAll"=open(fn+"_distanceAll","w")
	"distance00"=open(fn+"_distance00","w")
	"distance01"=open(fn+"_distance01","w")
	"distance10"=open(fn+"_distance10","w")
	"distance10"=open(fn+"_distance10","w")
	}
	
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
						orstring = "%i%i"%(getStrand(vs[0]),getStrand(matelvs[0]))
						outfiles["distanceAll"].write(d)
						outfiles["distance"+orstring].write(d)
			lines=[]
	for i in outfiles:
		i.close()


			


if __name__ == '__main__':
	main()

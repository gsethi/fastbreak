def splitLine(line):
	return line.rstrip("\n").split("\t")
	
def parseLine(line,headerarg=False):
	global headers
	h = []
	if not headerarg:
		h = headers
	else:
		h	= headerarg
	rv = {}
	for i,v in enumerate(splitLine(line)):
		rv[h[i]]=v
	return rv
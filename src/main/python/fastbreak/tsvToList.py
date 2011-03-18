def tsvToList(tsvfile,fields):
	returnA = []
	for line in tsvfile:
		if line.startswith("#"):
			continue
		values = line.rstrip().split("\t")
		rowdict = {}
		for i, name in enumerate(fields):
			if i < len(values):
				rowdict[name]=values[i]
			else:
				rowdict[name] = " "
		returnA.append(rowdict)
	return returnA
def parseEqList(ins):
	retDic = {}
	for term in ins.rstrip().split():
		term = term.split("=")
		if len(term)==2:
			retDic[term[0]]=term[1]
	return retDic

def wigToTsv(wig,sample,outf):
	vStep = True
	chr = ""
	start = 1
	span = 1
	step = 0
	#outf = open(outfn,"w")
	for line in wig:
		
		if line.startswith("track"):
			continue
		if line.startswith("variableStep"):
			vStep = True
			params = parseEqList(line)
			chr = params["chrom"]			
			span = params["span"] or 1
			continue
		if line.startswith("fixedStep"):
			vStep = False
			params = parseEqList(line)
			chr = params["chrom"]			
			span = params["span"] or 1
			start = int(params["start"])
			step = params["step"]
			continue
		value = 0
		if vStep == True:
			values = line.rstrip().split()
			start = values[0]
			value = values[1]
		else:
			value = line.rstrip()
		
		outf.write("\t".join([sample,chr,start,span,value+"\n"]))
			
		if vStep == False:
			start = int(start)+int(step)
	#outf.close()
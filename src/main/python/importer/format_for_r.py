pf = open("patients.txt","r")

ps = pf.read()

pf.close()

pfs = ps.replace("./","").replace(".tile.wig","").replace("-",".").split("\t")

pf = open("patientNames.txt","w")
plf  = open("patientList.txt","w")
bcbypatient ={}

for filen in pfs:	
	pf.write("%s\t%s\n"%(filen,filen[0:28]))
	patienbc=filen[0:28]
	bcbypatient[patienbc[0:15]]=patienbc
	plf.write(patienbc+"\n")

pf.close()
plf.close()

gif = open("genes.txt","r")
gof = open("geneList.txt","w")

gof.write(gif.read().replace("\t","\n"))

gof.close()

dataf = open("fastbreak.per.gene.score.matrix.tsv","r")
datalines=[]
for line in dataf:
	datalines.append(line)
dataf.close()

header=datalines[0]

newheadermembers = []

for colhead in header.rstrip().split("\t"):
	if colhead[0:4] == "TCGA":
		colhead=colhead[0:28]
	newheadermembers.append(colhead)
	
datalines[0]="\t".join(newheadermembers)+"\n"
dataf = open("fastbreak.per.gene.score.matrix.tsv","w")
for line in datalines:
	dataf.write(line)
dataf.close()

dataf = open("coverage.per.gene.per.sample.tsv","r")
datalines=[]
for line in dataf:
	line=line.split("\t")
	line.pop(1)
	line.pop(2)
	line="\t".join(line)
	datalines.append(line)
dataf.close()

header=datalines[0]

newheadermembers = []

for colhead in header.rstrip().split("\t"):
	if colhead.find("TCGA")!=-1:
		colhead = colhead.lstrip().lstrip("./").replace("-",".")
		colhead=colhead[0:28]
	newheadermembers.append(colhead)
	
datalines[0]="\t".join(newheadermembers)+"\n"
dataf = open("coverage.per.gene.per.sample.tsv","w")
for line in datalines:
	dataf.write(line)
dataf.close()

patientStatus={}
patientResistance = {}

dataf = open("tcga_Clinical_HighGrade_ExcludedSamples.txt","r")

dataf.next()

for line in dataf:
	vals = line.replace("-",".").replace(" ",".").rstrip().split("\t")
	print vals[0]
	patientResistance[vals[0]]=vals[24]
	patientStatus[vals[0]]=vals[1]


dataf.close()



dataf = open("ClassVars_prenercols.txt","r")

linesbysample = {}

headers = []


for line in dataf:
	if line.startswith("Name"):		
		headers = line.rstrip().split("\t")
	elif line.startswith("TCGA"):
		patient=line.split("\t")[0]
		
		linesbysample[line.split("\t")[0]]=line
		
samples = linesbysample.keys()
for sample in samples:
	tissue = sample[13:15]
	oposite = sample[0:13]+sample[14:15]+sample[13:14]
	if oposite in bcbypatient and not oposite in linesbysample:
		oldline = linesbysample[sample].rstrip().split("\t")
		#decode the oposite tissue
		tissueopositesymbol = "ERROR"
		if tissue == "01":
			tissueopositesymbol ="BLOOD"	
		elif tissue =="10":
			tissueopositesymbol ="CANCER"
		
		line = "\t".join([bcbypatient[oposite],tissueopositesymbol,oldline[2]])+"\n"
		linesbysample[bcbypatient[oposite]]=line
dataf.close()

headers.append("STATUS")
headers.append("RESISTANCE")
#print headers

dataf = open("ClassVarsOld.txt","w")
dataf.write("\t".join(headers)+"\n")
sortedkeys = linesbysample.keys()
sortedkeys.sort()
for sample in sortedkeys:
	vals=linesbysample[sample].rstrip().split("\t")
	if sample[0:12] in patientStatus:
		patient=sample[0:12]
		print "patient %s"%(patient)
		vals.append(patientStatus[patient])
		vals.append(patientResistance[patient])
	else:
		vals.append("NA")
		vals.append("NA")
	dataf.write("\t".join(vals)+"\n")
dataf.close()
	

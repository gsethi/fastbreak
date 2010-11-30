foin = open("ClassVarsOld.txt","r")
foin.next()

patients = {}
for line in foin:
	line = line.rstrip().replace(".","-").split("\t")
	patient = line[0][0:12]
	
	
	patients[patient]={"line":"\t".join([patient,line[2],"Status: "+line[3]+" Resistance: "+line[4]])+"\n"}
	patients[patient][line[1]] = line
	
samplefo = open("samples.tsv","w")
patientfo = open("patients.tsv","w")

for patient in patients.keys():
	if "CANCER" in patients[patient] and "BLOOD" in patients[patient]:
		print patient
		patientfo.write(patients[patient]["line"])
		
		ts = patients[patient]["CANCER"]
		bl = patients[patient]["BLOOD"]
		samplefo.write("\t".join([ts[0],patient,"Tumor",bl[0],glob.glob(ts+"*.listcalled")[0],glob.glob(ts+"*.tile.wig")[0]]))
		samplefo.write("\t".join([bl[0],patient,"Blood",ts[0],glob.glob(bl+"*.listcalled")[0],glob.glob(bl+"*.tile.wig")[0]]))
		
		
		
samplefo.close()
patientfo.close()
	
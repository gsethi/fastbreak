import glob

foin = open("ClassVarsOld.txt","r")
foin.next()

patients = {}
for line in foin:
	line = line.rstrip().replace(".","-").split("\t")
	patient = line[0][0:12]
	
	if not patient in patients:
		patients[patient]={"line":"\t".join([patient,line[2],"Status: "+line[3]+" Resistance: "+line[4]])+"\n"}
	#print line[1]
	patients[patient][line[1]] = line

foin.close()	
samplefo = open("samples.tsv","w")
patientfo = open("patients.tsv","w")

for patient in patients.keys():
	#print patient
	#print "\t".join(patients[patient].keys())
	if "CANCER" in patients[patient].keys() and "BLOOD" in patients[patient].keys():
		
		patientfo.write(patients[patient]["line"])
		
		ts = patients[patient]["CANCER"]
		bl = patients[patient]["BLOOD"]
		samplefo.write("\t".join([ts[0], patient, "Tumor", bl[0], glob.glob(ts[0]+"*.listcalled")[0], glob.glob(ts[0]+"*.tile.wig")[0]])+"\n")
		samplefo.write("\t".join([bl[0], patient,"Blood",ts[0], glob.glob(bl[0]+"*.listcalled")[0], glob.glob(bl[0]+"*.tile.wig")[0]]) +"\n")
		
		
		
samplefo.close()
patientfo.close()
	
import os, glob, shutil, errno


	
	
def makeDataDir(extension,targetdir):
	try:
		os.makedirs(targetdir)
	except OSError, exc: # Python 2.5 was "except OSError as exc"
		if exc.errno == errno.EEXIST:
			pass
		else: raise
		
	patients = {}
	for infile in glob.glob(os.path.join(os.getcwd(),'*'+extension)):
		patients[os.path.basename(infile)[0:12]] = os.path.basename(infile)
	
	patientfo = open(targetdir+"/patients.tsv","w")
	samplefo = open(targetdir+"/samples.tsv","w")
	
	for patient in patients.keys():
		print "Procesing patient "+patient
		comment = " "
		bc = patients[patient].lower()
		type = "Unknown"
		if not bc.find("good") == -1:
			type = "Good"
		elif not bc.find("medium") == -1:
			type = "Medium"
		elif not bc.find("poor") == -1:
			type = "Poor"
		patientfo.write("%s\t%s\t%s\n"%(patient,type,comment))
		
		tumorbf=os.path.basename(glob.glob(os.path.join(os.getcwd(),patient+'-01*'+extension))[0])
		shutil.copy(tumorbf,targetdir)
		print "Copying file "+tumorbf
		tumorbc =tumorbf[0:28]
		
		normalbf=os.path.basename(glob.glob(os.path.join(os.getcwd(),patient+'-10*'+extension))[0])
		shutil.copy(normalbf,targetdir)
		print "Copying file "+normalbf
		normalbc = normalbf[0:28]
		
		tumorwig=os.path.basename(glob.glob(os.path.join(os.getcwd(),patient+'-01*.tile.wig'))[0])
		shutil.copy(tumorwig,targetdir)
		print "Copying file "+tumorwig
		
		normalwig=os.path.basename(glob.glob(os.path.join(os.getcwd(),patient+'-10*.tile.wig'))[0])
		shutil.copy(normalwig,targetdir)
		print "Copying file "+normalwig
		
		#tumor file
		samplefo.write("\t".join([tumorbc,patient,"Tumor",normalbc," ",tumorbf,tumorwig])+"\n")
		samplefo.write("\t".join([normalbc,patient,"Normal",tumorbc," ",normalbf,normalwig])+"\n")
		
			
	patientfo.close()
	samplefo.close()
	


if __name__ == "__main__":
	makeDataDir(".listcalled","fastbreak_data_upload")
	makeDataDir(".breakdancer.out","breakdancer_data_upload")
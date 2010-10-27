# Usage
# Zipfile:
# python importZip.py Archive.zip genelist.txt /work/space/dir /pickle/path/root
# Directory:
# python importZip.py /in/dir genelist.txt /work/space/dir /pickle/path/root
# Note : pickle files will be created in /pickle/path/root/work/space/dir
import urlparse
import zipfile
import pickleBreakDancerOut
import wigToTsv
import tsvToList
import sys
import os
try: import json #python 2.6 included simplejson as json
except ImportError: import simplejson as json
		
#config section. Should be moved to sperate file if it grows much



#this method is called as the main method when run as a scrip
def importZip(zipfilen,genelistfile,picklepath,ws):

	openAbstraction = lambda x : x
	if zipfilen.find(".zip") == -1:
		openAbstraction = lambda fn : open(os.path.join(zipfilen,fn),"r")
		
	else:
		zfile = zipfile.ZipFile(zipfilen, "r")
		openAbstraction = lambda fn : zfile.open(fn)
		
		
	patientFs=["id","classification","comments"]
	sampleFs=["sample_id","patient_id","classification","mate","comments","break_file","track_file"]
	
	#parse the manifests
	patientL = tsvToList.tsvToList(openAbstraction("patients.tsv"),patientFs)
	#patientjson = open("patients.json","w")
	#patientjson.write(json.dumps(patientL))
	#patientjson.close()
	
	sampleL = tsvToList.tsvToList(openAbstraction("samples.tsv"),sampleFs)
	#samplejson = open("samples.json","w")
	#samplejson.write(json.dumps(sampleL))
	#samplejson.close()
	
	
	samplesbypatient = {}
	
	for patient in patientL:
		samplesbypatient[patient["id"]]=[]	
	#trackf = "track.tsv"
	outf = open("track.tsv","w")
	outf.write("sample_id\tchr\tstart\tspan\tvalue\n")
	for sample in sampleL:
		
		wfilen = sample["track_file"]
		wfile = openAbstraction(wfilen)
		#convert to the database table format used by hector
		wigToTsv.wigToTsv(wfile,sample["sample_id"],outf) 
		wfile.close()
		
		#TODO: .breaks vs breakdancer out
		bfilen = sample["break_file"]
		bfile = openAbstraction(bfilen)
		#pickle the data
		pickleBreakDancerOut.doPickle(bfile,bfilen,genelistfile,picklepath)
		bfile.close()
		
		samplesbypatient[sample["patient_id"]].append(sample)
	outf.close()
		
		
	

	
	#calculate score using the files writtent out by the pickler
	#this may need to be tweaked base on what john wants
	
	
	collist=["gene_id"]
	firstpass=True
	scoref= open("patientgenescores.tsv","w")
	pairs=[]
	loop=True
	bfsById = {}
	jsonIndex = []
	
	#pair files and write json
	for patient in patientL:
		patient["samples"]=[]
		tumor = ""
		normal = ""
		dict={}
		collist.append(patient["id"])
		for sample in samplesbypatient[patient["id"]]:
			patient["samples"].append({"id":sample["sample_id"],"patient_id":sample["patient_id"],"classification":sample["classification"],"mate":sample["mate"],"comments":sample["comments"],"pickleFile":os.path.join(ws,sample["break_file"].lstrip("/")+".pickle")})
			bfsById[sample["sample_id"]]=sample["break_file"]
			if sample["classification"] == "Tumor" and sample["mate"] != "":
				dict["tumor"] = sample["sample_id"]
				dict["normal"] = sample["mate"]
		
		jsonIndex.append(patient)
		pairs.append(dict)
	
	patientjson = open("patients.json","w")
	patientjson.write(json.dumps({"patients":jsonIndex}))
	patientjson.close()
		
	#open files
	for pair in pairs:
		pair["tumorfile"] = open(bfsById[pair["tumor"]]+".t.per.gene")
		pair["normalfile"] = open(bfsById[pair["normal"]]+".t.per.gene")
	
	scoref.write("\t".join(collist)+"\n")
	
	while loop==True:
		
		firstpass=True
		scores = []
		for pair in pairs:
			try:
				nline = pair["normalfile"].next()
			except StopIteration:
				loop=False
			try:
				tline = pair["tumorfile"].next()
			except StopIteration:
				loop=False
			if loop == True:
				tv = tline.rstrip().split("\t")
				nv = nline.rstrip().split("\t")
				if tv[0] == "gene_symbol":
					continue
				if firstpass==True:
					scores.append(tv[0])
					firstpass = False
				#this is the score (tumorBREAKS - normalBREAKS) /((geneEND - geneSTART)/10000)
				#10000 was chosen to make the score a reasonable number
				scores.append(	"%g"%(( float(tv[4]) - float(nv[4]))	/	( (float(tv[3]) - float(tv[2]))/10000 )) )
				
		if loop==True:
			scoref.write("\t".join(scores)+"\n")
			
	for pair in pairs:
		pair["tumorfile"].close()
		pair["normalfile"].close()	
	scoref.close()
		
			
#for us as script
if __name__ == "__main__":
        for i,val in enumerate(sys.argv[1:]):
                print "%i : %s"%(i,str(val))
        somepath = os.path.join(sys.argv[4],sys.argv[3].lstrip("/"))
        importZip(sys.argv[1],sys.argv[2],somepath,sys.argv[3])

#usage:
#/tools/bin/python ../../python/getFiles.py searchpath days outfile
#to find all ovarian youngar then 20 days:
#/tools/bin/python ../python_ryans/clinicalParser.py /titan/cancerregulome7/TCGA/repositories/dcc-mirror/ov/bcr/intgen.org/bio/clin 20 ov_clinical_data.tsv

import sys
import subprocess, shlex, shutil
import os, glob
from xml.etree.ElementTree import ElementTree

def findAndParse(searchpath, days,outputfile):
	
	findcommand = "find %s -iname *clinical.TCGA-*.xml -atime -%i"%(searchpath,days)
	print "Atempting to run : "+  findcommand
	
	proc = subprocess.Popen(findcommand, shell=True, stdout=subprocess.PIPE)
	
	
	files = proc.communicate()[0]
	filelist = files.rstrip().lstrip().split("\n")
	print "Parsing %i files."%(len(filelist))
	
	patient_data={}
	patient_data_cols={}
	
	for fn in filelist:
		if fn == "":
			print "fn is \"\""
			continue
		sys.stdout.write(".")
		sys.stdout.flush()
		
		basename= os.path.basename(fn)
		tcgaindex= basename.find("TCGA")
		patient = basename[tcgaindex:tcgaindex+12]
		patient_data[patient]={}
		tree = ElementTree()
		tree.parse(fn)
		
		for el in tree.iter():
			patient_data_cols[el.tag]=True
			patient_data[patient][el.tag]=el.text
	print("\nOutputing Results to "+outputfile )
	
	outf = open(outputfile,"w")
	cols = patient_data_cols.keys()
	cols.insert(0,"patient")
	outf.write("\t".join(cols)+"\n")
	for patient,data in patient_data.items():
		out_data=[patient]
		for col in cols[1:]:
			if col in data:
				out_data.append(data[col])
			else:
				# R standard NA character
				out_data.append("NA")
		outf.write("\t".join([ str(el) for el in out_data ])+"\n")
		
	
			
			
		
		
		
		
	
		
if __name__ == "__main__":
	
	
	searchpath=sys.argv[1]
	days=int(sys.argv[2])
	outputfile=sys.argv[3]
	findAndParse(searchpath,days,outputfile)
	
		
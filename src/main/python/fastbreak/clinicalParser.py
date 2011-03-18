#!/usr/bin/python
#
# 
#     Copyright (C) 2003-2010 Institute for Systems Biology
#                             Seattle, Washington, USA.
# 
#     This library is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 2.1 of the License, or (at your option) any later version.
# 
#     This library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public
#     License along with this library; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
# 

"""
"""

__author__ = "Ryan Bressler"

#usage:
#/tools/bin/python ../../python/getFiles.py searchpath days outfile
#to find all ovarian youngar then 20 days:
#/tools/bin/python ../python_ryans/clinicalParser.py /titan/cancerregulome7/TCGA/repositories/dcc-mirror/ov/bcr/intgen.org/bio/clin 20 ov_clinical_data.tsv

import sys
import subprocess
import shlex
import shutil
import os
import glob
from xml.etree.ElementTree import ElementTree

def findAndParse(searchpath, days,outputfile):
	
	findcommand = "find %s -iname *clinical.TCGA-*.xml -ctime -%i"%(searchpath,days)
	print "Atempting to run : "+  findcommand
	
	proc = subprocess.Popen(findcommand, shell=True, stdout=subprocess.PIPE)
	
	
	files = proc.communicate()[0]
	filelist = files.rstrip().lstrip().split("\n")
	print "Parsing %i files."%(len(filelist))
	
	patient_data={}
	patient_by_file={}
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
		patient_by_file[fn]=patient
		patient_data[fn]={}
		tree = ElementTree()
		tree.parse(fn)
		
		for el in tree.iter():
			patient_data_cols[el.tag]=True
			patient_data[fn][el.tag]=str(el.text).rstrip().lstrip()
	print("\nOutputing Results to "+outputfile )
	
	outf = open(outputfile,"w")
	cols = patient_data_cols.keys()
	cols.insert(0,"patient")
	cols.insert(0,"file")
	outf.write("\t".join(cols)+"\n")
	for file,data in patient_data.items():
		
		out_data=[file,patient_by_file[file]]
		for col in cols[2:]:
			if col in data:
				out_data.append(data[col])
			else:
				# R standard NA character
				out_data.append("NA")
		outf.write("\t".join([ str(el.rstrip().lstrip()) for el in out_data ])+"\n")
		
	
			
			
		
		
		
		
	
		
if __name__ == "__main__":
	
	
	searchpath=sys.argv[1]
	days=int(sys.argv[2])
	outputfile=sys.argv[3]
	findAndParse(searchpath,days,outputfile)
	
		
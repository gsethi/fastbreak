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
#/tools/bin/python ../../python/getFiles.py /titan/cancerregulome1/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1 08.sorted.bam.breakdancer.out /titan/cancerregulome2/synthetic_cancer/trans_out_patient/callednosubtract TCGA-09-0369 TCGA-13-0803 TCGA-13-0891 TCGA-13-0904 TCGA-13-0905 TCGA-13-1492 TCGA-13-1494 TCGA-23-1032 TCGA-24-0970 TCGA-25-1314 TCGA-25-1319 
# OR
#/tools/bin/python ../../python/getFiles.py /titan/cancerregulome1/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1 08.sorted.bam.breakdancer.out /titan/cancerregulome2/synthetic_cancer/trans_out_patient/callednosubtract 
import sys
import subprocess
import shlex
import shutil
import os
import glob

def getForPatient(searchpath,fileNameEnd,todir,patient,notfound):
	
	findcommand = "find "+searchpath+" -name \""+ patient+"*"+fileNameEnd+"\""
	print "Atempting to run : "+  findcommand
	
	proc = subprocess.Popen(findcommand, shell=True, stdout=subprocess.PIPE)
	
	
	files = proc.communicate()[0]
	filelist = files.rstrip().lstrip().split("\n")
	print "Got %i files."%(len(filelist))
	
	for fn in filelist:
		if fn == "":
			notfound.write(patient+"\n")
			print "fn is \"\""
			continue
		print "Copying " + fn + " to "+ todir
		shutil.copy(fn,todir)
	
		
if __name__ == "__main__":
	patients = []
	if len(sys.argv)==4:
		files = glob.glob("./TCGA-*")
		patientdic = {}
		for filen in files:
			patientdic[os.path.basename(filen)[0:12]] = 1

		patients = patientdic.keys()
	
	else:
		patients = sys.argv[4:]
	
	notfound = open("notfount.txt","w")
	for patient in patients:
		getForPatient(sys.argv[1],sys.argv[2],sys.argv[3],patient,notfound)
	notfound.close()
		

		
		
	
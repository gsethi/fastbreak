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

import glob

def getfn(pattern):
	li = glob.glob(pattern)
	rv="NA"
	if len(li)>0:
		rv = li[0]
	else:
		print pattern + " not found"
	
	return rv

def writeSampleLine(samplefo,patient,sample,type,mate):
	listcalled = getfn(sample+"*.listcalled")
	wig = getfn(sample+"*.tile.wig")
	if listcalled != "NA" and wig != "NA":
		samplefo.write("\t".join([sample, patient, type, mate, "", listcalled, wig ])+"\n")
	
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
		
		ts = patients[patient]["CANCER"][0]
		bl = patients[patient]["BLOOD"][0]
		
		writeSampleLine(samplefo,patient,ts,"Tumor", bl)
		writeSampleLine(samplefo,patient,bl,"Blood", ts)
		
		
		
		
		
		
samplefo.close()
patientfo.close()
	
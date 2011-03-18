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

import sys
import os
import glob

import tsvparser
import genelist
import makeCalls

coveragecutoff = 10
padby=1000
includeAllGenes = False

genelistfn = sys.argv[1]

removedpatients = []

wigfiles = glob.glob("./*.tile.wig")
patients = {}
for filen in wigfiles:
	patients[os.path.basename(filen)[0:12]] = 1

patients = patients.keys()
patientn = len(patients)

patientoutf = open("patientsbycoverage.txt","w")

types = ["small","other"]
	
genes=genelist.loadGenes(genelistfn,types)
wigfos = {}

genesperewig = {}

for wigfn in wigfiles:		
# 		if not wigfn.find(patient) == -1:
# 			print wigfn + " matches " + patient
# 			continue
		print "Finding Covered Regions"
		
		coveredregions  = {}

		wig =  makeCalls.loadWigHash(wigfn)
		fitleredcount = 0
		passedCount = 0
		for chr in wig:
			if not chr in coveredregions:
				coveredregions[chr] = {}
			for tile in wig[chr]:
				if int(wig[chr][tile]) >= int(coveragecutoff):
					passedCount +=1
					coveredregions[chr][tile] = True					
				else:
					coveredregions[chr][tile] = False
					fitleredcount += 1
		print "Found %i tiles covered over cutoff and %i tiles covered but below cutoff"%(passedCount,fitleredcount)
		
		genecoverdcount = 0
		genesperewig[wigfn] = {}
		
		for chr in genes:		
			
			if chr in coveredregions:	
				for gene in genes[chr]:
					covered = False
					for tile in xrange(makeCalls.getTile(int(gene["start"])-int(padby)),makeCalls.getTile(int(gene["end"])+int(padby))):
						if tile in coveredregions[chr] and coveredregions[chr][tile] == True:
							covered = True
							genecoverdcount +=1
							break
					
					genesperewig[wigfn][gene["name"]] = covered
		print "%i genes covered"%(genecoverdcount)

for i in xrange(patientn):


	
	
	mingenecount = 0
	minpatients = []
	
	
	
			
			
	print "Pass %i"%(i)
	
	for patient in patients:
		print "Fixing Patient " + patient
		genecount = 0

		
		
		
			
		#TODO: do this once for all
		for chr in genes:
			for gene in genes[chr]:
				covered = True
				
				for wigfn in wigfiles:		
					if not wigfn.find(patient) == -1:
						#print wigfn + " matches " + patient
						continue
					if (not gene["name"] in genesperewig[wigfn] ) or genesperewig[wigfn][gene["name"]] == False:
						covered = False
				if covered == True:
					genecount +=1	
		
		if genecount == mingenecount:
			minpatients.append(patient)
			
		if genecount > mingenecount:
			mingenecount = genecount
			minpatients = [patient]
		print "removing %s results in coverage of %i genes"%(patient,genecount)
	
	print "#Pass %i\n# max of %i genes\n#removed:\n"%(i, mingenecount)
	patientoutf.write("#Pass %i\n# max of %i genes\n#removed:\n"%(i, mingenecount))
	patientoutf.write("\n".join(minpatients)+"\n")
	print "\n".join(minpatients)+"\n"
	patientoutf.flush()
	os.fsync(patientoutf)
	
	for minpatient in minpatients:
		print "Removing " + minpatient
		patients.remove(minpatient)
	if(len(patients)==0):
		break
patientoutf.close()
		
		
		
		

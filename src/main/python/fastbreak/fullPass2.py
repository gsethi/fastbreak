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

#example usage (in the directory with jakes output)
#python fullPass2.py TCGA-25-1328 TCGA-25-1319 TCGA-25-1314

import sys
import os
import glob

import plotL
import makeCalls

do1stplots = False
makecalls = True
do2ndplots = False


def fullPass2(patient,dir):
	global do1stplots,makecalls,do2ndplots
	if do1stplots:
		plotL.plotL(patient,dir)
	if makecalls:
		filenbase = os.path.join(dir,patient)+"*oddreads.list"
		print "Looking for odd read files matching " + filenbase
		for filename in glob.glob(filenbase):
			print "Making calls for file " + filename
			makeCalls.makeCalls(open(filename,"r"),open(filename+"called","w"),filename+"distances")
	if do2ndplots:
		plotL.plotLcalled(patient,dir)
	
	
if __name__ == "__main__":
	patients=[]
	if len(sys.argv)==1:
		wigfiles = glob.glob("./*.tile.wig")
		patientdic = {}
		for filen in wigfiles:
			patientdic[os.path.basename(filen)[0:12]] = 1
			patients = patientdic.keys()
	else:
		patients = sys.argv[1:]
	
	for patient in patients:
		fullPass2(patient,"./")
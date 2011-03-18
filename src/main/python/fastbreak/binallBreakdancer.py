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
import binBreakdancer

def main():
	for filename in glob.glob("*.bam.breakdancer.out"):
		distancefnglob = "./"+filename[0:28]+"*.tile.wig"
		fns = glob.glob(distancefnglob)
		if len(fns)>0:
			distancefn = fns[0]
			#distancefn = distancefn.replace(".tile.wig","oddreads.list")
			
			binBreakdancer.makeCalls(open(filename,"r"),open(filename+".binned","w"),distancefn)
		else:
			print("No match found for "+distancefnglob)
			
if __name__ == "__main__":
	main()
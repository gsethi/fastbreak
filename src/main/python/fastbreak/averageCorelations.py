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

def doAvg(fo):
    valAccum1={"01":0.0,"10":0.0,"11":0.0}
    countAccum1={"01":0,"10":0,"11":0}
    valAccum2={"01":0.0,"10":0.0,"11":0.0}
    countAccum2={"01":0,"10":0,"11":0}

    for line in fo:
        name, val1,val2 = line.rstrip().split("\t")[0:3]
        if val1!="NA":
            countAccum1[name[13:15]]+=1
            valAccum1[name[13:15]]+=float(val1)
        if val2!="NA":
            countAccum2[name[13:15]]+=1
            valAccum2[name[13:15]]+=float(val2)

    for type in valAccum1:
        if countAccum1[type] > 0:
            print "Type %s\t%s avg 1\n"%(type,str(valAccum1[type]/countAccum1[type]))

    for type in valAccum2:
        if countAccum2[type] > 0:
            print "Type %s\t%s avg 2\n"%(type,str(valAccum2[type]/countAccum2[type]))







if __name__ == "__main__":

    print "breakdancerCoverageCorelations.txt"
    fo = open("breakdancerCoverageCorelations.txt")
    doAvg(fo)
    fo.close()

    print "fastbreakCoverageCorelations.txt"
    fo = open("fastbreakCoverageCorelations.txt")
    doAvg(fo)
    fo.close()
  
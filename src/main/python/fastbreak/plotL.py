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

# example usage
# python plotL.py TCGA-13-0897
import sys
import glob
import random
import os
import shlex
import subprocess

filenbase = ""
ageprognosis = ""

def startRDev(rfilen):

	rf = open(rfilen,"w")
	rf.write("""
	pdf(file="%(outf)s",11,8.5)
	"""%{"outf":rfilen.rstrip("R")+"pdf"})
	return rf
	
def doRMainTitle(rf,title):
	title = "Prognosis_age " + ageprognosis + ":" +title
	rf.write("""
	title("%(title)s",outer=TRUE)

	"""%{"title":title})

def doRPar(rf):
	rf.write("""
	par(mfrow=c(2,2),oma=c(0,0,2,0))

	""")
	
def finishAndRun(rf,rfilen):
	rf.write("""
	dev.off()
	""")
	
	rcmd = "R CMD BATCH --no-save --no-restore "+rfilen
	print "Running:\""+ rcmd+"\""
	subprocess.Popen(shlex.split(rcmd))
	print "R running in batch mode; use \"tail -f "+rfilen+"out\" to wath progress."

def doPlot(rf,bloodfn,tumorfn,title):
	#have to be really carefull about memory usage in R so this code runs slow
	rf.write("""
	
	xs = 0:50/5
	
	for(qual in c(60,70,80,90))
	{

		
		td = scan("%(tf)s",sep=",")
		ts = scan("%(tsf)s",sep=",")
		td = td[ts>qual]
		rm(ts)
		td = log10(td [td != 0 ])
		th = hist(td,xs,plot=FALSE)
		rm(td)
		tc = th$counts
		rm(th)
		tc[tc==0]=1
		
		plot(xs[1:50],tc,col="red",type="l",xlab="log(distance)",ylab="Count",log="y")
		
		rm(tc)
		
		bd= scan("%(bf)s",sep=",")
		bs = scan("%(bsf)s",sep=",")
	
		bd = bd[bs>qual]
		rm(bs)
		bd = log10(bd [bd != 0 ])
		
		bh = hist(bd,xs,plot=FALSE)
		rm(bd)
		bc = bh$counts
		rm(bh)
		bc[bc==0]=1
		lines(xs[1:50],bc,col="blue")
		rm(bc)
		
		title(paste("%(title)s Quality>",qual))
	}
	
	"""%{"bf":bloodfn,"bsf":bloodfn+"MapQ","tf":tumorfn,"tsf":tumorfn+"MapQ","title":title})
	
def doPlotCalled(rf,bloodfn,tumorfn,title):
	#have to be really carefull about memory usage in R so this code runs slow
	rf.write("""
	
	xs = 5:20/2
		
	td = scan("%(tf)s",sep=",")
	
	td = log10(td [td != 0 ])
	th = hist(td,xs,plot=FALSE)
	rm(td)
	tc = th$counts
	rm(th)
	tc[tc==0]=1
	
	plot(xs[1:15],tc,col="red",type="l",xlab="log(distance)",ylab="Count",log="y")
	
	rm(tc)
	
	bd= scan("%(bf)s",sep=",")
	
	bd = log10(bd [bd != 0 ])
	
	bh = hist(bd,xs,plot=FALSE)
	rm(bd)
	bc = bh$counts
	rm(bh)
	bc[bc==0]=1
	lines(xs[1:15],bc,col="blue")
	rm(bc)
	
	title("%(title)s")

	
	"""%{"bf":bloodfn,"tf":tumorfn,"title":title})
	
def doPlotMapQ(rf,bloodfn,tumorfn,title):
        #have to be really carefull about memory usage in R so this code runs slow
        rf.write("""

        xs = 0:100

        ts = scan("%(tsf)s",sep=",")
	#ts = log10(ts[ts!=0])
        th = hist(ts,xs,plot=FALSE)
        tc = th$counts
        rm(th)
        tc[tc==0]=1

        plot(xs[1:100],tc,col="red",type="l",xlab="mapQ Score",ylab="Count",log="y")
        rm(tc)
        bs = scan("%(bsf)s",sep=",")
	#bs = log10(bs[bs!=0])
        bh = hist(bs,xs,plot=FALSE)
        bc = bh$counts
        rm(bh)
        bc[bc==0]=1
        lines(xs[1:100],bc,col="blue")
        rm(bc)

        title(paste("%(title)s"))

        """%{"bsf":bloodfn+"MapQ","tsf":tumorfn+"MapQ","title":title})

def getFileName(type,oriantation):
	global filenbase
	filepatern = filenbase+"-"+type+"*distance"+oriantation
	print "lookinf for files matching " + filepatern
	return glob.glob(filepatern)[0]

def getAgePrognosis(filename):
        global ageprognosis
        #example file format TCGA-13-0890-01A-01W-0420-08-good_56-test_distance01
        tk = filename.split("-")
        ageprognosis = tk[len(tk)-2]
        return ageprognosis
	
def plotLcalled(patient,indir):		
	global filenbase
	filenbase = os.path.join(indir,patient)
	rfilen = filenbase + "-calledplots.R"
	rf=startRDev(rfilen)
	print "using file base " + filenbase
	age_prognosis = getAgePrognosis(getFileName("10","*"))
	for ori in ["01","11","00","10"]:
		doRPar(rf)
		
		for co in ["0", "2", "4", "8"]:		
			doPlotCalled(rf,getFileName("10",ori+"cutoff"+co),getFileName("01",ori+"cutoff"+co),"Orientation "+ ori+" supporting reads >= " + co )
		doRMainTitle(rf,"Patient " + patient + "Cutoff by Count")
		
		doRPar(rf)
		
		for co in ["0", "0.1", "0.2", "0.3"]:		
			doPlotCalled(rf,getFileName("10",ori+"coveragecutoff"+co),getFileName("01",ori+"coveragecutoff"+co),"Orientation "+ ori+" ratio supporting reads >= " + co )
		
		doRMainTitle(rf,"Patient "  + patient + "Cutoff by Ratio")
	
	finishAndRun(rf,rfilen)
	
def plotL(patient,indir):
	global filenbase
	filenbase = os.path.join(indir,patient)
	rfilen = filenbase + "-plots.R"
	rf=startRDev(rfilen)
	print "using file base " + filenbase
	age_prognosis = getAgePrognosis(getFileName("10","*"))
	for ori in ["01","10","11","00"]:
		doRPar(rf)
		doPlot(rf,getFileName("10",ori),getFileName("01",ori),"")
		#doPlotMapQ(rf,getFileName("10",ori),getFileName("01",ori),ori)
		doRMainTitle(rf,"Patient " + patient+" Orientation "+ori)
	doRPar(rf)
	for ori in ["01","10","11","00"]:
                doPlotMapQ(rf,getFileName("10",ori),getFileName("01",ori),"Orientation " + ori + " mapQ Distribution")

	
	finishAndRun(rf,rfilen)

if __name__ == "__main__":
	for patient in sys.argv[1:]:
                plotL(patient,"./")
	#plotL(sys.argv[1],"./")

library("bioDist")
library("biclust")
library("MASS")
#patched version
source("mutualInfo.R")
#versionwithout examples
source("BicBin.R")

#
# Helper functions
#


#John's function to floor a matrix
floorMatrix<-function(inmatrix,floorValue)
{
for(i in 1:length(inmatrix))
{
if(inmatrix[i]<floorValue)
{
inmatrix[i]=floorValue
}
}
(inmatrix)
}


#John's function to remove matrix values
removeMatrixValues<-function(inMatrix,minVal)
{
matrix(3,nrow(inMatrix),ncol(inMatrix))->rr
for(i in 1:length(inMatrix))
{
if(inMatrix[i]<minVal)
	inMatrix[i]<-3
else
	rr[i]<-inMatrix[i]


}
rownames(rr)<-rownames(inMatrix)
colnames(rr)<-colnames(inMatrix)
(rr)
}

#John's function to do filtering to get population matrix
getPopulationMatrix<-function(inMatrix)
{
rr_matrix<-matrix(3,nrow(inMatrix),ncol(inMatrix))

rr_matrix<- inMatrix>3
for(i in 1:length(rr_matrix))
{

if(rr_matrix[i])
rr_matrix[i]<-1
else
rr_matrix[i]<-3
}
rownames(rr_matrix)<-rownames(inMatrix)
colnames(rr_matrix)<-colnames(inMatrix)
(rr_matrix)
}

#output counts of various tipes for use after filtering
printCountByType<-function(patientClasses,popMatrix)
{
	cancerTypes=levels(factor(patientClasses[,"CANCER_TYPE"]))
	tissueTypes=levels(factor(patientClasses[,"TISSUE"]))
	for (typei in cancerTypes)
	{
		for ( tissue in tissueTypes)
		{
			length(intersect(colnames(popMatrix),rownames(patientClasses)[patientClasses[,"CANCER_TYPE"]==typei&patientClasses[,"TISSUE"]==tissue]))->count
			cat(count)
			cat(" of cancer type ")
			cat(typei)
			cat(" and tissue ")
			cat(tissue)
			cat("\n")
		}
	}
}

#calculat the C-Index using of a cancer type using patientClasses and midsit
getCIndexByType<-function(cancerType,patientClasses,midist)
{
	
	samples = rownames(patientClasses)[patientClasses[,"CANCER_TYPE"]==cancerType]
	#browser()

	return(getCIndexBySamples(samples,midist))

}

#calculat the C-Index of a cancer type and tissue using patientClasses and Midist
getCIndexByTypeAndTissue<-function(cancerType,cancerTissue,patientClasses,midist)
{
	samples = rownames(patientClasses)[patientClasses[,"CANCER_TYPE"]==cancerType&patientClasses[,"TISSUE"]==cancerTissue]
	return(getCIndexBySamples(samples,midist))
}

#calculat the C-Index of a tissue using patientClasses and Midist
getCIndexByTissue<-function(cancerTissue,patientClasses,midist)
{
	samples = rownames(patientClasses)[patientClasses[,"TISSUE"]==cancerTissue]
	#browser()
	return(getCIndexBySamples(samples,midist))
}

#calculate the C Index for a list of samples using Midist (called by the above)
getCIndexBySamples<-function(samples,midist)
{
	
	midistLocal = as.matrix(midist)
	sortedDist = sort(as.vector(midistLocal[upper.tri(midistLocal,diag=FALSE)]))
	rcfilter = intersect(rownames(midistLocal),samples)
	mclusterdist = midistLocal[rcfilter,rcfilter]
	mclusterdist[upper.tri(mclusterdist,diag=TRUE)]=0
	clusterdist = sum(mclusterdist)
	comparisons = sum(upper.tri(mclusterdist))
	maxdist = sum(sortedDist[(length(sortedDist)-comparisons+1):length(sortedDist)])
	mindist = sum(sortedDist[1:comparisons])
	
	print(c(clusterdist,mindist,maxdist))
	return((clusterdist-mindist)/(maxdist-mindist))
}

#conveniance wrapper for car for debuging
logcat<-function(msg)
{
	debugmode = FALSE
	if(debugmode)
	{
		cat(msg)
	}
}

#this function loads the data and does most of the filtering based on the biclustering and builds 
#the data matrixes used later it is used by most of the analysis routines.
doFiltering<-function(infilename,tissue,outfilename,cutoff)
{
	cat("\nProccesing ")
	cat(infilename)
	cat(" for tissue==")
	cat(tissue)
	cat("\n")
	
	logcat("Loading Data\n")

	read.table(infilename,header=TRUE,row.names=1,sep ="\t")->fastbreakTable
	#read.table("patientNames.txt",header=FALSE,row.names=1,sep ="\t")->patientNames
	read.table("sampleMetaData.txt",header=TRUE,row.names=1,sep ="\t")->patientClasses
	

	as.matrix(fastbreakTable)->fastbreakMatrix
	
	maxcount=max(as.vector(fastbreakMatrix))
	cat(paste("Max is",maxcount, "at:\n"))
	print(which(fastbreakMatrix==maxcount,TRUE))
	png(paste(outfilename,"_break_count_density_density_tail.png",sep=""),400,300)

	
	plot(density(as.vector(fastbreakMatrix)),col=rgb(1,0,0,alpha=.5), main="",ylim=c(0,1))# main="Density of OV (blue) vs GBM (red)")

	
	dev.off()
	
	
	
	
	
	
	
	#colnames(fastbreakMatrix)<-as.vector(patientNames[colnames(fastbreakTable),1])
	

	
	
	read.table("biclusteredSamples.txt")->biclusteredPatients
	read.table("biclusteredGenes.txt")->biclusteredGenes
	
	logcat("Correctiong for Coverage\n")
	

	
	intersect(biclusteredPatients[,1],colnames(fastbreakMatrix))->correctCoveragePatients
	intersect(biclusteredGenes[,1],rownames(fastbreakMatrix))->correctCoverageGenes
	

	
	logcat("Get Population Matrix\n")
	getPopulationMatrix(fastbreakMatrix[correctCoverageGenes,correctCoveragePatients])->popMatrix
	

	
	#sumMatrixCols(popMatrix) ->sumPopMatrixCols
	logcat("Selecting Columns to Use\n")
	if(tissue=="ALL")
	{
		rownames(patientClasses)->colsToUse
	}
	else
	{
		rownames(patientClasses)[patientClasses[,"TISSUE"]==tissue]->colsToUse
	}
	
	
	
	intersect(colnames(popMatrix),colsToUse) ->colsToUse
	

	
	logcat("Filtering\n")
	popMatrix[,colsToUse]->bb
		
	
	
	
	return(list(patientClasses=patientClasses, #information about each sample
				bb=bb, # the fully filtered and binirized matrix
				fastbreakMatrix=fastbreakMatrix[rownames(bb),colnames(bb)],# the raw but filtered counts of sv per sample and gene
				fastbreakMatrixUnfiltered=as.matrix(fastbreakTable) # the raw but filtered counts of sv per sample and gene
				
				)) 
}

#
# Analysis Routines
#

#Output a count of the number of sv's in a gene across all selected samples
#and the number of samples that have greater then 3 disruption
doCountByGenes<-function(infilename,tissue,cancer,outfilename,cutoff)
{
	
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	

	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	fastbreakMatrix=filtered[["fastbreakMatrix"]]
	filteris = (patientClasses[colnames(bb),"CANCER_TYPE"]==cancer & patientClasses[colnames(bb),"TISSUE"]==tissue)
	
	write.table(rowSums(fastbreakMatrix[,filteris]),paste(outfilename,"_by_gene_Counts.txt",sep=""))
	write.table(rowSums(fastbreakMatrix[,filteris]>3),paste(outfilename,"_discrit_by_gene_Counts.txt",sep=""))
	
	

}


# do an analysis of the disruptions per gene
doGeneGene<-function(infilename,tissue,cancer,outfilename,cutoff)
{
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	cat(paste("Disease is",cancer,"\n"))
	
	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	fastbreakMatrix=filtered[["fastbreakMatrix"]]
	
	filteris = patientClasses[colnames(bb),"CANCER_TYPE"]==cancer
	bb=bb[,filteris]
	
	
	filteris = (patientClasses[colnames(bb),"CANCER_TYPE"]==cancer & patientClasses[colnames(bb),"TISSUE"]==tissue)
	totalCols = dim(bb)[1]
	cat("\nTotal Genes:\n")
	print(totalCols)
	
	cat("\nMean disruption per gene:\n")
	print(mean(rowSums(bb[,filteris]==1)))
	
	cat("\nMean disruption per patient:\n")
	print(mean(colSums(bb[,filteris]==1)))
	
	cat("\nMean percent disruption per gene:\n")
	print(mean(colSums(bb[,filteris]==1))/totalCols)
	
	
	
	#browser()
	genenames = c("RCL1","RPL23AP82")
	for ( genename in genenames)
	{
	#genename="RCL1"
	cat(paste("\n",genename,":\n",sep=""))
	
	cat("\nRow:\n")
	print(bb[genename,filteris])
	
	cat("\nNumber of disrupted patients:\n")
	#browser()
	print(sum(bb[genename,filteris]==1))
	
	#browser()
	
	cat("\nPrevalance of disruptions in all genes for disrupted patients:\n")
	print(colSums(as.matrix(bb[,bb[genename,filteris]==1])==1)/totalCols)
	
	cat("\nPrevalance of disruption disruption in all genes for non disrupted patients:\n")
	print(colSums(as.matrix(bb[,bb[genename,filteris]==3])==1)/totalCols)
	}
	
	
	
	

	
	
	
	
	

}

#calculate and save the mutual information distance between genes
doGeneByGeneMI<-function(infilename,tissue,cancer,outfilename,cutoff)
{
	
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	
	

	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	
	filteris = patientClasses[colnames(bb),"CANCER_TYPE"]==cancer
	bb=bb[,filteris]
	
	logcat("MIdist\n")
	
	cat("calling midist by gene\n")
	
	
	
	write.table(as.matrix(MIdist(bb)),paste(outfilename,"_by_gene_MIdist.distmatrix.txt",sep=""))
	
	write.table(as.matrix(mutualInfo(bb)),paste(outfilename,"_by_gene_mutualInfo.distmatrix.txt",sep=""))
	write.table(as.matrix(dist(bb)),paste(outfilename,"_by_gene_Euclid.distmatrix.txt",sep=""))
}

#do some biclustering of genes
doBiClustFile<-function(infilename,tissue,cancer,outfilename,cutoff)
{
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	
	

	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	
	filteris = patientClasses[colnames(bb),"CANCER_TYPE"]==cancer
	bb=bb[,filteris]
	bb[bb==3] = FALSE
	bb[bb==1] = TRUE
	
	write.table(as.matrix(bb),paste(infilename,".",tissue,".",cancer,".binmatrix.txt",sep=""))
	
	pdf(paste(infilename,".",tissue,".",cancer,".biclusters.pdf",sep=""),8,8)
	heatmap(bb)
	#bics <- biclust(bb,BCBimax(),minr=2, minc=10, number=100)
	#browser()
	#drawHeatmap(bb,bics,1,plotAll=TRUE,local=FALSE)
	#drawHeatmap(bb,bics,2,plotAll=TRUE,local=FALSE)
	#drawHeatmap(bb,bics,3,plotAll=TRUE,local=FALSE)
	
	#writeBiclusterResults(paste(infilename,".",tissue,".",cancer,".biclusters.txt",sep=""),bics,"bimax",rownames(bb),colnames(bb))
	dev.off()
	
	library(sddpack)
	A=sdd(bb)
	save(A,file=paste(infilename,".",tissue,".",cancer,".sdd.saved.txt",sep=""))
	
	
	#set.seed(1) 
	#pdf(paste(infilename,".",tissue,".",cancer,".plaid.bicluster.pdf",sep=""),8,8)
	#bics <- biclust(bb,BCPlaid(), back.fit = 2, shuffle = 3, fit.model = ~m + a + b, iter.startup = 5, iter.layer = 30, verbose = TRUE) 
	#drawHeatmap(bb,bics)
	#dev.off()


}



#the main analisis routing
#calculates the distance between samples using selectable distance metrics
#(mutual information beting the one we settled on) and embeds the result in 
#2d space and makes various plots
doPlot<-function(infilename,tissue,outfilename,cutoff,metric,covmat)
{
	
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	
	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	
	
	#perform distance calculations
	cat(paste("Calculating distance using",metric, "\n"))
	
	
	
	0->ss
	if(metric=="MIdist")
	{
		logcat("MIdist\n")
		MIdist(t(bb))->ss
		write.table(as.matrix(ss),paste(outfilename,"tissue",tissue,"MIdist.txt",sep=""))
	}
	else if(metric=="Hamming") # not used
	{
		
	}
	else #Euclidian
	{
		dist(t(bb))->ss
	}
	
	
	# caclulate C Indexes for various clasifications
	cancerTypes=levels(factor(patientClasses[,"CANCER_TYPE"]))
	
	for(type in cancerTypes){
		cat("C index for ")
		cat(type)
		cat(" in ")
		cat(infilename)
		cat(" ")
		cat(tissue)	
		cat(":")
		cat(getCIndexByType(type,patientClasses,ss))
		cat("\n")
	}
	
	if(tissue == "ALL")
	{
		tissueTypes=levels(factor(patientClasses[,"TISSUE"]))
		for(tissueType in tissueTypes){
			
				cat("C index for ")
				cat(tissueType)
				cat(" in ")
				cat(infilename)
				cat(" ")
				cat(tissue)	
				cat(":")
				cat(getCIndexByTissue(tissueType,patientClasses,ss))
				cat("\n")
		}
			
		for(type in cancerTypes){
			for(tissueType in tissueTypes){
			
				cat("C index for ")
				cat(tissueType)
				cat(" and ")
				cat(type)
				cat(" in ")
				cat(infilename)
				cat(" ")
				cat(tissue)	
				cat(": ")
				cat(getCIndexByTypeAndTissue(type,tissueType,patientClasses,ss))
				cat("\n")
			}
		}
	
	}
	
	#Multi dimensional scaling
	logcat("cmdscale\n")
	fit <- cmdscale(ss, eig=TRUE,k=2)
	
	
	cat("Eigen values are:\n")
	print(fit$eig)
	
	logcat("ploting\n")
	x <- fit$points[,1]
	y <- fit$points[,2]
	
	#calcualte normailzed versions of each vector of the mds Fit
	normalFit <- fit$points[,1:2]
	
	for(gg in 1:dim(normalFit)[1])
	{
	normalFit[gg,]<-normalFit[gg,]/(sum(normalFit[gg,]^2)^.5)
	}
	
	
	#Node colors and shape by class
	nodecolor = list(
	GBM = list(BLOOD = rgb(1,0,0,alpha=.5),CANCER =  rgb(1,0,0,alpha=.5)),
	OVARIAN = list(BLOOD = rgb(0,0,1,alpha=.5),CANCER =  rgb(0,0,1,alpha=.5))
	)
	nodeshape = list(
	GBM = list(BLOOD = 17,CANCER =  19),
	OVARIAN = list(BLOOD = 17,CANCER = 19)
	)
	
	#browser()
	nodecolors=c()
	nodeshapes=c()
	cancer=c()
	cancer_gbm=c()
	cancer_ov=c()
	blood=c()
	
	#build vectors of node colors and shape
	#and lists of samples for use in density ploting
	for (patient in colnames(bb))
	{
		nodecolors=append(nodecolors,nodecolor[[patientClasses[patient,"CANCER_TYPE"]]][[patientClasses[patient,"TISSUE"]]])
		nodeshapes=append(nodeshapes,nodeshape[[patientClasses[patient,"CANCER_TYPE"]]][[patientClasses[patient,"TISSUE"]]])
		val = x[patient==colnames(bb)]
		
		if(patientClasses[patient,"TISSUE"]=="BLOOD")
		{
			blood=append(blood,val)
			
		}
		
		if(patientClasses[patient,"TISSUE"]=="CANCER")
		{
			cancer= append(cancer,val)
			if(patientClasses[patient,"CANCER_TYPE"]=="GBM")
			{
				cancer_gbm = append(cancer_gbm,val)
			}
			if(patientClasses[patient,"CANCER_TYPE"]=="OVARIAN")
			{
				cancer_ov = append(cancer_ov,val)
			}
		}
	
	}

	
	
	
	# 2d scatter plot of mds
	png(paste(outfilename,".png",sep=""),800,800)

	plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Sample by sample diffrences projected using 2D Metric MDS", type="p", ylim=c(-.3,.3), cex=5,pch=nodeshapes, col=nodecolors)
	text(x, y, labels = colnames(bb), cex=.5,adj = c(.5, .5))
	if(tissue=="ALL")
	{
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, 1))
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"TISSUE"]), cex=.7,adj = c(.5, -.1))
	}
	else
	{
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, .5))
	}
	dev.off()
	
	bw=.05
	
	if(metric=="euclid")
	{
	bw=1
	}
	
	#density plots along the first axis
	if(tissue=="ALL" | tissue=="CANCER")
	{
	png(paste(outfilename,"_GMV_vs_OV_density.png",sep=""),400,300)
	d1=density(cancer_ov,bw=bw)
	d2=density(cancer_gbm,bw=bw)
	
	#ylim = c(0,max(d1$y,d2$y))
	#xlim = c(min(d1$x,d2$x),max(d1$x,d2$x))
	
	if(metric=="euclid")
	{
	ylim = c(0,.4)
	xlim = c(-70,60)
	}
	else
	{
	ylim = c(0,8)
	xlim = c(-.5,.6)
	}
	
	plot(d1, type="n", xlim=xlim, ylim=ylim, main="")#, main="Density of Blood (Green) vs Cancer (Black)")
	polygon(d1, col=rgb(0,0,1,alpha=.5))
	polygon(d2, col=rgb(1,0,0,alpha=.5))
	
	dev.off()
	}
	
	
	if(tissue=="ALL")
	{
	png(paste(outfilename,"_CANCER_vs_BLOOD_density.png",sep=""),400,300)
	d1=density(blood,bw=bw)
	d2=density(cancer,bw=bw)
	
	#ylim = c(0,max(d1$y,d2$y))
	#xlim = c(min(d1$x,d2$x),max(d1$x,d2$x))
	if(metric=="euclid")
	{
	ylim = c(0,.4)
	xlim = c(-70,60)
	}
	else
	{
	ylim = c(0,8)
	xlim = c(-.5,.6)
	}
	
	plot(d1, type="n", xlim=xlim, ylim=ylim, main="")#, main="Density of Blood (Green) vs Cancer (Black)")
	polygon(d1, col=rgb(0,1,0,alpha=.5))
	polygon(d2, col=rgb(0,0,0,alpha=.5))
	
	dev.off()
	}
	
	
	
	#normalized scater plot (to emphasize angular diffrences)
	png(paste(outfilename,"_normalized.png",sep=""),800,800)
	plot(normalFit[,1], normalFit[,2], xlab="Coordinate 1", ylab="Coordinate 2", main="Sample by sample diffrences projected using 2D Metric MDS", type="p", cex=7,pch=nodeshapes, col=nodecolors)
	if(tissue=="ALL")
	{
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, 1))
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"TISSUE"]), cex=.7,adj = c(.5, -.1))
	}
	else
	{
		#text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, .5))
	}
	dev.off()
	
	
	#if using non euclidian (euclid fails) do a non metric mds scatter plot
	if(metric!="euclid")
	{
		nonmetricfit <-isoMDS(ss)
		
		nmx <- nonmetricfit$points[,1]
		nmy <- nonmetricfit$points[,2]
		
		png(paste(outfilename,"non_metric.png",sep=""),800,800)
		plot(nmx, nmy, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=nodeshapes, col=nodecolors)
		if(tissue=="ALL")
		{
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, 1))
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(bb),"TISSUE"]), cex=.7,adj = c(.5, -.1))
		}
		else
		{
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, .5))
		}
		dev.off()
	}
	
	#scatter plot of just ov fastbreak to look fore corespondance with clinical data
	if(outfilename == "Fastbreak_tumor_cutoff_3" || outfilename == "Fastbreak_blood_cutoff_3" )
	{
		png(paste(outfilename,"_all_info.png",sep=""),800,800)
		plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=nodeshapes, col=nodecolors)

		
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"TISSUE"]), cex=.7,adj = c(.5, -1.8))
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, -.6))
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"STATUS"]), cex=.7,adj = c(.5, .6))
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"RESISTANCE"]), cex=.7,adj = c(.5, 1.8))
		dev.off()
		
		filteris = patientClasses[colnames(bb),"CANCER_TYPE"]=="OVARIAN"
		ovbb=as.matrix(ss)[filteris,filteris]
		ovss=as.dist(ovbb)
		
		png(paste(outfilename,"_hclust_just_ov.png",sep=""),800,800)
		plot(hclust(ovss))
		dev.off()
		
		logcat("cmdscale of\n")

		fit <- cmdscale(ovss, eig=TRUE,k=2)
		
		cat("Eigen values of just ov are:\n")
		print(fit$eig)
		
		logcat("ploting\n")
		x <- fit$points[,1]
		y <- fit$points[,2]
		

		png(paste(outfilename,"_all_info_just_ov.png",sep=""),800,800)
		plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=rgb(0,0,.3,alpha=.5))

		
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"TISSUE"]), cex=.7,adj = c(.5, -1.1))
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"STATUS"]), cex=.7,adj = c(.5, 0))
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"RESISTANCE"]), cex=.7,adj = c(.5, 1.1))
		dev.off()
		
		if(metric!="euclid")
		{
			nonmetricfit <-isoMDS(ovss)
		
			nmx <- nonmetricfit$points[,1]
			nmy <- nonmetricfit$points[,2]
			
			png(paste(outfilename,"_all_info_non_metric_just_ov.png",sep=""),800,800)
			plot(nmx, nmy, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=rgb(0,0,.3,alpha=.5))
	
			
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"TISSUE"]), cex=.7,adj = c(.5, -1.1))
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"STATUS"]), cex=.7,adj = c(.5, 0))
			text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"RESISTANCE"]), cex=.7,adj = c(.5, 1.1))
			dev.off()
		}			
		
	
	

	
	
	}
	
	


	#plot to compare with coverage if coverage was passed in
	if(!missing(covmat))
	{
		for (i in 1:2)
		{
			covvec = covmat[,i]
			sampvec = fit$points[,i]
			commonsamples = intersect(names(covvec),names(sampvec))
			filename = paste(outfilename,"_vs_coverage_component_",i,".png",sep="")
			#pdf(filename,12,12)
			png(filename,800,800)
			plot(sampvec[commonsamples], covvec[commonsamples], xlab=paste("Coordinate",i,"Breaks"), ylab=paste("Coordinate",i,"Coverage"), main="Mutual Information projected using 2D Metric MDS", type="n")
			text(sampvec[commonsamples], covvec[commonsamples], labels=commonsamples, cex=.7)
			cat("Wrote coverage comparison plot to ")
			cat(filename)
			cat("\n")
			
			dev.off()
		}
		
		
	}
	return(fit$points)
}

#do all the miplots with score filreting
doMIPlotsByScore<-function()
{
	covcanc = doPlot("formated.coverage.per.gene.per.sample.tsv","CANCER","coverage_tumor_cutoff_3_MIdist",3,"MIdist")
	covblood = doPlot("formated.coverage.per.gene.per.sample.tsv","BLOOD","coverage_blood_cutoff_3_MIdist",3,"MIdist")
	covall = doPlot("formated.coverage.per.gene.per.sample.tsv","ALL","coverage_all_cutoff_3_MIdist",3,"MIdist")


	for (scoreCutoff in c(0))#)c(0,25,50,75,90,94,96,98,99))
	{
		for (coli in c(4,5))
		{
			filename = paste("formated.fastbreak.per.gene.score.minscore.",scoreCutoff,".col.",coli,".matrix.tsv",sep="")
			
			doPlot(filename,"BLOOD",paste(filename,".blood",sep=""),3,"MIdist",covblood)
			doPlot(filename,"CANCER",paste(filename,".tumor",sep=""),3,"MIdist",covcanc)
			doPlot(filename,"ALL",paste(filename,".all",sep=""),3,"MIdist",covall)
		}
	}
	
	doPlot("breakdancer.per.gene.score.matrix.tsv","CANCER","breakdancer_tumor_cutoff_3_MIdist",3,"MIdist",covcanc)
	doPlot("breakdancer.per.gene.score.matrix.tsv","BLOOD","breakdancer_blood_cutoff_3_MIdist",3,"MIdist",covblood)
	doPlot("breakdancer.per.gene.score.matrix.tsv","ALL","breakdancer_all_cutoff_3_MIdist",3,"MIdist",covall)
	

}

#do gene midistance calculations for each cancer
doGeneMIs<-function()
{
	filename = "formated.fastbreak.per.gene.score.minscore.0.col.4.matrix.tsv"
	doGeneByGeneMI(filename,"CANCER","OVARIAN","Fastbreak_tumor_cutoff_OV_3",3)
	doGeneByGeneMI(filename,"CANCER","GBM","Fastbreak_tumor_cutoff_GBM_3",3)
}

#do gene analysis
doGeneGenes<-function()
{
	filename = "formated.fastbreak.per.gene.score.minscore.0.col.4.matrix.tsv"
	#doGeneGene(filename,"CANCER","OVARIAN","Fastbreak_tumor_cutoff_OV_3",3)
	doGeneGene(filename,"CANCER","GBM","Fastbreak_tumor_cutoff_GBM_3",3)
}

#calculate gene counts
doGeneCounts<-function()
{
	filename = "formated.fastbreak.per.gene.score.minscore.0.col.4.matrix.tsv"
	doCountByGenes(filename,"CANCER","OVARIAN","Fastbreak_tumor_cutoff_OV_3",3)
	doCountByGenes(filename,"CANCER","GBM","Fastbreak_tumor_cutoff_GBM_3",3)
	doCountByGenes(filename,"BLOOD","OVARIAN","Fastbreak_blood_cutoff_OV_3",3)
	doCountByGenes(filename,"BLOOD","GBM","Fastbreak_blood_cutoff_GBM_3",3)
}

#do biclustering of genes
doBiClust<-function()
{
	filename = "formated.fastbreak.per.gene.score.minscore.0.col.4.matrix.tsv"
	doBiClustFile(filename,"CANCER","OVARIAN","Fastbreak_tumor_cutoff_OV_3",3)
	doBiClustFile(filename,"CANCER","GBM","Fastbreak_tumor_cutoff_GBM_3",3)
}



checkPairs<-function(samplenames)
{
	rv=c()
	oplist=list("01"="10","10"="01")
	
	for (sn in samplenames)
	{
		op = paste(substring(sn,0,13),oplist[[substring(sn,14,15)]],sep="")
		if (op %in% samplenames)
		{
			rv=c(rv,sn)
		}
	}
	
	return(rv);

}


do2Clusts<-function(x,outfilename)
{
	clust <- try(kmeans(x, c(min(x),max(x)),iter.max = 40))
	if(class(clust)=="try-error")
	{
		cat("\nClustering Failed.\n")
		return();
	}
	
			
	d1=density(x)
	d2=density(x[clust$cluster==1],bw=d1$bw)
	d3=density(x[clust$cluster==2],bw=d1$bw)
	
	d2$y=d2$y*(sum(clust$cluster==1)/length(x))
	d3$y=d3$y*(sum(clust$cluster==2)/length(x))
		
	ymax=max(max(d1$y),max(d2$y),max(d3$y))
	
	png(paste(outfilename,"2_cluster_density.png",sep=""),400,300)
	plot(d1,col=rgb(0,0,0,alpha=.5), main="Clustering Based on Gene Coverage",ylim=c(0,ymax))
	polygon(d2, col=rgb(0,1,0,alpha=.5))
	polygon(d3, col=rgb(1,0,0,alpha=.5))
	
	dev.off()
	
	return(clust);
}

doAll<-function()
{
	doQA()
	doMIPlotsByScore()
	
}

doQA<-function()
{


	
	cat("Loading sample metadata.\n")
	patientClasses=read.table("sampleMetaData.txt",header=TRUE,row.names=1,sep ="\t")
	
	cat("Loading fastbreak results.")
	unfilteredBreaks = as.matrix(read.table("formated.fastbreak.per.gene.score.minscore.0.col.4.matrix.tsv",header=TRUE,row.names=1,sep ="\t"))
	
	cat("Looking for blood sample outliers.\n")
	bloodsamples = rownames(patientClasses)[patientClasses[,"TISSUE"]=="BLOOD"]
	cancersamples = rownames(patientClasses)[patientClasses[,"TISSUE"]=="CANCER"]
	cat("There are ",length(bloodsamples),"BLOOD samples and ",length(cancersamples),"CANCER samples.\n")
	cat("This includes",sum(patientClasses[,"CANCER_TYPE"]=="GBM"),"GBM samples and",sum(patientClasses[,"CANCER_TYPE"]=="OVARIAN"),"OVARIAN samples.\n")
	
	
	breakSums = colSums(unfilteredBreaks[,bloodsamples])
	#plot
	clustRS = do2Clusts(breakSums,"qa_plots_BLOOD_Breaks_colSums")
	cutoff=(mean(breakSums))
	goodbloodsamples = names(breakSums[breakSums<cutoff])
	cat("Found",length(bloodsamples)-length(goodbloodsamples),"abnormal blood samples:\n")
	print(names(breakSums[breakSums>=cutoff]))
	badbloodremoveddamples = checkPairs(c(cancersamples,goodbloodsamples))
	
#	for ( tissue in c("BLOOD","CANCER"))
#	{
#		samples = rownames(patientClasses)[patientClasses[,"TISSUE"]==tissue] #goodcovSamples[patientClasses[goodcovSamples,"TISSUE"]==tissue]
#		
#		clustRS = do2Clusts(colSums(unfilteredBreaks[,samples]),paste("qa_plots_",tissue,"_Breaks_colSums",sep=""))
#		
#		logcat("MIdist\n")
#		MIdist(t(unfilteredBreaks[,samples]))->ss
#		
#		logcat("cmdscale\n")
#		fit <- cmdscale(ss, eig=TRUE,k=2)
#		
#		
#		cat("Eigen values are:\n")
#		print(fit$eig)
#		
#		logcat("ploting\n")
#		x <- fit$points[,1]
#		y <- fit$points[,2]
#		clustMI = do2Clusts(x,paste("qa_plots_",tissue,"_Breaks_Midist_CMD_commponent1",sep=""))
#	}
	
	
	#browser()

	

	
#	
#	logcat("MIdist\n")
#	#browser()
#	MIdist(t(unfilteredCov))->ss
#	
#	logcat("cmdscale\n")
#	fit <- cmdscale(ss, eig=TRUE,k=2)
#	
#	
#	cat("Eigen values are:\n")
#	print(fit$eig)
#	
#	logcat("ploting\n")
#	x <- fit$points[,1]
#	y <- fit$points[,2]
#	
#	clust = do2Clusts(x,"qa_plots_coverage_Midist_CMD_commponent1_")
#	#browser()
#	
#	cat("Cluster 1:\n\n",colnames(unfilteredCov)[clust$cluster==1],"\n",sep=" ")
#	cat("Cluster 2:\n\n",colnames(unfilteredCov)[clust$cluster==2],"\n",sep=" ")
#	
#	
#	goodcovSamples = checkPairs(colnames(unfilteredCov)[clust$cluster==1])
	
	
	

	cat("Loading gene info from genelist.txt\n")
	read.table("genelist.txt",header=FALSE,row.names=1,sep ="\t")->geneData
	
	cat("Loading coverage data.\n")
	unfilteredCov = as.matrix(read.table("formated.coverage.per.gene.per.sample.tsv",header=TRUE,row.names=1,sep ="\t"))
	unfilteredCov[,badbloodremoveddamples]->thresholdedCov
	rownames(unfilteredCov)->genenames
	
	geneLengths = geneData[genenames,5]-geneData[genenames,4]
	thresholdedCov<-t(t(thresholdedCov)/geneLengths)
	
#	for ( gene in genenames)
#	{
#		thresholdedCov[gene,] <- thresholdedCov[gene,]/(geneData[gene,5]-geneData[gene,4]) #Theo's heuristic
#	}

	thresholdedCov=thresholdedCov>mean(thresholdedCov)
	
	cat("Finding bicluster.\n")
	biclusters = BicBin(thresholdedCov, 0.5, 0.5, sum(thresholdedCov) / length(thresholdedCov))
	
	biclustersamples=checkPairs(colnames(thresholdedCov)[biclusters$y==1])
	
	
	biclustergenes=rownames(thresholdedCov)[biclusters$x==1]
	
	cat(length(biclustersamples),"samples and",length(biclustergenes)," genes passed biclustering.\n")
	cat("This includes",sum(patientClasses[biclustersamples,"CANCER_TYPE"]=="GBM"),"GBM samples and",sum(patientClasses[biclustersamples,"CANCER_TYPE"]=="OVARIAN"),"OVARIAN samples.\n")
	
	write.table(biclustersamples,"biclusteredSamples.txt",row.names = FALSE, col.names = FALSE, quote=FALSE)
	write.table(biclustergenes,"biclusteredGenes.txt",row.names = FALSE, col.names = FALSE, quote=FALSE)

	



}


x <- matrix(rnorm(100), nrow = 5)
      mutualInfo(x, nbin = 3)







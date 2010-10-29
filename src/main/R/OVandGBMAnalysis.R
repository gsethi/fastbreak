filterMatrix<-function(inmatrix,thresholdamount)
{
	#basic filter by sum
	vector("numeric",nrow(inmatrix))->inmatrix_sums
	for(i in 1:nrow(inmatrix))
	{
		inmatrix_sums[i]<-sum(inmatrix[i,])
	}

	filteredRows<- (inmatrix_sums > thresholdamount)

	inmatrix[filteredRows,]
}

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

getCIndexByType<-function(cancerType,patientClasses,midist)
{
	
	samples = rownames(patientClasses)[patientClasses[,"CANCER_TYPE"]==cancerType]
	#browser()

	return(getCIndexBySamples(samples,midist))

}

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

getCIndexByTypeAndTissue<-function(cancerType,cancerTissue,patientClasses,midist)
{
	samples = rownames(patientClasses)[patientClasses[,"CANCER_TYPE"]==cancerType&patientClasses[,"TISSUE"]==cancerTissue]
	return(getCIndexBySamples(samples,midist))
}

getCIndexByTissue<-function(cancerTissue,patientClasses,midist)
{
	samples = rownames(patientClasses)[patientClasses[,"TISSUE"]==cancerTissue]
	#browser()
	return(getCIndexBySamples(samples,midist))
}

getCIndexBySamples<-function(samples,midist)
{
	sortedDist = sort(as.vector(midist))
	midist = as.matrix(midist)
	rcfilter = intersect(rownames(midist),samples)
	mclusterdist = midist[rcfilter,rcfilter]
	mclusterdist[upper.tri(mclusterdist,diag=TRUE)]=0
	clusterdist = sum(mclusterdist)
	comparisons = sum(upper.tri(mclusterdist))
	maxdist = sum(sortedDist[(length(sortedDist)-comparisons+1):length(sortedDist)])
	mindist = sum(sortedDist[1:comparisons])
	
	
	return((clusterdist-mindist)/(maxdist-mindist))
}

logcat<-function(msg)
{
	debugmode = FALSE
	if(debugmode)
	{
		cat(msg)
	}
}


doFiltering<-function(infilename,tissue,outfilename,cutoff)
{
	cat("Proccesing ")
	cat(infilename)
	cat(" for tissue==")
	cat(tissue)
	cat("\n")
	
	logcat("Loading Data\n")

	read.table(infilename,header=TRUE,row.names=1)->fastbreakTable
	read.table("patientNames.txt",header=FALSE,row.names=1)->patientNames
	read.table("ClassVarsOld.txt",header=TRUE,row.names=1)->patientClasses
	

	as.matrix(fastbreakTable)->fastbreakMatrix
	colnames(fastbreakMatrix)<-as.vector(patientNames[colnames(fastbreakTable),1])
	
	
	read.table("patientList.txt")->biclusteredPatients
	read.table("geneList.txt")->biclusteredGenes
	
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
		
	
	filterMatrix(bb,cutoff)->cc
	
	return(list(cc=cc,patientClasses=patientClasses,bb=bb))
}

doGeneByGeneMI<-function(infilename,tissue,cancer,outfilename,cutoff)
{
	
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	
	cc=filtered[["cc"]]
	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	
	filteris = patientClasses[colnames(bb),"CANCER_TYPE"]==cancer
	bb=bb[,filteris]
	
	logcat("MIdist\n")
	
	#MIdist(t(cc))->ss
	cat("calling midist by gene\n")
	
	write.table(rowSums(cc),paste(outfilename,"_by_gene_Counts.txt",sep=""))
	
	write.table(as.matrix(MIdist(cc)),paste(outfilename,"_by_gene_MIdist.txt",sep=""))
}

doPlot<-function(infilename,tissue,outfilename,cutoff,covmat)
{
	
	doFiltering(infilename,tissue,outfilename,cutoff)->filtered
	
	cc=filtered[["cc"]]
	patientClasses=filtered[["patientClasses"]]
	bb=filtered[["bb"]]
	
	
	
	logcat("MIdist\n")
	
	MIdist(t(cc))->ss
	
	
	#browser()
	cat("calling midist by gene\n")
	
	
	
	#write.table(as.matrix(MIdist(cc)),paste(outfilename,"_by_gene_MIdist.txt",sep=""))

	
	cancerTypes=levels(factor(patientClasses[,"CANCER_TYPE"]))
	
	for(type in cancerTypes){
		cat("C index for ")
		cat(type)
		cat(" in ")
		cat(infilename)
		cat(" using tissue type ")
		cat(tissue)	
		cat(":\n")
		print(getCIndexByType(type,patientClasses,ss))
	}
	
	if(tissue == "ALL")
	{
		tissueTypes=levels(factor(patientClasses[,"TISSUE"]))
		for(tissueType in tissueTypes){
			
				cat("C index for ")
				cat(tissueType)
				cat(" in ")
				cat(infilename)
				cat(" using tissue type ")
				cat(tissue)	
				cat(":\n")
				print(getCIndexByTissue(tissueType,patientClasses,ss))
		}
			
		for(type in cancerTypes){
			for(tissueType in tissueTypes){
			
				cat("C index for ")
				cat(tissueType)
				cat(" and ")
				cat(type)
				cat(" in ")
				cat(infilename)
				cat(" using tissue type ")
				cat(tissue)	
				cat(":\n")
				print(getCIndexByTypeAndTissue(type,tissueType,patientClasses,ss))
			}
		}
	
	}
	
	logcat("cmdscale\n")
	fit <- cmdscale(ss, eig=TRUE,k=2)
	
	
	cat("Eigen values are:\n")
	print(fit$eig)
	
	logcat("ploting\n")
	x <- fit$points[,1]
	y <- fit$points[,2]
	
	nonmetricfit <-isoMDS(ss)
	
	nmx <- nonmetricfit$points[,1]
	nmy <- nonmetricfit$points[,2]
	
	#browser()
	

	
	#pdf(paste(outfilename,".pdf",sep=""),12,12)
	
	
	nodecolor = list(
	GBM = list(BLOOD = rgb(1,0,0,alpha=.5),CANCER =  rgb(.3,0,0,alpha=.5)),
	OVARIAN = list(BLOOD = rgb(0,0,1,alpha=.5),CANCER =  rgb(0,0,.3,alpha=.5))
	)
	
	#browser()
	nodecolors=c()
	for (patient in colnames(bb))
	{
	nodecolors=append(nodecolors,nodecolor[[patientClasses[patient,"CANCER_TYPE"]]][[patientClasses[patient,"TISSUE"]]])
	}
	#browser()
	
	png(paste(outfilename,".png",sep=""),800,800)
	plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=nodecolors)
	if(tissue=="ALL")
	{
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, 1))
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"TISSUE"]), cex=.7,adj = c(.5, -.1))
	}
	else
	{
		text(x, y, labels = as.vector(patientClasses[colnames(bb),"CANCER_TYPE"]), cex=.7,adj = c(.5, .5))
	}
	dev.off()
	
	png(paste(outfilename,"non_metric.png",sep=""),800,800)
	plot(nmx, nmy, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=nodecolors)
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
	
	
	if(outfilename == "Fastbreak_tumor_cutoff_3" || outfilename == "Fastbreak_blood_cutoff_3" )
	{
		png(paste(outfilename,"_all_info.png",sep=""),800,800)
		plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=nodecolors)

		
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
		
		nonmetricfit <-isoMDS(ovss)
	
		nmx <- nonmetricfit$points[,1]
		nmy <- nonmetricfit$points[,2]
		
		png(paste(outfilename,"_all_info_just_ov.png",sep=""),800,800)
		plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=rgb(0,0,.3,alpha=.5))

		
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"TISSUE"]), cex=.7,adj = c(.5, -1.1))
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"STATUS"]), cex=.7,adj = c(.5, 0))
		text(x, y, labels = as.vector(patientClasses[colnames(ovbb),"RESISTANCE"]), cex=.7,adj = c(.5, 1.1))
		dev.off()
		
		png(paste(outfilename,"_all_info_non_metric_just_ov.png",sep=""),800,800)
		plot(nmx, nmy, xlab="Coordinate 1", ylab="Coordinate 2", main="Mutual Information projected using 2D Metric MDS", type="p", cex=8,pch=19, col=rgb(0,0,.3,alpha=.5))

		
		text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"TISSUE"]), cex=.7,adj = c(.5, -1.1))
		text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"STATUS"]), cex=.7,adj = c(.5, 0))
		text(nmx, nmy, labels = as.vector(patientClasses[colnames(ovbb),"RESISTANCE"]), cex=.7,adj = c(.5, 1.1))
		dev.off()
			
		
	
	

	
	
	}
	
	
	
	
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


doMIPlots<-function()
{
	covcanc = doPlot("coverage.per.gene.per.sample.tsv","CANCER","coverage_tumor_cutoff_3",3)
	covblood = doPlot("coverage.per.gene.per.sample.tsv","BLOOD","coverage_blood_cutoff_3",3)
	covall = doPlot("coverage.per.gene.per.sample.tsv","ALL","coverage_all_cutoff_3",3)

	doPlot("fastbreak.per.gene.score.matrix.tsv","BLOOD","Fastbreak_blood_cutoff_3",3,covblood)
	doPlot("fastbreak.per.gene.score.matrix.tsv","CANCER","Fastbreak_tumor_cutoff_3",3,covcanc)
	doPlot("fastbreak.per.gene.score.matrix.tsv","ALL","Fastbreak_all_cutoff_3",3,covall)





	doPlot("breakdancer.per.gene.score.matrix.tsv","CANCER","breakdancer_tumor_cutoff_3",3,covcanc)
	doPlot("breakdancer.per.gene.score.matrix.tsv","BLOOD","breakdancer_blood_cutoff_3",3,covblood)
	doPlot("breakdancer.per.gene.score.matrix.tsv","ALL","breakdancer_all_cutoff_3",3,covall)
}

doGeneMIs<-function()
{
	doGeneByGeneMI("fastbreak.per.gene.score.matrix.tsv","CANCER","OVARIAN","Fastbreak_tumor_cutoff_OV_3",3)
	doGeneByGeneMI("fastbreak.per.gene.score.matrix.tsv","CANCER","GBM","Fastbreak_tumor_cutoff_GBM_3",3)
}


library("bioDist")
library("MASS")
#patched version
source("mutualInfo.R")









#doPlot("fastbreak.per.gene.score.matrix.tsv","CANCER","Fastbreak_tumor_cutoff_6",6)
#
#doPlot("breakdancer.per.gene.score.matrix.tsv","CANCER","breakdancer_tumor_cutoff_6",6)
#doPlot("breakdancer.per.gene.score.matrix.tsv","BLOOD","breakdancer_blood_cutoff_6",6)
#doPlot("breakdancer.per.gene.score.matrix.tsv","ALL","breakdancer_all_cutoff_6",6)
#
#doPlot("coverage.per.gene.per.sample.tsv","CANCER","coverage_tumor_cutoff_6",6)
#doPlot("coverage.per.gene.per.sample.tsv","BLOOD","coverage_blood_cutoff_6",6)
#doPlot("coverage.per.gene.per.sample.tsv","ALL","coverage_all_cutoff_6",6)
#
#doPlot("fastbreak.per.gene.score.matrix.tsv","CANCER","Fastbreak_tumor_cutoff_9",9)
#
#doPlot("breakdancer.per.gene.score.matrix.tsv","CANCER","breakdancer_tumor_cutoff_9",9)
#doPlot("breakdancer.per.gene.score.matrix.tsv","BLOOD","breakdancer_blood_cutoff_9",9)
#doPlot("breakdancer.per.gene.score.matrix.tsv","ALL","breakdancer_all_cutoff_9",9)
#
#doPlot("coverage.per.gene.per.sample.tsv","CANCER","coverage_tumor_cutoff_9.pdf",9)
#doPlot("coverage.per.gene.per.sample.tsv","BLOOD","coverage_blood_cutoff_9.pdf",9)
#doPlot("coverage.per.gene.per.sample.tsv","ALL","coverage_all_cutoff_9.pdf",9)
#
#doPlot("fastbreak.per.gene.score.matrix.tsv","ALL","Fastbreak_tumor_cutoff_3.pdf",3)
#doPlot("fastbreak.per.gene.score.matrix.tsv","ALL","Fastbreak_tumor_cutoff_6.pdf",6)
#doPlot("fastbreak.per.gene.score.matrix.tsv","ALL","Fastbreak_tumor_cutoff_9.pdf",9)
#doPlot("fastbreak.per.gene.score.matrix.tsv","BLOOD","Fastbreak_blood.pdf")


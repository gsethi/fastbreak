doGeneSepPlot<-function(infilename)
{
	cat(paste("Procesing",infilename,"\n"))
	as.matrix(read.table(infilename,header=TRUE,row.names=1))->ggMId
	
	#is this suffichent filtering?
	filterVec = rowSums(ggMId<1 & ggMId> .97) > 0
	
	#ggMId[ggMId==1 & ggMId < .97] = NA
	ggMId = ggMId[filterVec,filterVec]
	
	fit <- cmdscale(as.dist(ggMId), eig=TRUE,k=6)
	
	
	cat("Eigen values are:\n")
	print(fit$eig)
	

	x <- fit$points[,1]
	y <- fit$points[,2]
	mydata<-fit$points[,1:2]
	
	
	pdf(paste(infilename,".MDS.clusters.pdf",sep=""),16,16)

	plot(x, y, xlab="Coordinate 1", ylab="Coordinate 2", main="Gene by gene diffrences projected using 2D Metric MDS", type="n")
	text(x, y, labels = rownames(ggMId), cex=.4)
	
	

	# Cluster Plot against 1st 2 principal components
	fit <- kmeans(mydata, 10,iter.max = 40)
	print(fit)
	write.table(fit$cluster,paste(infilename,".kmeans.clusters.txt",sep=""))
	# vary parameters for most readable graph
	library(cluster) 
	clusplot(mydata, fit$cluster, color=TRUE, shade=TRUE, labels=2, lines=0)
	#text(x, y, labels = rownames(ggMId), cex=.4)
	
	# Centroid Plot against 1st 2 discriminant functions
	library(fpc)
	plotcluster(mydata, fit$cluster)
	#text(x, y, labels = rownames(ggMId), cex=.4)
	
	
	
	dev.off()
	
	
	
}

doGG<-function()
{
	doGeneSepPlot("Fastbreak_tumor_cutoff_GBM_3_by_gene_MIdist.distmatrix.txt")
	doGeneSepPlot("Fastbreak_tumor_cutoff_OV_3_by_gene_MIdist.distmatrix.txt")
}

doBiclust<-function(infile)
{


}

library("bioDist")
library("MASS")

#patched version
source("mutualInfo.R")



setGeneric("mutualInfo", function(x, ...) standardGeneric("mutualInfo"))

setMethod("mutualInfo", signature=signature("matrix"),
    function(x, nbin=10, diag=FALSE, upper=FALSE)
{
   x <- as.matrix(x)
   nc <- ncol(x)
   nr <- nrow(x)
   clist <- vector("list", length=nr)
   for(i in 1:nr)
   {
   
		bincount = nbin   	
       if(max(x[i,])==min(x[i,]) && length(bincount)==1)
       {
       mymin = min(x[i,]) - 1
       mymax = mymin + 2
       bincount = mymin + 0:bincount*(2/(bincount))
       	
       }
       clist[[i]] <- cut(x[i,], breaks=bincount)
	}
   ppfun <- function(pp) {pp<-pp[pp>0]; -sum(pp*log(pp ))}
   appfun <- function(x,y) {ppfun(table(x)/nc)+ppfun(table(y)/nc) -
                                 ppfun(c(table(x, y)/nc))}

   rvec<-rep(NA, nr*(nr-1)/2)
   ct <- 1
   for(i in 1:(nr-1))
       for(j in (i+1):nr) {
           rvec[ct] <- appfun(clist[[i]], clist[[j]])
           ct <- ct+1
   }   
   attributes(rvec) <- list(Size = nr, Labels = row.names(x),
                            Diag = diag, Upper = upper, methods =
                            "mutualInfo", class = "dist")
   rvec
} )

setMethod("mutualInfo", signature=signature("ExpressionSet"),
    function(x, nbin=10, diag=FALSE, upper=FALSE, sample=TRUE) {
        if( sample ) ep = t(exprs(x)) else ep = exprs(x)
        mutualInfo(ep, nbin, diag, upper)
    })


setGeneric("MIdist", function(x, ...) standardGeneric("MIdist"))

setMethod("MIdist", signature=signature("matrix"),
    function(x, nbin=10, diag=FALSE, upper=FALSE) 
  1 - (1 - exp(-2*mutualInfo(x, nbin, diag, upper)))^.5
)

setMethod("MIdist", signature=signature("ExpressionSet"),
    function(x, nbin=10, diag=FALSE, upper=FALSE, sample=TRUE) {
        if( sample ) ep = t(exprs(x)) else ep = exprs(x)
        MIdist(ep, nbin, diag, upper)
        })

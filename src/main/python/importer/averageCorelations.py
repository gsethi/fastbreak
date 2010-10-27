__author__ = 'rbressle'

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
  
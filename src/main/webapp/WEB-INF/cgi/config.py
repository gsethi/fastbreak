#!/local/bin/python2.6.5/python

#path to the .breakdancer.out and breakdancer.out.pickle 
datapath = "/local/addama/domains/public/scripts/transplantdemo/pickleFiles"
#transplantws = "/cgi-bin/transplantws.py"

#paths to datasources. can use dataproxy.py if needed to avoid XSS
#survivaldatasource = "/addama/datasources/csacr/prognosis/google-ds-api"
#genedatasource = "/addama/datasources/csacr/genes/google-ds-api"

#server to proxy over for dataservices if needed to avoid XSS limitations
#proxyhost = "http://jefferson:9081"

#server paths
#jsdir = "/transplants/"
#loadergif = "/transplants/ajax-loader.gif"

#picklehost="https://addama-systemsbiology-public.appspot.com"
loadPickleFromUri=False
debugmode=True
logfile="log.txt"

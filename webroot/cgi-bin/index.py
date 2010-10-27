#!/usr/bin/python
import os, glob
import cgi
import cgitb
cgitb.enable()
from config import *


vars={'checkboxes':"",'transplantws':transplantws,'survivaldatasource':survivaldatasource,'genedatasource':genedatasource,"jsdir":jsdir,"loadergif":loadergif}


files=[]
tr=""
lastfile = ""
for infile in glob.glob(os.path.join(os.getcwd(),'../data/*out.pickle')):
	basename = os.path.basename(infile);
	if basename[:12] != lastfile [:12]:
		vars['checkboxes'] +="<br/><br/>%s:<br/>"%basename[:12]
	vars['checkboxes'] += "<input type='checkbox' id='%(file)s' name='%(file)s'/>%(file)s "%{'file':basename}
	files.append(basename)
	lastfile=basename
vars["files"]="['"+"','".join(files)+"']"
	
	
print "Content-type: text/html"
print
print """<?xml version="1.0" ?>

<html xmlns="http://www.w3.org/1999/xhtml" 

                 xmlns:svg="http://www.w3.org/2000/svg"

     xmlns:xlink="http://www.w3.org/1999/xlink"

     lang="en-US">
<head>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />

<title>Transplant</title>

<style>
body { 
font: 8pt helvetica neue;
color: #666;
}
td { 
font: 8pt helvetica neue;
color: #666;
}
input {
font: 10pt helvetica neue;
}
.outlined {
	color: #666;
	border-color: #F5F5F5;
	border-width: 2px 2px 2px 2px;
	border-style: solid;
	border-spacing: 0px;
	
	}

</style>
	
<script type='text/javascript' src='http://www.google.com/jsapi'></script>
<script type='text/javascript'>
  google.load('visualization', '1', {packages:["table"]});
  //google.load('prototype', '1.6');
</script>
<script type='text/javascript' src='../transplant.js'></script>

<script type='text/javascript' >


filenames = %(files)s;
transplantws = "%(transplantws)s";
survivaldatasource = "%(survivaldatasource)s";
genedatasource = "%(genedatasource)s";
loadingpatientinfo = true;
patients = {};
sampletypes = {};
progstyle ={"Poor":"border-color: #F5B9B9;","Good":"border-color: #B9F5B9;","Medium":"border-color: #F5F5B9;"};
samplelabels = {"10":"Blood","11":"Adjacent","01":"Tumor"};
ajloader = "../ajax-loader.gif"

function grow()
{
	loadingpatientinfo = true;
	document.getElementById('visdiv').innerHTML="<center><img src='"+ajloader+"'/><br/>Loading Patient Data...<\/center>";
	loadthese=[];
	drawthese=[];

	patients = {}
	sampletypes = {"10":true,"11":true,"01":true};
	
	
	
	for (var i in filenames)
	{
		var filename = filenames[i];
		if(document.getElementById(filename).checked)
		{
			loadthese.push(filename);
			
			var patientid = filename.substring(0,12);
			var sampletype = filename.substring(13,15)
			log("patient '" + patientid + "' sampletype '" + sampletype + "'")
			
			if(!patients.hasOwnProperty(patientid))
			{
				patients[patientid] = {samples:{}}
			}
			if(!patients[patientid].samples.hasOwnProperty(sampletype))
			{
				patients[patientid].samples[sampletype]=[];
			}
			patients[patientid].samples[sampletype].push(filename);
			
			
			sampletypes[sampletype] = true
			
			/*var filename = filenames[i];
			loadthese.push(filename);
			var patientid = filename.substring(0,12)
			var sampletype = filename.substring(13,15)
			log("patient '" + patientid + "' sampletype '" + sampletype + "'")
			
			if(!patients.hasOwnProperty(patientid))
			{
				patients[patientid] = {samples:{}}
			}
			if(!patients[patientid].samples.hasOwnProperty(sampletype))
			{
				patients[patientid].samples[sampletype]=[];
			}
			patients[patientid].samples[sampletype].push(filename);
			
			
			sampletypes[sampletype] = true*/
		}
	}
	loadAll();
	
	log("building survival query");
	var orarray = []
	for (var patient in patients)
	{
		orarray.push("(PATIENT_ID = '"+patient+"')");
	}
	
	var patientquery = "select * where " + orarray.join(" or ") + "order by time_years desc";
	
	var query = new google.visualization.Query(survivaldatasource);
	query.setQuery(patientquery);
	
	log("sending query " + patientquery + " to " + survivaldatasource);
	query.send(handleSurvivalResponse);
	
	
	
			
}






</script>
<script type='text/javascript' src='../transplantpage.js' ></script>
<style>
body { margin: 30px; text-align: left; white-space: nowrap;}

</style>

</head>

<body>

<div>
<form>
Data Files:<br/>
<input type="checkbox" id="checkallb" onchange = "script:checkallf();" /> Check All
<div style="width:95%%;height:300;overflow:auto;border:2px grey solid;">
%(checkboxes)s
</div>
<br/>Root:<br/>
Chr:<input type='text' id="chr" value="chr22"/>
Start:<input type='text' id="start" value="27793997"/>
End:<input type='text' id="end" value="28226514"/><br/>
Search:<br/>
Depth:<input type='text' id="depth" value="2"/>
Radius:<input type='text' id="radius" value="200000"/>
<br/>
<input type="button" value="Grow Transplants" onclick="script:grow();"/>
</form>
</div>

<div id="visdiv" style="white-space: nowrap;"></div>
</body>
</html>"""%vars
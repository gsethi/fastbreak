#!/usr/bin/python
import os, glob
import cgi
import cgitb
cgitb.enable()

vars={'checkboxes':""}
files=[]
tr=""
lastfile = ""
for infile in glob.glob(os.path.join(os.getcwd(),'../data/*out')):
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
font: 10pt helvetica neue;
padding-left: 40px;
color: #666;
}
input {
font: 10pt helvetica neue;
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
loadthese=[]

function checkallf()
{
	val = document.getElementById("checkallb").checked;
	for( i in filenames)
	{
		document.getElementById(filenames[i]).checked = val;
	}
}

function log(msg)
{
	if(window.console && console.debug)
	{
		console.log(msg)
	}
}

function grow()
{
	loadthese=[]
	document.getElementById('visdiv').innerHTML="<div id='legenddiv'></div><br/>";
	
	document.getElementById('visdiv').innerHTML+="<table><tr>";
	for (var i in filenames)
	{
		if(document.getElementById(filenames[i]).checked)
		{
			document.getElementById('visdiv').innerHTML+="<td>"+filenames[i]+":<br/><div id='"+filenames[i]+"div' ><center><img src='../ajax-loader.gif'/><\/center><\/div><\/td>";
			if(filenames[parseInt(i)+1]!=undefined && filenames[i].substring(0,13)!=filenames[parseInt(i)+1].substring(0,13))
				document.getElementById('visdiv').innerHTML+="<\/tr><\/table><br/><table><tr>"
			loadthese.push(filenames[i])
		}
	}
	document.getElementById('visdiv').innerHTML+="</tr></table>";
	org.systemsbiology.visualization.transplant.colorkey(org.systemsbiology.visualization.transplant.chrmcolors.human,document.getElementById('legenddiv'));
	loadNext();
			
}

function handleResponse(response)
{
	
	log("response recieved");
	if (response.isError()) {
    	alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    	return;
  	}
  	var data = response.getDataTable();
  	log("data table created");
  	var vis = new org.systemsbiology.visualization.transplant(document.getElementById(loadthese[0]+'div'));
  	log("vis created");
	google.visualization.events.addListener(vis, 'select', function () { log("selection event"); vis.recenter(vis.getSelection()); } );
	vis.draw(data,{chr:document.getElementById('chr').value, start:document.getElementById('start').value, end:document.getElementById('end').value, radius:document.getElementById('radius').value, dataservice:'transplantws.py?file='+loadthese[0] });
	log("vis drawn");
	loadthese.shift();
	loadNext();

}


function loadNext()
{
	if (loadthese.length == 0)
		return;
	var query = new google.visualization.Query('transplantws.py?chr='+document.getElementById('chr').value+'&start='+document.getElementById('start').value+'&end='+document.getElementById('end').value+'&depth='+document.getElementById('depth').value+'&radius='+document.getElementById('radius').value+'&file='+loadthese[0]);
	query.send(function(re){handleResponse(re);});
}


</script>
<style>
body { margin: 30px; text-align: left; white-space: nowrap;}

</style>

</head>

<body>
<form>
Data Files:<br/>
<input type="checkbox" id="checkallb" onchange = "script:checkallf();" /> Check All
<div style="width:95%%;height:300;overflow:auto;border:2px grey solid;">
%(checkboxes)s
</div>
<br/>Root:<br/>
Chr:<input type='text' id="chr" value="chr1"/>
Start:<input type='text' id="start" value="12000000"/>
End:<input type='text' id="end" value="14000000"/><br/>
Search:<br/>
Depth:<input type='text' id="depth" value="4"/>
Radius:<input type='text' id="radius" value="1000000"/>
<br/>
<input type="button" value="Grow Transplants" onclick="script:grow();"/>
</form>

<div id="visdiv" style="white-space: nowrap;"></div>
</body>
</html>"""%vars
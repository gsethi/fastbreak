var TransplantParameters = Class.create({
    initialize: function(){
        this.widthfield = "5";
        this.radius = "400000";
        this.branchdepth="3";
        this.includeITX=true;
        this.includeCTX=false;
        this.itxMinScore = "0";
        this.ctxMinScore = "80";
        this.win = null;
        this.listeners = [];

    },

    addListener: function(listener){
             this.listeners[this.listeners.length] = listener;
    },

    publishParameterSelection: function(parameters){
        this.listeners.each(function(listener){
            listener.onParameterSelection(parameters);
        })
    },

    show: function(){
        var control = this;
        var breakpointdata = [["5","Number of Reads"],["7","Score"],["false","No decoration"]];
        var comboBreakPointData = new Ext.form.ComboBox({
             fieldLabel: 'Use Data Field',
                    xtype: 'combo',
                    store: breakpointdata,
                    forceSelection: true,
                    triggerAction: 'all',
//                    listeners:{
//                        'afterrender': function(item){
//
//                        }
//                    }
                    selectOnFocus: true,
                    ref: '../breakwidth',
                    autoSelect: true
        });

        var parameterForm = new Ext.FormPanel({
            labelWidth: 75,
            frame: true,
            bodyStyle: 'padding:5px 5px 0',
            width: 400,

            items: [{
                xtype: 'fieldset',
                title: 'Break Point Width',
                autoHeight: true,
                items:[comboBreakPointData]
            },{
                xtype: 'fieldset',
                title: 'Tree Parameters',
                autoHeight: true,
                itemId: 'treeParameters',
                items:[{
                    xtype: 'textfield',
                    fieldLabel: 'Maximum Branch Depth',
                    ref: '../branchDepth',
                    value: 3
                },{
                    xtype: 'textfield',
                    fieldLabel: 'Search Radius',
                    ref: '../searchradius',
                    value: 400000
                },{
                    layout: 'column',
                    itemId: 'columnValues',
                    items:[{
                        columnWidth: .5,
                        layout: 'form',
                        items:[{
                            xtype: 'checkbox',
                            fieldLabel: 'Include ITX',
                            ref: '../../../includeitx',
                            anchor: '95%',
                            checked: true
                        },{
                            xtype: 'checkbox',
                        fieldLabel: 'Include CTX',
                        ref: '../../../includectx',
                        anchor: '95%',
                        checked: false

                    }]
                },{columnWidth: .5,
                    layout: 'form',
                        itemId:'minScores',
                    items:[{
                        xtype: 'textfield',
                        fieldLabel: 'Minimum Score',
                        ref: '../../../itxminscore',
                        anchor: '95%',
                        value: '0'
                    },{
                        xtype: 'textfield',
                        fieldLabel: 'Minimum Score',
                        ref: '../../../ctxminscore',
                        anchor: '95%',
                        value: '80'
                    }]
                }]
                }]
            }],
            buttons:[{
                text: 'Submit',
                handler: function(){
                    if(parameterForm.getForm().isValid())
                    {
                         control.branchdepth = parameterForm.branchDepth.getValue();
                         control.ctxMinScore = parameterForm.ctxminscore.getValue();
                         control.includeCTX = parameterForm.includectx.getValue();
                        control.includeITX = parameterForm.includeitx.getValue();
                        control.itxMinScore = parameterForm.itxminscore.getValue();
                        control.radius = parameterForm.searchradius.getValue();
                        control.widthfield = parameterForm.breakwidth.getValue();
                        control.publishParameterSelection(control);
                         control.win.close();
                    }
                }
            }]

        });


        control.win = new Ext.Window({
            autoWidth: true,
            autoHeight: true,
            title: 'Visualization Parameters',
            items: parameterForm,
            frame: true
        });
        control.win.show();


    }
});





var TransplantVisualization = Class.create({
    initialize: function(container, refgenUri, coverageDatasourceUri,chromRangeUri){
        this.container = $(container);
        this.refgenUri = refgenUri;
        this.coverageDatasourceUri = coverageDatasourceUri;
        this.advParameters = new TransplantParameters();
        this.patients = new Array();
        this.chromosomeRange = chromRangeUri;
        this.parameterschanged = false;
        this.patientchanged = false;
        this.rangechanged = false;
        this.transplants=[];
        this.locationhistory=[];
       

    },

    onPatientSelection: function(patientArray){
        var control = this;
        control.patients = patientArray;
        control.patientchanged = true;
      //  if(patientArray.length > 0 && control.chromosomeRange != '')
      //  {
      //      control.loadVisualizationForSelectedPatients();
      //  }
    },

    onRangeSelection: function(chromRangeUri){
        var control = this;
        control.chromosomeRange = chromRangeUri;
        control.rangechanged = true;

       // if(control.patients.length > 0 && control.chromosomeRange != '')
      //  {
       //     control.loadVisualizationForSelectedPatients();
      //  }
    },

    onParameterSelection: function(parameters){
        var control = this;
        control.advParameters = parameters;
        control.parameterschanged = true;
        control.loadVisualizationForSelectedPatients();
    },


    onGeneSelection: function(geneSymbol){
        //do nothing for now....will be triggered with range selection

    },


    loadVisualizationForSelectedPatients: function () {
        var control = this;
        if(control.patients.length == 0 || control.chromosomeRange == '')
        {
            control.container.innerHTML="<p><b>A chromosome range and set of patients must be selected to view visualizations.</b></p>";
            return;
        }
        if(!control.rangechanged && !control.patientchanged && !control.parameterschanged){
            return;
        }

        //reloading the visualization, reset the array of visualizations
        control.transplants=[];
    
    var compAN = function (a,b)
    {
           a= a.toLowerCase();
           b= b.toLowerCase();
         if (a < b) //sort string ascending
              return -1
        if (a > b)
             return 1
         return 0 //default return value (no sorting)
     }

    var sortpatientorsample = function(a,b)
    {
        compAN(a.classification,b.classification);
       }
    control.patients = control.patients.sort(sortpatientorsample);

    var html = "";
    var transplantws = "/addama/tools/breakpoint";

        var rangeItems = control.chromosomeRange.split("/");
        var chr = rangeItems[0];
        var start = rangeItems[1];
        var end = rangeItems[2];
    html = '';

    $A(control.patients).each(function(p) {
        html+="<table><tr><td>"+p.id+"<br/>"+p.classification+"<br/>"+p.comments+"</td>";
        p.samples=p.samples.sort(sortpatientorsample);
        for(var i=0;i<p.samples.length; i++)
        {
            var s = p.samples[i];
            html+="<td class='outlined'>"+s.id+" "+s.classification+"<br/><div id='" + s.id +"div'></div></td>";
            var filters = JSON.stringify(control.getfilters());
            //var query = new google.visualization.Query(transplantws+'?key='+apiKey+'&filters='+filters+'&chr='+document.getElementById('chr').value+'&start='+document.getElementById('start').value+'&end='+document.getElementById('end').value+'&depth='+document.getElementById('depth').value+'&radius='+document.getElementById('radius').value+'&file='+s.pickleFile);
            var query = new google.visualization.Query(transplantws+'?chr='+chr+'&start='+start+'&end='+end+'&depth=' + control.advParameters.branchdepth + '&radius=' + control.advParameters.radius + '&file='+s.pickleFile);
            query.send(control.getVisResponseHandler(s.id,s.pickleFile,transplantws,control.refgenUri,control.coverageDatasourceUri));
        }
        html += "</tr></table>";
        //html += "<div>" + Ext.encode(p) + "</div>";
    });
    control.container.innerHTML=html;
   // org.systemsbiology.visualization.transplant.colorkey(org.systemsbiology.visualization.transplant.chrmcolors.human,document.getElementById('legenddiv'));
},

getVisResponseHandler: function(id,file,transplantws,genedatasource,trackds)
{
    var control = this;
    return function(resp){ control.visResponseHandler(resp,id,file,transplantws,genedatasource,trackds);}
},

visResponseHandler: function(response,id,file,transplantws,genedatasource,trackds)
{
    var control = this;
        if (response.isError()) {
            alert("Error in query: " + response.getMessage() + " " + response.getDetailedMessage());
            return;
        }
        var data = response.getDataTable();
        //log("data table created");
        var div = document.getElementById(id+"div");
        var vis = new org.systemsbiology.visualization.transplant(div);

                var rangeItems = control.chromosomeRange.split("/");
        var chr = rangeItems[0];
        var start = rangeItems[1];
        var end = rangeItems[2];
        control.transplants.push(vis);

        google.visualization.events.addListener(vis, 'select', control.getSelectionHandler(vis) );
        google.visualization.events.addListener(vis, 'recenter', control.getRecenterListener(vis) );
        var filters = control.getfilters();
        vis.draw(data,{
            trackds:trackds,
            sample_id:id,
            widthfield:control.advParameters.widthfield,
            //filters:filters,
            chr:chr,
            depth:control.advParameters.branchdepth,
            start:start,
            end:end,
            radius:control.advParameters.radius,
            dataservice:transplantws+"?file="+file,
            refgenomeUri: control.refgenUri
        });
},

getRecenterListener: function(vis)
{
    var control = this;
	return function (loc) {
	//	log("recenter event");
		control.locationhistory.push(loc);
	//	document.getElementById('chr').value = loc.chr;
	//	document.getElementById('start').value = loc.start;
	//	document.getElementById('end').value = loc.end;
        control.onRangeSelection(loc.chr + '/' + loc.start + '/' + loc.end);
		for(var i in control.transplants)
		{
			if(control.transplants[i]!=vis)
				control.transplants[i].recenteronlocation(loc.chr,loc.start,loc.end);
		}
	}

},

getSelectionHandler: function(vis)
{
    var control = this;
	return function () {
		//log("selection event");
		var loc = vis.recenteronrow(vis.getSelection());
		control.locationhistory.push(loc);
	//	document.getElementById('start').value = loc.start;
	//	document.getElementById('end').value = loc.end;
        control.onRangeSelection(loc.chr + '/' + loc.start + '/' + loc.end);
		for(var i in control.transplants)
		{
			if(control.transplants[i]!=vis)
				control.transplants[i].recenteronlocation(loc.chr,loc.start,loc.end);
		}
	}

},

getfilters: function(){

    var control = this;
        var filters = [];
            if(control.advParameters.includeITX) {
                filters.push({type:"ITX",minscore:control.advParameters.itxMinScore});
            }
            if(control.advParameters.includeCTX) {
                filters.push({type:"CTX",minscore:control.advParameters.ctxMinScore});
            }

        return filters;

}
});

var TransplantParameters = Class.create({
    initialize: function() {
        this.widthfield = "5";
        this.radius = "400000";
        this.branchdepth = "3";
        this.includeSmall = true;
        this.includeOther = true;
        this.smallMinScore = "98";
        this.otherMinScore = "98";
        this.win = null;
        this.listeners = [];

    },

    addListener: function(listener) {
        this.listeners[this.listeners.length] = listener;
    },

    publishParameterSelection: function(parameters) {
        this.listeners.each(function(listener) {
            listener.onParameterSelection(parameters);
        })
    },

    show: function() {
        var control = this;
        var breakpointdata = [
            ["5","Number of Reads"],
            ["7","Score"],
            ["false","No decoration"]
        ];
        var comboBreakPointData = new Ext.form.ComboBox({
            fieldLabel: 'Use Data Field',
            xtype: 'combo',
            store: breakpointdata,
            forceSelection: true,
            triggerAction: 'all',
            listeners:{
                render: function(item){
                    item.setValue(control.widthfield);
                }
            },
            selectOnFocus: true,
            ref: '../breakwidth',
            autoSelect: true
        });

        var parameterForm = new Ext.FormPanel({
            frame: true,
            bodyStyle: 'padding:5px 5px 0',
            width: 500,
            items: [
                {
                    xtype: 'fieldset',
                    title: 'Break Point Width',
                    autoHeight: true,
                    items:[comboBreakPointData]
                },
                {
                    xtype: 'fieldset',
                    title: 'Tree Parameters',
                    autoHeight: true,
                    itemId: 'treeParameters',
                    items:[
                        {
                            layout: 'column',
                            padding: '5 5 5 5',
                            items:[
                                {
                                    columnWidth: .5,
                                    layout: 'form',
                                    items:[
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Maximum Branch Depth',
                                            ref: '../../../branchDepth',
                                            value: control.branchdepth,
                                            anchor: '95%'
                                        }
                                    ]
                                },
                                {
                                    columnWidth: .5,
                                    layout: 'form',
                                    items:[
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Search Radius',
                                            ref: '../../../searchradius',
                                            value: control.radius,
                                            anchor: '95%'
                                        }
                                    ]
                                }
                            ]}
                    ]},
                {
                    xtype: 'fieldset',
                    title: 'Include Breakpoints Found By',
                    items:[
                        {
                            layout: 'column',
                            padding: '5 5 5 5',
                            itemId: 'columnValues',
                            items:[
                                {
                                    columnWidth: .5,
                                    layout: 'form',
                                    items:[
                                        {
                                            xtype: 'checkbox',
                                            fieldLabel: 'Distance',
                                            ref: '../../../includesmall',
                                            anchor: '95%',
                                            checked: control.includeSmall
                                        },
                                        {
                                            xtype: 'checkbox',
                                            fieldLabel: 'Orientation or Chromosome',
                                            ref: '../../../includeother',
                                            anchor: '95%',
                                            checked: control.includeOther
                                        }
                                    ]
                                },
                                {columnWidth: .5,
                                    layout: 'form',
                                    itemId:'minScores',
                                    items:[
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Minimum Score',
                                            ref: '../../../smallminscore',
                                            anchor: '95%',
                                            value: control.smallMinScore
                                        },
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Minimum Score',
                                            ref: '../../../otherminscore',
                                            anchor: '95%',
                                            value: control.otherMinScore
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            buttons:[
                {
                    text: 'Submit',
                    handler: function() {
                        if (parameterForm.getForm().isValid())
                        {
                            control.branchdepth = parameterForm.branchDepth.getValue();
                            control.otherMinScore = parameterForm.otherminscore.getValue();
                            control.includeOther = parameterForm.includeother.getValue();
                            control.includeSmall = parameterForm.includesmall.getValue();
                            control.smallMinScore = parameterForm.smallminscore.getValue();
                            control.radius = parameterForm.searchradius.getValue();
                            control.widthfield = parameterForm.breakwidth.getValue();
                            control.publishParameterSelection(control);
                            control.win.close();
                        }
                    }
                }
            ]

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
    initialize: function(container, refgenUri, coverageDatasourceUri, chromRangeUri) {
        this.container = $(container);
        this.refgenUri = refgenUri;
        this.coverageDatasourceUri = coverageDatasourceUri;
        this.advParameters = new TransplantParameters();
        this.patients = new Array();
        this.chromosomeRange = chromRangeUri;
        this.parameterschanged = false;
        this.patientchanged = false;
        this.rangechanged = false;
        this.transplants = [];
        this.locationhistory = [];
        this.options = {};
        this.options.div_width = 550;
        this.options.div_height = 350;


    },

    onPatientSelection: function(patientArray) {
        var control = this;

        function objectsAreSame(x, y) {
            var objectsAreSame = false;
            var match = 0;
            for (i in x) {
                for (j in y) {
                    if (i['id'] == j['id']) {
                        match++;
                    }
                }
            }
            if (x.length == match && y.length == match) {
                objecstAreSame = true;
            }
            return objectsAreSame;
        }

        if (!objectsAreSame(patientArray, control.patients)) {
            control.patients = patientArray;

            control.patientchanged = true;
        }

        //  if(patientArray.length > 0 && control.chromosomeRange != '')
        //  {
        //      control.loadVisualizationForSelectedPatients();
        //  }
    },

    onRangeSelection: function(chromRangeUri) {
        var control = this;
        if (chromRangeUri != control.chromosomeRange) {
            control.chromosomeRange = chromRangeUri;
            control.rangechanged = true;
        }

        // if(control.patients.length > 0 && control.chromosomeRange != '')
        //  {
        //     control.loadVisualizationForSelectedPatients();
        //  }
    },

    onParameterSelection: function(parameters) {
        var control = this;
        control.advParameters = parameters;
        control.parameterschanged = true;
        control.loadVisualizationForSelectedPatients();
    },


    onGeneSelection: function(geneSymbol) {
        //do nothing for now....will be triggered with range selection

    },


    loadVisualizationForSelectedPatients: function () {
        var control = this;
        if (control.patients.length == 0 || control.chromosomeRange == '' || control.chromosomeRange == undefined)
        {
            control.container.innerHTML = "<p><b>A chromosome range and set of patients must be selected to view visualizations.</b></p>";
            return;
        }
        if (!control.rangechanged && !control.patientchanged && !control.parameterschanged) {
            return;
        }

        control.rangechanged = false;
        control.patientchanged = false;
        control.parameterschanged = false;

        //reloading the visualization, reset the array of visualizations
        control.transplants = [];

        var compAN = function (a, b)
        {
            a = a.toLowerCase();
            b = b.toLowerCase();
            if (a < b) //sort string ascending
                return -1
            if (a > b)
                return 1
            return 0 //default return value (no sorting)
        }

        var sortpatientorsample = function(a, b)
        {
            compAN(a.classification, b.classification);
        }
        control.patients = control.patients.sort(sortpatientorsample);

        var html = "";
        var transplantws = "/simple-proxy-svc/addama/tools/breakpoint";

        var rangeItems = control.chromosomeRange.split("/");
        var chr = rangeItems[0];
        var start = rangeItems[1];
        var end = rangeItems[2];
        html = '';
        control.query_array = [];
        control.response_array = [];

        $A(control.patients).each(function(p) {
            html += "<table><tr><td>" + p.id + "<br/>" + p.classification + "<br/>" + p.comments + "</td>";
            p.samples = p.samples.sort(sortpatientorsample);
            for (var i = 0; i < p.samples.length; i++)
            {
                var s = p.samples[i];
                html += "<td class=\'outlined\'>" + s.classification + "<br/><div id=\'" + s.id + "div\' style=\"" +
                        "width: " + control.options.div_width + "; height: " + control.options.div_height + ";\"></div></td>";
                var filters = control.getfilters().toJSON();
                //var query = new google.visualization.Query(transplantws+'?key='+apiKey+'&filters='+filters+'&chr='+document.getElementById('chr').value+'&start='+document.getElementById('start').value+'&end='+document.getElementById('end').value+'&depth='+document.getElementById('depth').value+'&radius='+document.getElementById('radius').value+'&file='+s.pickleFile);

                var query = new google.visualization.Query(transplantws + '?filters=' + filters + '&chr=' + chr + '&start=' + start + '&end=' + end + '&depth=' + control.advParameters.branchdepth + '&radius=' + control.advParameters.radius + '&file=' + s.pickleFile);
                //            control.query_array.push({'query':query,'sample':s,'transplantws':transplantws});
                query.send(control.getVisResponseHandler(s.id, s.pickleFile, transplantws, control.refgenUri, control.coverageDatasourceUri));

            }
            html += "</tr></table>";
            //html += "<div>" + Ext.encode(p) + "</div>";
        });
        control.container.innerHTML = html;
        //       this.distributeQueries();
        // org.systemsbiology.visualization.transplant.colorkey(org.systemsbiology.visualization.transplant.chrmcolors.human,document.getElementById('legenddiv'));
    },

    distributeQueries: function() {
        for (var i = 0; i < 1; i++) {
            if (this.query_array.length < 1) {
                return;
            }
            var query_obj = this.query_array.shift();
            var query = query_obj.query;
            var s = query_obj.sample;
            var transplantws = query_obj.transplantws;
            $(s.id + "div").innerHTML = "Loading...";
            query.send(this.getVisResponseHandler(s.id, s.pickleFile, transplantws, this.refgenUri, this.coverageDatasourceUri));

        }
    },

    getVisResponseHandler: function(id, file, transplantws, genedatasource, trackds)
    {
        var control = this;
        return function(resp) {
            control.visResponseHandler(resp, id, file, transplantws, genedatasource, trackds);
        }
    },

    visResponseHandler: function(response, id, file, transplantws, genedatasource, trackds)
    {
        var control = this;
        control.response_array.push(id);
        if (control.response_array.length >= 1) {
            control.response_array = [];
            control.distributeQueries();
        }
        if (response.isError()) {
            alert("Error in query: " + response.getMessage() + " " + response.getDetailedMessage());
            return;
        }
        var data = response.getDataTable();
        //log("data table created");
        var div = document.getElementById(id + "div");
        var vis = new org.systemsbiology.visualization.transplant(div);

        var rangeItems = control.chromosomeRange.split("/");
        var chr = rangeItems[0];
        var start = rangeItems[1];
        var end = rangeItems[2];
        control.transplants.push(vis);

        google.visualization.events.addListener(vis, 'select', control.getSelectionHandler(vis));
        google.visualization.events.addListener(vis, 'recenter', control.getRecenterListener(vis));
        var filters = control.getfilters().toJSON();
        vis.draw(data, {
            trackds:trackds,
            sample_id:id,
            widthfield:control.advParameters.widthfield,
            filters:filters,
            width: control.options.div_width,
            height: control.options.div_height,
            chr:chr,
            depth:control.advParameters.branchdepth,
            start:start,
            end:end,
            radius:control.advParameters.radius,
            dataservice:transplantws + "?file=" + file,
            refgenomeUri: control.refgenUri
        });
    },

    getRecenterListener: function(vis)
    {
        var control = this;
        return function (loc) {

            google.visualization.events.trigger(control, 'rangeSelect', {chr:loc.chr.substring(3),start:loc.start,end:loc.end,gene:loc.gene,cancel_bubble: true});
            //	log("recenter event");
            control.locationhistory.push(loc);
            control.onRangeSelection(loc.chr + '/' + loc.start + '/' + loc.end);
            for (var i in control.transplants)
            {
                if (control.transplants[i] != vis)
                    control.transplants[i].recenteronlocation(loc.chr, loc.start, loc.end);
            }
        }


    },

    getSelectionHandler: function(vis)
    {
        var control = this;
        return function () {
            //log("selection event");
            var loc = vis.recenteronrow(vis.getSelection());
            google.visualization.events.trigger(control, 'rangeSelect', {chr:loc.chr.substring(3),start:loc.start,end:loc.end,gene:null,cancel_bubble: true});
            control.locationhistory.push(loc);
            control.onRangeSelection(loc.chr + '/' + loc.start + '/' + loc.end);
            for (var i in control.transplants)
            {
                if (control.transplants[i] != vis)
                    control.transplants[i].recenteronlocation(loc.chr, loc.start, loc.end);
            }
        }
    },

    getfilters: function() {

        var control = this;
        var filters = [];
        if (control.advParameters.includeSmall) {
            filters.push({type:"small",minscore:control.advParameters.smallMinScore});
        }
        if (control.advParameters.includeOther) {
            filters.push({type:"other",minscore:control.advParameters.otherMinScore});
        }

        return filters;

    }
});

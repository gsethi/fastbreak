var referenceGenomeChromosomes = null;

function renderResultParameters(node, divContainer){
    workspaceUri = node.attributes.datasetUri;
    trackUri = workspaceUri + "/track.tsv";

    var tb = new Ext.Toolbar();
        tb.add({
            text: 'Submit',
            handler: onItemClick,
            hiddenName: node.attributes.text,
            cls: "x-btn-text-icon",
            pressed: false,
            buttonAlign: 'right'
        });

    var patientsDiv = createDiv(node.attributes.text + ".patientsDiv");
    var coordinatesDiv = createDiv(node.attributes.text + ".coordinatesDiv");
    var advancedDiv = createDiv(node.attributes.text + ".advancedDiv");

    $(divContainer.id).appendChild(patientsDiv);
    $(divContainer.id).appendChild(coordinatesDiv);
    $(divContainer.id).appendChild(advancedDiv);

    var parametersPanel = new Ext.Panel({
        frame: true,
        width: 900,
        height: 600,
        margins: '5 0 5 5',
        split: true,
        layout: 'accordion',
        title: 'Parameter Settings',
        renderTo: divContainer.id,
        items: [{
            title: 'Patient Selection',frame: true,contentEl: patientsDiv.id
        },{
            title: 'Coordinates Selection',frame: true,contentEl: coordinatesDiv.id
        },{
            title: 'Advanced Options',frame: true,contentEl: advancedDiv.id
        }],
        tbar: tb

    });

    loadPatients(node,workspaceUri, patientsDiv);
    loadReferenceGenomesChromosomes(node,coordinatesDiv,renderGeneSelectionForm);
    renderTreeParameterForm(advancedDiv);

}
function loadReferenceGenomesChromosomes(node,divContainer,callback) {
    new Ajax.Request("/addama/refgenome/hg18", {
        method:"get",
        onSuccess:function(o) {
            var json = o.responseJSON;
            if (json && json.items) {
                referenceGenomeChromosomes = json.items;
                callback(node,divContainer);
            }
        }
    })
}

function loadPatients(node,workspaceUri, divContainer,containerTab,callback) {
    new Ajax.Request(workspaceUri + "/patients.json", {
        method: "get",
        onSuccess: function(o) {
            var json = Ext.decode(o.responseText, true);
            if (json && json.patients) {
                var patientsArray = new Array();

                var patients = json.patients;
                var i=0;
                $A(patients).each(function(patient) {
                    if (patient.samples) {
                        var samples = patient.samples;
                        $A(samples).each(function(sample) {
                           var patientArray = new Array();
                            patientArray[0]=patient.id;
                            patientArray[1] = sample.id;
                            patientArray[2] = sample.classification;
                             patientsArray[i]=patientArray;
                            i++;
                        });

                    }


                });

               var arrayReader = new Ext.data.ArrayReader({
                   fields: ['patientid','sampleid','sampleclassification']
               });
               var sm = new Ext.grid.CheckboxSelectionModel();
               var ds = new Ext.data.GroupingStore({
                   reader: arrayReader,
                   data: patientsArray,
                   groupField: 'patientid'
               });

                var grid = new Ext.grid.GridPanel({
                    store: ds,
                    columns: [
                        sm,
                        {header: "Patient", dataIndex: 'patientid', sortable: true},
                        {header: "Sample ID", dataIndex: 'sampleid', sortable: true},
                        {header: "Sample Classification", dataIndex: 'sampleclassification', sortable: true}
                    ],
                    width:400,
                    height:200,
                    frame: true,
                    sm: sm,
                    view: new Ext.grid.GroupingView({
                        forceFit: true,
                        groupTextTpl: '{text}'
                    }),
                    renderTo: divContainer.id

                });

            }
        }
    });

}

function renderGeneSelectionForm(node,divContainer){

    var flexBarDiv = createDiv(node.attributes.text + ".flexBar");
        flexBarDiv.style.height = "50px";
    $(divContainer.id).appendChild(flexBarDiv);

    var chromDropDownDiv = createDiv(node.attributes.text + ".chromDropDown");
    $(divContainer.id).appendChild(chromDropDownDiv);

    var searchFieldDiv = createDiv(node.attributes.text + ".searchField");
    $(divContainer.id).appendChild(searchFieldDiv);

    var startFieldDiv = createDiv(flexBarDiv.id + ".startField");
    $(flexBarDiv.id).appendChild(startFieldDiv);

    var endFieldDiv = createDiv(flexBarDiv.id + ".endField");
    $(flexBarDiv.id).appendChild(endFieldDiv);

     var refGenChrom = [];
    if (referenceGenomeChromosomes) {
        $A(referenceGenomeChromosomes).each(function(chrom) {
            refGenChrom[refGenChrom.length] = [chrom.uri, chrom.name];
        });
    };

    var chromDropDown = new Ext.form.ComboBox({
        store: new Ext.data.ArrayStore({
                                fields: ["uri", "label"],
                                data: refGenChrom
        }),
        renderTo: chromDropDownDiv.id,
        displayField: 'label',
        hiddenName: "refGenChrom",
        valueField: "uri",
        fieldLabel: "Chromosome",
        typeAhead: false,
        mode: 'local',
        forceSelection: true,
        triggerAction: 'all',
        emptyText: 'Select a chromosome...',
        selectOnFocus: true,
        width: 150,
        listeners: {
            select: function(cb,rec,index){
             loadFlexScroll(rec.data.uri, flexBarDiv);
            }
        }
    });


    //create geneSearch field
    var geneSearchField = new Ext.ux.form.SearchField({
        width: 100,
        renderTo: searchFieldDiv.id,
        fieldLabel: "Gene Search"
    });


    var startField = new Ext.form.TextField({
        width: 100,
        id: startFieldDiv.id + ".id",
        renderTo: startFieldDiv.id
    });

    var endField = new Ext.form.TextField({
        width: 100,
        id:  endFieldDiv.id + ".id",
        renderTo: endFieldDiv.id
    });

    //create panel to place all items in
    var panel = new Ext.form.FormPanel({
        frame: true,
        renderTo: divContainer.id,
        width: 800,
        items: [{fieldLabel: 'Chromosome', contentEl:chromDropDownDiv.id}, {fieldLabel: "Gene Search", contentEl: searchFieldDiv.id},
            { contentEl: flexBarDiv.id},{fieldLabel: "Start",contentEl: startFieldDiv.id},{fieldLabel: "End",contentEl: endFieldDiv.id}]
    });

}

function renderFlexScroll(scrollBarContainer,minPosition,maxPosition){
            document.getElementById(scrollBarContainer.id + ".startField.id").value   = minPosition;
         document.getElementById(scrollBarContainer.id + ".endField.id").value = maxPosition;

    var listener = function(x,dx){
        document.getElementById(scrollBarContainer.id + ".startField.id").value   = x;
         document.getElementById(scrollBarContainer.id + ".endField.id").value = parseInt(x) + parseInt(dx);

    }

    var flexbar = new org.systemsbiology.visualization.protovis.FlexScroll( scrollBarContainer, listener);

    var data ={DATATYPE : "org.systemsbiology.visualization.protovis.models.FlexScrollData", CONTENTS : "test"};


    var options = {plotWidth : 700, plotHeight: 50, dblclick_notifier: zoomScrollBar,
           verticalPadding : 10, horizontalPadding: 30, font :"sans", minPosition: Math.round(minPosition / 1000) ,
           maxPosition: Math.round(maxPosition / 1000), scaleMultiplier : 1000};

    flexbar.draw(data,options)


}

function zoomScrollBar(scrollBarContainer) {
            scrollBarContainer.innerHTML = "";
            renderFlexScroll(scrollBarContainer,$(scrollBarContainer.id + ".startField").value,$(scrollBarContainer.id + ".endField").value);
}

function loadFlexScroll(chromUri, flexBarDiv){
        new Ajax.Request(chromUri, {
                    method:"get",
                    onSuccess:function(o) {
                        var json = o.responseJSON;
                        if (json && json.length) {
                           renderFlexScroll(flexBarDiv,0,json.length);
                        }
                    }
                });
}
function createDiv(id){
     var divObj;
        try {
            divObj = document.createElement('<div>');
        } catch (e) {
        }
        if (!divObj || !divObj.name) { // Not in IE, then
            divObj = document.createElement('div')
        }
        if (id) divObj.id = id;

    return divObj;

}

function renderTreeParameterForm(divContainer){
    var treeParameters = new Ext.Panel({
        frame: true,
        autoWidth: true,
        autoHeight: true,
        contentEl: 'container_parameters',
        renderTo: divContainer.id
    });

}





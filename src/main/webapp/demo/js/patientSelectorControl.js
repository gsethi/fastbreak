var PatientSelectorControl = Class.create({
    initialize: function(container,workspaceUri){
        this.container = $(container);
        this.workspaceUri = workspaceUri;
        this.selectedPatients = new Array();
        this.selectionListeners = new Array();
        this.patients = new Array();
        this.loadPatients();

    },

    loadPatients: function(){
        var control = this;

        new Ajax.Request(this.workspaceUri + "/patients.json", {
            method: "get",
            onSuccess: function(o) {
                var json = Ext.decode(o.responseText, true);
                if (json && json.patients) {
                    control.patients = json.patients;
                }
                control.loadControl();
            }
        });      
    },

    loadControl: function(){
         var control = this;
        //go thru and put patient info into array
                   var i=0;
                    var patientsArray = new Array();
                    var newJson = [];

                    $A(control.patients).each(function(patient) {
                        var patientArray = new Array();
                        patientArray[0] = patient.id;
                        patientArray[1] = "";
                        patientArray[2] = "";
                        patientArray[3] = patient;
                        patientArray[4] = false;
                        patientsArray[i]=patientArray;
                        var patientJson = {"patientid": patient.id, "patient": patient, "sampleclassification": '', "sampleid": '', "expanded" : true, "text": patient.id, "checked": true, "children":[]};

                        i++;
                        if (patient.samples) {
                            var samples = patient.samples;
                            $A(samples).each(function(sample) {
                                patientArray = new Array();
                                patientArray[0]=patient.id;
                                patientArray[1] = sample.id;
                                patientArray[2] = sample.classification;
                                patientArray[3] = "";
                                patientsArray[i]=patientArray;
                                var sampleJson = {"patientid": '', "patient": {}, "sampleclassification": sample.classification, "sampleid": sample.id, "leaf": true};
                                patientJson.children[patientJson.children.length] = sampleJson;

                                i++;

                            });
                        }

                         newJson[newJson.length] = patientJson;

                    });



         var tree2 = new Ext.ux.tree.TreeGrid({
width: 500,
height: 300,
             itemId: 'patientGrid',
renderTo: $('container_tree'),
enableDD: true,
columns:[{
header: 'Patient',
dataIndex: 'patientid',
width: 200
},{
header: 'Sample Id',
dataIndex: 'sampleid',
width: 300
},{
header: 'Sample Classification',
width: 100,
dataIndex: 'sampleclassification'
}]
});




var root = new Ext.tree.AsyncTreeNode({text:'patienttree',draggable:false,id:'source',children: newJson});

tree2.setRootNode(root);
tree2.render();
root.expand(false, false);
     //   loadPatientTree(control.workspaceUri,$('container_tree'),function(){});
        var fpPatients = new Ext.FormPanel({
                    frame: true,
                    layout: 'fit',
                    buttonAlign: 'center',
                    items: tree2,
                    renderTo: $(control.container),
                    buttons: [{
                        text: 'Submit',
                        handler: function(){
                            if(fpPatients.getForm().isValid())
                            {
                                control.selectedPatients = new Array();
                                fpPatients.getComponent('patientGrid').getChecked().each(function(rec){
                                    control.selectedPatients[control.selectedPatients.length] = rec.attributes.patient;

                                });

                              control.publishPatientSelection(control.selectedPatients);

                            }
                        }
                    }]
                });


    },


    addSelectionListener: function(listener){
             this.selectionListeners[this.selectionListeners.length] = listener;
    },

    publishPatientSelection: function(patients){
        this.selectionListeners.each(function(listener){
            listener.onPatientSelection(patients);
        })
    },

    publishPatientsLoaded: function(){
        this.selectionListeners.each(function(listener){
            listener.onPatientsLoaded();
        })
    }
})

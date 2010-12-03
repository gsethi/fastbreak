var PatientSelectorControl = Class.create({

    initialize: function(workspaceUri,loadedcallback,selpatientscallback){
        this.patientGrid = null;
        this.loadedCallback = loadedcallback;
        this.selpatientsCallback = selpatientscallback;
        this.workspaceUri = workspaceUri;
        this.loadPatients();
        this.selectedPatients = new Array();

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
                    var newJson = [];

                    $A(control.patients).each(function(patient) {
                        var patientJson = {"patientid": patient.id, "patientclassification": patient.classification, "status": patient.status, "resistance": patient.resistance, "patient": patient};

                         newJson[newJson.length] = patientJson;

                    });

        var rootJson = {"data":newJson};

        var patientReader = new Ext.data.JsonReader({
               idProperty: 'patientid',
               root: 'data',
               fields: [{
                   name: 'patientid'
               }, {
                   name: 'patientclassification'
               },  {
                   name: 'status'
               },  {
                   name: 'resistance'
               }, {
                   name: 'patient'
               }]
        });

        var groupingstore = new Ext.data.GroupingStore({
            reader: patientReader,
            data: rootJson,
            sortInfo: {
                   field: 'patientid',
                   direction: 'ASC'
            },
            groupField: 'patientclassification'
        });

        //initialize the store now that we have the json
        var patientstore = new Ext.data.JsonStore({
               // store configs
               autoDestroy: true,
               data: rootJson,
               remoteSort: false,
               sortInfo: {
                   field: 'patientid',
                   direction: 'ASC'
               },
               storeId: 'patientStore',
               // reader configs
               idProperty: 'patientid',
               root: 'data',
               fields: [{
                   name: 'patientid'
               }, {
                   name: 'patientclassification'
               },  {
                   name: 'status'
               },  {
                   name: 'resistance'
               }, {
                   name: 'patient'
               }]
           });




var filters = new Ext.ux.grid.GridFilters({
        // encode and local configuration options defined previously for easier reuse
        encode: false, // json encode the filter query
        local: true,   // defaults to false (remote filtering)
        filters: [{
            type: 'string',
            dataIndex: 'patientid'
        },  {
            type: 'list',
            dataIndex: 'patientclassification',
            options: ['OVARIAN','GBM']
        }, {
            type: 'list',
            dataIndex: 'status',
            options: ['NA','DECEASED','LIVING']
        }, {
            type: 'list',
            dataIndex: 'resistance',
            options: ['NA','FALSE','PRIMARY-RESISTANCE','SENSITIVE']
        }]
    });


// use a factory method to reduce code while demonstrating
        // that the GridFilter plugin may be configured with or without
        // the filter types (the filters may be specified on the column model
        var sm = new Ext.grid.CheckboxSelectionModel({
            listeners: {
            'rowselect': function(sm, rowIndex,record){
                selectedItems = sm.getSelections();
                control.selectedPatients = new Array();
                $A(selectedItems).each(function(item){
                    control.selectedPatients[control.selectedPatients.length]=item.json.patient;
                });
                control.selpatientsCallback(control.selectedPatients);
            },
            'rowdeselect': function(sm,rowIndex,record){
                selectedItems = sm.getSelections();
                control.selectedPatients = new Array();
                $A(selectedItems).each(function(item){
                    control.selectedPatients[control.selectedPatients.length]=item.json.patient;
                });
                control.selpatientsCallback(control.selectedPatients);
                
            }
        }
        });
        var createColModel = function (finish, start) {

            var columns = [
                sm,
                {
                dataIndex: 'patientid',
                header: 'Patient Id',
                // instead of specifying filter config just specify filterable=true
                // to use store's field's type property (if type property not
                // explicitly specified in store config it will be 'auto' which
                // GridFilters will assume to be 'StringFilter'
                filterable: true,
                width: 200
                //,filter: {type: 'numeric'}
            },  {
                dataIndex: 'patientclassification',
                header: 'Patient Classification',
                filterable: true,
                width: 150
            },  {
                dataIndex: 'status',
                header: 'Status',
                filter: {
                    type: 'list',
                    options: ['NA','LIVING','DECEASED']
                },
                width: 150
            },  {
                dataIndex: 'resistance',
                header: 'Resistance',
                filterable: true,
                width: 150
            }];

            return new Ext.grid.ColumnModel({
                columns: columns.slice(start || 0, finish),
                defaults: {
                    sortable: true,
                    width: 120
                }
            });
        };

         control.patientGrid = new Ext.grid.GridPanel({
        border: true,
        store: groupingstore,
        colModel: createColModel(5),
             columnLines: true,
             sm: sm,
             frame: true,
             iconCls:'icon-grid',
             stripeRows: true,
             height: 400,
             width: 700,
             title: 'Patients',
        loadMask: true,
        view: new Ext.grid.GroupingView({
            forceFit: true,
            groupTextTpl: '{text} ({[values.rs.length]} {[values.rs.length > 1 ? "Items" : "Item"]})'
        }),
        plugins: [filters]
    });


        control.loadedCallback();

    }
})

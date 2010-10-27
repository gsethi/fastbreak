var fpUpload = null;
var fileWindow = null;
var fpAnalyze = null;

function renderCreateDatasetForm(uri) {
    fpUpload = new Ext.FormPanel({
        fileUpload: true,
        width: 400,
        frame: true,
        autoHeight: true,
        bodyStyle: 'padding: 10px 10px 0 10px;',
        method: 'POST',
        standardSubmit: true,
        items: [ {
            xtype: 'textfield',
            fieldLabel: "Label",
            name: "label",
            allowBlank:false,
            id:"datasetLabel"
        },{
            xtype: 'fileuploadfield',
            fieldLabel: 'Dataset'
        }],
        buttons: [{
            text: 'Upload',
            handler: function(){
                if(fpUpload.getForm().isValid()){
                    new Ajax.Request(uri + "/" + Ext.getDom("datasetLabel").value, {
                        method: "post",
                        onSuccess: function(o) {
                            workspaceUri = o.responseJSON.uri;
                            //now submit the file
                            submitFile();
                        },
                        onFailure: function(o,e) {
                            showError("Submit Dataset", e);
                        },
                        onException: function(o,e) {
                            showError("Submit Dataset", e);
                        }
                    });
                }
            }
        }]
    });

    fileWindow = new Ext.Window({
            width:400,
            autoHeight:true,
            title: 'Create New Dataset',
            items: fpUpload,
            frame: true
        }).show();
}

function submitFile() {
    new Ajax.Request(workspaceUri + "/directlink", {
        method: "get",
        onSuccess: function(o) {
            var json = o.responseJSON;
            if (json && json.location) {
                fpUpload.getForm().url = json.location;
                fpUpload.getForm().submit({
                    waitMsg: 'Uploading your file...',
                    onSuccess: function(fp, o){

                        msg('Success', 'Processed file "'+o.result.file+'" on the server');
                    },
                    onFailure: function(fp,o,e){
                        showError("Upload File",e);

                    }

                });
                fileWindow.close();

                loadReferenceGenomes(function() {
                                renderAnalyzeWindow("/addama/repositories/workspaces/" + json.email);
                            });

            }
        },
        onFailure: function(o,e){
            fileWindow.close();
            showError("Upload File",e);
        },
        onException: function(o,e){
            fileWindow.close();
            showError("Upload File",e);
        }
    });
}

            function loadReferenceGenomes(callback) {
                new Ajax.Request("/addama/refgenome", {
                    method:"get",
                    onSuccess:function(o) {
                        var json = o.responseJSON;
                        if (json && json.items) {
                            referenceGenomes = json.items;
                            callback();
                        }
                    }
                })
            }

function renderAnalyzeWindow(){
     var refGenData = [];
    if (referenceGenomes) {
        $A(referenceGenomes).each(function(refGen) {
            refGenData[refGenData.length] = [refGen.uri, refGen.name];
        });
    }

     var fpAnalyze = new Ext.FormPanel({
                    frame: true,
                    width: 500,
                    buttonAlign: 'center',
                    items:[
                        new Ext.form.ComboBox({
                            fieldLabel: "Reference Genome",
                            hiddenName: "refgen",
                            store: new Ext.data.ArrayStore({
                                fields: ["uri", "label"],
                                data: refGenData
                            }),
                            allowBlank: false,
                            valueField:"uri",
                            displayField:"label",
                            typeAhead: false,
                            mode: "local",
                            triggerAction: "all",
                            emptyText:"Select a Reference Genome Build",
                            selectOnFocus:true,
                            width:190
                        }),
                        { xtype:'textfield',fieldLabel: "Filename", name: "filename", allowBlank:false, id:"filenameLabel" }
                    ],
                    buttons: [{
                        text: 'Process Dataset',
                        handler: function(){
                            referenceGenomeUri = Ext.getDom("refgen").value;
                            submitJob(referenceGenomeUri);
                        }
                    }]
                });

    fileWindow = new Ext.Window({
                    width: 400,
                    autoHeight:true,
                    title: 'Analyze Dataset',
                    items: fpAnalyze,
                    frame: true
                }).show();
}

function submitJob(referenceGenUri) {
    new Ajax.Request("/addama/tools/transplantdemo/workspace/jobs", {
        method: "post",
        parameters: {
            workspace: workspaceUri,
            referenceGenome: referenceGenUri
        },
        onSuccess: function(o) {
            fileWindow.close();
            Ext.MessageBox.show({
                title: 'Please wait',
                msg: 'Processing job',
                width: 300,
                progress: true,
                closable: false,
                wait: true,
                waitConfig: {interval:200}
                
            });

             var ajaxUpd = new Ajax.PeriodicalUpdater("span_progress", o.responseJSON.uri, {
                    method: "get",
                    frequency: 3,
                    onSuccess: function(o) {
                        var json = o.responseJSON;
                        if (json && json.status) {
                            if (json.status == "completed") {
                                ajaxUpd.stop();
                                Ext.MessageBox.hide();
                                Ext.Msg.alert('Success','Job ran successfully');
                                loadDataSets(email, "container_userDataSets", centertabs,"User DataSets", "Public DataSets");
                            }
                        }
                    }
                });
        },
        onFailure: function(o, e) {
            fileWindow.close();
            showError("Submit Job", e);
            loadDataSets(email, "container_userDataSets", centertabs,"User DataSets", "Public DataSets");
        }
    });
}



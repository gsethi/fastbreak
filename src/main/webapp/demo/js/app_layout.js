var chrom_list = [];
chrom_list.push({value:'*',label:'*'});
for(var i =1;i <= 22; i++) {
    chrom_list.push({value:i+'',label:i+''});
}
chrom_list.push({value:'X',label:'X'});
chrom_list.push({value:'Y',label:'Y'});

var dataset_list = [{label:'FinalC',id:'crad'},{label:'FinalC - NonProximal',id:'crad-np'},{label:'FinalD',id:'crad-d'}];

var scatterplot_window,scatterplot_window_mask;

var order_list = [{value:'correlation',label:'Correlation'},{value:'importance',label:'Importance'}];

var limit_list = [{value:10,label:'10'},{value:20,label:'20'},{value:40, label:'40'},{value:100, label:'100'},{value:200, label:'200'},
            {value:1000, label:'1000'},{value:2000, label:'2000'}];

var helpWindowReference = null;

function generateFeatureRequest() {
    requestFeatureData(
            Ext.getCmp('f1_type_combo').getValue(),
            Ext.getCmp('f1_label_field').getValue(),
            Ext.getCmp('f1_chr_combo').getValue(),
            Ext.getCmp('f1_chr_start').getValue(),
            Ext.getCmp('f1_chr_stop').getValue(),

            Ext.getCmp('f2_type_combo').getValue(),
            Ext.getCmp('f2_label_field').getValue(),
            Ext.getCmp('f2_chr_combo').getValue(),
            Ext.getCmp('f2_chr_start').getValue(),
            Ext.getCmp('f2_chr_stop').getValue(),

            Ext.getCmp('min_importance').getValue(),
            Ext.getCmp('min_correlation').getValue(),

            Ext.getCmp('order_combo').getValue(),
            Ext.getCmp('limit_combo').getValue()
            );
}

function renderScatterPlot() {
    openSPWindow();
    scatterplot_draw(document.getElementById('scatterplot_panel'));
    scatterplot_window_mask.hide();
}

function openSPWindow() {
    scatterplot_window.show();
    scatterplot_window_mask =  new Ext.LoadMask('scatterplot-window', {msg:"Loading Data..."});
    scatterplot_window_mask.show();
}

function export_svg() {
    var serializer = new XMLSerializer();
    var svg_tags;
    var panel_dom = Ext.get('circle-panel').dom;
    if (panel_dom.firstChild.id == ""){
        svg_tags =serializer.serializeToString(panel_dom.firstChild);
    }
    Ext.getCmp('export-textarea').setRawValue(svg_tags);
}


Ext.onReady(function() {
    var randomforestPanel = new Ext.Panel({
        id:'randomforest-panel',
        name:'randomforest-panel',
        layout : 'border',
        title : 'Random Forest',
        iconCls : 'forest',
        defaults: {
            bodyStyle: 'padding:5px',
            animFloat: false,
            floatable: false
        },
        tools: [{
            id: 'help',
            handler: function(event, toolEl, panel){
                openHelpWindow('Random Forest',rfHelpString + "<p>" + viewHelpString);
            }

        }],

        items:[
            {region: 'center', id: 'view-region',
                xtype: 'tabpanel',
                border : false,
                activeTab : 0,
                items: [               {
                    xtype : 'panel', id :'rf-graphical',
                    layout : 'auto', title: 'Graphical',
                    autoScroll : 'true',
                    items: [{
                        xtype: 'panel', id:'circle-parent',
                        layout : 'absolute',
                        height: 900,
                        width:1050,
                        collapsible : true,
                        title : 'Genome-level View',
                        tools: [{
                            id: 'help',
                            handler: function(event, toolEl, panel){
                                openHelpWindow('Genome-level View',genomeLevelHelpString);
                            }}],
                        items : [ {
                            xtype: 'panel', id:'circle-panel',
                            width:800,
                            x:20,
                            y:20
                        },
                            {
                                xtype: 'panel', id:'circle-legend-panel',
                                width:150,
                                border:false,
                                frame : false,
                                x:880,
                                y:20
                            }]
                    }, {
                        xtype: 'panel', id:'linear-parent',
                        layout : 'absolute',
                        height: 800,
                        width:1050,
                        collapsible : true,
                        collapsed : true,
                        title : 'Chromosome-level View',
                        tools: [{
                            id: 'help',
                            handler: function(event, toolEl, panel){
                                openHelpWindow('Chromosome-level View',chromosomeLevelHelpString);
                            }}],
                        items : [ {
                            xtype: 'panel', id:'linear-panel',
                            width:800,
                            x:20,
                            y:20,
                            html: 'For a Chromosome-level view of the data, select a point of focus from the Genome-level View.<p>' +
                                    'Click on:' +
                                    '<ol><li>Chromosome Label</li><li>Tick Label</li>'
                        },
                            {
                                xtype: 'panel', id:'linear-legend-panel',
                                width:150,
                                border:false,
                                frame : false,
                                x:820,
                                y:20
                            }]
                    }]}, {
                    xtype: 'panel',  id:'grid-panel',
                    name : 'grid-panel',
                    title : 'Data Table',
                    autoScroll : 'true',
                    layout : 'auto',
                    height: 650,
                    width:1050,
                    collapsible : false,
                    tools: [{
                        id: 'help',
                        handler: function(event, toolEl, panel){
                            openHelpWindow('Data-level View',dataLevelViewHelpString);
                        }}],
                    items : [
                        {
                            xtype:'grid',
                            id : 'data_grid',
                            name : 'data_grid',
                            height: 650,
                            width:1050,
                            cm : new Ext.grid.ColumnModel({
                                columns: [
                                    { header: "Type", width: 40,  id:'target_source', dataIndex:'target_source',groupName:'Target'},
                                    { header: "Label", width: 120, id: 'target_label',dataIndex:'target_label',groupName:'Target'},
                                    { header: "Chr", width:30 , id:'target_chr', dataIndex:'target_chr',groupName:'Target'},
                                    { header: "Start", width:100, id:'target_start',dataIndex:'target_start',groupName:'Target'},
                                    { header: "Stop", width:100, id:'target_stop',dataIndex:'target_stop',groupName:'Target'},
                                    { header: "Type", width: 40,  id:'source_source', dataIndex:'source_source',groupName:'Source'},
                                    { header: "Label", width: 120, id: 'source_label',dataIndex:'source_label',groupName:'Source'},
                                    { header: "Chr", width:30 , id:'source_chr', dataIndex:'source_chr',groupName:'Source'},
                                    { header: "Start", width:100, id:'source_start',dataIndex:'source_start',groupName:'Source'},
                                    { header: "Stop", width:100, id:'source_stop',dataIndex:'source_stop',groupName:'Source'},
                                    { header: "Importance", width:50, id:'importance',dataIndex:'importance'},
                                    { header: "Correlation", width:50, id:'correlation',dataIndex:'correlation'}
                                ],
                                defaults: {
                                    sortable: true,
                                    width: 100
                                }
                            }),
                            store : new Ext.data.JsonStore({
                                autoLoad:false,
                                storeId:'data_grid_store',
                                fields : ['target_source','target_label','target_chr','target_start','target_stop',
                                    'source_source','source_label','source_chr','source_start','source_stop','importance','correlation']
                            })
                        }]
                }]
            },
            {region: 'east',
                collapsible: true,
                floatable: true,
                autoHide:false,
                split: true,
                width: 250,
                title: 'Tools',

                layout: {
                    type: 'accordion'
                },
                tools: [{
                    id: 'help',
                    handler: function(event, toolEl, panel){
                        openHelpWindow('Tools',toolsHelpString);
                    }}],
                items: [{
                    xtype: 'panel', id:'filters',
                    title : 'Filtering',
                    autoScroll : true,
                    height : 250,
                    tools: [{
                        id: 'help',
                        handler: function(event, toolEl, panel){
                            openHelpWindow('Filtering',filteringHelpString);
                        }}],
                    items :[
                        { xtype:'form',
                            id :'filter_panel',
                            name :'filter_panel',
                            bodyStyle:'padding:5px 5px 5px 5px',
                            defaults:{anchor:'100%'},
                            border : false,
                            labelAlign : 'right',
                            labelWidth: 70,
                            labelSeparator : '',
                            defaultType:'textfield',
                            monitorValid : true,
                            buttons : [
                                {
                                    text: 'Filter',
                                    formBind : true,
                                    listeners : {
                                        click : function(button,e) {
                                            generateFeatureRequest();
                                        }
                                    }
                                },
                                { text: 'Reset',
                                    listeners : {
                                        click : function(button,e) {
                                            Ext.getCmp('f1_type_combo').reset(),
                                                    Ext.getCmp('f1_label_field').reset(),
                                                    Ext.getCmp('f1_chr_combo').reset(),
                                                    Ext.getCmp('f1_chr_start').reset(),
                                                    Ext.getCmp('f1_chr_stop').reset(),
                                                    Ext.getCmp('f2_type_combo').reset(),
                                                    Ext.getCmp('f2_label_field').reset(),
                                                    Ext.getCmp('f2_chr_combo').reset(),
                                                    Ext.getCmp('f2_chr_start').reset(),
                                                    Ext.getCmp('f2_chr_stop').reset(),
                                                    Ext.getCmp('min_importance').reset(),
                                                    Ext.getCmp('min_correlation').reset(),
                                                    Ext.getCmp('order_combo').reset(),
                                                    Ext.getCmp('limit_combo').reset()
                                        }
                                    }
                                }
                            ],
                            items : [
                                {  xtype:'fieldset',
                                    title:'Target',
                                    collapsible: true,
                                    defaults:{anchor:'100%'},
                                    labelWidth: 70,
                                    labelSeparator : '',
                                    defaultType:'textfield',
                                    autoHeight:true,
                                    items:[
                                        {
                                            xtype:'combo',
                                            name:'f1_type_combo',
                                            id:'f1_type_combo',
                                            mode:'local',
                                            allowBlank : true,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: [
                                                    {value: '*',label:'All'},
                                                    {value: 'GEXP',label:'Gene Expression'},
                                                    {value: 'METH',label:'Methylation'},
                                                    {value: 'CNVR',label:'Copy # Var'},
                                                    {value: 'CLIN',label:'Clinical'}
                                                ],
                                                storeId:'f1_type_combo_store'
                                            }),
                                            fieldLabel:'Type',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 0,
                                            typeAhead : true,
                                            selectOnFocus:true,
                                            triggerAction : 'all',
                                            forceSelection : true,
                                            emptyText : 'Select a Type...',
                                            value : 'GEXP'
                                        }, {
                                            name:'f1_label_field',
                                            id:'f1_label_field',
                                            emptyText : 'Input Label...',
                                            tabIndex: 1,
                                            selectOnFocus:true,
                                            fieldLabel:'Label'
                                        },
                                        { xtype:'combo', name:'f1_chr_combo',id:'f1_chr_combo',
                                            mode:'local',
                                            allowBlank : false,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: chrom_list,
                                                storeId:'f1_chr_combo_store'
                                            }),
                                            fieldLabel:'Chromosome',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 2,
                                            selectOnFocus:true,
                                            forceSelection : true,
                                            triggerAction : 'all',
                                            emptyText : 'Select Chr...',
                                            value : '*'
                                        },{xtype : 'numberfield',
                                            id:'f1_chr_start',
                                            name :'f1_chr_start',
                                            allowNegative: false,
                                            decimalPrecision : 0,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            maxValue: 99999999,
                                            minValue:1,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            allowDecimals : false,
                                            fieldLabel : 'Start >=',
                                            value : ''
                                        },{xtype : 'numberfield',
                                            id:'f1_chr_stop',
                                            name :'f1_chr_stop',
                                            allowNegative: false,
                                            decimalPrecision : 0,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            maxValue: 250999999,
                                            minValue:1,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            allowDecimals : false,
                                            fieldLabel : 'Stop <=',
                                            value : ''
                                        }

                                    ]},
                                {  xtype:'fieldset',
                                    title:'Predictor',
                                    collapsible: true,
                                    defaults:{anchor:'100%'},
                                    labelWidth: 70,
                                    labelSeparator : '',
                                    defaultType:'textfield',
                                    autoHeight:true,
                                    items:[
                                        {
                                            xtype:'combo',
                                            name:'f2_type_combo',
                                            id:'f2_type_combo',
                                            mode:'local',
                                            allowBlank : true,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: [
                                                    {value: '*',label:'All'},
                                                    {value: 'GEXP',label:'Gene Expression'},
                                                    {value: 'METH',label:'Methylation'},
                                                    {value: 'CNVR',label:'Copy # Var'},
                                                    {value: 'CLIN',label:'Clinical'}
                                                ],
                                                storeId:'f2_type_combo_store'
                                            }),
                                            fieldLabel:'Type',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 0,
                                            typeAhead : true,
                                            selectOnFocus:true,
                                            triggerAction : 'all',
                                            forceSelection : true,
                                            emptyText : 'Select a Type...',
                                            value : '*'
                                        }, {
                                            name:'f2_label_field',
                                            id:'f2_label_field',
                                            emptyText : 'Input Label...',
                                            tabIndex: 1,
                                            selectOnFocus:true,
                                            fieldLabel:'Label'
                                        },
                                        { xtype:'combo', name:'f2_chr_combo',id:'f2_chr_combo',
                                            mode:'local',
                                            allowBlank : true,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: chrom_list,
                                                storeId:'f2_chr_combo_store'
                                            }),
                                            fieldLabel:'Chromosome',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 2,
                                            selectOnFocus:true,
                                            forceSelection : true,
                                            triggerAction : 'all',
                                            emptyText : 'Select Chr...',
                                            value : '*'
                                        },{xtype : 'numberfield',
                                            id:'f2_chr_start',
                                            name :'f2_chr_start',
                                            allowNegative: false,
                                            decimalPrecision : 0,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            maxValue: 99999999,
                                            minValue:1,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            allowDecimals : false,
                                            fieldLabel : 'Start >=',
                                            value : ''
                                        },{xtype : 'numberfield',
                                            id:'f2_chr_stop',
                                            name :'f2_chr_stop',
                                            allowNegative: false,
                                            decimalPrecision : 0,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            maxValue: 250999999,
                                            minValue:1,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            allowDecimals : false,
                                            fieldLabel : 'Stop <=',
                                            value : ''
                                        }

                                    ]},
                                {  xtype:'fieldset',
                                    defaults:{anchor:'100%'},
                                    labelWidth : 90,
                                    labelSeparator : '',
                                    title:'Link',
                                    collapsible: true,
                                    autoHeight:true,
                                    items:[
                                        {xtype : 'numberfield',
                                            id:'min_importance',
                                            name :'min_importance',
                                            allowNegative: false,
                                            decimalPrecision : 2,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            minValue:0,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            fieldLabel : 'Importance >=',
                                            value : 0
                                        },
                                        {xtype : 'numberfield',
                                            id:'min_correlation',
                                            name :'min_correlation',
                                            allowNegative: false,
                                            decimalPrecision : 2,
                                            emptyText : 'Input value...',
                                            invalidText:'This value is not valid.',
                                            minValue:0,
                                            tabIndex : 1,
                                            validateOnBlur : true,
                                            fieldLabel : 'Abs(Corr) >=',
                                            value : 0
                                        }, { xtype:'combo', name:'order_combo',id:'order_combo',
                                            mode:'local',
                                            allowBlank : true,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: order_list,
                                                storeId:'order_combo_store'
                                            }),
                                            fieldLabel:'Order By',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 2,
                                            typeAhead : true,
                                            selectOnFocus:true,
                                            triggerAction : 'all',
                                            value : 'importance'
                                        },
                                        { xtype:'combo', name:'limit_combo',id:'limit_combo',
                                            mode:'local',
                                            allowBlank : true,
                                            store: new Ext.data.JsonStore({
                                                autoLoad : true,
                                                fields : ['value','label'],
                                                idProperty:'value',
                                                data: limit_list,
                                                storeId:'limit_combo_store'
                                            }),
                                            fieldLabel:'Max Results',
                                            valueField:'value',
                                            displayField:'label',
                                            tabIndex : 2,
                                            typeAhead : true,
                                            selectOnFocus:true,
                                            triggerAction : 'all',
                                            value : 200
                                        }
                                    ]
                                }
                            ]
                        }]}, {
                    xtype: 'form', id:'Mode',
                    title : 'Mode',
                    bodyStyle:'padding:5px 5px 5px 5px',
                    defaults:{anchor:'100%'},
                    border : false,
                    labelAlign : 'right',
                    labelWidth: 70,
                    labelSeparator : '',
                    defaultType:'textfield',
                    monitorValid : true,
                    tools: [{
                        id: 'help',
                        handler: function(event, toolEl, panel){
                            openHelpWindow('Selection',selectionHelpString);
                        }}],
                    items :[ {
                        xtype:'fieldset',

                        collapsible: true,
                        defaults:{anchor:'100%'},
                        labelWidth: 70,
                        labelSeparator : '',
                        defaultType: 'radiogroup', // each item will be a checkbox
                        items:[{
                            fieldLabel:'Genome-Level',
                            columns : 1,
                            items: [{
                                inputValue : 1,
                                checked: true,
                                name: 'gen-ex',
                                boxLabel: 'Examine'
                            }, {
                                boxLabel: 'Collect',
                                inputValue : 2,
                                disabled: true,
                                name: 'gen-co'
                            }, {
                                boxLabel: 'Link To',
                                inputValue : 3,
                                disabled: true,
                                name: 'gen-li'
                            }]
                        }]
                    },{
                        xtype:'fieldset',
                        collapsible: true,
                        defaults:{anchor:'100%'},
                        labelWidth: 70,
                        labelSeparator : '',
                        defaultType: 'radiogroup', // each item will be a checkbox
                        items:[{
                            fieldLabel:'Chromosome-Level',
                            columns : 1,
                            items: [{
                                inputValue : 1,
                                checked: true,
                                name: 'chr-ex',
                                boxLabel: 'Examine'
                            }, {
                                boxLabel: 'Collect',
                                inputValue : 2,
                                disabled: true,
                                name: 'chr-co'
                            }, {
                                boxLabel: 'Link To',
                                inputValue : 3,
                                disabled: true,
                                name: 'chr-li'
                            }]
                        }]
                    }]},{
                    xtype: 'panel', id:'navigation',
                    title : 'Data',
                    height : 300,
                    tools: [{
                        id: 'help',
                        handler: function(event, toolEl, panel){
                            openHelpWindow('Data',dataHelpString);
                        }}],
                    items:[{   xtype:'listview',
                        id:'dataset_list',
                        name:'dataset_list',
                        disabled : true,
                        mode : 'local',
                        multiselect: false,
                        store: new Ext.data.JsonStore({
                            autoLoad:true,
                            root:'Datasets',
                            storeId:'dataset_list_store',
                            fields:['label','id'],
                            data : {Datasets:dataset_list}
                        }),
                        columns:[{
                            header : 'DataSet',
                            dataIndex:'label'
                        }]
                    }]
                },{
                    xtype: 'panel',  id:'export',
                    title : 'Export',
                    layout : 'anchor',
                    tools: [{
                        id: 'help',
                        handler: function(event, toolEl, panel){
                            openHelpWindow('Export',exportHelpString);
                        }}],
                    height : 300,
                    padding : '5',
                    items:[{
                        xtype:'button',
                        text:'Export Plot',
                        listeners: {
                            click : function() {
                                export_svg();
                            }
                        }
                    },{
                        xtype:'textarea',
                        id:'export-textarea',
                        name:'export-textarea',
                        padding : '5 0 0 0',
                        autoScroll:true,
                        anchor:'100% -40'
                    }]
                }]
            }]

    });

    var parallelcoordinatesPanel = new Ext.Panel({
        id :'pc-panel',
        name :'pc-panel',
        title : 'Parallel Coordinates',
        layout : 'border',
        tools: [{
            id: 'help',
            handler: function(event, toolEl, panel){
                openHelpWindow('Parallel Coordinates',parCoordHelpString);
            }
        }],
        items:[{
            region:'center',
            xtype:'tabpanel',
            id:'pc-tabpanel',
            name:'pc-tabpanel',
            border : false,
            activeTab : 0,
            items:[{
                xtype:'panel',
                id:'pc-items',
                iconCls:'parallel_coordinates',
                    autoScroll : true,
                    title : 'Graphic',
                    layout : 'auto',
                items:[{
                    id:'pc_text',
                    padding	:'5',
                    border :false,
                    html :'<p>The parallel coordinates plot below shows the three different cancer ' +
                            'types with their associated structural variation counts for each gene.  A range of items can be ' +
                            'selected by clicking and dragging the mouse on any given column.  In this way, genes that display a ' +
                            'trend across cancer types can be selected and further explored.'
                },{
                    xtype:'panel',
                    id:'pc_draw',
                    name:'pc_draw'
                },{xtype:'panel',
                                       border : false,
                                       buttonAlign : 'center',
                               buttons:[
                               {	xtype :	'button',
                                       x:0,
                                       y:0,
                                   text:'Add Filtered Set',
                                   listeners : {
                                       click : function() {
                                           var set = paco_obj.getFiltered();
                                           var record_set = set.map(function(json){return new (Ext.StoreMgr.get('pc_selection_store')).recordType(json,json.gene);})
                                           appendToPCSelectionGrid(record_set);
                                       }
                                   }
                               },
                               {   xtype:'button',
                                   x:30,
                                   y:0,
                                   text:'Add Selection',
                                   listeners : {
                                       click : function() {
                                           var json = paco_obj.getSelected();
                                           if (json ==null) { return;}
                                          var record = new (Ext.StoreMgr.get('pc_selection_store')).recordType(json,json.gene);
                                           appendToPCSelectionGrid(record);
                                       }
                                   }
                               }
                           ]}]

            },{
                xtype:'grid',
                id:'pc_table',
                iconCls : 'table',
                draggable : true,
                ddGroup : 'pc_drag_group',
                enableDragDrop   : true,
                stripeRows       : true,
                name:'pc_table',
                title : 'Data Table',
                cm: new Ext.grid.ColumnModel({
                    defaults : {
                        width : 120,
                        sortable : true
                    },
                    columns : [
                        {id : 'gene', header:'Gene', dataIndex:'gene'},
                        {id : 'COAD',header: 'COAD', dataIndex: 'COAD'},
                        {id : 'GBM',header: 'GBM', dataIndex: 'GBM'},
                        {id : 'OV',header: 'OV', dataIndex: 'OV'}
                    ]
                }),
                store: new Ext.data.JsonStore({
                    autoLoad: false,
                    storeId:'pc_table_store',
                    fields: ['gene', 'COAD', 'GBM', 'OV'],
                    sortInfo : {
                        field : 'gene',
                        direction : 'ASC'
                    },
                    idProperty : 'gene'
                })
            }]
        },{
            region: 'east',
            layout : 'anchor',
            width:300,
            split: true,
            id:'pc_selection_panel',
            title:'Selections',
            collapsible : true,
            minimizable : true,
            collapsed : false,

            items : [{
                id:'pc_selection_grid',
                name:'pc_selection_grid',
                xtype:'grid',
                margins: '0 5 5 0',
                height : 400,
                border:true,
                autoScroll: true,
                ddGroup : 'pc_drag_group',
                pruneModifiedRecords : true,
                stripeRows       : true,
                cm: new Ext.grid.ColumnModel({
                    defaults : {
                        width : 60,
                        sortable : true
                    },
                    columns : [
                        {id : 'gene', header:'Gene', dataIndex:'gene', width:90},
                        {id : 'COAD',header: 'COAD', dataIndex: 'COAD'},
                        {id : 'GBM',header: 'GBM', dataIndex: 'GBM'},
                        {id : 'OV',header: 'OV', dataIndex: 'OV'}
                    ]
                }),
                store: new Ext.data.JsonStore({
                    autoLoad: false,
                    storeId:'pc_selection_store',
                    fields: ['gene', 'COAD', 'GBM', 'OV'],
                    sortInfo : {
                        field : 'gene',
                        direction : 'ASC'
                    },
                    idProperty : 'gene'
                }),
                buttons: [{
                xtype:'button',
                        text:'Remove Selection',
                        listeners : {
                            click : function(e) {
                                var grid = Ext.getCmp('pc_selection_grid');
                                var sels = grid.getSelectionModel().getSelections();
                                if (sels.length > 0) {
                                    grid.getStore().remove(sels);
                                }
                            }
                        }
                },{
                xtype:'button',
                        text:'Remove All',
                        listeners : {
                            click : function(e) {
                                var grid = Ext.getCmp('pc_selection_grid');
                                    grid.getStore().removeAll();
                            }
                        }
                }],
                listeners : {
                    render : setupSelectionDropTarget
                }
           }]
        }],
        listeners : {
            render : function() {loadCancerSV(renderCancerPaCo);}
        }
    });

    function setupSelectionDropTarget() {
        var pcSelectionDropTarget = new Ext.dd.DropTarget(Ext.getCmp('pc_selection_grid').getView().scroller.dom, {
            ddGroup     : 'pc_drag_group',
            notifyDrop : function(ddSource, e, data){
                var records =  ddSource.dragData.selections;
                appendToPCSelectionGrid(records);
                return true;
            }
        });
    }
    function appendToPCSelectionGrid(records) {
        var grid = Ext.getCmp('pc_selection_grid');

        Ext.each(records, grid.store.remove, grid.store);
        try{
        grid.store.add(records);
        grid.store.sort('gene', 'ASC');
        }
        catch(e) {
            console.log(e);
        }
        return true;
    }
   var geneSearchPanel = new Ext.FormPanel({
                     labelAlign: 'top',
                     iconCls: 'gene_select',
                     title: 'Gene Select',
                     height : 120,
                     frame: true,
                     padding: '5',
                     tools: [{
                         id: 'help',
                         handler: function(event, toolEl, panel){
                             openHelpWindow('Gene Search','Enter a valid Gene Symbol into the text box.<br/><br/>  The matched human gene will be ' +
                                     'selected as the current chromosomal range for analysis (with a 20Kbp interval added to both ends.)');
                         }
                     }],
                     items:[{
                            layout:'column',
                            items:[{
                                columnWidth: 0.8,
                                layout:'form',
                                items:[{
                                    xtype:'textfield',
                                    fieldLabel: 'Gene Symbol',
                                    name:'gene_symbol',
                                    id:'gene_symbol',
                                    anchor:'95%'
                                }]
                            }]
                     }],
                     buttons: [{
                         text:'Select',
                         listeners:{
                             click: function(){ onGeneSelection(Ext.getCmp('gene_symbol').getValue());
                             Ext.getCmp('gene_symbol').setValue("");}
                         }
                     }]

                 });

   var currentRange =  new Ext.FormPanel({
                     title: 'Current Selections',
                     labelAlign: 'top',
                     iconCls:'current_selections',
                     frame: true,
                     height: 175,
                     padding: '5',
                     tools: [{
                         id: 'help',
                         handler: function(event, toolEl, panel){
                             openHelpWindow('Current Selections','This panel displays the currently selected chromosomal range to be displayed in '+
                             'the Fastbreak view.<p>  If a gene symbol has been selected specifically, the symbol is displayed.  The selection can '+
                                     'be modified using multiple methods including:<ul><li> the Gene Select panel below.'+
                                     '<li>clicking on a feature in any Circvis Plot' +
                                     '<li>any Data Table row selection<li>the \"Range and Patient Selection\" dialog in the Fastbreak view' +
                                     '<li>clicking on a feature in the Fastbreak view</li></ul><p>See the example on the Home Page for more information.');
                         }
                     }],
                     items:[{
                         layout:'column',
                         items:[{
                             columnWidth: 0.95,
                             layout:'form',
                             items:[{
                                 xtype:'label',
                                 fieldLabel:'Chr',
                                 id:'currentrange_chr',
                                 width: 30,

                                 readOnly:true
                             },
                                     {
                                 xtype:'label',
                                 fieldLabel:'Range',
                                 id:'currentrange_range',
                                 fieldClass:'chr_range',
                                         width: 150,

                                 readOnly:true
                             },
                                     {
                                 xtype:'label',
                                 fieldLabel:'Gene',
                                 id:'currentrange_gene',
                                 width: 80,

                                 readOnly:true
                             }]
                             }]
                     }]
                     });


    new Ext.Viewport({
        layout: {
            type: 'border',
            padding: 5
        },
        defaults: {
            split: true
        },
        items: [
            {
            region: 'north', id:'toolbar-region',
            collapsible: false,
            border : false,
            title: 'Regulome Explorer',
            split: false,
            height: 27,
            layout : 'fit'
        },
            {region: 'west',
            id:'nav-region',
            collapsible: true,
            expanded: true,
            width: 200,
            layout: {
                type: 'vbox',
                padding: '5,5,5,5',
                align: 'stretch'
            },
            defaults : {
                padding : '0, 0, 5, 0'
            },
            items : [{xtype:'treepanel',
                title: 'Navigation',
                iconCls: 'navigation',
                rootVisible: false,
                lines: false,
                singleExpand: true,
                tools: [{
                    id: 'help',
                    handler: function(event, toolEl, panel){
                        openHelpWindow('Navigation',navHelpString);
                    }
                }],
                useArrows: true,
                height : 380,
                padding: '5',
                autoScroll: true,
                loader: new Ext.tree.TreeLoader(),
                root: new Ext.tree.AsyncTreeNode({
                    expanded: true,
                    children: [{
                        text: 'Home Page',
                        iconCls: 'home',
                        leaf: true,
                        id: 'homepage'
                    }, {
                        text: 'Cancer Comparator',
                        iconCls:'comparator',
                        leaf: false,
                        id: 'comparator',
                        children :[{
                                text: 'COAD/GBM/OV',
                                iconCls: 'parallel_coordinates',
                                leaf: true,
                                id: 'pc_compare'
                            }
                        ]
                    },
{
                            text: 'Gene Disruption',
                            leaf: false,
                            id: 'genedisruption',
                            children: [{
                                text: 'OV',
                                iconCls:'circvis',
                                leaf: true,
                                id: 'ov'
                            },{
                                text: 'GBM',
                                iconCls:'circvis',
                                leaf: true,
                                id: 'gbm'
                            }]
                        },{
                            text: 'Fastbreak',
                            iconCls: 'fastbreak',
                            leaf: true,
                            id: 'fastbreak'
                        },
{
                        text: 'Individual Cancers',
                        leaf: false,
                        iconCls : 'feature_associations',
                        id: 'featureassociations',
                        children: [{
                            text: 'COAD',
                            leaf: false,
                            id: 'coad',
                            children : [{
                                text: 'Random Forest',
                                iconCls:'forest',
                                leaf: true,
                                id: 'coad_rf'
                            },{
                                text: 'Structural Variation',
                                iconCls: 'fastbreak',
                                leaf: true,
                                disabled : true,
                                id: 'coad_sv'
                            }]
                        },
                        {
                            text: 'GBM',
                            leaf: false,
                            id: 'gbm_rf',
                            children : [{
                                text: 'Random Forest',
                                iconCls:'forest',
                                disabled : true,
                                leaf: true,
                                id: 'coad_gbm'
                            },{
                                text: 'Structural Variation',
                                iconCls: 'fastbreak',
                                leaf: true,

                                id: 'gbm_sv'
                            }]
                        },
                        {
                            text: 'OV',
                            leaf: false,
                            id: 'ov_rf',
                            children : [{
                                text: 'Random Forest',
                                iconCls:'forest',
                                leaf: true,
                                disabled : true,
                                id: 'ov_rf'
                            },{
                                text: 'Structural Variation',
                                iconCls: 'fastbreak',
                                leaf: true,
                                id: 'ov_sv'
                            }]
                        }]
                    }]
                }),
                listeners : {
                    click : function(selected_node) {
                        switch(selected_node.id){
			    case('gbm'):
				alert("selecting gbm");
				onCircvisTypeSelected('gbm');
				break;
                            case('coad_rf'):
                                Ext.getCmp('center-panel').layout.setActiveItem('randomforest-panel');
                                Ext.getCmp('nav-region').collapse();
                                if (Ext.get('circle-panel').dom.firstChild.id != ""){
                                    generateFeatureRequest();
                                }
                                break;
                            case('coad_sv'):
                                Ext.getCmp('center-panel').layout.setActiveItem('sv-panel');
                                break;
                            case('pc_compare'):
                                Ext.getCmp('center-panel').layout.setActiveItem('pc-panel');
                                break;
                            case('homepage'):
                                Ext.getCmp('center-panel').layout.setActiveItem('homepage-panel');
                                break;
                            case('ov_sv'):
                            case('gbm_sv'):
                                openFastbreakTab();
                            default:
                                break;
                        }
                    }
                }
            },currentRange,geneSearchPanel]
            },
            { region:'center',
            id:'center-panel', name:'center-panel',
            layout:'card',
            border:false,
            closable:false,
            activeItem:0,
            height: 800,
            margins: '0 5 5 0',
            items:[{
                id:'homepage-panel',
                iconCls:'home',
                layout: 'fit',
                autoScroll : true,
                autoLoad : {
                    url : 'home_tab.html'
                },
                title: 'Home'
            }
                ,parallelcoordinatesPanel
                ,randomforestPanel
//                {
//                id:'sv-panel',
//                iconCls:'home',
//                layout: 'fit',
//                html:'Sv Panel!',
//                title: 'Structural Variation'
//            }
            ]
        }
        ],
        renderTo:Ext.getBody()
    });


    scatterplot_window =
            new Ext.Window({
                id          : 'scatterplot-window',
                renderTo    : 'view-region',
                modal       : false,
                closeAction : 'hide',
                layout      : 'anchor',
                width       : 500,
                height      : 400,
                title       : "Scatterplot",
                closable    : true,
                layoutConfig : {
                    animate : true
                },
                maximizable : false,
                items : [{
                    xtype:'panel',
                    id:'scatterplot_panel',
                    name:'scatterplot_panel',
                    margins: '3 0 3 3',
                    height : 400,
                    width : 500,
                    frame:true
                }]
            });
    scatterplot_window.hide();
    loadAnnotations(function() {return;});

});

function requestFeatureData() {
    arg_obj = {f1_type:arguments[0],f1_label:arguments[1], f1_chr:arguments[2], f1_start:arguments[3],f1_stop:arguments[4],
        f2_type:arguments[5],f2_label:arguments[6], f2_chr:arguments[7], f2_start:arguments[8],f2_stop:arguments[9],
        importance:arguments[10],correlation:arguments[11],order:arguments[12],limit:arguments[13]};
    loadFilteredData(arg_obj);
}

function openHelpWindow(subject,text) {
    if (helpWindowReference == null || helpWindowReference.closed) {
        helpWindowReference = window.open('','help-popup','width=400,height=300,resizable=1,scrollbars=1,status=0,'+
        'titlebar=0,toolbar=0,location=0,directories=0,menubar=0,copyhistory=0');
    }
        helpWindowReference.document.title='Help - ' + subject;
        helpWindowReference.document.body.innerHTML = '<b>' + subject +'</b><p><div style=width:350>' + text + '</div>';
        helpWindowReference.focus();


}

var navHelpString = 'The Navigation Panel provides a way to navigate the site.  <br/>' +
        'Clicking on an arrow will expand an item.  Selecting an item without an arrow will display the corresponding view in the main panel.',
 cancerComparatorHelpString = 'The Cancer Comparator Panel provides a way to compare features across cancers.  ' +
'<p>The Parallel Coordinates view displays each cancer as a separate column.  Points on the cancer columns represent the ' +
         'number of structural variations found in a given gene for that cancer type.<p>' +
'Selection of ranges on each of the three cancer columns can be done by clicking and dragging the mouse on a given ' +
'column.  In this way, trends of structural variations across cancer types can be viewed.   Additionally, items can be ' +
'selected and transferred to a gene list for further investigation. <p>' +
'The underlying data represented in the Parallel Coordinates visualization can be viewed in a data table by ' +
         'clicking on the Data Table tab at the top of the view.',
rfHelpString = 'The Random Forest Panel provides a way to explore the multivariate data analysis performed using the ' +
        'random forest algorithm on the TCGA data.  The tools panel allows for data filtering, selection, and ' +
        'exporting of the circular plot image.  The main view panel has three different data viewing visualizations ' +
        'that have various interactions depending on what action a user takes on the visualization.  See the help ' +
        'sections of each specific view panel for more details on the visualization and user interactions available.',
viewHelpString = 'Two tabs are available to look at the results of Random Forest analysis.  The Graphical tab provides ' +
        'the Genome-level View and the Chromosome-level View.  The Genome-level view displays a circular plot of the multivariate features found in the TCGA dataset.  ' +
        'By scrolling down, or minimizing the Genome-level View the Chromosome-level View is displayed showing the ' +
        'feature associations at a single chromosome level.  <br/>The \'Data Table\' tab can be selected as well.'
        'The Data-level View is shown and provides a way to view a specific feature and its associated links.',
genomeLevelHelpString = 'The Genome-level View is an interactive circular plot showing the links between target and ' +
        'predictor features within the dataset.  Tooltips over various points give the underlying data associated with ' +
        'a node or link.  Clicking on the links within the plot will display a coorelation scatterplot of the associated ' +
        'features.  Mouse clicks on chromosomes, links, and nodes within the plot also bring up drill-down information ' +
        'in the Chromosome-level and Data-level views.<p>' +
'The subset of data shown in the circular plot can be filtered by using the tools panel filtering section.  Once a plot ' +
        'of interest has been found, an export of the plot can be achieved by using the tools panel export option.  ' +
        'The mouse-click behavior of the interactive plot can be changed by choosing different options in the tools ' +
        'panel selection area.',
chromosomeLevelHelpString = 'The Chromosome-level View provides a way to navigate the features of a given dataset on ' +
        'a single chromosome level.  The view will be populated with chromosome information once a chromosome is ' +
        'selected by either clicking on a specific chromosome number  or end-point of a link in the Genome-level view.<p>'+
        'Feature information on a given chromosome is displayed in 4 different plots.  The Distal Intra-Chromosome ' +
        'Correlates plot shows the location of the predictors for a target within a chromosome.  The Proximal Feature ' +
        'Predictors plot also displays feature associations within the chromosome, but only displays ones where the ' +
        'start and end location of a predictor is less than 250,000 bp in length.  The Unmapped Feature Coorelates ' +
        'shows features for which there does not exist a mapped location.  Finally, the Feature Locations plot shows ' +
        'the locations of the various targets involved in the links.   All plots have tooltips giving more details of ' +
        'the underlying data. Coorelation scatterplots are displayed when an item is selected within a plot.<p>' +
'A sliding scale showing all feature locations is given at the bottom of the view.  A range can be selected to zoom ' +
        'in on a given chromosome location by clicking the mouse and dragging it over a region.  The same zoom and ' +
        'selection capability is also available within the top 4 plots.',
dataLevelViewHelpString = 'The Data-level View is a data table displaying the feature selected in the Genome-level ' +
        'view and its related links.  This view allows the user to easily navigate all the related data values ' +
        'associated with a single feature.',
toolsHelpString = 'The Tool Panel provides a way for filtering, selecting, and exporting different datasets.  ' +
        'The Panel can also be minimized by clicking the `>>` icon, which then expands main panel view.  ' +
        'See each individual tool help for further details on their capabilities.',
filteringHelpString = 'The Filtering Panel allows the user to filter the dataset based on target, ' +
        'predictor, and link attributes of the feature associations.',
selectionHelpString = 'The Selection Panel provides a way to customize the selection behavior within the Genome-level ' +
        'view circular plot.',
dataHelpString = 'The Data Panel displays all available datasets that can be selected, filtered, and ' +
        'viewed within the Random Forest View.',
exportHelpString = 'The Export Panel allows the user to export the Genome-level view circular plot into a .svg image.<p>' +
        'How to obtain the image:<br> ' +
        '    1. Click the "Export Plot" button when you have a circular plot that you wish to save.  The textarea below the button will fill with SVG markup.<br/>' +
        '    2. Copy and paste (or Select All + drag and drop) the entire text string in the textarea to a text editor(Notepad, etc).<br/>' +
        '    3. Save the text file to your desktop with a ".svg" extension (ex test.svg).<br/>' +
        '    4. Open the file in a SVG Image manipulator. <a href="http://www.gimp.org/">GIMP</a> is an ' +
        'excellent choice. So is <a href="http://inkscape.org/">Inkscape</a>.<br/>' +
        '    5. Save the image to any format you prefer at any resolution.  You may wish to add a flat background color.<br/>' +
        '    6. You\'re ready to use the image.',
parCoordHelpString = 'The parallel coordinates plot below shows the three different cancer types with their associated ' +
        'structural variation counts for each gene.  A range of items can be selected by clicking and dragging the ' +
        'mouse on any given column.  In this way, genes that ' +
        'display a trend across cancer types can be selected and further explored.';

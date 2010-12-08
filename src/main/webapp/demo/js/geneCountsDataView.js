    function createOVGBMDataTable(tableData){
            var dataArray =tableData.map(function(c){ return {cancertype1: c.chr1.indexOf('GBM') > -1 ? 'GBM' : 'OV',
            genecount1:c.value1, gene1: c.options1.split('=')[1], genecount2: c.value2, gene2: c.options2.split('=')[1],
            cancertype2: c.chr2.indexOf('GBM') > -1 ? 'GBM' : 'OV',
            linkValue: c.linkValue};})

        var totalDataArray = {'root': dataArray};

        var ovgbmStore = new Ext.data.JsonStore({
                      // store configs
                      autoDestroy: true,
                      data: totalDataArray,
                      remoteSort: false,
                      sortInfo: {
                          field: 'linkValue',
                          direction: 'DESC'
                      },
                      storeId: 'ovgbmstore',
                      // reader configs
                      root: 'root',
                      fields: [{
                          name: 'cancertype1'
                      }, {
                          type: 'float',
                          name: 'genecount1'
                      },  {
                          name: 'gene1'
                      },  {
                          type: 'float',
                          name: 'genecount2'
                      }, {
                          name: 'gene2'
                      },{
                          name: 'cancertype2'
                      },{
                          type: 'float',
                          name: 'linkValue'
                      }]
                  });

         var filters = new Ext.ux.grid.GridFilters({
        // encode and local configuration options defined previously for easier reuse
        encode: false, // json encode the filter query
        local: true,   // defaults to false (remote filtering)
        filters: [{
            type: 'string',
            dataIndex: 'gene1'
        }, {
            type: 'string',
            dataIndex: 'gene2'
        },  {
            type: 'list',
            dataIndex: 'cancertype1',
            options: ['OV','GBM']
        },{
            type: 'list',
            dataIndex: 'cancertype2',
            options: ['OV','GBM']
        }, {
            type: 'float',
            dataIndex: 'genecount1'
        }, {
            type: 'float',
            dataIndex: 'genecount2'
        }, {
            type: 'float',
            dataIndex: 'linkValue'
        }]
    });

        var createColModel = function (finish, start) {

            var columns = [
                {
                dataIndex: 'cancertype1',
                header: 'Cancer 1',
                filterable: true,
                width: 60
            },  {
                dataIndex: 'gene1',
                header: 'Gene 1',
                filterable: true,
                width: 80
            }, {
                dataIndex: 'genecount1',
                header: 'Gene Count 1',
                filterable: true,
                width: 80
            }, {
                dataIndex: 'cancertype2',
                header: 'Cancer 2',
                filterable: true,
                width: 60
            }, {
                dataIndex: 'gene2',
                header: 'Gene 2',
                filterable: true,
                width: 80
            },  {
                dataIndex: 'genecount2',
                header: 'Gene Count 2',
                filterable: true,
                width: 80
            },  {
                dataIndex: 'linkValue',
                header: 'Link Value',
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

        return new Ext.grid.GridPanel({
        border: true,
        store: ovgbmStore,
        height: 600,
        colModel: createColModel(7),
             columnLines: true,
             frame: true,
             iconCls:'icon-grid',
             stripeRows: true,
             height: 600,
             width: 700,
            sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
        loadMask: true,
        plugins: [filters]
    });





    }

    function createDataTable(tableData){
            var dataArray =tableData.map(function(c){ return {
            chr:c.chr, gene: c.options.split('=')[1], start: c.start, end: c.end,
            patientvalue: c.value, genecount: c.genecount};})

        var totalDataArray = {'root': dataArray};

        var ovgbmStore = new Ext.data.JsonStore({
                      remoteSort: true,
            autoDestroy: true,
                      sortInfo: {
                          field: 'genecount',
                          direction: 'DESC'
                      },
                      storeId: 'ovgbmstore',
                      // reader configs
                      root: 'root',
                      fields: [ {
                          type: 'float',
                          name: 'start'
                      },  {
                          name: 'chr'
                      },  {
                          type: 'float',
                          name: 'end'
                      }, {
                          name: 'gene'
                      },{
                          type: 'float',
                          name: 'patientvalue'
                      },{
                          type: 'float',
                          name: 'genecount'
                      }],
                proxy: new Ext.ux.data.PagingMemoryProxy(totalDataArray, {
                    customFilter: function(el){
                        var d = el.data;
                        var c = el.data;
                    }
                })

                  });

         var filters = new Ext.ux.grid.GridFilters({
        // encode and local configuration options defined previously for easier reuse
        encode: false, // json encode the filter query
        local: false,   // defaults to false (remote filtering)
        autoReload: true,
        filters: [{
                          type: 'float',
                          dataIndex: 'start'
                      },  {
                          type: 'string',
                          dataIndex: 'chr'
                      },  {
                          type: 'float',
                          dataIndex: 'end'
                      }, {
                          type: 'string',
                          dataIndex: 'gene'
                      },{
                          type: 'float',
                          dataIndex: 'patientvalue'
                      },{
                          type: 'float',
                          dataIndex: 'genecount'
                      }]
    });

        var createColModel = function (finish, start) {

            var columns = [
                {
                          header: 'Gene',
                          dataIndex: 'gene',
                          width: 150
                      },  {
                          header: 'Chr',
                          dataIndex: 'chr'
                      },  {
                          header: 'Start',
                          dataIndex: 'start'
                      }, {
                          header: 'End',
                          dataIndex: 'end'
                      },{
                          header: '# Patients',
                          dataIndex: 'patientvalue'
                      },{
                          header: '# Disruptions',
                          dataIndex: 'genecount'
                      }];

            return new Ext.grid.ColumnModel({
                columns: columns.slice(start || 0, finish),
                defaults: {
                    sortable: true,
                    width: 100,
                    filterable: true
                }
            });
        };

          var sm = new Ext.grid.RowSelectionModel({
                listeners: {
                    'rowselect': function(sm,rowIndex,record){
                        var chrom = record.json.chr;
                        var startpos = record.json.start;
                        var endpos = record.json.end;
                        var gene_symbol = record.json.gene;
                        var buffer=20000;
                        onRangeSelection(chrom,startpos-buffer < 0 ? 0 : startpos-buffer,endpos+buffer,gene_symbol);
                    }
                }
           });

        return new Ext.grid.GridPanel({
        border: true,
        store: ovgbmStore,
        height: 600,
        colModel: createColModel(6),
             columnLines: true,
             frame: true,
             iconCls:'icon-grid',
             stripeRows: true,
             height: 600,
             width: 700,
            sm: sm,
        loadMask: true,
            plugins: [filters],
            bbar: new Ext.PagingToolbar({
                       pageSize: 50,
                       store: ovgbmStore,
                       displayInfo: true,
                       displayMsg: 'Displaying items {0} - {1} of {2}',
                       emptyMsg: "No items to display",
                       plugins: [filters]
                   }),
            listeners: {
                'render': function(grid){
                     grid.store.load({params:{start:0, limit:50}});
                }
            }
    });

    }
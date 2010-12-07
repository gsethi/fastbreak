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
                width: 80
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
            genecount1:c.value1, gene1: c.options1.split('=')[1], genecount2: c.value2, gene2: c.options2.split('=')[1],
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
                      fields: [ {
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
                width: 80
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
        colModel: createColModel(5),
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
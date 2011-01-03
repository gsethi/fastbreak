var GeneScoresQuery = Class.create({
    initialize: function(container, workspaceUri, refGenomeUri){
        this.container = $(container);
        this.workspaceUri = workspaceUri;
        this.refGenomeUri = refGenomeUri;
        this.patients = new Array();
        this.chromosomeRange = '';
        this.genes = new Array();
        this.loadControl();
        this.totalQueries=0;
        this.data = null;
    },

    loadControl: function(){

        var html = "<p><b>Patients and a chromosome range or gene selection must be made before showing query results.</b></p>";

        this.container.innerHTML =html;

    },

    onPatientSelection: function(patientArray){
        var control = this;
        control.patients = patientArray;

        if(patientArray.length > 0 && control.genes.length > 0)
        {
            control.loadGeneScoresQueryData();
        }

    },

    onRangeSelection: function(chromRangeUri){
        var control = this;

        control.genes = new Array();
        new Ajax.Request(control.refGenomeUri + "/" + chromRangeUri + "/genes", {
            method: "get",
            onSuccess: function(o) {
                var json = o.responseJSON;
                if (json && json.items) {
                    $A(json.items).each(function(item) {
                        control.genes[control.genes.length] = item.label;
                    });

                    if(control.patients.length > 0 && control.genes.length > 0)
                    {
                        control.loadGeneScoresQueryData();
                    }
                }
            }
        });
    },

    onGeneSelection: function(geneSymbol){
        var control = this;
        control.genes = new Array();
        control.genes[0] = geneSymbol;

        if(control.patients.length > 0 && control.genes.length > 0)
        {
            control.loadGeneScoresQueryData();
        }

    },

    loadGeneScoresQueryData: function(){
         var control = this;

        //first put the genes into groups of 4
        var geneCount = 0;
        var genesArrayof4 = new Array();
        var totalGenesArray = new Array();
        control.data = null;
        $A(control.genes).each(function(gene) {
            geneCount++;
            if(geneCount > 4)
            {
                geneCount = 0;
                totalGenesArray[totalGenesArray.length] = genesArrayof4;
                genesArrayof4 = new Array();
            }
            genesArrayof4[genesArrayof4.length] = gene;

        });

        //need to put last one into totalGenesArray
        totalGenesArray[totalGenesArray.length] = genesArrayof4;

        //now make batch calls out to get the patient gene scores for the genes
         control.totalQueries=totalGenesArray.length;
        for(var i=0; i< totalGenesArray.length; i++){
            var queryString = 'select gene_id, ';
            var first=0;
            $A(control.patients).each(function(p) {
                if(first == 1)
                {
                    queryString = queryString + ', ';
                }
                first = 1;
                queryString = queryString + p.id.replace(/-/g,"_");
            });
            first = 0;

            for(var j=0; j< totalGenesArray[i].length; j++){
                if(first == 1)
                {
                    queryString = queryString + ' or ';
                }
                else{
                 queryString = queryString + ' where ';
                }
                first = 1;
                queryString = queryString + ' gene_id=\''+totalGenesArray[i][j]+ '\'';
            }

            queryString = queryString + ' order by gene_id asc';

            var query = new google.visualization.Query(this.workspaceUri + "/patientgenescores.tsv/query");
            query.setQuery(queryString);
            query.send(function (response) { control.loadGeneScoresQueryVis(response); });
        }

    },

    loadGeneScoresQueryVis: function(response){
        var control = this;
        control.totalQueries--;
        $(control.container).innerHTML = "";
        if (response.isError()) {
            alert("Error in query: " + response.getMessage() + " " + response.getDetailedMessage());
            return;
        }
        var dataTable = response.getDataTable();
        if(control.data == null)
        {
            control.data = dataTable;
        }
        else{

            for (var row = 0; row < dataTable.getNumberOfRows(); row++) {
                var dataRowArray = new Array();
                dataRowArray[dataRowArray.length] = dataTable.getValue(row,0);
                for(var col = 1; col < dataTable.getNumberOfColumns(); col++){
		            dataRowArray[dataRowArray.length] = dataTable.getValue(row,col);
                }

                control.data.addRow(dataRowArray);
            }
        }

        if(control.totalQueries == 0){
            var visualization = new google.visualization.Table($(control.container));
            var options = new Array();
            options['page'] = 'enable';
            options['pageSize'] = 20;
            options['pagingButtonsConfiguration'] = 'auto';
            visualization.draw(control.data,options);
        }

    }
});
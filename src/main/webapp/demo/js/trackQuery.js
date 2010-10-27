var TrackQuery = Class.create({
    initialize: function(container, workspaceUri){
        this.container = $(container);
        this.workspaceUri = workspaceUri;
        this.patients = new Array();
        this.chromosomeRange = '';
        this.geneSymbol = '';
        this.loadControl();
    },

    loadControl: function(){

        var html = "<p><b>Patients and a chromosome range or gene selection must be made before showing query results.</b></p>";

        this.container.innerHTML =html;
       
    },

    onPatientSelection: function(patientArray){
        var control = this;
        control.patients = patientArray;

        if(patientArray.length > 0 && control.chromosomeRange != '')
        {
            control.loadTrackQueryData();
        }
       
    },

    onRangeSelection: function(chromRangeUri){
        var control = this;
        control.chromosomeRange = chromRangeUri;

        if(control.patients.length > 0 && control.chromosomeRange != '')
        {
            control.loadTrackQueryData();
        }
    },

    onGeneSelection: function(geneSymbol){
        var control = this;
        control.geneSymbol = geneSymbol;

        if(control.patients.length > 0 && control.geneSymbol != '')
        {
            control.loadPatientGeneScoresQueryData();
        }

    },

    loadTrackQueryData: function(){
        var control = this;

        var rangeItems = control.chromosomeRange.split("/");
        var chr = rangeItems[0];
        var start = rangeItems[1];
        var end = rangeItems[2];

        var queryString = 'select * where chr=\''+chr+ '\' and start >='+start + ' and start <= ' + end + ' and ( ';
        var first = 0;
        $A(control.patients).each(function(p) {
            for(var i=0;i<p.samples.length; i++)
            {
                if(first == 1)
                {
                    queryString = queryString + ' or ';
                }
                first = 1;
                var s = p.samples[i];
                queryString = queryString + ' sample_id=\'' + s.id + '\'';
            }
        });

        queryString = queryString + ') order by start asc';

        var query = new google.visualization.Query(this.workspaceUri + "/track.tsv/query");
        query.setQuery(queryString);
        query.send(function (response) { control.loadTrackQueryVis(response); });

    },

    loadTrackQueryVis: function(response){
        var control = this;
        $(control.container).innerHTML = "";
        if (response.isError()) {
            alert("Error in query: " + response.getMessage() + " " + response.getDetailedMessage());
            return;
        }
        var data = response.getDataTable();
        var visualization = new google.visualization.Table($(control.container));

        var options = new Array();
          options['page'] = 'enable';
         options['pageSize'] = 20;
        options['pagingButtonsConfiguration'] = 'auto';
        visualization.draw(data,options);

    }
});
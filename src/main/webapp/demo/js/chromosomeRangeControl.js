var ChromosomeRangeControl = Class.create({
    initialize: function(container, svcLocation, chromName,chromStart,chromEnd,startPos,endPos) {
        this.container = Ext.getDom(container);
        this.selectionListeners = new Array();
        this.chromosomes = new Hash();
        this.selectedChromosome = ["chr"+chromName,0];
        this.geneSymbol = '';
        this.startPosition = startPos;
        this.endPosition = endPos;
        this.chromstart = chromStart;
        this.chromend = chromEnd;
        this.radioPanel=null;
        this.flexScrollPanel = null;
        this.rangeControlMask = null;
        this.chromoCombo = null;
        this.svcLocation = svcLocation;

        this.loadChromosomes();
    },

    addSelectionListener: function(listener) {
        this.selectionListeners[this.selectionListeners.length] = listener;
    },

    onRangeSelectionChange: function(chromName, startPos,endPosition){
        if(this.selectedChromosome[0] == "chr"+chromName && this.startPosition == startPos && this.endPosition == endPosition)
            return;


         this.selectedChromosome = ["chr"+chromName,this.chromosomes.get("chr"+chromName)];
         this.startPosition = startPos;
        this.endPosition = endPosition;

        if(this.chromoCombo != null){
            this.chromoCombo.setValue(this.selectedChromosome[0]);
            this.displayRangeControl(false);
  
        }

    },

    getChromInfoQueryHandler: function(){
        var control = this;
        return function(resp){
             control.handleChromInfoQuery(resp);
        }
    },

     handleChromInfoQuery: function(response) {
         var control = this;
            var chromosomeArray = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable());
             for (var i = 0; i < chromosomeArray.length; i++) {
                        var item = chromosomeArray[i];
                        control.chromosomes.set("chr"+item.chr_name, item.chr_length);
             }
            control.displayChromosomes();
     },

    loadChromosomes: function() {
        var control = this;
         var chrom_query = new google.visualization.Query(control.svcLocation + '/addama/systemsbiology.org/datasources/tcgajamboree/fastbreak/chrom_info/query');
        chrom_query.setQuery('select chr_name, chr_length');
        chrom_query.send(control.getChromInfoQueryHandler());
    },

    displayChromosomes: function() {
        var control = this;
        var displayFlex = false;

        var chromosomeArray = new Array();
         var selected = false;
        this.chromosomes.each(function(chromosome) {
            if(control.selectedChromosome[0] == chromosome.key){
                selected=true;
                displayFlex = true;
            }
            
           chromosomeArray[chromosomeArray.length] = [chromosome.value, chromosome.key];

        });

        control.chromoCombo = new Ext.form.ComboBox({
            store: chromosomeArray,
            typeAhead: true,
            mode: 'local',
            forceSelection: true,
            triggerAction: 'all',
            padding: '5 5 5 5',
            width: 75,
            flex: 2
        });

         control.chromoCombo.on('select', function(n){
               control.selectedChromosome = [n.lastSelectionText,n.value];
               control.displayRangeControl();
         });

        if(selected){
            control.chromoCombo.setValue(control.selectedChromosome[0]);
        }

        control.flexScrollPanel = new Ext.Panel({
            align: 'center',
            flex: 10,
            contentEl: this.container
        });

        control.radioPanel = new Ext.Panel({
            height: 80,
            anchor:'100%',
            baseCls:'x-plain',
            layout:'hbox',
            layoutConfig: {
                padding: 5,
                align: 'middle'
            },
            defaults:{margins:'0 5 0 0'},            
            autoShow: true,
            items: [control.chromoCombo,control.flexScrollPanel]
        });

        if(displayFlex){
            control.renderFlexScroll(control.chromstart,control.chromend,control.startPosition,control.endPosition);
        }
             this.selectionListeners.each(function(listener) {
            listener.onChromosomeRangeLoaded();
        });

    },

    displayRangeControl: function(externalChange) {
        var control = this;
         if(externalChange){
             control.startPosition = 0;
             control.endPosition = control.selectedChromosome[1];
         }

        var start = control.startPosition  < control.selectedChromosome[1] ? control.startPosition : control.selectedChromosome[1] - 20000;
        var end = control.endPosition < control.selectedChromosome[1] ? control.endPosition : control.selectedChromosome[1];
        control.renderFlexScroll(0,control.selectedChromosome[1],start,end);

    },

    publishSelection: function(start, end) {
        var control = this;
        this.selectionListeners.each(function(listener) {
            listener.onRangeSelection(control.selectedChromosome[0].substring(3,control.selectedChromosome[0].length), start ,end);
        });
    },

    getRangeSelection: function() {
           return {chr:this.selectedChromosome[0].substring(3),start: this.startPosition ,end: this.endPosition};
    },

    renderFlexScroll: function(minPosition,maxPosition,startPos,endPos){
        var control = this;

        var listener = function(x,dx){
            control.startPosition = x;
            control.endPosition =  parseInt(x) + parseInt(dx);
           // control.publishSelection(control.startPosition, control.endPosition);
        };

        var flexbar = new vq.FlexScroll();

        var data ={DATATYPE : "vq.models.FlexScrollData", CONTENTS : {
            PLOT :{width : 700, height: 50,
           vertical_padding : 10, horizontal_padding: 10, font :"sans", min_position: Math.round(minPosition / 1000) ,
           max_position: Math.round(maxPosition / 1000), scale_multiplier : 1000, container : this.container},
            notifier : listener
        }};
        var length = endPos - startPos;


        flexbar.draw(data);
        if(minPosition != startPos && maxPosition != endPos){
            flexbar.set_position(Math.round(startPos / 1000),Math.round(length / 1000));
        }
       
    }
});

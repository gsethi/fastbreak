var ChromosomeRangeControl = Class.create({
    initialize: function(container, referenceGenomeUri, chromName,chromStart,chromEnd,startPos,endPos) {
        this.container = Ext.getDom(container);
        this.referenceGenomeUri = referenceGenomeUri;
        this.selectionListeners = new Array();
        this.chromosomes = new Hash();
        this.selectedChromosome = "chr"+chromName;
        this.geneSymbol = '';
        this.startPosition = startPos;
        this.endPosition = endPos;
        this.chromstart = chromStart;
        this.chromend = chromEnd;
        this.radioPanel=null;
        this.flexScrollPanel = null;
        this.rangeControlMask = null;
        this.chromoCombo = null;

        this.loadChromosomes();
    },

    addSelectionListener: function(listener) {
        this.selectionListeners[this.selectionListeners.length] = listener;
    },

    onRangeSelectionChange: function(chromName, startPos,endPosition){
        if(this.selectedChromosome == "chr"+chromName && this.startPosition == startPos && this.endPosition == endPosition)
            return;
        
         this.selectedChromosome = "chr"+chromName;
         this.startPosition = startPos;
        this.endPosition = endPosition;

        if(this.chromoCombo != null){
            this.chromoCombo.setValue(this.selectedChromosome);
            this.displayRangeControl(false);
  
        }

    },


    loadChromosomes: function() {
        var control = this;

        Ext.Ajax.request({
            url: this.referenceGenomeUri,
            method: "get",
            success: function(o) {
                var json = Ext.util.JSON.decode(o.responseText);
                if (json && json.items) {
                    for (var i = 0; i < json.items.length; i++) {
                        var item = json.items[i];
                        control.chromosomes.set(item.name, item.uri);
                    }
                }
                control.displayChromosomes();
            }
        });
    },

    displayChromosomes: function() {
        var control = this;
        var displayFlex = false;

        var chromosomeArray = new Array();
         var selected = false;
        this.chromosomes.each(function(chromosome) {
            if(control.selectedChromosome == chromosome.key){
                selected=true;
                displayFlex = true;
            }
            
           chromosomeArray[chromosomeArray.length] = chromosome.key;

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
               control.selectedChromosome = n.value;
               control.displayRangeControl();
         });

        if(selected){
            control.chromoCombo.setValue(control.selectedChromosome);
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
        if(control.flexScrollPanel.getEl() != null) {
            control.rangeControlMask = new Ext.LoadMask(control.flexScrollPanel.getEl(), {msg:"Loading Chromosome Range..."});
            control.rangeControlMask.show();
        }
        Ext.Ajax.request({
             url: this.referenceGenomeUri + "/" + this.selectedChromosome,
             method:"get",
             success:function(o) {
                var json = Ext.util.JSON.decode(o.responseText);
                if (json && json.length) {
                    if(externalChange){
                    control.startPosition = 0;
                    control.endPosition = json.length;
                    }
                    var start = control.startPosition  < json.length ? control.startPosition : json.length - 20000;
                    var end = control.endPosition < json.length ? control.endPosition : json.length;
                    control.renderFlexScroll(0,json.length,start,end);
                }
                 if(control.rangeControlMask != null)
                    control.rangeControlMask.hide();
             }
         });
    },

    publishSelection: function(start, end) {
        var control = this;
        this.selectionListeners.each(function(listener) {
            listener.onRangeSelection(control.selectedChromosome.substring(3,control.selectedChromosome.length), start ,end);
        });
    },

    getRangeSelection: function() {
           return {chr:this.selectedChromosome.substring(3),start: this.startPosition ,end: this.endPosition};
    },

    renderFlexScroll: function(minPosition,maxPosition,startPos,endPos){
        var control = this;

        var listener = function(x,dx){
            control.startPosition = x;
            control.endPosition =  parseInt(x) + parseInt(dx);
           // control.publishSelection(control.startPosition, control.endPosition);
        };

        var flexbar = new isbv.FlexScroll( Ext.getDom(this.container), listener);

        var data ={DATATYPE : "isbv.models.FlexScrollData", CONTENTS : "test"};
        var length = endPos - startPos;

        var options = {plotWidth : 700, plotHeight: 50,
           verticalPadding : 10, horizontalPadding: 10, font :"sans", minPosition: Math.round(minPosition / 1000) ,
           maxPosition: Math.round(maxPosition / 1000), scaleMultiplier : 1000};

        flexbar.draw(data,options);
        if(minPosition != startPos && maxPosition != endPos){
            flexbar.setPosition(Math.round(startPos / 1000),Math.round(length / 1000));
        }
       
    }
});

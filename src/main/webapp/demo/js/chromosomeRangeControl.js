var ChromosomeRangeControl = Class.create({
    initialize: function(container, referenceGenomeUri, chromName,chromStart,chromEnd,startPos,endPos) {
        this.container = Ext.getDom(container);
        this.referenceGenomeUri = referenceGenomeUri;
        this.selectionListeners = new Array();
        this.chromosomes = new Hash();
        this.selectedChromosome = chromName;
        this.geneSymbol = '';
        this.startPosition = startPos;
        this.endPosition = endPos;
        this.chromstart = chromStart;
        this.chromend = chromEnd;
        this.radioPanel=null;

        this.loadChromosomes();
    },

    addSelectionListener: function(listener) {
        this.selectionListeners[this.selectionListeners.length] = listener;
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

        var radioButtonArray = new Array();
        this.chromosomes.each(function(chromosome) {
            var selected = false;
            if(control.selectedChromosome == chromosome.key){
                selected=true;
                displayFlex = true;
            }
            var radioConfig = new Ext.form.Radio({
                boxLabel: chromosome.key,
                name: 'rb-chromosome',
                boxMaxWidth: 20,
                checked: selected
            });
            radioConfig.on('check',function(cb){
                if(radioConfig.checked){
                    control.selectedChromosome = cb.boxLabel;
                    control.displayRangeControl();
                }
            });
            
           radioButtonArray[radioButtonArray.length] = radioConfig;

        });



        control.radioPanel = new Ext.form.FormPanel({
            height: 150,
            padding: '5 5 5 5',
            items: [{
                xtype: 'fieldset',
                align: 'center',
                items:[{
                    xtype:'radiogroup',
                    items:radioButtonArray
                },{
                    align: 'center',
                    items:[ {
                        align: 'center',
                        contentEl: this.container
                    }]
                }]
            }]
        });

        if(displayFlex){
            control.renderFlexScroll(control.chromstart,control.chromend,control.startPosition,control.endPosition);
        }
             this.selectionListeners.each(function(listener) {
            listener.onChromosomeRangeLoaded();
        });




    },

    displayRangeControl: function() {
        var control = this;

         Ext.Ajax.request({
             url: this.referenceGenomeUri + "/" + this.selectedChromosome,
             method:"get",
             success:function(o) {
                var json = Ext.util.JSON.decode(o.responseText);
                if (json && json.length) {
                    control.startPosition = 0;
                    control.endPosition = json.length;
                    control.renderFlexScroll(0,json.length,0,json.length);
                }
             }
         });
    },

    publishSelection: function(start, end) {
        var chromRangeUri = this.selectedChromosome + "/" + start + "/" + end;
        this.selectionListeners.each(function(listener) {
            listener.onRangeSelection(chromRangeUri);
        });
    },


    renderFlexScroll: function(minPosition,maxPosition,startPos,endPos){
        var control = this;

        var listener = function(x,dx){
            control.startPosition = x;
            control.endPosition =  parseInt(x) + parseInt(dx);
            control.publishSelection(control.startPosition, control.endPosition);
        }

        var flexbar = new isbv.FlexScroll( Ext.getDom(this.container), listener);

        var data ={DATATYPE : "isbv.models.FlexScrollData", CONTENTS : "test"};


        var options = {plotWidth : 700, plotHeight: 50,
           verticalPadding : 10, horizontalPadding: 10, font :"sans", minPosition: Math.round(minPosition / 1000) ,
           maxPosition: Math.round(maxPosition / 1000), scaleMultiplier : 1000};

        flexbar.draw(data,options);
        if(minPosition != startPos && maxPosition != endPos){
            flexbar.setPosition(Math.round(startPos / 1000),Math.round(endPos / 1000));
        }

      //  this.selectionListeners.each(function(listener) {
      //      listener.onChromosomeRangeLoaded();
      //  });
        
    }
});

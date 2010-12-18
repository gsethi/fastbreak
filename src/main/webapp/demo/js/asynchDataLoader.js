var AsyncLoader = Class.create({

    initialize: function() {
        console.log("AsyncLoader.initialize");
        this.dataLoaders = [];
    },

    addDataLoader: function(dl) {
        console.log("AsyncLoader.addDataLoader=" + dl.container);
        this.dataLoaders[this.dataLoaders.length] = dl;
        dl.isRequested = false;
        dl.isReady = false;
        dl.isFired = false;
    },

    startLoad: function(callback) {
        console.log("AsyncLoader.startLoad:" + this.dataLoaders.length);

        for (var i = 0; i < this.dataLoaders.length; i++) {
            var dl = this.dataLoaders[i];
            Ext.get(dl.container).on("asynchload", callback, dl);
        }

        var pe = new PeriodicalExecuter(this.onPeriodic, 1);
        pe.dataLoaders = this.dataLoaders;
    },

    onPeriodic: function() {
        console.log("AsyncLoader.onPeriodic:" + this.dataLoaders.length);

        for (var i = 0; i < this.dataLoaders.length; i++) {
            var dl = this.dataLoaders[i];
            console.log("AsyncLoader.onPeriodic:" + dl.container + ":" + dl.isRequested + ":" + dl.isReady + ":" + dl.isFired);

            if (!dl.isRequested) {
                Ext.Ajax.request({ url: "/addama/asynch" + dl.uri, method: "get", success: function(o) {
                    var json = Ext.util.JSON.decode(o.responseText);
                    if (json && json.uri) {
                        dl.asynchUri = json.uri;
                        dl.isRequested = true;
                    }
                }});
                return;
            }

            if (!dl.isReady) {
                Ext.Ajax.request({ url: dl.asynchUri, method: "get", success: function() {
                    dl.isReady = true;
                }});
                return;
            }

            if (!dl.isFired) {
                var ev = Ext.getDom(dl.container).fire("asynchload", dl);
                if (ev) {
                    dl.isFired = true;
                }
            }
        }

        console.log("AsyncLoader.isComplete?");

        for (var c = 0; c < this.dataLoaders.length; c++) {
            var x = this.dataLoaders[c];
            if (!x.isRequested || !x.isReady || !x.isFired) {
                return;
            }
        }

        this.stop();
        console.log("AsyncLoader.stop");

        for (var y = 0; y < this.dataLoaders.length; y++) {
            var q = this.dataLoaders[y];
            console.log("AsyncLoader.query:" + q.container);

            var query = new google.visualization.Query(q.asynchUri);
            query.send(q.callback);            
        }
    }
});

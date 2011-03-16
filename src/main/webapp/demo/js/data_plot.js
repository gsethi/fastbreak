
var empty_params = ['','','','','',''],
    source_list = ['GEXP','METH','CNVR','CLIN'],
    source_map = pv.numerate(source_list),
    link_sources_colors =  pv.colors(
           "#c2c4ff","#9c9ede", "#7375b5", "#4a5584",
    "#e7cb94", "#e7ba52", "#bd9e39",    "#8c6d31",
    "#cedb9c", "#b5cf6b","#8ca252", "#637939",
    "#e7969c", "#d6616b", "#ad494a", "#843c39"),
    linear_unit = 100000,
    proximal_distance = 2.5 * linear_unit,
    paco_obj,
    source_color_scale=  pv.Colors.category10();

node_colors = function(source) { return source_color_scale(source_map[source]);};

function openFastbreakTab() {
       var fastbreak_url = 'http://fastbreak.systemsbiology.net';
              window.open(fastbreak_url,'_blank');
              return false;
}

function loadFilteredData(query_params) {
    network_mask = new Ext.LoadMask('circle-parent', {msg:"Loading Data..."});
    network_mask.show();
    wipeLinearPlot();
    loadNetworkData(query_params,renderCircleData);
}

function wipeLinearPlot(){
    Ext.getCmp('linear-parent').setTitle('Chromosome-level View');
        document.getElementById('linear-panel').innerHTML='';
        Ext.getCmp('linear-parent').collapse(true);
}

function renderCancerPaCo() {
    Ext.StoreMgr.get('pc_table_store').loadData(cancer['sv']);
    paco_obj = paco_draw(document.getElementById('pc_draw'));
}

function renderCircleData() {
    Ext.getCmp('circle-parent').expand(true);
    wedge_plot(document.getElementById('circle-panel'));
    legend_draw(document.getElementById('circle-legend-panel'));
    load_data_store();
    network_mask.hide();
}

function load_data_store() {

    var data = responses['network'].map(function(row) {
        var target = row.alias1.split(':');
        var source = row.alias2.split(':');
  return {target_source: target[1],target_label: target[2],target_chr: target[3].slice(3),
      target_start: target[4],target_stop: target[5],
                                    source_source : source[1],source_label: source[2],source_chr: source[3].slice(3),
      source_start: source[4],source_stop: source[5],
                importance : row.importance, correlation:row.correlation };
                            });
 Ext.StoreMgr.get('data_grid_store').loadData(data);
}

function renderLinearData(chr,start,range_length) {
    Ext.getCmp('linear-parent').expand(true);
    linear_plot(document.getElementById('linear-panel'),chr,start,range_length);
    legend_draw(document.getElementById('linear-legend-panel'));
    Ext.getCmp('linear-parent').setTitle('Chromosome-level View: Chromosome ' + chr);
}

function inter_chrom_click(node) {
    initiateScatterplot(node);
}

function initiateScatterplot(link) {
    loadFeatureData(link,function() {renderScatterPlot(link);});
}

function legend_draw(div) {

    var vis= new pv.Panel()
            .width(150)
            .height(300)
            .left(0)
            .top(20)
            .lineWidth(1)
            .strokeStyle('black')
            .canvas(div);

    var drawPanel = vis.add(pv.Panel)
            .top(20)
            .left(0);

    drawPanel.add(pv.Label)
            .textAlign('left')
            .top(10)
            .left(12)
            .text('Features')
            .font("14px helvetica");

    var color_panel = drawPanel.add(pv.Panel)
            .left(10)
            .top(10);
    var entry =  color_panel.add(pv.Panel)
            .data(source_list.slice(0,3))
            .top(function() { return this.index*12;})
            .height(12);
    entry.add(pv.Bar)
            .left(0)
            .width(12)
            .top(1)
            .bottom(1)
            .fillStyle(function(type) { return source_color_scale(source_map[type]);});
    entry.add(pv.Label)
            .bottom(0)
            .left(20)
            .textAlign('left')
            .textBaseline('bottom')
            .font("11px helvetica");

    var link_panel = drawPanel.add(pv.Panel)
            .top(80)
            .bottom(10)
            .left(10);
    drawPanel.add(pv.Label)
            .top(80)
            .textBaseline('bottom')
            .left(12)
            .text('Links')
            .font('14px helvetica');

    var link = link_panel.add(pv.Panel)
            .data(pv.cross(source_list,source_list))
            .top(function() { return this.index*12;})
            .height(12);

    link.add(pv.Bar)
            .left(0)
            .width(12)
            .top(1)
            .bottom(1)
            .fillStyle(function(type) { return link_sources_colors(source_map[type[0]] * source_list.length + source_map[type[1]]) ;});
    link.add(pv.Label)
            .bottom(0)
            .left(20)
            .textAlign('left')
            .textBaseline('bottom')
            .font('11px helvetica')
            .text(function(types) { return types[1] + ' -> ' + types[0];});

    vis.render();
}


function wedge_plot(div) {
    var width=800, height=800;
    var	ring_radius = width / 20;
    var chrom_keys = ["1","2","3","4","5","6","7","8","9","10",
        "11","12","13","14","15","16","17","18","19","20","21","22","X","Y"];

    function genome_listener(chr) {
            renderLinearData(chr);
        }

    function wedge_listener(feature) {
                    var chr = feature.chr;
                    var start = bpToMb(feature.start) - 2.5;
                    var range_length = bpToMb(feature.end) - start + 2.5;
                    renderLinearData(chr,start,range_length);
                }

        var ucsc_genome_url = 'http://genome.ucsc.edu/cgi-bin/hgTracks';
          var tick_listener = function(feature){
              window.open(ucsc_genome_url + '?position=chr' + feature.chr + ':' + (feature.start) +
                      '-'+ (feature.end ? feature.end : feature.start + linear_unit),'_blank');
              return false;
              };

       var karyotype_tooltip_items = {
           'Karyotype Label' : function(feature) { return  vq.utils.VisUtils.options_map(feature)['label'];},
            Location :  function(feature) { return 'Chr' + feature.chr + ' ' + feature.start + '-' + feature.end;}
        },
        unlocated_tooltip_items = {
            Target :  function(feature) { return feature.sourceNode.source + ' ' + feature.sourceNode.label +
                    (feature.sourceNode.chr ? ' Chr'+ feature.sourceNode.chr : '') +
                    (feature.sourceNode.start ? ' '+ feature.sourceNode.start : '') +
                    (feature.sourceNode.end ? '-'+ feature.sourceNode.end : '');},
            Predictor :  function(feature) { return feature.targetNode.source + ' ' + feature.targetNode.label +
                    (feature.targetNode.chr ? ' Chr'+ feature.targetNode.chr : '') +
                    (feature.targetNode.start ? ' '+ feature.targetNode.start : '') +
                    (feature.targetNode.end ? '-'+ feature.targetNode.end : '');}
        };
    var chrom_leng = vq.utils.VisUtils.clone(annotations['chrom_leng']);

    var ring = vq.utils.VisUtils.clone(parsed_data['features']).filter(function(feature) { return feature.chr != '' && feature.rank != '';})
           .map(function(feature) { return vq.utils.VisUtils.extend(feature,{value:feature.rank, options:feature.weight});});
    var weight_color = pv.Scale.linear(ring.map(function(feature) { return feature.options;})).range('blue','red');

    var ticks = vq.utils.VisUtils.clone(parsed_data['features']);

    var unlocated_map = vq.utils.VisUtils.clone(parsed_data['unlocated']).filter(function(link) { return  link.node1.chr != '';})
            .map(function(link) {
      var node =  vq.utils.VisUtils.extend(link.node2,{ chr:link.node1.chr, start:link.node1.start,end:link.node1.end, value: 0});
        node.sourceNode = vq.utils.VisUtils.extend({},link.node1); node.targetNode = vq.utils.VisUtils.extend({},link.node2);
        return node;
    }).concat(vq.utils.VisUtils.clone(parsed_data['unlocated']).filter(function(link) { return  link.node2.chr != '';})
            .map(function(link) {
      var node =  vq.utils.VisUtils.extend(link.node1,{ chr:link.node2.chr, start:link.node2.start,end:link.node2.end, value: 0});
        node.sourceNode = vq.utils.VisUtils.extend({},link.node1); node.targetNode = vq.utils.VisUtils.extend({},link.node2);
        return node;
    }));

    var data = {
        GENOME: {
            DATA:{
                key_order : chrom_keys,
                key_length : chrom_leng
            },
            OPTIONS: {
                radial_grid_line_width: 1,
                label_layout_style : 'clock',
                listener : genome_listener,
                label_font_style : '20pt helvetica bold'
            }
        },
        TICKS : {
            DATA : {
                data_array : ticks
            },
            OPTIONS :{
                 display_legend : false,
                listener : wedge_listener,
                fill_style : function(tick) {return node_colors(tick.source); },
                tooltip_items : {Tick : function(node) { return node.label+ ' ' + node.source + ' Chr' + node.chr + ' ' + node.start +
                            '-' + node.end;}}
            }
        },
        PLOT: {
            width : width,
            height :  height,
            horizontal_padding : 30,
            vertical_padding : 30,
            container : div,
            enable_pan : false,
            enable_zoom : false,
            show_legend: true,
            legend_include_genome : true,
            legend_corner : 'ne',
            legend_radius  : width / 15
        },
           WEDGE:[
            {
                PLOT : {
                    height : ring_radius/2,
                    type :   'karyotype'
                },
                DATA:{
                    data_array : cytoband
                },
                OPTIONS: {
                    legend_label : 'Karyotype Bands' ,
                    legend_description : 'Chromosomal Karyotype',
                    outer_padding : 10,
//                    fill_style : function(feature) { return feature.value;},
//                    stroke_style : function(feature) { return feature.value;},
                    tooltip_items : karyotype_tooltip_items
//                    listener : wedge_listener
                }
            },{
                    PLOT : {
                    height : ring_radius/2,
                    type :   'scatterplot'
                },
                DATA:{
                    data_array : unlocated_map
                },
                OPTIONS: {
                    legend_label : 'Unmapped Feature Correlates' ,
                    legend_description : 'Feature Correlates with No Genomic Position',
                    outer_padding : 10,
                    base_value : 0,
                    min_value : -1,
                    max_value : 1,
                    radius : 4,
                    draw_axes : false,
                    shape:'dot',
                    fill_style  : function(feature) {return link_sources_colors(source_map[feature.sourceNode.source] * source_list.length + source_map[feature.targetNode.source]); },
                    stroke_style  : function(feature) {return link_sources_colors(source_map[feature.sourceNode.source] * source_list.length + source_map[feature.targetNode.source]); },
                    tooltip_items : unlocated_tooltip_items,
                    listener : initiateScatterplot
                }
            }

        ],

        NETWORK:{
            DATA:{
                data_array : parsed_data['network']
            },
            OPTIONS: {
                outer_padding : 15,
                node_highlight_mode : 'isolate',
                node_fill_style : 'ticks',
                link_line_width : 2,
                node_key : function(node) { return node['label'];},
                node_listener : wedge_listener,
                link_listener: initiateScatterplot,
                link_stroke_style : function(link) {
                    return link_sources_colors(source_map[link.sourceNode.source] * (source_list.length) + source_map[link.targetNode.source]);},
                constant_link_alpha : 0.7,
                node_tooltip_items :  {Node : function(node) { return node.label+ ' ' + node.source + ' Chr' + node.chr + ' ' + node.start +
                            '-' + node.end;}},
                link_tooltip_items :  {
                    'Target' : function(link) { return link.sourceNode.label+ ' ' + link.sourceNode.source + ' Chr' + link.sourceNode.chr + ' ' + link.sourceNode.start +
                            '-' + link.sourceNode.end;},

                    'Predictor' : function(link) { return link.targetNode.label+ ' ' + link.targetNode.source + ' Chr' + link.targetNode.chr + ' ' + link.targetNode.start +
                            '-' + link.targetNode.end;},
                    'Importance' : 'importance',
                    Correlation : 'correlation'
                }
            }
        }
    };
    var circle_vis = new vq.CircVis();
    var dataObject ={DATATYPE : "vq.models.CircVisData", CONTENTS : data };
    circle_vis.draw(dataObject);
    return circle_vis;
}

function bpToMb(bp) {
    return bp != null ? (bp == 0 ? 0 : bp / 1000000): null;
}

function mbpToBp(num) {
    return Math.floor(num* 1000000);
}

function linear_plot(div,chrom,start,range_length) {
     var ucsc_genome_url = 'http://genome.ucsc.edu/cgi-bin/hgTracks';
          var tile_listener = function(feature){
              window.open(ucsc_genome_url + '?position=chr' + feature.chr + ':' + mbpToBp(feature.start) +
                      '-'+ mbpToBp(feature.end),'_blank');
              return false;
              };
    var spot_listener = function(feature){
              window.open(ucsc_genome_url + '?position=chr' + feature.chr + ':' + mbpToBp(feature.start)  +
                      '-'+ mbpToBp(feature.start+ 20),'_blank');
              return false;
              };

     var unlocated_tooltip_items = {
            Target : function(tie) {
            return tie.sourceNode.label + ' ' + tie.sourceNode.source},
        Predictor : function(tie) {
          return tie.targetNode.label + ' ' + tie.targetNode.source },
         'Importance' : 'importance',
         Correlation : 'correlation'

        },
        located_tooltip_items = {
            Target : function(tie) {
            return tie.label + ' ' + tie.source + ' Chr' +tie.chr + ' ' +
                    mbpToBp(tie.start) + (tie.end != null ? '-'+mbpToBp(tie.end) : '');}
        },
        inter_tooltip_items = {
            Target : function(tie) {
            return tie.sourceNode.label + ' ' + tie.sourceNode.source + ' Chr' +tie.sourceNode.chr + ' ' +tie.sourceNode.start +'-'+
                    tie.sourceNode.end;},
        Predictor : function(tie) {
          return tie.targetNode.label + ' ' + tie.targetNode.source +
                  ' Chr' + tie.targetNode.chr+ ' ' +tie.targetNode.start +'-'+tie.targetNode.end;},
         'Importance' : 'importance',
         Correlation : 'correlation'

        };

    var hit_map = parsed_data['unlocated'].filter(function(link) { return  link.node1.chr == chrom;})
            .map(function(link) {
        var node1_clone = vq.utils.VisUtils.extend({importance:link.importance, correlation:link.correlation},link.node1);
                node1_clone.start = bpToMb(node1_clone.start); node1_clone.end = bpToMb(node1_clone.end);
        node1_clone.sourceNode = vq.utils.VisUtils.extend({},link.node1);
        node1_clone.targetNode = vq.utils.VisUtils.extend({},link.node2);
        return node1_clone;
    }).concat(parsed_data['unlocated'].filter(function(link) { return  link.node2.chr == chrom;})
            .map(function(link) {
      var node1_clone = vq.utils.VisUtils.extend({importance:link.importance, correlation:link.correlation},link.node2);
                node1_clone.start = bpToMb(node1_clone.start); node1_clone.end = bpToMb(node1_clone.end);
        node1_clone.sourceNode = vq.utils.VisUtils.extend({},link.node1);
        node1_clone.targetNode = vq.utils.VisUtils.extend({},link.node2);
        return node1_clone;
        }));


    var tie_map = parsed_data['network'].filter(function(link) {
        return link.node1.chr == chrom && link.node2.chr == chrom &&
                Math.abs(link.node1.start - link.node2.start) > proximal_distance;})
            .map(function(link) {
      var node1_clone = vq.utils.VisUtils.extend({importance:link.importance, correlation:link.correlation},link.node1);
        node1_clone.start = link.node1.start <= link.node2.start ?
                link.node1.start : link.node2.start;
        node1_clone.end = link.node1.start <= link.node2.start ? link.node2.start : link.node1.start;
        node1_clone.start = bpToMb(node1_clone.start);node1_clone.end = bpToMb(node1_clone.end);
        node1_clone.sourceNode = vq.utils.VisUtils.extend({},link.node1);
        node1_clone.targetNode = vq.utils.VisUtils.extend({},link.node2);
        node1_clone.importance = link.importance,node1_clone.correlation = link.correlation;
        return node1_clone;
    });

    var neighbor_map = parsed_data['network'].filter(function(link) {
        return link.node1.chr == chrom && link.node2.chr == chrom &&
                Math.abs(link.node1.start - link.node2.start) < proximal_distance;})
            .map(function(link) {
     var node1_clone = vq.utils.VisUtils.extend({importance:link.importance, correlation:link.correlation},link.node1),
        node2_clone = vq.utils.VisUtils.extend({},link.node2);
        node1_clone.start = bpToMb(node1_clone.start);node1_clone.end = bpToMb(node1_clone.end);
        node1_clone.sourceNode = vq.utils.VisUtils.extend({},link.node1);
        node1_clone.targetNode = vq.utils.VisUtils.extend({},link.node2);

        return node1_clone;
    });


    var locations = vq.utils.VisUtils.clone(parsed_data['features']).filter(function(node) { return node.chr == chrom;})
            .map(function (location)  {
    var node =location;
        node.start = bpToMb(node.start);node.end = bpToMb(node.end);
        node.label = location.value;
        return node;
    });
    var node2_locations = parsed_data['network']
            .filter(function(link) {  return link.node2.chr == chrom;})
            .map(function(link) {
        var node = vq.utils.VisUtils.extend({},link.node2);
               	node.start = bpToMb(node.start); node.end = bpToMb(node.end);
        return node;
    });

    locations = locations.concat(node2_locations);

    var location_map = pv.numerate(locations,function(node) { return node.id+'';});

    locations = pv.permute(locations,pv.values(location_map));

    var data_obj = function() { return {
        PLOT :     {
            width:800,
            height:700,
            min_position:1,
            max_position:maxPos,
            vertical_padding:20,
            horizontal_padding:20,
            container : div,
            context_height: 100},
        TRACKS : [
            { type: 'tile',
                label : 'Feature Locations',
                description : 'Genome Location of Features',
                CONFIGURATION: {
                    fill_style : function(node) { return node_colors(node.source);},          //required
                    stroke_style : function(node) { return node_colors(node.source);},          //required
                    track_height : 50,           //required
                    tile_height:20,                //required
                    track_padding: 20,             //required
                    tile_padding:6,              //required
                    tile_overlap_distance:1,    //required
                    notifier:tile_listener,         //optional
                    tooltip_items :  located_tooltip_items     //optional
                },
                data_array : locations
            },  { type: 'glyph',
                label : 'Unmapped Feature Correlates',
                description : '',
                CONFIGURATION: {
                    fill_style : function(hit) { return node_colors(hit.source);},
                    stroke_style : null,
                    track_height : 60,
                    track_padding: 20,
                    tile_padding:6,              //required
                    tile_overlap_distance:.1,    //required
                    shape :  'dot',
                    tile_show_all_tiles : true,
                    radius : 3,
                    notifier:inter_chrom_click,
                  tooltip_items : unlocated_tooltip_items
                },
                data_array : hit_map
            },
                { type: 'glyph',
                label : 'Proximal Feature Predictors',
                description : '',
                CONFIGURATION: {
                    fill_style : function(link) { return link_sources_colors(source_map[link.sourceNode.source] * (source_list.length) + source_map[link.targetNode.source])},
                    stroke_style : null,
                    track_height : 80,
                    track_padding: 20,
                    tile_padding:4,              //required
                    tile_overlap_distance:1,    //required
                    shape :  'dot',
                    tile_show_all_tiles : true,
                    radius : 3,
                    notifier:inter_chrom_click,
                  tooltip_items : inter_tooltip_items
                },
                data_array : neighbor_map
            },
            { type: 'tile',
                label : 'Distal Intra-Chromosomal Correlates',
                description : '',
                CONFIGURATION: {
                    fill_style :  function(link) { return link_sources_colors(source_map[link.sourceNode.source] * (source_list.length) + source_map[link.targetNode.source]);},
                    stroke_style : function(link) { return link_sources_colors(source_map[link.sourceNode.source] * (source_list.length) + source_map[link.targetNode.source]);},
                    track_height : 280,
                    track_padding: 15,             //required
                    tile_height : 2,
                    tile_padding:7,              //required
                    tile_overlap_distance:.1,    //required
                    tile_show_all_tiles : true,
                    notifier : inter_chrom_click,
                    tooltip_items : inter_tooltip_items
                },
                data_array : tie_map
            }]
    }
    };
    var chrom_leng = vq.utils.VisUtils.clone(annotations['chrom_leng']);
    var chr_match = chrom_leng.filter(function(chr_obj) { return chr_obj.chr_name == chrom;});
    var maxPos = Math.ceil(bpToMb(chr_match[0]['chr_length']));

    var lin_browser = new vq.LinearBrowser();
    var lin_data = {DATATYPE: 'vq.models.LinearBrowserData',CONTENTS: data_obj()};

    lin_browser.draw(lin_data);

    if (start != null && start > 0 && range_length != null && range_length > 0) {
        lin_browser.setFocusRange(start,range_length);
    }
      return lin_browser;
}

function scatterplot_draw(div) {

         if (patients['data'].length != 1) {return;}  //prevent null plot
        var data = patients['data'][0];
    var patient_labels = annotations['patients'];
    var f1 = data.f1id, f2 = data.f2id,
            f1values = data.f1values.split(':').map(function(val) {return parseFloat(val);}),
            f2values = data.f2values.split(':').map(function(val) {return parseFloat(val);}),
    f1label = data.f1alias, f2label = data.f2alias;
    var data_array = [];
    for (var i=0; i< f1values.length; i++) {
        var obj = {};
        obj[f1] = f1values[i], obj[f2]=f2values[i], obj['patient_id'] = patient_labels[i];
        data_array.push(obj);
    }

    var tooltip = {};
    tooltip[data.f1alias] = f1,tooltip[data.f2alias] = f2,tooltip['Sample'] = 'patient_id';

       var sp = new vq.ScatterPlot();

        var config ={DATATYPE : "vq.models.ScatterPlotData", CONTENTS : {
            PLOT : {container: div,
                width : 400,
                height: 300,
            vertical_padding : 40, horizontal_padding: 40, font :"14px sans"},
            data_array: data_array,
            xcolumnid: f1,
            ycolumnid: f2,
            valuecolumnid: 'patient_id',
            xcolumnlabel : f1label,
            ycolumnlabel : f2label,
            valuecolumnlabel : 'Sample Id',
            tooltip_items : tooltip
        }};
        sp.draw(config);

    return sp;
}

function paco_draw(div) {
var data = cancer['sv'];

    var    pa_co = new vq.PaCo();

     var dataObject ={DATATYPE : "vq.models.PaCoData", CONTENTS : {
        PLOT: {container: div,
            width : 700,
            height: 500,
            vertical_padding : 30,
            horizontal_padding: 80
        },
        CONFIGURATION : {
            identifier_column : 'gene',
            label_column : 'gene',
            COORD_COLUMN_ARRAY : [
                {id:'COAD',
                    label:'COAD',
                    scale_type : 'linear'
                },
                {id:'GBM',
                    label:'GBM',
                    scale_type : 'linear'
                },
                {id:'OV',
                    label:'OV',
                    scale_type : 'linear'
                }

            ]
        },
                 data_array: data
     }};

     pa_co.draw(dataObject);
    return pa_co;

}
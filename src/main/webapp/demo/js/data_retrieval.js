
var base_query_url = '',
    csacr_base_query_uri = '/google-dsapi-svc/addama/datasources/csacr',
    tcga_base_query_uri = '/google-dsapi-svc/addama/datasources/tcga',
    network_uri = '/mv_crad_feature_networks/query',
    feature_uri = '/v_crad_features/query',
    patient_uri = '/v_crad_patients/query',
    cancer_sv_uri = '/cancer_sv/query',
    feature_data_uri = '/v_crad_patient_values/query',
    query_uri = '/query',
    parsed_data = {network : null,unlocated : null,features : null,unlocated_features:null,located_features:null},
    responses = {network : null},
    patients = {data : null},
    cancer = {sv : null},
    annotations = {'chrom_leng': null,'patients': null};

buildGQLQuery = function(args) {
      var query = 'select alias1, alias2, f1rank, f2rank, feature1id, feature2id, correlation, importance';
    var whst = ' where',
    where = whst;

    if (args['f1_type'] != '' && args['f1_type'] != '*') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f1source = \'' +args['f1_type']+ '\'';
    }
    if (args['f2_type'] != '' && args['f2_type'] != '*') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f2source = \'' +args['f2_type']+ '\'';
    }

    if (args['f1_label'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += '`f1label` = \'' +args['f1_label']+ '\'';
    }
     if (args['f2_label'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += '`f2label` = \'' +args['f2_label']+ '\'';
    }

    if (args['f1_chr'] != '' && args['f1_chr'] != '*') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f1chr = \'' +args['f1_chr']+'\'';
    }
    if (args['f2_chr'] != '' && args['f2_chr'] != '*') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f2chr = \'' +args['f2_chr']+'\'';
    }
    if (args['f1_start'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f1start >= ' +args['f1_start'];
    }
    if (args['f2_start'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f2start >= ' +args['f2_start'];
    }
    if (args['f1_stop'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f1end <= ' +args['f1_stop'];
    }
    if (args['f2_stop'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'f2end <= ' +args['f2_stop'];
    }
    if (args['importance'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += 'importance >= ' +args['importance'];
    }
    if (args['correlation'] != '') {
        where += (where.length > whst.length ? ' and ' : ' ');
        where += '(correlation >= ' +args['correlation'] + ' or correlation <= -' + args['correlation'] +')';
    }

    query += (where.length > whst.length ? where : '');
    query += ' order by '+args['order'] +' DESC';

    query += ' limit '+args['limit'] + ' label `feature1id` \'f1id\', `feature2id` \'f2id\'';

    return query;
};
function loadFeatureData(link,callback) {
    patients = {data : null};

    var timer =  new vq.utils.SyncDatasources(4000,40,callback,patients);
    timer.start_poll();

    var query_str = 'select f1id, f2id, f1alias, f1values, f2alias, f2values ' +
            'where f1id  = ' + link.sourceNode.id + ' and f2id = ' + link.targetNode.id + ' limit 1';
    var patient_query = new google.visualization.Query(base_query_url + tcga_base_query_uri + feature_data_uri);
    patient_query.setQuery(query_str);

    function patientQueryHandle(response) {
          if (!response.isError()) {
              patients['data'] = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable());
          }  else {
              console.log('Patient Data request failed');
          }
    }

    patient_query.send(patientQueryHandle);

}

function loadAnnotations(callback) {

    annotations = {'chrom_leng': null,'patients': null};

    var timer = new vq.utils.SyncDatasources(2000,40,callback,annotations);
    timer.start_poll();
    var chrom_query = new google.visualization.Query(base_query_url + csacr_base_query_uri + '/chrom_info' + query_uri);
    chrom_query.setQuery('select chr_name, chr_length');
    function handleChromInfoQuery(response) {
        annotations['chrom_leng'] = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable());
    }
    chrom_query.send(handleChromInfoQuery);

    var patient_query = new google.visualization.Query(base_query_url + tcga_base_query_uri + patient_uri);
    patient_query.setQuery('limit 1');

    function patientQueryHandle(response) {
          if (!response.isError()) {
              annotations['patients'] = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable())[0]['barcode'].split(':');
          }
    }

    patient_query.send(patientQueryHandle);
}

function loadCancerSV(callback) {

    cancer = {'sv': null};

    var timer = new vq.utils.SyncDatasources(2000,40,callback,cancer);
    timer.start_poll();
    var chrom_query = new google.visualization.Query(base_query_url + tcga_base_query_uri + cancer_sv_uri);
    //chrom_query.setQuery('select chr_name, chr_length');
    function handleChromInfoQuery(response) {
        if (!response.isError()) {
              cancer['sv'] = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable());
          }
    }
    chrom_query.send(handleChromInfoQuery);
}

function parseNetwork(query_params,callback) {

    parsed_data = {network : null,unlocated : null, features : null,unlocated_features:null,located_features:null};
    var timer = new vq.utils.SyncDatasources(4000,40,callback,parsed_data);

    timer.start_poll();

    var whole_net = responses['network'].map(function(row) {
        var node1 = row.alias1.split(':');
        var node2 = row.alias2.split(':');
           return {node1: {id : row.f1id,rank:row.f1rank, source : node1[1], label : node1[2], chr : node1[3].slice(3),
               start: parseInt(node1[4]), end:node1[5] != '' ? parseInt(node1[5]) : parseInt(node1[4])},
            node2: {id : row.f2id,rank:row.f2rank, source : node2[1], label : node2[2], chr : node2[3].slice(3),
                start: parseInt(node2[4]), end:node2[5] != '' ? parseInt(node2[5]) : parseInt(node2[4])},
            importance : row.importance, correlation:row.correlation};
    }
            );
        var located_responses = whole_net.filter(function(feature) {
        return feature.node1.chr != '' && feature.node2.chr != '';});

        var unlocated_responses =  whole_net.filter(function(feature) {
        return feature.node1.chr == '' || feature.node2.chr == '';});

    var feature_ids = {};
    var features = [];
    whole_net.forEach(function(link) {
        if (feature_ids[link.node1.id] == null) {feature_ids[link.node1.id]=1;features.push(vq.utils.VisUtils.extend({value:link.node1.label},link.node1));    }
        if (feature_ids[link.node2.id] == null) {feature_ids[link.node2.id]=1;features.push(vq.utils.VisUtils.extend({value:link.node2.label},link.node2));    }
    });

    parsed_data['features'] = features;
    parsed_data['network'] = located_responses;
    parsed_data['unlocated'] = unlocated_responses;
    parsed_data['unlocated_features'] = vq.utils.VisUtils.clone(features).filter(function(feature) {
            return feature.chr =='';
        });
    parsed_data['located_features'] = vq.utils.VisUtils.clone(features).filter(function(feature) {
            return feature.chr !='';
        });
}


function loadNetworkData(query_params,callback) {
    response_check={data : null};

    var importance =query_params['importance'],
            correlation =query_params['correlation'];

    if (importance.length < 1) importance = 0;
    if (correlation.length < 1) correlation = 0;


    function handleNetworkQuery(response) {
        response_check['data'] = 1;
        responses = {network : null};
        var timer = new vq.utils.SyncDatasources(4000,40,function() {parseNetwork(query_params,callback);},responses);
        timer.start_poll();
        responses['network'] = vq.utils.GoogleDSUtils.dataTableToArray(response.getDataTable());
    }


    var rank_query = new google.visualization.Query(base_query_url + tcga_base_query_uri + network_uri);

    rank_query = new google.visualization.Query(base_query_url + tcga_base_query_uri + network_uri);
    rank_query.setQuery(buildGQLQuery(query_params));
    var timer = new vq.utils.SyncDatasources(10000,40,function() {return null;},response_check);
    timer.start_poll();
    rank_query.send(handleNetworkQuery);
}
 var analysisPanel = null;
function loadDataSets(email, container,tabPanel, userRootName, publicRootName) {
    $(container).innerHTML="";
    var topRootNode = new Ext.tree.TreeNode({
        draggable: false,
        text: "root",
        expandable: true,
        expanded: true,
        children: []
    });

    var userRootNode = new Ext.tree.TreeNode({
        text: userRootName,
        draggable:false,
        expandable: true,
        expanded: true,
        children: []
    });


    var publicRootNode = new Ext.tree.TreeNode({
        text: publicRootName,
        draggable:false,
        expandable: true,
        expanded: true,
        children: []
    });

    topRootNode.appendChild(userRootNode);
    topRootNode.appendChild(publicRootNode);

    var treePanel = new Ext.tree.TreePanel({
        renderTo: container,
        useArrows:false,
        autoScroll:true,
        animate:true,
        enableDD:false,
        containerScroll: true,
        rootVisible: false,
        frame: true,
        iconCls: 'no-icon',
        listeners: {
            render: function(){
                Ext.getBody().on("contextmenu",Ext.emptyFn,null,{preventDefault: true});
            }
        },
        root: topRootNode
    });

    new Ajax.Request("/addama/repositories/workspaces/" + email, {
        method: "get",
        onSuccess: function(o) {
            var json = o.responseJSON;
            if (json && json.items) {
                loadJobs(json.items,tabPanel);
                $A(json.items).each(function(item) {
                    appendDatasetNode(userRootNode, item.name, item.uri,tabPanel);
                });
            }
        }
    });

        new Ajax.Request("/addama/repositories/workspaces/informatics@systemsbiology.org", {
        method: "get",
        onSuccess: function(o) {
            var json = o.responseJSON;
            if (json && json.items) {
                $A(json.items).each(function(item) {
                    appendDatasetNode(publicRootNode, item.name, item.uri,tabPanel);
                });
            }
        }
    });

}

function onItemClick(item){
      if(item.text == 'Change Parameters')
      {
          //just change the card for now and disable
          analysisPanel.getLayout().setActiveItem(0);
      }
    else
      {
          //grow visualization here....get list of patients, also need dataset id
          var test =  Ext.getCmp(item.hiddenName + "." );
          analysisPanel.getLayout().setActiveItem(1);
      }
}

function appendDatasetNode(rootNode, label, uri,tabPanel) {
    var datasetNode = new Ext.tree.TreeNode({
        text: label,
        datasetUri: uri,                                      
        leaf: true,
        draggable:false,
        expandable: false,
        expanded: true,
        iconCls: 'no-icon',
        children: []
    });
    datasetNode.on("click", function(node) {
        var link = "DataAnalysisResult.html?workspace=" + node.attributes.datasetUri;
        tabPanel.add({
            title: node.attributes.text + " Dataset Results",
            closable: true,
            id: node.attributes.text,
            xtype: 'iframepanel',
            border: true,
            width: "100%",
            height: 600,
            defaultSrc: link,
            autoScroll: true
        });
        tabPanel.setActiveTab(node.attributes.text);

    });


    datasetNode.on('contextmenu',function(node){
                 var menuC = new Ext.menu.Menu({
                     renderTo: 'container_treeContextMenu',
                     items:[new Ext.menu.Item({text: 'Analyze', click: loadReferenceGenomes(renderAnalyzeWindow)})]
                 });
            menuC.show(node.ui.getEl());
    });

    rootNode.appendChild(datasetNode);
}

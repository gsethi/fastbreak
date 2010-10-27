/*!
 * Ext JS Library 3.1.0
 * Copyright(c) 2006-2009 Ext JS, LLC
 * licensing@extjs.com
 * http://www.extjs.com/license
 */
/**
 * @class Ext.ux.tree.TreeGridNodeUI
 * @extends Ext.tree.TreeNodeUI
 */
Ext.ux.tree.TreeGridNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    isTreeGridNodeUI: true,

    renderElements : function(n, a, targetNode, bulkRender){
        var t = n.getOwnerTree(),
            cols = t.columns,
            c = cols[0],
            i, buf, len;

        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';
var cb = Ext.isBoolean(a.checked),
            nel,
            href = a.href ? a.href : Ext.isGecko ? "" : "#",
        buf = [
             '<tbody class="x-tree-node">',
                '<tr ext:tree-node-id="', n.id ,'" class="x-tree-node-el ', a.cls, '">',
                    '<td class="x-treegrid-col">',
                        '<span class="x-tree-node-indent">', this.indentMarkup, "</span>",
                        '<img src="', this.emptyIcon, '" class="x-tree-ec-icon x-tree-elbow">',
                        '<img src="', a.icon || this.emptyIcon, '" class="x-tree-node-icon', (a.icon ? " x-tree-node-inline-icon" : ""), (a.iconCls ? " "+a.iconCls : ""), '" unselectable="on">',
                        cb ? ('<input class="x-tree-node-cb" type="checkbox" ' + (a.checked ? 'checked="checked" />' : '/>')) : '',
                        '<a hidefocus="on" class="x-tree-node-anchor" href="', a.href ? a.href : '#', '" tabIndex="1" ',
                            a.hrefTarget ? ' target="'+a.hrefTarget+'"' : '', '>',
                        '<span unselectable="on">', (c.tpl ? c.tpl.apply(a) : a[c.dataIndex] || c.text), '</span></a>',
                    '</td>'
        ];

        for(i = 1, len = cols.length; i < len; i++){
            c = cols[i];
            buf.push(
                    '<td class="x-treegrid-col ', (c.cls ? c.cls : ''), '">',
                        '<div unselectable="on" class="x-treegrid-text"', (c.align ? ' style="text-align: ' + c.align + ';"' : ''), '>',
                            (c.tpl ? c.tpl.apply(a) : a[c.dataIndex]),
                        '</div>',
                    '</td>'
            );
        }

        buf.push(
            '</tr><tr class="x-tree-node-ct"><td colspan="', cols.length, '">',
            '<table class="x-treegrid-node-ct-table" cellpadding="0" cellspacing="0" ><colgroup>'
        );
        for(i = 0, len = cols.length; i<len; i++) {
            buf.push('<col style="width: ', (cols[i].hidden ? 0 : cols[i].width) ,'px;" />');
        }
        buf.push('</colgroup></table></td></tr></tbody>');

        if(bulkRender !== true && n.nextSibling && n.nextSibling.ui.getEl()){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", n.nextSibling.ui.getEl(), buf.join(''));
        }else{
            //alert(targetNode);
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf.join(''));
        }

        this.elNode = this.wrap.childNodes[0];
        this.ctNode = this.wrap.childNodes[1].firstChild.firstChild;
        var cs = this.elNode.firstChild.childNodes;
        this.indentNode = cs[0];
        this.ecNode = cs[1];
        this.iconNode = cs[2];
        this.anchor = cs[3];
        this.textNode = cs[3].firstChild;
        var index = 3;
        if(cb){
            this.checkbox = cs[3];
            // fix for IE6
            this.checkbox.defaultChecked = this.checkbox.checked;
            index++;
        }
        this.anchor = cs[index];
        this.textNode = cs[index].firstChild;
    },

    // private
    animExpand : function(cb){
        this.ctNode.style.display = "";
        Ext.ux.tree.TreeGridNodeUI.superclass.animExpand.call(this, cb);
    }
});

Ext.ux.tree.TreeGridRootNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    isTreeGridNodeUI: true,

    // private
    render : function(){
        if(!this.rendered){
            this.wrap = this.ctNode = this.node.ownerTree.innerCt.dom;
            this.node.expanded = true;
        }

        if(Ext.isWebKit) {
            // weird table-layout: fixed issue in webkit
            var ct = this.ctNode;
            ct.style.tableLayout = null;
            (function() {
                ct.style.tableLayout = 'fixed';
            }).defer(1);
        }
    },


    isChecked :function(){
        return this.checkbox
            ? (Ext.fly(this.checkbox).hasClass('x-tree-node-checked')
                ? true
                :Ext.fly(this.checkbox).hasClass('x-tree-node-grayed')
                    ? this.grayedValue
                    :false)
            :false;
    },


    getChecked : function(a, startNode){
        startNode = startNode || this.root;
        var r = [];
        var f = function(){

            if(this.ui.getChecked()){
                r.push(!a ? this : (a == 'id' ? this.id : this.attributes[a]));
            }
        };
        startNode.cascade(f);
        return r;
    },

    // private
    onCheckChange : function(){
        var checked = this.checkbox.checked;
        // fix for IE6
        this.checkbox.defaultChecked = checked;
        this.node.attributes.checked = checked;
        this.fireEvent('checkchange', this.node, checked);
    },

    /**
 * Sets the checked status of the tree node to the passed value, or, if no value was passed,
 * toggles the checked status. If the node was rendered with no checkbox, this has no effect.
 * @param {Boolean} (optional) The new checked status.
 */
    toggleCheck : function(value){
        var cb = this.checkbox;
        if(cb){
            cb.checked = (value === undefined ? !cb.checked : value);
            this.onCheckChange();
        }
    },


     // private
    onDisableChange : function(node, state){
        this.disabled = state;
        if (this.checkbox) {
            this.checkbox.disabled = state;
        }
        if(state){
            this.addClass("x-tree-node-disabled");
        }else{
            this.removeClass("x-tree-node-disabled");
        }
    },

    destroy : function(){
        if(this.elNode){
            Ext.dd.Registry.unregister(this.elNode.id);
        }
        delete this.node;
    },

    collapse : Ext.emptyFn,
    expand : Ext.emptyFn
});
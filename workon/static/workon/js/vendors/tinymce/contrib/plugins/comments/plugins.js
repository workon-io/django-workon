
(function(exports, undefined) {
    "use strict";
    //#  SECTION TINYMCE INTEGRATION  #//
    var PluginManager = exports.tinymce.PluginManager;
    var Tools = exports.tinymce.util.Tools;
    var Menu = exports.tinymce.ui.Menu;
    var DOMUtils = exports.tinymce.dom.DOMUtils;
    var JSONRequest = exports.tinymce.util.JSONRequest;
    PluginManager.add('comments', function(editor, url) {
        editor.addButton('comments', {
            text: 'Commentaires',
            icon: false,
            onclick: function(sel, node, parent, tooltip) {

                sel = editor.selection.getSel();
                node = sel.focusNode;
                parent = node.parentElement;
                tooltip = "";
                if( parent.dataset.tooltip && parent.dataset.tooltip != 'undefined' ) {
                    tooltip = parent.dataset.tooltip;
                }

                // Open window
                editor.windowManager.open({
                    title: 'Ajouter un commentaire',
                    body: [
                        { type: 'textbox', name: 'title', label: 'Commentaire', value: tooltip }
                    ],
                    onsubmit: function(e) {
                        // Insert content when the window form is submitted
                        // console.log(editor.selection)
                        // editor.insertContent('Title: ' + e.data.title);
                        if(tooltip != "") {
                            if(e.data.title == "") {
                                $(node).unwrap()
                            }
                            else {
                                parent.dataset.tooltip = e.data.title
                            }
                        }
                        else {
                            if(e.data.title != "") {
                                editor.selection.setContent('<span class="lepole-quote" data-tooltip="'+e.data.title+'">' + editor.selection.getContent() + '</span>');
                            }
                        }
                    }
                });
            }
        });
    });
})(this);

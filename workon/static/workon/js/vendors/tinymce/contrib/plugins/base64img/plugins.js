
(function(exports, undefined) {
    "use strict";
    //#  SECTION TINYMCE INTEGRATION  #//
    var PluginManager = exports.tinymce.PluginManager;
    var Tools = exports.tinymce.util.Tools;
    var Menu = exports.tinymce.ui.Menu;
    var DOMUtils = exports.tinymce.dom.DOMUtils;
    var JSONRequest = exports.tinymce.util.JSONRequest;
    PluginManager.add('base64img', function(editor, url) {
        editor.addButton('base64img', {
            text: 'Image Disque',
            icon: false,
            onclick: function(sel, node, parent, tooltip) {

                editor.windowManager.open({
                    //text for dialog
                    title: "Inserer une image depuis l'ordinateur",
                    width: 450,
                    //location:
                    height: 80,
                    //we need a to put a base64 encode image into texteditor
                    html: '<input type="file" class="input" name="bdesk_image" id="image_embed" style="font-size:14px;padding:30px;" accept="image/x-png, image/gif, image/jpeg"/>',
                    buttons: [{
                        text: "Insert",
                        subtype: "primary",
                        onclick: function () {
                            if (window.File && window.FileReader && window.FileList && window.Blob) {
                                var imagefile = document.getElementsByName("bdesk_image")[0].files;
                                var class_filereader = new FileReader();
                                for (var i = 0, f; f = imagefile[i]; i++) {
                                    var filesiz = f.size;
                                }
                                if(filesiz > 512000){
                                    //alert("La taille de l'image est trop importante pour etre inclue ici.");
                                    //(this).parent().parent().close();
                                }
                                class_filereader.onload = function (base64, imgData) {
                                    imgData = base64.target.result;
                                    var img = new Image();
                                    img.src = imgData;

                                    if(img.height > 800 || img.width > 800){
                                        //alert("The image is big in size. The image must be 800x800 in Size");
                                        //(this).parent().parent().close();
                                        editor.selection.setContent("<img style='width:800px;' src='" + imgData + "' />");
                                    }
                                    else {
                                        //console.log("<img src='" + imgData + "' />")
                                        editor.selection.setContent("<img src='" + imgData + "' />");
                                    }
                                }
                                 class_filereader.onerror = function (err) {
                                            console.log("error", err);
                                            console.log(err.getMessage());
                                  };
                                  if (imagefile.length > 0) {
                                            class_filereader.readAsDataURL(imagefile[0]);
                                  }
                                  else {
                                      alert("No File selected");
                                  }
                              }
                            else {
                                alert("Please change your browser to modern one");
                            }
                            (this).parent().parent().close();
                        }
                    },
                    {
                        text: "Close",
                        onclick: function () {
                            (this).parent().parent().close();
                        }
                    }],
                });
            }
        });
    });
})(this);


// /**
//  * Buddyexpress Desk
//  *
//  * @package   Bdesk
//  * @author    Buddyexpress Core Team <admin@buddyexpress.net
//  * @copyright 2014 BUDDYEXPRESS NETWORKS.
//  * @license   Buddyexpress Public License http://www.buddyexpress.net/Licences/bpl/
//  * @link      http://labs.buddyexpress.net/bdesk.b
//  */

// tinymce.PluginManager.add("base64img", function (editor, f) {
// /**
// * Setup buttons for Bdesk Editor
// * @lastchange: $arsalanshah
// */
//    editor.addButton("base64img", {
//       icon: 'image',
//       title: 'Image Embed Upload',
//       cmd: "base64img"
//     });
// /**
// * Init the plugin
// * @lastchange $arsalanshah
// */
//    editor.addCommand("base64img", function () {

//     });
// /**
// * Setup Insert buttons for Bdesk Editor Dialog
// * @lastchange: $arsalanshah
// */
//      editor.addMenuItem("base64img", {
//         cmd: "base64img",
//         context: "insert",
//         text: 'Embed Image',
//         icon: 'image',
//     });
// });
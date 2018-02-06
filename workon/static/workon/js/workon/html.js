// (function ($, selector, load)
// {    
//     selector = '[data-form-widget-html]'

//     load = function($input, config) 
//     {
//         if(!config.apply_format)
//         {
//             config.apply_format = 'html'
//         }
//         if(config.type == "tinymce")
//         {
//             var tinymce_config = config['settings'];
//             id = tinymce_config['elements'];
//             if(id.match(/__prefix__/i)) {
//                 id = $input.attr('id');
//                 tinymce_config['elements'] = id
//             }

//             console.log($input, id, tinymce.editors[id]);

//             if (tinymce.editors[id])
//             {
//                 tinymce.editors[id].destroy()
//             }
//             if (!tinymce.editors[id])
//             {
//                 tinymce_config.setup = function(editor)
//                 {
//                     editor.on('change', function(e)
//                     {
//                         if(config.placeholder && !config.settings.placeholder_disabled)
//                         {
//                             var content = editor.getContent({ format : config.apply_format });
//                             var content_text = $.trim(editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, ''));
//                             if(config.apply_format == "text")
//                             {
//                                 content = $.trim(content.replace('&nbsp;', ''))
//                             }

//                             // if(config.inline)
//                             // {
//                                 placeholder = editor.getElement().getAttribute("placeholder");
//                                 if (typeof placeholder !== 'undefined' && placeholder !== false && content_text == placeholder)
//                                 {
//                                     return;
//                                 }
//                                 $input.html(content).change();
//                             // }
//                         }
//                     });
//                     editor.on('change', function (e) {
//                         editor.save();
//                     });
//                     // editor.on('submit', function(e)
//                     // {
//                     //     var content = editor.getContent({ format : config.apply_format });
//                     //     var content_text = $.trim(editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, ''));
//                     //     if(config.apply_format == "text")
//                     //     {
//                     //         content = $.trim(content.replace('&nbsp;', ''))
//                     //     }
//                     //     placeholder = editor.getElement().getAttribute("placeholder");
//                     //     if (typeof placeholder !== 'undefined' && placeholder !== false && content_text == placeholder)
//                     //     {
//                     //         return;
//                     //     }
//                     //     $input.html(content).change();
//                     // });
//                     editor.on('init', function(e, placeholder)
//                     {
//                         var textarea = editor.getElement();
//                         $(editor.editorContainer).before(textarea);
//                         textarea.style.display = "";
//                         if(config.placeholder && !config.settings.placeholder_disabled)
//                         {
//                             placeholder = textarea.getAttribute("placeholder");
//                             if (typeof placeholder !== 'undefined' && placeholder !== false)
//                             {
//                                 //var label = new Label;
//                                 function onFocus()
//                                 {
//                                     var content = editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, '');
//                                     if(content == '' || content == placeholder)
//                                     {
//                                         editor.focus();
//                                         editor.setContent('');
//                                         tinymce.setActive(editor);
//                                         editor.focus();
//                                         editor.execCommand('mceFocus', false, id);
//                                         $(editor.getElement()).click();
//                                     }
//                                 }

//                                 function onBlur()
//                                 {
//                                     var content = editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, '');
//                                     if(content == '')
//                                     {
//                                         var placeholder_html = '<span style="font-style:italic;color:grey;" class="workon-html_input-placeholder">'+placeholder+'</span>'
//                                         editor.setContent(placeholder_html);
//                                         editor.getElement().innerHTML = placeholder_html
//                                     }
//                                 }
//                                 //tinymce.DOM.bind(label.el, 'click', onFocus);
//                                 editor.on('focus', onFocus);
//                                 editor.on('blur', onBlur);
//                                 onBlur();
//                             }
//                         }

//                     });
//                 }
//                 var instance = tinymce.init(tinymce_config);
//             }
//         }
//     }

//     $.fn.formWidgetHtml = function (options) 
//     {
//         var settings = $.extend({}, options);
//         $.each(this, function (i, element, config, loadScript) 
//         {
//             var $element = $(element);
//             if(!$element[0].formWidgetHtmlInitialized) 
//             {
//                 config = $element.data('form-widget-html');
//                 // if(typeof tinymce === 'undefined') {
//                 //     loadScript = function(url, callback)
//                 //     {
//                 //         var head = document.getElementsByTagName('head')[0];
//                 //         var script = document.createElement('script');
//                 //         script.type = 'text/javascript';
//                 //         script.src = url;
//                 //         script.onreadystatechange = callback;
//                 //         script.onload = callback;
//                 //         head.appendChild(script);
//                 //     }
//                 //     loadScript(config.settings.tinymce_url, function() {
//                 //         console.log('hu');
//                 //         load($element, config);
//                 //     });
//                 // }
//                 // else {
//                 load($element, config);
//                 // }
//                 $element[0].formWidgetHtmlInitialized = true;                
//             }
//         })
//         return this;
//     }

//     $(document).ready(function () 
//     {
//         $(selector).formWidgetHtml();
//     });
//     $(document).on('xhr.response', function(e) {
//         $(selector).formWidgetHtml();
//     });
//     $(document).on('modal.ready', function(e) {
//         $(selector).formWidgetHtml();
//     });
//     $(document).on('tabs.changed', function(e) {
//         console.log(e)
//         $(selector).formWidgetHtml();
//     });
// }(jQuery));
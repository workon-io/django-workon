tinymce.PluginManager.add('placeholder', function(editor) {

    editor.on('init', function(placeholder) {


        placeholder = editor.getElement().getAttribute("placeholder");
        if (typeof placeholder !== 'undefined' && placeholder !== false)
        {
            //var label = new Label;
            function onFocus()
            {
                var content = editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, '');
                if(content == '' || content == placeholder)
                {
                    editor.setContent('');
                }
            }

            function onBlur()
            {
                var content = editor.getContent({ format : 'text' }).replace(/^\s+|\s+$/g, '');
                if(content == '')
                {
                    if(placeholder) editor.setContent(placeholder);
                }
            }
            //tinymce.DOM.bind(label.el, 'click', onFocus);
            editor.on('focus', onFocus);
            editor.on('blur', onBlur);
            onBlur();
        }

    });
});


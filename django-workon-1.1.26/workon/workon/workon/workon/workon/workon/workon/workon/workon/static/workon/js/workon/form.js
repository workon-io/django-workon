(function($) {
    var re = /([^&=]+)=?([^&]*)/g;
    var decodeRE = /\+/g;  // Regex for replacing addition symbol with a space
    var decode = function (str) {return decodeURIComponent( str.replace(decodeRE, " ") );};
    $.parseParams = function(query) {
        if(query == '.') {
            query = document.location.href;
        }
        var params = {}, e;
        while ( e = re.exec(query) ) { 
            var k = decode( e[1] ), v = decode( e[2] );
            if (k.substring(k.length - 2) === '[]') {
                k = k.substring(0, k.length - 2);
                (params[k] || (params[k] = [])).push(v);
            }
            else params[k] = v;
        }
        return params;
    };
})(jQuery);

(function ($, formSelector)
{

    formSelector = '[data-form]';    

    $(document).on('submit', formSelector, function(e, data, form)
    {
        form = $(this);
        clearTimeout(this.submit_timeout);
        form.addClass('loading');
        method = form.attr('method')

        var options = {
            type: method ? method : 'POST',
            url: form.attr('action'),
            success: function(data)
            {
                $.fn.ajaxResponse(data, form);
                form.removeClass('loading');
            },
            error: function(data) {
                try {
                    var html = $(data.responseText);
                    var ifr = $('<iframe class="error500"></iframe>');
                    form.prepend(ifr);
                    ifr[0].contentWindow.document.write(data.responseText);
                }
                catch(e) {
                    form.prepend('<pre class="error500">'+data.responseText+'</pre>');
                }
                form.removeClass('loading').addClass('error500');                
            }
        };
        if(form.attr('enctype') == 'multipart/form-data')
        {
            var formData = new FormData(form[0]);
            if(data) {
                for(var name in data) {
                    formData.append(name, data[name]);
                }
            }
            options.data = formData;
            options.contentType = false;
            options.processData = false;
        }
        else
        {
            options.data = form.serializeArray();
            if(data) {
                for(var name in data) {
                    options.data.push({ name:name, value:data[name] });
                }
            }
        }
        if(this.xhr_unform) {

            var params = $.param(options.data);
            $(this).attr('action', $(this).attr('action')+'?'+params);
            // $(this).attr('action')+'&_action='+this.xhr_unform)
            form.removeClass('loading');
            return true;
        }
        $.ajax(options);

        if(form.data('form')['queryHistory'] == true) 
        { 
            var query = $.param(options.data);
            query = query.replace( /csrfmiddlewaretoken\=[\w\d]+/gi, "" ).replace(/^&/, '');
            query +=  document.location.hash;
            History.pushState({}, null, "?"+query);
            if (history.pushState) {
                var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + query;
                window.history.pushState({path:newurl},'',newurl);
            };
        }
        e.stopPropagation();
        return false;
    });

    $(document).on('change', formSelector+' input, '+
                             formSelector+' select, '+
                             formSelector+' textarea', function(e, form)
    {
        if($(this.form).data('form')['submitOnChanges'] == true) { 
            $(this.form).submit(); 
        }
    });
    $(document).on('keyup', '[data-form] input[type="text"]', function(form)
    {
        if($(this.form).data('form')['submitOnChanges'] == true) { 
          
            form = this.form
            clearTimeout(form.submit_timeout);
            form.submit_timeout = setTimeout(function() { 
                $(form).submit(); 
            }, 1000);
        }
    });
    $(document).on('click', '[data-form] [type="submit"]', function(e, self)
    {
        if($(e.target).is('[data-unform]')) {
            this.form.xhr_unform = $(this).val();
        }
        self = $(this);
        if(self.attr('name') && self.attr('value')) 
        {           
            var data = {} ;
            data[self.attr('name')] = self.attr('value')
            $(this.form).trigger('submit', data);
            e.stopPropagation();
            return false;
        }
    });
    $(document).on('click', '[data-form] [data-page]', function(e)
    {
        $(this).parents('[data-form]').eq(0).trigger('submit', { page: $(this).data('page') });
        e.stopPropagation();
        return false;
    });
    
    $(document).ready(function()
    {
        $('[data-form]').each(function(i, form) 
        {
            if($(form).data('form')['submitOnLoads']) 
            {
                $(form).submit();
            }
        });
    });
   
}( jQuery ));

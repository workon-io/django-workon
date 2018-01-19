(function($, modal, open, wrapper, content, closer, content, oldContainer, addClose, blocker, createModalWrapper)
{
    blocker = false;

    $(document).ready(function() { createModalWrapper(); });

    $(document).on('click', '[data-modal]', function(e) { $(this).modal('open'); });
    $(document).on('click', '[data-modal-close]', function(e) { $(this).modal('close'); });
    $(document).on('dblclick', '[data-dblclick-modal]', function(e) { $(this).modal('open'); });

    $.fn.modal = function(options, trigger, target, body)
    {
        if(options == "open")
        {
            trigger = $(this);
            options = trigger.data('modal') || trigger.data('dblclick-modal');
            target = trigger.data('modal') || trigger.data('dblclick-modal');
            open(options, trigger, target);
        }
        else if(options == "close")
        {
            wrapper.removeClass('active');
            closer.removeClass('active');
            $('body').removeClass('has-modal');
        }
        else {
            open(options, null, options);
        }

    }

    createModalWrapper = function() {

        wrapper = $('<div id="modal-wrapper"></div>').appendTo($('body'));
        content = $('<div id="modal-content"></div>').appendTo(wrapper);
        closer = $('<a id="modal-closer"><i class="icon">close</i></a>').click(function() {
            
            wrapper.removeClass('active');
            closer.removeClass('active');
            $('body').removeClass('has-modal');
        }).appendTo(content);
    }

    open = function(options, trigger, target, body)
    {
        blocker = true;
        // $.fn.modalDefaults.closeOnClick = false;
        body = $('body');
        if(!wrapper) { createModalWrapper(); }
        wrapper.addClass('active loading');
        closer.addClass('active');
        body.addClass('has-modal');
        var target_lower = target.toLowerCase();
        if(target[0] == '#')
        {
            var target = $(target);
            oldContainer = html.parent();
            content.empty().append(target);
            wrapper.removeClass('loading');
            $(content).trigger('modal.ready', {
                content: content,
                wrapper: wrapper,
                target: target
            });
        }
        else if(target_lower.endsWith('.png') || target_lower.endsWith('.jpg') || target_lower.endsWith('.gif'))
        {
            content.empty().append('<div class="modal modal-media large"><img src="'+target+'"/></div>');
            body.addClass('has-modal');
            wrapper.removeClass('loading');
            $(content).trigger('modal.ready', {
                content: content,
                wrapper: wrapper,
                target: target
            });
        }
        else
        {
            oldContainer = null;
            var options = {
                type: 'GET',
                url: target,
                success: function(data)
                {
                    content.html(data);
                    wrapper.removeClass('loading');
                    body.addClass('has-modal');
                    $(content).trigger('modal.ready', {
                        content: content,
                        wrapper: wrapper,
                        xhrdata: data
                    });
                },
                error: function(data) {
                    try {
                        var html = $(data.responseText);
                        content.html('<div class="modal-body"><iframe class="error500"></iframe></div>');
                        content.find('iframe')[0].contentWindow.document.write(data.responseText)
                    }
                    catch(e) {
                        content.html('<div class="modal-body"><pre class="error500">'+data.responseText+'</pre></div>')
                    }
                    wrapper.removeClass('loading').addClass('error500');                
                }
            };
            $.ajax(options);
        }
    }

})(jQuery);
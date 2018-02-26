(function($, modal, dblclickTO, open, wrapper, closer, content, oldContainer, addClose, blocker, createModalWrapper)
{
    blocker = false;

    $(document).ready(function() { createModalWrapper(); });

    $(document).on('click', '[data-modal]', function(e, self) { 
        self = $(this);
        // if(!self.data('dblclick-modal')) {
        self.modal('open'); 
        // }
        // else {
        //     dblclickTO = setTimeout(function() {
        //         self.modal('open');
        //     }, 300);
        // }    
        e.stopPropagation();    
    });
    $(document).on('dblclick', '[data-dblclick-modal]', function(e) { 
        clearTimeout(dblclickTO);
        $(this).modal('open');
    });
    $(document).on('click', '[data-modal-close]', function(e) { 
        $(this).modal('close'); 
    });

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

        closer = $('<div id="modal-closer" data-modal-close><i class="icon">close</i></div>').appendTo($('body'));
        wrapper = $('<div id="modal-wrapper"></div>').appendTo($('body'));
        content = $('<div id="modal-content"></div>').appendTo(wrapper);
    }

    open = function(options, trigger, target, body)
    {
        blocker = true;
        // $.fn.modalDefaults.closeOnClick = false;
        body = $('body');
        if(!wrapper) { createModalWrapper(); }
        wrapper.addClass('active loading').removeClass('error500');
        closer.addClass('active');
        body.addClass('has-modal');
        var target_lower = target.toLowerCase();
        if(target[0] == '#')
        {
            var target = $(target);
            oldContainer = target.parent();
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
            content.html('<div class="modal modal-media"><img src="'+target+'"/></div>');
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
                    body.addClass('has-modal');
                    wrapper.removeClass('loading');
                    $(content).trigger('modal.ready', {
                        content: content,
                        wrapper: wrapper,
                        xhrdata: data
                    });
                },
                error: function(data) {
                    try {
                        var html = $(data.responseText);
                        content.html('<div class="modal"><div class="modal-body"><iframe class="error500"></iframe></div></div>');
                        content.find('iframe')[0].contentWindow.document.write(data.responseText)
                    }
                    catch(e) {
                        content.html('<div class="modal"><div class="modal-body"><pre class="error500">'+data.responseText+'</pre></div></div>')
                    }
                    body.addClass('has-modal');
                    wrapper.removeClass('loading').addClass('error500');
                    $(content).trigger('modal.ready', {
                        content: content,
                        wrapper: wrapper,
                        xhrdata: data
                    });              
                }
            };
            $.ajax(options);
        }
    }

})(jQuery);
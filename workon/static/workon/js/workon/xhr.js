(function ($, formSelector)
{
        
    formSelector = '[data-form]';  
    
    $(document).on('click', '[data-load]', function(e, trigger)
    {
        trigger = $(this).addClass('loading');
        var target = trigger.data('load');
        var options = {
            type: "GET",
            url: target,
            success: function(data) { 
                $.fn.ajaxResponse(data); 
                trigger.removeClass('loading');
            },
            error: function(data) {
                try {
                    var html = $(data.responseText);
                    var ifr = $('<iframe class="error500"></iframe>');
                    trigger.prepend(ifr);
                    ifr[0].contentWindow.document.write(data.responseText);
                }
                catch(e) {
                    trigger.prepend('<pre class="error500">'+data.responseText+'</pre>');
                }
                trigger.removeClass('loading').addClass('error500');                
            }
            
        };
        $.ajax(options);
        e.stopPropagation();
        return false;
    });

    $(document).on('click', '[data-toggle]', function(e)
    {
        var target = $($(this).data('toggle'));
        target.toggle();
        e.stopPropagation();
        return false;
    });

    $.fn.ajaxResponse = function(data, form, trigger, isModal, cb)
    {
        if(data) {

            if(typeof(data) == "object")
            {
                if(data.remove)
                {
                    if(isArray(data.remove)) { for(var i in data.remove) { $(data.remove[i]).remove(); } }
                    if(isDict(data.remove)) { for(var id in data.remove) { $(id).remove(); } }
                    else { $(data.remove).remove(); }
                }
                if(data.load)
                {
                    if(isArray(data.load))
                    {
                    }
                    else {
                        $(document.body).addClass('loading');
                         $.ajax({
                            type: "GET", url: data.load,
                            success: function(data) { 
                                $.fn.ajaxResponse(data); 
                                $(document.body).removeClass('loading');
                            }
                        });
                    }
                }
                if(data.replace)
                {
                    if(isArray(data.replace))
                    {
                        for(var i in data.replace)
                        {
                            var elm = $(data.replace[i]);
                            var old = $('#'+elm.attr('id'));
                            if(old.length)
                            {
                                old.replaceWith(elm);
                            }
                        }
                    }
                    else if(isDict(data.replace))
                    {
                        for(var id in data.replace)
                        {
                            var old = $('#'+id);
                            if(old.length)
                            {
                                old.replaceWith($(data.replace[id]));
                            }
                        }
                    }
                    else {
                        var $elm = $(data.replace)
                        if($elm.attr('id'))
                        {
                            $('#'+$elm.attr('id')).replaceWith($elm);
                        }
                    }
                }
                if(data.replaceInner)
                {
                    if(isArray(data.replaceInner))
                    {
                        for(var i in data.replaceInner)
                        {
                            var elm = $(data.replaceInner[i]);
                            var old = $('#'+elm.attr('id'));
                            if(old.length)
                            {
                                old.html(elm.html());
                            }
                        }
                    }
                    else if(isDict(data.replaceInner))
                    {
                        for(var id in data.replaceInner)
                        {
                            var old = $('#'+id);
                            if(old.length)
                            {
                                old.html($(data.replaceInner[id]).html());
                            }
                        }
                    }
                    else {
                        var $elm = $(data.replaceInner)
                        if($elm.attr('id'))
                        {
                            $('#'+$elm.attr('id')).html($elm.html());
                        }
                    }
                }
                if(data.replaceHTML)
                {
                    if(isDict(data.replaceHTML))
                    {
                        for(var id in data.replaceHTML)
                        {
                            var old = $('#'+id);
                            if(old.length)
                            {
                                old.html(data.replaceHTML[id]);
                            }
                        }
                    }
                }
                if(data.appendTo)
                {
                    if(isDict(data.appendTo))
                    {
                        for(var id in data.appendTo)
                        {
                            var box = $('#'+id);
                            if(box.length)
                            {
                                box.append($(data.appendTo[id]));
                            }
                        }
                    }
                }
                if(data.json)
                {
                    if(isDict(data.json))
                    {
                        for(var id in data.json)
                        {
                            var box = $('#'+id);
                            if(box.length)
                            {   
                                box.empty();
                                // if(!box[0]._has_json_editor) {
                                result = new JSONEditor(box[0], 
                                {
                                    name: id,
                                    mode: 'view',
                                    modes: ['code', 'form', 'text', 'tree', 'view']
                                });
                                // box[0]._has_json_editor = true;
                                //     // result.collapse();
                                // }    
                                // console.log('set', data.json[id])                        
                                result.set(data.json[id]);
                            }
                        }
                    }
                }
                if(data.permanotice)
                {
                    if(isDict(data.permanotice)) { $.fn.notice(data.permanotice, { delay:0 }); }
                    else if(isArray(data.permanotice)) { for(var id in data.permanotice) { $.fn.notice(data.permanotice[id], { delay:0 });  } }
                    else { $.fn.notice(data.notice, { delay:0 }); }
                }
                if(data.notice)
                {
                    if(isDict(data.notice)) { $.fn.notice(data.notice); }
                    else if(isArray(data.notice)) { for(var i in data.notice) { $.fn.notice(data.notice[i]); } }
                    else { $.fn.notice(data.notice); }
                }
                if(data.modal)
                {
                    if(isDict(data.modal)) { $.fn.modal(data.modal); }
                    else if(isArray(data.modal)) { for(var i in data.modal) { $.fn.modal(data.modal); } }
                    else { $.fn.modal(data.modal); }
                }
                if(data.replaceModal)
                {
                    data.leaveModal = true;
                    if(form) form.replaceWith(data.replaceModal);
                }
                if(data.redirectModal)
                {
                    $(modalFormSelector).addClass('loading')
                    data.leaveModal = true;
                    $.get(data.redirectModal, function(data)
                    {
                        if(form) form.replaceWith(data);
                    })
                }
                if(data.redirect)
                {
                    document.location.href = data.redirect;
                    return;
                }
                if(data.callback)
                {
                    window[data.callback](data);
                    if(form) form.modal('close');
                    return;
                }
                if(data.closeModal == true)//form && $(form).data('form')['closeModalOnSucess'])
                {
                    form.modal('close');
                }
                // if(form && data.leaveModal != true)//form && $(form).data('form')['closeModalOnSucess'])
                // {
                //     form.modal('close');
                // }
                if(form && data.formAction)
                {
                    form.attr('action', data.formAction);
                }
            }
            // HTML data Case
            else
            {
                var $data = $(data);
                if(form && $data.data('form'))
                {
                    form.html($data.html());
                    if(form.parent().attr('id') == 'modal-content' ) {
                        form.parent().trigger('modal.ready', {
                            content: form.parent(),
                            wrapper: form.parent().parent(),
                            target: form
                        });
                    }
                }
                // else if($data.is(formSelector) && form)
                // {
                //     if(form) form.html($data.html())
                // }
                else if($data.attr('id'))
                {
                    $('#'+$data.attr('id')).replaceWith($data);
                    // if(form && $(form).data('form')['closeModalOnSucess']) form.modal('close');
                    if(form) form.modal('close');
                }
                else {
                    var nd = document.open("text/html", "replace");
                    nd.write(data);
                    nd.close();
                }
            }
            data._trigger = trigger;
            if (form) { form.trigger('xhr.response', data); }
        }
        data._trigger = trigger;
        $(document).trigger('xhr.response', data);
    }
}( jQuery ));
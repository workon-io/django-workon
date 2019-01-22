(function ($, noticec, offNotice, notices)
{
    notices = {};
    offNotice = function(notice)
    {
        if(notice) {
            clearTimeout(notice[0].workon_notice_to);
            notice.addClass('off').stop().animate({ marginTop: -notice.outerHeight() -parseInt(notice.css('paddingTop')) -parseInt(notice.css('paddingBottom')) }, 250);
            notice[0].workon_notice_to = setTimeout(function() 
            { 
                delete notices[notice[0].workon_notice_html];
                if(notice[0].workon_notice_uid) 
                {
                    delete notices[notice[0].workon_notice_uid];

                } 
                notice.remove(); 
            }, 5000);
        }
    };
    $.fn.notice = function (options, options2, defaults, notice)
    {
        if(options == 'remove') {
            notice = $(this);
            offNotice(notice);
        }
        else {
            defaults = {
                delay: 3000,
                classes: '',
                uid: null,
                removeOthers: false,
                pulse: 'pulse1'
            };
            var body = $('body');
            if(!noticec) {
                noticec = $('<div class="notice-wrapper"></div>').appendTo(body);
            }
            if(typeof options == "object")
            {
                options = $.extend(defaults, options, options2);
            }
            else
            {
                options = $.extend(defaults, {
                    content: options
                }, options2);
            }

            var html = '<div class="notice '+options.classes+'">'+options.content+'</div>';
            if(notices[html])
            {
                notice = notices[html];
                clearTimeout(notice[0].workon_notice_to);
                notice.stop().removeClass('off').css('margin-top', '');
            }
            else if(options.uid && notices[options.uid])
            {
                notice = notices[options.uid];
                clearTimeout(notice[0].workon_notice_to);
                notice.stop().removeClass('off').css('margin-top', '');
                notice.html(options.content);
                notice.attr('class', 'notice '+options.classes);
            }
            else {
                if(options.removeOthers) {
                    $.each(notices, function(i, notice) {
                        offNotice(notice);
                    });
                }
                notice = $(html).on('click', function(self)
                {
                    offNotice(notice);
                });
                notices[html] = notice;
                notice[0].workon_notice_html = html;
                if(options.uid)
                {
                    notices[options.uid] = notice;
                }
                notice[0].workon_notice_uid = options.uid || null;
                noticec.append(notice);
            }
            if(options.delay && options.delay > 0) 
            {
                clearTimeout(notice[0].workon_notice_to);
                notice[0].workon_notice_to = setTimeout(function() { offNotice(notice); }, options.delay);
            }
            else {
                notice[0].workon_notice_to = null;
            }
            if(options.pulse)
            {
                notice.addClass(options.pulse);
                setTimeout(function() { notice.removeClass(options.pulse) }, 2000);
            }

            body.addClass('has-notice');
        }

        return notice;
    };
    $(document).on('click', '[data-notice]', function(e)
    {
        $.fn.notice($(this).data('notice'));
    });
}( jQuery ));

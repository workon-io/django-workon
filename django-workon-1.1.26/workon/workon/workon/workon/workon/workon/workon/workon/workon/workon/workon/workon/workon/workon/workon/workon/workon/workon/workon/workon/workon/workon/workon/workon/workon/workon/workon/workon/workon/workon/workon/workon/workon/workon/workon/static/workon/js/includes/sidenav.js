(function ($, overlay, target)
{
    overlay = null;
    $(document).on('click', '[data-sidenav]', function()
    {
        target = $('#'+$(this).data('sidenav'))
        target.addClass('active');
        if(!overlay) {
            overlay = $('<div class="sidenav-back"></div>').on('click', function() {
                target.removeClass('active');
                $(this).removeClass('active');
                $('body').removeClass('has-sidenav');
            }).appendTo('body');
        }
        $('body').addClass('has-sidenav');
        overlay.addClass('active');
    });

}( jQuery ));
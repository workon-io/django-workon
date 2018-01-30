$(window).on('resize', function() 
{
    $('[data-iframe]').each(function(self) 
    {
        self = $(this);
        self.height( $(window).height() - self.offset().top - parseInt($('main').css('paddingBottom')) );
    });
});
$(document).ready(function() {
    $(window).trigger('resize');
})
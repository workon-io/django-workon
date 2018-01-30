$.fn.modalDefaults = {
    closeOnClick: false
}

$.ajaxSetup({ cache: false });

$(document).on('click', 'li > label a', function(e) {
    e.preventDefault();
    $(this).parent().click()
});

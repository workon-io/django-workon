$(document).on('click', '[data-tree] input', function() 
{
    var ul = $(this).parents('ul').eq(0);
    var tree = ul.parents('[data-tree]').eq(0);
    tree.find('ul').removeClass('active');
    $(this).parents('ul').addClass('active');

});
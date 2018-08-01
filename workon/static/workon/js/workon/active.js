$(document).on('click', '[data-active]', function() 
{
	var target = $(this).data('active');
	if(target) {
		if(target == "parent") {
			target = $(this).parent()
		}	
		else {
			target = $(target);
		}
	}
	(target ? target:$(this)).toggleClass('active');
});

$(document).on('click', '[data-desactive]', function() 
{
	var target = $(this).data('desactive');
	if(target) {
		if(target == "parent") {
			target = $(this).parent()
		}	
		else {
			target = $(target);
		}
	}
	(target ? target:$(this)).removeClass('active');
});
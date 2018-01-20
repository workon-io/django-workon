/*!
 * Waves v0.6.4
 * http://fian.my.id/Waves
 *
 * Copyright 2014 Alfiana E. Sibuea and other contributors
 * Released under the MIT license
 * https://github.com/fians/Waves/blob/master/LICENSE
 */

;(function($) {
    'use strict';
	$(document).on('change', '[data-widget-image] input:file', function(e, field, input) 
	{
		field = $(this).parents('[data-widget-image]').eq(0);
		input = this;
		if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                field.find('.preview img').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(input.files[0]);
        }
	});
})(jQuery);
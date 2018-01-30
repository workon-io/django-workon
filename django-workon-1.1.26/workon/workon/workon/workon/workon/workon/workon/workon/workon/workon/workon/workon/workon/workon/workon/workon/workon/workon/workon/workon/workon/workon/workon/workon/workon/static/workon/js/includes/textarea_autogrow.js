jQuery.fn.autoGrow = function(options)
{
    return this.each(function() {

        if(this.autoGrow) return;
        this.autoGrow = true;

        var settings = jQuery.extend({
            extraLine: true,
        }, options);

        var createMirror = function(textarea) {
            jQuery(textarea).after('<div class="autogrow-textarea-mirror"></div>');
            return jQuery(textarea).next('.autogrow-textarea-mirror')[0];
        }

        var sendContentToMirror = function (textarea) {
            mirror.innerHTML = String(textarea.value)
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\n/g, '<br />') +
                (settings.extraLine? '.<br/>.' : '')
            ;

            if (jQuery(textarea).height() != jQuery(mirror).height())
                jQuery(textarea).height(jQuery(mirror).height());
        }

        var growTextarea = function () {
            sendContentToMirror(this);
        }

        // Create a mirror
        var mirror = createMirror(this);

        // Style the mirror
        mirror.style.display = 'none';
        mirror.style.wordWrap = 'break-word';
        mirror.style.whiteSpace = 'pre-wrap';
        mirror.style.padding = jQuery(this).css('paddingTop') + ' ' +
            jQuery(this).css('paddingRight') + ' ' +
            jQuery(this).css('paddingBottom') + ' ' +
            jQuery(this).css('paddingLeft');

        mirror.style.borderStyle = jQuery(this).css('borderTopStyle') + ' ' +
            jQuery(this).css('borderRightStyle') + ' ' +
            jQuery(this).css('borderBottomStyle') + ' ' +
            jQuery(this).css('borderLeftStyle');

        mirror.style.borderWidth = jQuery(this).css('borderTopWidth') + ' ' +
            jQuery(this).css('borderRightWidth') + ' ' +
            jQuery(this).css('borderBottomWidth') + ' ' +
            jQuery(this).css('borderLeftWidth');

        mirror.style.width = jQuery(this).css('width');
        mirror.style.fontFamily = jQuery(this).css('font-family');
        mirror.style.fontSize = jQuery(this).css('font-size');
        mirror.style.lineHeight = jQuery(this).css('line-height');
        mirror.style.letterSpacing = jQuery(this).css('letter-spacing');

        // Style the textarea
        this.style.overflow = "hidden";
        // this.style.minHeight = this.rows+"em";

        // Bind the textarea's event
        this.onkeyup = growTextarea;
        this.onfocus = growTextarea;

        // Fire the event for text already present
        sendContentToMirror(this);

    });
};

$(document).on('focus', 'textarea', function () {
    $(this).autoGrow();
});
$(document).ready(function() {
    $('.field textarea').autoGrow();
})

// // Textarea Auto Resize
//         var hiddenDiv = $('.hiddendiv').first();
//         if (!hiddenDiv.length) {
//             hiddenDiv = $('<div class="hiddendiv common"></div>');
//             $('body').append(hiddenDiv);
//         }
//         var text_area_selector = 'textarea';

//         function textareaAutoResize($textarea) {
//             // Set font properties of hiddenDiv

//             var fontFamily = $textarea.css('font-family');
//             var fontSize = $textarea.css('font-size');
//             var lineHeight = $textarea.css('line-height');

//             if (fontSize) { hiddenDiv.css('font-size', fontSize); }
//             if (fontFamily) { hiddenDiv.css('font-family', fontFamily); }
//             if (lineHeight) { hiddenDiv.css('line-height', lineHeight); }

//             if ($textarea.attr('wrap') === "off") {
//                 hiddenDiv.css('overflow-wrap', "normal")
//                                    .css('white-space', "pre");
//             }

//             hiddenDiv.text($textarea.val() + '\n');
//             var content = hiddenDiv.html().replace(/\n/g, '<br>');
//             hiddenDiv.html(content);


//             // When textarea is hidden, width goes crazy.
//             // Approximate with half of window size

//             if ($textarea.is(':visible')) {
//                 hiddenDiv.css('width', $textarea.width());
//             }
//             else {
//                 hiddenDiv.css('width', $(window).width()/2);
//             }

//             /**
//                * Resize if the new height is greater than the
//                * original height of the textarea
//                */
//             if ($textarea.data("original-height") <= hiddenDiv.height()) {
//                 $textarea.css('height', hiddenDiv.height());
//             } else if ($textarea.val().length < $textarea.data("previous-length")) {
//                 /**
//                    * In case the new height is less than original height, it
//                    * means the textarea has less text than before
//                    * So we set the height to the original one
//                    */
//                 $textarea.css('height', $textarea.data("original-height"));
//             }
//             $textarea.data("previous-length", $textarea.val().length);
//         }

//         $(text_area_selector).each(function () {
//             var $textarea = $(this);
//             /**
//                * Instead of resizing textarea on document load,
//                * store the original height and the original length
//                */
//             $textarea.data("original-height", $textarea.height());
//             $textarea.data("previous-length", $textarea.val().length);
//         });

//         $(document).on('keyup keydown autoresize', 'textarea', function () {
//             textareaAutoResize($(this));
//         });
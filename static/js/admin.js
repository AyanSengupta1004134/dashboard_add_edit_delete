
$(document).ready(function () {
    $('a').click(function () {

        $('a').addClass('in-active');       // ADD CLASS TO ALL THE TAGS.

        if ($(this).hasClass('in-active')) {    // CHECK IF THE TAG HAS 'in-active' CLASS.

            $(this)
                .removeClass('in-active')
                .addClass('active');
        }
    })
});
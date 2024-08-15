// For navbar scroll
$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('.custom-navbar').addClass('navbar-scroll');
        } else {
            $('.custom-navbar').removeClass('navbar-scroll');
        }
    });
});
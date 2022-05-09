function navbarTogglePin() {
    // For mobile screen size, keep navbar toggle pinned to bottom and extend menu up
    if($(window).width() <= 500) {
        $('#navbarSupportedContent').addClass('order-1');
        $('#navbar-icon').addClass('order-2');
        $('#navbar-brand').addClass('order-3');
        $('#navbar-toggler').addClass('order-4');
        // $('#navbarSupportedContent').removeClass('hidden');
        // $('#navbar-icon').removeClass('hidden');
        // $('#navbar-brand').removeClass('hidden');
        // $('#navbar-toggler').removeClass('hidden');
    }
    // For desktop screen size, keep navbar toggle pinned to top and extend menu down
    if($(window).width() > 500) {
        // $('#navbarSupportedContent').addClass('hidden');
        // $('#navbar-icon').addClass('hidden');
        // $('#navbar-brand').addClass('hidden');
        // $('#navbar-toggler').addClass('hidden');
        $('#navbarSupportedContent').removeClass('order-1');
        $('#navbar-icon').removeClass('order-2');
        $('#navbar-brand').removeClass('order-3');
        $('#navbar-toggler').removeClass('order-4');
        // $('#navbarSupportedContent').removeClass('hidden');
        // $('#navbar-icon').removeClass('hidden');
        // $('#navbar-brand').removeClass('hidden');
        // $('#navbar-toggler').removeClass('hidden');
    }
}

$(document).ready(function(){
    if($(window).width() > 500) {
        navbarTogglePin()
    }

    // Page-loading spinner animation
    $(window).on('pageshow', function() {
        // $('#spinner-img').hide();
        $('.overlay').hide();
      });
  
    // Only display spinning animation if used as PWA, not in browser
    if (window.matchMedia('(display-mode: standalone)').matches) {
        $(window).on('beforeunload', function() {
            // $('#spinner-img').show();
            $('.overlay').show();
        });
    }
});

$(window).on('resize', function() {
    navbarTogglePin()
});
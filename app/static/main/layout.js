function navbarTogglePin() {
    // For mobile screen size, keep navbar toggle pinned to bottom and extend menu up
    if($(window).width() <= 500) {
        $('#navbarSupportedContent').addClass('order-1');
        $('#navbar-brand').addClass('order-2');
        $('#navbar-toggler').addClass('order-3');
    }
    // For desktop screen size, keep navbar toggle pinned to top and extend menu down
    if($(window).width() > 500) {
        $('#navbarSupportedContent').removeClass('order-1');
        $('#navbar-brand').removeClass('order-2');
        $('#navbar-toggler').removeClass('order-3');
    }
}

$(document).ready(function(){
    navbarTogglePin()

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
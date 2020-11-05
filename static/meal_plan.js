$(document).ready(function(){
    $('#clear-mealplan-proceed').click(function () {

        // Execute AJAX to inactivate meals in database
        $.ajax({
            url: '/_clear_meal_plan',
            type: 'POST',

            // Reload Breakfast/Lunch/Dinner cards with meal plan cleared out
            success: function(result) {
                $( "#accordion" ).load(window.location.href + " #accordion" );
            }
        });
    });
});



$(document).ready(function(){

    // User selects button to clear entire meal plan
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

    // User selects button to remove individual recipe from breakast section of meal plan
    $('.remove-bfast-recipe-proceed').click(function () {

        var baseMealId = $(this).attr("name");
        var bfastDiv = document.getElementById("bfast-li-".concat(baseMealId));
        var bfastLength = document.getElementById("bfast-length").innerText;
        var newBfastLength = Number(bfastLength) - 1;
        

        // Execute AJAX to inactivate meals in database
        $.ajax({
            url: '/_remove_bfast_meal_plan',
            type: 'POST',
            data: { recipe_id:baseMealId },

            // Reload Breakfast card with recipe removed
            success: function(result) {
                // BELOW LINE COMMENTED BECAUSE AJAX WOULDN'T FIRE FOR SECONDARY DELETIONS AFTER RELOADING DIV
                //$( "#breakfast-card" ).load(window.location.href + " #breakfast-card" );
                // ALTERNATE SOLUTION BELOW OF DELETING RECIPE DIV AND UPDATING RECIPE COUNT
                bfastDiv.remove();
                document.getElementById("bfast-length").textContent=newBfastLength;
            }
        });
    });

    // User selects button to remove individual recipe from lunch section of meal plan
    $('.remove-lunch-recipe-proceed').click(function () {

        var baseMealId = $(this).attr("name");
        var lunchDiv = document.getElementById("lunch-li-".concat(baseMealId));
        var lunchLength = document.getElementById("lunch-length").innerText;
        var newLunchLength = Number(lunchLength) - 1;

        // Execute AJAX to inactivate meals in database
        $.ajax({
            url: '/_remove_lunch_meal_plan',
            type: 'POST',
            data: { recipe_id:baseMealId },

            // Reload Lunch card with recipe removed
            success: function(result) {
                // BELOW LINE COMMENTED BECAUSE AJAX WOULDN'T FIRE FOR SECONDARY DELETIONS AFTER RELOADING DIV
                //$( "#lunch-card" ).load(window.location.href + " #lunch-card" );
                // ALTERNATE SOLUTION BELOW OF DELETING RECIPE DIV AND UPDATING RECIPE COUNT
                lunchDiv.remove();
                document.getElementById("lunch-length").textContent=newLunchLength;
            }
        });
    });

    // User selects button to remove individual recipe from dinner section of meal plan
    $('.remove-dinner-recipe-proceed').click(function () {

        var baseMealId = $(this).attr("name");
        var dinnerDiv = document.getElementById("dinner-li-".concat(baseMealId));
        var dinnerLength = document.getElementById("dinner-length").innerText;
        var newDinnerLength = Number(dinnerLength) - 1;

        // Execute AJAX to inactivate meals in database
        $.ajax({
            url: '/_remove_dinner_meal_plan',
            type: 'POST',
            data: { recipe_id:baseMealId },

            // Reload Dinner card with recipe removed
            success: function(result) {
                // BELOW LINE COMMENTED BECAUSE AJAX WOULDN'T FIRE FOR SECONDARY DELETIONS AFTER RELOADING DIV
                //$( "#dinner-card" ).load(window.location.href + " #dinner-card" );
                // ALTERNATE SOLUTION BELOW OF DELETING RECIPE DIV AND UPDATING RECIPE COUNT
                dinnerDiv.remove();
                document.getElementById("dinner-length").textContent=newDinnerLength;
            }
        });
    });

});



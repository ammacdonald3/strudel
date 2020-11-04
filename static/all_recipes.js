$(document).ready(function(){
    // Toggle "favorite" button color depending on whether the recipe is one of the user's favorites
    $('.favorite-button').click(function () {
        var $this = $(this);
        var favId = ".".concat($(this).attr("id"));
        if ($this.hasClass("btn-success")) {
            $(favId).addClass("btn-danger")
            $(favId).removeClass("btn-success")
            $(favId).text("Remove from Favorites")
            $.ajax({
                url: '/_favorite',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"checked" },
                success: function(result) {
                    // console.log(result);
                    $( "#favorites-card" ).load(window.location.href + " #favorites-card" );
                }
            });
        } else {
            $(favId).addClass("btn-success")
            $(favId).removeClass("btn-danger")
            $(favId).text("Add to Favorites")
            $.ajax({
                url: '/_favorite',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"unchecked" },
                success: function(result) {
                    $( "#favorites-card" ).load(window.location.href + " #favorites-card" );
                }
            });
        }
    });

    // Toggle "meal plan" button color depending on whether the recipe is on the user's meal plan
    $('.meal-button').click(function () {
        var $this = $(this);
        var baseMealId = $(this).attr("name")
        var mealId = ".".concat($(this).attr("id"));
        if ($this.hasClass("btn-success")) {
            $(mealId).attr("data-toggle", "modal")
            // Update button data attributes if recipe is in "Favorites" section
            if ($this.hasClass("fav-meal-button")) {
                $(mealId).attr("data-target", "#mealtime-modal-fav-".concat(baseMealId))
            };
            // Update button data attributes if recipe is in "Your Recipes" section
            if ($this.hasClass("your-meal-button")) {
                $(mealId).attr("data-target", "#mealtime-modal-your-".concat(baseMealId))
            };
            // Update button data attributes if recipe is in "Editor's Picks" section
            if ($this.hasClass("editor-meal-button")) {
                $(mealId).attr("data-target", "#mealtime-modal-editor-".concat(baseMealId))
            };
            // Update button data attributes if recipe is in "Uploaded by Others" section
            if ($this.hasClass("other-meal-button")) {
                $(mealId).attr("data-target", "#mealtime-modal-other-".concat(baseMealId))
            };

        } else {
            // If recipe is already on the user's meal plan, prompt whether to remove it
            // User selects 'cancel' button (i.e. do not remove recipe from meal plan)
            // BELOW CODE IS COMMENTED OUT BECAUSE MODAL HIDE IS HANDLED IN HTML
            /* $('.meal-button-cancel').click(function () {
                $('.modal').modal('hide');
                return;
            }) */

            // User selects 'proceed' button (i.e. remove recipe from meal plan)
            $('.meal-button-proceed').click(function () {

                // Update color of Meal Plan button
                $(mealId).addClass("btn-success")
                $(mealId).removeClass("btn-danger")

                // Change text of Meal Plan button
                $(mealId).text("Add to Meal Plan")

                // Change button data target so that it renders the Breakfast/Lunch/Dinner modal if clicked again
                $(mealId).attr("data-target", "#mealtime-modal-other-".concat(baseMealId))

                // Execute AJAX to remove from database
                $.ajax({
                    url: '/_meal_plan',
                    type: 'POST',
                    data: { recipe_id:$(this).attr("name"), status:"unchecked" }
                });

            })
        }
    });


    // AJAX for adding recipe to user's meal plan as Breakfast
    $('.meal-breakfast').click(function () {
        var $this = $(this);
        var baseMealId = $(this).attr("name")
        var mealId = ".meal-".concat($(this).attr("name"));
        
        // Update color of Meal Plan button
        $(mealId).removeClass("btn-success")
        $(mealId).addClass("btn-danger")

        // Change button data target so that it renders the Delete Confirm modal if clicked again
        $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/_meal_breakfast',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });

        // Render the "success" modal displaying that the recipe was added to the breakfast meal plan
        var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        $(successModalId).modal('show')

    });

    // AJAX for adding recipe to user's meal plan as Lunch
    $('.meal-lunch').click(function () {
        var $this = $(this);
        var baseMealId = $(this).attr("name")
        var mealId = ".meal-".concat($(this).attr("name"));
        
        // Update color of Meal Plan button
        $(mealId).removeClass("btn-success")
        $(mealId).addClass("btn-danger")

        // Change button data target so that it renders the Delete Confirm modal if clicked again
        $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/meal_lunch',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });

        // Render the "success" modal displaying that the recipe was added to the lunch meal plan
        var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        $(successModalId).modal('show')

    });

    // AJAX for adding recipe to user's meal plan as Dinner
    $('.meal-dinner').click(function () {
        var $this = $(this);
        var baseMealId = $(this).attr("name")
        var mealId = ".meal-".concat($(this).attr("name"));
        
        // Update color of Meal Plan button
        $(mealId).removeClass("btn-success")
        $(mealId).addClass("btn-danger")

        // Change button data target so that it renders the Delete Confirm modal if clicked again
        $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/_meal_dinner',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });

        // Render the "success" modal displaying that the recipe was added to the dinner meal plan
        var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        $(successModalId).modal('show')

    });
});



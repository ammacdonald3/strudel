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

            // If recipe is already on the user's meal plan, prompt whether to remove it
        } else {
            // User selects 'cancel' button (i.e. do not remove recipe from meal plan)
            /* $('.meal-button-cancel').click(function () {
                $('.modal').modal('hide');
                return;
            }) */
            // User selects 'proceed' button (i.e. remove recipe from meal plan)
            $('.meal-button-proceed').click(function () {
                $(mealId).addClass("btn-success")
                $(mealId).removeClass("btn-danger")
                $(mealId).text("Add to Meal Plan")
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
        var mealId = ".meal-".concat($(this).attr("name"));
        console.log(mealId)
        $(mealId).addClass("btn-danger")
        $(mealId).removeClass("btn-success")
        $(mealId).removeAttr("data-toggle")
        $(mealId).removeAttr("data-target")
        $(mealId).text("Remove from Meal Plan")
        $('.modal').modal('hide');
        $.ajax({
            url: '/_meal_breakfast',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });
        bootbox.alert({
            message: "Added to your breakfast meal plan!",
            backdrop: true
        });
    });

    // AJAX for adding recipe to user's meal plan as Lunch
    $('.meal-lunch').click(function () {
        var $this = $(this);
        var mealId = ".meal-".concat($(this).attr("name"));
        console.log(mealId)
        $(mealId).addClass("btn-danger")
        $(mealId).removeClass("btn-success")
        $(mealId).removeAttr("data-toggle")
        $(mealId).removeAttr("data-target")
        $(mealId).text("Remove from Meal Plan")
        $('.modal').modal('hide');
        $.ajax({
            url: '/_meal_lunch',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });
        bootbox.alert({
            message: "Added to your lunch meal plan!",
            backdrop: true
        });
    });

    // AJAX for adding recipe to user's meal plan as Dinner
    $('.meal-dinner').click(function () {
        var $this = $(this);
        var mealId = ".meal-".concat($(this).attr("name"));
        console.log(mealId)
        $(mealId).addClass("btn-danger")
        $(mealId).removeClass("btn-success")
        $(mealId).removeAttr("data-toggle")
        $(mealId).removeAttr("data-target")
        $(mealId).text("Remove from Meal Plan")
        $('.modal').modal('hide');
        $.ajax({
            url: '/_meal_dinner',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        });
        
        var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        console.log(successModalId)
        $(successModalId).modal('show')
    });
});



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
            if ( !confirm("Do you want to delete this item from your meal plan?")) return;
            $(mealId).addClass("btn-success")
            $(mealId).removeClass("btn-danger")
            $(mealId).text("Add to Meal Plan")
            $.ajax({
                url: '/_meal_plan',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"unchecked" }
            });
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
        return alert("Added to breakfast meal plan!")
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
        return alert("Added to lunch meal plan!")
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
        return alert("Added to dinner meal plan!")
    });
});



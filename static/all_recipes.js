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
            // $("#favorites-card").load(" #favorites-card");
            // $( "#favorites-card" ).load(window.location.href + " #favorites-card" );
        } else {
            $(favId).addClass("btn-success")
            $(favId).removeClass("btn-danger")
            $(favId).text("Add to Favorites")
            $.ajax({
                url: '/_favorite',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"unchecked" },
                success: function(result) {
                    // console.log(result);
                    $( "#favorites-card" ).load(window.location.href + " #favorites-card" );
                }
            });
            // $("#favorites-card").load(" #favorites-card");
            // $( "#favorites-card" ).load(window.location.href + " #favorites-card" );
        }
    });

    // Toggle "meal plan" button color depending on whether the recipe is on the user's meal plan
    $('.meal-button').click(function () {
        var $this = $(this);
        var baseMealId = $(this).attr("name")
        var mealId = ".".concat($(this).attr("id"));
        if ($this.hasClass("btn-success")) {
            $(mealId).attr("data-toggle", "modal")
            $(mealId).attr("data-target", "#mealtime-modal-".concat(baseMealId))
/*             $(mealId).addClass("btn-danger")
            $(mealId).removeClass("btn-success")
            $(mealId).text("Remove from Meal Plan") */
            // $('.modal').modal('show');
            // $('.toast').toast('show');
/*             $.ajax({
                url: '/_meal_plan',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"checked" }
            }); */
        } else {
            // $(mealId).attr("onclick", "return confirm('Are you sure that you want to delete {{ recipe.Recipe.recipe_name }} from your meal plan?');")
            if ( !confirm("Do you want to delete this item from your meal plan?")) return alert("Okay, item will not be deleted.")
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
        // $('.toast').toast('hide');
        $('.modal').modal('hide');
        $.ajax({
            url: '/_meal_breakfast',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
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
        // $('.toast').toast('hide');
        $('.modal').modal('hide');
/*         $.ajax({
            url: '/_meal_lunch',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        }); */
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
        // $('.toast').toast('hide');
        $('.modal').modal('hide');
/*         $.ajax({
            url: '/_meal_dinner',
            type: 'POST',
            data: { recipe_id:$(this).attr("name"), status:"checked" }
        }); */
    });
});



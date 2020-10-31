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
        var mealId = ".".concat($(this).attr("id"));
        if ($this.hasClass("btn-success")) {
            $(mealId).addClass("btn-danger")
            $(mealId).removeClass("btn-success")
            $(mealId).text("Remove from Meal Plan")
            $('.toast').toast('show');
            $.ajax({
                url: '/_meal_plan',
                type: 'POST',
                data: { recipe_id:$(this).attr("name"), status:"checked" }
            });
        } else {
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

});



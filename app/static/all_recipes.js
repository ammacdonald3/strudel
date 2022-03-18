$(document).ready(function () {
    // Dispay the number of recipes displayed
    var recipeLength = $('.recipe-item:visible').length
    $('.recipe-length span').text(recipeLength);

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
                data: {
                    recipe_id: $(this).attr("name"),
                    status: "checked"
                },
                success: function (result) {
                    // console.log(result);
                    $("#favorites-card").load(window.location.href + " #favorites-card");
                }
            });
        } else {
            $(favId).addClass("btn-success")
            $(favId).removeClass("btn-danger")
            $(favId).text("Add to Favorites")
            $.ajax({
                url: '/_favorite',
                type: 'POST',
                data: {
                    recipe_id: $(this).attr("name"),
                    status: "unchecked"
                },
                success: function (result) {
                    $("#favorites-card").load(window.location.href + " #favorites-card");
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
                // "Favorites" section
                if ($this.hasClass("fav-meal-button")) {
                    $(mealId).attr("data-target", "#mealtime-modal-fav-".concat(baseMealId))
                }
                // "Your Recipes" section
                if ($this.hasClass("your-meal-button")) {
                    $(mealId).attr("data-target", "#mealtime-modal-your-".concat(baseMealId))
                }
                // "Editor's Picks" section
                if ($this.hasClass("editor-meal-button")) {
                    $(mealId).attr("data-target", "#mealtime-modal-editor-".concat(baseMealId))
                }
                // "Uploaded by Others" section
                if ($this.hasClass("other-meal-button")) {
                    $(mealId).attr("data-target", "#mealtime-modal-other-".concat(baseMealId))
                }

                // Execute AJAX to remove from database
                $.ajax({
                    url: '/_meal_plan',
                    type: 'POST',
                    data: {
                        recipe_id: baseMealId,
                        status: "unchecked"
                    }
                });
                console.log(baseMealId)
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
        // "Favorites" section
        if ($this.hasClass("meal-breakfast-fav")) {
            $(mealId).attr("data-target", "#mealtime-modal-fav-confirm-delete-".concat(baseMealId))
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-breakfast-your")) {
            $(mealId).attr("data-target", "#mealtime-modal-your-confirm-delete-".concat(baseMealId))
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-breakfast-editor")) {
            $(mealId).attr("data-target", "#mealtime-modal-editor-confirm-delete-".concat(baseMealId))
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-breakfast-other")) {
            $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))
        }

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/_meal_breakfast',
            type: 'POST',
            data: {
                recipe_id: $(this).attr("name"),
                status: "checked"
            }
        });

        // Render the "success" modal displaying that the recipe was added to the breakfast meal plan
        // "Favorites" section
        if ($this.hasClass("meal-breakfast-fav")) {
            var successModalId = "#mealtime-modal-fav-success-".concat($(this).attr("name"));
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-breakfast-your")) {
            var successModalId = "#mealtime-modal-your-success-".concat($(this).attr("name"));
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-breakfast-editor")) {
            var successModalId = "#mealtime-modal-editor-success-".concat($(this).attr("name"));
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-breakfast-other")) {
            var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        }
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
        // "Favorites" section
        if ($this.hasClass("meal-lunch-fav")) {
            $(mealId).attr("data-target", "#mealtime-modal-fav-confirm-delete-".concat(baseMealId))
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-lunch-your")) {
            $(mealId).attr("data-target", "#mealtime-modal-your-confirm-delete-".concat(baseMealId))
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-lunch-editor")) {
            $(mealId).attr("data-target", "#mealtime-modal-editor-confirm-delete-".concat(baseMealId))
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-lunch-other")) {
            $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))
        }

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/_meal_lunch',
            type: 'POST',
            data: {
                recipe_id: $(this).attr("name"),
                status: "checked"
            }
        });

        // Render the "success" modal displaying that the recipe was added to the lunch meal plan
        // "Favorites" section
        if ($this.hasClass("meal-lunch-fav")) {
            var successModalId = "#mealtime-modal-fav-success-".concat($(this).attr("name"));
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-lunch-your")) {
            var successModalId = "#mealtime-modal-your-success-".concat($(this).attr("name"));
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-lunch-editor")) {
            var successModalId = "#mealtime-modal-editor-success-".concat($(this).attr("name"));
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-lunch-other")) {
            var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        }
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
        // "Favorites" section
        if ($this.hasClass("meal-dinner-fav")) {
            $(mealId).attr("data-target", "#mealtime-modal-fav-confirm-delete-".concat(baseMealId))
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-dinner-your")) {
            $(mealId).attr("data-target", "#mealtime-modal-your-confirm-delete-".concat(baseMealId))
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-dinner-editor")) {
            $(mealId).attr("data-target", "#mealtime-modal-editor-confirm-delete-".concat(baseMealId))
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-dinner-other")) {
            $(mealId).attr("data-target", "#mealtime-modal-other-confirm-delete-".concat(baseMealId))
        }

        // Change text of Meal Plan button
        $(mealId).text("Remove from Meal Plan")

        // Hide the open modal (which allows user to select Breakfast/Lunch/Dinner)
        $('.modal').modal('hide');

        // Execute AJAX to add to database
        $.ajax({
            url: '/_meal_dinner',
            type: 'POST',
            data: {
                recipe_id: $(this).attr("name"),
                status: "checked"
            }
        });

        // Render the "success" modal displaying that the recipe was added to the dinner meal plan
        // "Favorites" section
        if ($this.hasClass("meal-dinner-fav")) {
            var successModalId = "#mealtime-modal-fav-success-".concat($(this).attr("name"));
        }
        // "Your Recipes" section
        if ($this.hasClass("meal-dinner-your")) {
            var successModalId = "#mealtime-modal-your-success-".concat($(this).attr("name"));
        }
        // "Editor's Picks" section
        if ($this.hasClass("meal-dinner-editor")) {
            var successModalId = "#mealtime-modal-editor-success-".concat($(this).attr("name"));
        }
        // "Uploaded by Others" section
        if ($this.hasClass("meal-dinner-other")) {
            var successModalId = "#mealtime-modal-other-success-".concat($(this).attr("name"));
        }
        $(successModalId).modal('show')

    });


    // meal filters function
    $.fn.mealFilters = function(){ 
        if($('.meal-uncategorized-check').is(":checked"))
            $('.meal-uncategorized').show()
        else
            $('.meal-uncategorized').hide()

        if($('.breakfast-check').is(":checked") && $('.lunch-check').is(":checked") && $('.dinner-check').is(":checked"))
            $('.breakfast').show(),
            $('.lunch').show(),
            $('.dinner').show(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').show(),
            $('.breakfast-lunch-dinner').show();
        else if(!$('.breakfast-check').is(":checked") && !$('.lunch-check').is(":checked") && !$('.dinner-check').is(":checked"))
            $('.breakfast').hide(),
            $('.lunch').hide(),
            $('.dinner').hide(),
            $('.breakfast-lunch').hide(),
            $('.breakfast-dinner').hide(),
            $('.lunch-dinner').hide(),
            $('.breakfast-lunch-dinner').hide();
        else if($('.breakfast-check').is(":checked") && !$('.lunch-check').is(":checked") && !$('.dinner-check').is(":checked"))
            $('.breakfast').show(),
            $('.lunch').hide(),
            $('.dinner').hide(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').hide(),
            $('.breakfast-lunch-dinner').show();
        else if(!$('.breakfast-check').is(":checked") && $('.lunch-check').is(":checked") && !$('.dinner-check').is(":checked"))
            $('.breakfast').hide(),
            $('.lunch').show(),
            $('.dinner').hide(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').hide(),
            $('.lunch-dinner').show(),
            $('.breakfast-lunch-dinner').show();
        else if(!$('.breakfast-check').is(":checked") && !$('.lunch-check').is(":checked") && $('.dinner-check').is(":checked"))
            $('.breakfast').hide(),
            $('.lunch').hide(),
            $('.dinner').show(),
            $('.breakfast-lunch').hide(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').hide(),
            $('.breakfast-lunch-dinner').show();
        else if($('.breakfast-check').is(":checked") && $('.lunch-check').is(":checked") && !$('.dinner-check').is(":checked"))
            $('.breakfast').show(),
            $('.lunch').show(),
            $('.dinner').hide(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').show(),
            $('.breakfast-lunch-dinner').show();
        else if($('.breakfast-check').is(":checked") && !$('.lunch-check').is(":checked") && $('.dinner-check').is(":checked"))
            $('.breakfast').show(),
            $('.lunch').hide(),
            $('.dinner').show(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').show(),
            $('.breakfast-lunch-dinner').show();
        else if(!$('.breakfast-check').is(":checked") && $('.lunch-check').is(":checked") && $('.dinner-check').is(":checked"))
            $('.breakfast').hide(),
            $('.lunch').show(),
            $('.dinner').show(),
            $('.breakfast-lunch').show(),
            $('.breakfast-dinner').show(),
            $('.lunch-dinner').show(),
            $('.breakfast-lunch-dinner').show();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    }


    // Show or hide meal elements based on meal type user-filtering
    $('.breakfast-check').click(function () {
        $.fn.mealFilters();
    })

    $('.lunch-check').click(function () {
        $.fn.mealFilters();
    })

    $('.dinner-check').click(function () {
        $.fn.mealFilters();
    })

    $('.meal-uncategorized-check').click(function () {
        $.fn.mealFilters();
    })


    // dietary restrictions function
    $.fn.dietaryFilters = function(){ 
        if($('.no-diet-check').is(":checked"))
            $('.no-diet').show()
        else
            $('.no-diet').hide()

        if($('.vegan-check').is(":checked") && $('.vegetarian-check').is(":checked") && $('.gluten-check').is(":checked"))
            $('.vegan').show(),
            $('.vegetarian').show(),
            $('.gluten').show(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').show(),
            $('.vegan-vegetarian-gluten').show();
        else if(!$('.vegan-check').is(":checked") && !$('.vegetarian-check').is(":checked") && !$('.gluten-check').is(":checked"))
            $('.vegan').hide(),
            $('.vegetarian').hide(),
            $('.gluten').hide(),
            $('.vegan-vegetarian').hide(),
            $('.vegan-gluten').hide(),
            $('.vegetarian-gluten').hide(),
            $('.vegan-vegetarian-gluten').hide();
        else if($('.vegan-check').is(":checked") && !$('.vegetarian-check').is(":checked") && !$('.gluten-check').is(":checked"))
            $('.vegan').show(),
            $('.vegetarian').hide(),
            $('.gluten').hide(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').hide(),
            $('.vegan-vegetarian-gluten').show();
        else if(!$('.vegan-check').is(":checked") && $('.vegetarian-check').is(":checked") && !$('.gluten-check').is(":checked"))
            $('.vegan').hide(),
            $('.vegetarian').show(),
            $('.gluten').hide(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').hide(),
            $('.vegetarian-gluten').show(),
            $('.vegan-vegetarian-gluten').show();
        else if(!$('.vegan-check').is(":checked") && !$('.vegetarian-check').is(":checked") && $('.gluten-check').is(":checked"))
            $('.vegan').hide(),
            $('.vegetarian').hide(),
            $('.gluten').show(),
            $('.vegan-vegetarian').hide(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').hide(),
            $('.vegan-vegetarian-gluten').show();
        else if($('.vegan-check').is(":checked") && $('.vegetarian-check').is(":checked") && !$('.gluten-check').is(":checked"))
            $('.vegan').show(),
            $('.vegetarian').show(),
            $('.gluten').hide(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').show(),
            $('.vegan-vegetarian-gluten').show();
        else if($('.vegan-check').is(":checked") && !$('.vegetarian-check').is(":checked") && $('.gluten-check').is(":checked"))
            $('.vegan').show(),
            $('.vegetarian').hide(),
            $('.gluten').show(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').show(),
            $('.vegan-vegetarian-gluten').show();
        else if(!$('.vegan-check').is(":checked") && $('.vegetarian-check').is(":checked") && $('.gluten-check').is(":checked"))
            $('.vegan').hide(),
            $('.vegetarian').show(),
            $('.gluten').show(),
            $('.vegan-vegetarian').show(),
            $('.vegan-gluten').show(),
            $('.vegetarian-gluten').show(),
            $('.vegan-vegetarian-gluten').show();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    }

    // Show or hide diet elements based on user-filtering
    $('.vegan-check').click(function () {
        $.fn.dietaryFilters();
    })

    $('.vegetarian-check').click(function () {
        $.fn.dietaryFilters();
    })

    $('.gluten-check').click(function () {
        $.fn.dietaryFilters();
    })

    $('.no-diet-check').click(function () {
        $.fn.dietaryFilters();
    })


    
    
    // Show or hide cook time elements based on user-filtering
    $('.total-time-30-check').click(function () {
        if($('.total-time-30-check').is(":checked"))   
            $('.total-time-30').show();
        else
            $('.total-time-30').hide();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    })

    $('.total-time-60-check').click(function () {
        if($('.total-time-60-check').is(":checked"))   
            $('.total-time-60').show();
        else
            $('.total-time-60').hide();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    })

    $('.total-time-90-check').click(function () {
        if($('.total-time-90-check').is(":checked"))   
            $('.total-time-90').show();
        else
            $('.total-time-90').hide();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    })

    $('.total-time-over-90-check').click(function () {
        if($('.total-time-over-90-check').is(":checked"))   
            $('.total-time-over-90').show();
        else
            $('.total-time-over-90').hide();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    })

    $('.favorite-check').click(function () {
        if($('.favorite-check').is(":checked"))   
            $('.not-favorite').hide();
        else
             $('.not-favorite').show();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
    })

    $('.user-recipe-check').click(function () {
        if($('.user-recipe-check').is(":checked"))   
            //$('.user-recipe').show(),
            $('.not-user-recipe').hide();
        else
            //$('.user-recipe').show(),
            $('.not-user-recipe').show();
        var recipeLength = $('.recipe-item:visible').length
        $('.recipe-length span').text(recipeLength);
        // else
        //     $('.user-recipe').hide();
    })
    

});


//Get the button
let mybutton = document.getElementById("btn-back-to-top");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (
    document.body.scrollTop > 20 ||
    document.documentElement.scrollTop > 20
  ) {
    mybutton.style.display = "block";
  } else {
    mybutton.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
mybutton.addEventListener("click", backToTop);

function backToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
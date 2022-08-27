var MaxIngredientInputs = 12; //maximum input boxes allowed
var AddIngredientButton = $("#addingredientfield"); //Add button ID
var x = $('.IngredientInputsWrapper').length;

var StepInputsWrapper = $("#StepInputsWrapper"); //Input boxes wrapper ID
var AddStepButton = $("#addstepfield"); //Add button ID
var y = $('.StepInputsWrapper').length;

// Below function used to identify next increment value of ingreident input boxes. Based on count() function from Flask route representing the number of ingredients already assigned to the existing recipe.
function ingredientFunc(ingredient_count) {
    IngredientFieldCount = ingredient_count
}

// Below function used to identify next increment value of step input boxes. Based on count() function from Flask route representing the number of steps already assigned to the existing recipe.
function stepFunc(step_count) {
    StepFieldCount = step_count
}

$(AddIngredientButton).click(function (e) //on add input button click
    {
        //Get current count of ingredients
        var ing_count = $('#ing_count').val();
        
        //Update ingredient count to += 1
        ing_count ++;
        $('#ing_count').val(ing_count);

        //if(x <= MaxInputs) //max input box allowed
        if (x <= IngredientFieldCount) {
            IngredientFieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><div class="row"><div class="form-group col-lg-2">Ingredient ' + IngredientFieldCount + '</div><div class="form-group col-lg-7"><input name="ingredient_desc' + IngredientFieldCount + '" class="form-control col" placeholder="Ingredient ' + IngredientFieldCount + '"></div><div class="form-group col-lg-3"><button class="removeclass btn btn-danger col">Delete</button></div></div></div>').insertBefore(IngredientInputsLine);
            x++; //text box increment
        }
        return false;
    });   

$(AddStepButton).click(function (g) //on add input button click
    {
        //Get current count of steps
        var stepCount = $('#step_count').val();
        
        //Update step count to += 1
        stepCount ++;
        $('#step_count').val(stepCount);

        //if(x <= MaxInputs) //max input box allowed
        if (y <= StepFieldCount) {
            StepFieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><div class="row"><div class="form-group col-lg-1">Step ' + StepFieldCount + '</div><div class="form-group col-lg-8"><input name="recipe_step' + StepFieldCount + '" class="form-control col" placeholder="Step ' + StepFieldCount + '"></div><div class="form-group col-lg-3"><button class="removeclass btn btn-danger col">Delete</button></div></div></div>').insertBefore(StepInputsLine);
            y++; //text box increment
        }
        return false;
    });

//Remove "ingredient" text box
$("body").on("click", ".ingremoveclass", function (e) { //user click on remove text
    //Get current count of ingredients
    var ingCount = $('#ing_count').val();
        
    //Update ingredient count to -= 1
    ingCount --;

    $('#ing_count').val(ingCount);
    if (x > 1) {
        $(this).parent('div').parent('div').parent('div').remove(); //remove text box
        x--; //decrement textbox
    }
    return false;
})

// Remove "recipe step" textbox
$("body").on("click", ".stepremoveclass", function (e) { //user click on remove text
    //Get current count of steps
    var stepCount = $('#step_count').val();
        
    //Update ingredient count to -= 1
    stepCount --;

    $('#step_count').val(stepCount);
    if (y > 1) {
        $(this).parent('div').parent('div').parent('div').remove(); //remove text box
        y--; //decrement textbox
    }
    return false;
})

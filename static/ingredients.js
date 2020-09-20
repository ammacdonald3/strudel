var MaxIngredientInputs = 12; //maximum input boxes allowed
var IngredientInputsWrapper = $("#IngredientInputsWrapper"); //Input boxes wrapper ID
var AddIngredientButton = $("#addingredientfield"); //Add button ID

var x = IngredientInputsWrapper.length; //initial text box count
var IngredientFieldCount = 1; //to keep track of text box added


var MaxStepInputs = 12; //maximum input boxes allowed
var StepInputsWrapper = $("#StepInputsWrapper"); //Input boxes wrapper ID
var AddStepButton = $("#addstepfield"); //Add button ID
    
var y = StepInputsWrapper.length; //initial text box count
var StepFieldCount = 1; //to keep track of text box added

$(AddIngredientButton).click(function (e) //on add input button click
    {
        //if(x <= MaxInputs) //max input box allowed
        if (x <= IngredientFieldCount) {
            IngredientFieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><div class="row"><div class="form-group col-lg-2">Ingredient ' + IngredientFieldCount + '</div><div class="form-group col-lg-7"><input name="ingredient_desc' + IngredientFieldCount + '" class="form-control col" placeholder="Ingredient ' + IngredientFieldCount + '"></div><div class="form-group col-lg-3"><button class="removeclass btn btn-danger col">Delete</button></div></div></div>').insertBefore(IngredientInputsWrapper);
            x++; //text box increment
        }
        return false;
    });   

$(AddStepButton).click(function (g) //on add input button click
    {
        //if(x <= MaxInputs) //max input box allowed
        if (y <= StepFieldCount) {
            StepFieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><div class="row"><div class="form-group col-lg-1">Step ' + StepFieldCount + '</div><div class="form-group col-lg-8"><input name="recipe_step' + StepFieldCount + '" class="form-control col" placeholder="Step ' + StepFieldCount + '"></div><div class="form-group col-lg-3"><button class="removeclass btn btn-danger col">Delete</button></div></div></div>').insertBefore(StepInputsWrapper);
            y++; //text box increment
        }
        return false;
    });


$("body").on("click", ".removeclass", function (e) { //user click on remove text
    console.log(x);
    if (x > 1) {
        console.log(x);
        $(this).parent('div').parent('div').parent('div').remove(); //remove text box
        x--; //decrement textbox
    }
    return false;
})



var MaxIngredientInputs = 12; //maximum input boxes allowed
var IngredientInputsWrapper = $("#IngredientInputsWrapper"); //Input boxes wrapper ID
var AddIngredientButton = $("#addingredientfield"); //Add button ID

var x = IngredientInputsWrapper.length; //initial text box count
var IngredientFieldCount = 1; //to keep track of text box added


var MaxStepInputs = 12; //maximum input boxes allowed
var StepInputsWrapper = $("#StepInputsWrapper"); //Input boxes wrapper ID
var AddStepButton = $("#addstepfield"); //Add button ID
    
var x = StepInputsWrapper.length; //initial text box count
var StepFieldCount = 1; //to keep track of text box added

$(AddIngredientButton).click(function (e) //on add input button click
    {
        //if(x <= MaxInputs) //max input box allowed
        if (x <= IngredientFieldCount) {
            IngredientFieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><p>Ingredient ' + IngredientFieldCount + '</p><div class="row"><div class="form-group col-sm"><input type="text" name="ingredient_qty' + IngredientFieldCount + '" id="ingredient_qty' + IngredientFieldCount + '" placeholder="Qty ' + IngredientFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><input type="text" name="ingredient_measurement' + IngredientFieldCount + '" id="ingredient_measurement' + IngredientFieldCount + '" placeholder="Measurement ' + IngredientFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><input type="text" name="ingredient_desc' + IngredientFieldCount + '" id="ingredient_desc' + IngredientFieldCount + '" placeholder="Ingredient' + IngredientFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><button class="removeclass btn btn-outline-danger col">Delete</button></div></div></div>').insertBefore(IngredientInputsWrapper);
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
            $('<div class="form-group"><p>Ingredient ' + StepFieldCount + '</p><div class="row"><div class="form-group col-sm"><input type="text" name="ingredient_qty' + StepFieldCount + '" id="ingredient_qty' + StepFieldCount + '" placeholder="Qty ' + StepFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><input type="text" name="ingredient_measurement' + StepFieldCount + '" id="ingredient_measurement' + StepFieldCount + '" placeholder="Measurement ' + StepFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><input type="text" name="ingredient_desc' + StepFieldCount + '" id="ingredient_desc' + StepFieldCount + '" placeholder="Ingredient' + StepFieldCount + '" class="form-control col"/></div><div class="form-group col-sm"><button class="removeclass btn btn-outline-danger col">Delete</button></div></div></div>').insertBefore(StepInputsWrapper);
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
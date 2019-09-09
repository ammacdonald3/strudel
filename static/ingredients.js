var MaxInputs = 12; //maximum input boxes allowed
var InputsWrapper = $("#InputsWrapper"); //Input boxes wrapper ID
var AddButton = $("#addfield"); //Add button ID

var x = InputsWrapper.length; //initial text box count
var FieldCount = 1; //to keep track of text box added

$(AddButton).click(function (e) //on add input button click
    {
        //if(x <= MaxInputs) //max input box allowed
        if (x <= FieldCount) {
            FieldCount++; //text box added increment
            //add input box
            $('<div class="form-group"><p>Ingredient ' + FieldCount + '</p><div class="form-row"><input type="text" name="ingredient_qty' + FieldCount + '" id="ingredient_qty' + FieldCount + '" placeholder="Qty ' + FieldCount + '" class="form-control col"/><input type="text" name="ingredient_measurement' + FieldCount + '" id="ingredient_measurement' + FieldCount + '" placeholder="Measurement ' + FieldCount + '" class="form-control col"/><input type="text" name="ingredient_desc' + FieldCount + '" id="ingredient_desc' + FieldCount + '" placeholder="Ingredient' + FieldCount + '" class="form-control col"/> <button class="removeclass btn btn-outline-danger col">Delete</button></div></div>').insertBefore(InputsWrapper);
            x++; //text box increment
        }
        return false;
    });

$("body").on("click", ".removeclass", function (e) { //user click on remove text
    console.log(x);
    if (x > 1) {
        console.log(x);
        $(this).parent('div').parent('div').remove(); //remove text box
        x--; //decrement textbox
    }
    return false;
})
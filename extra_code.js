<script>
          for (IngredientFieldCount = 1; IngredientFieldCount < {{ ingredient_list.count() }}; IngredientFieldCount++) {
            document.write('<div class="form-group"><div class="row"><div class="form-group col-lg-2">Ingredient ' + IngredientFieldCount + '</div><div class="form-group col-lg-7"><input name="ingredient_desc' + IngredientFieldCount + '" class="form-control col" placeholder="Ingredient ' + IngredientFieldCount + '" value="{{ ingredient_list[' + (IngredientFieldCount - 1) + '].ingredient_desc }}"></div><div class="form-group col-lg-3"><button class="removeclass btn btn-outline-danger col">Delete</button></div></div></div>')
          }
      </script>


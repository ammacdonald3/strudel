/* $(document).ready(function(){
    $("#fav").click(function (e) {
        e.preventDefault();
        $.ajax({
            url : '/favorite_recipe_route',
            type : 'GET',
            contentType: 'application/json;charset=UTF-8',
            data : {recipe_id : this.value, 'recipeid':$(this).data('recipeid')},
            dataType:"json"
        });
    });
}); */


$(document).on("click","#fav",function(e){
    //e.preventDefault();
    $.ajax({
        url : '/favorite_recipe_route',
        type : 'POST',
        contentType: 'application/json;charset=UTF-8',
        //data : {recipe_id : this.value, 'recipeid':$(this).data('recipeid')},
        //data : {recipe_id : $(this).data('recipeid')},
        //data : {recipe_id : this.value},
        //data : {recipe_id : $('#fav').attr('data-recipeid')},
        //data : JSON.stringify($('#fav').attr('data-recipeid')),
        //data : 'testestest',
        data: {recipe_id : 5},
        dataType:"json",
        success: function (textStatus, status) {
            console.log(textStatus);
            console.log(status);
        },
        error: function(xhr, textStatus, error) {
            console.log(xhr.responseText);
            console.log(xhr.statusText);
            console.log(textStatus);
            console.log(error);
            console.log(this.value);
            console.log($(this).data('recipeid'));
        }
    });
});
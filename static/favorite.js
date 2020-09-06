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


/* $(document).on("click","#fav",function(e){
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
 */

$('.click').click(function() {
	if ($('span').hasClass("fa-star")) {
			$('.click').removeClass('active')
		setTimeout(function() {
			$('.click').removeClass('active-2')
		}, 30)
			$('.click').removeClass('active-3')
		setTimeout(function() {
			$('span').removeClass('fa-star')
			$('span').addClass('fa-star-o')
		}, 15)
	} else {
		$('.click').addClass('active')
		$('.click').addClass('active-2')
		setTimeout(function() {
			$('span').addClass('fa-star')
			$('span').removeClass('fa-star-o')
		}, 150)
		setTimeout(function() {
			$('.click').addClass('active-3')
		}, 150)
		$('.info').addClass('info-tog')
		setTimeout(function(){
			$('.info').removeClass('info-tog')
		},1000)
	}
})
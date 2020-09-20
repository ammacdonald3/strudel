// $('#shop-list').sortable();

// $(function() {
//     $( "#shop-list" ).sortable();
//     $( "#shop-list" ).disableSelection();
//  });

// var el = document.getElementById('shop-list');
// var sortable = Sortable.create(el);


$(document).ready(function(){
    $("input:checkbox").click(function () {
        var $this = $(this);
        if (this.checked) {
            $this.nextAll(':lt(2)').addClass('completed');
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"checked" }
            });
        } else {
            $this.nextAll(':lt(2)').removeClass('completed');
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"unchecked" }
            });
        }
    });
    $('.fa-trash').click(function () {
        var $this = $(this);
        $(this).closest("li").fadeOut(100,function(){
            $(this).remove;
        });
        $.ajax({
            url: '/_del_shopping_list_items',
            type: 'POST',
            data: { s_list_id:$(this).attr("id") }
        });
    })
    $('#shop-list').sortable({
        // stop: function(event, ui) {
        //     alert("New position: " + ui.item.index());
        //     $.ajax({
        //         url: '/_shopping_list_sort',
        //         type: 'POST',
        //         data: { s_list_id:$(this).attr("id"), item_index:ui.item.index() }
        //     });
        // }
        handle: '.handle',
        axis: 'y',
        update: function (event, ui) {
            var data = $(this).sortable('serialize');

            // POST to server using $.post or $.ajax
            $.ajax({
                data: data,
                type: 'POST',
                url: '/_shopping_list_sort'
            });
        }
    });
});



/* $(document).on("click",".big-checkbox",function(e){
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
}); */


/* $(document).ready(function(){
    $("input:checkbox").change(function() { 
        if($(this).is(":checked")) { 
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"checked" }
            });
        } else {
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"unchecked" }
            });
        }
    }); 
});
 */

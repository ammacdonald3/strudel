
$(document).ready(function(){
    // Convert table to DataTable
    /* $('#shopping-table').DataTable( {
        "paging": false
    } ); */


    // Strikethrough and fade shopping list items when checked
    $(".container").on("click", ".big-checkbox", function() {
        var $this = $(this);
        var $this_parent = $this.parent()
        var row = $this.closest('tr')
        if (this.checked) {
            $this_parent.siblings().addClass("completed");
            // Move checked item to the bottom of the shopping list
            setTimeout(
                function() {
                    row.insertAfter( row.parent().find('tr:last-child') )
                }, 
                300
            );
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"checked" }
            });
        } else {
            $this_parent.siblings().removeClass("completed");
            // Move unchecked item to the top of the shopping list
            setTimeout(
                function() {
                    row.insertBefore( row.parent().find('tr:first-child') )
                }, 
                300
            );
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"unchecked" }
            });
        }
    });

    // Completely delete shopping list items when clicking trash can icon
    $('.fa-trash').click(function () {
        var $this = $(this);
        $(this).closest("tr").fadeOut(300,function(){
            $(this).remove;
        });
        $.ajax({
            url: '/_del_shopping_list_items',
            type: 'POST',
            data: { s_list_id:$(this).attr("id") }
        });
    })

    // Show or hide table column for trash can icon
    $('#edit-button').click(function () {
        var $this = $(this);
        if ($this.hasClass("edit-inactive")) {
            $(this).addClass("edit-active");
            $(this).removeClass("edit-inactive");
            document.getElementById("edit-button").innerText="Exit Edit Mode";
            $(".trash-column").removeClass("d-none");
        }

        else {
            $(this).addClass("edit-inactive");
            $(this).removeClass("edit-active");
            document.getElementById("edit-button").innerText="Enter Edit Mode";
            $(".trash-column").addClass("d-none");
        }
    });

    // Show or hide table column for recipe name
    $('#hide-recipe').click(function () {
        var $this = $(this);
        if (this.checked) {
            $(".recipe-column").addClass("d-none")
        } else {
            $(".recipe-column").removeClass("d-none")
        }
    });

    // Reload shopping list items to account for changes made by an alternate user
    $(function() {
        setInterval(function() {
            $('#shopping-table').load(document.URL +  ' #shopping-table');
        }, 5000);
    });


});

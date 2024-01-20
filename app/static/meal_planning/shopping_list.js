
$(document).ready(function(){

    // Define the interval variable that defines how often to refresh the shopping list table
    var interval;  // Timer variable
    var resetCountdownValue = 10;  // Initial countdown value (in seconds)
    var countdownValue = resetCountdownValue;  // Initial countdown value (in seconds)


    // Function to decrement the table refresh countdown value and check if it reaches 0
    function decrementTimer() {
        countdownValue--;

        if (countdownValue <= 0) {
            // Timer reached 0, execute the function
            reloadTableResetTimer();
        }
    }

    function reloadTableResetTimer() {
        reloadShoppingTable();

        // Reset the countdownValue to start again
        countdownValue = resetCountdownValue;  // Set to your desired initial value
    }

    // Define the interval used for decrementing the table refresh timer
    function startInterval() {
        interval = setInterval(function () {
            decrementTimer();
        }, 1000);  // Decrement every second
    }

    // Function to add time to the table refresh timer
    function addTimeToTimer(secondsToAdd) {
        countdownValue += secondsToAdd;
    }

    // Function to delete a shopping list item
    function deleteShoppingListItem(element) {
        var $this = $(element);
        $(element).closest("tr").fadeOut(300,function(){
            $(this).remove;
        });
        $.ajax({
            url: '/_del_shopping_list_items',
            type: 'POST',
            data: { s_list_id:$(element).parent().parent().attr("id") }
        });
    }

    function reloadShoppingTable() {
        $('#shopping-table').load(document.URL + ' #shopping-table > *', function() {
            // Reinitialize Sortable after reload
            editShoppingTable();
            $('.fa-trash').click(function () {
                deleteShoppingListItem(this);
            });
        });
    }


    // Reusable function to re-sort the shopping list table
    // Initiated both on page load and after each table reload
    function editShoppingTable() {
        const updatedList = document.getElementById('shopping-list-body');
        new Sortable(updatedList, {
          handle: '.handle', // handle's class
          animation: 150,
      
          onSort: function (event) {
            // Get the new order data
            const newOrderData = Array.from(event.to.children).map((item, index, array) => {
              return {
                id: item.getAttribute('data-id'),
                // position: index + 1, // Assuming the position starts from 1
                position: array.length - index, // Reverse the index values
              };
            });
            
            // Send the new order data to the server
            fetch('/_shopping_list_sort', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ newOrderData: newOrderData }),
            })
              .then(response => response.json())
              .then(data => {
                // Handle the response from the server if needed
              })
              .catch(error => {
                console.error('Error:', error);
              });
          },
        });
    }
    
    // // Set up global Ajax settings
    // var simulateFailure = true;
    // $.ajaxSetup({
    //     beforeSend: function(xhr) {
    //         // Check the testing variable to simulate failure
    //         if (simulateFailure) {
    //             xhr.abort(); // Abort the request to simulate failure
    //         }
    //     }
    // });


    // Strikethrough and fade shopping list items when checked
    $(".container").on("click", ".big-checkbox", function() {
        var $this = $(this);
        var $this_parent = $this.parent()
        var itemNameRecipeName = $this.parent().next().children('.item-name-recipe-name');
        var shoppingListId = $this.attr("id");
        var successMessage = '#success-message-' + shoppingListId;
        var errorMessage = '#error-message-' + shoppingListId;

        var row = $this.closest('tr')
        if (this.checked) {
            // Clear previous messages
            $(successMessage).hide().text('');
            $(errorMessage).hide().text('');
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"checked" },
                success: function(response) {
                    // Handle success
                    $(successMessage).text('Item updated successfully.').show();
                    $(successMessage).text('Item updated successfully.').delay(4000).fadeOut();
                    // Move checked item to the bottom of the shopping list
                    setTimeout(
                        function() {
                            row.insertAfter( row.parent().find('tr:last-child') )
                        }, 
                        300
                    );
                    itemNameRecipeName.addClass("completed");
                    // If countdownValue is less than 4, add 2 seconds to the timer
                    if (countdownValue < 4) {
                        addTimeToTimer(2);  // Add 2 seconds
                    }
                },
                error: function() {
                    // Handle error
                    $(errorMessage).text('Failed to mark item complete. Check your connection and try again.').show();
                },
            });
        } else {
            // Clear previous messages
            $(successMessage).hide().text('');
            $(errorMessage).hide().text('');
            $.ajax({
                url: '/_shopping_list_items',
                type: 'POST',
                data: { s_list_id:$(this).attr("id"), status:"unchecked" },
                success: function(response) {
                    // Handle success
                    $(successMessage).text('Item updated successfully.').show();
                    $(successMessage).text('Item updated successfully.').delay(4000).fadeOut();
                    // Move unchecked item to the top of the shopping list
                    setTimeout(
                        function() {
                            row.insertBefore( row.parent().find('tr:first-child') )
                        }, 
                        300
                    );
                    // $this_parent.siblings().removeClass("completed");
                    itemNameRecipeName.removeClass("completed");
                },
                error: function() {
                    // Handle error
                    $(errorMessage).text('Failed to mark item complete. Check your connection and try again.').show();
                },
            });
            // If countdownValue is less than 4, add 2 seconds to the timer
            if (countdownValue < 4) {
                addTimeToTimer(2);  // Add 2 seconds
            }
        }
    });

    $('.fa-trash').click(function () {
        deleteShoppingListItem(this);
    });

    // Show or hide table column for trash can icon and re-sortable handle
    $('#edit-button').click(function () {
        var $this = $(this);
        if ($this.hasClass("edit-inactive")) {
            $(this).addClass("edit-active");
            $(this).removeClass("edit-inactive");
            document.getElementById("edit-button").innerText="Exit Edit Mode";
            $(".table-edit-column").removeClass("d-none");
            clearInterval(interval);
        }
        else {
            $(this).addClass("edit-inactive");
            $(this).removeClass("edit-active");
            document.getElementById("edit-button").innerText="Enter Edit Mode";
            $(".table-edit-column").addClass("d-none");
            startInterval();
            reloadTableResetTimer();
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

    
    // Initiate the shopping list re-sort function on page load
    editShoppingTable();

    // Start the countdown timer
    startInterval();
    

});

$(document).ready(function(){
    $("input:checkbox").click(function () {
        var $this = $(this);
        if (this.checked) {
            $this.parent().addClass('completed');
        } else {
            $this.parent().removeClass('completed');
        }
    });
});
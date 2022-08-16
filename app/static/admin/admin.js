$(document).ready( function () {
    // $('#admin-table').DataTable();
    $('#admin-table').DataTable( {
        responsive: true,
        colReorder: true,
        order: [[1, 'desc']],
        pageLength: 100
    } );
} );
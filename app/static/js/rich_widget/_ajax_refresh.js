$(document).ready( function() {
    $('#{{ _trigger }}').click(function() {
       $.ajax("{{ url_for( action ) }}").done(function (reply) {
          $('#{{ _taget }}').html(reply);
       });
    });
});
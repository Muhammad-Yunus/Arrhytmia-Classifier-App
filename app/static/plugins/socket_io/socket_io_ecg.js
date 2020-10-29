$(document).ready(function() {

    namespace = '/arrhytmia';
    var socket = io(namespace);

    socket.on('connect', function() {
        socket.emit('ecg_event', {data: 'connected'});
    });

    socket.on('ecg_receive', function(msg, cb) {
        $('#socket_output').html(msg.count + " - " + msg.data + "<br>");
        console.log(msg);
        if (cb) cb();
    });

    $('form#emit').submit(function(event) {
        socket.emit('ecg_event', {data: $('#emit_data').val()});
        return false;
    });
});
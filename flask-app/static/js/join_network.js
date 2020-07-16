$(function(){
  $('#join-network-btn').click(function(){
    var user = $("#ssid :selected").val();
    var pass = $("#wifi-key-field").val();
    $.ajax({
      url: 'http://localhost:8080/connect',
      data: $('form').serialize(),
      type: 'POST',
      success: function(response){
        console.log(response);
      },
      error: function(error){
        console.log(error);
      }
    });
  });
});
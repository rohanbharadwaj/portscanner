$(function(){

   $('#action-button').click(function(){
      console.log("rohan");
      // var user = $('#txtUsername').val();
      // var pass = $('#txtPassword').val();
      $.ajax({
         url: '/fetchdata',
         // data: $('form').serialize(),
         data: {
            format: 'json'
         },
         type: 'GET',
         success: function(response){
            $("#display").html(response);
            console.log(response);
         },
         error: function(error){
            console.log(error);
         }
      });
   });
});



// $("#action-button").click(function(){
//     $.ajax({url: "http://127.0.0.1:5000/fetchdata", success: function(result){
//         $("#display").html(result);
//     }});
// }); 

// $(function(){
// $('#action-button').click(function() {
//    alert("hello");
//    $.ajax({
//       url: '/fetchdata';
//       data: {
//          format: 'json'
//       },
//       error: function() {
//          $('#display').html('<p>An error has occurred</p>');
//       },
//       dataType: 'json',
//       success: function(data) {
//          // var $title = $('<h1>').text(data.talks[0].talk_title);
//          // var $description = $('<p>').text(data.talks[0].talk_description);
//          $("#display").html(result);
//       },
//       type: 'GET'
//    });
// });
// });


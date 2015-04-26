$(function(){

   // $('#SendData').click(function(){
   //    console.log("rohan");
   //    console.log($('#connect-form').serialize());
   //    // var user = $('#txtUsername').val();
   //    // var pass = $('#txtPassword').val();
   //     $.ajax({
   //        url: '/receivedata',
   //        data: $('#connect-form').serialize(),
   //    //     data: {
   //    //        format: 'json'
   //    //     },
   //        type: 'POST',
   //        success: function(response){
   //    //       // $("#display").html(response);
   //           console.log(response);
   //        },
   //        error: function(error){
   //           console.log(error);
   //        }
   //     });
   // });

   $('#SendData').click(function(){
      alert("rohan")
      console.log($('form'));
      // var user = $('#txtUsername').val();
      // var pass = $('#txtPassword').val();
      $.ajax({
         url: '/receivedata',
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
  
  // When the browser is ready...
  $(function() {
    $.validator.addMethod('IP4Checker', function(value) {
            var ip = "^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$";
                return value.match(ip);
            }, 'Invalid IP address');


  
    $("#register-form1").validate({

        // Specify the validation rules
        rules: {
            input_ipblock: {
              required: true,
              IP4Checker: true,
            },            
        },
        // Specify the validation error messages
        messages: {
            ip: "Please enter valid IP Address",
            // firstname: "Please enter your first name",  
        },
        submitHandler: function(form) {
            form.submit();
        }
    });

    $("#connect-form").validate({

        // Specify the validation rules
        rules: {
            connect_input_ip: {
              required: true,
              IP4Checker: true,
            },            
        },
        // Specify the validation error messages
        messages: {
            ip: "Please enter valid IP Address",
            // firstname: "Please enter your first name",  
        },
        submitHandler: function(form) {
            form.submit();
        }
    });




    // Setup form validation on the #register-form element
    $("#register-form").validate({

    
        // Specify the validation rules
        rules: {
            input_ip: {
              // required: true,
              IP4Checker: true,
            },
            firstname: "required",
            lastname: "required",
            email: {
                required: true,
                email: true
            },
            password: {
                required: true,
                minlength: 5
            },
            agree: "required"
        },
        
        // Specify the validation error messages
        messages: {
            // ip: "Please enter valid IP Address",
            firstname: "Please enter your first name",
            lastname: "Please enter your last name",
            password: {
                required: "Please provide a password",
                minlength: "Your password must be at least 5 characters long"
            },
            email: "Please enter a valid email address",
            agree: "Please accept our policy"
        },
        
        submitHandler: function(form) {
            form.submit();
        }
    });

  });
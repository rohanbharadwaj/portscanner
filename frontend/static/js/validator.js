  
  // When the browser is ready...
  $(function() {
    $.validator.addMethod('IP4Checker', function(value) {
            var ip = "^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$";
                return value.match(ip);
            }, 'Invalid IP address');

    $.validator.addMethod('PortRange', function(value) {
            var port = "^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])-([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])";
                return value.match(port);
            }, 'Invalid Port Range');


        $("#isup-form").validate({
        // Specify the validation rules
        rules: {
            connect_input_ip: {
              required: true,
              IP4Checker: false,
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
    
    $('#isup').on('click', function() {
        // alert("in 1");
    $("#isup-form").valid();

    });

    $("#connect-form").validate({
        // Specify the validation rules
        rules: {
            connect_input_ip: {
              required: true,
              IP4Checker: false,
            },
            connect_port: {
              required: true,
              PortRange: true,
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

    $('#connectSubmit').on('click', function() {
        // alert("in 1");
    $("#connect-form").valid();

    });
  
    $("#isup-form").validate({

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
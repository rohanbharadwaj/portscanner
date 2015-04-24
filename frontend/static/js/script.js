$(function(){

	var reqId;
	var done = false;
	var totalobj;

   $('#connectSubmit').click(function(){
      // alert("rohan")
      console.log($('form'));
      $.ajax({
         url: '/receivedata',
         data: $('form').serialize(),
         type: 'POST',
         dataType: 'json',
         success: function(response){
            console.log(response["reqId"]);
            reqId = response["reqId"];
            totalobj = response["numjobs"];
            connectPoll(reqId,totalobj);
         },
         error: function(error){
            console.log(error);
         }
      });
   });

function fetchConnectResults(reqid){
	$.ajax({
			url: '/fetchResults',
			data: {"reqId":reqId,"scantype":"CONNECT_SCAN"},
			type: 'POST',
			success: function(response){
				console.log(response);
				$('#connect-response').append(response)
			},
			error: function(error){
				console.log(error);
			}
		});
}

   function connectPoll(reqid,totalJobs){
    $.post('/getJobStatus',{"reqId":reqId,"scantype":"CONNECT_SCAN"},function(data) {
        //console.log(reqid);  // process results here
        //console.log(data[0].done);
        // totalJobs = response[0].numjobs;
        // console.log(reqId);
         console.log(data[0].count);
         console.log(data[0].reqId);
        if(data[0].count < totalobj && !done){
        // 	// Poll until the job is not ready
        	// remaining = data[0].pending;
         // 	updateProgress((remaining/totalJobs)*100);

         }
         else if(data[0].count >= totalobj && !done){
        // //job is completed display on the UI
        	fetchConnectResults(reqid)
        	console.log("Job completed")
        	done = true

         }
        setTimeout(connectPoll,5000);
    },'json');
	}


   $('#register').click(function(){
		//console.log($('form'));
		var user = $('#txtUsername').val();
		var pass = $('#txtPassword').val();
		$.ajax({
			url: '/signUpUser',
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


	$('#getReports').click(function(){
		// alert("yayy")
		console.log($('form'));
		// var user = $('#txtUsername').val();
		// var pass = $('#txtPassword').val();
		$.ajax({
			url: '/submit',
			data: $('form').serialize(),
			type: 'POST',
			dataType: "json",
			success: function(response){
				console.log(response[0].reqId);
				//test(response);
				reqId = response[0].reqId
				doPoll(reqId,response[0].numjobs);

			},
			error: function(error){
				console.log(error);
			}
		});
	});

	function test(response){
		console.log("this is awesome");
		console.log(response[0].reqId);
	}

	function updateProgress(percentage){
		if(percentage == 100){
			 $("#results_id").show();
		}
	    if(percentage > 100) {
	    	percentage = 100;
	    }
	    if(!isNaN(percentage)){

		    $('#progressBar').css('width', percentage+'%');
		    $('#progressBar').html('Fetching data '+percentage+'% complete');
		}
	}

	function doPoll(reqid,totalJobs){
    $.post('/getJobStatus',function(data) {
        //console.log(reqid);  // process results here
        //console.log(data[0].done);
        // totalJobs = response[0].numjobs;
        // console.log(reqId);
        // console.log(data[0].done);
        if(data[0].done!='true' && notdone){
        // 	// Poll until the job is not ready
        	remaining = data[0].pending;
         	updateProgress((remaining/totalJobs)*100);

         }
         else if(data[0].done!='false' && notdone){
        // //job is completed display on the UI

        	notdone = false;

         }
        setTimeout(doPoll,5000);
    },'json');
	}

});

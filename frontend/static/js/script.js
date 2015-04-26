$(function(){

	var done = false;
	var totalobj;
	var reqid;
	var connect_printed = false;

   $('#connectSubmit').click(function(){
      // alert("rohan")
      console.log($('form'));
      $.ajax({
         url: '/receivedata',
         data: $('form').serialize() + '&scantype=CONNECT_SCAN',
         type: 'POST',
         dataType: 'json',
         success: function(response){
         	// console.log(response);
         	// console.log(response[0]["numjob"])
         	// console.log(response[0]["reqid"])
            //console.log(response["reqid"]);
            reqid = response[0]["reqid"];
            totalobj = response[0]["numjob"];
            connectPoll();
            // console.log(reqid)
            // console.log(totalobj)
         },
         error: function(error){
            console.log(error);
         }
      });
   });

function fetchConnectResults(){
	console.log("Fetching Results in fetchConnectResults")
	$.ajax({
			url: '/fetchResults',
			data: {"reqId":reqid,"scantype":"CONNECT_SCAN"},
			type: 'POST',
			dataType: 'json',
			success: function(response){
			    $("#newScan").show();
			    $("#myTable").show();
				console.log(response);
//				a = JSON.parse(response)
                console.log("Response Length "+response.length);
                var res="rohan";
                if(!connect_printed){
                var table = document.getElementById("myTable");
//                var header = table.createTHead();
//                var row = header.insertRow(0);
//                var cell = row.insertCell(0);
//                var cell1 = row.insertCell(1);
//                var cell2 = row.insertCell(2);
//                var cell3 = row.insertCell(3);
//                var cell4 = row.insertCell(4);
//                var cell5 = row.insertCell(5);
//                var cell6 = row.insertCell(6);
                for(i=0;i<response.length;i++){
//                    console.log(response[i].scanType);
//                    console.log(response[i].jobId);
//                    console.log(response[i].workerIP_Port);
//                    console.log(response[i].IPs);
                    var scanType = response[i].scanType;
                    var jobId = response[i].jobId;
                    var workerIP_Port = response[i].workerIP_Port;
                    var IPs = response[i].IPs;
                    var report = response[i].report;
                    //var ports = response[i].ports.toString();
                    console.log(response[i].ports);
                    //Math.min.apply(Math, [100,13,3,6]);
                    var ports = Math.min.apply(Math,response[i].ports)+"-"+Math.max.apply(Math,response[i].ports);
                    console.log(response[i].ports);
                    var timestamp = response[i].timestamp;
                    var row = table.insertRow(i);
                    var cell1 = row.insertCell(0);
                    var cell2 = row.insertCell(1);
                    var cell3 = row.insertCell(2);
                    var cell4 = row.insertCell(3);
                    var cell5 = row.insertCell(4);
                    var cell6 = row.insertCell(5);
                    var cell7 = row.insertCell(6);

                    cell4.innerHTML = scanType;
                    cell1.innerHTML = i+1;
                    cell5.innerHTML = workerIP_Port;
                    cell2.innerHTML = IPs;
                    cell6.innerHTML = report;
                    cell7.innerHTML = ports;
                    cell3.innerHTML = timestamp;

                   //res+="<p>"+response[i].scanType+" "+response[i].jobId+" "+response[i].workerIP_Port+" "+response[i].IPs+" "+"</p>";
                }
                connect_printed = true;
                }
                //$('#connect-response').append(res)
                //console.log(res)
				//$('#connect-response').append(response)
			},
			error: function(error){
				console.log(error);
			}
		});
}
	
function updateConnectProgress(percentage){
		$("#connectprogressBar").show();
		if(percentage >= 100){
			fetchConnectResults();
			 // $("#connectprogressBar").show();
		}
	    // if(percentage > 100) {
	    // 	percentage = 100;
	    // }
	    if(!isNaN(percentage)){
            if(percentage >100)  percentage = 100;
		    $('#connectprogressBar').css('width', percentage+'%');
		    $('#connectprogressBar').html('Fetching data '+Math.floor(percentage)+'% complete');
		}
	}	
   function connectPoll(){

    $.post('/getJobStatus',{"reqId":reqid,"scantype":"CONNECT_SCAN"},function(data) {
        //console.log(reqid);  // process results here
        //console.log(data[0].done);
        // totalJobs = response[0].numjobs;
        // console.log(reqId);
        reqid = data[0].reqId;
         console.log(reqid);
         console.log(totalobj);
         console.log(data[0].count);
         console.log(data[0].reqId);
        if(data[0].count <= totalobj && !done){
        // 	// Poll until the job is not ready
        	 remaining = data[0].count;
             updateConnectProgress((remaining/totalobj)*100);

         }


         else if(data[0].count > totalobj && !done){
        // //job is completed display on the UI
        	//remaining = data[0].count;
        	//updateConnectProgress((remaining/totalJobs)*100);
        	//fetchConnectResults(reqid)
        	remaining = data[0].count;
            updateConnectProgress((remaining/totalobj)*100);
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
    $.post('/getReports',{},function(data) {
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

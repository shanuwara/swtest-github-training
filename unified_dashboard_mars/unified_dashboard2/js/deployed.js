function deployed(data) {

	if (data['jenkins'] == undefined)
		return ;

	data['jenkins']['builds'].sort(function(a,b) {
			//return parseInt(b.id) - parseInt(a.id);
			return Date.parse(b.time) - Date.parse(a.time);

	});

	var deployed_table = $("#deployed table");
	deployed_table.find("tbody>tr").remove();

	var count = 0;
	$.each(data['jenkins']['builds'], function(index, build) {
	
		if (build['_type'] == "deploy" || build['_type'] == "promote"){

			if (++count > 20)
				return false;

			var status = "failure";
			if (build['status'] == "1")
				status = "success";

			var duration = (parseFloat(build['duration'] / 1000).toFixed(0));
			var service = build['_service'].substring(0,32) + ((build['_service'].length>32)  ? "...":"");
		
			$(deployed_table).append('<tr class="' + status  + '"><td tag="' + new Date(build['time'].replace(" ", "T")).getTime() +'">' + formatDate(new Date(build['time'].replace(" ", "T"))) + 
								'</td><td tag="' + build['_environment'] + '">' + build['_environment']  + '</td><td tag="' + service + '">' + service + '</td><td tag="' + duration + '">' + duration + " s</td></tr>");
			//$("#deployments").find("td").css({"padding-left":"5px"});
		}

	});
}

queue.push("deployed");
window['deployed'] = deployed;
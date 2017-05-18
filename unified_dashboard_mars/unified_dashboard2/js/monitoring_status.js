function monitoring_status(data) {

	if (data['tibco'] == undefined)
		return ;

	$(".amber-server").remove();
	$.each(data.tibco.statuses, function(a,b) { 
		var server = $('<span class="amber-server"></span>').insertBefore($("#amber>br"));
		server.addClass("amber-server-" + b.status.toLowerCase());
		server.on("click", function() { window.location = "http://ldsrvtibadmp001.ladsys.net:9774" + b.link})
	})
	$("#amber-general").removeClass();
	$("#amber-general").addClass("amber-server-" + data.tibco.status.toLowerCase());
	$("#amber-general").on("click", function() {
		window.location = "http://ldsrvtibadmp001.ladsys.net:9774/?style=Default&userMode=XXX"
	});
}

queue.push("monitoring_status");
window["monitoring_status"] = monitoring_status;
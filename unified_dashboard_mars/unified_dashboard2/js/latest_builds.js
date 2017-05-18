function latest_builds() {

	if (tt.jenkins == undefined)
		return;

	var builds = $.unique(window.tt.jenkins.builds.map(function(d) { return d.name }));
	if (builds.indexOf("") != -1)
	  	builds.splice(builds.indexOf(""), 1);

	console.log(builds);




	var builds = [];
	$.each(window.tt.jenkins.builds, function(a,b) {

		if (b.name != "" && builds.indexOf(b.name) == -1) {
			builds.push(b.name);
			$("#watch_build").append('<option id="' + b.name + '"">' + b.alias + "</option>");
		}

	})

	$("#watch_build").find("option").eq(1).prop("selected", true);
	window.watch_build = $("#watch_build option").eq(1).attr("id");
}

queue.push("latest_builds");
window['latest_builds'] = latest_builds;
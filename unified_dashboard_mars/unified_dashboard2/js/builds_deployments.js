function builds_deployments_clean_empty() {

	$.each(window.tt.jenkins.builds, function(index, val) { 
			
			if (val != undefined &&  (val.name == "" || val.time == "") ) {
				window.tt.jenkins.builds.splice(index,1);
			}
		});

	delete window.tt.jenkins.buildsperday['None'];



	var builds = $.unique(window.tt.jenkins.builds.map(function(d) { return d.name }));
	if (builds.indexOf("") != -1)
	  	builds.splice(builds.indexOf(""), 1);


}



function getBuildsPerDay(_type) {

	var sBuilds = {};
	var fBuilds = {};


	for (i=0; i < 14; i++) {

		var sDate = formatDate3(new Date( new Date().getTime() - i * 24 * 3600 * 1000 ));
		sBuilds[sDate] = 0;
		fBuilds[sDate] = 0;
	}

	$.each(tt.jenkins.builds, function(a,b) { 
		if (b.type == _type && b.status == "1" && b.time != "")  {

			sDate = b.time.substring(0,10);
			if (sBuilds[sDate] == undefined)
				return ;

			sBuilds[sDate] += 1;

		} else if (b.type == _type && (b.status == "0" || b.status == "") ) {

			sDate = b.time.substring(0,10);
			if (fBuilds[sDate] == undefined)
				return ;

			fBuilds[sDate] += 1;
		}

	});

	return [sBuilds, fBuilds];
}

		

function getBuildNumber(days, type) {

	var rangeDate = new Date();
	rangeDate.setDate(rangeDate.getDate() - days);
	console.log(rangeDate);
	var builds = getBuildsPerDay(type)[0];

	var _keys = Object.keys(builds);
	_keys = _keys.filter( function(d) { return new Date(new Date(rangeDate).toJSON().slice(0,10)) <= new Date(d)});
	// console.log(_keys);
	var total = 0;
	$.each(_keys, function(i,d) { 
		total += builds[d];
	});


	var builds = getBuildsPerDay(type)[1];
	$.each(_keys, function(i,d) { 
		total += builds[d];
	});



	console.log(total);

	return total;
}
 

function builds_deployments() {

	builds_deployments_clean_empty();

	$("#builds_build_today>h1").html(getBuildNumber(0, "build"));
	$("#builds_build_7>h1").html(getBuildNumber(7, "build"));
	$("#builds_build_14>h1").html(getBuildNumber(14, "build"));


	$("#builds_deploy_today>h1").html(getBuildNumber(0, "deploy"));
	$("#builds_deploy_7>h1").html(getBuildNumber(7, "deploy"));
	$("#bbuilds_deploy_14>h1").html(getBuildNumber(14, "deploy"));

}

queue.push("builds_deployments");
window["builds_deployments"] = builds_deployments;

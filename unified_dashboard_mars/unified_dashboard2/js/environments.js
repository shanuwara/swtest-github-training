

function download(_data, _server) {

	console.log(_data);
	var form = document.createElement("form");
	form.setAttribute("method", "post");
	form.setAttribute("action", "http://10.33.20.14:9051");

	form.setAttribute("target", "formresult");

	var hiddenField = document.createElement("input");  
	hiddenField.setAttribute("name", "_data");  
	hiddenField.setAttribute("value", JSON.stringify(_data));          
	form.appendChild(hiddenField);

	var hiddenField = document.createElement("input");  
	hiddenField.setAttribute("name", "_server");  
	hiddenField.setAttribute("value", _server);          
	form.appendChild(hiddenField);

	// window.open('test.html', 'formresult','scrollbars=no,menubar=no,height=600,width=800,resizable=yes,toolbar=no,status=no');

	form.submit();
}


window.loadEnvironments = function(gOffset) {


	if (tt['services'] == undefined)
		return ;

	$("#env-screen1").empty();

	if (gOffset == undefined)
		var gOffset = 1.0;





	/*var xOffset = 1.0 * gOffset;
	var yOffset = 1.0 * gOffset;

	var rOffset = 1.0 * gOffset;*/

	var xOffset = 1.0, yOffset = 1.0, rOffset = 1.0, gOffset = 1.0;;

	window.table = [];

	window.tmpEnv = [];

	window.missingServices = [];

	window.missingServices2 = [];

	window.servicesInServer = [];

	window.servicesInServerAll = [];




	$.each(window.tt['services'], function(a,b) { 
		if (table[b.service] == undefined) {
		table.push(b.service);

		table[b.service] = [];
		table[b.service].push(b.environment);
		table[b.service][b.environment] = b.date;


	} else {

		table[b.service].push(b.environment);
		table[b.service][b.environment] = b.date;

	}

	});


	window.servers = ["eisperf", "LeedsUATEAI", "leedsdev", "LeedsSITEAI", "ukiccpreprod", "gibeisprod"];
	window.envServices = [];


	window.array1 = [];
	window.array2 = [];
	window.missing = [];

	array1[baseEnvironment] = [];
	array2[baseEnvironment] = [];
	missingServices[baseEnvironment] = [];
	missingServices[baseEnvironment] = [];
	missingServices[baseEnvironment][0] = [];
	missingServices[baseEnvironment][1] = [];
	missingServices[baseEnvironment][2] = [];
	missingServices[baseEnvironment][3] = [];

	missingServices2[baseEnvironment] = [];
	missingServices2[baseEnvironment] = [];
	missingServices2[baseEnvironment][0] = [];
	missingServices2[baseEnvironment][1] = [];
	missingServices2[baseEnvironment][2] = [];
	missingServices2[baseEnvironment][3] = [];




	missingServicesPerServer = [];
	missingServicesPerServer[baseEnvironment] = [];


	$.each(servers, function(a,b) {
		window.array1[b] = [];
		window.array2[b] = [];
		missingServices[b] = [];
		missingServices[b][0] = [];
		missingServices[b][1] = [];
		missingServices[b][2] = [];
		missingServices[b][3] = [];
		missingServices[b][4] = [];

		missingServices2[b] = [];
		missingServices2[b][0] = [];
		missingServices2[b][1] = [];
		missingServices2[b][2] = [];
		missingServices2[b][3] = [];
		missingServices2[b][4] = [];


		missing[b] = 0;

		missingServicesPerServer[b] = [];

	});



	$.each(tt.services, function(a,b) {

		if (b.environment != baseEnvironment ) {

			if (array1[b.environment] == undefined)
				return ;
			array1[b.environment].push(b.service);
			window.array2[b.environment].push(b);
			

		}
		else  {
			if (array1[b.environment] == undefined)
				return ;

			array1[baseEnvironment].push(b.service);
			window.array2[baseEnvironment].push(b);
		}


	});

	
	window.getServiceObject = function (service, environment) {
		var objService;
		$.each(tt.services, function(a,b) {
			
			if (b.environment == environment && b.service == service) {
				objService = b;
				//console.log(b);
				return false;
			}
		});

		if (objService == undefined) {
			console.log("objService " + service + " ," + environment);
			
		}

		return objService;
	}

	$.each(Object.keys(array1), function(a,b) {



		if (b != baseEnvironment) {



			$.each(array1[b], function(c, d) {
				missingServicesPerServer[b].push(d);

				// orphaned services
				if (array1[baseEnvironment].indexOf(d) == -1) {
					missingServices[b][4].push(d);
					missingServices2[b][4].push(getServiceObject(d,b));
				} else {

					var objService = getServiceObject(d, b);
					var objProdService = getServiceObject(d, baseEnvironment);
					// console.log(objService);

					if ( (new Date(objService.date.replace(" ", "T")).getTime()) > (new Date(objProdService.date.replace(" ", "T")).getTime()) ) {
						missingServices[b][3].push(d);
						missingServices2[b][3].push(getServiceObject(d,b));
					} else

					if ( (new Date(objService.date.replace(" ", "T")).getTime()) < (new Date(objProdService.date.replace(" ", "T")).getTime()) ) {
						missingServices[b][2].push(d);
						missingServices2[b][2].push(getServiceObject(d,b));
					}

					else {
						missingServices[b][0].push(d);
						missingServices2[b][0].push(getServiceObject(d,b));
					}

				}


			});

			$.each(array1[baseEnvironment], function(c, d) {


				// missing services
				if (array1[b].indexOf(d) == -1) {
					missingServices[b][1].push(d);
					missingServices2[b][1].push(getServiceObject(d,baseEnvironment));
					missingServicesPerServer[b].push(d);
				} 


			});



		} else {

			$.each(array1[b], function(c, d) {
				missingServices[b][0].push(d);
				missingServices2[b][0].push(getServiceObject(d,b));
			});
		}

	});



	/*var points = [
	{"x":55 * xOffset, "y":190 * yOffset},
	{"x":95 *xOffset , "y":70 * yOffset},
	{"x":170 *xOffset , "y":170 * yOffset},
	{"x":220 *xOffset, "y":65 * yOffset},
	{"x":290 *xOffset, "y":160 * yOffset},
	{"x":350 *xOffset, "y":70 *yOffset},
	{"x":395 *xOffset, "y":190 * yOffset},

	]*/


	var points = [
	{"x":35 * xOffset, "y":190 * yOffset},
	{"x":75 *xOffset , "y":70 * yOffset},
	{"x":150 *xOffset , "y":170 * yOffset},
	{"x":190 *xOffset, "y":65 * yOffset},
	{"x":270 *xOffset, "y":160 * yOffset},
	{"x":330 *xOffset, "y":70 *yOffset},
	{"x":375 *xOffset, "y":190 * yOffset},

	]

	var connections = [
		{"p1":0, "p2": 1},
		{"p1":0, "p2": 2},
		{"p1":1, "p2": 3},
		{"p1":2, "p2": 3},
		{"p1":3, "p2": 4},
		{"p1":4, "p2": 5},
		{"p1":4, "p2": 6},
	]

	var lowerColor = "#AB6464";
	var missingColor = "#597C9A";
	var matchColor = "#5C8B62";
	var newerColor = "#CAB43B";

	var radius = 50/2;



	var data2 = [];
	var tmpKeys = ["leedsdev", "LeedsSITEAI", "LeedsUATEAI", "eisperf", "ukiccpreprod", "gibeisprod", baseEnvironment];


$.each(tmpKeys, function(a,b) { 


		if (b != baseEnvironment)
		var tmp = [{"population": missingServices[b][0] == undefined ? 0 : missingServices[b][0].length, "color":matchColor, "server" : b, "status" : 0},
					{"population": missingServices[b][1] == undefined ? 0 : missingServices[b][1].length, "color":missingColor, "server" : b, "status" : 1},
					{"population": missingServices[b][2] == undefined ? 0 : missingServices[b][2].length, "color":lowerColor, "server" : b, "status" : 2},
					{"population": missingServices[b][3] == undefined ? 0 : missingServices[b][3].length, "color":newerColor, "server" : b, "status" : 3}
					];
		else
		var tmp = [{"population": missingServices[b][0]== undefined ? 0 : missingServices[b][0].length, "color":matchColor, "server" : b, "status" : 0},
					{"population": 0 , "color":missingColor, "server" : b, "status" : 1},
					{"population": 0 , "color":lowerColor, "server" : b, "status" : 2},
					{"population": 0 , "color":newerColor, "server" : b, "status" : 3}
					];

		data2.push(tmp);

	});


	var stats = [];
	console.log("data2");
	console.log(data2);

	$.each(data2, function(a,b) { 

		$.each(b, function(c,d) { 
			//console.log("status=" + d.status + ";population=" + d.population);
			 

			if (d.population > 0 && d.status == 1) {
				if (stats[a] == undefined || stats[a] == 1 || stats[a] == 0) {
					stats[a] = 1; 
					console.log(1);
				}
			}

			if (d.population > 0 && d.status == 2) { 
				if (stats[a] == undefined || stats[a] > -1) {
					stats[a] = 2; 
					console.log(2); 
				}
			}

			if (d.population > 0 && d.status == 0) { 
				if (stats[a] == undefined || stats[a] == 0) {
					stats[a] = 0; 
					console.log(2); 
				}
			}
				
		}); 
	});

	$.each(stats, function(a,b) { 
		switch(b) {

			case 0:
				stats[a] = matchColor;
			break;

			case 1:
				stats[a] = lowerColor;
			break;

			case 2:
				stats[a] = lowerColor;
			break;
		}
	});


	/*var canvas = d3.select("#environments").append("svg")
		.attr("width", "450px")
		.attr("height", "250px");*/
	var canvas = d3.select("#environments").select("#env-screen1")
		// .attr("width", (450 * gOffset) + "px")
		// .attr("height", (250 * gOffset) + "px")
		.attr("preserveAspectRatio", "xMidYMin meet")
		.attr("viewBox", "0 0 400 300")
		.style("background-color", "#2f2f2f")
		.style("width", "100%")
		.style("height", "100%")
		.style("display", "block");


	canvas
		.selectAll("line")
		.data(connections)
		.enter()
		.append("line")
			.attr("x1", function(d,i) { return points[d.p1].x})
			.attr("x2", function(d,i) { return points[d.p2].x})
			.attr("y1", function(d,i) { return points[d.p1].y})
			.attr("y2", function(d,i) { return points[d.p2].y})
			.style("stroke", "#424242")
			.style("stroke-width", "10px")

	/*canvas
		.append("image")
		.attr("xlink:href", "env.png")
		.attr("width", "450px")
		.attr("height", "250px");*/

	var arc = d3.svg.arc()
	    .outerRadius(radius * rOffset)
	    .innerRadius((radius - 20/2)*rOffset);


	var pie = d3.layout.pie()
	.sort(null)
	.value(function(d) { return d.population; });


	for (j = 0; j < data2.length; j++) {
		data1 = data2[j];
		console.log(data1);


		var group = canvas.append("g")
			.classed("arcs-content", true)

		group
			.append("circle")
			.attr("r", 30 * rOffset)
			.attr("transform", "translate(" + points[j].x + "," + points[j].y + ")")
			.style("fill", "#424242");	


		group
			.selectAll("path")
			.data(data1)
			.enter()
			.append("path")
			.style("fill", function(d) { return d.color})
			.attr("transform", function(d,i) { var pos = Math.floor(i / 3); return "translate(" + points[j].x + "," + points[j].y+ ")"})
			.attr("d", function(d,i) { return arc(pie(data1)[i]); })



		group
			.append("circle")
			.classed("middle_circle", true)
			.on("click", function(d) {
				
				// window.data1 = data2[j];
				var index = ($(this).parent().index(".arcs-content"));

				if (data2[index][0].server == baseEnvironment)
					return false;

				loadEnvironments2(data2[index], 1.0);
				loadTriangles(data2[index][0].server, 1.0);

			/*	$(window).resize(function() {
					loadEnvironments2(data2[index], gOffset);
					loadTriangles(data2[index][0].server, gOffset);
				});
*/
				
				canvas
					.style("display", "none");

				// $("#env-screen1").parent().css("display", "none");

				d3.select("#legend")
					.style("display", "none");

			})
			.attr("r", 12 * rOffset)
			.attr("transform", "translate(" + points[j].x + "," + points[j].y + ")")
			.style("fill", function(d,i) { return stats[j]});			

		canvas
			.append("g")
			.classed("server_label", true)
			.selectAll("text")
			.data(data1.filter(function(d,i) { if (i % 4 == 0) return d; }))
			.enter()
			.append("text")
				.style("fill", "#c2c2c4")
				.style("text-anchor", "middle")
				.style("font-size", "10px")
				.attr("transform", function(d) { return "translate(" + (points[j].x) + "," + (points[j].y - 40) +")"; })
				.text(function(d) { return d.server})


		var offset = -30;
		// canvas
		// 	.selectAll("g")
		group
			.selectAll("text")
			.data(data1.filter(function(d,i) { if (d.status == 1 || d.status == 2 || d.status == 3) return d; }))
			.enter()
			.append("text")
				.classed("values", true)
				.attr("transform", function(d,i) { offset += 15; return  "translate(" + (points[j].x + 35 + (5 * (i % 2))  ) + "," + (points[j].y+offset) + ")";})
				.attr("fill", function(d) { return d.color})
				.style("font-size", "12px")
				.text(function(d) { return d.population; })

	}

	d3.select("#environments")
	.selectAll(".arcs-content")
		.on("mouseover", function() {
			d3.select(this)
			.selectAll("text")
				.style("display", "initial") ;
		})
		.on("mouseout", function() {
			d3.select(this)
			.selectAll("text")
				.style("display", "none") ;
		})
		.selectAll(".values")
			.style("display", "none");



/* screen2 */


window.loadEnvironments2 = function(data1, gOffset) {

	
// $(".server_label").eq($(".arcs-content").eq(5).index(".arcs-content")).find("text").eq(0).attr("value")


	var gOffset = 1.0;


	console.log("server=" + data1[0].server);
	d3.select("#environments").select(".env-screen2").remove(); // clean



	// var canvas = d3.select("#environments")
	var canvas = d3.select("#env-container")
		.append("svg")
		.attr("preserveAspectRatio", "xMidYMin meet")
		.style("width", "100%")
		.style("height", "85%")
		.attr("viewBox", "0 0 450 250")
		.attr("tag", "");
			

	canvas
		.attr("width", (450*gOffset)+"px")
		.attr("height", (250*gOffset)+"px")
		.style("background-color", "#2f2f2f")
		.style("border", "1px solid #c2c2c4")
		.classed("env-screen2", true);

	/*canvas
		.on("click", function(d) {
			console.log(d);
			canvas.remove();
			d3.select("#env-screen1")
				.style("display", "initial");
			d3.select("#legend")
					.style("display", "initial");

		});	*/	




/* circle */
	//window.data1 = data2[0]

	var arc = d3.svg.arc()
	    .outerRadius(40 * rOffset)
	    .innerRadius((40 - 15)*rOffset);


	var pie = d3.layout.pie()
		.sort(null)
		.value(function(d) { return d.population; });

	var group = canvas.append("g")
			// .classed("arcs-content", true)
			.attr("transform", "translate(72,80)")

		group
			.append("text")
			.attr("fill", "white")
			.attr("transform", "translate(-15,5)")
			.style("font-size", "14px")
			.style("font-weight", "bold")
			.attr("id", "circle-percent");


		group
			.selectAll("path")
			.data(data1)
			.enter()
			.append("path")
			.style("fill", function(d) { return d.color})
			
			.attr("d", function(d,i) { return arc(pie(data1)[i]); })
			.on("mouseout", function(d,i) { 
				var arc = d3.svg.arc()
			    var index = ($(this).index());
				var arc = d3.svg.arc()
				    .outerRadius(40 * rOffset)
				    .innerRadius((40 - 15)*rOffset);


				var pie = d3.layout.pie()
					.sort(null)
					.value(function(d) { return d.population; });
			 	d3.select(this)
			 		.transition()
			 		.duration(500)
			 		.attr("d", arc(pie(data1)[i])); 

		 		d3.select("#circle-percent")
					.text("");
			})



			.on("mouseover", function(d,i) { 
				var arc = d3.svg.arc()
			    var index = ($(this).index());
				var arc = d3.svg.arc()
				    .outerRadius(45 * rOffset)
				    .innerRadius((45 - 15)*rOffset);

				d3.select("#circle-percent")
					.text(function() {

						var percent = data1[i].population / data1.map(function(a,b) { 
							return a.population; 
						}).reduce(function(a,b) { return a+b}, 0) * 100;

						return Math.round(percent) + "%";
					})
					.attr("fill", function() { console.log(d); return d.color})


				var pie = d3.layout.pie()
					.sort(null)
					.value(function(d) { return d.population; });
				d3.select(this)
					.transition()
					.duration(200)
					.attr("d", arc(pie(data1)[i])) 
				});

/* circle - end */


/* text labels  */

	canvas
		.append("text")
			.attr("transform", "translate(25,14)")
			.style("font-size", "10px")
			.attr("fill", "#c2c2c4")
			.style("text-transform", "uppercase")
			.text(function(d) { return data1[0].server});

	canvas
		.append("line")
			.attr("x1", "0")
			.attr("y1", "0")
			.attr("x2", "128")
			.attr("y2", "1")
			.attr("transform", "translate(13,29)")
			.attr("stroke", "#808080");

	canvas
		.append("line")
			.attr("x1", "0")
			.attr("y1", "0")
			.attr("x2", "128")
			.attr("y2", "1")
			.attr("transform", "translate(13,129)")
			.attr("stroke", "#808080");

	canvas
		.append("text")
		.classed("screen2-legend", true)
		.attr("transform", "translate(33,143)")
		.text("MATCH");

	canvas
		.append("text")
		.classed("screen2-legend-value", true)
		.attr("fill", "#86ac86")
		.attr("transform", "translate(102,143)")
		.text(function(d) { return data1[0].population});		




	canvas
		.append("text")
		.classed("screen2-legend", true)
		.attr("transform", "translate(33,159)")
		.text("OLD");

	canvas
		.append("text")
		.classed("screen2-legend-value", true)
		.attr("fill", "#a05e5a")
		.attr("transform", "translate(102,159)")
		.text(function(d) { return data1[2].population});




	canvas
		.append("text")
		.classed("screen2-legend", true)
		.attr("transform", "translate(33,175)")
		.text("NEW");

	canvas
		.append("text")
		.classed("screen2-legend-value", true)
		.attr("fill", "#e39b02")
		.attr("transform", "translate(102,175)")
		.text(function(d) { return data1[3].population});



	canvas
		.append("text")
		.classed("screen2-legend", true)
		.attr("transform", "translate(33,191)")
		.text("MISSING");

	canvas
		.append("text")
		.classed("screen2-legend-value", true)
		.attr("fill", "#568ca8")
		.attr("transform", "translate(102,191)")
		.text(function(d) { return data1[1].population});


/* text labels - end */


/* x-closing button */


	canvas
		.append("text")
		.attr("transform", "translate(5,15)")
		.attr("fill", "#c2c2c4")
		.text("x")
		.style("cursor", "pointer")
		.on("click", function(d) {
			console.log(d);
			canvas.remove();
			d3.select("#env-screen1")
				.style("display", "initial");

			// $("#env-screen1").parent().css("display", "initial");

			d3.select("#legend")
					.style("display", "initial");

		});		


/* x-closing button */



/* general report */


	var reportBtn = canvas.append("g");

	reportBtn
		.style("cursor", "pointer")
		.on("click", function() { 

			download(missingServices2[ data1[0].server ], data1[0].server)

		});

	reportBtn
		.append("polygon")
		.attr("points", "13,216 141,216 141,238 13,238")
		.style("stroke-width", "1px")
		.style("stroke", "#fafafa")
		.style("fill", "#2f2f2f");
		

	reportBtn
		.append("text")
		.attr("transform", "translate(33,231)")
		.classed("screen2-legend", true)
		.style("text-transform", "uppercase")
		.style("fill", "#c2c2c4")
		.text("general report");


/* general report - end */




/* triangles */

window.loadTriangles = function(env) {
console.log(env);
	var a = [ 
			{"x" : 10 * gOffset, "y": 0 * gOffset}, 
			{"x": 0 * gOffset,   "y": 16 * gOffset}, 
			{"x": 20 * gOffset,  "y": 16 * gOffset}] 

	var b = [ 
			{"x" : 12 * gOffset, "y": 0 * gOffset}, 
			{"x": 22 * gOffset, "y": 16 * gOffset}, 
			{"x": 32 * gOffset, "y": 0 * gOffset}] 



	var a1 = [ 
			{"x" : 22 * gOffset, "y": 0 * gOffset}, 
			{"x": 12 * gOffset,   "y": 16 * gOffset}, 
			{"x": 32 * gOffset,  "y": 16 * gOffset}] 

	var b1 = [ 
			{"x" : 0, "y": 0}, 
			{"x": 10, "y": 16}, 
			{"x": 20, "y": 0}] 





	var trianglesArray = [];
	var yOffset = 20;
	var xOffset = 24;
	var position = 0;
	var delimiter = 22;


	countServices = missingServices[env][0].length + 
					missingServices[env][1].length + 
					missingServices[env][2].length +
					missingServices[env][3].length;

	for (i = 0; i < countServices; i++) {

		position = i - (Math.floor(i/delimiter) * delimiter);
		var reverse = (Math.floor(i / delimiter) % 2) ;
		// console.log("odd");
		var tmp = [];


		if ((position  % 2) == reverse)
			var inputPoints = (reverse == 0) ? a : eval("a" + 1);
		else
			var inputPoints = (reverse == 0) ? b : eval("b" + 1);
		$.each(inputPoints, function(aa,bb) {
			// tmp.push(bb);
			// console.log(bb);
			var xDiff = bb.x  + (Math.floor(position/2) * xOffset) ;
			var yDiff = bb.y + (Math.floor(i/delimiter) * yOffset);
			tmp.push({"x" : xDiff, "y": yDiff})
			

		});
		trianglesArray.push(tmp);

		
	}



	var canvas = d3.select("#environments")
		.select(".env-screen2");

	canvas
		.append("g")
		.attr("transform", "translate(" + (160*gOffset) + "," + (11*gOffset) + ")")
		.classed("triangles", true)
		.selectAll("polygon")
		.data(trianglesArray)
		.enter()
		.append("polygon")
			.attr("points",function(d) { 
	         return $.map(d, function(d) {
	            return [(d.x),(d.y)].join(",");
	        }).join(" ");
	    })

			.on("click", function(){

				d3.select(".tooltip").remove();

				var index = ($(this).index());
				console.log(index);
				//var serviceName = table[index];
				var serviceName = missingServicesPerServer[env][index];

				var serviceObject;
				var serviceProd;
				tt.services.map(function(d) { if (d.service == serviceName && d.environment == env) serviceObject = d; });
				tt.services.map(function(d) { if (d.service == serviceName && d.environment == baseEnvironment) serviceProd = d; });
				console.log(serviceObject);

				if (serviceObject == undefined) {
					
					var serviceObject = jQuery.extend(true, {}, serviceProd);
					serviceObject.date = "THIS SERVICE IS MISSING";
					
				}

				if (serviceProd == undefined) {

					var serviceProd = jQuery.extend(true, {}, serviceObject);
					serviceProd.date = "SERVICE NOT IN LIVE";
				}

				var body = d3.select("body");
				var tooltip = 
					body
						.append("div")
						.classed("tooltip", true);
						


				

				posLeft = $("#environments>svg").position().left;
				posTop = $("#environments>svg").position().top;

				if ($("#environments>svg:nth(1)") != undefined) {
					posLeft = $("#environments>svg:nth(1)").position().left + 20;
					posTop = $("#environments>svg:nth(1)").position().top  + 20;
				}

				console.log("posLeft" + posLeft);



				tooltip
					.style("left", posLeft + "px")
					.style("top", posTop + "px");

				tooltip
					.append("div")
					.classed("servicelabel", true)
						.append("p")
						.classed("x-container", true)
							.text("x")
							.on("click", function() {
								$(this).parent().parent().remove();

							});

				tooltip.select(".servicelabel")
						.append("p")
							.text(serviceObject.service);



				tooltip
					.append("div")
					.classed("label", true)
					.text("Curent Version");

				tooltip
					.append("div")
					.classed("status", true)
					.text(serviceObject.date)
					.style("background-color", $(this).css("fill"));

				tooltip
					.append("div")
					.classed("label", true)
					.text("Production Version");
				tooltip
					.append("div")
					.classed("status", true)
					.text(serviceProd.date);

				tooltip
					.append("div")
					.classed("commentlabel", true)
					.text("Comments");

				tooltip
					.append("div")
					.classed("commentcontent", true)
					.text(serviceObject.comment)

				tooltip
					.append("br")
					.style("clear", "both");





			})
			.on("mouseover", function(){

				$(this).css({"stroke":"white"});
			})
			.on("mouseout", function(){

				$(this).css({"stroke":"#87847a"});
			})

			.style("fill", function(d,i) {
				//var service = table[i];
				var service = missingServicesPerServer[env][i];
				if (missingServices[env][0].indexOf(service) != -1)
					return "#739273";
				if (missingServices[env][1].indexOf(service) != -1)
					return "#2f2f2f";
				if (missingServices[env][2].indexOf(service) != -1)
					return "#9e5f5e";
				if (missingServices[env][3].indexOf(service) != -1)
					return "#b5935f";

				// return "#b5935f";
				return "#424242";


			})
			.style("stroke", "#87847a")
			.style("stroke-width", "1");

/*
			$(window).resize(function() {
				

				posLeft = $("#environments>svg").eq(1).position().left;
				posTop = $("#environments>svg").eq(1).position().top;
				tooltip = $(".tooltip");
				tooltip.css({"left":posLeft + "px", "top":posTop + "px"});				

			});*/


	/* triangles - end */
}


/* screen2 - end */
}

}


function environments() {

	loadEnvironments($("#env-screen1").parent().width() / 450);

	/*$(window).resize(function() {
		loadEnvironments($("#env-screen1").parent().width() / 450);
	});*/

	
}


queue.push("environments");
window["environments"] = environments;
function versionChart(param, data) {
 
	/*var data = [{ "progress": 95, "ticket": "DX-132"}, 
				{ "progress":55, "ticket":"DX-190"}, 
				{ "progress": 0, "ticket":"DX-40"},
				{ "progress":50, "ticket":"DX-11"},
				{ "progress": 80, "ticket": "DX-132"}, 
				{ "progress":55, "ticket":"DX-190"}, 
				{ "progress": 5, "ticket":"DX-40"},
				{ "progress":50, "ticket":"DX-11"},
				{ "progress": 100, "ticket":"DX-40"},

				];*/


	var total = 0;
	for (var i in data) {
		total += data[i].percent;
	}

	var progress = ((total / (data.length * 100)) * 100).toFixed(0);
	var scaleResult = d3.scale.linear().domain([0,100]).range([38.5,83]);

	var anglePercentage = d3.scale.linear().domain([0, 100]).range([0, 2 * Math.PI]);
    var fullAnglePercentage = 100;
	var totalSpend = data.length;
 	window.dataPoints = [];
        var startAnglePercentage = 0;
        for (var i=0; i < data.length; i++) {
            var endAnglePercentage = 1 / data.length * 100 + startAnglePercentage;
            dataPoints.push([startAnglePercentage, endAnglePercentage]);
            startAnglePercentage = endAnglePercentage;
    }

    var arc = d3.svg.arc()
        .innerRadius(33)
        .outerRadius(function(d,i) {
	    	var index=-1;
	         for (p in dataPoints) { 
	        	
	         	if (dataPoints[p][0] == d[0] && dataPoints[p][1] == d[1])
	         	 index=p; 
	         }
	         console.log("index="+index); 
	         return scaleResult(data[index].percent) 
     	})
        .startAngle(function(d){return +(anglePercentage(d[0]));})
        .endAngle(function(d){return +(anglePercentage(d[1]));});




	window.canvas = document.createElement("svg");

	// canvas = d3.select(canvas);

	d3.select(param).selectAll("svg").remove();
	canvas = d3.select(param).append("svg");

// preserveAspectRatio= "xMinYMin meet" viewBox="0 0 800 960"
	canvas
		.style("width", "100%")
		.style("height", "100%")
		.style("background-color", "#2f2f2f")
		.attr("preserveAspectRatio", "xMidYMid meet")
		.attr("viewBox", "0 0 220 190")
		.style("padding-top", "15px")
		.style("margin-top", "10px")
		.style("border", "1px solid white")
		// .style("padding-left", "50%")
		// .style("padding-top", "50%");
 
	var oldCanvas = canvas;

	canvas = 
		canvas
			.append("g")
				.attr("preserveAspectRatio", "xMidYMid meet")
				.attr("transform", "translate(110,0)"); // move to the middle

	var big_circle_bg =
		canvas
			.append("circle")
			.attr("r", 89.5)
			.attr("transform", "translate(0,89.5)")
			.attr("fill", "#7f7f7f");

	var big_circle_fg =
		canvas
			.append("circle")
			.attr("r", 87.5)
			.attr("transform", "translate(0,89.5)")
			.attr("fill", "#424242");


	var radius = 83;
	
	var arcs = canvas
		.selectAll("g")
			.data(dataPoints)
			.enter()
			.append("g")
			.attr("class", "arc");


	arcs
		.append("path")
		.style("fill", function(d,i) { 
			if (data[i].percent == 0) return "#536c82"; 
			if (data[i].percent == 100) return "#749173";
			if (data[i].percent > 0 && data[i].percent <= 50) return "#a05e5a";
			if (data[i].percent > 50) return "#b7925e";
			
		})
		.attr("transform", function(d,i) { var pos = Math.floor(i / 3); return "translate(0,89.5)"})
		.attr("d", arc)
		.style("stroke", "black")
		.style("stroke-width", 0.5)
		.on("mouseover", function(d,i) {
			    window.insideIndex = -1;
			    var arc = d3.svg.arc()
		        .innerRadius(scaleResult(100) - 50)
		        .outerRadius(function(d,i) {
			    	
			        for (p in dataPoints) { 				        	
			         	if (dataPoints[p][0] == d[0] && dataPoints[p][1] == d[1])
			         		insideIndex=p; 
			        }
			        return scaleResult(110) 
		     	})
		        .startAngle(function(d){return +(anglePercentage(d[0]));})
		        .endAngle(function(d){return +(anglePercentage(d[1]));});

		    d3.select(this.parentNode).select("text")
		    	.transition()
				.duration(200)
				.style("visibility", "visible");
			console.log("insideIndex=" + insideIndex);
			middleText.text((data[i].percent) + "%");

			d3.select(this)
				.transition()
				.duration(200)
				.attr("d", arc) 
		})
		.on("mouseout", function(d,i) {
			var index = -1;
			var arc = d3.svg.arc()
		        .innerRadius(scaleResult(100) - 50)
		        .outerRadius(function(d,i) {
			    	var index=-1;
			        for (p in dataPoints) { 				        	
			         	if (dataPoints[p][0] == d[0] && dataPoints[p][1] == d[1])
			         		index=p; 
			        }
			        return scaleResult(data[index].percent) 
		     	})
		        .startAngle(function(d){return +(anglePercentage(d[0]));})
		        .endAngle(function(d){return +(anglePercentage(d[1]));});

		    d3.select(this.parentNode).select("text")
		    	.transition()
				.duration(200)
				.style("visibility", "hidden");

			middleText.text((progress) + "%");

			d3.select(this)
				.transition()
				.duration(200)
				.attr("d", arc) 

		})


 	arcs.append("text")
      .attr("transform", function(d, i) { //set the label's origin to the center of the arc
    
    	var arc = d3.svg.arc()
        .innerRadius(scaleResult(100) - 50)
        .outerRadius(function(d,i) {
	    	var index=-1;
	         for (p in dataPoints) { 				        	
	         	if (dataPoints[p][0] == d[0] && dataPoints[p][1] == d[1])
	         	 index=p; 
	         }
	         return scaleResult(100) 
     	})
        .startAngle(function(d){return +(anglePercentage(d[0]));})
        .endAngle(function(d){return +(anglePercentage(d[1]));});

      	var c = arc.centroid(d);
    	return "translate(" + ( + c[0]) + "," + (89.5 + c[1]) + ")";
      })
      .attr("text-anchor", "middle") //center the text on it's origin
      .style("fill", "#000")
      .style("visibility", "hidden")
      .style("font", "bold 8px Arial")
      .text(function(d, i) { return data[i].key }); //get the label from our original

	var middle_circle = 
		canvas
			.append("circle")
			.attr("r", 30)
			.attr("transform", "translate(0,89.5)")
			.attr("fill", "#2f2f2f");

	var middleText = 
		canvas
			.append("text")
			.text(progress + "%")
			.attr("transform", "translate(0,94.5)")
			.attr("fill", "#bbbbbd")
			.attr("size", 14)
			.style("text-anchor", "middle")


}
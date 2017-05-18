function circle(param, data) {

  var container = param;
  var value = data;

/* circle */
  //window.data1 = data2[0]

  if (value == undefined)
    value = "0";

  value = value.replace("%", "");

  var tmp = [{"population": value , "color":"#58715a"},
          {"population": (100 - value) , "color":"#a05e5a"},
         
          ];
   

    var data2 = [];
    data2.push(tmp);
    data1 = data2[0];

  var arc = d3.svg.arc()
      .outerRadius(40)
      .innerRadius(40 - 15);


  var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.population; });


    d3.select(container).select("svg").remove();
  var canvas = d3.select(container).append("svg");

  canvas
    .attr("width", 100)
    .attr("height", 100);

  var group = canvas.append("g")
      // .classed("arcs-content", true)
      .attr("transform", "translate(40,40)")

    group
      .append("text")
      .attr("fill", "white")
      .attr("transform", "translate(-15,5)")
      .style("text-anchor", "middle")
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
      d3.select("#circle-percent")
          .text(function(d,i) { return data1[i].population});
      


   

/* circle - end */
}



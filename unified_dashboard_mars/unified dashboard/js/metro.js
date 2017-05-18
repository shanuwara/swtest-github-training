var two = [];
var three = [];
var four  = [];



$(document).ready(function() {

  $.each($(".two-row"), function(a,b) { 
    two.push( parseInt($(b).attr("id").replace("element","") )); 
  });

  $.each($(".three-row"), function(a,b) { 
    three.push( parseInt($(b).attr("id").replace("element","") )); 
  });

  $.each($(".four-row"), function(a,b) { 
    four.push( parseInt($(b).attr("id").replace("element","") )); 
  });


  function calibrate(_array, _class) {
  for (i = 0; i < _array.length; i++) {
      var top = $("#element" + _array[i]).position().top;
      $.each($("#wrapper").children(), function(a,b) {
        if ($(b).position().top == top) 
          $(b).addClass(_class);
      });
    }
  }

  function metro() {
  $.each($("#wrapper").children(), function(a,b) {
      var posElement = parseInt($(b).attr("id").replace("element", ""));
      if (two.indexOf(posElement) == -1 && three.indexOf(posElement) == -1 && four.indexOf(posElement) == -1) {
      //if (one.indexOf(posElement) != -1) {
        $(b).removeClass("two-row");
        $(b).removeClass("three-row");
        $(b).removeClass("four-row");
        $(b).addClass("one-row");

      }
    });

    calibrate(two, "two-row");
    calibrate(three, "three-row");
    calibrate(four, "four-row");
  }


  metro();

  $(window).resize(function() {
    metro();
  });
  

});
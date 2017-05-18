function update(project, data) {

  if (document.querySelector("#" + project.name) == undefined) {
    return 0;
  }

  if (data.length == 0) {
    $("#" + project.name).find("polygon.cls-1").css({"stroke":"grey"});
    $("#" + project.name).find("polygon.cls-7").css({"stroke":"grey"});
    $("#" + project.name).find("text.cls-3").html("")
    $("#" + project.name).find("text.cls-9").html("")

    return;
  }


  for (var i = 0; i < data.length; i++) {
    var item = data[i];
    var red = "red";
    var green = "#66a74a";

    var query = '#' + project.name + ' #BorderHex-' + item.order;
    // console.log("query=" + query);
    var borderObj = document.querySelector(query);

    var environmentObj = document.querySelector('#' + project.name + ' #Server' + item.order + ' text:last-child');
    var versionObj = document.querySelector('#' + project.name + ' #Server' + item.order + ' text');

    
    borderObj.setAttribute('style', 'stroke: ' + green);
    versionObj.innerHTML = item.version;

    if (item.version == "") {
      versionObj.innerHTML = '';
      borderObj.setAttribute('style', 'stroke: ' + red);
    }

    

  }
}

setTimeout(function() {

  var xhttp = [];
  
  for (var j = 0; j < projects.length; j++) {

    (function (j){
      var project = projects[j];
      var projectId = project.id;

      var url = "http://10.33.20.14:8055/api/environment/deployment/" + projectId;
      console.log(url);
      xhttp[j] = new XMLHttpRequest();
      xhttp[j].onreadystatechange = function() {
        if (xhttp[j].readyState == 4 && xhttp[j].status == 200) {
          var response =  xhttp[j].responseText;
          console.log(response);
          console.log(project.name);

          if (response != undefined) {
            var data = JSON.parse(response);

            update(projects[j], data);
          }
        }
      };

      xhttp[j].open("GET", url, true);
      xhttp[j].send();
    })(j);

  }


}, 500);


setTimeout(function() {
        

for (var i = 0; i < clickLinks.length; i++) {
  var item = clickLinks[i];

  (function(item) {
      $("#" + item.id).parent().parent().find("h2").on("click", function(){
        window.location = item.url;
        console.log(item.url);

    });


      
      

  })(item);
  
}
}, 500);
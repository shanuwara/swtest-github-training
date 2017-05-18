function promoted_deployed_tabs() {
	$("#promoted_click").css({"background-color": "#282828"});
	$("#promoted_click").on("click", function() {
		$(this).css({"background-color": "#282828"});
		$("#deployed_click").css({"background-color": "#424242"});

			$("#promoted").css({"display":"block"}); 
			$("#deployed").css({"display":"none"}); 
	});

	$("#deployed_click").on("click", function() {
		$(this).css({"background-color": "#282828"});
		$("#promoted_click").css({"background-color": "#424242"});

		$("#promoted").css({"display":"none"}); 
		$("#deployed").css({"display":"block"}); 
	});


	$("#promoted").css({"display":"block"}); 
	$("#deployed").css({"display":"none"}); 
}

queue.push("promoted_deployed_tabs");
window['promoted_deployed_tabs'] = promoted_deployed_tabs;

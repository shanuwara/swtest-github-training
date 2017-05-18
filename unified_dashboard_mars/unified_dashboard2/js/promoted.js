function promoted(data) {

	var promoted_table = $("#promoted table");
	promoted_table.find("tbody>tr").remove();

	$.each(data['artifactory'], function(index, element) { 
		$(promoted_table).append("<tr><td>" + element['name'] + "</td><td>" + formatDate(new Date(element['date'].replace(" ", "T"))) + "</td><td></td></tr>")
	});

}

queue.push("promoted");
window["promoted"] = promoted;
function sprint_issues_in_progress(data) {

	if (data['jira'] == undefined)
		return;

	var inprogress_table = $("#features_in_progress table tbody");
	inprogress_table.find("tbody>tr").remove();

	$.each(data['jira']['issuesinprogress'] ,function(index, element) {
		$(inprogress_table).append("<tr><td>" + element['key'] +"</td><td>" + element['summary'] + "</td></tr>");
	});
}

queue.push("sprint_issues_in_progress");
window["sprint_issues_in_progress"] = sprint_issues_in_progress;
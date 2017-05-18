function sprint_issues_count(data) {

	if (data['jira'] == undefined)
		return;
	$("#sprint_issues_total>h3").html(data['jira']['total']);
	$("#sprint_issues_wip>h3").html(data['jira']['inprogress']);
	$("#sprint_issues_done>h3").html(data['jira']['inprogress']);

	$("#sprint_insert").html(data['jira']['sprintname']);
	$("#sprint_insert2").html(data['jira']['sprintstart'] + " - " + data['jira']['sprintend']);

}

queue.push("sprint_issues_count");
window["sprint_issues_count"] = sprint_issues_count;
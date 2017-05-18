function svn_summary(data) {

	if (data['svn'] == undefined)
		return;
	
	var svn_summary_table = $("#svn_summary");
	var svn_summary_commits = $(svn_summary_table).find("tr").eq(0);
	var svn_summary_contributers = $(svn_summary_table).find("tr").eq(1);

	$(svn_summary_commits).find("td").eq(1).html(data['svn']['totalcommits7']);
	$(svn_summary_commits).find("td").eq(2).html(data['svn']['totalcommits14']);

	$(svn_summary_contributers).find("td").eq(1).html(data['svn']['totalcontributors7']);
	$(svn_summary_contributers).find("td").eq(2).html(data['svn']['totalcontributors14']);
}

queue.push("svn_summary");
window["svn_summary"] = svn_summary;
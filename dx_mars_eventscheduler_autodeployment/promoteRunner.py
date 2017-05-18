#!python2.7 -u

import sys, os
sys.path.append(os.getcwd())
from cqm_libs.jira import jira
from promote import Promote


def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "" or value == "None":
			value = None
		globals()[element] = value

elements = ("WORKSPACE", "ARTIUSER", "ARTIPASS", "SERVICE", "ARTISERVER", "BRANCH", "RC", "SVNUSER",
					"SVNPASS", "SETTINGS_URL", "ENVIRONMENT", "JIRASERVER", "JIRAUSER", "JIRAPASS", "JIRAKEY")
setGlobals(elements)

REPOSITORY = "DX-MARS"
EXTENSION = ".war"

 
if __name__ == "__main__":


	try:
		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
		comment = "{color:green}Package promoted successfully{color}"

		promote = Promote(
					ARTIUSER=ARTIUSER, 
					ARTIPASS=ARTIPASS, 
					ARTISERVER=ARTISERVER,
					extension=".war", 
					repository="DX-MARS", 
					service=SERVICE,
					branch=BRANCH,
					rc=RC
				)

		output = promote.execute()
		if output["returncode"] == 0:
			if JIRAKEY is not None and JIRAKEY != "":
				jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
		else:
			if JIRAKEY is not None and JIRAKEY != "":
				comment = "{color:red}Promotion failed{color}\n" + str(output)
				jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)

	except Exception as e:
		print e

		comment = "{color:red}Promotion failed{color}\n" + str(e)
		if JIRAKEY is not None and JIRAKEY != "":
			jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
		raise Exception(comment)
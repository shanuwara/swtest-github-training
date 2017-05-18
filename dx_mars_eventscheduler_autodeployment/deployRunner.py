#!python2.7 -u

import sys, os
sys.path.append(os.getcwd())
from cqm_libs.jira import jira
from deploy import Deploy


def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "" or value == "None":
			value = None
		globals()[element] = value

elements = ("WORKSPACE", "ARTIUSER", "ARTIPASS", "SERVICE", "ARTISERVER", "BRANCH", "RC", "SVNUSER",
					"SVNPASS", "SETTINGS_URL", "ENVIRONMENT", "JIRASERVER", "JIRAUSER", "JIRAPASS", "JIRAKEY", "BUILD_NUMBER")
setGlobals(elements)

REPOSITORY = "DX-MARS"
EXTENSION = ".war"


if __name__ == "__main__":


	try:
		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
		comment = "{color:green}Package deployed successfully{color}"

		deploy = Deploy(
					ARTISERVER=ARTISERVER, 
					ARTIUSER=ARTIUSER, 
					ARTIPASS=ARTIPASS, 
					SVNUSER=SVNUSER,
					SVNPASS=SVNPASS,
					service=SERVICE,
					extension=EXTENSION,
					repository=REPOSITORY,
					branch=BRANCH,
					rc=RC,
					settings_url=SETTINGS_URL,
					environment=ENVIRONMENT,
				)

		output = deploy.execute()
		print output

		if output["returncode"] == 0:
			if JIRAKEY is not None and JIRAKEY != "":
				comment = comment.replace("'", "&quot;")
				jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
		else:
			if JIRAKEY is not None and JIRAKEY != "":
				comment = "{color:red}Deployment failed{color}\n"
				comment += "http://jira.ladbrokes.co.uk/jenkins/view/DX/job/DX_EventScheduler_deploy/{0}\n\n".format(BUILD_NUMBER)
				if len(str(output)) < 30000:
					comment += str(output)

				comment = comment.replace("'", "&quot;")
				jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)

	except Exception as e:
		print e

		comment = "{color:red}Deployment failed{color}\n"
		comment += "http://jira.ladbrokes.co.uk/jenkins/view/DX/job/DX_EventScheduler_deploy/{0}\n\n".format(BUILD_NUMBER)
		if len(str(e)) < 30000:
			comment += str(e)

		comment = comment.replace("'", "&quot;")

		if JIRAKEY is not None and JIRAKEY != "":
			
			jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
		raise Exception(comment)
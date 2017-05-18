#!python2.7 -u

import sys, os
sys.path.append(os.getcwd())
import shlex
import json
import urllib2
import base64
import subprocess as sb
import re
import hashlib
import json

from deploy import Deploy
from cqm_libs.jira import jira


def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "" or value == "None":
			value = None
		globals()[element] = value

def validateGlobals(elements):
	for element in elements:
		if globals()[element] == None:
			raise ValueError(element + " is not set")



elements = ("JIRAPASS", "JIRAUSER", "JIRASERVER", "ENVIRONMENT", "HOT_RELEASE", "BUILD_NUMBER", "BUILD_ID", "SERVICE", "SVNUSER", "SVNPASS", "WORKSPACE", "ARTIUSER", "ARTIPASS", "RC", "FOLDER", "SETTINGS_URL") 
setGlobals(elements)
validateGlobals(elements)


elements2 = ("JIRAKEY", "REPORTER", "REGRESSION_TEST", "EMS_SCRIPTS", "COUCHBASE_SCRIPTS", "BRANCH")
setGlobals(elements2)

Destination_dir = "/opt/tibco/cqm_eis_deployment"

# SVN_SCRIPTS = "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/"
# SVN_BW = "http://10.32.18.100/svn/DX/DX/trunk/Development/Code/Bw/"
# REPOSITORY = "http://10.32.18.100/svn/DX/DX/trunk/Development/Code/Bw/"

ARTISERVER = "http://10.33.20.7:8080"
comment = ""

try:
	deploy = Deploy(JIRAKEY=JIRAKEY, 
					JIRAPASS = JIRAPASS,
					JIRAUSER = JIRAUSER,
					ARTISERVER=ARTISERVER, 
					ARTIUSER=ARTIUSER, 
					ARTIPASS=ARTIPASS,
					service=SERVICE, 
					rc=RC,
					branch=BRANCH,
					extension=".zip",
					repository="DX-MARS",
					environment=ENVIRONMENT,
					SETTINGS_URL=SETTINGS_URL,
					debug=True
					# SVNUSER=SVNUSER,
					# SVNPASS=SVNPASS,

					)

	deploy.setBuildNumber(BUILD_NUMBER)
	deploy.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	deploy.execute()

	comment = "{color:green}Deployment finished{color}"

	if JIRAKEY != None and JIRAKEY != "":
		jiraManager = jira(server=JIRASERVER, userName = JIRAUSER, password = JIRAPASS)
		jiraManager.addComment(jiraKey = JIRAKEY, comment = comment)

except Exception as e1:
	comment = "{color:red}Deployment failed: {color}" + str(e1)
	comment = comment.replace("\"", "&quot;")
	comment = comment.replace("'", "&quot;")
	if JIRAKEY != None and JIRAKEY != "":
		jiraManager = jira(server=JIRASERVER, userName = JIRAUSER, password = JIRAPASS)
		jiraManager.addComment(jiraKey = JIRAKEY, comment = comment)

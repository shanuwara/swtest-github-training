#!python2.7

import sys
import os
import subprocess as sb
import shlex
import json
import csv
import shutil
import re
import hashlib


#sys.path.append("autodeployment")
from settings import Settings

global SERVICE, SVNUSER, SVNPASS, BUILD_NUMBER, ARTIUSER, ARTIPASS, BRANCH

SERVICE = os.getenv("SERVICE", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
BUILD_NUMBER = os.getenv("BUILD_NUMBER", None)
WORKSPACE = os.getenv("WORKSPACE", None)
BRANCH = os.getenv("BRANCH", None)
repository = "PnG" 
artifactory = "PnG"


SVNREPOSITORY = "PandG"

def downloadSVN(username, password, source, target, branch = None):

	if os.path.exists(target):
		shutil.rmtree(target)

	if branch is not None:
		source = source.replace("/trunk", "/branch/" + branch)

	svn_co_command = "svn export --non-interactive --force --username={0} --password={1} {2} {3}".format(username, password, source, target)
	print svn_co_command
	print "[INFO] Executing: ", svn_co_command
	svn_co = sb.Popen(shlex.split(svn_co_command), stdout=sb.PIPE, stderr=sb.PIPE)
	data_svn_co = " ".join(svn_co.communicate())
	# data_svn_co = svn_co.stdout.read()
	
	output = data_svn_co
	tmp = output.lower()
	
	if tmp.find("doesn't exist") != -1 or tmp.find("Unable to connect ") != -1 or tmp.find("authorization failed") != -1:
		comment = "{color:red}downloadSVN: " + output + "{color}"
		JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment=comment )
		raise Exception("downloadSVN: " + output)
	else:
		print "[INFO] Output: ", output	
		p = re.compile(ur'Exported revision ([0-9]*)', re.DOTALL)
		group = re.search(p, output)
		if group is not None:
			return group.groups()[0]
 

if __name__ == "__main__":
	try:
		settings = Settings()
		settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
		settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
		conf = settings.getSettings()
		print "### Testing settings feature", conf[SERVICE]["SVNName"], "###"
		SERVICE = conf[SERVICE]["SVNName"]
		with open("settings.properties", "w") as params:
			params.write("SERVICE=" + SERVICE + "\n")


	except Exception as e1:
		print e1
		sys.exit(-1)


	target = os.path.join(WORKSPACE, SERVICE)
	source = "http://10.33.20.5:8080/svn/{1}/{0}/trunk".format(SERVICE, SVNREPOSITORY)

	branch = BRANCH
	if BRANCH == None or BRANCH == "":
		branch = None



	revision = downloadSVN(username=SVNUSER, 
				password=SVNPASS, 
				source=source,
				target=target,
				branch=branch)

	with open("settings.properties", "a") as params:
			params.write("REVISION=" + revision + "\n")

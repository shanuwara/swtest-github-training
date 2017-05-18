#!python2.7 -u


import os, sys
sys.path.append(os.getcwd())
import csv
import shlex
import subprocess as sb
import re
import json
import shutil
import httplib
import urllib

from settings import Settings
#from cqm_libs.jira import jira
#from cqm_libs.artefactory import artefactory

# PROXY = "squid01.ladbrokes.co.uk"
# PROXY_PORT = 8080
URL = "https://api.newrelic.com/v2/applications/{0}/deployments.json"
# APIKEY = "a4385fcdce5548f6e2b3ab876fcb44438b8fa2868a4805e"


PROXY_PORT = os.getenv("PROXY_PORT", None)
PROXY = os.getenv("PROXY", None)
APIKEY = os.getenv("APIKEY", None)
SERVICE = os.getenv("SERVICE", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
ARTIUSER = os.getenv("ARTIUSER", None)
ARTIPASS = os.getenv("ARTIPASS", None)
BUILD_NUMBER = os.getenv("BUILD_NUMBER", None)
WORKSPACE = os.getenv("WORKSPACE", None)
ENVIRONMENT = os.getenv("ENVIRONMENT", None)

JIRASERVER = os.getenv("JIRASERVER", None)
JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
RC = os.getenv("RC", None)
REPOSITORY = "http://10.33.20.5:8080/svn/PandG/"
BRANCH = os.getenv("BRANCH", None)
REPORTER = os.getenv("REPORTER", None)


def post(url, payload, headers):
	conn = httplib.HTTPConnection(PROXY, PROXY_PORT)
	conn.request("POST", url, payload, headers)
	res = conn.getresponse()
	output = res.read()
	status = res.status
	conn.close()

	
	return int(status)

def main():

	settings = Settings()
	settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
	settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	conf = settings.getSettings()

	if conf is None or SERVICE not in conf:
		raise ValueError("Failure, incorrect config file")

	parameters = conf[SERVICE]
	appId = parameters["{0}_NEWRELIC_ID".format(ENVIRONMENT)]

	payload = {"deployment":
	{
		"revision": RC,
		"changelog": JIRAKEY,
		"description": "",
		"user": REPORTER
	}}

	url = URL.format(appId)
	status = post(url, json.dumps(payload), {"X-Api-Key": APIKEY, 'Content-Type': 'application/json' })
	print "payload=", payload
	print "url=", url


	if status == 201:
		print "[INFO] Success"
	else:
		raise Exception("Failure, status:", status)






if __name__ == "__main__":
	main()
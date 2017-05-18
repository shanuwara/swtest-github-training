#!python2.7 -u

import csv
import os
import sys
import shlex
import subprocess as sb
import re
import json
import shutil

# sys.path.append(os.path.join(WORKSPACE, "cqm"))
sys.path.append(os.getcwd())
from cqm_libs.jira import jira
from cqm_libs.artefactory import artefactory


global SERVICE, SVNUSER, SVNPASS, BUILD_NUMBER, ARTIUSER, ARTIPASS, BRANCH, RELEASECANDIDATE, ENVIRONMENT


SERVICE = os.getenv("SERVICE", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
ARTIUSER = os.getenv("ARTIUSER", None)
ARTIPASS = os.getenv("ARTIPASS", None)
BUILD_NUMBER = os.getenv("BUILD_NUMBER", None)
WORKSPACE = os.getenv("WORKSPACE", None)
ENVIRONMENT = os.getenv("ENVIRONMENT", None)
RELEASECANDIDATE = os.getenv("RELEASECANDIDATE", None)
JIRASERVER = os.getenv("JIRASERVER", None)
JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
RC = os.getenv("RC", None)
REPOSITORY = "http://10.33.20.5:8080/svn/PandG/"
BRANCH = os.getenv("BRANCH", None)

if BRANCH == "" or BRANCH == "trunk":
	BRANCH = None

artifactory = "PnG"


if RC is None:
	RC = "trunk"

#### unit test

if WORKSPACE is None:
	JIRAKEY = "PNGT-333"
	JIRAUSER = "CQMJIRA"
	JIRAPASS = "CQMJIRA"
	SVNUSER = "cqmsvn"
	SVNPASS = "K_29^ob"
	ARTIUSER = "admin"
	ARTIPASS = "K_29^ob"
	JIRASERVER = "http://10.33.20.21:8080/jira"
	WORKSPACE = "/home/extraspace/home/mtz/png/png_autodeployment/"
	SERVICE = "LBRGames"
	ENVIRONMENT = "DEV"


###  ####
	




class Settings:
	def __init__(self):
		self.__filename = ""
		self.__SUBVERSIONusername = ""
		self.__SUBVERSIONpassword = ""
		pass

	def setFileName(self, filename):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__filename = filename

	def setSubversionCredentials(self, username, password):
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password

	def getSettings(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		# print "[INFO]", sys._getframe().f_code.co_name
		filename = self.__filename

		
		if self.__SUBVERSIONusername == "":
			raise ValueError("self.__SUBVERSIONusername is empty")

		if self.__SUBVERSIONpassword == "":
			raise ValueError("self.__SUBVERSIONpassword is empty")
			

		values = {
			"username": self.__SUBVERSIONusername,
			"password": self.__SUBVERSIONpassword,
			"filename": filename
		}
		cmd = "curl -s -u {username}:{password} -X GET {filename}".format(**values )
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0].split("\n")


		output = {}
		reader = csv.DictReader(data) # in case of csv with headers
		for line in reader:
			output[line['ServiceName']] = line


		return output





# def getListFiles(source, username, password, _exception = True ):
# 	print "[INFO]", sys._getframe().f_code.co_name
# 	# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
# 	# global ARTIUSER, ARTIPASS, artifactory_server
# 	# command_curl_get_list = "curl -D- -X GET -u " + username + ":" + password + " " + artifactory_server + _folder + "/" 


# 	if source[-1] != "/":
# 		source = source + "/"

# 	command_curl_get_list = "curl -s -D- -X GET -u {0}:{1} {2}".format(username, password, source)

# 	print "[EXECUTING]",command_curl_get_list
# 	curl_get_list = sb.Popen(shlex.split(command_curl_get_list), stdout=sb.PIPE)
# 	data_curl_get_list = curl_get_list.communicate()[0]
# 	# print data_curl_get_list
# 	# data_curl_get_list = curl_get_list.stdout.read()
# 	p = re.compile(ur'({.*})', re.DOTALL)
# 	group = re.search(p, data_curl_get_list)
# 	# print group.groups()
# 	if group is not None:
# 		files = []
# 		# print group.groups()[0]
# 		# print group.groups()
# 		data_json = json.loads(group.groups()[0])
# 		if "children" in data_json:
# 		  return data_json['children']
# 		else:
# 		  msg = "[ERROR] Artifactory " + _folder + " is empty or service not found"
# 		  raise Exception(msg)
# 		  # print msg
# 		  # mail.write(msg)
# 		  if _exception == False:
# 		    msg = "[INFO] Folder " + _folder + " allowed to be empty\n"
# 		    print msg
# 		    # mail.write(msg)
# 		    # mail.flush()
# 		  else:
# 		    raise Exception("Source Artifactory folder is empty")

def customSort(value):
	convert = lambda text: int(text) if text.isdigit() else text
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	return sorted(l, key = alphanum_key)

def getListFiles(source, username, password, _exception = True ):
	print "[FUNC]", sys._getframe().f_code.co_name
	
	if source[-1] != "/":
		source = source + "/"

	command_curl_get_list = "curl -s -X GET -u {0}:{1} {2}".format(username, password, source)

	print command_curl_get_list
	curl_get_list = sb.Popen(shlex.split(command_curl_get_list), stdout=sb.PIPE)
	data_curl_get_list = curl_get_list.communicate()[0]
	
	files = []

	data_json = json.loads(data_curl_get_list)

	if "children" in data_json:
		return data_json['children']

	if _exception == False:
		msg = "[INFO] Folder " + source + " allowed to be empty\n"
		print msg
	else:
		msg = "[ERROR] Artifactory " + source + " is empty or service not found"
		raise Exception(msg)



def getLatestFile(_list, _service, _sortkey = str.lower):
	# print "[INFO]", sys._getframe().f_code.co_name
	print "[FUNC]", sys._getframe().f_code.co_name
	files = []
	for f in _list:
		group = re.search(ur'^(' + _service + ').*tgz$', str(f['uri'][1:]))

		if group is not None and len(group.groups()) > 0 and group.groups()[0] == _service:
			# print group.groups()
			# print "group is not none"
			files.append(str(f['uri'][1:]))

	# files = sorted(files)
	# files.sort(key=str.lower)

	files.sort(key=_sortkey)
	# files.sort(key=lambda x: (int(x.split("-")[1]), int(x.split(".tgz")[0]) ))
	# print files[-1][1:]
	if len(files) > 0:
		return files[-1]
	else:
		return None


def getTargets(environments, environment):
	print "[INFO]", sys._getframe().f_code.co_name

	targets = []
	for env in environments:
		if env['environment'] == environment:
			if env['ip'] != "":
				targets.append(env['ip'])	
	return targets



def loadConfigSettings(filename):
	print "[FUNC]", sys._getframe().f_code.co_name
	config = open(filename, "r")
	output = []
	reader = csv.DictReader(config)
	for line in reader:
		# print line
		# output[line["environment"]] = line
		output.append(line)

	config.close()
	return output



###############################3



try:
	if SERVICE is None or SVNUSER is None or SVNPASS is None or WORKSPACE is None or ARTIUSER is None or ARTIPASS is None or ENVIRONMENT is None:
		raise Exception("Initial variable is not set up")

	if SERVICE == "" or SVNUSER == "" or SVNPASS == "" or BUILD_NUMBER == "" or WORKSPACE == "" or ARTIPASS == "" or ARTIUSER == "" or ENVIRONMENT == "":
		raise Exception("Initial variable is set up incorrectly")	



	## download settings from autodeployment ###
	os.system("rm -f {0}".format( os.path.join(WORKSPACE, "environments.csv")))
	cmd = "svn export --username={0} --password={1} --non-interactive --force  http://10.33.20.5:8080/svn/PandG/autodeployment/environments.csv {3}".format(SVNUSER, SVNPASS, SERVICE, os.path.join(WORKSPACE, "environments.csv"))
	print "[INFO] Executing: ", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	output = proc.communicate()
	print "[INFO] output: ", output


	JIRA = jira(server=JIRASERVER, userName=JIRAUSER, password=JIRAPASS)
	ARTEFACTORY = artefactory(server="http://10.33.20.7:8080", userName=ARTIUSER, password=ARTIPASS)

	settings = Settings()
	settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
	settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	conf = settings.getSettings()

	SVNName = str(conf[SERVICE]['SVNName'])



	# list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, RC), username=ARTIUSER, password=ARTIPASS )
	# print "[INFO] Found packages: ", list

	convert = lambda text: int(text) if text.isdigit() else text
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

	if BRANCH is None or BRANCH == "":
		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, "trunk"), username=ARTIUSER, password=ARTIPASS )
		latest = getLatestFile(list, SERVICE, alphanum_key)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory,"trunk",latest)
	else:
		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, "trunk_" + BRANCH), username=ARTIUSER, password=ARTIPASS )
		latest = getLatestFile(list, SERVICE, alphanum_key)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory,"trunk_" + BRANCH,latest)
	


	print "[INFO] Found packages: ", list
	# latest = getLatestFile(_list=list, _service=SERVICE )

	
	if latest is None or latest == "":
		raise ValueError("latest is incorrect")

	print "[INFO] Found latest package:", latest
	print "[INFO] Package found:", source
	# source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory,RC,latest)

	targets = getTargets(loadConfigSettings(os.path.join(WORKSPACE, "environments.csv")), ENVIRONMENT)
	print "[INFO] Found targets:", targets

	cmd = "mco rpc -F ipaddress=\"/({0})/\" deploy_png  lbr source='{1}'".format("|".join("^"+ip+"$" for ip in targets), source)

	print "[INFO] Executing", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	output = proc.communicate()
	print "[INFO] output: ", output
	proc.wait()

	tmp = "\n".join(output)

	# indexes = multi_find(tmp, "### SUCCESS ###")

	
	if JIRAKEY is not None:
		comment = ""
		print "[INFO] JIRAKEY=", JIRAKEY
		if tmp.lower().find("error") != -1:
			print "[INFO] Found error"
			comment = "{color:red}Error occurred during deployment:{color}"
		else:
			print "[INFO] No error found"
			comment = "{color:blue}Package has been deployed{color} "

		comment += "http://jira.ladbrokes.co.uk/jenkins/view/PNG/job/PnG_Deployment_LBR/{0}/console \n\n".format(BUILD_NUMBER)
		if len(tmp) < 30000:
			comment += tmp
			

		print "[INFO] Adding comment in JIRA"
		comment = comment.replace("'", "&quot;")
		comment = comment.replace("\"", "&quot;")

		print comment


		JIRA.addComment(jiraKey=JIRAKEY, comment=comment)


except Exception as e1: 
	print e1

	if JIRAKEY is not None and JIRAKEY != "":
		comment = "http://jira.ladbrokes.co.uk/jenkins/view/PNG/job/PnG_Deployment_LBR/{0}/console \n\n".format(BUILD_NUMBER)
		comment += "{color:red}Unexpected error{color} "

		if len(str(e1)) < 30000:
			comment += str(e1)

		comment = comment.replace("'", "&quot;")
		comment = comment.replace("\"", "&quot;")

		print "[INFO] Adding comment in JIRA"
		JIRA.addComment(jiraKey=JIRAKEY, comment=comment)

	raise Exception("Deployment LBR failed")





#!python2.7 -u

import csv
import os
import sys
sys.path.append(os.getcwd())
import shlex
import subprocess as sb
import re
import json
from cqm_libs.artefactory import artefactory


global SERVICE, SVNUSER, SVNPASS, BUILD_NUMBER, ARTIUSER, ARTIPASS, BRANCH, RELEASECANDIDATE, ENVIRONMENT

SERVICE = os.getenv("SERVICE", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
ARTIUSER = os.getenv("ARTIUSER", None)
ARTIPASS = os.getenv("ARTIPASS", None)
BUILD_NUMBER = os.getenv("BUILD_NUMBER", None)
WORKSPACE = os.getenv("WORKSPACE", None)
BRANCH = os.getenv("BRANCH", None)
ENVIRONMENT = os.getenv("ENVIRONMENT", None)
RELEASECANDIDATE = os.getenv("RELEASECANDIDATE", None)
TARGET = os.getenv("TARGET", None)
JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
repository = "PandG"
artifactory = "PnG"
project = "PnG"




# SERVICE = "fairgaming"
# SVNUSER = "cqmsvn"
# SVNPASS = "K_29^ob"
# BUILD_NUMBER = 100
# WORKSPACE = "/home/extraspace/home/mtz/png"
# ARTIUSER = "admin"
# ARTIPASS = "K_29^ob"
# ENVIRONMENT = "DEV"
# RELEASECANDIDATE = "RC6"
# TARGET = "/var/www/vhosts/tst1-fbg-lcm.ladbrokes.com/htdocs/"

class Settings:
	def __init__(self):
		self.__filename = ""
		self.__SUBVERSIONusername = ""
		self.__SUBVERSIONpassword = ""
		pass

	def setFileName(self, filename):
		self.__filename = filename

	def setSubversionCredentials(self, username, password):
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password

	def getSettings(self):
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



if SERVICE is None or SVNUSER is None or SVNPASS is None or WORKSPACE is None or ARTIUSER is None or ARTIPASS is None or ENVIRONMENT is None or RELEASECANDIDATE is None:
	raise Exception("Initial variable is not set up")

if SERVICE == "" or SVNUSER == "" or SVNPASS == "" or BUILD_NUMBER == "" or WORKSPACE == "" or ARTIPASS == "" or ARTIUSER == "" or ENVIRONMENT == "" or RELEASECANDIDATE == "":
	raise Exception("Initial variable is set up incorrectly")	



def getListFiles(source, username, password, _exception = True ):
	
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

def getLatestFile(_list, _service):
	files = []
	for f in _list:
		group = re.search(ur'^PnG_('+ _service + ')_.*tar.gz$', str(f['uri'][1:]))
		if group is not None and len(group.groups()) > 0 and group.groups()[0] == _service:
			# print group.groups()
			# print "group is not none"
			files.append(str(f['uri'][1:]))

	# files = sorted(files)
	# files.sort(key=str.lower)

	files.sort(key=lambda x: (int(x.split("_")[3]), int(x.split("_")[5]) ) )
	# print files[-1][1:]
	if len(files) > 0:
		return files[-1]
	else:
		return None


def getLatestFile2(repository, folder, searchName, sortPattern):
	
	manager = artefactory(userName=self.__ARTIUSER, password=self.__ARTIPASS, server=self.__ARTISERVER)
	packages = manager.advancedSearch(repository=repository, folder=folder, searchName=searchName, sortPattern=sortPattern)
	
	if len(packages) > 0:
		package = packages[0]
		if package is not None and package != "":
			return package

	return None




def loadConfigSettings(filename):
	config = open(filename, "r")
	output = []
	reader = csv.DictReader(config)
	for line in reader:
		# print line
		# output[line["environment"]] = line
		output.append(line)

	config.close()
	return output



def getTargets(environments, environment):

	targets = []
	for env in environments:
		if env['environment'] == environment:
			if env['ip'] != "":
				targets.append(env['ip'])	
	return targets



#"The service {color:red}" + target.split("_")[1] + "{color} has been promoted successfully and is available here: " + target
def JIRA_add_comment(url, key, comment, username, password):
	_comment = {}
	_comment['add'] = {}
	_comment['add']['body'] = comment


	_json = {}
	_json['update'] = {}
	_json['update']['comment'] = [_comment]

	command  = "curl -D- -u " + username + ":" + password +"  -X  PUT -d " + "'" + str(json.dumps(_json)) + "' -H \"Content-Type: application/json\" " + url + "/rest/api/2/issue/" + key
	print command
	sb_command = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
	print sb_command.communicate()[0]

def multi_find(s, r):
    return [pos for pos in range(len(s)) if s.startswith(r,pos)]


## download settings from autodeployment ###
os.system("rm -f {0}".format( os.path.join(WORKSPACE, "environments.csv")))
cmd = "svn export --username={0} --password={1} --non-interactive --force  http://10.33.20.5:8080/svn/PandG/autodeployment/environments.csv {3}".format(SVNUSER, SVNPASS, SERVICE, os.path.join(WORKSPACE, "environments.csv"))
print "[INFO] Executing: ", cmd
proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
output = proc.communicate()
print "[INFO] output: ", output

#######################


try:

	settings = Settings()
	settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
	settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	conf = settings.getSettings()
	print "### Testing settings feature", conf[SERVICE][ENVIRONMENT + "_PATH"], "###"
	TARGET = conf[SERVICE][ENVIRONMENT + "_PATH"]
	SERVICE = conf[SERVICE]["SVNName"]



	if TARGET is None or SERVICE is None or TARGET == "" or SERVICE == "":
		raise ValueError("TARGET or SERVICE is incorrect")


	if BRANCH is None or BRANCH == "":
		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, RELEASECANDIDATE), username=ARTIUSER, password=ARTIPASS )
		latest = getLatestFile(list, SERVICE)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory,RELEASECANDIDATE,latest)
	else:
		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, RELEASECANDIDATE + "_trunk_" + BRANCH), username=ARTIUSER, password=ARTIPASS )
		# searchName = "{0}_REV_*_BUILD_*_{1}.zip".format(SERVICE, "trunk_" + BRANCH)

		latest = getLatestFile(list, SERVICE)
		# latest = getLatestFile2(repository, folder, searchName=searchName, sortPattern)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory,RELEASECANDIDATE + "_trunk_" + BRANCH,latest)
	
	
	if latest is None or latest == "":
		raise ValueError("Variable of latest is incorrect")

	targets = getTargets(loadConfigSettings(os.path.join(WORKSPACE, "environments.csv")), ENVIRONMENT)

	if len(targets) == 0:
		raise ValueError("Variable of targets is incorrect")



	
	#target = "/var/www/vhosts/tst1-fbg-lcm.ladbrokes.com/htdocs/"
	target = TARGET
	cmd = "mco rpc -F ipaddress=\"/({0})/\" deploy_png  artifactory source='{1}' target='{2}' environment='{3}' service='{4}'".format("|".join("^"+ip+"$" for ip in targets), source, target, ENVIRONMENT, SERVICE)

	print "[INFO] Executing", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	output = proc.communicate()
	print "[INFO] output: ", output
	proc.wait()

	tmp = " ".join(output)

	indexes = multi_find(tmp, "### SUCCESS ###")


	print indexes

	if tmp.find("[ERROR]") != -1:
		errorIndex = tmp.find("[ERROR]")
		raise Exception("Error has occurred", tmp[errorIndex:])


	if tmp.find("ladsys.net") == -1:
		raise Exception("Server(s) not found or not allowed to deploy")


	if len(indexes) != len(targets):
		raise Exception("The package has not been fully deployed to all servers")

	comment = "The service {color:red}" + SERVICE + " ( " + source + " ){color} has been deployed successfully to : " + ENVIRONMENT
	print comment
	JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY, comment=comment)

except Exception as e1:
	e = sys.exc_info()[0]
	print e
	error = str(e1).replace("\"", "")
	error = error.replace("'", "")
	comment = "http://jira.ladbrokes.co.uk/jenkins/view/PNG/job/PnG_Deployment/{0}/console \n\n".format(BUILD_NUMBER)

	if len(error) > 32000:
		comment += "{color:red}Deployment has failed{color}: Log is too long to show it in JIRA, check link above"
	else:
		comment += "{color:red}Deployment has failed{color}: " + error
	print comment
	JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY, comment=comment)
	sys.exit(-1)

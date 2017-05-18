#!/usr/bin/python2.6 -u


import subprocess as sb
import sys
import shlex
import os
import re
from time import sleep
import datetime
import base64
import urllib2
import json
import hashlib
import glob
import fnmatch

sys.path.append(os.getenv("WORKSPACE", ""))

from DesignTimeParser.DesignTimeParser import DesignTimeParser

global JIRAKEY
global BRANCH
global REPOSITORY_BW

BRANCH = ""
#os.system("export JAVA_HOME=/opt/tibco/tibcojre64/1.7.0/bin")
#os.system("export JVM_LIB_DIR=/opt/tibco/tibcojre64/1.6.0/lib/amd64/server")


os.system("pwd")

# REPOSITORY_BW = "http://10.32.18.100/svn/eis/trunk/Development/Build/Bw/"

#REPOSITORY_BUILD_BW = "http://10.32.18.100/svn/eis/trunk/Development/Build/Bw/"
#REPOSITORY_CODE_BW = "http://10.32.18.100/svn/eis/trunk/Development/Code/Bw/"
global REPOSITORY_BASE
REPOSITORY_BASE = "http://10.32.18.100/svn/eis/"


# REPOSITORY_BW = "http://10.32.18.100/svn/cqm/cqm_dev_test/Build/Bw"

if  'REPOSITORY' in os.environ:
	REPOSITORY_LIST = os.environ['REPOSITORY']

JIRAKEY = os.getenv("JIRAKEY", "")

if 'REPORTER' in os.environ:
	global REPORTER
	REPORTER = os.environ['REPORTER'].split(":")[0]


if 'BUILD_NUMBER' in os.environ:
	global BUILD_NUMBER
	BUILD_NUMBER = os.environ['BUILD_NUMBER']
else:
	print "[ERROR] BUILD_NUMBER has not been set up"
	sys.exit(-1)

if 'BRANCH' in os.environ:
	BRANCH = os.environ['BRANCH'].strip()

WORKSPACE = os.environ['WORKSPACE']

if BRANCH is not None and len(BRANCH) > 0:
	REPOSITORY_CODE_BW = os.path.join(REPOSITORY_BASE, "branches", BRANCH, "Development/Code/Bw/")
	REPOSITORY_BUILD_BW = os.path.join(REPOSITORY_BASE, "branches", BRANCH, "Development/Build/Bw/")

	REPOSITORY_BW = REPOSITORY_BUILD_BW
	_subject = open(os.path.join(WORKSPACE, "subject.env"), "w")
	_subject.write("CUSTOMSUBJECT=" + BRANCH)
	_subject.close()


else:
	REPOSITORY_CODE_BW = os.path.join(REPOSITORY_BASE, "trunk", "Development/Code/Bw/")
	REPOSITORY_BUILD_BW = os.path.join(REPOSITORY_BASE, "trunk", "Development/Build/Bw/")
	REPOSITORY_BW = REPOSITORY_BUILD_BW

	_subject = open(os.path.join(WORKSPACE, "subject.env"), "w")
	_subject.write("CUSTOMSUBJECT=TRUNK")
	_subject.close()



global JIRAUSER, JIRAPASSWD
JIRAUSER = os.getenv("JIRAUSER", "")
JIRAPASSWD = os.getenv("JIRAUSER", "")

global SVNUSER,SVNPASS
SVNUSER = os.environ['SVNUSER']

SVNPASS = os.environ['SVNPASS']

VALIDATE_ONLY = os.environ['VALIDATE_ONLY']

BUILD_ONLY = os.environ['BUILD_ONLY']




global JIRAURL
JIRAURL="http://10.33.20.21:8080/jira"

def cleanUp():
	dirs = os.walk(WORKSPACE)
	dirs.next()
	dirs.next()

	for dir in dirs:
		if dir[0].find("repo") == -1 and dir[0].find("branches") == -1:
			os.system("rm -rf " + dir[0])




if os.path.exists(WORKSPACE + "/repo"):
	cleanUp()

#######################################################################################
#
#

def zipFile(_filein, _fileout):
	command_zip_file = "zip -r " + _fileout + " " + _filein
	zip_file = sb.Popen(shlex.split(command_zip_file), stdout=sb.PIPE)
	data_zip_file = zip_file.stdout.read()
	print "[INFO] " + data_zip_file

########################################################################################
# Get List of domains for Environments
#

def getEnvTable():
  os.chdir(WORKSPACE)
  command = "curl -u " + SVNUSER + ":" + SVNPASS + " -X GET http://10.33.20.5:8080/svn/eis/cqm/AutoDeployment/EIS_Environment_List.txt"
  print command
  cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE)
  data_cmd = cmd.communicate()[0]
  return data_cmd



#######################################################################################
#	Artifactory module
#

global repository, artifactory_server
repository = "EIS_DEVOPS"
artifactory_server = "http://10.33.20.7:8080/artifactory/simple/" + repository + "/"

mail = open("Mail.txt", "w")

if "ARTIPASS" in os.environ and "ARTIUSER" in os.environ:
	global ARTIPASS, ARTIUSER
	ARTIPASS = os.environ['ARTIPASS']
	ARTIUSER = os.environ['ARTIUSER']
else:
	msg = "[ERROR] User or password for artifactory has not been set up"
	print msg
	mail.write(msg + "\n")
	os.exit(-1)



def uploadToFolder(_file, _folder):
# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
	global ARTIUSER, ARTIPASS, artifactory_server
	preHash = open(_file, "rb").read()
	hash_md5 = hashlib.md5(preHash).hexdigest()
	hash_sha1 = hashlib.sha1(preHash).hexdigest()
	command_curl_upload = "curl -D- -X PUT -u " + ARTIUSER + ":" + ARTIPASS + " " + artifactory_server + _folder + "/ -T " + _file + " -H 'X-Checksum-Md5: " + hash_md5 + "' -H 'X-Checksum-Sha1: " + hash_sha1 + "'"
	print command_curl_upload
	curl_upload = sb.Popen(shlex.split(command_curl_upload), stdout=sb.PIPE, stderr=sb.PIPE)
	data_curl_upload = curl_upload.stdout.read()

	# print data_curl_upload
	if data_curl_upload.find("201 Created") == -1:
		msg = "[ERROR] File has not been uploaded to artifactory properly: " + data_curl_upload
		print msg
		mail.write(msg + "\n")
		return False
	else:
		msg = "[INFO] " + data_curl_upload
		return True


def uploadToTrunk(_file):
	if BRANCH is not None and len(BRANCH) > 0:
		return uploadToFolder(_file, "trunk_" + BRANCH)
	else:
		return uploadToFolder(_file, "trunk")


########################################################################################


def scmPollLog(_folder):
	if not os.path.exists(os.path.join(WORKSPACE, _folder)):
		# svn_co_command = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " http://10.33.20.5:8080/svn/cqm/cqm_dev_test/Code/Bw repo"
		svn_co_command = "svn --non-interactive co --username=" + SVNUSER + " --password=" + SVNPASS + " " + REPOSITORY_CODE_BW + " " + _folder
		print svn_co_command
		svn_co = sb.Popen(shlex.split(svn_co_command), stdout=sb.PIPE)
		data_svn_co = svn_co.stdout.read()
		print data_svn_co



	os.chdir(_folder)
	os.system("pwd")
	svn_log_command = "svn up --non-interactive --username=" + SVNUSER + " --password=" + SVNPASS
	print svn_log_command
	svn_log = sb.Popen(shlex.split(svn_log_command), stdout=sb.PIPE)
	data_svn_log = svn_log.stdout.read()
	print data_svn_log
	os.chdir(WORKSPACE)
	os.system("pwd")

	# file1 = open("s.txt", "r")
	# data = file1.read()
	# file1.close()


	data = data_svn_log.split("\n")
	# data = data.split("------------------------------------------------------------------------")

	serviceList = []
	for i in data:
		print i
		# group = re.search(ur'(D|M|A)\s((?:\/|\w|[0-9\.]|)+)', i)
		group = re.search(ur'(D|M|A|AU|U)\s+((?:\/|\w|[0-9\.])+)', i)
		if group is not None and group.groups() is not None:
			print group.groups()
			subGroup = re.search(ur'[0-9]\.[0-9]\/([^\/]*)', group.group(2))
			if subGroup is not None and subGroup.groups is not None:
				serviceList.append(subGroup.group(1))
				print subGroup.groups()

	if len(serviceList) > 0:
		myset = set(serviceList)
		print myset
		return myset
	else:
		return None


#######################################################################################


def deploy_module(_EAR_NAME, _IP_ADDRESS, _HOT_RELEASE):

  deployment_log = open("deployment.log", "w")
  if _HOT_RELEASE == "NO":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./manageApp.sh " + _EAR_NAME + " 1 stop; ./deploy.sh " + _EAR_NAME + "; ./manageApp.sh " + _EAR_NAME + " 1 start\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    print data_command
    deployment_log.write(data_command)
  elif _HOT_RELEASE == "YES":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh " + _EAR_NAME + " 2>&1;\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    print data_command
    deployment_log.write(data_command)

  return data_command


#######################################################################################

def JiraGetRepoList(JIRAKEY):
	url = os.path.join("http://10.33.20.21:8080/jira/rest/api/2/issue", JIRAKEY)
	print url
	req = urllib2.Request(url)
	req.add_header("Authorization", "Basic " + base64.b64encode(JIRAUSER + ":" + JIRAPASSWD))
	resp = urllib2.urlopen(req)
	data = resp.read()
	data = json.loads(data.replace("\\r\\n", '$'))

	# print json.loads(json.dumps(data['fields']['comment']['comments'][0]))['body'].split("$")[1:-1]

	REPOSITORY_LIST = ""
	# REPOSITORY_LIST_TMP = data['fields']['comment']['comments']['body'].split("$")[1:-1]
	REPOSITORY_LIST_TMP = json.loads(json.dumps(data['fields']['comment']['comments'][0]))['body'].split("$")[1:-1]
	
	for i in range(0, len(REPOSITORY_LIST_TMP)):
		# print REPOSITORY_LIST_TMP[i]
		if (REPOSITORY_LIST_TMP[i].find(".ear") != -1):
			print REPOSITORY_LIST_TMP[i]
			print i
			REPOSITORY_LIST += str(REPOSITORY_LIST_TMP[i][:-4]) + ","
	REPOSITORY_LIST = REPOSITORY_LIST[:-1]
	print REPOSITORY_LIST
	return REPOSITORY_LIST




def JIRA_add_comment(username, password, comment, url, key):
	"""
	{3}/rest/api/2/issue/{4}

str(json.dumps(_json)), JIRAURL, JIRAKEY
	"""

	""" _file, _folder

	"""

	url = os.path.join(url, "rest/api/2/issue", key)

	_comment = {}
	_comment['add'] = {}
	# _comment['add']['body'] = "The service {color:red}" + _file.split("_")[0] + "{color} has been built successfully and is available here: " + artifactory_server + _folder + "/" + _file
	_comment['add']['body'] = comment

	_json = {}
	_json['update'] = {}
	_json['update']['comment'] = [_comment]

	# command  = "curl -D- -u " + JIRAUSER + ":" + JIRAPASSWD +"  -X  PUT -d " + "'" + str(json.dumps(_json)) + "' -H \"Content-Type: application/json\" " + JIRAURL + "/rest/api/2/issue/" + JIRAKEY
	command  = "curl -D- -u {0}:{1}  -X  PUT -d '{2}' -H \"Content-Type: application/json\" {3}".format(username, password, str(json.dumps(_json)), url)
	print command
	sb_command = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
	print sb_command.communicate()[0]

	




def validate_configs(_file):
	os.chdir(WORKSPACE)
	os.chdir("tmp")
	os.system("rm -rf /opt/tibco/applications/devops/deploy/cfg/*.cfg")
	os.system("cp cfg/*.cfg /opt/tibco/applications/devops/deploy/cfg")

	os.system("rm -rf /opt/tibco/applications/devops/deploy/ear/*.ear")
	os.system("cp " + _file +".ear /opt/tibco/applications/devops/deploy/ear")



	lines = getEnvTable()
	requiredList = set()
	for item in lines.split("\n"):
		line = item.split("|")
		if len(line) > 1:
			requiredList.add(line[-2])

	_files = os.walk(WORKSPACE + "/tmp/cfg")

	_configs = _files.next()
	_passed = True

	for item in requiredList:
		if len(_configs) < 2 or _file + "-" + item + ".cfg" not in _configs[2]:
			msg = "[WARNING] Missing config file: " + _file + "-" + item + ".cfg\n"
			mail.write(msg +"\n")
			print msg
			_passed = False

	# if _passed is False:
		# return False 



	data_all_configs = ""
	_list_files = glob.glob(WORKSPACE + "/tmp/cfg/*.cfg")


	for __file in _list_files:
		#_env_conf =  __file[__file.find("-")+1:__file.find(".")]
		_env_conf =  __file.split("/")[-1].split("-")[-1].split(".")[0]

		#[__file.find("-")+1:__file.find(".")]
		msg = "[INFO] Starting config validation for: " + _env_conf + "\r\n"
		print msg
		mail.write(msg +"\n")
		mail.flush()

		os.chdir("/opt/tibco/applications/devops/deploy/bin")
		command_validate_conf = "./deploy.sh " + _file + " makeConfig " + _env_conf
		sb_command_validate_conf = sb.Popen(shlex.split(command_validate_conf), stdout=sb.PIPE, stderr=sb.PIPE)
		(data_command_validate_confg_out, data_command_validate_confg_err) = sb_command_validate_conf.communicate()
		data_command_validate_confg = data_command_validate_confg_out + "\n" + data_command_validate_confg_err
		print data_command_validate_confg
		data_all_configs += data_command_validate_confg + "\r\n"
		mail.write(data_command_validate_confg + "\n")
		mail.flush()

	if data_all_configs.lower().find("error") == -1 and data_all_configs.lower().find("fail") == -1 and data_all_configs.lower().find("exception") == -1:
		return True
	return False

repo_folder = "repo"
if BRANCH is not None and len(BRANCH) > 0:
	repo_folder = os.path.join("branches", BRANCH)

myset = scmPollLog(repo_folder)
REPOSITORY_LIST = ""
if myset is not None and len(myset) > 0:
	for i in range(0, len(myset)):
		REPOSITORY_LIST += myset.pop() + ","
	REPOSITORY_LIST = REPOSITORY_LIST[:-1]
else:
	msg = "[INFO] No changes in svn"
	print msg
	mail.write(msg +"\n")
	mail.flush()


if "FORCE_SERVICE" in os.environ and os.environ['FORCE_SERVICE'] is not None and os.environ['FORCE_SERVICE'] != "":
	print "[INFO] Trying to build service by force"
	REPOSITORY_LIST = (os.environ['FORCE_SERVICE'])

if REPOSITORY_LIST is None or len(REPOSITORY_LIST) == 0:
	msg = "[WARNING] There is no service on the list to build"
	print msg
	mail.write(msg +"\n")
	mail.flush()
	sys.exit(0)

# REPOSITORY_LIST = JiraGetRepoList(JIRAKEY)
print "REPOSITORY_LIST" + str(REPOSITORY_LIST)



command_svn_list = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" " + " list " + REPOSITORY_BW + " -R "
print command_svn_list
sb1 = sb.Popen(shlex.split(command_svn_list), stdout=sb.PIPE)
data_in = sb1.stdout.read()
sb2 = sb.Popen(shlex.split("egrep \"/$\""), stdout=sb.PIPE, stdin=sb.PIPE)
data_out = sb2.communicate(input=data_in)[0]
# print (data_out)

data_svn_list = data_out


# os.system("rm -rf " + WORKSPACE + "/\!(repo)")

mail = open("Mail.txt", "w")
mail.write("Started at: " + str(datetime.datetime.now()) + "\n")
mail.flush()


if "REPORTER" in globals() and REPORTER is not None and REPORTER != "":
	msg = "[INFO] Triggered by " + REPORTER + "\n"
	mail.write(msg)
	mail.flush()
	print msg



svn_auth =  " --non-interactive --username=\"" + SVNUSER + "\" --password=\"" + SVNPASS + "\" "

command_svn_list_code = "svn " + svn_auth + " list " + REPOSITORY_CODE_BW + " -R | egrep \"\.archive$\" "

LIST_COMMITERS = {}
LIST_REVISION = {}

def validate(repo):

	repo_list = repo.split("/")
	print "[INFO] Repository: " + repo

	print "[INFO] " + str(repo_list)
	print "[INFO] " + str(repo_list[-1:][0])
	archive_file = os.path.join("Build",repo_list[-2:][0] + ".archive")

	command_svn_info_code_archive = "svn " + svn_auth + " info " + os.path.join(repo, archive_file)

	print "[COMMAND] " + command_svn_info_code_archive



	svn_info_code_archive = sb.Popen(shlex.split(command_svn_info_code_archive), stdout=sb.PIPE)

	data_svn_info_code_archive = svn_info_code_archive.stdout.read()

	print data_svn_info_code_archive

	if data_svn_info_code_archive.find("Path:") != -1:

		group = re.search(ur'Last Changed Author: (.*)\n', data_svn_info_code_archive)
		if group is not None and group.group() is not None and len(group.groups()) > 0:
			LIST_COMMITERS[os.path.basename(os.path.dirname(repo))] = group.group(1)

		group = re.search(ur'Revision: (.*)\n', data_svn_info_code_archive)
		# group = re.search(ur'Last Changed Rev: (.*)\n', data_svn_info_code_archive)
		
		if group is not None and group.group() is not None and len(group.groups()) > 0:
			LIST_REVISION[os.path.basename(os.path.dirname(repo))] = group.group(1)


		print "[OK] Found archive file in: " + os.path.join(repo, archive_file)

	else:

		msg = "[ERROR] Archive file not found in: " + repo
		print msg
		mail.write(msg + "\n")
		mail.flush()
		return False



	# repo_build = repo.replace("Code/Bw", "Build/Bw")

	# command_svn_info_build_bin = "svn " + svn_auth + " info " + os.path.join(repo_build, "bin")

	# svn_info_build_bin = sb.Popen(shlex.split(command_svn_info_build_bin), stdout=sb.PIPE)

	# data_svn_info_build_bin = svn_info_build_bin.stdout.read()

	# print "[COMMAND] " + command_svn_info_build_bin

	# if data_svn_info_build_bin.find("Path:") != -1:

	# 	print "[OK] Found bin in: " + repo_build + "bin"

	# else:

	# 	msg = "[ERROR] Not found bin in: " + repo_build
	# 	print msg
	# 	mail.write(msg + "\n")
	# 	mail.flush()
	# 	return False

	return True

def getEnvTable():
  os.chdir(WORKSPACE)
  command = "curl -u " + SVNUSER + ":" + SVNPASS + " -X GET http://10.33.20.5:8080/svn/eis/cqm/AutoDeployment/EIS_Environment_List.txt"
  print command
  cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE)
  data_cmd = cmd.communicate()[0]
  return data_cmd


def getIpAddress(_data_cmd, _ENVIRONMENT = ""):

  # data_cmd = getEnvTable()
  data_cmd = _data_cmd

  group = re.search(_ENVIRONMENT + ur'\|([^\|]*)\|[^\|]*', data_cmd)

 #  if _ENVIRONMENT != null and _ENVIRONMENT != "":
	# group = re.search(_ENVIRONMENT + ur'\|([^\|]*)\|[^\|]*', data_cmd)  	
  if group is not None and len(group.groups()) > 0:
    print group.groups()[0]
    domain = group.groups()[0]

    command = "nslookup " + domain
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_cmd = ""
    data_cmd = cmd.communicate()
    tmp = data_cmd[0].split()[-1]
    if tmp.split() != "":
      global IP_ADDRESS
      IP_ADDRESS = tmp
      
      print IP_ADDRESS
      # return IP_ADDRESS
    else:
      msg = "[ERROR] IP_ADDRESS does not exist from server " + _ENVIRONMENT + "\n"
      print msg
      mail.write(msg +"\n")
      sys.exit(-1)
  else:
    msg = "[ERROR] IP_ADDRESS does not exist from server " + _ENVIRONMENT + "\n"
    print msg
    mail.write(msg +"\n")
    sys.exit(-1)

#getDTL(pathSvnLib, os.path.join(WORKSPACE, "dtl"), os.path.join(WORKSPACE, "file.properties") )
def getDTL(_path, _dtlfolder, _fileproperties, _servicefolder):

	print "### getDTL ###"

	delete_old_libs = "rm -rf {0}".format(_dtlfolder)
	print "[INFO] Executing", delete_old_libs
	sb_delete_old_libs = sb.Popen(shlex.split(delete_old_libs), stdout=sb.PIPE, stderr=sb.PIPE)
	print sb_delete_old_libs.communicate()

	cmd = "svn --non-interactive --force --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" export {0} {1}".format(_path, _dtlfolder)
	print "[INFO] Executing", cmd
	sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	data_cmd = sb_cmd.communicate()

	print data_cmd

	
	designTimeParser = DesignTimeParser(source=os.path.join(_servicefolder, ".designtimelibs"), 
		target=_fileproperties, 
		folder=_dtlfolder,
		debug=True)
	designTimeParser.generateConfiguration()


def copy_tibco_artifact(_Ear_Bundles, _IP_address, _Destination_dir, _ENVIRONMENT):
  command1 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"rm -rf " + _Destination_dir + "; mkdir -p " + _Destination_dir + "\""
  print command1
  command1_sb = sb.Popen(shlex.split(command1), stdout=sb.PIPE)
  data_command1 = command1_sb.communicate()[0]
  print data_command1

  command2 = "scp -i /home/jenkinsci/.ssh/tibco_id_rsa " + _Ear_Bundles + " tibco@" + _IP_address + ":" + _Destination_dir
  print command2
  command2_sb = sb.Popen(shlex.split(command2), stdout=sb.PIPE, stderr=sb.PIPE)
  data_command2 = command2_sb.communicate()[0]
  print data_command2

  # command3 = "ssh -i ~/.ssh/tibco_id_rsa tibco@$" + _IP_address + " -C \"cd " + _Destination_dir + "; unzip " + _Ear_Bundles + "; cd temp; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp *.cfg  /opt/tibco/applications/devops/deploy/cfg/; \""
  command3 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + _Destination_dir + "; unzip " + _Ear_Bundles + "; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp cfg/*.cfg  /opt/tibco/applications/devops/deploy/cfg/; \""
  print command3
  command3_sb = sb.Popen(shlex.split(command3), stdout=sb.PIPE)
  data_command3 = command3_sb.communicate()[0]
  print data_command3

  data_command4 = ""
  if "EMS_SCRIPTS" in os.environ and EMS_SCRIPTS is not None and EMS_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    command4 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + Destination_dir + "; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*; cp -r " + EMS_SCRIPTS + " /opt/tibco/applications/devops/deploy/ems/; rm -rf " + EMS_SCRIPTS + "\""
    # ssh -i ~/.ssh/tibco_id_rsa tibco@$IP_address -C "cd $Destination_dir; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*; cp -r $EMS_SCRIPTS /opt/tibco/applications/devops/deploy/ems/; rm -rf $EMS_SCRIPTS"
    print command4
    command4_sb = sb.Popen(shlex.split(command4), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command4 = command4_sb.communicate()[0]


  data_command5 = ""
  if "COUCHBASE_SCRIPTS" in os.environ and COUCHBASE_SCRIPTS is not None and COUCHBASE_SCRIPTS != "" and VALIDATION_ONLY == "NO":
    command5 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + Destination_dir + "; tar xvf Couchbase.tar;  mkdir -p /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*; cp -r " + COUCHBASE_SCRIPTS + " /opt/tibco/applications/devops/deploy/couchbase/; rm -rf " + EMS_SCRIPTS + "\""
    print command5
    command5_sb = sb.Popen(shlex.split(command5), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command5 = command5_sb.communicate()[0]


  return data_command1 + "\n" + data_command2 + "\n" + data_command3 + "\n" + data_command4 + "\n" + data_command5 + "\n"


def getSuffix(_data_cmd, _ENVIRONMENT):
  data_cmd = _data_cmd
  group = re.search(_ENVIRONMENT +  ur'\|[^\|]*\|([^\|]*)', data_cmd)
  if group is not None and len(group.groups()) > 0:
    # print group.groups()[0]
    global SUFFIX
    SUFFIX = group.groups()[0]
    print "[INFO] " + SUFFIX + "\n"


def BuildEarFile(REPOSITORY):	
	print REPOSITORY
	REPOSITORY = REPOSITORY[:-1]


	WORKSPACE = os.environ['WORKSPACE']


	buildear = "/opt/tibco/tra/5.7/bin/buildear"
	tibco_dir = "/opt/tibco/tra/5.7/bin/"

	basename = os.path.basename(REPOSITORY)


	TMP = REPOSITORY
	
	# if BRANCH is not None and len(BRANCH) > 0:
	# 	TMP = TMP.replace("branches", "trunk")
	# 	TMP = TMP.replace(BRANCH + "/", "")

	#REPOSITORY_BUILD = os.path.join(REPOSITORY.replace("Code/Bw", "Build/Bw"), "bin")
	REPOSITORY_BUILD = os.path.join(TMP.replace("Code/Bw", "Build/Bw"), "bin")


	os.chdir(WORKSPACE)
	os.system("pwd")
	
	
	



	# command for svn checkout

	command_svn_co = "svn --non-interactive --username=" + SVNUSER +" --password=" + SVNPASS +" co " + REPOSITORY

	svn_co = sb.Popen(shlex.split(command_svn_co), stdout=sb.PIPE, stderr=sb.PIPE)

	print svn_co.stdout.read()



	# change directory to tibco tool

	print "[INFO] buildear folder: " + os.path.dirname(buildear)		
	os.chdir(os.path.dirname(buildear))
	os.system("pwd") 





	# command_tibco = buildear +  " -s -x -ear /Build/" + basename + ".archive" + " -p " + WORKSPACE + "/" + basename + " -o " + WORKSPACE + "/tmp/" + basename + ".ear"
	command_tibco = "./buildear -s -x -a " + WORKSPACE + "/file.properties -ear /Build/" + basename + ".archive" + " -p " + os.path.join(WORKSPACE, basename) + " -o " + os.path.join(WORKSPACE,"tmp", basename + ".ear")

	print command_tibco









	# /opt/tibco/tra/5.7/bin/buildear -x -s -ear /Build/ContentBroker.archive -o /tmp/file.ear -p /app/jenkins-slave/workspace/cqm_build_ear/ContentBroker

	# command_svn_import = "svn --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" import -m \"Adding " + basename + ".ear\" "  + WORKSPACE + "/" + basename + ".ear " + REPOSITORY_BUILD + basename + ".ear"


	command_svn_info_dir = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" info " + REPOSITORY_BUILD

	#command_svn_info_file = "svn --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" info " + os.path.join(REPOSITORY_BUILD, basename + ".ear")

	command_svn_co_dir = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" co " + REPOSITORY_BUILD + " tmp --depth empty"

	command_svn_co_file = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" up " + basename + ".ear"

	command_svn_ci_file = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" ci -m \" Changed file: "  + basename + ".ear ;Last Committed by: " + LIST_COMMITERS[basename] + " ;Revision: " + LIST_REVISION[basename] + "\" " + basename + ".ear"

	

	
	


	# @deprecated
	#command_svn_co_dir_cfg = "svn --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" co " + REPOSITORY_BUILD.replace("bin", "cfg") + " cfg"


	command_svn_co_dir_cfg = "svn --non-interactive --username=\"" + SVNUSER +"\" --password=\"" + SVNPASS + "\" co " + REPOSITORY_BUILD.replace("bin", "cfg") + " cfg"



	print "[INFO] " + command_svn_info_dir

	#print "[INFO] " + command_svn_info_file

	# @deprecated
	#print "[INFO] " + command_svn_co_dir

	# @deprecated
	#print "[INFO] " + command_svn_co_file

	# @deprecated
	#print "[INFO] " + command_svn_ci_file

	print "[INFO] " + command_svn_co_dir_cfg




	svn_info_dir = sb.Popen(shlex.split(command_svn_info_dir), stdout=sb.PIPE)

	# deprecated
	#svn_info_file = sb.Popen(shlex.split(command_svn_info_file), stdout=sb.PIPE)

	data_svn_info_dir = svn_info_dir.stdout.read()

	#data_svn_info_file = svn_info_file.stdout.read()

	print "[INFO] " + data_svn_info_dir

	#print "[INFO] " + data_svn_info_file


	# Check consistency in svn repository Code and Build tree
	if (data_svn_info_dir.find("Path") != -1):

		#if (data_svn_info_file.find("Path") != -1):

		os.chdir(WORKSPACE)
		os.system("pwd")

		


		if BRANCH is not None and len(BRANCH) > 0:
			pathSvnLib = "http://10.33.20.5:8080/svn/eis/{0}/Development/Code/Bw/Shared".format(os.path.join("branches", BRANCH) )
		else:
			pathSvnLib = "http://10.33.20.5:8080/svn/eis/{0}/Development/Code/Bw/Shared".format("trunk")

		getDTL(_path=pathSvnLib, 
			_dtlfolder=os.path.join(WORKSPACE, "dtl"), 
			_fileproperties=os.path.join(WORKSPACE, "file.properties"), 
			_servicefolder=os.path.join(WORKSPACE, basename))




		# clean or create tmp directory
		if not (os.path.exists(WORKSPACE + "/tmp")):

			os.makedirs("tmp")

		# if not (os.path.exists(WORKSPACE + "/cfg")):
		# 	os.makedirs("cfg")

		os.system("rm -rf tmp/*")
		os.system("rm -rf tmp/.*")

		# os.system("rm -rf cfg/*")
		# os.system("rm -rf cfg/.*")


		# Checkout empty directory
		svn_co_dir = sb.Popen(shlex.split(command_svn_co_dir), stdout=sb.PIPE)

		data_svn_co_dir = svn_co_dir.stdout.read()

		print data_svn_co_dir

		os.chdir("tmp")
		os.system("pwd")

		# Checkout EAR File - deprecated
		# svn_co_file = sb.Popen(shlex.split(command_svn_co_file), stdout=sb.PIPE)

		# data_svn_co_file = svn_co_file.stdout.read()

		# print "[INFO] " + data_svn_co_file

		# Remove old EAR Files
		os.system("rm -rf " + basename + ".ear")


		# checkout cfg files
		svn_co_dir_cfg = sb.Popen(shlex.split(command_svn_co_dir_cfg), stdout=sb.PIPE)
		data_svn_co_dir_cfg = svn_co_dir_cfg.communicate()[0]
		print "[INFO] " + data_svn_co_dir_cfg
		os.system("rm -rf cfg/.svn")

		# go to tibco to run command
		os.chdir(tibco_dir)
		os.system("pwd")

		_list = os.walk(WORKSPACE + "/tmp/cfg").next()[2]
		if len(_list) > 0:
			_list = _list[0]
			if _list.find(".cfg") != -1:
				print _list
				for line in open(WORKSPACE + "/tmp/cfg/" + _list):
					if "binding[1]/product/version=5.12" in line:
						buildear = "/opt/tibco/tra/5.9/bin/buildear"
						tibco_dir = "/opt/tibco/tra/5.9/bin/"
						print "[INFO] buildear folder: " + os.path.dirname(buildear)
						os.chdir(os.path.dirname(buildear))
						os.system("pwd") 



		# Set environment variable for linux (xvfb/x11)
		os.environ['DISPLAY'] = "localhost:1.0"
		os.system("export DISPLAY=localhost:1.0")
		print "[INFO] DISPLAY=" + os.getenv("DISPLAY")
		# os.system(command_tibco)
		tibco_out = ""
		tibco_sb = sb.Popen(shlex.split(command_tibco), stdout=sb.PIPE, stdin=sb.PIPE)
		# tibco_out = tibco_sb.stdout.read()
		tibco_out = tibco_sb.communicate(input=os.linesep.join(['y']))[0]
		# tibco_out = os.popen(command_tibco).read()
		if tibco_out.lower().find("exception") != -1:
			msg = "[ERROR] Exception: " + str(tibco_out)
			print msg
			mail.write(msg +"\n")
		else:
			print "[INFO] " + str(tibco_out)

		print "[INFO] DISPLAY=" + os.getenv("DISPLAY")

		os.chdir(os.path.join(WORKSPACE, "tmp"))
		os.system("pwd")

		os.system("ls -lah")
        
		# Push EAR File to svn (aka artifactory) - deprecated
		if BUILD_ONLY != "true" and tibco_out.lower().find("exception") == -1:
			# svn_ci_file = sb.Popen(shlex.split(command_svn_ci_file), stdout=sb.PIPE)

			# data_svn_ci_file = svn_ci_file.stdout.read()

			# print "[INFO] " + data_svn_ci_file

			
			data_cmd = getEnvTable()
			getIpAddress(data_cmd, "LS_DEV")
			getSuffix(data_cmd, "LS_DEV")

			devConfigFile = basename + "-" + SUFFIX + ".cfg"
			if os.path.exists(WORKSPACE + "/tmp/cfg/" + devConfigFile) != True:
				msg = "[ERROR] Missing config " + devConfigFile
				print msg
				mail.write(msg +"\n")
				mail.flush()
				return -1

			os.chdir(os.path.join(WORKSPACE, "tmp"))
			BRANCH_SUFFIX = ""
			if BRANCH is not None and len(BRANCH) > 0:
				BRANCH_SUFFIX = "trunk_" + BRANCH
			else:
				BRANCH_SUFFIX = "trunk"

			zipfile = basename + "_REV_" + LIST_REVISION[basename] + "_BUILD_" + BUILD_NUMBER + "_" + BRANCH_SUFFIX + ".zip"
			print zipfile
			zipFile(basename + ".ear" + " cfg", zipfile) 


			if (validate_configs(basename) == True):
				msg = "[INFO] Config validation passed successfully"
				print msg
				mail.write(msg +"\n")
				mail.flush()
				os.chdir(os.path.join(WORKSPACE, "tmp"))
				os.chdir(WORKSPACE + "/tmp")
				print WORKSPACE + "/tmp"
				os.system("ls -lah")
				os.system("pwd")

				
				os.chdir(WORKSPACE + "/tmp")
				os.system("ls -lah")
				os.system("pwd")
				data_copy_tibco_artifact = copy_tibco_artifact(zipfile, IP_ADDRESS, "/opt/tibco/cqm_eis_deployment", "LS_DEV")
				print data_copy_tibco_artifact

				data_deploy_module = deploy_module(basename, IP_ADDRESS, "YES").lower()
				msg = "[INFO] deploy_module: "  + data_deploy_module
				mail.write(msg)
				mail.flush
				print msg
				if (data_deploy_module.find("fail") == -1) and (data_deploy_module.find("error") == -1) and (data_deploy_module.find("exception")):
					if uploadToTrunk(zipfile):
						#if 'JIRAKEY' in globals() and JIRAKEY != None and JIRAKEY != "":
						if JIRAKEY != "":
							# JIRA_add_comment(zipfile, "trunk")

							comment = "The service {color:red}" + basename + "{color} has been built successfully and is available here: " + artifactory_server + "trunk" + "/" + zipfile
							JIRA_add_comment(username=JIRAUSER, password=JIRAPASSWD, url=JIRAURL, key=JIRAKEY, comment=comment)
				else:
					msg = "[ERROR] Build Ear File Failed"
					print msg
					mail.write(msg +"\n")
					mail.write("[ERROR] data_deploy_module: " + data_deploy_module)
					mail.flush()
					return -1
			else:
				msg = "[ERROR] Config validation failed\n"
				print msg
				mail.write(msg)





		# else:
		# 	msg = "[ERROR] Archive File: " + os.path.join(REPOSITORY,"Build",basename + ".archive") + " does not exist"
		# 	print msg
		# 	mail.write(msg+"\n")
		# 	mail.flush()
		# 	sys.exit(-1)
	else:
		msg = "[ERROR] Directory: " + REPOSITORY_BUILD + " does not exist"
		print msg
		mail.write(msg + "\n")
		mail.flush()
		sys.exit(-1)


#####################################################################


LIST = REPOSITORY_LIST.split(",")
LIST2 = []


LIST_FOUND = {}

for i in range(0, len(LIST)):
	LIST_FOUND[LIST[i]] = ""


print "LIST = " + str(LIST) + str(REPOSITORY_LIST) + str(LIST_FOUND)

data_svn_list = data_svn_list.split("\n")
print "[INFO] " + str(data_svn_list)

for i in range(0, len(LIST)):
	# print LIST[i]
	for p in range(0, len(data_svn_list)):
		tmp = data_svn_list[p].split("/")
		# print tmp
		if  len(tmp) > 1 and tmp[-2] == LIST[i]:

			REPOSITORY_EXEC = ""
			REPOSITORY_EXEC = "/".join(tmp)
			REPOSITORY_EXEC_TMP = REPOSITORY_EXEC


			reviewFile = open(os.path.join(WORKSPACE, "review.prop"), "w")
			reviewFile.write("directory=" + REPOSITORY_EXEC_TMP +"\n")

			branchName = BRANCH
			if BRANCH is None:
				branchName = "trunk"

			reviewFile.write("branch=" + branchName + "\n")
			reviewFile.close()

			print "[INFO] REPOSITORY_EXEC_TMP=" + REPOSITORY_EXEC_TMP
			print "[INFO] @@@ " + os.path.join(REPOSITORY_CODE_BW, REPOSITORY_EXEC_TMP)
			REPOSITORY_EXEC = os.path.join(REPOSITORY_BW, REPOSITORY_EXEC)
			group = re.search(ur'http.*\/[0-9]\.[0-9]\/.*\/$', REPOSITORY_EXEC)
			if group != None and len(group.group()) > 0:
				print "[INFO] " + str(group.group())
				# REPOSITORY_EXEC = REPOSITORY_EXEC[:-1]
				# @@@
				REPOSITORY_EXEC = os.path.join(REPOSITORY_CODE_BW, REPOSITORY_EXEC_TMP)
				#REPOSITORY_EXEC = REPOSITORY_EXEC.replace("Build/Bw", "Code/Bw")
				print "[INFO] " + str(REPOSITORY_EXEC)

				LIST2.append(REPOSITORY_EXEC)
				LIST_FOUND[LIST[i]] = REPOSITORY_EXEC
			
print LIST2

if len(LIST2) > len(LIST):
	msg = "[ERROR] Inconsistency in svn"
	print msg
	mail.write(msg + "\n")
	mail.flush()

if len(LIST2) != len(LIST):
	msg = ""
	for i in range(0, len(LIST_FOUND)):
		if LIST_FOUND[LIST_FOUND.keys()[i]] == "":
			msg = "[ERROR] Service " + LIST_FOUND.keys()[i] + " has not been found"
			print msg
			mail.write(msg + "\n")
			
	# sys.exit(-1)



# if 'REPOSITORY' not in locals() or len(REPOSITORY) == 0:
# 	print "[ERROR] Incorrect service was given as a parameter"
# 	return 0



validate_passed = True
for i in range(0, len(LIST2)):
	if validate(LIST2[i]) == False:
		validate_passed = False


if VALIDATE_ONLY != "true" and validate_passed == True:
	for i in range(0, len(LIST2)):
		mail.write("Service " + LIST2[i] + "\n")
		BuildEarFile(LIST2[i])


	
mail.flush()
mail.close()
print LIST_COMMITERS


mail = open(WORKSPACE + "/Mail.txt", "r")
if mail.read().lower().find("error") != -1 or mail.read().lower().find("fail") != -1:
	print "[BUILD FAILED]"
	if JIRAKEY != "":
		comment = "{color:red} BUILD FAILED: http://10.33.20.13:8080/jenkins/job/EIS_DevOps_buildear/" + BUILD_NUMBER + "/console"
		JIRA_add_comment(username=JIRAUSER, password=JIRAPASSWD, url=JIRAURL, key=JIRAKEY, comment=comment)
	sys.exit(-1)

# BuildEarFile("http://10.32.18.100/svn/cqm/cqm_dev_test/Code/Bw/Customer/Loyalty/LoyaltyAccount/2.0/LoyaltyAccount20")


# if (data_svn_info_dir.find("Path") != -1):

# 	svn_import = sb.Popen(shlex.split(command_svn_import), stdout=sb.PIPE)

# 	print svn_import.stdout.read()


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
from settings import Settings

global SERVICE, SVNUSER, SVNPASS, BUILD_NUMBER, ARTIUSER, ARTIPASS, BRANCH

SERVICE = os.getenv("SERVICE", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
ARTIUSER = os.getenv("ARTIUSER", None)
ARTIPASS = os.getenv("ARTIPASS", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
JIRAKEY = os.getenv("JIRAKEY", None)
BUILD_NUMBER = os.getenv("BUILD_NUMBER", None)
WORKSPACE = os.getenv("WORKSPACE", None)
BRANCH = os.getenv("BRANCH", None)
repository = "PnG" 
artifactory = "PnG"

# SVNREPOSITORY = "classic_web_interim"
SVNREPOSITORY = "PandG"


# SERVICE = "Fairgaming"
# SVNUSER = "cqmsvn"
# SVNPASS = "K_29^ob"
# BUILD_NUMBER = 100
# WORKSPACE = "/home/extraspace/home/mtz/png"
# ARTIUSER = "admin"
# ARTIPASS = "K_29^ob"




# SERVICE = SERVICE.lower()




if SERVICE is None or SVNUSER is None or SVNPASS is None or BUILD_NUMBER is None or WORKSPACE is None or ARTIPASS is None or ARTIUSER is None:
	raise Exception("Initial variable is not set up")

if SERVICE == "" or SVNUSER == "" or SVNPASS == "" or BUILD_NUMBER == "" or WORKSPACE == "" or ARTIPASS == "" or ARTIUSER == "":
	raise Exception("Initial variable is set up incorrectly")	



def loadConfigSettings(filename):
	config = open(filename, "r")
	output = {}
	reader = csv.DictReader(config)
	for line in reader:
		# print line
		output[line["environment"]] = line

	config.close()
	return output


def generateConfigs(folder,service):
	configs = loadConfigSettings("config.csv")
	for entry in configs:
		config = open(os.path.join(folder, entry + "_{0}.php.config".format(service)), "w")
		for key in configs[entry]:
			config.write( "%s\t=\t%s\n" % (key, configs[entry][key]) )
		config.close()




def tarFile(source, target): 

	if source.endswith("/"):
		source = source[:-1]

	parent = os.path.dirname(source) 

	os.chdir(parent)
	cmd = "/bin/tar -czf {0} {1}".format(target,  os.path.basename(source) )
	print "[INFO] Executing: ", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	output = proc.communicate()[0]

	print "[INFO] Output: ", output	


def JIRA_add_comment(url, key, username, password, comment):

	_comment = {}
	_comment['add'] = {}
	_comment['add']['body'] = comment.replace("'", "&quot;")


	_json = {}
	_json['update'] = {}
	_json['update']['comment'] = [_comment]

	command  = "curl -D- -u " + username + ":" + password +"  -X  PUT -d " + "'" + str(json.dumps(_json)) + "' -H \"Content-Type: application/json\" " + url + "/rest/api/2/issue/" + key
	print command
	sb_command = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
	print sb_command.communicate()[0]



def uploadArtifactory(source, target, username, password, artifactory):
	output = ""

	artifactory_server = "http://10.33.20.7:8080/artifactory/simple/" + artifactory + "/"
	preHash = open(source, "rb").read()
	hash_md5 = hashlib.md5(preHash).hexdigest()
	hash_sha1 = hashlib.sha1(preHash).hexdigest()

	if target[-1] != "/":
		target += "/"



	# target = target.replace("trunk.tar", target.split("/")[-2])
	RC = target.split("/")[-2]
	bundle = os.path.join(target, os.path.basename(source).replace("trunk.tar.gz", RC + ".tar.gz"))

	# os.path.join(target, os.path.basename(source))

	command_curl_upload = "curl -D- -X PUT -u {0}:{1}  {2} -T {3} -H 'X-Checksum-Md5: {4}' -H 'X-Checksum-Sha1: {5}'".format(username, 
					password, 
					bundle, 
					os.path.basename(source), 
					hash_md5, 
					hash_sha1)
	msg = "[INFO] Executing: " + command_curl_upload
	print msg
	output += msg + "\n"
	curl_upload = sb.Popen(shlex.split(command_curl_upload), stdout=sb.PIPE)
	data_curl_upload = curl_upload.stdout.read()
	msg = "[INFO] Output: " + data_curl_upload
	print msg
	output += msg + "\n"


	if data_curl_upload.find("201 Created") == -1:
		msg = "[ERROR] File has not been uploaded to artifactory properly: " + data_curl_upload

		if JIRAKEY != None and JIRAKEY != "":
			JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment="{color:red}" + msg + "{color}" )

		raise Exception(msg)
	else:
		msg = "[INFO] " + data_curl_upload
		print msg
		output += msg + "\n"

		if JIRAKEY != None and JIRAKEY != "":
			comment = "The package is now available here: " + bundle
			JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment=comment )

		return output.lower(), bundle 

	# mail.write(msg)


## download settings from autodeployment ###
# cmd = "svn export --username={0} --password={1} --non-interactive --force  http://10.33.20.5:8080/svn/{4}/{2}/autodeployment/config.csv {3}".format(SVNUSER, SVNPASS, SERVICE, os.path.join(WORKSPACE, "config.csv"), SVNREPOSITORY)
# print "[INFO] Executing: ", cmd
# proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
# output = proc.communicate()[0]
# print "[INFO] output: ", output

#######################


# try:

# 	settings = Settings()
# 	settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
# 	settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# 	conf = settings.getSettings()
# 	print "### Testing settings feature", conf[SERVICE]["SVNName"], "###"
# 	SERVICE = conf[SERVICE]["SVNName"]

# except:
# 	e = sys.exc_info()[0]
# 	print e
# 	sys.exit(-1)


target = os.path.join(WORKSPACE, SERVICE)
source = "http://10.33.20.5:8080/svn/{1}/{0}/trunk".format(SERVICE, SVNREPOSITORY)

branch = BRANCH
if BRANCH == None or BRANCH == "":
	branch = None


if branch is not None:
	rc = "http://10.33.20.7:8080/artifactory/{0}/trunk_{1}".format(artifactory, branch)	
else:
	rc = "http://10.33.20.7:8080/artifactory/{0}/trunk".format(artifactory)





# revision = downloadSVN(username=SVNUSER, 
# 			password=SVNPASS, 
# 			source=source,
# 			target=target,
# 			branch=branch)

revision = os.getenv("REVISION", None)

if revision is not None and int(revision) > 0:
	#generateConfigs( os.path.join(WORKSPACE, SERVICE, "_private/conf"), SERVICE )
	name = "PnG_{0}_REV_{1}_BUILD_{2}_trunk.tar.gz".format(SERVICE, revision, BUILD_NUMBER)
	bundle = os.path.join(WORKSPACE, name)
	tarFile(source=target, target=bundle)
	os.system("ls -l")
	uploadArtifactory(username=ARTIUSER, password=ARTIPASS, source=bundle, target=rc, artifactory=artifactory)


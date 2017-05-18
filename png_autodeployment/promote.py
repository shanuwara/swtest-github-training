#!python2.7 -u

import os
import sys
import subprocess as sb
import shlex
import hashlib
import re
import json
import csv

# global ARTIUSER, ARTIPASS, repository

global JIRAKEY

ARTIUSER = os.getenv("ARTIUSER", None)
ARTIPASS = os.getenv("ARTIPASS", None)
ARTISOURCE = os.getenv("ARTISOURCE", None)
SERVICE = os.getenv("SERVICE", None)
RELEASECANDIDATE = os.getenv("RELEASECANDIDATE", None)
WORKSPACE = os.getenv("WORKSPACE", None)
JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
SVNUSER = os.getenv("SVNUSER", None)
SVNPASS = os.getenv("SVNPASS", None)
BRANCH = os.getenv("BRANCH", None)
repository = "PandG"
artifactory = "PnG"
project = "PnG"

# ARTIUSER = "admin"
# ARTIPASS = "K_29^ob"
# ARTISOURCE = "trunk"
# SERVICE = "Fairgaming"



# RELEASE-0_trunk_MARS-0

# RELEASECANDIDATE + "_trunk_" + BRANCHNAME


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



if ARTIUSER is None or ARTIPASS is None or ARTISOURCE is None or SERVICE is None or RELEASECANDIDATE is None or WORKSPACE is None or JIRAKEY is None:
	raise Exception("One of initial variable is not set up")


if ARTIUSER == "" or ARTIPASS == "" or ARTISOURCE == "" or SERVICE == "" or RELEASECANDIDATE == "" or WORKSPACE == "" or JIRAKEY == "":
	raise Exception("One of initial variable is set up incorrectly")




def JIRA_add_comment(url, key, username, password, comment):
	_comment = {}
	_comment['add'] = {}
	_comment['add']['body'] = comment


	_json = {}
	_json['update'] = {}
	_json['update']['comment'] = [_comment]

	command  = "curl -s -D- -u " + username + ":" + password +"  -X  PUT -d " + "'" + str(json.dumps(_json)) + "' -H \"Content-Type: application/json\" " + url + "/rest/api/2/issue/" + key
	print command
	sb_command = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
	print sb_command.communicate()[0]




def getListFiles(source, username, password, _exception = True ):
	# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
	# global ARTIUSER, ARTIPASS, artifactory_server
	# command_curl_get_list = "curl -D- -X GET -u " + username + ":" + password + " " + artifactory_server + _folder + "/" 


	if source[-1] != "/":
		source = source + "/"

	command_curl_get_list = "curl -s -D- -X GET -u {0}:{1} {2}".format(username, password, source)

	print command_curl_get_list
	curl_get_list = sb.Popen(shlex.split(command_curl_get_list), stdout=sb.PIPE)
	data_curl_get_list = curl_get_list.communicate()[0]
	# print data_curl_get_list
	# data_curl_get_list = curl_get_list.stdout.read()
	p = re.compile(ur'({.*})', re.DOTALL)
	group = re.search(p, data_curl_get_list)
	# print group.groups()
	if group is not None:
		files = []
		# print group.groups()[0]
		# print group.groups()
		data_json = json.loads(group.groups()[0])
		if "children" in data_json:
		  return data_json['children']
		else:
		  msg = "[ERROR] Artifactory " + _folder + " is empty or service not found"
		  raise Exception(msg)
		  # print msg
		  # mail.write(msg)
		  if _exception == False:
		    msg = "[INFO] Folder " + _folder + " allowed to be empty\n"
		    print msg
		    # mail.write(msg)
		    # mail.flush()
		  else:
		    raise Exception("Source Artifactory folder is empty")


def getLatestFile(_list, _service):
	files = []
	for f in _list:
		group = re.search(ur'^PnG_('+ _service + ').*tar.gz$', str(f['uri'][1:]))
		if group is not None and len(group.groups()) > 0 and group.groups()[0] == _service:
			# print group.groups()
			print "group is not none"
			files.append(str(f['uri'][1:]))

	# files = sorted(files)
	# files.sort(key=str.lower)

	files.sort(key=lambda x: (int(x.split("_")[3]), int(x.split("_")[5]) ) )
	print files
	# print files[-1][1:]
	if len(files) > 0:
		return files[-1]
	else:
		return None



def zipFile(_filein, _fileout):
	command_zip_file = "zip -r " + _fileout + " " + _filein
	zip_file = sb.Popen(shlex.split(command_zip_file), stdout=sb.PIPE)
	data_zip_file = zip_file.stdout.read()
	msg = "[INFO] " + data_zip_file
	print msg
	mail.write(msg)


def downloadArtifactory(source, target, username, password):

	"""
		source - artifactory link
		target - destination on hdd (zipfile)

	"""

	# command_curl_download = "curl -X GET -u " + ARTIUSER + ":" + ARTIPASS + " " + artifactory_server + ARTISOURCE + "/" + _file + " -o " + _file
	command_curl_download = "curl -s -X GET -u {0}:{1} {2} -o {3}".format(username, password, source, target)
	print "[INFO] Executing: ", command_curl_download
	curl_download = sb.Popen(shlex.split(command_curl_download), stdout=sb.PIPE)
	data_curl_download = curl_download.communicate()[0]
	print "[INFO] Output: ", data_curl_download




def uploadArtifactory(source, target, username, password, artifactory):
	output = ""
	# curl -D- -X PUT -u jghj http://10.33.20.7:8080/artifactory/simple/CQM/trunk/
	global ARTIUSER, ARTIPASS, repository
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
		raise Exception(msg)
	else:
		msg = "[INFO] " + data_curl_upload
		print msg
		output += msg + "\n"
		return output.lower(), bundle 

	# mail.write(msg)



def promote(source, target, RC ,username, password, artifactory, service ):
  
	"""
		source - artifactory link
		target - destination on hdd (zipfile)

	"""

	if RC[-1] != "/":
		RC = RC + "/"

	downloadArtifactory(source=source, target=target, username=username, password=password)


	os.system("ls -lah")
	# cmd = "zipinfo -1 " + target
	cmd = "tar -tzf {0}".format(target)
	print "[INFO] Executing: ", cmd

	sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	data = sb_cmd.communicate()[0]

	print "[INFO] Output: ",data

	output, bundle = uploadArtifactory(username=username, 
						password=password,
						source=target,
						target=RC,
						artifactory=artifactory
						)



	comment = "The service {color:red}" + service + "{color} has been promoted successfully and is available here: " + bundle
	JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment=comment )




try:

	settings = Settings()
	settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
	settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	conf = settings.getSettings()
	print "### Testing settings feature", conf[SERVICE]["SVNName"], "###"
	SERVICE = conf[SERVICE]["SVNName"]


	if BRANCH is None or BRANCH == "":

		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, "trunk"), username=ARTIUSER, password=ARTIPASS)
		latest = getLatestFile(list, SERVICE)
		rc = "http://10.33.20.7:8080/artifactory/{0}/{1}".format(artifactory, RELEASECANDIDATE)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory, "trunk", latest)
	else:
		# RELEASECANDIDATE + "_trunk_" + BRANCHNAME
		list = getListFiles(source="http://10.33.20.7:8080/artifactory/api/storage/{0}/{1}/".format(artifactory, "trunk_" + BRANCH), username=ARTIUSER, password=ARTIPASS)
		latest = getLatestFile(list, SERVICE)
		rc = "http://10.33.20.7:8080/artifactory/{0}/{1}".format(artifactory, RELEASECANDIDATE + "_trunk_" + BRANCH)
		source = "http://10.33.20.7:8080/artifactory/{0}/{1}/{2}".format(artifactory, "trunk_" + BRANCH, latest)
		

	target = os.path.join(WORKSPACE, latest)

	promote(username=ARTIUSER, 
			password=ARTIPASS, 
			source=source,
			target=target,
			RC=rc,
			artifactory=artifactory,
			service=SERVICE)

except:
	e = sys.exc_info()[0]
	print e

	print sys.exc_info()

	comment = "{color:red}Promotion has failed{color}"
	JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment=comment )
	sys.exit(-1)

#!python2.7 -u


import os, sys
sys.path.append(os.getcwd())
import csv
import shlex
import subprocess as sb
import re
import json
import shutil



# sys.path.append(os.path.join(WORKSPACE, "cqm"))
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


JIRASERVER = os.getenv("JIRASERVER", None)
JIRAKEY = os.getenv("JIRAKEY", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
RC = os.getenv("RC", None)
REPOSITORY = "http://10.33.20.5:8080/svn/PandG/"
BRANCH = os.getenv("BRANCH", None)

if BRANCH == "" or BRANCH == "trunk":
	BRANCH = None



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


###  ####







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

###############################3



def downloadSVN(username, password, source, target, branch = None):
	print "[FUNC]", sys._getframe().f_code.co_name

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
		# JIRA_add_comment(username=JIRAUSER, password=JIRAPASS, url="http://10.33.20.21:8080/jira", key=JIRAKEY,  comment=comment )
		# comment = comment.replace("\"", "&quot;")
		# comment = comment.replace("'", "&quot;")
		# jiraManager.addComment(jiraKey=JIRAKEY, comment=comment)
		
		raise Exception("downloadSVN: " + output)
	else:
		print "[INFO] Output: ", output	
		p = re.compile(ur'Exported revision ([0-9]*)', re.DOTALL)
		group = re.search(p, output)
		if group is not None:
			return group.groups()[0]


def build(folder):
	print "[FUNC]", sys._getframe().f_code.co_name
	os.chdir(folder)
	# cmd = "ls -lah" ## unit test
	cmd = "pear package package.xml"
	print "[INFO] Executing: ", cmd
	stdout = None
	stderr = None
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	stdout, stderr = proc.communicate()


	packageName = None
	ppp = "ttt"
	if stdout is not None:
		groups = re.findall(ur'Package (.*) done', stdout, re.DOTALL)
		if groups is not None and len(groups) > 0:
			packageName = groups[0]


	# return stdout, stderr, packageName
	return stdout, stderr, packageName

	
	





JIRA = jira(server=JIRASERVER, userName=JIRAUSER, password=JIRAPASS)
ARTEFACTORY = artefactory(server="http://10.33.20.7:8080", userName=ARTIUSER, password=ARTIPASS)

settings = Settings()
settings.setFileName("http://10.33.20.5:8080/svn/PandG/autodeployment/vhosts.csv")
settings.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
conf = settings.getSettings()

SVNName = str(conf[SERVICE]['SVNName'])
SVNUrl = os.path.join(REPOSITORY, SVNName, RC)
target = os.path.join(WORKSPACE, SVNName)

try:
	stdout = stderr = packageName = None
	REVISION = downloadSVN(username=SVNUSER, password=SVNPASS, source=SVNUrl, target=target, branch = BRANCH)

	if REVISION is not None and int(REVISION) > 0:
		folder = os.path.join(WORKSPACE, SVNName)
		stdout, stderr, packageName = build(folder=folder)

		print stdout, stderr, packageName
		print "#"+packageName+"#"
		# packageName = "LBRGames-1.5.3.tgz"
		if packageName is not None:
			pass
			# print ARTEFACTORY.search(repository="PnG", folder="trunk", searchName="LBRGames")
			if BRANCH == None:
				folder = "trunk"
			else:
				folder = "trunk_" + BRANCH
			ARTEFACTORY.upload(repository="PnG", folder=folder, file=os.path.join(target, packageName))
			if JIRAKEY is not None and JIRAKEY != "":
				comment = "Package has been built succesfully"
				JIRA.addComment(jiraKey=JIRAKEY, comment=comment)


except Exception as e1: 
	print e1

	if JIRAKEY is not None and JIRAKEY != "":
		comment = "{color:red}Unexpected error{color}: " + str(e1) + "\n" + str(stdout) +"\n" + str(stderr)
		# comment = "" + comment
		comment = comment.replace("'", "&quot;")
		comment = comment.replace("\"", "&quot;")
		JIRA.addComment(jiraKey=JIRAKEY, comment=comment)

	raise Exception("Build failed")





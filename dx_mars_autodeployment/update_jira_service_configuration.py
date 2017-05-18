#!python2.7 -u

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
import csv

## loads libs, unit test or jenkins
if (os.path.exists("../custom_field_editor")):
	sys.path.append(os.path.join("../custom_field_editor"))
else:
	sys.path.append(os.path.join("custom_field_editor"))
from CustomFieldEditor import CustomFieldManager

if (os.path.exists("../cqm_libs")):
	sys.path.append(os.path.join("../cqm_libs"))
else:
	sys.path.append(os.path.join("cqm"))
from artefactory import artefactory
from jira import jira


# if (os.path.exists("../custom_field_editor")):
# 	print "importing cfm"
# 	sys.path.append(os.path.join("../custom_field_editor"))
# else:
# 	sys.path.append(os.path.join("custom_field_editor"))
# from CustomFieldEditor import CustomFieldManager



global JIRAKEY
global BRANCH
global REPOSITORY_BW
global SVNUSER
global SVNPASS
global WORKSPACE



class DTL:
	def __init__(self, filename, source, directory):
		self.source = source
		self.directory = directory
		self.file = os.path.join(self.directory, filename)

class Build:
	def __init__(self, workspace, service, repository, dtl, target, branch):
		self.__WORKSPACE = workspace
		self.__SERVICE = service
		self.__REPOSITORY = repository
		self.__DTLFile = dtl.file
		self.__DTLDir = dtl.directory
		self.__DTLSource = dtl.source

		self.__SVNUSER = None
		self.__SVNPASS = None

		self.__PROJECT = "DX"

		self.__BUILDNUMBER = 0

		self.__TibcoDir59 = "/opt/tibco/tra/5.9/bin/"
		self.__TibcoDir57 = "/opt/tibco/tra/5.7/bin/"

		self.__TibcoBuildEar57 = "/opt/tibco/tra/5.7/bin/buildear"
		self.__TibcoBuildEar59 = "/opt/tibco/tra/5.9/bin/buildear"

		self.__TibcoDir = None
		self.__TibcoBuildEar = None

		self.__BuildFolder = target
		print self.cleanBuildFolder()


		if (os.path.join(self.__WORKSPACE, "") == os.path.join(self.__DTLDir, "")):
			raise ValueError("Libraries must not be placed in WORKSPACE")

		self.__BRANCH = branch

		self.TYPE_ALL = 1
		self.TYPE_SINGLE = 0

	def setBuildNumber(self, number):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__BUILDNUMBER = number

	def cleanBuildFolder(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "rm -rf {0}".format(self.__BuildFolder)
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()

		return output


	def setSubversionCredentials(self, username, password):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__SVNUSER = username
		self.__SVNPASS = password

	def exportSVN(self, _url, _target):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "svn export --force --non-interactive --username={0} --password={1} {2} {3}".format(self.__SVNUSER, self.__SVNPASS, _url, _target)
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()

		return output

	def build(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		os.environ['DISPLAY'] = "localhost:1.0" ## tweaking xserver
		os.chdir(self.getTibcoDir())
		cmd = "./buildear -s -x -a {0} -ear /Build/{1}.archive -p {2} -o {3}".format(self.__DTLFile, self.__SERVICE, os.path.join(self.__BuildFolder, "code"), os.path.join(self.__BuildFolder, self.__SERVICE + ".ear"))
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()
		os.chdir(self.__WORKSPACE)

		return output


	def getTibcoDir(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__TibcoDir = self.__TibcoDir57
		folder = os.path.join(self.__BuildFolder, "cfg")
		if not os.path.exists(folder):
			return None

		_list = os.walk(folder).next()[2]
		if len(_list) > 0:
			_list = _list[0]
			if _list.find(".cfg") != -1:
				print _list
				for line in open(os.path.join(folder,_list)):
					if "binding[1]/product/version=5.12" in line:
						self.__TibcoDir = self.__TibcoDir59
						
		return self.__TibcoDir

	def getRevision(self):
		print "[FUNC]", sys._getframe().f_code.co_name

		cmd = "svn info --non-interactive --username={0} --password={1} {2}".format(self.__SVNUSER, self.__SVNPASS, self.__REPOSITORY)
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()

		tmp = output[0].split()
		pos = tmp.index("Revision:") + 1

		return tmp[pos]


	def execute(self, _type):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.getDTL()

		services = self.getServiceList()
		self.__REVISION = self.getRevision()

		### unit test
		# del services['SportsbookEvent_MARS10']
		##
		print services

		buildErrors = {}

		if _type == self.TYPE_SINGLE:
			url = services[self.__SERVICE]
			
			configUrl = url.replace("Code/Bw", "Build/Bw")
			print configUrl
			
			if self.__BRANCH != "trunk":
				configUrl = os.path.join(self.__REPOSITORY, "branch", self.__BRANCH, configUrl)
			else:
				configUrl = os.path.join(self.__REPOSITORY, self.__BRANCH, configUrl)

			
			codeUrl = configUrl.replace("Build/Bw", "Code/Bw")
			
			print self.getConfigs(url = configUrl)
			print "[INFO] tibco_dir=", self.getTibcoDir()
			if self.getTibcoDir() == None:
				raise ValueError("No config files found for service " + self.__SERVICE)


			print "[INFO] codeUrl=",codeUrl
			print "[INFO] configUrl=",configUrl

			self.getCode(codeUrl)
			out, err = self.build()

			print out
			if out.lower().find("error") == -1 and out.lower().find("fail") == -1 and out.lower().find("exception") == -1:
				return True

		elif _type == self.TYPE_ALL:

			
			for service, url in services.items():
				buildErrors[service] = ""
				self.__SERVICE = service

				print "service=", service
				print "url=", url
				self.cleanBuildFolder()
			
				configUrl = url.replace("Code/Bw", "Build/Bw")
				print configUrl
				
				if self.__BRANCH != "trunk":
					configUrl = os.path.join(self.__REPOSITORY, "branch", self.__BRANCH, configUrl)
				else:
					configUrl = os.path.join(self.__REPOSITORY, self.__BRANCH, configUrl)

				
				codeUrl = configUrl.replace("Build/Bw", "Code/Bw")

				print self.getConfigs(url = configUrl)
				print "[INFO] tibco_dir=", self.getTibcoDir()

				if self.getTibcoDir() == None:
					out = "[ERROR] No config files found for service " + service
					buildErrors[service] = out
					continue

				print "[INFO] codeUrl=",codeUrl
				print "[INFO] configUrl=",configUrl

				self.getCode(codeUrl)
				out, err = self.build()

				print out

				if out.lower().find("error") != -1 or out.lower().find("fail") != -1 or out.lower().find("exception") != -1:
					buildErrors[service] = out
				else:
					_filein = os.path.join(self.__BuildFolder, service + ".ear") + " " + os.path.join(self.__BuildFolder, "cfg")
					_fileout = os.path.join(self.__WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(self.__REVISION, self.__BUILDNUMBER, self.__BRANCH) + ".zip")
					self.zipFile(_filein=_filein, _fileout=_fileout)

			return buildErrors


		return False




	def cleanDTL(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "rm -rf {0}".format(self.__DTLDir)
		print "[EXECUTING]", cmd
		sb_delete_old_libs = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		return sb_delete_old_libs.communicate()



	def getDTL(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		print self.cleanDTL()
		print self.exportSVN(self.__DTLSource, self.__DTLDir)


		libs = []
		print "### libs=[] ###"
		for root, dirnames, filenames in os.walk(self.__DTLDir):
		    for filename in fnmatch.filter(filenames, '*.projlib'):
		        libs.append(os.path.join(root, filename))

		properties = open(self.__DTLFile, "w")
		for lib in libs:
			line = "tibco.alias.{0}={1}\n".format(os.path.basename(lib) ,os.path.join(self.__DTLDir, lib))
			print "[INFO] DTL=" + line
			properties.write( line )

		properties.close()


	def getConfigs(self, url):
		print "[FUNC]", sys._getframe().f_code.co_name
		return self.exportSVN(_url=url, _target=self.__BuildFolder)

	def getCode(self, url):
		return self.exportSVN(_url=url, _target= os.path.join(self.__BuildFolder, "code"))		


	def getServiceList(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		url = os.path.join(self.__REPOSITORY, "trunk" )
		print url
		if self.__BRANCH != "trunk":
			url = os.path.join(self.__REPOSITORY, "branch", self.__BRANCH)

		command_svn_list = "svn --non-interactive --username=\"{0}\" --password=\"{1}\"  list {2}  -R ".format(self.__SVNUSER, self.__SVNPASS, url)
		print command_svn_list
		sb1 = sb.Popen(shlex.split(command_svn_list), stdout=sb.PIPE)
		data_in = sb1.stdout.read()
		# sb2 = sb.Popen(shlex.split("egrep \"/$\""), stdout=sb.PIPE, stdin=sb.PIPE)
		sb2 = sb.Popen(shlex.split("egrep \"[a-zA-Z_0-9]*/[0-9].[0-9]/[a-zA-Z_0-9]*/$\""), stdout=sb.PIPE, stdin=sb.PIPE)
		data_out = sb2.communicate(input=data_in)[0]

		services = data_out

		if services != "":
			services = services.split("\n")
			services = filter(None, services)
		else: 
			return None


		listServices = {}

		for service in services:
			tmp = service.split("/")
			tmp = filter(None, tmp)

			# print tmp

			left = tmp[-3] + tmp[-2].replace(".", "")
			right = tmp[-1]

			# print left
			if left.lower() == right.lower():
				listServices[right] = service

		return listServices

	def zipFile(self, _filein, _fileout):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "zip -r " + _fileout + " " + _filein
		print "[EXECUTING]", cmd
		zip_file = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data_zip_file = zip_file.stdout.read()
		print "[INFO] " + data_zip_file



class CustomFieldManagerExt (CustomFieldManager):
	def __init__(self):
		CustomFieldManager.__init__(self)
		self.__configFileName = None

		self.__CONFusername = None
		self.__CONFpassword = None

		self.__SUBVERSIONusername = None
		self.__SUBVERSIONpassword = None



	def setSubversionCredentials(self, username, password):
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password



	def setConfigFileName(self, filename):
		self.__configFileName = filename

	def getConfiguration(self):

		cmd = "curl -u {0}:{1} -X GET \"{2}\"".format(self.__SUBVERSIONusername, self.__SUBVERSIONpassword, self.__configFileName)
		print "[INFO] Executing:", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		(data, error) = proc.communicate()
		# print output, error


		data = data.split("\n")
		output = {}
		# reader = csv.DictReader(data) # in case of csv with headers
		reader = csv.reader(data)
		for line in reader:
			if len(line) == 0:
				continue
			print line, "test"
			output[line[0]] = line[1:]

		return output



def addEntries(groupname, entries):
	group = cfm.getGroup(groupname)

	if group is None:
		group = cfm.addGroup(groupname)


	if group is not None:
		print cfm.enableGroup(group["id"])
		for entry in entries:
			child = cfm.getChild(group["id"], entry)
			if child is None:
				print cfm.addChild(group["id"], entry)
			else:
				print cfm.enableChild(group["id"], child["id"])



def cleanUp(cfm):

	groups = cfm.getGroups()
	print groups[0]
	for group in groups:

		cfm.disableGroup(group["id"])
		children = cfm.getChildren(group["id"])
		for child in children:
			print cfm.disableChild(group["id"], child["id"])



## settings
ARTISERVER = "http://10.33.20.7:8080"
ARTIUSER = os.getenv("ARTIUSER", "")
ARTIPASS = os.getenv("ARTIPASS", "")
AUTOMATIC = os.getenv("AUTOMATIC", "")
BUILDNUMBER = os.getenv("BUILD_NUMBER", "")
REVISION = 0

WORKSPACE = os.getenv("WORKSPACE", "")

SVNUSER = os.getenv("SVNUSER", "")
SVNPASS = os.getenv("SVNPASS", "")

JIRAKEY = os.getenv("JIRAKEY", "")
JIRAUSER = os.getenv("JIRAUSER", "")
JIRAPASS = os.getenv("JIRAPASS", "")
JIRASERVER = "http://10.33.20.21:8080/jira"

repository = "http://10.33.20.5:8080/svn/DX/DX"
artifactory = "http://10.33.20.7:8080/artifactory/simple/DX-MARS/"
branch = os.getenv("BRANCH", "")
target = os.path.join(WORKSPACE, "tmp")

service = os.getenv("FORCE_SERVICE", "")
# bundle = os.path.join(WORKSPACE, service + ".zip")



###


## library package
libs = DTL
libs.directory = os.path.join(WORKSPACE, "libs")
libs.file = os.path.join(WORKSPACE, "file.properties")
if branch != "trunk":
	libs.source = os.path.join(repository, "branch" , branch, "Development/Code/Bw/Shared")
else:
	libs.source = os.path.join(repository, "trunk", "Development/Code/Bw/Shared")
###



## unit test
if os.getenv("WORKSPACE", "") == "":
	SVNUSER = "cqmsvn"
	SVNPASS = "K_29^ob"
	WORKSPACE = "/home/extraspace/home/mtz/DX"
	ARTIUSER = "admin"
	ARTIPASS = "K_29^ob"
	JIRAUSER = "CQMJIRA"
	JIRAPASS = "CQMJIRA"
	JIRAKEY = "DXMT-8"
	AUTOMATIC = "YES"



# data = list(['SportsbookEvent_MARS', 'RetailSportsbookPublisher11'])
# print data

# service = 'RetailSportsbookPublisher11'
###


build = Build(workspace = WORKSPACE, service="*all", repository=repository, dtl=libs, target=target, branch="trunk")
build.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# build.setBuildNumber(BUILDNUMBER)
# REVISION = build.getRevision()
availableServices = build.getServiceList()
build = None

print availableServices




cfm = CustomFieldManagerExt()
cfm.setJIRAServer("http://10.33.20.21:8080/jira")
cfm.setJIRACredentials(username=JIRAUSER, password=JIRAPASS)
cfm.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
cfm.setCustomField(12901, "default")
cfm.setConfigFileName(filename="http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_service_configuration.csv")
newEntries = cfm.getConfiguration()



newEntries["trunk"] = []
for service in availableServices:
	newEntries["trunk"].append(service)


dictlist = []
for key, value in newEntries.iteritems():
    temp = [key] + value
    dictlist.append(temp)
    print temp

print dictlist




with open("jira_service_configuration.csv", "w") as config:
	writer = csv.writer(config, delimiter=',')
	for item in dictlist:
		writer.writerow(item)


def updateConfiguration():
	cmd = "svn --non-interactive --username={0} --password={1} remove  http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_service_configuration.csv -m '[~] removing jira service configuration' ".format(SVNUSER, SVNPASS)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	print proc.communicate()

	cmd = "svn --force --non-interactive --username={0} --password={1} import  jira_service_configuration.csv http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_service_configuration.csv -m '[~] updating jira service configuration' ".format(SVNUSER, SVNPASS)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	print proc.communicate()


updateConfiguration()

# cleanUp(cfm)


# for newEntry in newEntries:
# 	groupname = newEntry
# 	entries = newEntries[newEntry]

# 	addEntries(groupname, entries)

# cfm.sortGroups()

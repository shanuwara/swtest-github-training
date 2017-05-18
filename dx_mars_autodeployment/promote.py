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
import ntpath
import csv


def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "" or value == "None":
			value = None
		globals()[element] = value

elements = ("ARTIUSER", "ARTIPASS", "AUTOMATIC", "BUILD_NUMBER", "RC", "COUCHBASE_SCRIPTS", "EMS_SCRIPTS", "WORKSPACE", "SVNUSER",
			"SVNPASS", "JIRAKEY", "JIRAUSER", "JIRAPASS", "ENVIRONMENT", "SERVICE", "BRANCH",)


setGlobals(elements)

## settings
ARTISERVER = "http://10.33.20.7:8080"
BUILDNUMBER = BUILD_NUMBER
REVISION = 0


JIRASERVER = "http://10.33.20.21:8080/jira"
repository = "http://10.33.20.5:8080/svn/DX/DX"
artifactory = "http://10.33.20.7:8080/artifactory/simple/DX-MARS/"
branch = BRANCH
target = os.path.join(WORKSPACE, "tmp")

service = SERVICE
# bundle = os.path.join(WORKSPACE, service + ".zip")
EXTENSION = "zip"



###


sys.path.append(os.path.join(WORKSPACE, "cqm_libs"))	
sys.path.append(os.path.join(WORKSPACE, "custom_field_editor"))

from artefactory import artefactory
from jira import jira
from CustomFieldEditor import CustomFieldManager


class Promote:

	def __init__(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name

		self.__WORKSPACE = kwargs.pop('workspace', None)
		self.__SERVICE = kwargs.pop('service', None)
		self.__REPOSITORY = kwargs.pop('repository', None)
		self.__BRANCH = kwargs.pop('branch', None)
		self.__EXTENSION = kwargs.pop('extension', None)
		self.__BRANCH = "trunk" if self.__BRANCH is None or self.__BRANCH == "" else self.__BRANCH


		self.__SVNUSER = None
		self.__SVNPASS = None

		self.__ENVIRONMENT = kwargs.pop('environment', None)

		self.__ARTIUSER = None
		self.__ARTIPASS = None
		self.__ARTISERVER = None
		self.__artiManager = None
		self.__artiRepository = "DX-MARS"

		self.__PROJECT = "DX"

		self.__BUILDNUMBER = 0

		self.__RC = kwargs.pop('release', None)

		self.__COUCHBASE_URL = None
		self.__COUCHBASE_SCRIPT = None
		self.__EMS_URL = None
		self.__EMS_SCRIPT = None

		if self.__RC == self.__BRANCH:
			raise ValueError("Branch must be different from RC")



	def setSubversionCredentials(self, username, password):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__SVNUSER = username
		self.__SVNPASS = password

	def setArtefactoryCredentials(self, username, password, server):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__ARTIUSER = username
		self.__ARTIPASS = password
		self.__ARTISERVER = server

		self.__artiManager = artefactory(userName=self.__ARTIUSER, password=self.__ARTIPASS, server=self.__ARTISERVER)

	def setCouchBaseScript(self, script):
		print "[FUNC]", sys._getframe().f_code.co_name
		if script is None or script == "":
			return False
		self.__COUCHBASE_SCRIPT = script
		self.__COUCHBASE_URL = os.path.join(self.__REPOSITORY, "trunk/Development/Build/Couchbase",self.__COUCHBASE_SCRIPT)
		return True



	def setEmsScript(self, script):
		print "[FUNC]", sys._getframe().f_code.co_name
		if script is None or script == "":
			return False
		self.__EMS_SCRIPT = script
		self.__EMS_URL = os.path.join(self.__REPOSITORY, "trunk/Development/Build/Ems",self.__EMS_SCRIPT)
		return True


	def getServiceList(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		url = os.path.join(self.__REPOSITORY, "trunk" )
		
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

	def getRevision(self, url, branch = None):
		print "[FUNC]", sys._getframe().f_code.co_name

		cmd = "svn info --non-interactive --username={0} --password={1} {2}".format(self.__SVNUSER, self.__SVNPASS, url)
		try:
			print "[EXECUTING]", cmd
			proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
			output = proc.communicate()

			tmp = output[0].split()
			pos = tmp.index("Revision:") + 1
			return tmp[pos]
		except Exception as e:
			pass

		return 0

	def createBranch(self, url):
		print "[FUNC]", sys._getframe().f_code.co_name
		
		cmd = "svn --username={0} --password={1} mkdir {2}  --parents --non-interactive -m \"creating folder for branch\"".format(self.__SVNUSER, self.__SVNPASS, url)
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		data = proc.communicate()


		
		return data

	def getPackage(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		pattern=re.compile('(.*)_Rev_([0-9]*)_Build_([0-9]*)_(.*)(\..*)',re.IGNORECASE)
		key = lambda x:(int(pattern.match(x).groups()[1]),int(pattern.match(x).groups()[2]))
		sortPattern = {"key": key, "reverse":True}

		searchName = "{0}_REV_*_BUILD_*_trunk.zip".format(self.__SERVICE)

		manager = self.__artiManager
		packages = manager.advancedSearch(repository=self.__artiRepository, folder="trunk", searchName=searchName, sortPattern=sortPattern)
		print packages
		if len(packages) > 0:
			package = packages[0]

		if package is not None and package != "":
			destName = os.path.join(self.__WORKSPACE, package)
			manager.download(repository=self.__artiRepository,srcFolder="trunk",fileName=package,destName=destName, debug=True)
			newPackage = package.replace("_trunk.zip", "_{0}.zip".format(self.__RC))
			os.rename(os.path.join(self.__WORKSPACE, package), os.path.join(self.__WORKSPACE, newPackage))
			return newPackage

		return None

	def getPackage2(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		searchName = "{0}_REV_*_BUILD_*_{1}.zip".format(self.__SERVICE, self.__BRANCH)
		manager = self.__artiManager
		packages = manager.advancedSearch(repository=self.__artiRepository, folder="", searchName=searchName)
		print packages

		if len(packages) > 0 and isinstance(packages, list):
			package = packages[-1]
		else:
			return None

		if package is not None and package != "":
			# destName = os.path.join(self.__WORKSPACE, package)
			newPackage = package.replace("_{0}.zip".format(self.__BRANCH), "_{0}_{1}.zip".format(self.__BRANCH, self.__RC))
			manager.download(repository=self.__artiRepository,srcFolder=self.__BRANCH, fileName=package, destName=newPackage, debug=True)
			return newPackage
		return None


	def cleanRC(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		pattern=re.compile('(.*)_Rev_([0-9]*)_Build_([0-9]*)_(.*)(\..*)',re.IGNORECASE)
		key = lambda x:(int(pattern.match(x).groups()[1]),int(pattern.match(x).groups()[2]))
		sortPattern = {"key": key, "reverse":True}

		searchName = "{0}_REV_*_BUILD_*_{1}.{2}".format(self.__SERVICE, self.__RC, self.__EXTENSION)

		manager = self.__artiManager
		packages = manager.advancedSearch(repository=self.__artiRepository, folder=self.__RC, searchName=searchName, sortPattern=sortPattern)
		if packages is not None:
			print packages
			for package in packages:
				manager.delete(repository=self.__artiRepository, folder=self.__RC, fileName=package, debug=True)

	def cleanRC2(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		
		searchName = "{0}_REV_*_BUILD_*_{1}_{2}.{3}".format(self.__SERVICE, self.__BRANCH, self.__RC, self.__EXTENSION)

		manager = self.__artiManager
		packages = manager.advancedSearch(repository=self.__artiRepository, folder="", searchName=searchName)
		if packages is not None:
			print packages
			for package in packages:
				manager.delete(repository=self.__artiRepository, folder=self.__RC, fileName=package, debug=True)

	def sendPackage(self, _file):
		print "[FUNC]", sys._getframe().f_code.co_name
		manager = self.__artiManager
		manager.upload(repository=self.__artiRepository, folder=self.__RC, file=_file)
		return True


	def copyBranch(self, _from, _to):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "svn --username={0} --password={1}  copy {2}  {3} --non-interactive -m \"creating branch\"".format(self.__SVNUSER, self.__SVNPASS, _from, _to)
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		data = proc.communicate()

		return data

	def getEmsPackage(self):
		print "[FUNC]", sys._getframe().f_code.co_name

		if os.path.exists(os.path.join(self.__WORKSPACE, "Ems")):
			print "[INFO] Removing Ems folder"
			os.system("rm -rf {0}".format(os.path.join(self.__WORKSPACE, "Ems")))

		cmd = "svn export --username={0} --password={1} {2} {3} --force --non-interactive".format(self.__SVNUSER, self.__SVNPASS, self.__EMS_URL, os.path.join(self.__WORKSPACE, "Ems", self.__EMS_SCRIPT))
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		output = proc.communicate()[0]
		proc.wait()

		cmd = "tar -cvf {0} --directory={1} {2}".format(os.path.join(self.__WORKSPACE, "Ems.tar"), os.path.join(self.__WORKSPACE, "Ems"), self.__COUCHBASE_SCRIPT)
		print "[EXECUTING]", cmd
		# os.system(cmd)
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		output += "\n" + proc.communicate()[0]

		return output



	def getCouchbasePackage(self):
		print "[FUNC]", sys._getframe().f_code.co_name

		if os.path.exists(os.path.join(self.__WORKSPACE, "Couchbase")):
			print "[INFO] Removing Couchbase folder"
			os.system("rm -rf {0}".format(os.path.join(self.__WORKSPACE, "Couchbase")))
		cmd = "svn export --username={0} --password={1} {2} {3} --force --non-interactive".format(self.__SVNUSER, self.__SVNPASS, self.__COUCHBASE_URL, os.path.join(self.__WORKSPACE, "Couchbase", self.__COUCHBASE_SCRIPT))
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		output = proc.communicate()[0]
		proc.wait()

		cmd = "tar -cvf {0} --directory={1} {2}".format(os.path.join(self.__WORKSPACE, "Couchbase.tar"), os.path.join(self.__WORKSPACE, "Couchbase"), self.__EMS_SCRIPT)
		print "[EXECUTING]", cmd
		# os.system(cmd)
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		output += "\n" + proc.communicate()[0]

		return output

	def includeEmsPackage(self, bundle):
		print "[FUNC]", sys._getframe().f_code.co_name
		os.system("zip -jg {0} {1}".format(bundle, os.path.join(self.__WORKSPACE, "Ems.tar")))

	def includeCouchbasePackage(self, bundle):
		print "[FUNC]", sys._getframe().f_code.co_name
		os.system("zip -jg {0} {1}".format(bundle, os.path.join(self.__WORKSPACE, "Couchbase.tar")))

	def execute(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		services = self.getServiceList()
		print "[INFO] services", services
		print self.__SERVICE
		print services[self.__SERVICE]

		sourceCodeUrl = os.path.join(self.__REPOSITORY, self.__BRANCH, services[self.__SERVICE])
		sourceBuildUrl = sourceCodeUrl.replace("Code/Bw", "Build/Bw")

		package = self.getPackage2()
		packagePath = os.path.join(self.__WORKSPACE, package)

		if package is None or package == "":
			raise Exception("Cannot download package")

		

		if self.__EMS_SCRIPT is not None and self.__EMS_SCRIPT != "":
			print self.getEmsPackage()
			self.includeEmsPackage( packagePath)

		if self.__COUCHBASE_SCRIPT is not None and self.__COUCHBASE_SCRIPT != "":
			print self.getCouchbasePackage()
			self.includeCouchbasePackage( packagePath)			

		self.cleanRC2()		
		self.sendPackage(_file=package)


		# trunkCodeUrl = os.path.join(self.__REPOSITORY, "trunk", services[self.__SERVICE])
		# trunkBuildUrl = trunkCodeUrl.replace("Code/Bw", "Build/Bw")

		# branchCodeUrl = os.path.join(self.__REPOSITORY, "branch", self.__RC, services[self.__SERVICE])
		# branchBuildUrl = branchCodeUrl.replace("Code/Bw", "Build/Bw")


		# ## parent folder
		# if branchCodeUrl.endswith("/"):
		# 	branchCodeUrl = os.path.dirname(branchCodeUrl)

		# if branchBuildUrl.endswith("/"):
		# 	branchBuildUrl = os.path.dirname(branchBuildUrl)

		# branchCodeUrl = os.path.dirname(branchCodeUrl)
		# branchBuildUrl = os.path.dirname(branchBuildUrl)
		# ###


		# revisionBranch = self.getRevision(url=branchCodeUrl)
		# revisionTrunk = self.getRevision(url=trunkCodeUrl)
		
		# print trunkCodeUrl
		# print trunkBuildUrl

		# print branchCodeUrl
		# print branchBuildUrl
		

		# if revisionTrunk == 0:
		# 	raise ValueError("revisionTrunk == 0")


		# package = self.getPackage()
		# packagePath = os.path.join(self.__WORKSPACE, package)
		# if package is None or package == "":
		# 	raise Exception("Cannot download package")


		# if self.__EMS_SCRIPT is not None and self.__EMS_SCRIPT != "":
		# 	print self.getEmsPackage()
		# 	self.includeEmsPackage( packagePath)

		# if self.__COUCHBASE_SCRIPT is not None and self.__COUCHBASE_SCRIPT != "":
		# 	print self.getCouchbasePackage()
		# 	self.includeCouchbasePackage( packagePath)

		# self.cleanRC()
		# self.sendPackage(_file=package)

		

		# service in branch does not exist
		# if revisionBranch == 0:
		# 	print self.createBranch(url=branchCodeUrl)
		# 	print self.createBranch(url=branchBuildUrl)

		# 	print self.copyBranch(_from=trunkCodeUrl, _to=branchCodeUrl)	
		# 	print self.copyBranch(_from=trunkBuildUrl, _to=branchBuildUrl)

		return {"package":package}

		
##########################################################

class CustomFieldManagerExt (CustomFieldManager):
	def __init__(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		CustomFieldManager.__init__(self)
		self.__configFileName = None

		self.__CONFusername = None
		self.__CONFpassword = None

		self.__SUBVERSIONusername = None
		self.__SUBVERSIONpassword = None



	def setSubversionCredentials(self, username, password):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password



	def setConfigFileName(self, filename):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__configFileName = filename

	def getConfiguration(self):
		print "[FUNC]", sys._getframe().f_code.co_name

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


################################################################
		
def updateConfiguration(folder, rc, service):
	print "[FUNC]", sys._getframe().f_code.co_name
	cfm = CustomFieldManagerExt()
	# cfm.setJIRAServer("http://10.33.20.21:8080/jira")
	# cfm.setJIRACredentials(username=JIRAUSER, password=JIRAPASS)
	cfm.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
	# cfm.setCustomField(12901, "default")
	cfm.setConfigFileName(filename="http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_rc_service_configuration.csv")
	newEntries = cfm.getConfiguration()

	print "newEntries", newEntries


	# if rc not in newEntries:
		# newEntries[branch] = []
	if rc not in newEntries:
		newEntries[rc] = []

	if service not in newEntries[rc]:
		newEntries[rc].append(service)


	dictList = []
	for key, value in newEntries.iteritems():
		temp = [key] + value
		print "temp", temp
		dictList.append(temp)
		print "temp ok"
		

	print "dictList", dictList

	with open(os.path.join(folder, "jira_rc_service_configuration.csv"), "w") as config:
		writer = csv.writer(config, delimiter=',')
		for item in dictList:
			writer.writerow(item)



	cmd = "svn --non-interactive --username={0} --password={1} remove  http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_rc_service_configuration.csv -m '[-] removing jira rc_service configuration' ".format(SVNUSER, SVNPASS)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	print proc.communicate()

	cmd = "svn --force --non-interactive --username={0} --password={1} import  jira_rc_service_configuration.csv http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_rc_service_configuration.csv -m '[+] updating jira service configuration' ".format(SVNUSER, SVNPASS)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
	print proc.communicate()



def getEnvTable(username, password, url):
	print "[FUNC]", sys._getframe().f_code.co_name
	command = "curl -s -u {0}:{1} -X GET {2}".format(username, password, url)
	print command
	cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE)
	data_cmd = cmd.communicate()[0]
	return data_cmd


def getIpAddress(_data_cmd, _ENVIRONMENT = ""):
	print "[FUNC]", sys._getframe().f_code.co_name
	data_cmd = _data_cmd

	group = re.search(_ENVIRONMENT + ur'\|([^\|]*)\|[^\|]*', data_cmd)
	
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

			return IP_ADDRESS

	return None


def copy_tibco_artifact(_Ear_Bundles, _IP_address, _Destination_dir):
  print "[FUNC]", sys._getframe().f_code.co_name
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
  command3 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + _Destination_dir + "; unzip " + os.path.basename(_Ear_Bundles) + "; ls -lah; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp cfg/*.cfg  /opt/tibco/applications/devops/deploy/cfg/; \""
  print command3
  command3_sb = sb.Popen(shlex.split(command3), stdout=sb.PIPE)
  data_command3 = command3_sb.communicate()[0]
  print data_command3

  data_command4 = ""
  # if "EMS_SCRIPTS" in os.environ and EMS_SCRIPTS is not None and EMS_SCRIPTS != "" and VALIDATION_ONLY == "NO":
  #   command4 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + Destination_dir + "; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/" + EMS_SCRIPTS + "/*; cp -r " + EMS_SCRIPTS + " /opt/tibco/applications/devops/deploy/ems/; rm -rf " + EMS_SCRIPTS + "\""
  #   # ssh -i ~/.ssh/tibco_id_rsa tibco@$IP_address -C "cd $Destination_dir; tar xvf Ems.tar; mkdir -p /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*;  rm -rf /opt/tibco/applications/devops/deploy/ems/$EMS_SCRIPTS/*; cp -r $EMS_SCRIPTS /opt/tibco/applications/devops/deploy/ems/; rm -rf $EMS_SCRIPTS"
  #   print command4
  #   command4_sb = sb.Popen(shlex.split(command4), stdout=sb.PIPE, stderr=sb.PIPE)
  #   data_command4 = command4_sb.communicate()[0]


  data_command5 = ""
  # if "COUCHBASE_SCRIPTS" in os.environ and COUCHBASE_SCRIPTS is not None and COUCHBASE_SCRIPTS != "" and VALIDATION_ONLY == "NO":
  #   command5 = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_address + " -C \"cd " + Destination_dir + "; tar xvf Couchbase.tar;  mkdir -p /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*;  rm -rf /opt/tibco/applications/devops/deploy/couchbase/" + COUCHBASE_SCRIPTS + "/*; cp -r " + COUCHBASE_SCRIPTS + " /opt/tibco/applications/devops/deploy/couchbase/; rm -rf " + EMS_SCRIPTS + "\""
  #   print command5
  #   command5_sb = sb.Popen(shlex.split(command5), stdout=sb.PIPE, stderr=sb.PIPE)
  #   data_command5 = command5_sb.communicate()[0]


  return data_command1 + "\n" + data_command2 + "\n" + data_command3 + "\n" + data_command4 + "\n" + data_command5 + "\n"


def getSuffix(_data_cmd, _ENVIRONMENT):
	print "[FUNC]", sys._getframe().f_code.co_name
	data_cmd = _data_cmd
	group = re.search(_ENVIRONMENT +  ur'\|[^\|]*\|([^\|]*)', data_cmd)
	if group is not None and len(group.groups()) > 0:
		# print group.groups()[0]
		# global SUFFIX
		SUFFIX = group.groups()[0]
		return SUFFIX
		# print "[INFO] " + SUFFIX + "\n"
	return None


def deploy_module(_EAR_NAME, _IP_ADDRESS, _HOT_RELEASE):
  print "[FUNC]", sys._getframe().f_code.co_name

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



def deploy(username, password, bundle, service, environment, hotrelease):
	print "[FUNC]", sys._getframe().f_code.co_name
	environments = getEnvTable(username, password, "http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/DX-MARS_Environment_List.txt")
	ip = getIpAddress(environments, environment)
	suffix = getSuffix(environments, environment)

	resultCopy = copy_tibco_artifact(bundle, ip, "/opt/tibco/cqm_eis_deployment")
	print "[INFO] copy_tibco_artifact", resultCopy

	if resultCopy.lower().find("exception") != -1 or resultCopy.lower().find("No such file") != -1 or resultCopy.lower().find("fail") != -1 or resultCopy.lower().find("error") != -1:
		raise Exception("Function of copy_tibco_artifact failed", resultCopy)

	deployResult = deploy_module(service, ip, hotrelease)
	print "[INFO] deploy_module", deployResult

	if deployResult.lower().find("exception") != -1 or deployResult.lower().find("No such file") != -1 or deployResult.lower().find("fail") != -1 or deployResult.lower().find("error") != -1:
		raise Exception("Function of deploy_module failed", deployResult)
		

if __name__ == "__main__":
	print "[FUNC]", sys._getframe().f_code.co_name

	comment = "{{color:green}}Promote of {0} has been finished successfully and is available under release of {1}{{color}}".format(service, RC)
	try:
		promote = Promote(workspace = WORKSPACE, 
			repository = repository, 
			service = service, 
			release=RC, 
			environment=ENVIRONMENT, 
			branch=BRANCH,
			extension="zip")	
		promote.setArtefactoryCredentials(username=ARTIUSER, password=ARTIPASS, server=ARTISERVER)
		promote.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
		promote.setCouchBaseScript(COUCHBASE_SCRIPTS)
		promote.setEmsScript(EMS_SCRIPTS)
		result = promote.execute()
		updateConfiguration(folder=WORKSPACE, service=service, rc=RC)


		bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".{0}".format(EXTENSION))
		if result is None:
			raise Exception("Promotion failed")

		if result["package"] is None:
			raise ValueError("Package does not exist")

		deploy(username=SVNUSER, password=SVNPASS, bundle=result["package"], environment=ENVIRONMENT, hotrelease="YES", service=service)

	except Exception as e:
		print e
		print "[EXCEPTION]", " ", str(e)
		comment = "{{color:red}}Overall promote of {0} failed{{color}}: \n\n{1}".format(service , str(e))
		

	if JIRAKEY is not None and JIRAKEY != "":
			jiraManager = jira(server=JIRASERVER, userName = JIRAUSER, password = JIRAPASS)
			jiraManager.addComment(jiraKey = JIRAKEY, comment = comment)


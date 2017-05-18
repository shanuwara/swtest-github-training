#!python2.7 -u

import os
import sys

sys.path.append(os.getcwd())

from DesignTimeParser.DesignTimeParser import DesignTimeParser
from custom_field_editor.CustomFieldEditor import CustomFieldManager as CFM
from cqm_libs.artefactory import artefactory
from cqm_libs.jira import jira
from cqm_libs.utility import info
from cqm_libs.utility import utility



import subprocess as sb
import shlex
import re
from time import sleep
import datetime
import base64
import urllib2
import json
import hashlib
import glob
import fnmatch
from zipfile import ZipFile as zipfile





class Build:

	TYPE_BUILD = 1
	TYPE_DEPLOYMENT = 2

	@info()	
	def __init__(self, **kwargs):
		self.__WORKSPACE = kwargs.pop("workspace", None)
		self.__REPOSITORY = kwargs.pop("repository", None)
		self.__SERVICE_OBJ = kwargs.pop("serviceObj", None)
		dtl = kwargs.pop("dtl", None)
		self.__DTLFile = dtl.file
		self.__DTLDir = dtl.directory
		# self.__DTLSource = dtl.source

		self.__PROJECT = kwargs.pop("project", None)


		self.__BUILD_ERRORS = {}

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

		self.__BuildFolder = kwargs.pop("target", None)

		assert self.__BuildFolder != None

		print self.cleanBuildFolder()
		self.createBuildFolder()


		if (os.path.join(self.__WORKSPACE, "") == os.path.join(self.__DTLDir, "")):
			raise ValueError("Libraries must not be placed in WORKSPACE")

		if self.__PROJECT == None:
			raise ValueError("Value of project is not set")

		self.__BRANCH = kwargs.pop("branch", None)
		

		self.TYPE_ALL = 1
		self.TYPE_SINGLE = 0


	@info()
	def getBranch(self):
		if self.__BRANCH in [None, "None", ""]:
			self.__BRANCH = "trunk"
		
		return self.__BRANCH

	@info()
	def getConfigDir(self):
		return os.path.join(self.getBuildDir(), "cfg")

	
	@info()
	def getBuildDir(self):
		return self.__BuildFolder

	@info()
	def getCodeDir(self):
		return os.path.join(self.getBuildDir(), "code")


	@info()
	def getServiceObj(self):
		return self.__SERVICE_OBJ

	@info()
	def getServiceName(self):
		return self.getServiceObj().getName()

	@info()
	def runCommand(self, cmd):
		print "[EXECUTING]", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()

		return output

	@info()
	def setBuildNumber(self, number):
		self.__BUILDNUMBER = number

	@info()
	def cleanBuildFolder(self):
		cmd = "rm -rf {0}".format(self.__BuildFolder)
		output = self.runCommand(cmd)

		return output

	@info()
	def createBuildFolder(self):
		if not os.path.exists(self.getBuildDir()):
			folder = self.getCodeDir()
			print "[EXECUTING]", "os.makedirs({0})".format(folder)
			os.makedirs(folder)

			folder = self.getConfigDir()
			print "[EXECUTING]", "os.makedirs({0})".format(folder)
			os.makedirs(folder)


	@info()
	def setSubversionCredentials(self, username, password):
		self.__SVNUSER = username
		self.__SVNPASS = password
		return self


	@info()
	def exportSVN(self, _url, _target):
		assert _url != None
		assert _target != None

		if _url == "" or _target == "":
			return None

		cmd = "svn export --force --non-interactive --username={0} --password={1} {2} {3}".format(self.__SVNUSER, self.__SVNPASS, _url, _target)
		output = self.runCommand(cmd)


		return output

	@info()
	def build(self):
		os.environ['DISPLAY'] = "localhost:1.0" ## tweaking xserver
		os.chdir(self.getTibcoDir())
		cmd = "./buildear -s -x -a {0} -ear /Build/{1}.archive -p {2} -o {3}".format(self.__DTLFile, self.getServiceName(), self.getCodeDir(), os.path.join(self.getBuildDir(), self.getServiceName() + ".ear"))

		output = self.runCommand(cmd)
		os.chdir(self.__WORKSPACE)

		return output


	@info()
	def getTibcoDir(self):
		version = self.getServiceObj().getTibcoTraVersion()
		if version == "5.9":
			return self.__TibcoDir59
		elif version == "5.7":
			return self.__TibcoDir57
		else:
			return None

	@info()
	def getTibcoBuildEar(self):
		version = self.getServiceObj().getTibcoTraVersion()
		if version == "5.9":
			return self.__TibcoBuildEar59
		elif version == "5.7":
			return self.__TibcoBuildEar57
		else:
			return None




	@info()
	def getRevision(self):
		cmd = "svn info --non-interactive --username={0} --password={1} {2}".format(self.__SVNUSER, self.__SVNPASS, self.__REPOSITORY)
		output = self.runCommand(cmd)

		tmp = output[0].split()
		pos = tmp.index("Revision:") + 1

		return tmp[pos]

	@info()
	def getBuildErrors(self):
		return self.__BUILD_ERRORS


	@info()
	def execute(self, _type):
		self.getDTL()

		# services = self.getServiceList()
		self.__REVISION = self.getRevision()

		# print services

		buildErrors = {}
		errorPatterns = ["error", "fail", "exception"]


		if _type == self.TYPE_SINGLE:
			configUrl = ""
			codeUrl = ""


			print self.downloadConfigs()
			print "[INFO] tibco_dir=", self.getTibcoDir()
			if self.getTibcoDir() == None:
				raise ValueError("tibco_tra_version is not set for service of " + self.getServiceName())

			self.downloadCode()
			out, err = self.build()

			
			errorFound = False

			for pattern in errorPatterns:
				if out.lower().find(pattern) != -1:
					errorFound = True
					break

			self.__BUILD_ERRORS[self.getServiceName()] = out
			

		# elif _type == self.TYPE_ALL:

			
		# 	for service, url in services.items():
		# 		configUrl = ""
		# 		codeUrl = ""
		# 		buildErrors[service] = ""
		# 		self.__SERVICE = service

		# 		print "service=", service
		# 		print "url=", url
		# 		self.cleanBuildFolder()
		# 		self.createBuildFolder()
			
				
		# 		print self.downloadConfigs(url = configUrl)
		# 		print "[INFO] tibco_dir=", self.getTibcoDir()

		# 		if self.getTibcoDir() == None:
		# 			out = "[ERROR] No config files found for service " + service
		# 			buildErrors[service] = out
		# 			continue

		# 		print "[INFO] codeUrl=",codeUrl
		# 		print "[INFO] configUrl=",configUrl

		# 		self.downloadCode(codeUrl)
		# 		out, err = self.build()

		# 		print out

		# 		errorFound = False

		# 		for pattern in errorPatterns:
		# 			if out.lower().find(pattern) != -1:
		# 				errorFound = True
		# 				buildErrors[service] = out

		# 		if errorFound == False:
		# 			_filein = os.path.join(self.__BuildFolder, service + ".ear") + " " + self.getConfigDir()
		# 			_fileout = os.path.join(self.__WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(self.__REVISION, self.__BUILDNUMBER, self.getBranch()) + ".zip")
		# 			self.zipFile(_filein=_filein, _fileout=_fileout)

		# 	return buildErrors


		return not errorFound




	@info()
	def cleanDTL(self):
		cmd = "rm -rf {0}".format(self.__DTLDir)

		output = self.runCommand(cmd)
		return output



	@info()
	def getDTL(self):
		print self.cleanDTL()
		# print self.exportSVN(self.__DTLSource, self.__DTLDir)
		self.__DTLSource = self.getServiceObj().getBuild(branch=self.getBranch()).get("dtl_url", "")
		self.exportSVN(self.__DTLSource, self.__DTLDir)

		
		designTimeParser = DesignTimeParser(
			source=os.path.join(self.__WORKSPACE, "tmp", "code", ".designtimelibs"), 
			target=self.__DTLFile, 
			folder=self.__DTLDir,
			debug=True)
		designTimeParser.generateConfiguration()



	@info()
	def downloadConfigs(self):
		deployment = self.getServiceObj().getDeployment(branch=self.getBranch())
		keys = deployment.keys()

		for key in keys:
			config_url = deployment.get(key, {}).get("config_url", None)
			if config_url is not None:
				self.exportSVN(_url=config_url, _target= self.getConfigDir())


	@info()
	def downloadCode(self):
		build = self.getServiceObj().getBuild(branch = self.getBranch())
		codebase_url = build.get("codebase_url", None)
		if codebase_url is not None:
			return self.exportSVN(_url=codebase_url, _target= self.getCodeDir())
		return None


	@info()
	def getServiceList(self):
		url = os.path.join(self.__REPOSITORY, "trunk" )
		print url
		if self.getBranch() != "trunk":
			url = os.path.join(self.__REPOSITORY, "branch", self.getBranch())

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

			print tmp

			left = tmp[-3] + tmp[-2].replace(".", "")
			right = tmp[-1]

			print left
			print right
			if left.lower() == right.lower():
				listServices[right] = service

		return listServices

	@info()
	def zipFile(self, _filein, _fileout):
		cmd = "zip -r " + _fileout + " " + _filein
		print "[EXECUTING]", cmd
		zip_file = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data_zip_file = zip_file.stdout.read()
		print "[INFO] " + data_zip_file







@info()
def scmPollLog(_url, _folder):
	if not os.path.exists(_folder):
		# svn_co_command = "svn co --username=" + SVNUSER + " --password=" + SVNPASS + " http://10.33.20.5:8080/svn/cqm/cqm_dev_test/Code/Bw repo"
		svn_co_command = "svn --non-interactive co --username={0} --password={1} {2} {3}".format(SVNUSER, SVNPASS, _url, os.path.basename(_folder))
		print svn_co_command
		svn_co = sb.Popen(shlex.split(svn_co_command), stdout=sb.PIPE)
		data_svn_co = svn_co.stdout.read()
		# print data_svn_co
		data_svn_log = data_svn_co

	else:
		os.chdir(_folder)
		os.system("pwd")
		svn_log_command = "svn up --non-interactive --username={0} --password={1}".format(SVNUSER, SVNPASS)
		# print svn_log_command
		svn_log = sb.Popen(shlex.split(svn_log_command), stdout=sb.PIPE)
		data_svn_log = svn_log.stdout.read()
		# print data_svn_log
		os.chdir(WORKSPACE)
		os.system("pwd")


	# data_svn_log = data_svn_co
	
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



# def exportSVN(_username, _password,_url, _target):
# 	print "[FUNC]", sys._getframe().f_code.co_name
# 	cmd = "svn export --force --non-interactive --username={0} --password={1} {2} {3}".format(_username, _password, _url, _password)
# 	proc = sb.Popen(shlex.split(command_svn_info_dir), stdout=sb.PIPE, stderr=sb.PIPE)
# 	output = proc.communicate()

# 	return output



# def zipFile(_filein, _fileout):
# 	print "[FUNC]", sys._getframe().f_code.co_name
# 	cmd = "zip -r " + _fileout + " " + _filein
# 	print "[EXECUTING]", cmd
# 	zip_file = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
# 	data_zip_file = zip_file.stdout.read()
# 	print "[INFO] " + data_zip_file

@info()
def zipFile(_filein, _fileout):

	listFile = _filein.split()
	with zipfile(_fileout, "w") as zip:
		for item in listFile:
			print item
			print os.walk(os.path.dirname(item))
			os.chdir(os.path.dirname(item))
			if os.path.isfile(item):
				print os.path.basename(item)
				zip.write(os.path.basename(item))
				continue
			for dirname, subdirs, files in os.walk(item):
				zip.write(os.path.basename(dirname))
				print dirname
				print subdirs
				print files
				#print os.path.dirname(dirname)
				for filename in files:
					pass
					zip.write(os.path.join(os.path.basename(dirname), filename))
					#print os.path.join(os.path.dirname(dirname), filename)
					print os.path.join(os.path.basename(dirname), filename)



@info()
def getEnvTable(username, password, url):
	command = "curl -s -u {0}:{1} -X GET {2}".format(username, password, url)
	print command
	cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE)
	data_cmd = cmd.communicate()[0]
	return data_cmd


@info()
def getIpAddress(_data_cmd, _ENVIRONMENT = ""):
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

@info()
def copy_tibco_artifact(_Ear_Bundles, _IP_address, _Destination_dir):
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



@info()
def getSuffix(_data_cmd, _ENVIRONMENT):
	data_cmd = _data_cmd
	group = re.search(_ENVIRONMENT +  ur'\|[^\|]*\|([^\|]*)', data_cmd)
	if group is not None and len(group.groups()) > 0:
		# print group.groups()[0]
		# global SUFFIX
		SUFFIX = group.groups()[0]
		return SUFFIX
		# print "[INFO] " + SUFFIX + "\n"
	return None


@info()
def deploy_module(_EAR_NAME, _IP_ADDRESS, _HOT_RELEASE):

  deployment_log = open("deployment.log", "w")
  if _HOT_RELEASE == "NO":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./manageApp.sh " + _EAR_NAME + " 1 stop; ./deploy.sh " + _EAR_NAME + "; ./manageApp.sh " + _EAR_NAME + " 1 start\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    # print data_command
    deployment_log.write(data_command)
  elif _HOT_RELEASE == "YES":
    command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@" + _IP_ADDRESS + " -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh " + _EAR_NAME + " 2>&1;\" "
    print command
    cmd = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
    data_command = cmd.communicate()[0]
    # print data_command
    deployment_log.write(data_command)

  return data_command



@info()
def deploy(username, password, bundle, service, environment, hotrelease):
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







##########################################################



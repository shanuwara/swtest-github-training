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
from ServiceConfiguration1.ServiceConfiguration import Configuration
from ServiceConfiguration1.Service import Service
from build import Build

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




@info()
def setGlobals(*args, **kwargs):
	utility.setGlobals(*args, **kwargs)


## settings

elements = ( "ARTIUSER", "ARTIPASS", "AUTOMATIC", "BUILD_NUMBER", 
	"WORKSPACE", "SVNUSER", "SVNPASS", "JIRAKEY", 
	"JIRAUSER", "JIRAPASS", "BRANCH", "FORCE_SERVICE" )

setGlobals(globals(), elements)

ARTISERVER = "http://10.33.20.7:8080"
REVISION = 0
JIRASERVER = "http://10.33.20.21:8080/jira"
repository = "http://10.33.20.5:8080/svn/DX/DX"

artifactory = "http://10.33.20.7:8080/artifactory/simple/DX-MARS/"
artifactoryName = "DX-MARS"
branch = BRANCH if BRANCH is not None else "trunk"
target = os.path.join(WORKSPACE, "tmp")
service = FORCE_SERVICE




class DTL:
	def __init__(self, filename, source, directory):
		self.source = source
		self.directory = directory
		self.file = os.path.join(self.directory, filename)
 


# if __name__ == "__main__":


# 	## library package
# 	libs = DTL
# 	libs.directory = os.path.join(WORKSPACE, "libs")
# 	libs.file = os.path.join(WORKSPACE, "file.properties")

# 	if branch != "trunk":
# 		libs.source = os.path.join(repository, "branch" , branch, "Development/Code/Bw/Shared")
# 	else:
# 		libs.source = os.path.join(repository, "trunk", "Development/Code/Bw/Shared")
# 	###


# 	## 1. build flow - automatic
# 	comment = ""
# 	if AUTOMATIC == "YES":
# 		try:
# 			comment = ""
# 			changedServices = scmPollLog(_url = os.path.join(repository, "trunk", "Development/Code/Bw"), _folder="repo")
# 			print changedServices

# 			build = Build(workspace = WORKSPACE, service="*all", repository=repository, dtl=libs, target=target, branch="trunk")
# 			build.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# 			build.setBuildNumber(BUILDNUMBER)
# 			REVISION = build.getRevision()
# 			availableServices = build.getServiceList()
# 			build = None

# 			if changedServices is not None:
# 				for entry in changedServices:
# 					if entry not in availableServices:
# 						del availableServices[entry]
# 			else:
# 				availableServices = None

# 			print availableServices

# 			## unit test
# 			# del availableServices['SportsbookEvent_MARS10']

# 			###

# 			deployable = False
# 			if availableServices is not None:
# 				deployable = True
# 				for foundService in availableServices:
# 					## build flow
# 					build = Build(workspace = WORKSPACE, service=foundService, repository=repository, dtl=libs, target=target, branch="trunk")
# 					build.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# 					build.setBuildNumber(BUILDNUMBER)
# 					buildResult = build.execute(build.TYPE_SINGLE)
# 					###

# 					## packaging
# 					if not buildResult:
# 						deployable = False
# 					else:
# 						bundle = os.path.join(WORKSPACE, foundService + + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 						zipFile(_filein = os.path.join(target, foundService + ".ear") + " " + os.path.join(target, "cfg"), _fileout=bundle)
# 					###


# 			## validate package
# 			if deployable:
# 				try:
# 					for foundService in availableServices:
# 						bundle = os.path.join(WORKSPACE, foundService + + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 						deploy(username=SVNUSER, password=SVNPASS, bundle=bundle, environment="LS_DEV", hotrelease="YES", service=foundService)
# 				except Exception as e:
# 					deployable = False
# 					print "[EXCEPTION]", " ".join(e)
# 					comment += "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(" ".join(e))

# 			if deployable:
# 				for foundService in availableServices:
# 					bundle = os.path.join(WORKSPACE, foundService + + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 					artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
# 					artefactoryManager.upload(repository="DX-MARS", folder=branch, file=bundle)

# 					comment += "\n\n{{color:green}}Service {0} has been built and deployed (to LS_DEV) successfully{{color}}".format(foundService)
# 			###

				
# 		except Exception as e:
# 			print "[EXCEPTION]", " ".join(e)
# 			comment = "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(" ".join(e))


# 		if JIRAKEY is not None and JIRAKEY != "":
# 			jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
# 			jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)

# 		sys.exit(0)
# 	###




# 	######################################################3



# 	## 2. build flow - manual
# 	comment = ""
# 	try:
# 		build = Build(
# 			workspace = WORKSPACE, 
# 			service=service, 
# 			repository=repository, 
# 			dtl=libs, 
# 			target=target, 
# 			branch=branch)
# 		build.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# 		build.setBuildNumber(BUILDNUMBER)
# 		REVISION = build.getRevision()

# 		if service.lower() == "all" or service.lower() == "*all":
# 			buildType = build.TYPE_ALL
# 		else:
# 			buildType = build.TYPE_SINGLE

# 		buildResult = build.execute(buildType)
# 		###



# 		## validate package
# 		if buildType == build.TYPE_SINGLE:

# 			## packaging
# 			if buildResult == True:
# 				bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 				zipFile(_filein = os.path.join(target, service + ".ear") + " " + os.path.join(target, "cfg"), _fileout=bundle)
# 			###

# 				deploy(username=SVNUSER, password=SVNPASS, bundle=bundle, environment="LS_DEV", hotrelease="YES", service=service)

# 				artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
# 				artefactoryManager.upload(repository="DX-MARS", folder=branch, file=bundle)

# 				comment = "{{color:green}}Service {0} has been built and deployed to LS_DEV successfully{{color}}".format(service)


		
# 		if buildType == build.TYPE_ALL:
# 			deployable = True
# 			print buildResult

# 			for index, result in buildResult.items():
# 				if result != "":
# 					deployable = False
# 					comment += "{color:red}" + index + "{color}: " + result + "\n\n"
# 				else:
# 					comment += "{color:green}" + index + ": [SUCCESS]{color}\n\n"

# 			if not deployable:
# 				comment += "\n\nAs the result of previous failure(s) no artifact has been deployed"
# 				raise Exception(comment)

# 			## validate package
# 			try:
# 				for service, result in buildResult.items():
# 					bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 					deploy(username=SVNUSER, password=SVNPASS, bundle=bundle, environment="LS_DEV", hotrelease="YES", service=service)
# 			except Exception as e:
# 				deployable = False
# 				print "[EXCEPTION]", " ".join(e)
# 				comment += "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(" ".join(e))

# 			if deployable:
# 				for service, result in buildResult.items():
# 					bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
# 					artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
# 					artefactoryManager.upload(repository="DX-MARS", folder=branch, file=bundle)

# 					comment += "\n\n{{color:green}}Service {0} has been built and deployed (to LS_DEV) successfully{{color}}".format(service)
# 			###

			

# 	except Exception as e:
# 		print "[EXCEPTION]", str(e)
# 		comment = "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(str(e))



# 	if JIRAKEY is not None and JIRAKEY != "":
# 		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
# 		jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
# 	###


if __name__ == "__main__":



	## 2. build flow - manual
	comment = ""
	try:
		manager = Configuration(SVNUSER=SVNUSER, SVNPASS=SVNPASS, URL="http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/services.json")
		serviceObj = Service(manager.getService(service))


		libs = DTL
		libs.directory = os.path.join(WORKSPACE, "libs")
		libs.file = os.path.join(WORKSPACE, "file.properties")
		# libs.source = serviceObj.getDTLDir



		build = Build(
			workspace = WORKSPACE, 
			repository=repository, 
			dtl=libs, 
			target=target, 
			branch=branch,
			serviceObj=serviceObj,
			project="DX")

		build.setSubversionCredentials(username=SVNUSER, password=SVNPASS) \
			.setBuildNumber(BUILD_NUMBER)

		REVISION = build.getRevision()


		buildResult = build.execute(build.TYPE_SINGLE)

		if buildResult:
			comment = "{{color:green}}Service {0} has been built successfully{{color}}".format(service)

			parameters = {}
			parameters["rev"] = REVISION
			parameters["build"] = BUILD_NUMBER
			parameters["branch"] = build.getBranch()
			parameters["service"] = build.getServiceName()

			bundle = os.path.join(WORKSPACE, "{service}_REV_{rev}_BUILD_{build}_{branch}.zip".format(**parameters) )
			zipFile(_filein = os.path.join(build.getBuildDir(), service + ".ear") + " " + build.getConfigDir(), _fileout=bundle)
			artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
			artefactoryManager.upload(repository=artifactoryName, folder=build.getBranch(), file=bundle)

			parameters["file"] = os.path.basename(bundle)

			with open("parameters.txt", "w") as f:
				for key, val in parameters.items():
					f.write("{0}={1}\n".format(key, value))

		else:
			# comment = "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(str(build.getBuildErrors()))
			raise Exception(str(build.getBuildErrors()))

		###
		## validate package
		# if buildType == build.TYPE_SINGLE:

		# 	## packaging
		# 	if buildResult == True:
		# 		bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILD_NUMBER, branch) + ".zip")
		# 		zipFile(_filein = os.path.join(build.getBuildDir(), service + ".ear") + " " + build.getConfigDir(), _fileout=bundle)
		# 	###

		# 		# deploy(username=SVNUSER, password=SVNPASS, bundle=bundle, environment="LS_DEV", hotrelease="YES", service=service)

		# 		# artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
		# 		# artefactoryManager.upload(repository="DX-MARS", folder=branch, file=bundle)

		# 		# comment = "{{color:green}}Service {0} has been built and deployed to LS_DEV successfully{{color}}".format(service)


		
		# if buildType == build.TYPE_ALL:
		# 	deployable = True
		# 	print buildResult

		# 	for index, result in buildResult.items():
		# 		if result != "":
		# 			deployable = False
		# 			comment += "{color:red}" + index + "{color}: " + result + "\n\n"
		# 		else:
		# 			comment += "{color:green}" + index + ": [SUCCESS]{color}\n\n"

		# 	if not deployable:
		# 		comment += "\n\nAs the result of previous failure(s) no artifact has been deployed"
		# 		raise Exception(comment)

		# 	## validate package
		# 	try:
		# 		for service, result in buildResult.items():
		# 			bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
		# 			deploy(username=SVNUSER, password=SVNPASS, bundle=bundle, environment="LS_DEV", hotrelease="YES", service=service)
		# 	except Exception as e:
		# 		deployable = False
		# 		print "[EXCEPTION]", " ".join(e)
		# 		comment += "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(" ".join(e))

		# 	if deployable:
		# 		for service, result in buildResult.items():
		# 			bundle = os.path.join(WORKSPACE, service + "_REV_{0}_BUILD_{1}_{2}".format(REVISION, BUILDNUMBER, branch) + ".zip")
		# 			artefactoryManager = artefactory(userName=ARTIUSER,password=ARTIPASS,server=ARTISERVER)
		# 			artefactoryManager.upload(repository="DX-MARS", folder=branch, file=bundle)

		# 			comment += "\n\n{{color:green}}Service {0} has been built and deployed (to LS_DEV) successfully{{color}}".format(service)
		# 	###

			

	except Exception as e:
		print "[EXCEPTION]", str(e)
		comment = "{{color:red}}Overall build failed{{color}}: \n\n{0}".format(str(sys.exc_info()))



	if JIRAKEY is not None and JIRAKEY != "":
		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
		jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
	###

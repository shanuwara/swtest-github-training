#!python2.7

import os
import sys
sys.path.append(os.getcwd())
import subprocess as sb
import shlex
from cqm_libs.artefactory import artefactory
from cqm_libs.jira import jira

def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "" or value == "None":
			value = None
		globals()[element] = value

elements = ("WORKSPACE", "SVN_REVISION_1", "BUILD_NUMBER", "BRANCH", "JIRAKEY", "ARTIUSER", "ARTIPASS", "JIRAUSER", "JIRAPASS")

setGlobals(elements)

REVISION = SVN_REVISION_1
ARTISERVER = "http://10.33.20.7:8080"
JIRASERVER = "http://10.33.20.21:8080/jira"


if BRANCH == "" or BRANCH == "trunk":
	BRANCH = None


class Build:

	def __init__(self, workspace, javac, revision, buildnumber, branch):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.WORKSPACE = workspace
		self.JAVAC = javac
		self.REVISION = revision
		self.BUILD_NUMBER = buildnumber
		self.BRANCH = branch

		self.ARTIUSER = None
		self.ARTIPASS = None
		self.ARTISERVER = None

	def setArtifactoryCredentials(self, server, username, password):
		self.ARTIUSER = username
		self.ARTIPASS = password
		self.ARTISERVER = server

	def execute(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "ant -f build.xml localDeploy -DlocalProject.path={0} -DlocalWarDeployDestination={0} -Dtomcat.home={0} -DjavacPath={1}"
		cmd = cmd.format(self.WORKSPACE, self.JAVAC)

		print "[EXECUTING]", cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()
		tmp = '\n\n'.join(output).lower()

		if self.__checkForErrors(tmp):
			pass
			raise Exception('Build failed', tmp)

		if self.BRANCH is None:
			branch = "trunk"
			branchFolder = "trunk"
		else:
			branch = self.BRANCH
			branchFolder = os.path.join("branch", self.BRANCH)

		defaultFilename = os.path.join(self.WORKSPACE, "eventscheduler.war")

		filename = "eventscheduler_REV_{0}_BUILD_{1}_{2}.war".format(self.REVISION, self.BUILD_NUMBER, branch)
		if os.path.exists(defaultFilename):
			os.rename(defaultFilename, filename)
		else:
			raise Exception('Package eventscheduler.war not found')

		artefactoryManager = artefactory(userName=self.ARTIUSER,password=self.ARTIPASS,server=self.ARTISERVER)
		artefactoryManager.upload(repository="DX-MARS", folder=branch, file=filename)

		




	def __checkForErrors(self,input):
		markers = ['fail', 'error', 'exception']

		for marker in markers:
			if input.find(marker) != -1:
				return True

		return False


javac = "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.102-1.b14.el7_2.x86_64/bin/javac"

try:
	build = Build(workspace = WORKSPACE, javac = javac, revision = REVISION, buildnumber=BUILD_NUMBER, branch = BRANCH)
	build.setArtifactoryCredentials(server=ARTISERVER, username=ARTIUSER, password=ARTIPASS)
	build.execute()


	if JIRAKEY is not None and JIRAKEY != "":
		comment = "{color:green}Packages built successfully{color}"
		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
		jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
except Exception as e:
	if JIRAKEY is not None and JIRAKEY != "":
		comment = "{color:red}Build package failed{color}" + str(e)
		jiraManager = jira(userName=JIRAUSER, password=JIRAPASS, server=JIRASERVER)
		jiraManager.addComment(jiraKey= JIRAKEY, comment=comment)
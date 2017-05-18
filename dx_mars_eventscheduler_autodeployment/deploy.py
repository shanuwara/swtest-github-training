#!python2.7

import sys, os, shlex, json, csv, StringIO
sys.path.append(os.getcwd())
from collections import defaultdict
import subprocess as sb
from cqm_libs.artefactory import artefactory

class Deploy:
	def __init__(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__ARTISERVER = kwargs.pop('ARTISERVER', None)
		self.__ARTIUSER = kwargs.pop('ARTIUSER', None)
		self.__ARTIPASS = kwargs.pop('ARTIPASS', None)

		self.__SVNUSER = kwargs.pop('SVNUSER', None)
		self.__SVNPASS = kwargs.pop('SVNPASS', None)


		self.__REPOSITORY = kwargs.pop('repository', None)
		self.__SERVICE = kwargs.pop('service', None)
		self.__RC = kwargs.pop('rc', None)
		self.__BRANCH = kwargs.pop('branch', None)
		self.__EXTENSION = kwargs.pop('extension', None)
		self.__SETTINGS_URL = kwargs.pop('settings_url', None)
		self.__ENVIRONMENT = kwargs.pop('environment', None)
		

	def getArtefactoryManager(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		if self.__ARTISERVER is None or self.__ARTIUSER is None or self.__ARTIPASS is None:
			return None

		artefactoryManager = artefactory(server=self.__ARTISERVER,userName=self.__ARTIUSER,password=self.__ARTIPASS)
		return artefactoryManager

	
	def runCommand(self, cmd):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "{0}".format(cmd)
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()
		return {"stdout": output[0], "stderr": output[1], "returncode": proc.returncode}

	def getArtifactoryUrl(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		artefactoryManager = self.getArtefactoryManager()
		
		if self.__RC is not None:
			suffix = self.__BRANCH + "_" + self.__RC if self.__BRANCH is not None and self.__BRANCH != "" else "trunk" + "_" + self.__RC
		else:
			suffix = self.__BRANCH if self.__BRANCH is not None and self.__BRANCH != "" else "trunk"

		suffix += self.__EXTENSION

		# print "{0}_REV_*_BUILD_*_{1}".format(self.__SERVICE, suffix)

		bundles = artefactoryManager.advancedSearch(repository=self.__REPOSITORY,folder=self.__RC, searchName="{0}_REV_*_BUILD_*_{1}".format(self.__SERVICE, suffix), sortPattern=None)
		if len(bundles) == 0:
			return None
		bundle = bundles[-1]
		
		url = None

		if self.__RC is not None:
			url = os.path.join(self.__ARTISERVER, "artifactory", self.__REPOSITORY, self.__RC, bundle)
		else:
			url = os.path.join(self.__ARTISERVER, "artifactory", self.__REPOSITORY, "trunk" if self.__BRANCH is None or self.__BRANCH == "" else self.__BRANCH, bundle)

		return url

	def getSettings(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "curl -u {0}:{1} -X GET {2}".format(self.__SVNUSER, self.__SVNPASS, self.__SETTINGS_URL)
		output = self.runCommand(cmd)
		
		if output["returncode"] != 0 or output["stdout"] is None or output["stdout"] == "":
			return None

		lines = defaultdict(list)
	
		reader = csv.DictReader(StringIO.StringIO(output["stdout"]))
		for line in reader:
			lines[line["environment"]].append(line)
		return lines

	def getNodes(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		settings = self.getSettings()
		return settings[self.__ENVIRONMENT]


	def execute(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		nodes = self.getNodes()
		source = self.getArtifactoryUrl()
		target = nodes[0]['target']
		package = self.__SERVICE + self.__EXTENSION

		if nodes is None:
			raise ValueError("Servers not found in configuration")

		if source is None:
			raise ValueError("Package not found in artifactory")

		if target is None:
			raise ValueError("Target folder is incorrect")

		if package is None:
			raise ValueError("Target filename is incorrect")
			

		
		cmd = "mco rpc -F ipaddress='/({0})/' dx_mars_eventscheduler  deploy url='{1}' package='{2}' target='{3}'".format("|".join(["^" +  x['ip'] + "$" for x in nodes]), source, package, target)
		print cmd
		print "[EXECUTE]", cmd
		output = self.runCommand(cmd)
		return output


if __name__ == "__main__":
	pass	








		



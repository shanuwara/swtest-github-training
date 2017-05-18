#!python2.7 -u

import subprocess as sb
import shlex, sys, json

class Configuration:
	def __init__(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.url = kwargs.pop("URL", None)
		self.__SVNUSER = kwargs.pop("SVNUSER", None)
		self.__SVNPASS = kwargs.pop("SVNPASS", None)
		self.__JSON = None

	def getJson(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		if self.__JSON == None:
			response = self.runCommand("curl -s -u {0}:{1} -X GET {2}".format(self.__SVNUSER, self.__SVNPASS, self.url))["stdout"]
			self.__JSON = json.loads(response)

		return self.__JSON

	def getService(self, service):
		print "[FUNC]", sys._getframe().f_code.co_name
		confJson = self.getJson()
		for services in confJson:
			if services["service"] == service:
				return services

	def getServices(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		confJson = self.getJson()
		branch = kwargs.pop("branch", None)

		# for service in confJson:
		# 	for build in service["build"]:
		# 		if build["branch"] != branch:
		# 			print build
		# 			del build


		


		return confJson


	def getConfigurationBuild(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		service = kwargs.pop("service", None)
		branch = kwargs.pop("branch", None)
		environment = kwargs.pop("environment", None)

		confJson = self.getService(service)

		for entry in confJson["build"]:
			if entry["branch"] == branch:
				
				return entry

		return None

	def getConfigurationDeployment(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		service = kwargs.pop("service", None)
		branch = kwargs.pop("branch", None)
		environment = kwargs.pop("environment", None)

		confJson = self.getService(service)
		confDeployment = []

		for entry in confJson["deployment"]:
			if entry["branch"] == branch:
				if entry["env"] == environment or environment is None:	
					confDeployment.append( entry)

		return confDeployment
		

	def runCommand(self, cmd):
		print "[FUNC]", sys._getframe().f_code.co_name
		output = {}
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		stdout, stderr = proc.communicate()
		output = {"stdout":stdout, "stderr": stderr, "returncode":proc.returncode}
		# output = {"stdout":"stdout", "stderr": "stderr", "returncode":"proc.returncode"}
		return output
		


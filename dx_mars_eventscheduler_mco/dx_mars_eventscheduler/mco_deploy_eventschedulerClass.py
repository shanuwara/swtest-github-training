#!python2.7 -u

# @file_version #23

import sys, os, shlex
import subprocess as sb


class Deploy:

	def __init__(self, **kwargs):
		print "[FUNC]", sys._getframe().f_code.co_name
		self.__SYSTEM_SERVICE = kwargs.pop("systemService", None)
		self.__TARGET = kwargs.pop("target", None)
		self.__PACKAGE = kwargs.pop("package", None)
		self.__URL = kwargs.pop("url", None)


	def runCommand(self, cmd):
		print "[FUNC]", sys._getframe().f_code.co_name
		output = {}
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		stdout, stderr = proc.communicate()
		output = {"stdout":stdout, "stderr": stderr, "returncode":proc.returncode}
		return output

	def downloadPackage(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "curl -sS -o {0} {1}".format(os.path.join(self.__TARGET, self.__PACKAGE), self.__URL)
		print "[EXECUTE]", cmd
		result = self.runCommand(cmd)
		return result


	def cleanUp(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "rm -f {0}".format(os.path.join(self.__TARGET, self.__PACKAGE))
		print "[EXECUTE]", cmd
		result = self.runCommand(cmd)
		return result


	def restartService(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "service {0} restart".format(self.__SYSTEM_SERVICE)
		print "[EXECUTE]", cmd
		result = self.runCommand(cmd)
		return result

	def execute(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		if self.cleanUp()["returncode"] != 0:
			raise Exception("self.cleanUp().returncode != 0")


		if self.downloadPackage()["returncode"] != 0:
			raise Exception("self.downloadPackage().returncode != 0")

		if self.restartService()["returncode"] != 0:
			raise Exception("self.restartService().returncode != 0")
		


if __name__ == "__main__":
	# target = "/apps/tomcat7/webapps"
	# package = sys.argv[1]
	# service = "tomcat7"
	pass

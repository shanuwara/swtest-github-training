#!python2.7

import sys, os, shlex, json, csv, StringIO
sys.path.append(os.getcwd())
from collections import defaultdict
import subprocess as sb
from cqm_libs.artefactory import artefactory

class Promote:
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
		# self.__SETTINGS_URL = kwargs.pop('settings_url', None)
		# self.__ENVIRONMENT = kwargs.pop('environment', None)
		

	def getArtefactoryManager(self):
		print "[FUNC]", sys._getframe().f_code.co_name
		if self.__ARTISERVER is None or self.__ARTIUSER is None or self.__ARTIPASS is None:
			return None

		artefactoryManager = artefactory(server=self.__ARTISERVER,userName=self.__ARTIUSER,password=self.__ARTIPASS)
		return artefactoryManager

	# def downloadPackage(self):
	# 	print "[FUNC]", sys._getframe().f_code.co_name
	# 	cmd = "curl -sS -o {0} {1}".format(os.path.join(self.__TARGET, self.__PACKAGE), self.__URL)
	# 	print "[EXECUTE]", cmd
	# 	result = self.runCommand(cmd)
	# 	return result
	
	def runCommand(self, cmd):
		print "[FUNC]", sys._getframe().f_code.co_name
		cmd = "{0}".format(cmd)
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		output = proc.communicate()
		return {"stdout": output[0], "stderr": output[1], "returncode": proc.returncode}

	def getArtifactoryUrl(self, fromTrunk=False):
		print "[FUNC]", sys._getframe().f_code.co_name
		artefactoryManager = self.getArtefactoryManager()
		
		if self.__RC is not None and fromTrunk == False:
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

		if self.__RC is not None and fromTrunk == False:
			url = os.path.join(self.__ARTISERVER, "artifactory", self.__REPOSITORY, self.__RC, bundle)
		else:
			url = os.path.join(self.__ARTISERVER, "artifactory", self.__REPOSITORY, "trunk" if self.__BRANCH is None or self.__BRANCH == "" else self.__BRANCH, bundle)

		return url

	# def getSettings(self):
	# 	print "[FUNC]", sys._getframe().f_code.co_name
	# 	cmd = "curl -u {0}:{1} -X GET {2}".format(self.__SVNUSER, self.__SVNPASS, self.__SETTINGS_URL)
	# 	output = self.runCommand(cmd)
		
	# 	if output["returncode"] != 0 or output["stdout"] is None or output["stdout"] == "":
	# 		return None

	# 	lines = defaultdict(list)
	
	# 	reader = csv.DictReader(StringIO.StringIO(output["stdout"]))
	# 	for line in reader:
	# 		lines[line["environment"]].append(line)
	# 	return lines


	def execute(self):
		print "[FUNC]", sys._getframe().f_code.co_name

		self.__URL = self.getArtifactoryUrl(fromTrunk=True)

		if self.__URL is None or self.__URL == "":
			raise ValueError("Package not found in artifactory")

		package = newPackage = os.path.basename(self.__URL)
		newPackage = newPackage.replace(self.__EXTENSION, "_{0}{1}".format(self.__RC, self.__EXTENSION))

		srcFolder = "trunk" if self.__BRANCH is None else self.__BRANCH

		self.getArtefactoryManager().download(repository=self.__REPOSITORY,srcFolder=srcFolder,fileName=package,destName=newPackage)
		self.getArtefactoryManager().upload(repository=self.__REPOSITORY,folder=self.__RC,file=newPackage)

		return {"returncode":0}



if __name__ == "__main__":
	pass	








		



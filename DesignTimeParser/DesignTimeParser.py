#!python2.7

import sys, os, fnmatch


class DesignTimeParser:
	def __init__(self, **kwargs):
		self.__class__.__name__
		print "[FUNC]", self.__class__.__name__, sys._getframe().f_code.co_name
		self.__debug = kwargs.pop("debug", False)

		if self.__debug:
			print "[DEBUG]",kwargs

		self.__DTLInputFileName = kwargs.pop("source", None)
		self.__DTLOutputFileName = kwargs.pop("target", None)
		self.__DTLDir = kwargs.pop("folder", None)
		

	def parse(self):
		print "[FUNC]", self.__class__.__name__, sys._getframe().f_code.co_name
		libs = self.getList()
		parseList  = []

		print "[DEBUG]",libs


		if os.path.exists( self.__DTLInputFileName):
			with open(self.__DTLInputFileName, "r") as f:
				data = f.read()
				data = data.split("\n")

				if self.__debug:
					print "[DEBUG]",data

				for line in data:
					line = line.strip()

					if self.__debug:
						print "[DEBUG]",line

					if line != "" and not line.startswith("#"):
						lib = line.split('\=')[0].split("=")[1]
						if lib is not None and lib != "":
							parseList.append(lib + "=" + libs[lib])
					

		return parseList

	def generateConfiguration(self):
		print "[FUNC]", self.__class__.__name__, sys._getframe().f_code.co_name
		with open(self.__DTLOutputFileName, "w") as f:
			for line in self.parse():
				f.write(line + "\n")


	def getList(self):
		print "[FUNC]", self.__class__.__name__, sys._getframe().f_code.co_name

		libs = {}
		for root, dirnames, filenames in os.walk(self.__DTLDir):
			for filename in fnmatch.filter(filenames, '*.projlib'):
				# libs.append(os.path.join(root, filename))
				libs[filename] = os.path.join(root, filename)
		return libs
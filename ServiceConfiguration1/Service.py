#!python2.7 -u

# -*- coding: utf-8 -*- 


import collections



class Service(object):
	def __init__(self, json):
		self.__JSON = json
		self.__DEPLOYMENT = {}
		self.__BUILD = {}
		
		self.__setBuild().__setDeployment()


	def __setBuild(self):
		service = self.getService()
		for build in service["build"]:
			self.__BUILD[build["branch"]] = build
		return self

	def __setDeployment(self):
		service = self.getService()
		deployment = service.get("deployment", {})
		self.__DEPLOYMENT = deployment
		nested_dict = lambda: collections.defaultdict(nested_dict)
		arr = nested_dict()
		for entry in deployment:
			arr[entry["branch"]][entry["env"]] = entry

		self.__DEPLOYMENT = arr
		return self

	def getService(self):
		return self.__JSON

	

	def getBuild(self, branch = None):
		arr = self.__BUILD
		if branch is not None:
			arr = arr.get(branch, [])
		return arr

	def getName(self):
		return self.__JSON.get("service", None)

	def getDeployment(self, branch=None, environment=None):
		arr = self.__DEPLOYMENT

		if branch is not None:
			arr = arr.get(branch, {})
			if environment is not None:
				arr = arr.get(environment, [])

		return arr

	def getTibcoTraVersion(self):
		return self.getService().get("tibco_tra_version", None)

	






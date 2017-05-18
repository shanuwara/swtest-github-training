#!python2.7 -u

import json
import unittest
from mock import patch, MagicMock
from ServiceConfiguration import Configuration

class ServiceConfigurationTest(unittest.TestCase):
	def setUp(self):
		self.__JSON_INPUT = [
		  {
			"service": "RetailSportsbookPublisher20",
			"configuration": [
			  {
				"env": "SIT",
				"codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20",
				"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
				"branch": "trunk"
			  }
			]
		  }
		]

		self.module = Configuration(SVNUSER="123", SVNPASS="456", URL="http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/services.json")

	def test_getService(self):
		mockGetJson = MagicMock(return_value=self.__JSON_INPUT)
		self.module.getJson = mockGetJson

		conf = self.module.getService("RetailSportsbookPublisher20")
		self.assertIsNotNone(conf)
		self.assertIsNotNone(conf["configuration"])

	def test_getJson(self):
		output = {"stdout":self.__JSON_INPUT, "stderr": "", "returncode": 0}
		mockRunCommand = MagicMock(return_value=output)
		self.module.runCommand = mockRunCommand

		content = self.module.getJson()
		self.assertIsNotNone(content)
		print content
		self.assertEquals("RetailSportsbookPublisher20", content[0]["service"])
		mockRunCommand.assert_called_with("curl -s -u 123:456 -X GET http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/services.json")

	def test_getConfigurationBuild(self):
		mockGetService = MagicMock(return_value={
			"service": "RetailSportsbookPublisher20",
			"build": [
			  {
				"codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20",
				"branch": "trunk"
			  }
			],
			"deployment": [
			  {
				"env": "SIT",
				"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
			  }
			]
		  })
		self.module.getService = mockGetService
		conf = self.module.getConfigurationBuild(service="RetailSportsbookPublisher20", branch="trunk")
		self.assertIsNotNone(conf)
		self.assertEquals("trunk", conf["branch"])
		self.assertEquals("http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20", conf["codebase_url"])


	def test_getConfigurationDeployment(self):
		mockGetService = MagicMock(return_value={
			"service": "RetailSportsbookPublisher20",
			"build": [
			  {
				"codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20",
				"branch": "trunk"
			  }
			],
			"deployment": [
			  {
				"env": "SIT",
				"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
				"branch": "trunk",
				"domain": "eisperf"
			  },
			  {
				"env": "UAT",
				"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
				"branch": "trunk",
				"domain": "LeedsSITEAI"
			  }
			]
		  })
		self.module.getService = mockGetService
		conf = self.module.getConfigurationDeployment(service="RetailSportsbookPublisher20", branch="trunk", environment="SIT")
		self.assertIsNotNone(conf)
		self.assertEquals("trunk", conf[0]["branch"])
		self.assertEquals("SIT", conf[0]["env"])
		self.assertEquals("http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg", conf[0]["config_url"])
		self.assertEquals("eisperf", conf[0]["domain"])
		self.assertEquals(1, len(conf))

		conf = self.module.getConfigurationDeployment(service="RetailSportsbookPublisher20", branch="trunk")
		self.assertEquals(2, len(conf))

		conf = self.module.getConfigurationDeployment(service="RetailSportsbookPublisher20")
		self.assertEquals(0, len(conf))




if __name__ == "__main__":
	unittest.main()
#!python2.7 -u

import unittest
from mock import MagicMock, patch
from Service import Service
from ServiceConfiguration import Configuration
import json


class ServiceTest(unittest.TestCase):

	def test_constructor(self):
		payload = """
				  {
					"service": "RetailSportsbookPublisher20",
					"tibco_tra_version": "5.9",
					"deployment": [
					  {
						"env": "LS_UAT",
						"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsUATEAI.cfg",
						"domain": "LeedsUATEAI",
					"branch": "trunk"
					  },
					  {
						"env": "LS_SIT",
						"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
						"domain": "LeedsSITEAI",
					"branch": "trunk"
					  },
					{
						"env": "LS_DEV",
						"config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-leedsdev.cfg",
						"domain": "leedsdev",
					"branch": "trunk"
					  }
					],
					"build": [
					  {
						"branch": "trunk",
						"codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20"


					  }
					]
				  }
				
		"""
		service = Service(json.loads(payload))
		
		self.assertEquals("RetailSportsbookPublisher20", service.getName())
		self.assertEquals("5.9", service.getTibcoTraVersion())
		self.assertEquals("leedsdev", service.getDeployment(branch="trunk", environment="LS_DEV").get("domain", None))
		self.assertEquals("http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20", service.getBuild(branch="trunk").get("codebase_url", None))

		# print service.getDeployment(branch="trunk").get("LS_DEV", None)
		# print service.getBuild(branch="trunk").get("codebase_url", None)


if __name__ == "__main__":
	unittest.main()









#!python2.7


import unittest, sys, os
from StringIO import StringIO
from collections import defaultdict
from mock import patch
from mock import MagicMock
import mock

from deploy import Deploy
sys.path.append('../cqm_libs')
from artefactory import artefactory


class DeploymentCase(unittest.TestCase):

	previous = False

	def setUp(self):
		self.__ARTISERVER = "http://10.33.20.7:8080"
		self.__ARTIUSER = "admin"
		self.__ARTIPASS = "K_29^ob"
		self.__SERVICE = "eventscheduler"
		self.__ENVIRONMENT = "DEV"
		self.__RC = "RCTEST-1"
		self.__BRANCH = "MarsDayX"
		self.__SETTINGS_URL = "http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/DX_MARS_eventscheduler_environments.csv"
		self.__SVNUSER = "cqmsvn"
		self.__SVNPASS = "K_29^ob"
		pass

	def test_getArtifactoryUrl(self):
		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE,
			extension=".war",
			repository="DX-MARS"

			)

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", deploy.getArtifactoryUrl())

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE, 
			branch=self.__BRANCH,
			rc=self.__RC,
			extension=".war",
			repository="DX-MARS"
			)

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/RCTEST-1/eventscheduler_REV_13434_BUILD_12_MarsDayX_RCTEST-1.war", deploy.getArtifactoryUrl())		

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=".war",
			repository="DX-MARS")

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/RCTEST-1/eventscheduler_REV_13434_BUILD_12_trunk_RCTEST-1.war", deploy.getArtifactoryUrl())

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE, 
			rc=self.__RC,
			branch=self.__BRANCH,
			extension=".war",
			repository="DX-MARS")

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/RCTEST-1/eventscheduler_REV_13434_BUILD_12_MarsDayX_RCTEST-1.war", deploy.getArtifactoryUrl())

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE, 
			branch="trunk",
			extension=".war",
			repository="DX-MARS")

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", deploy.getArtifactoryUrl())

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS, 
			service=self.__SERVICE, 
			branch="",
			extension=".war",
			repository="DX-MARS")

		self.assertEqual("http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", deploy.getArtifactoryUrl())


	def test_getArtefactoryManager(self):

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=".war",
			repository="DX-MARS")
		self.assertIsNotNone(deploy.getArtefactoryManager())


	def test_runCommand(self):
		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=".war",
			repository="DX-MARS")
		self.assertIsNotNone(deploy.runCommand("curl -X GET {0}".format(self.__SETTINGS_URL)))
		self.assertIsNotNone(deploy.runCommand("curl -X GET {0}".format(self.__SETTINGS_URL))["stdout"])

	def test_getSettings(self):
		data = {"stdout": """environment,host,ip,target
								DEV,ldgrvapifrmd001,10.35.104.27,/apps/tomcat7/webapps/
								UAT,ldgrvapifrmu001,10.35.108.40,/apps/tomcat7/webapps/
								PROD,ldsrvapifrmp001,10.33.22.27,/apps/tomcat7/webapps/
								PROD,ldsrvapifrmp002,10.33.22.28,/apps/tomcat7/webapps/
								PROD,ldsrvapifrmp003,10.33.22.29,/apps/tomcat7/webapps/
								PROD,ldsrvapifrmp004,10.33.22.30,/apps/tomcat7/webapps/""",
								"stderr" : "",
								"returncode": 0
							}

		deploy = Deploy()
		deploy.runCommand = MagicMock(return_value=data)

		self.assertIsNotNone(deploy.getSettings())

	def test_getNodes(self):
		data = defaultdict(list, {
			'PROD': [{'environment': 'PROD', 'ip': '10.33.22.27', 'host': 'ldsrvapifrmp001', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.28', 'host': 'ldsrvapifrmp002', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.29', 'host': 'ldsrvapifrmp003', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.30', 'host': 'ldsrvapifrmp004', 'target': '/apps/tomcat7/webapps/'}], 
			'UAT': [{'environment': 'UAT', 'ip': '10.35.108.40', 'host': 'ldgrvapifrmu001', 'target': '/apps/tomcat7/webapps/'}], 
			'DEV': [{'environment': 'DEV', 'ip': '10.35.104.27', 'host': 'ldgrvapifrmd001', 'target': '/apps/tomcat7/webapps/'}]})


		deploy = Deploy(environment="DEV")
		deploy.getSettings = MagicMock(return_value=data)


		self.assertIsNotNone(deploy.getNodes())
		self.assertEqual(1, len(deploy.getNodes()))


	def test_execute(self):
		data_runCommand = {"stdout": "OK", "stderr": "", "returncode" : 0}
		data_getNodes = [{'environment': 'PROD', 'ip': '10.33.22.27', 'host': 'ldsrvapifrmp001', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.28', 'host': 'ldsrvapifrmp002', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.29', 'host': 'ldsrvapifrmp003', 'target': '/apps/tomcat7/webapps/'}, 
				{'environment': 'PROD', 'ip': '10.33.22.30', 'host': 'ldsrvapifrmp004', 'target': '/apps/tomcat7/webapps/'}]
		data_getArtifactoryUrl = "http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war"

		deploy = Deploy(environment="SIT", service="eventscheduler", extension=".war")
		deploy.runCommand = MagicMock(return_value = data_runCommand)
		deploy.getNodes = MagicMock(return_value = data_getNodes)
		deploy.getArtifactoryUrl = MagicMock(return_value = data_getArtifactoryUrl)


		output = deploy.execute()
		self.assertEqual(0, output["returncode"])
		with patch('sys.stdout', new=StringIO()) as fakeOutput:
			deploy.execute()
			stringShouldBe = "mco rpc -F ipaddress=\"/(^10.33.22.27$|^10.33.22.28$|^10.33.22.29$|^10.33.22.30$)/\" dx_mars_eventscheduler  deploy url='http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war' package='eventscheduler.war' target='/apps/tomcat7/webapps/'"
			assert fakeOutput.getvalue().strip().find(stringShouldBe) != -1



		
if __name__ == "__main__":
	unittest.main()
#!python2.7


import unittest, sys, os
from StringIO import StringIO
from collections import defaultdict
from mock import patch, MagicMock, call
import mock

from mco_deploy_eventschedulerClass import Deploy
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

	@patch("mco_deploy_eventschedulerClass.sb.Popen")
	def test_runCommand(self, mock_sb):
		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = ("downloaded", "")


		deploy = Deploy(package="eventscheduler.war", 
			url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
			systemService="tomcat7", 
			target="/apps/tomcat7/webapps/")

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
			result = deploy.runCommand("curl -X GET http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")
			mock_shlex.split.assert_called_with("curl -X GET http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")

	@patch("mco_deploy_eventschedulerClass.sb.Popen")
	def test_downloadPackage(self, mock_sb):
		mock_sb.return_value.returncode = 1
		mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
		deploy = Deploy(package="eventscheduler.war", 
			url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
			systemService="tomcat7", 
			target="/apps/tomcat7/webapps/")

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
			deploy.downloadPackage()
			mock_shlex.split.assert_called_with("curl -sS -o /apps/tomcat7/webapps/eventscheduler.war http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")

	
	@patch("mco_deploy_eventschedulerClass.sb.Popen")
	def test_cleanUp(self, mock_sb):
		mock_sb.return_value.returncode = 1
		mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
		deploy = Deploy(package="eventscheduler.war", 
			url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
			systemService="tomcat7", 
			target="/apps/tomcat7/webapps/")

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
			deploy.cleanUp()
			mock_shlex.split.assert_called_with("rm -f /apps/tomcat7/webapps/eventscheduler.war")

	
	@patch("mco_deploy_eventschedulerClass.sb.Popen")
	def test_cleanUp(self, mock_sb):
		mock_sb.return_value.returncode = 1
		mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
		deploy = Deploy(package="eventscheduler.war", 
			url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
			systemService="tomcat7", 
			target="/apps/tomcat7/webapps/")

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
			deploy.restartService()
			mock_shlex.split.assert_called_with("service tomcat7 restart")

	
	@patch("mco_deploy_eventschedulerClass.sb.Popen")
	def test_execute(self, mock_sb):
		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = ("downloaded", "")

		calls = [
				call.split("rm -f /apps/tomcat7/webapps/eventscheduler.war"), 
				call.split("curl -sS -o /apps/tomcat7/webapps/eventscheduler.war http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war"),
				call.split("service tomcat7 restart"),
			]

		deploy = Deploy(package="eventscheduler.war", 
			url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
			systemService="tomcat7", 
			target="/apps/tomcat7/webapps/")

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
			deploy.execute()
			mock_shlex.assert_has_calls(calls, any_order=False)

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.downloadPackage") as mock_downloadPackage:

			with self.assertRaises(Exception) as context:
				mock_downloadPackage = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
				deploy.execute()	

			self.assertTrue("self.downloadPackage().returncode != 0" in context.exception)	

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.restartService") as mock_restartService:

			with self.assertRaises(Exception) as context:
				mock_restartService = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
				deploy.execute()

			self.assertTrue("self.restartService().returncode != 0" in context.exception)

		with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.cleanUp") as mock_cleanUp:

			with self.assertRaises(Exception) as context:
				mock_cleanUp = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
				deploy.execute()

			self.assertTrue("self.cleanUp().returncode != 0" in context.exception)
			


			


			
			# mock_shlex.assert_has_calls(calls, any_order=False)



		
if __name__ == "__main__":
	unittest.main() 

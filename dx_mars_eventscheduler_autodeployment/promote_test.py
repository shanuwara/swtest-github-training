#!python2.7


import unittest, sys, os
# sys.path.append(os.getcwd())

from StringIO import StringIO
from collections import defaultdict
import mock
from mock import patch, MagicMock, call
import __builtin__


from promote import Promote
# from cqm_libs.artefactory import artefactory


class PromoteCase(unittest.TestCase):

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

	# @patch("mco_deploy_eventschedulerClass.sb.Popen")
	# def test_runCommand(self, mock_sb):
	# 	mock_sb.return_value.returncode = 0
	# 	mock_sb.return_value.communicate.return_value = ("downloaded", "")


	# 	deploy = Deploy(package="eventscheduler.war", 
	# 		url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
	# 		systemService="tomcat7", 
	# 		target="/apps/tomcat7/webapps/")

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
	# 		result = deploy.runCommand("curl -X GET http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")
	# 		mock_shlex.split.assert_called_with("curl -X GET http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")

	# @patch("mco_deploy_eventschedulerClass.sb.Popen")
	# def test_downloadPackage(self, mock_sb):
	# 	mock_sb.return_value.returncode = 1
	# 	mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
	# 	deploy = Deploy(package="eventscheduler.war", 
	# 		url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
	# 		systemService="tomcat7", 
	# 		target="/apps/tomcat7/webapps/")

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
	# 		deploy.downloadPackage()
	# 		mock_shlex.split.assert_called_with("curl -sS -o /apps/tomcat7/webapps/eventscheduler.war http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war")

	
	# @patch("mco_deploy_eventschedulerClass.sb.Popen")
	# def test_cleanUp(self, mock_sb):
	# 	mock_sb.return_value.returncode = 1
	# 	mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
	# 	deploy = Deploy(package="eventscheduler.war", 
	# 		url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
	# 		systemService="tomcat7", 
	# 		target="/apps/tomcat7/webapps/")

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
	# 		deploy.cleanUp()
	# 		mock_shlex.split.assert_called_with("rm -f /apps/tomcat7/webapps/eventscheduler.war")

	
	# @patch("mco_deploy_eventschedulerClass.sb.Popen")
	# def test_cleanUp(self, mock_sb):
	# 	mock_sb.return_value.returncode = 1
	# 	mock_sb.return_value.communicate.return_value = ("downloaded", "")
	
	# 	deploy = Deploy(package="eventscheduler.war", 
	# 		url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
	# 		systemService="tomcat7", 
	# 		target="/apps/tomcat7/webapps/")

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
	# 		deploy.restartService()
	# 		mock_shlex.split.assert_called_with("service tomcat7 restart")

	
	# @patch("mco_deploy_eventschedulerClass.sb.Popen")
	# def test_execute(self, mock_sb):
	# 	mock_sb.return_value.returncode = 0
	# 	mock_sb.return_value.communicate.return_value = ("downloaded", "")

	# 	calls = [
	# 			call.split("rm -f /apps/tomcat7/webapps/eventscheduler.war"), 
	# 			call.split("curl -sS -o /apps/tomcat7/webapps/eventscheduler.war http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war"),
	# 			call.split("service tomcat7 restart"),
	# 		]

	# 	deploy = Deploy(package="eventscheduler.war", 
	# 		url="http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_17026_BUILD_14_trunk.war", 
	# 		systemService="tomcat7", 
	# 		target="/apps/tomcat7/webapps/")

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex:
	# 		deploy.execute()
	# 		mock_shlex.assert_has_calls(calls, any_order=False)

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.downloadPackage") as mock_downloadPackage:

	# 		with self.assertRaises(Exception) as context:
	# 			mock_downloadPackage = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
	# 			deploy.execute()	

	# 		self.assertTrue("self.downloadPackage().returncode != 0" in context.exception)	

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.restartService") as mock_restartService:

	# 		with self.assertRaises(Exception) as context:
	# 			mock_restartService = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
	# 			deploy.execute()

	# 		self.assertTrue("self.restartService().returncode != 0" in context.exception)

	# 	with patch("mco_deploy_eventschedulerClass.shlex") as mock_shlex, patch("mco_deploy_eventschedulerClass.Deploy.cleanUp") as mock_cleanUp:

	# 		with self.assertRaises(Exception) as context:
	# 			mock_cleanUp = MagicMock(return_value = {"returncode":1, "stderr": "stderr", "stdout": "stdout"})
	# 			deploy.execute()

	# 		self.assertTrue("self.cleanUp().returncode != 0" in context.exception)
			


			


			
	# 		# mock_shlex.assert_has_calls(calls, any_order=False)

	@patch("promote.sb.Popen")
	def test_getArtefactoryManager(self, mock_sb):
		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = ("downloaded", "")
		promote = Promote(
			ARTIUSER="artiuser", 
			ARTIPASS="artipass", 
			ARTISERVER="http://10.33.20.7:8080",
			extension=".war", 
			repository="DX-MARS", 
			service="eventscheduler",
			branch="trunk",
			rc="RCTEST-4")
		self.assertIsNotNone(promote.getArtefactoryManager)


	@patch("promote.sb.Popen")
	def test_getArtifactoryUrl(self, mock_sb):
		response = """{
				  "results" : [ {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_12338_BUILD_11_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_12_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_13_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_1026_BUILD_14_trunk.war"
				  } ]
				}"""

		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = (response, "")
		promote = Promote(
			ARTIUSER="artiuser", 
			ARTIPASS="artipass", 
			ARTISERVER="http://10.33.20.7:8080",
			extension=".war", 
			repository="DX-MARS", 
			service="eventscheduler",
			branch="trunk",
			rc="RCTEST-4")

		with patch("cqm_libs.artefactory.shlex") as mock_shlex:
		
			url = promote.getArtifactoryUrl(fromTrunk=True)
			mock_shlex.split.assert_called_with("curl -s -X GET -u artiuser:artipass  http://10.33.20.7:8080/artifactory/api/search/artifact?name=eventscheduler_REV_*_BUILD_*_trunk.war&repos=DX-MARS")
			self.assertIsNotNone(url)
			self.assertEquals("http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_13_trunk.war", url)

		with patch("cqm_libs.artefactory.shlex") as mock_shlex:
		
			url = promote.getArtifactoryUrl(fromTrunk=False)
			mock_shlex.split.assert_called_with("curl -s -X GET -u artiuser:artipass  http://10.33.20.7:8080/artifactory/api/search/artifact?name=eventscheduler_REV_*_BUILD_*_trunk_RCTEST-4.war&repos=DX-MARS")
			self.assertIsNotNone(url)
			self.assertEquals("http://10.33.20.7:8080/artifactory/DX-MARS/RCTEST-4/eventscheduler_REV_13434_BUILD_13_trunk.war", url)





	


	@patch("promote.sb.Popen")
	def test_execute(self, mock_sb):
		response = """{
				  "results" : [ {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_12338_BUILD_11_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_12_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_13_trunk.war"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/eventscheduler_REV_1026_BUILD_14_trunk.war"
				  } ]
				}"""

		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = (response, "")

		promote = Promote(
			ARTIUSER="artiuser", 
			ARTIPASS="artipass", 
			ARTISERVER="http://10.33.20.7:8080",
			extension=".war", 
			repository="DX-MARS", 
			service="eventscheduler",
			branch="trunk",
			rc="RCTEST-4")

		calls = [
		call.split("curl -s -X GET -u artiuser:artipass  http://10.33.20.7:8080/artifactory/api/search/artifact?name=eventscheduler_REV_*_BUILD_*_trunk.war&repos=DX-MARS"),
		call.split("curl -s -X GET -u artiuser:artipass http://10.33.20.7:8080/artifactory/DX-MARS/trunk/eventscheduler_REV_13434_BUILD_13_trunk.war -o eventscheduler_REV_13434_BUILD_13_trunk_RCTEST-4.war"),
		call.split("curl -s -D- -X PUT -u artiuser:artipass http://10.33.20.7:8080/artifactory/simple/DX-MARS/RCTEST-4/ -T eventscheduler_REV_13434_BUILD_13_trunk_RCTEST-4.war -H 'X-Checksum-Md5: 2' -H 'X-Checksum-Sha1: 1'"),
		]

		with patch("promote.shlex") as mock_shlex1, patch("cqm_libs.artefactory.shlex") as mock_shlex2:
			with patch("__builtin__.open") as mock_open:
				with patch("cqm_libs.artefactory.hashlib") as mock_hashlib:
					mock_hashlib.sha1.return_value.hexdigest = MagicMock(return_value="1")
					mock_hashlib.md5.return_value.hexdigest = MagicMock(return_value="2")
					
					promote.execute()
					mock_shlex2.assert_has_calls(calls, any_order=False)
					


		
if __name__ == "__main__":
	unittest.main() 

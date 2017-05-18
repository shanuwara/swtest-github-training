#!python2.7 -u


import unittest, sys, os
from StringIO import StringIO
from collections import defaultdict
from mock import patch, call
from mock import MagicMock
import mock
import json

from deploy import Deploy
sys.path.append('../cqm_libs')
from artefactory import artefactory


class DeploymentCase(unittest.TestCase):

	previous = False

	def setUp(self):
		self.__ARTISERVER = "http://10.33.20.7:8080"
		self.__ARTIUSER = "user2"
		self.__ARTIPASS = "pass2"
		self.__SERVICE = "RetailSportsbookPublisher20"
		self.__ENVIRONMENT = "DEV"
		self.__RC = "RCTEST-1"
		self.__BRANCH = "MarsDayX"
		self.__SETTINGS_URL = "http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/DX_MARS_environments.csv"
		self.__SVNUSER = "user1"
		self.__SVNPASS = "password1"
		self.__EXTENSION = ".zip"


	@patch("deploy.sb.Popen")
	def test_getArtifactoryUrl(self, mock_sb):
		response = """{
				  "results" : [ {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/RetailSportsbookPublisher20_REV_12338_BUILD_11_trunk.zip"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/RetailSportsbookPublisher20_REV_13434_BUILD_12_trunk.zip"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/RetailSportsbookPublisher20_REV_13434_BUILD_13_trunk.zip"
				  }, {
				    "uri" : "http://10.33.20.7:8080/artifactory/api/storage/DX-MARS/trunk/RetailSportsbookPublisher20_REV_1026_BUILD_14_trunk.zip"
				  } ]
				}"""

		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate.return_value = (response, "")
		deploy = Deploy(
			ARTIUSER="artiuser", 
			ARTIPASS="artipass", 
			ARTISERVER="http://10.33.20.7:8080", 
			repository="DX-MARS", 
			service="RetailSportsbookPublisher20",
			branch="trunk",
			rc="RCTEST-3",
			extension=self.__EXTENSION)

		with patch("cqm_libs.artefactory.shlex") as mock_shlex:
		
			url = deploy.getArtifactoryUrl(fromTrunk=True)
			mock_shlex.split.assert_called_with("curl -s -X GET -u artiuser:artipass  http://10.33.20.7:8080/artifactory/api/search/artifact?name=RetailSportsbookPublisher20_REV_*_BUILD_*_trunk.zip&repos=DX-MARS")
			self.assertIsNotNone(url)
			self.assertEquals("http://10.33.20.7:8080/artifactory/DX-MARS/trunk/RetailSportsbookPublisher20_REV_13434_BUILD_13_trunk.zip", url)

		with patch("cqm_libs.artefactory.shlex") as mock_shlex:
		
			url = deploy.getArtifactoryUrl(fromTrunk=False)
			mock_shlex.split.assert_called_with("curl -s -X GET -u artiuser:artipass  http://10.33.20.7:8080/artifactory/api/search/artifact?name=RetailSportsbookPublisher20_REV_*_BUILD_*_trunk_RCTEST-3.zip&repos=DX-MARS")
			self.assertIsNotNone(url)
			self.assertEquals("http://10.33.20.7:8080/artifactory/DX-MARS/RCTEST-3/RetailSportsbookPublisher20_REV_13434_BUILD_13_trunk.zip", url)


	def test_getArtefactoryManager(self):

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=self.__EXTENSION,
			repository="DX-MARS")
		self.assertIsNotNone(deploy.getArtefactoryManager())


	def test_runCommand(self):
		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=self.__EXTENSION,
			repository="DX-MARS")
		with patch("deploy.sb.Popen") as mock_sb:
			mock_sb.return_value.communicate = MagicMock(return_value = {"stdout":"output", "stderr":"errors"})
			mock_sb.return_value.returncode = 0
			self.assertIsNotNone(deploy.runCommand("curl -s -X GET {0}".format(self.__SETTINGS_URL)))
			self.assertIsNotNone(deploy.runCommand("curl -s -X GET {0}".format(self.__SETTINGS_URL))["stdout"])


	def test_getSettings(self):
		data = {"stdout": """environment,host,ip
							RL_PROD1,ukrliccprodadm01,10.192.242.19
							RL_PROD2,ukrliccprodadm02,10.192.242.20
							LS_DEV,ldgrvtibadmd001,10.35.104.17
							LS_UAT,ldgrvtibadmu001,10.35.108.30
							LS_SIT,ldgrvtibadmi001,10.35.106.54
							LS_PREPROD1,ldgrvtibadmr001,10.35.16.38
							LS_PREPROD2,ldgrvtibadmr002,10.35.16.39
							LS_PERF1,ldgrvtibadml001,10.35.16.113
							LS_PERF2,ldgrvtibadml002,10.35.16.114
							SW_PROD1,ldsrvtibadmp001,10.33.4.36
							CQM_PROD,ldgrvtibadmu001,10.35.108.30
							SW_PROD2,ldsrvtibadmp002,10.33.4.37""",
								"stderr" : "",
								"returncode": 0
							}

		deploy = Deploy()
		deploy.runCommand = MagicMock(return_value=data)

		self.assertIsNotNone(deploy.getSettings())

	def test_getNodes(self):
		data = defaultdict(list, {'RL_PROD2': [{'environment': 'RL_PROD2', 'ip': '10.192.242.20', 'host': 'ukrliccprodadm02'}], 0: [], 'RL_PROD1': [{'environment': 'RL_PROD1', 'ip': '10.192.242.19', 'host': 'ukrliccprodadm01'}], 'LS_UAT': [{'environment': 'LS_UAT', 'ip': '10.35.108.30', 'host': 'ldgrvtibadmu001'}], 1: [], 'SW_PROD2': [{'environment': 'SW_PROD2', 'ip': '10.33.4.37', 'host': 'ldsrvtibadmp002'}], 'LS_SIT': [{'environment': 'LS_SIT', 'ip': '10.35.106.54', 'host': 'ldgrvtibadmi001'}], 'SW_PROD1': [{'environment': 'SW_PROD1', 'ip': '10.33.4.36', 'host': 'ldsrvtibadmp001'}], 'CQM_PROD': [{'environment': 'CQM_PROD', 'ip': '10.35.108.30', 'host': 'ldgrvtibadmu001'}], 'LS_PERF1': [{'environment': 'LS_PERF1', 'ip': '10.35.16.113', 'host': 'ldgrvtibadml001'}], 'LS_PERF2': [{'environment': 'LS_PERF2', 'ip': '10.35.16.114', 'host': 'ldgrvtibadml002'}], 'LS_PREPROD1': [{'environment': 'LS_PREPROD1', 'ip': '10.35.16.38', 'host': 'ldgrvtibadmr001'}], 'LS_DEV': [{'environment': 'LS_DEV', 'ip': '10.35.104.17', 'host': 'ldgrvtibadmd001'}], 'LS_PREPROD2': [{'environment': 'LS_PREPROD2', 'ip': '10.35.16.39', 'host': 'ldgrvtibadmr002'}]})


		deploy = Deploy(environment="LS_UAT")
		deploy.getSettings = MagicMock(return_value=data)


		self.assertIsNotNone(deploy.getNodes())
		self.assertEqual(1, len(deploy.getNodes()))


	def test_getConfigUrl(self):
		conf = """[
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
			      }
			    ]"""

		conf2 = """[
					  {
					    "service": "RetailSportsbookPublisher20",
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
					      }
					    ],
					    "build": [
					      {
					        "branch": "trunk",
					        "codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20"

					      }
					    ]
					  }
					]"""

		
		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=self.__EXTENSION,
			repository="DX-MARS",
			environment="LS_SIT"
			)
		
		
		with patch("deploy.Configuration.runCommand") as mock_runCommand:
			mock_runCommand.return_value = {"returncode":0, "stdout":conf2, "stderr":""}
			print "url", deploy.getConfigUrl(url="test")

		




	@patch("deploy.sb.Popen")
	def test_execute(self, mock_sb):
	
		mock_sb.return_value.returncode = 0
		mock_sb.return_value.communicate = MagicMock(return_value = ("stdout", ""))

		data_getArtifactoryUrl = "http://10.33.20.7:8080/artifactory/DX-MARS/TESTRC-3/RetailSportsbookPublisher20_REV_17026_BUILD_14_trunk.zip"

		data_getNodes = [{'environment': 'LS_SIT', 'ip': '10.35.106.54', 'host': 'ldgrvtibadmi001'},
						{'environment': 'LS_SIT', 'ip': '10.35.106.55', 'host': 'ldgrvtibadmi002'}]

		conf2 = """[
					  {
					    "service": "RetailSportsbookPublisher20",
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
					      }
					    ],
					    "build": [
					      {
					        "branch": "trunk",
					        "codebase_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20"

					      }
					    ]
					  }
					]"""						

		deploy = Deploy(ARTISERVER=self.__ARTISERVER, 
			ARTIUSER=self.__ARTIUSER, 
			ARTIPASS=self.__ARTIPASS,
			service=self.__SERVICE, 
			rc=self.__RC,
			extension=self.__EXTENSION,
			repository="DX-MARS",
			environment="LS_SIT"
			)

		deploy.setBuildNumber(5000)
		# deploy.runCommand = MagicMock(return_value = data_runCommand)
		deploy.getNodes = MagicMock(return_value = data_getNodes)
		deploy.getArtifactoryUrl = MagicMock(return_value = data_getArtifactoryUrl)

		calls = [
			call.split("""ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@10.35.106.54 -C \"set -x; rm -rf /opt/tibco/release_backup/5000/; mkdir -p /opt/tibco/release_backup/5000/; mkdir -p /opt/tibco/applications/devops/deploy/ems/; mkdir -p /opt/tibco/applications/devops/deploy/couchbase/; cp -r /opt/tibco/applications/devops/deploy/ear/ /opt/tibco/release_backup/5000/; cp -r /opt/tibco/applications/devops/deploy/cfg/ /opt/tibco/release_backup/5000/; cp -r /opt/tibco/applications/devops/deploy/ems/ /opt/tibco/release_backup/5000/; cp -r /opt/tibco/applications/devops/deploy/couchbase/ /opt/tibco/release_backup/5000/\""""),
			call.split("""ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@10.35.106.54 -C \"rm -rf /opt/tibco/cqm_eis_deployment; mkdir -p /opt/tibco/cqm_eis_deployment\""""),
			call.split("""scp -i /home/jenkinsci/.ssh/tibco_id_rsa RetailSportsbookPublisher20_REV_17026_BUILD_14_trunk.zip tibco@10.35.106.54:/opt/tibco/cqm_eis_deployment"""),
			call.split("""ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@10.35.106.54 -C \"zip -d /opt/tibco/cqm_eis_deployment/RetailSportsbookPublisher20_REV_17026_BUILD_14_trunk.zip cfg/* -x cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg\""""),
			call.split("""ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@10.35.106.54 -C \"cd /opt/tibco/cqm_eis_deployment; unzip RetailSportsbookPublisher20_REV_17026_BUILD_14_trunk.zip; cp *.ear  /opt/tibco/applications/devops/deploy/ear/; cp cfg/*.cfg  /opt/tibco/applications/devops/deploy/cfg/;\""""),
			call.split("""ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@10.35.106.54 -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh RetailSportsbookPublisher20 2>&1;\"""")


		]


		with patch("deploy.shlex") as mock_shlex, patch("deploy.Configuration.runCommand") as mock_runCommand:
			mock_runCommand.return_value = {"returncode":0, "stdout":conf2, "stderr":""}
			output = deploy.execute()
			mock_shlex.assert_has_calls(calls, any_order=False)
			# print output
			



		
if __name__ == "__main__":
	unittest.main() 


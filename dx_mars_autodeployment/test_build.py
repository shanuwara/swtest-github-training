#!python2.7

import os, sys, unittest, shlex
from mock import patch, MagicMock, Mock

class DTL:
	def __init__(self, filename, source, directory):
		self.source = source
		self.directory = directory
		self.file = os.path.join(self.directory, filename)


os.environ["WORKSPACE"] = os.getcwd()

sys.modules['DesignTimeParser.DesignTimeParser'] = Mock()
sys.modules['custom_field_editor'] = Mock()
sys.modules['custom_field_editor.CustomFieldEditor'] = Mock()
sys.modules['cqm_libs'] = Mock()
sys.modules['cqm_libs.artefactory'] = Mock()
sys.modules['cqm_libs.jira'] = Mock()



from build import Build, DTL


class BuildTest(unittest.TestCase):
	def setUp(self):
		self.json = """[
  {
    "service": "RetailSportsbookPublisher20",
    "deployment": [
      {
        "env": "LS_PERF1",
        "config_url": "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg",
        "domain": "eisperf",
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

	@patch("ServiceConfiguration1.ServiceConfiguration.Configuration.runCommand")
	# @patch("build.sb")
	def test_getCode(self, mock_runCommand):
		mock_runCommand.return_value = return_value = {"returncode":0, "stderr":"", "stdout":self.json}
		#mock_sb.Popen.return_value.returncode  =  0#MagicMock(return_value={"returncode":0, "stdout": "stdout", "stderr":"stderr"})

		libs = DTL("filename", "source", "directory")

		
		Build.cleanBuildFolder = Mock()
		


		build = Build(workspace = os.getcwd(), 
			service="RetailSportsbookPublisher20", 
			repository="repository", 
			dtl=libs, 
			target="target", 
			branch="trunk")

		build.setSubversionCredentials(username="user", password="pass")

		with patch("build.sb") as mock_sb, patch("build.shlex") as mock_shlex:
			mock_sb.Popen.return_value.returncode = 1
			build.getCode("url")
			mock_shlex.split.assert_called_with("svn export --force --non-interactive --username={0} --password={1} {2} {3}".format("user", "pass", "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Code/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20", "target/code"))


		
	@patch("ServiceConfiguration1.ServiceConfiguration.Configuration.runCommand")
	def test_getConfigs(self, mock_runCommand):
		mock_runCommand.return_value = return_value = {"returncode":0, "stderr":"", "stdout":self.json}

		libs = DTL("filename", "source", "directory")
		Build.cleanBuildFolder = Mock()

		build = Build(workspace = os.getcwd(), 
			service="RetailSportsbookPublisher20", 
			repository="repository", 
			dtl=libs, 
			target="target", 
			branch="trunk")

		build.setSubversionCredentials(username="user", password="pass")
		with patch("build.sb") as mock_sb, patch("build.shlex") as mock_shlex:
			mock_sb.Popen.return_value.returncode = 1
			build.getConfigs("url")
			mock_shlex.split.assert_called_with("svn export --force --non-interactive --username={0} --password={1} {2} {3}".format("user", "pass", "http://10.33.20.5:8080/svn/DX/DX/trunk/Development/Build/Bw/Technical/Retails/RetailSportsbookPublisher/2.0/RetailSportsbookPublisher20/cfg/RetailSportsbookPublisher20-LeedsSITEAI.cfg", "target/cfg"))





if __name__ == "__main__":
	unittest.main()
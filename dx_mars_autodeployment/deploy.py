#!python2.7 -u


import sys, os
sys.path.append(os.getcwd())

import subprocess as sb
import shlex
# from custom_field_editor.CustomFieldEditor import CustomFieldManager as CFM
from cqm_libs.artefactory import artefactory
from cqm_libs.jira import jira
from ServiceConfiguration1.ServiceConfiguration import Configuration
from collections import defaultdict
import csv, StringIO
#from paramiko import SSHClient
#import paramiko


class Deploy:
		def __init__(self, **kwargs):
			print "[FUNC]", sys._getframe().f_code.co_name
			self.__JIRAKEY = kwargs.pop('JIRAKEY', None)
			self.__JIRAUSER = kwargs.pop('JIRAUSER', None)
			self.__JIRAPASS = kwargs.pop('JIRAPASS', None)
			self.__SVN_SCRIPTS = kwargs.pop('SVN_SCRIPTS', None)
			self.__REPOSITORY = kwargs.pop('repository', None)
			self.__RC = kwargs.pop("rc", None)
			self.__EXTENSION = kwargs.pop("extension", None)
			self.__SERVICE = kwargs.pop("service", None)
			self.__ENVIRONMENT = kwargs.pop("environment", None)

			self.__ARTISERVER = kwargs.pop('ARTISERVER', None)
			self.__ARTIUSER = kwargs.pop('ARTIUSER', None)
			self.__ARTIPASS = kwargs.pop('ARTIPASS', None)

			self.__SVNUSER = kwargs.pop('SVNUSER', None)
			self.__SVNPASS = kwargs.pop('SVNPASS', None)

			self.__SETTINGS_URL = kwargs.pop('SETTINGS_URL', None)

			self.__PROJECT = "DX"

			self.__BUILDNUMBER = 0

		
			self.__BuildFolder = kwargs.pop("target", None)


			self.__SERVICE_CONFIGURATION_URL = "http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/services.json"

			self.__SSH_KEY = "/home/jenkinsci/.ssh/tibco_id_rsa"
			self.__SSH_USER = "tibco"


			self.__BRANCH = kwargs.pop("branch", None)
			self.__BRANCH = "trunk" if self.__BRANCH == None else self.__BRANCH

			self.TYPE_ALL = 1
			self.TYPE_SINGLE = 0

			self.__DEBUG = kwargs.pop("debug", False)

		def getSSHManager(self, ip):
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			# client.load_system_host_keys()
			client.connect(ip, username=self.__SSH_USER, key_filename=self.__SSH_KEY)
			return client

		def setBuildNumber(self, number):
			print "[FUNC]", sys._getframe().f_code.co_name
			self.__BUILDNUMBER = number

		def setSubversionCredentials(self, username, password):
			print "[FUNC]", sys._getframe().f_code.co_name
			self.__SVNUSER = username
			self.__SVNPASS = password


		def getConfigurationManager(self):
			print "[FUNC]", sys._getframe().f_code.co_name
			return Configuration(SVNUSER=self.__SVNUSER, SVNPASS=self.__SVNPASS, URL=self.__SERVICE_CONFIGURATION_URL)

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


		def getArtefactoryManager(self):
			print "[FUNC]", sys._getframe().f_code.co_name
			if self.__ARTISERVER is None or self.__ARTIUSER is None or self.__ARTIPASS is None:
				return None

			artefactoryManager = artefactory(server=self.__ARTISERVER,userName=self.__ARTIUSER,password=self.__ARTIPASS)
			return artefactoryManager

		def runCommand(self, command):
			print "[FUNC]", sys._getframe().f_code.co_name

			if self.__DEBUG == True:
				print "[DEBUG]", command

			proc = sb.Popen(shlex.split(command), stdout=sb.PIPE, stderr=sb.PIPE)
			stdout, stderr = proc.communicate()
			output = {"returncode": proc.returncode, "stdout": stdout, "stderr": stderr}
			return output

		def removeMotd(self, data):
			if data == "":
				return ""
			tmp = data.split("\n+")
			del tmp[0]
			tmp = "\n+".join(tmp)
			return tmp


		def getSettings(self):
			print "[FUNC]", sys._getframe().f_code.co_name
			cmd = "curl -u {0}:{1} -X GET {2}".format(self.__SVNUSER, self.__SVNPASS, self.__SETTINGS_URL)
			output = self.runCommand(cmd)
			
			if output["returncode"] != 0 or output["stdout"] is None or output["stdout"] == "":
				return None

			lines = defaultdict(list)
			if self.__DEBUG == True:
				print output["stdout"]

			reader = csv.DictReader(StringIO.StringIO(output["stdout"]))
			for line in reader:
				print line
				lines[line["environment"]].append(line)
			return lines

		def getNodes(self):
			print "[FUNC]", sys._getframe().f_code.co_name
			settings = self.getSettings()
			return settings[self.__ENVIRONMENT]

		def backup(self, parameters):
			print "[FUNC]", sys._getframe().f_code.co_name
			command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@{ip} -C \"set -x; rm -rf {backup_dir}; mkdir -p {backup_dir}; mkdir -p {ems_dir}; mkdir -p {couchbase_dir}; cp -r {ear_dir} {backup_dir}; cp -r {cfg_dir} {backup_dir}; cp -r {ems_dir} {backup_dir}; cp -r {couchbase_dir} {backup_dir}\"".format( **parameters )
			
			output = self.runCommand(command)
			# output["stderr"] = self.removeMotd(output["stderr"])

			# client = self.getSSHManager(parameters["ip"])
			# stdin, stdout, stderr = client.exec_command("set -x; rm -rf {backup_dir}; mkdir -p {backup_dir}; mkdir -p {ems_dir}; mkdir -p {couchbase_dir}; cp -r {ear_dir} {backup_dir}; cp -r {cfg_dir} {backup_dir}; cp -r {ems_dir} {backup_dir}; cp -r {couchbase_dir} {backup_dir}".format( **parameters ))
			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}


			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))

			# client.close()

			return output

		def cleanup(self, parameters):
			print "[FUNC]", sys._getframe().f_code.co_name
			command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@{ip} -C \"rm -rf /opt/tibco/cqm_eis_deployment; mkdir -p /opt/tibco/cqm_eis_deployment\"".format(**parameters)
			output = self.runCommand(command)
			# output["stderr"] = self.removeMotd(output["stderr"])

			# client = self.getSSHManager(parameters["ip"])
			# stdin, stdout, stderr = client.exec_command("rm -rf /opt/tibco/cqm_eis_deployment; mkdir -p /opt/tibco/cqm_eis_deployment".format( **parameters ))

			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}

			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))

			# client.close()

			return output

		def deploy(self, parameters):
			print "[FUNC]", sys._getframe().f_code.co_name

			outputs = []
			command = "scp -i /home/jenkinsci/.ssh/tibco_id_rsa {package} tibco@{ip}:/opt/tibco/cqm_eis_deployment".format(**parameters)
			output = self.runCommand(command)

			outputs.append(output)
			# output["stderr"] = self.removeMotd(output["stderr"])

			# client = self.getSSHManager(parameters["ip"])
			# sftp = client.open_sftp()
			# sftp.put(parameters["package"], "/opt/tibco/cqm_eis_deployment")
			# sftp.close()

			# stdin, stdout, stderr = client.exec_command("rm -rf /opt/tibco/cqm_eis_deployment; mkdir -p /opt/tibco/cqm_eis_deployment".format( **parameters ))
			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}


			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))


			command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@{ip} -C \"zip -d /opt/tibco/cqm_eis_deployment/{package} cfg/* -x cfg/{conf_file}\"".format(**parameters)
			output = self.runCommand(command)

			outputs.append(output)
			# output["stderr"] = self.removeMotd(output["stderr"])

			# client = getSSHManager(parameters["ip"])
			# stdin, stdout, stderr = client.exec_command("zip -d /opt/tibco/cqm_eis_deployment/{package} cfg/* -x cfg/{conf_file}".format( **parameters ))
			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}


			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))


			command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@{ip} -C \"cd /opt/tibco/cqm_eis_deployment; unzip {package}; cp *.ear  {ear_dir}; cp cfg/*.cfg  {cfg_dir};\"".format(**parameters)
			output = self.runCommand(command)

			outputs.append(output)
			# output["stderr"] = self.removeMotd(output["stderr"])
			# client = getSSHManager(parameters["ip"])
			# stdin, stdout, stderr = client.exec_command("cd /opt/tibco/cqm_eis_deployment; unzip {package}; cp *.ear  {ear_dir}; cp cfg/*.cfg  {cfg_dir};".format( **parameters ))
			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}



			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))

			command = "ssh -i /home/jenkinsci/.ssh/tibco_id_rsa tibco@{ip} -C \"cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh {service} 2>&1;\"".format(**parameters)
			output = self.runCommand(command)
			# output["stderr"] = self.removeMotd(output["stderr"])

			outputs.append(output)

			# client = getSSHManager(parameters["ip"])
			# stdin, stdout, stderr = client.exec_command("cd /opt/tibco/applications/devops/deploy/bin/; ./deploy.sh {service} 2>&1;".format( **parameters ))
			# output = {"returncode":stdout.channel.recv_exit_status(), "stdout":"".join(stdout.readlines()), "stderr":"".join(stderr.readlines())}


			# if output["returncode"] != 0 or output["stderr"] != "":
				# raise Exception(sys._getframe().f_code.co_name, str(output))

			# client.close()

			return outputs


		def getConfigurationManager(self):
			return Configuration(SVNUSER=self.__SVNUSER, SVNPASS=self.__SVNPASS, URL=self.__SERVICE_CONFIGURATION_URL)


		def setSubversionCredentials(self, username, password):
			print "[FUNC]", sys._getframe().f_code.co_name
			self.__SVNUSER = username
			self.__SVNPASS = password

		def getConfigUrl(self, url):
			print "[FUNC]", sys._getframe().f_code.co_name
			confManager = self.getConfigurationManager()
			conf = confManager.getConfigurationDeployment(service=self.__SERVICE, branch=self.__BRANCH, environment=self.__ENVIRONMENT)
			
			if len(conf) != 1:
				raise Exception("No config for environment found")

			confUrl = conf[0]["config_url"]

			if confUrl is None or confUrl == "":
				raise Exception("Config url is incorrect")

			return confUrl

			# print "getConfigs", conf
			# for item in conf:
			# 	conf_url = item["config_url"]
			# 	self.exportSVN(_url=conf_url, _target= os.path.join(self.__BuildFolder, "cfg"))
			# return self.exportSVN(_url=url, _target=self.__BuildFolder)


		def execute(self):
			print "[FUNC]", sys._getframe().f_code.co_name
			nodes = self.getNodes()
			source = self.getArtifactoryUrl()
			# package = self.__SERVICE + self.__EXTENSION
			package = os.path.basename(source)

			backup_dir = os.path.join("/opt/tibco/release_backup", str(self.__BUILDNUMBER), "")
			ems_dir = "/opt/tibco/applications/devops/deploy/ems/"
			cfg_dir = "/opt/tibco/applications/devops/deploy/cfg/"
			ear_dir = "/opt/tibco/applications/devops/deploy/ear/"
			couchbase_dir = "/opt/tibco/applications/devops/deploy/couchbase/"
			conf_file = os.path.basename(self.getConfigUrl(url=None))

			i = 0
			print nodes
			for node in nodes:
				# print node
			
				ip = node["ip"]
				parameters = {}
				parameters["backup_dir"] = backup_dir
				parameters["ems_dir"] = ems_dir
				parameters["cfg_dir"] = cfg_dir
				parameters["ear_dir"] = ear_dir
				parameters["couchbase_dir"] = couchbase_dir
				parameters["ip"] = ip
				parameters["package"] = package
				parameters["service"] = self.__SERVICE
				parameters["conf_file"] = conf_file

				print "[INFO]", sys._getframe().f_code.co_name, self.backup(parameters)
				print "[INFO]", sys._getframe().f_code.co_name, self.cleanup(parameters)
				print "[INFO]", sys._getframe().f_code.co_name, self.deploy(parameters)

			return False


if __name__ == "__main__":
	pass
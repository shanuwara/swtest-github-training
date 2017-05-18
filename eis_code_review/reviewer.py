import sys
import os
import subprocess as sb
import shlex

directory = os.environ['directory']

# WORKSPACE = '/app/jenkins-slave/EIS_DevOps_buildear'
WORKSPACE = os.environ['WORKSPACE']

BRANCH = None

if "branch" in os.environ:
	BRANCH = os.environ['branch']

branch_folder = "repo"

if BRANCH is not None and len(BRANCH) > 0 and BRANCH != "trunk":
	branch_folder = "branches/" + BRANCH

path = os.path.join('/app/jenkins-slave/workspace/EIS_DevOps_buildear/', branch_folder , directory)
service = directory.split("/")[-2]

"""
EXAMPLE:
 /app/jenkins/java/bin/java -DconfigDir=configuration -Dlog4j.configuration=file:"/app/jenkins-slave/workspace/EIS_DevOps_buildear/tmp/test/quality/configuration/log4j.properties" -jar codereview.jar 
"""

config = open(os.path.join(WORKSPACE, "test/quality/configuration/config.properties"), "w")
config.write("serviceLocation=" + path + "\n")
config.write("serviceName=" + service)
config.close()

cmd = "/app/jenkins/java/bin/java -DconfigDir={0} -Dlog4j.configuration=file:\"{1}\" -jar {2}".format(
				os.path.join(WORKSPACE, 'test/quality/configuration'),
				os.path.join(WORKSPACE, 'test/quality/configuration/log4j.properties'), 
				os.path.join(WORKSPACE, 'test/quality/codereview.jar')
		)

print "[INFO] " + cmd

sb_cmd = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
sb_data = sb_cmd.communicate()[0]

print sb_data

if sb_data.find("not found") != -1:
	sys.exit(-1)
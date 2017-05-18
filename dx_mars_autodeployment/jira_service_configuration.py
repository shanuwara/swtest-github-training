#!python2.7

import os
import sys
import shlex
import subprocess as sb
import threading
import re
import datetime
import time
import json
import urllib2
import urllib
import socket
import base64
import csv


def setGlobals(elements):
	for element in elements:
		value = os.getenv(element, None)
		if value == "":
			value = None
		globals()[element] = value

elements = ("SVNUSER", "SVNPASS", "JIRASERVER", "JIRAUSER", "JIRAPASS", "CUSTOMFIELD", "CONTEXT", "SETTINGS_URL", "WORKSPACE")
setGlobals(elements)



sys.path.append(os.path.join(WORKSPACE, "custom_field_editor"))
from CustomFieldEditor import CustomFieldManager

	

class CustomFieldManagerExt (CustomFieldManager):
	def __init__(self):
		CustomFieldManager.__init__(self)
		self.__configFileName = None

		self.__CONFusername = None
		self.__CONFpassword = None

		self.__SUBVERSIONusername = None
		self.__SUBVERSIONpassword = None



	def setSubversionCredentials(self, username, password):
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password



	def setConfigFileName(self, filename):
		self.__configFileName = filename

	def getConfiguration(self):

		cmd = "curl -u {0}:{1} -X GET \"{2}\"".format(self.__SUBVERSIONusername, self.__SUBVERSIONpassword, self.__configFileName)
		print "[INFO] Executing:", cmd
		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE, stderr=sb.PIPE)
		(data, error) = proc.communicate()
		# print output, error


		data = data.split("\n")
		output = {}
		# reader = csv.DictReader(data) # in case of csv with headers
		reader = csv.reader(data)
		for line in reader:
			# print line
			if len(line) == 0:
				continue
			output[line[0]] = line[1:]

		return output

	

def addEntries(groupname, entries):
	group = cfm.getGroup(groupname)

	if group is None:
		group = cfm.addGroup(groupname)


	if group is not None:
		print cfm.enableGroup(group["id"])
		for entry in entries:
			child = cfm.getChild(group["id"], entry)
			if child is None:
				print cfm.addChild(group["id"], entry)
			else:
				print cfm.enableChild(group["id"], child["id"])



def cleanUp(cfm):

	groups = cfm.getGroups()
	print groups
	if groups is None or len(groups) == 0:
		return

	for group in groups:
		print group
		cfm.disableGroup(group["id"])
		children = cfm.getChildren(group["id"])
		if children is None:
			continue

		if "statusCode" in children:
			print "[WARNING] children output:", children
			continue

		for child in children:
			print cfm.disableChild(group["id"], child["id"])




cfm = CustomFieldManagerExt()
cfm.setJIRAServer("http://10.33.20.21:8080/jira")
cfm.setJIRACredentials(username=JIRAUSER, password=JIRAPASS)
cfm.setSubversionCredentials(username=SVNUSER, password=SVNPASS)
# cfm.setCustomField(12901, "default")
cfm.setCustomField(CUSTOMFIELD, CONTEXT)
# cfm.setConfigFileName(filename="http://10.33.20.5:8080/svn/DX/cqm/AutoDeployment/jira_service_configuration.csv")
cfm.setConfigFileName(filename=SETTINGS_URL)
newEntries = cfm.getConfiguration()


cleanUp(cfm)


for newEntry in newEntries:
	groupname = newEntry
	entries = newEntries[newEntry]

	addEntries(groupname, entries)

cfm.sortGroups()
# group = cfm.getGroup("DXM-RC1")
# print group

# print cfm.getChildren(group["id"])
# cfm.sortGroup(group["id"])
# print cfm.getChildren(group["id"])
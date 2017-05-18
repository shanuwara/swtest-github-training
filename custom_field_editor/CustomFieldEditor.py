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




class CustomFieldManager:
	def __init__(self):
		self.__JIRAusername = None
		self.__JIRApassword = None

		self.__JIRAserver = None

		self.__CustomFieldId = None
		self.__ContextId = None	


	def setJIRACredentials(self, username, password):
		self.__JIRAusername = username
		self.__JIRApassword = password

	def setJIRAServer(self, server):
		self.__JIRAserver = server

	def setCustomField(self, customfieldid, contextid):
		self.__CustomFieldId = customfieldid
		self.__ContextId = contextid

	def __getParameters(self):
		parameters = {}
		parameters["JIRAUSER"] = self.__JIRAusername
		parameters["JIRAPASS"] = self.__JIRApassword
		parameters["customfieldid"] = self.__CustomFieldId
		parameters["contextid"] = self.__ContextId
		parameters["JIRASERVER"] = self.__JIRAserver
		return parameters

	def addGroup(self, value):
		parameters = self.__getParameters()
		parameters["optionvalue"] = value

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X POST \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options\" -H \"Content-Type: application/json\"  -d '{{\"optionvalue\":\"{optionvalue}\", \"disabled\":\"false\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None


	def getGroup(self, value):
		parameters = self.__getParameters()

		groups = self.getGroups()
		# groups = json.loads(groups)
		for group in groups:
			if group["optionvalue"] == value:
				return group

		return None


	def getGroups(self):
		parameters = self.__getParameters()

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X GET \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options\" "
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]

		if data is not None:
			return json.loads(data)

		return None

	def addChild(self, optionid, value):
		parameters = self.__getParameters()
		parameters["optionid"] = optionid
		parameters["optionvalue"] = value

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X POST \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}/childoptions\" -H \"Content-Type: application/json\"  -d '{{\"optionvalue\":\"{optionvalue}\", \"disabled\":\"false\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None

	def enableGroup(self, optionid):
		parameters = self.__getParameters()
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}\" -H \"Content-Type: application/json\"  -d '{{\"disabled\":\"false\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None

	def disableGroup(self, optionid):
		parameters = self.__getParameters()
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}\" -H \"Content-Type: application/json\"  -d '{{\"disabled\":\"true\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None		


	def enableChild(self, optionid, childid):
		parameters = self.__getParameters()
		parameters["childid"] = childid
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}/childoptions/{childid}\" -H \"Content-Type: application/json\"  -d '{{\"disabled\":\"false\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None

	def disableChild(self, optionid, childid):
		parameters = self.__getParameters()
		parameters["childid"] = childid
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}/childoptions/{childid}\" -H \"Content-Type: application/json\"  -d '{{\"disabled\":\"true\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)

		return None




	def getChildren(self, optionid):
		parameters = self.__getParameters()
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X GET \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}/childoptions\" "
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		if data is not None:
			return json.loads(data)
		return None

	def getChild(self, optionid, value):
		parameters = self.__getParameters()
		children = self.getChildren(optionid)

		if children is None:
			return None

		for child in children:
			if child["optionvalue"] == value:
				return child

		return None

	def sortGroups(self):
		parameters = self.__getParameters()
		

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/sort\" -H \"Content-Type: application/json\" -d '{{\"order\":\"ASCENDING\", \"locale\":\"en-EN\", \"strength\":\"PRIMARY\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		print data
		
		
	def sortGroup(self, optionid):
		parameters = self.__getParameters()
		parameters["optionid"] = optionid

		cmd = "curl -s -u {JIRAUSER}:{JIRAPASS} -X PUT \"{JIRASERVER}/rest/jiracustomfieldeditorplugin/1.2/user/customfields/{customfieldid}/contexts/{contextid}/options/{optionid}/childoptions/sort\" -H \"Content-Type: application/json\" -d '{{\"order\":\"ASCENDING\", \"locale\":\"en-EN\", \"strength\":\"PRIMARY\"}}'"
		print cmd
		cmd = cmd.format(**parameters)
		print cmd

		proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
		data = proc.communicate()[0]
		print data
		

#!python2.7

 
import sys
import os
import subprocess as sb
import shlex
import json
import csv
import shutil
import re
import hashlib


def module_exists(module_name):
	try:
		__import__(module_name)
	except ImportError:
		return False
	else:
		return True

class Settings:
	def __init__(self):
		self.__filename = ""
		self.__SUBVERSIONusername = ""
		self.__SUBVERSIONpassword = ""
		pass

	def setFileName(self, filename):
		self.__filename = filename

	def setSubversionCredentials(self, username, password):
		self.__SUBVERSIONusername = username
		self.__SUBVERSIONpassword = password

	def getSettings(self):
		filename = self.__filename

		
		if self.__SUBVERSIONusername == "":
			raise ValueError("self.__SUBVERSIONusername is empty")

		if self.__SUBVERSIONpassword == "":
			raise ValueError("self.__SUBVERSIONpassword is empty")
			

		values = {
			"username": self.__SUBVERSIONusername,
			"password": self.__SUBVERSIONpassword,
			"filename": filename
		}

		# check dependencies
		if not module_exists("requests"):
			cmd = "curl -s -u {username}:{password} -X GET {filename}".format(**values )
			proc = sb.Popen(shlex.split(cmd), stdout=sb.PIPE)
			data = proc.communicate()[0].split("\n")
		else:
			import requests
			res = requests.get("{filename}".format(**values), auth=(values['username'], values['password']))
			data = res.text.split("\n")


		output = {}
		reader = csv.DictReader(data) # in case of csv with headers
		for line in reader:
			output[line['ServiceName']] = line


		return output

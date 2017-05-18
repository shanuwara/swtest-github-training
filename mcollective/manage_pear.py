#!python2.7 -u

import sys
import subprocess as sb
import shlex
import os
import threading
import re


def getPackageList(_channel):
	print "[INFO]", sys._getframe().f_code.co_name

	cmd = "pear list -c {0}".format(_channel)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	data = proc.communicate()[0]
	if data is not None:
		data = data.split("\n")

	return data

def getNewPackageInfo(_filename):
	print "[INFO]", sys._getframe().f_code.co_name

	if not os.path.exists(_filename):
		raise ValueError("File not found")

	cmd = "pear info {0}".format(_filename)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	data = proc.communicate()[0]
	if data is not None:
		data = data.split("\n")

		for entry in data:
			if entry.find("Release Version") != -1:
				packageVersionName = entry.split()[2]

			if entry.find("Name") != -1:
				packageName = entry.split()[1]

		return {"version" : packageVersionName, "name" : packageName}

	return None


def downloadPear(_url, _target):
	print "[INFO]", sys._getframe().f_code.co_name
	cmd = "wget -O {0} {1}".format(os.path.join(_target, os.path.basename(url)), _url)
	print "[EXECUTING]", cmd
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	data = proc.communicate()[0]
	print data


def installPear(_filename):
	print "[INFO]", sys._getframe().f_code.co_name

	print "installing..."
	
	cmd = "pear install {0}".format(_filename)
	print cmd

	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	data = proc.communicate()

	print data



def upgradePear(_filename):
	print "upgrading..."
	
	cmd = "pear upgrade {0}".format(_filename)
	print "[EXECUTING]", cmd
	
	proc = sb.Popen(shlex.split(cmd), stderr=sb.PIPE, stdout=sb.PIPE)
	data = proc.communicate()

	print data


def compare(a, b):
	arr = [a, b]
	convert = lambda text: int(text) if text.isdigit() else text
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	arr = sorted(arr, key=alphanum_key)
	return arr[1] == b and a != b




####################################################3

if __name__ == "__main__":
	try:
		print "[INFO] parameters:", sys.argv # parameters

		if len(sys.argv) != 2:
			raise ValueError("Incorrect parameters")

		url = sys.argv[1]
		target = "/tmp"


		downloadPear(url, target)

		packageFilename = os.path.join(target, os.path.basename(url)) # new package
		packageName = None # new package
		packageVersionName = None # new package
		versionName = None # old package


		newPackageInfo = getNewPackageInfo(packageFilename)
		print "[INFO] Package info:", newPackageInfo
		packageName = newPackageInfo["name"]
		packageVersionName = newPackageInfo["version"]


		packages = getPackageList("__uri")

		for package in packages:
			if package.find(packageName) != -1:
				versionName = package.split()[1]

				


		print "[INFO] Current version:", versionName

		if versionName is None:
			print "[INFO] ", installPear(packageFilename)


		# if versionName is not None:
		# 	if versionName > packageVersionName:
		# 		raise Exception("Package is older, aborting")
		# 	if versionName == packageVersionName:
		# 		raise Exception("Package is in the same version, aborting")

		# 	if versionName < packageVersionName:
		# 		upgradePear(packageFilename)

		if versionName is not None:
			if compare(versionName, packageVersionName) != True:
				raise Exception("Package is in the same or older version, aborting")

			upgradePear(packageFilename)
						

	except Exception as e:
		print "[ERROR]", e

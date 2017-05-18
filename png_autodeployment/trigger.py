#!python2.7 -u

import csv
import os
import sys
import shlex
import subprocess as sb
import re
import json


JIRAKEY = os.getenv("JIRAKEY", None)
JIRASERVER = os.getenv("JIRASERVER", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
WORKSPACE = os.getenv("WORKSPACE", None)


SERVICE = None
TYPE = None
ENVIRONMENT = None

filename = None



### unit test ###

if WORKSPACE is None:
	JIRAKEY = "PNGT-1487"
	JIRAUSER = "CQMJIRA"
	JIRAPASS = "CQMJIRA"
	JIRASERVER = "http://10.33.20.21:8080/jira"
	WORKSPACE = "/home/extraspace/home/mtz/png/png_autodeployment/"



####


sys.path.append(os.path.join(WORKSPACE, "cqm"))
from jira import jira



def validateParams(array):
	for item in array:
		if array[item] is None or array[item] == 'None':
			print "[INFO] Found 'None'"
			array[item] = ""

	return array


JIRA = jira(server=JIRASERVER, userName=JIRAUSER, password=JIRAPASS)
arr1 = ['fields.issuetype.id']
arr2 = ['issuetype']
fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

print fields["issuetype"]

if fields is not None and "issuetype" in fields and int(fields["issuetype"]) == 11203:
	arr1 = ['fields.customfield_12910.value', 'fields.customfield_12911.value']
	arr2 = ['service', 'branch']
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = str(fields["service"])
	TYPE = "build"
	ENVIRONMENT = "CI"
	BRANCH = str(fields["branch"])
	
	filename = "PnG_Build_LBR.properties"


	jsonDic = {}
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['_ENVIRONMENT']=ENVIRONMENT
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['BRANCH'] = BRANCH

	jsonDic = validateParams(jsonDic)
	print jsonDic

	with open(filename, 'w') as myFile:
	    for key in jsonDic.keys():
	        print 'key='+key
	        print >>myFile,key+'='+jsonDic[key]
	    myFile.close()


if fields is not None and "issuetype" in fields and int(fields["issuetype"]) == 11204:
	arr1 = ['fields.customfield_12910.value', 'fields.customfield_12021.value', 'fields.customfield_12911.value']
	arr2 = ['service', 'environment', 'branch']
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = str(fields["service"])
	ENVIRONMENT = str(fields["environment"])
	TYPE = "deploy"
	BRANCH = str(fields["branch"])
	
	filename = "PnG_Deploy_LBR.properties"


	jsonDic = {}
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['_ENVIRONMENT']=ENVIRONMENT
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['ENVIRONMENT'] = ENVIRONMENT
	jsonDic['BRANCH'] = BRANCH


	jsonDic = validateParams(jsonDic)
	print jsonDic

	with open(filename, 'w') as myFile:
	    for key in jsonDic.keys():
	        print 'key='+key
	        print >>myFile,key+'='+jsonDic[key]
	    myFile.close()	    
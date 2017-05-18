#!python2.7

import sys
import os
import shlex
import json
import subprocess as sb
import re

# sys.path.append('./cqm')
sys.path.append(os.getcwd())
from cqm_libs.utility import utility
from cqm_libs.artefactory import artefactory
from cqm_libs.jira import jira

JIRAKEY = os.getenv("JIRAKEY", None)
JIRASERVER = os.getenv("JIRASERVER", None)
JIRAUSER = os.getenv("JIRAUSER", None)
JIRAPASS = os.getenv("JIRAPASS", None)
WORKSPACE = os.getenv("WORKSPACE", None)
JIRASERVER = "http://10.33.20.21:8080/jira"

SERVICE = None
TYPE = None
ENVIRONMENT = None

filename = None


JIRA = jira(server=JIRASERVER, userName=JIRAUSER, password=JIRAPASS)
arr1 = ['fields.issuetype.id']
arr2 = ['issuetype']
fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

print fields["issuetype"]

## build
if int(fields["issuetype"]) == 26:
	#arr1 = ['fields.customfield_12901.value','fields.customfield_12901.child.value', 'fields.customfield_12901.value']
	arr1 = ['fields.customfield_13011.value','fields.customfield_13011.child.value', 'fields.customfield_13011.value']
	arr2 = ['RC', 'service', 'branch']
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = str(fields["service"])
	RC = str(fields["RC"])
	TYPE = "build"
	ENVIRONMENT = "CI"
	BRANCH = str(fields["branch"])
	
	filename = "DX-MARS_Build.properties"

	jsonDic = {}
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['FORCE_SERVICE'] = SERVICE
	jsonDic['BRANCH'] = BRANCH
	jsonDic['RC'] = ""

	print jsonDic

	with open(filename, 'w') as myFile:
		for key in jsonDic.keys():
			print 'key='+key
			print >>myFile,key+'='+jsonDic[key]
		myFile.close()

# promote
elif int(fields["issuetype"]) == 10900:
	arr1 = ['fields.customfield_13000.value', 'fields.customfield_13003.value', 'fields.customfield_13007', 'fields.customfield_13002.value', 'fields.customfield_13001.value']
	arr2 = ['service', 'environment', 'RC', 'EMS_SCRIPTS', 'COUCHBASE_SCRIPTS']
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = str(fields["service"])
	ENVIRONMENT = str(fields["environment"])
	RC = str(fields["RC"])
	TYPE = "promote"
	EMS_SCRIPTS = str(fields['EMS_SCRIPTS'])
	COUCHBASE_SCRIPTS = str(fields['COUCHBASE_SCRIPTS'])
	
	filename = "DX-MARS_Promote.properties"


	jsonDic = {}
	jsonDic['_TYPE']=TYPE
	jsonDic['_SERVICE']=SERVICE
	jsonDic['_ENVIRONMENT']=ENVIRONMENT
	jsonDic['_RC']=RC
	jsonDic['SERVICE'] = SERVICE
	jsonDic['JIRAKEY'] = JIRAKEY
	jsonDic['ENVIRONMENT'] = ENVIRONMENT
	jsonDic['COUCHBASE_SCRIPTS'] = COUCHBASE_SCRIPTS
	jsonDic['EMS_SCRIPTS'] = EMS_SCRIPTS

	jsonDic['RC'] = RC
   

	print jsonDic

	with open(filename, 'w') as myFile:
		for key in jsonDic.keys():
			print 'key='+key
			print >>myFile,key+'='+jsonDic[key]
		myFile.close()	    
    
    
# deploy    
elif int(fields["issuetype"]) == 10800:
	arr1 = ['fields.customfield_12901.value','fields.customfield_12901.child.value', 'fields.customfield_13005.value', 'fields.customfield_11817.value', 'fields.customfield_13012.value' ]
	arr2 = ['rc', 'service', 'environment', 'hotrelease', 'branch' ]
	fields = JIRA.getJiraKeyInfo(jiraKey=JIRAKEY, fields=arr1, new_filed_names=arr2)

	SERVICE = str(fields["service"])
	ENVIRONMENT = str(fields["environment"])
	HOT_RELEASE = str(fields['hotrelease'])
	RC = str(fields['rc'])
	TYPE = "deploy"
	BRANCH = str(fields["branch"])
	
	filename = "DX-MARS_Deploy.properties"


	jsonDic = {}
	# jsonDic['VALIDATION_ONLY'] = "NO"

	jsonDic['_RC']= RC
	jsonDic['RC'] = RC

	jsonDic['HOT_RELEASE'] = HOT_RELEASE
	
	jsonDic['JIRAKEY'] = JIRAKEY
	
	jsonDic['_TYPE']=TYPE

	jsonDic['_SERVICE']=SERVICE
	jsonDic['SERVICE'] = SERVICE

	jsonDic['_ENVIRONMENT']=ENVIRONMENT
	jsonDic['ENVIRONMENT'] = ENVIRONMENT

	
	jsonDic['BRANCH'] = BRANCH

   

	print jsonDic

	with open(filename, 'w') as myFile:
		for key in jsonDic.keys():
			print 'key='+key
			print >>myFile,key+'='+jsonDic[key]
		myFile.close()	    
   
else:
	print "No such issue type"
	exit (1)